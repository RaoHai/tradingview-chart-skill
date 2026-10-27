import copy
import importlib.util
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('builder', Path(__file__).resolve().parents[1] / 'scripts/build_chart.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuilderTests(unittest.TestCase):
    def setUp(self):
        # Validation fixtures only; never used as market observations or examples.
        self.data = dict(symbol='TEST', currency='USD', as_of='fixture', source_name='fixture',
                         source_url='https://example.org', adjustment='fixture',
                         bars=[dict(time='2025-01-02', open=10, high=12, low=9, close=11)])

    def test_missing_volume_stays_missing(self):
        builder.validate(self.data)
        self.assertNotIn('volume', self.data['bars'][0])

    def test_invalid_bounds_and_nonfinite_rejected(self):
        for key, value in [('low', 20), ('high', float('nan')), ('volume', -1), ('open', True)]:
            data = copy.deepcopy(self.data)
            data['bars'][0][key] = value
            with self.assertRaises(ValueError):
                builder.validate(data)

    def test_duplicate_and_noncanonical_dates_rejected(self):
        data = copy.deepcopy(self.data)
        data['bars'] *= 2
        with self.assertRaises(ValueError):
            builder.validate(data)
        self.data['bars'][0]['time'] = '20250102'
        with self.assertRaises(ValueError):
            builder.validate(self.data)

    def test_sorting_and_unique_roots(self):
        self.data['bars'].insert(0, dict(time='2025-01-03', open=10, high=12, low=9, close=11))
        one = builder.build(self.data)
        self.assertEqual(self.data['bars'][0]['time'], '2025-01-02')
        self.assertNotEqual(one, builder.build(self.data))

    def test_script_injection_escaped(self):
        self.data['symbol'] = '</script><script>alert(1)</script>'
        html = builder.build(self.data)
        self.assertNotIn(self.data['symbol'], html)
        self.assertIn('\\u003c/script\\u003e', html)

    def test_standalone_and_fragment(self):
        self.assertNotIn('<!doctype', builder.build(self.data))
        self.assertIn('<!doctype html>', builder.build(self.data, standalone=True))

    def test_english_export_and_default_language(self):
        self.assertIn('lang="zh-CN"', builder.build(self.data, standalone=True))
        self.data['locale'] = 'en-US'
        self.assertIn('lang="en-US"', builder.build(self.data, standalone=True))

    def test_unsupported_language_rejected(self):
        self.data['locale'] = 'en-US"><script>'
        with self.assertRaises(ValueError):
            builder.build(self.data, standalone=True)

    def test_malformed_inputs_return_actionable_paths(self):
        cases = [([], '$'), ({'bars': {}}, 'bars'), ({'bars': [None]}, 'bars[0]'),
                 ({'bars': [{'time': '2025-02-30'}]}, 'bars[0].time'),
                 ({'levels': None}, 'levels'), ({'levels': [None]}, 'levels[0]'),
                 ({'source_url': 'https://'}, 'source_url'),
                 ({'symbol': '   '}, 'symbol'),
                 ({'retrieved_utc': '2026-10-27'}, 'retrieved_utc')]
        for change, path in cases:
            with self.subTest(change=change):
                data = dict(self.data, **change) if isinstance(change, dict) else change
                report = builder.inspect_data(data)
                self.assertFalse(report['valid'])
                self.assertEqual(report['errors'][0]['path'], path)
        del self.data['bars'][0]['close']
        self.assertEqual(builder.inspect_data(self.data)['errors'][0]['path'], 'bars[0].close')

    def test_report_distinguishes_omitted_and_zero_volume(self):
        self.data['bars'].append(dict(time='2025-01-03', open=10, high=12, low=9, close=11, volume=0))
        report = builder.inspect_data(self.data)
        self.assertTrue(report['valid'])
        self.assertEqual(report['summary']['missing_volume_count'], 1)
        self.assertEqual(report['summary']['volume_bar_count'], 1)
        self.assertEqual(report['summary']['first_session'], '2025-01-02')
        self.assertEqual(report['summary']['last_session'], '2025-01-03')
        self.assertEqual(report['summary']['available_moving_averages'], [])
        self.assertNotIn('volume', self.data['bars'][0])

    def test_complete_history_has_no_quality_warnings(self):
        import datetime
        start = datetime.date(2025, 1, 1)
        self.data['bars'] = [dict(time=str(start + datetime.timedelta(days=i)), open=10, high=12, low=9, close=11, volume=100) for i in range(50)]
        self.data['retrieved_utc'] = '2026-10-27T01:00:00Z'
        report = builder.inspect_data(self.data)
        self.assertEqual(report['warnings'], [])
        self.assertEqual(report['summary']['available_moving_averages'], [20, 50])
        self.assertIn('not verified', report['scope'])

    def test_cli_check_and_failed_build_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, report, output = root / 'data.json', root / 'report.json', root / 'chart.html'
            source.write_text(json.dumps(self.data), encoding='utf-8')
            command = [sys.executable, builder.__file__, '--input', str(source)]
            result = subprocess.run(command + ['--check', '--report', str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['valid'])
            self.assertEqual(json.loads(report.read_text()), json.loads(result.stdout))
            self.assertFalse(output.exists())
            self.data['bars'][0]['low'] = 20
            source.write_text(json.dumps(self.data), encoding='utf-8')
            result = subprocess.run(command + ['--output', str(output), '--report', str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(report.read_text())['errors'][0]['code'], 'invalid_ohlc')
            self.assertNotIn('Traceback', result.stderr)
            source.write_text('{broken json', encoding='utf-8')
            result = subprocess.run(command + ['--check'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['errors'][0]['code'], 'input_error')

    def test_cli_prevents_overwriting_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'data.json'
            original = json.dumps(self.data)
            source.write_text(original, encoding='utf-8')
            result = subprocess.run([sys.executable, builder.__file__, '--input', str(source), '--check', '--report', str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_text(), original)


if __name__ == '__main__':
    unittest.main()
