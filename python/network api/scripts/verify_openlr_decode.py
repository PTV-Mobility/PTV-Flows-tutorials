import json
import os

TOPOJSON = 'ptv_flows_network_12.442961_41.817077_12.491369_41.845216.topojson'

with open(TOPOJSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Walk through features (TopoJSON may store objects differently; try common places)
count = 0
examples = []

def extract_openlr(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() == 'openlr' and isinstance(v, str):
                examples.append(v)
            else:
                extract_openlr(v)
    elif isinstance(obj, list):
        for item in obj:
            extract_openlr(item)

extract_openlr(data)

print(f'Found {len(examples)} openlr entries (showing up to 10)')
for i, val in enumerate(examples[:10]):
    print(f'[{i}] raw: {val}')
    # Try to interpret as hex bytes and decode as utf-8/base64-like
    try:
        b = bytes.fromhex(val)
        try:
            s = b.decode('utf-8')
        except Exception:
            s = repr(b)
        print(f'    decoded: {s}')
    except Exception as e:
        print(f'    not-hex or decode failed: {e}')

print('Done')
