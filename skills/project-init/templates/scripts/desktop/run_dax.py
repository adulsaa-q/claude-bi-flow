"""Run a DAX file through pbi-cli's JSON interface, preserving failures."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        query = args.file.resolve().read_text(encoding='utf-8-sig')
        result = subprocess.run(
            ['pbi', '--json', 'dax', 'execute', '-', '--timeout', '60'],
            input=query, capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=90,
        )
        if result.returncode:
            print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
            return 1
        rows = json.loads(result.stdout)['rows']
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ValueError('invalid rows payload')
        if not rows:
            print('(no rows)')
            return 0
        columns = list(rows[0])
        def display(value):
            return 'BLANK' if value is None else str(value)
        widths = {c: max(len(c), *(len(display(row.get(c))) for row in rows)) for c in columns}
        print(' | '.join(c.ljust(widths[c]) for c in columns))
        for row in rows:
            print(' | '.join(display(row.get(c)).rjust(widths[c]) for c in columns))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f'DAX execution failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
