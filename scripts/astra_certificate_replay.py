#!/usr/bin/env python3
"""Replay the frozen, losslessly compressed two-root UNSAT certificate."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--drat-trim', type=Path)
    ap.add_argument('--integrity-only', action='store_true')
    ap.add_argument('--certificate-dir', type=Path, default=Path('data/astra_direct/two_root_certified'))
    args = ap.parse_args()
    if args.drat_trim is None and not args.integrity_only:
        ap.error('--drat-trim is required for proof replay')
    certificate = json.loads((args.certificate_dir / 'certificate.json').read_text())
    with tempfile.TemporaryDirectory(prefix='astra-unsat-') as tmp:
        tmp = Path(tmp)
        for item in certificate['files']:
            raw = tmp / item['path'].removesuffix('.gz')
            compressed = args.certificate_dir / item['path']
            if item.get('parts'):
                compressed = tmp / item['path']
                with compressed.open('wb') as combined:
                    for part in item['parts']:
                        with (args.certificate_dir / part).open('rb') as source:
                            shutil.copyfileobj(source, combined)
            digest = hashlib.sha256()
            count = 0
            with gzip.open(compressed, 'rb') as source, raw.open('wb') as target:
                while chunk := source.read(1 << 20):
                    digest.update(chunk)
                    count += len(chunk)
                    target.write(chunk)
            assert count == item['raw_bytes'] and digest.hexdigest() == item['raw_sha256']
        if args.integrity_only:
            print('COMPRESSED_CERTIFICATE_INTEGRITY_PASS')
            return
        result = subprocess.run([str(args.drat_trim.resolve()), str(tmp / 'formula.cnf'), str(tmp / 'unsat.drup')], text=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
        assert result.returncode == 0 and 's VERIFIED' in result.stdout and 's NOT VERIFIED' not in result.stdout
        print('INDEPENDENT_UNSAT_CERTIFICATE_PASS')


if __name__ == '__main__':
    main()
