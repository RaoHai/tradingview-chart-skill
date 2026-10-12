import argparse
import datetime
import json
import math
from pathlib import Path
import uuid
import re

def number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

def validate(data):
    for key in ('symbol', 'currency', 'as_of', 'source_name', 'source_url', 'adjustment'):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ValueError(f'Missing metadata: {key}')
    if not data.get('bars'):
        raise ValueError('No observations')
    dates = set()
    for bar in data['bars']:
        if not isinstance(bar.get('time'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', bar['time']):
            raise ValueError('Dates must use YYYY-MM-DD')
        datetime.date.fromisoformat(bar['time'])
        if bar['time'] in dates:
            raise ValueError('Duplicate date')
        dates.add(bar['time'])
        if any(not number(bar[k]) or bar[k] <= 0 for k in ('open','high','low','close')):
            raise ValueError('Invalid price')
        if not bar['low'] <= min(bar['open'],bar['close']) <= max(bar['open'],bar['close']) <= bar['high']:
            raise ValueError('Invalid OHLC bounds')
        if 'volume' in bar and (not number(bar['volume']) or bar['volume'] < 0):
            raise ValueError('Invalid volume')
    for level in data.get('levels', []):
        if not number(level.get('price')) or level['price'] <= 0 or level.get('kind') not in ('support','resistance') or not isinstance(level.get('title'), str):
            raise ValueError('Invalid level')
    if not data['source_url'].startswith('https://'):
        raise ValueError('Source must use HTTPS')
    data['bars'].sort(key=lambda b: b['time'])
    return data

def build(data, standalone=False):
    data = validate(data)
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    assets = Path(__file__).resolve().parent.parent / 'assets'
    template = (assets / 'chart-fragment.html').read_text(encoding='utf-8')
    fragment = template.replace('__ROOT_ID__', 'tv-'+uuid.uuid4().hex).replace('__CHART_DATA__', payload)
    if standalone:
        wrapper = (assets / 'standalone.html').read_text(encoding='utf-8')
        return wrapper.replace('__FRAGMENT__', fragment)
    return fragment

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--standalone', action='store_true', help='Write a complete browser page instead of an inline fragment')
    args = p.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8-sig'))
    rendered = build(data, standalone=args.standalone)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding='utf-8')
    print(f'{len(data["bars"])} validated bars -> {output}')

if __name__ == '__main__':
    main()
