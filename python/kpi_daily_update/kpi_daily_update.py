#!/usr/bin/env python3
"""kpi daily update

Exports the last 24 hours of KPI data for ALL active KPI instances from PTV Flows KPI API
into a ';' separated CSV.

APIs used (KPI Engine):
- GET  /instance/all           -> list all active KPI instances (kpiId, name, template, unit, ...)
- POST /result/by-kpi-ids      -> time series results for multiple KPI IDs and a time span

Authentication:
- HTTP header: apiKey

Output:
- One CSV per run, containing rows for each KPI/timeStamp.
- Includes both overallResult and (optionally) partial results (progressive) per timeStamp.

Notes:
- The script queries the *last 24 hours* relative to the time of execution (UTC by default).
- Use environment variable PTV_API_KEY to avoid putting secrets in code.
"""

import argparse
import csv
import datetime as dt
import os
import sys
import time
from typing import Dict, Any, List

try:
    import requests
except ImportError:
    print("Missing dependency: requests. Install with: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:
    ZoneInfo = None


BASE_URL_DEFAULT = "https://api.ptvgroup.tech/kpieng/v1"
INSTANCE_ALL_PATH = "/instance/all"
RESULT_BY_IDS_PATH = "/result/by-kpi-ids"


def iso_z(dt_utc: dt.datetime) -> str:
    """Return ISO-8601 UTC with Z suffix."""
    return dt_utc.replace(tzinfo=dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def http_request(method: str, url: str, headers: Dict[str, str], json_body=None,
                 timeout: int = 60, retries: int = 3, backoff: float = 1.7):
    """HTTP request with retries and basic error surfacing."""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.request(method, url, headers=headers, json=json_body, timeout=timeout)
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code} for {url}: {resp.text[:800]}")
            return resp
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff ** attempt)
            else:
                raise last_exc


def get_instances(base_url: str, api_key: str) -> List[Dict[str, Any]]:
    url = base_url.rstrip("/") + INSTANCE_ALL_PATH
    headers = {"apiKey": api_key}
    return http_request("GET", url, headers=headers).json()


def post_results_by_ids(base_url: str, api_key: str, kpi_ids: List[str], from_time_z: str, to_time_z: str):
    url = base_url.rstrip("/") + RESULT_BY_IDS_PATH
    headers = {"apiKey": api_key}
    payload = {"kpiIds": kpi_ids, "fromTime": from_time_z, "toTime": to_time_z}
    return http_request("POST", url, headers=headers, json_body=payload).json()


def safe_get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def to_local(ts: str, tz_name: str) -> str:
    """Convert ISO timestamp to local ISO (best effort)."""
    try:
        # Support trailing Z
        if ts.endswith('Z'):
            ts2 = ts[:-1] + '+00:00'
        else:
            ts2 = ts
        dt_obj = dt.datetime.fromisoformat(ts2)
        if dt_obj.tzinfo is None:
            dt_obj = dt_obj.replace(tzinfo=dt.timezone.utc)
    except Exception:
        return ts

    if ZoneInfo is None:
        return dt_obj.astimezone(dt.timezone.utc).isoformat(timespec='seconds')

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = dt.timezone.utc

    return dt_obj.astimezone(tz).isoformat(timespec='seconds')


