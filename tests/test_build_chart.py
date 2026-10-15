import copy
import importlib.util
import unittest
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


if __name__ == '__main__':
    unittest.main()
