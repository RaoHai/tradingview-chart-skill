"""Rebuild documentation pages from the bundled, dated market snapshots."""

from pathlib import Path

from build_chart import build
import json


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'output/showcase'
    output.mkdir(parents=True, exist_ok=True)
    for code in ('588000', '515000', '512800'):
        source = root / f'docs/examples/{code}.json'
        html = build(json.loads(source.read_text(encoding='utf-8')), standalone=True)
        theme = 'dark' if code == '512800' else 'light'
        html = html.replace('</head>', f'<style>:root {{ color-scheme: {theme}; }}</style></head>')
        (output / f'{code}.html').write_text(html, encoding='utf-8')
        print(f'{code}: {output / (code + ".html")}')


if __name__ == '__main__':
    main()
