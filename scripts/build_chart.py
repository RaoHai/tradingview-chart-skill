import argparse
import datetime
import json
import math
from pathlib import Path
import uuid
import re
import sys
from urllib.parse import urlsplit


class ValidationError(ValueError):
    def __init__(self, code, path, message):
        super().__init__(f'{path}: {message}')
        self.code = code
        self.path = path


def fail(code, path, message):
    raise ValidationError(code, path, message)

def number(value):
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        return False

def validate(data):
    if not isinstance(data, dict):
        fail('invalid_object', '$', 'Expected a JSON object')
    for key in ('symbol', 'currency', 'as_of', 'source_name', 'source_url', 'adjustment'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            fail('missing_metadata', key, 'Expected nonblank text')
    if data.get('locale', 'zh-CN') not in ('zh-CN', 'en-US'):
        fail('invalid_locale', 'locale', 'Choose zh-CN or en-US')
    if not isinstance(data.get('bars'), list) or not data['bars']:
        fail('invalid_bars', 'bars', 'Expected a nonempty array')
    dates = set()
    for index, bar in enumerate(data['bars']):
        path = f'bars[{index}]'
        if not isinstance(bar, dict):
            fail('invalid_bar', path, 'Expected an object')
        if not isinstance(bar.get('time'), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', bar['time']):
            fail('invalid_date', path + '.time', 'Dates must use YYYY-MM-DD')
        try:
            datetime.date.fromisoformat(bar['time'])
        except ValueError:
            fail('invalid_date', path + '.time', 'Invalid calendar date')
        if bar['time'] in dates:
            fail('duplicate_date', path + '.time', 'Duplicate date')
        dates.add(bar['time'])
        for key in ('open', 'high', 'low', 'close'):
            if not number(bar.get(key)) or bar[key] <= 0:
                fail('invalid_price', path + '.' + key, 'Expected a positive finite number')
        if not bar['low'] <= min(bar['open'],bar['close']) <= max(bar['open'],bar['close']) <= bar['high']:
            fail('invalid_ohlc', path, 'Invalid OHLC bounds')
        if 'volume' in bar and (not number(bar['volume']) or bar['volume'] < 0):
            fail('invalid_volume', path + '.volume', 'Expected a nonnegative finite number; omit missing volume')
    if not isinstance(data.get('levels', []), list):
        fail('invalid_levels', 'levels', 'Expected an array')
    for index, level in enumerate(data.get('levels', [])):
        if not isinstance(level, dict) or not number(level.get('price')) or level['price'] <= 0 or level.get('kind') not in ('support','resistance') or not isinstance(level.get('title'), str):
            fail('invalid_level', f'levels[{index}]', 'Expected positive price, title and support/resistance kind')
    try:
        url = urlsplit(data['source_url'])
        valid_url = url.scheme == 'https' and bool(url.hostname) and not any(c.isspace() for c in data['source_url'])
    except ValueError:
        valid_url = False
    if not valid_url:
        fail('invalid_source_url', 'source_url', 'Expected an HTTPS URL with a host')
    if 'retrieved_utc' in data:
        try:
            stamp = datetime.datetime.fromisoformat(data['retrieved_utc'].replace('Z', '+00:00'))
            if stamp.utcoffset() != datetime.timedelta(0):
                raise ValueError()
        except (ValueError, TypeError, AttributeError):
            fail('invalid_retrieval_time', 'retrieved_utc', 'Expected an ISO 8601 UTC datetime with Z or +00:00')
    data['bars'].sort(key=lambda b: b['time'])
    return data


def inspect_data(data):
    """Report structural quality only; no calendar or quote verification."""
    try:
        validate(data)
    except ValidationError as exc:
        return {'valid': False, 'errors': [{'code': exc.code, 'path': exc.path, 'message': str(exc)}], 'warnings': []}
    bars = data['bars']
    missing = sum('volume' not in bar for bar in bars)
    warnings = []
    if missing:
        warnings.append({'code': 'missing_volume', 'path': 'bars', 'message': f'{missing} of {len(bars)} bars have no volume; omitted, not zero-filled'})
    for period in (20, 50):
        if len(bars) < period:
            warnings.append({'code': 'insufficient_ma_history', 'path': 'bars', 'message': f'MA{period} needs {period} observations; found {len(bars)}'})
    if 'retrieved_utc' not in data:
        warnings.append({'code': 'missing_retrieval_time', 'path': 'retrieved_utc', 'message': 'Retrieval time was not recorded'})
    return {'valid': True, 'errors': [], 'warnings': warnings,
            'summary': {'symbol': data['symbol'], 'first_session': bars[0]['time'],
                        'last_session': bars[-1]['time'], 'bar_count': len(bars),
                        'volume_bar_count': len(bars) - missing, 'missing_volume_count': missing,
                        'available_moving_averages': [p for p in (20, 50) if len(bars) >= p]},
            'scope': 'Structural checks only; prices, trading-calendar completeness and adjustment consistency are not verified.'}

def build(data, standalone=False):
    data = validate(data)
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    assets = Path(__file__).resolve().parent.parent / 'assets'
    template = (assets / 'chart-fragment.html').read_text(encoding='utf-8')
    fragment = template.replace('__ROOT_ID__', 'tv-'+uuid.uuid4().hex).replace('__CHART_DATA__', payload)
    if standalone:
        wrapper = (assets / 'standalone.html').read_text(encoding='utf-8')
        return wrapper.replace('lang="zh-CN"', 'lang="'+data.get('locale', 'zh-CN')+'"').replace('__FRAGMENT__', fragment)
    return fragment

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--output')
    p.add_argument('--standalone', action='store_true', help='Write a complete browser page instead of an inline fragment')
    p.add_argument('--check', action='store_true', help='Validate and print a JSON report without rendering HTML')
    p.add_argument('--report', help='Also save the JSON validation report (including validation failures)')
    args = p.parse_args()
    if not args.check and not args.output:
        p.error('--output is required unless --check is used')
    if args.check and (args.output or args.standalone):
        p.error('--check cannot be combined with --output or --standalone')
    paths = [Path(path).resolve() for path in (args.input, args.output, args.report) if path]
    if len(set(paths)) != len(paths):
        p.error('--input, --output and --report must use different paths')
    try:
        data = json.loads(Path(args.input).read_text(encoding='utf-8-sig'))
        report = inspect_data(data)
    except (OSError, UnicodeError, ValueError) as exc:
        report = {'valid': False, 'errors': [{'code': 'input_error', 'path': '$', 'message': str(exc)}], 'warnings': []}
    report_json = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_json + '\n', encoding='utf-8')
    if args.check:
        print(report_json)
    if not report['valid']:
        if not args.check:
            print(report_json, file=sys.stderr)
        raise SystemExit(2)
    if args.check:
        return
    rendered = build(data, standalone=args.standalone)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding='utf-8')
    print(f'{len(data["bars"])} validated bars -> {output}')

if __name__ == '__main__':
    main()
