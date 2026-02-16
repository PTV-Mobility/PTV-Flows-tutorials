# kpi daily update

This project exports **all KPI data for all active KPIs for the last 24 hours** from the **PTV Flows KPI API** into a `;`-separated CSV.

## What the script does

1. Calls the KPI API endpoint to list all **active/running KPI instances** and collects their `kpiId` values.
2. Calls the KPI API endpoint that returns KPI **results for multiple KPI IDs** for a given time range.
3. Exports a CSV where each row corresponds to one KPI and one timestamp.

By default, it exports the **overallResult** for each KPI/timestamp.

Optionally, you can also export **partial results** (the `results[]` array with `progressive`) using `--include-partials`.

## Files

- `kpi_daily_update.py` — main script
- `requirements.txt` — dependencies

## Requirements

- Python 3.9+ recommended
- Internet access to `https://api.ptvgroup.tech`
- A valid **PTV Flows API Key**

Install dependencies:

```bash
pip install -r requirements.txt
```

## Security (API key)

**Do not hardcode keys** into the script.

Use an environment variable instead:

### Linux / macOS

```bash
export PTV_API_KEY="YOUR_API_KEY"
```

### Windows PowerShell

```powershell
$env:PTV_API_KEY="YOUR_API_KEY"
```

## Run

Basic run (last 24 hours; one CSV):

```bash
python kpi_daily_update.py --outdir ./exports
```

Export partial results too:

```bash
python kpi_daily_update.py --include-partials --outdir ./exports
```

Change lookback window (e.g., last 48 hours):

```bash
python kpi_daily_update.py --hours 48 --outdir ./exports
```

Tune KPI ID batching (if you have many KPIs):

```bash
python kpi_daily_update.py --batch-size 25 --outdir ./exports
```

## Output CSV

The CSV is `;` separated and includes:

- `kpiId`, `kpiName`, `template`, `unitOfMeasure`
- `timeStamp_utc` (timestamp of the measurement) and `timeStamp_local` (converted using `--tz`)
- `result_type`: `overall` or `partial`
- `progressive` (only meaningful for `partial` rows)
- `value`, `defaultValue`, `unusualValue`, `averageValue`

Output file name (default):

- `kpi_daily_update_YYYY-MM-DD_HHMM.csv`

## Scheduling (daily)

If you want a daily export, schedule it once per day:

### Linux cron (example: every day at 00:05)

```cron
5 0 * * * /usr/bin/python3 /path/kpi_daily_update.py --outdir /path/exports >> /path/exports/kpi_daily_update.log 2>&1
```

### Windows Task Scheduler

Create a daily task that runs:

- Program: `python.exe`
- Arguments: `C:\path\kpi_daily_update.py --outdir C:\path\exports`