def chunked(lst: List[str], n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


def main():
    parser = argparse.ArgumentParser(
        prog="kpi daily update",
        description="Export last 24 hours of ALL KPI data from PTV Flows KPI API to ';' separated CSV."
    )
    parser.add_argument("--api-key",  default=os.getenv("PTV_API_KEY"),
                        help="PTV Flows API key (or set env var PTV_API_KEY).")
    parser.add_argument("--base-url", default=BASE_URL_DEFAULT,
                        help=f"KPI API base URL (default: {BASE_URL_DEFAULT})")
    parser.add_argument("--outdir", default="out",
                        help="Output directory (default: ./out)")
    parser.add_argument("--tz", default="Europe/Rome",
                        help="Timezone used for extra local timestamp column (default: Europe/Rome)")
    parser.add_argument("--hours", type=int, default=24,
                        help="Lookback window in hours (default: 24)")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="How many KPI IDs per /result/by-kpi-ids request (default: 50)")
    parser.add_argument("--include-partials", action="store_true",
                        help="Also export partial results (the 'results' array with progressive) in addition to overallResult")
    parser.add_argument("--filename", default=None,
                        help="Optional output filename. Default: kpi_daily_update_<YYYY-MM-DD>_<HHmm>.csv")

    args = parser.parse_args()

    if not args.api_key:
        print("ERROR: API key missing. Provide --api-key or set env var PTV_API_KEY.", file=sys.stderr)
        sys.exit(2)

    # Compute window in UTC
    to_dt = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    from_dt = to_dt - dt.timedelta(hours=args.hours)
    from_z = iso_z(from_dt)
    to_z = iso_z(to_dt)

    # List active KPIs
    instances = get_instances(args.base_url, args.api_key) or []

    # Build instance lookup
    inst_by_id: Dict[str, Dict[str, Any]] = {}
    kpi_ids: List[str] = []
    for inst in instances:
        kid = inst.get("kpiId")
        if kid:
            inst_by_id[kid] = inst
            kpi_ids.append(kid)

    if not kpi_ids:
        print("No active KPI instances found (instance/all returned none). Nothing to export.")
        sys.exit(0)

    # Pull results in batches
    all_results: List[Dict[str, Any]] = []
    for batch in chunked(kpi_ids, max(1, args.batch_size)):
        res = post_results_by_ids(args.base_url, args.api_key, batch, from_z, to_z) or []
        # API returns a list of result objects
        if isinstance(res, list):
            all_results.extend(res)
        else:
            # In unexpected case, keep it but avoid crash
            all_results.append({"_unexpected": res, "kpiIds": batch})

    # Prepare rows
    run_ts_utc = iso_z(to_dt)
    rows = []

    for item in all_results:
        kpi_id = item.get("kpiId")
        ts = item.get("timeStamp")
        inst = inst_by_id.get(kpi_id, {})

        base = {
            "run_timestamp_utc": run_ts_utc,
            "fromTime_utc": from_z,
            "toTime_utc": to_z,

            "kpiId": kpi_id,
            "kpiName": inst.get("name"),
            "template": inst.get("template"),
            "unitOfMeasure": inst.get("unitOfMeasure"),
            "direction": inst.get("direction"),

            "timeStamp_utc": ts,
            "timeStamp_local": to_local(ts, args.tz) if ts else None,
        }

        overall = item.get("overallResult") or {}
        rows.append({
            **base,
            "result_type": "overall",
            "progressive": safe_get(overall, "progressive"),
            "value": safe_get(overall, "value"),
            "defaultValue": safe_get(overall, "defaultValue"),
            "unusualValue": safe_get(overall, "unusualValue"),
            "averageValue": safe_get(overall, "averageValue"),
        })

        if args.include_partials:
            for r in (item.get("results") or []):
                rows.append({
                    **base,
                    "result_type": "partial",
                    "progressive": r.get("progressive"),
                    "value": r.get("value"),
                    "defaultValue": r.get("defaultValue"),
                    "unusualValue": r.get("unusualValue"),
                    "averageValue": r.get("averageValue"),
                })

    # Output
    os.makedirs(args.outdir, exist_ok=True)
    if args.filename:
        out_name = args.filename
    else:
        local_now = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
        out_name = f"kpi_daily_update_{local_now}.csv"
    out_path = os.path.join(args.outdir, out_name)

    fieldnames = [
        "run_timestamp_utc", "fromTime_utc", "toTime_utc",
        "kpiId", "kpiName", "template", "unitOfMeasure", "direction",
        "timeStamp_utc", "timeStamp_local",
        "result_type", "progressive",
        "value", "defaultValue", "unusualValue", "averageValue",
    ]

    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    os.replace(tmp_path, out_path)
    print(f"OK - exported {len(rows)} rows for {len(kpi_ids)} KPIs to: {out_path}")


if __name__ == "__main__":
    main()
