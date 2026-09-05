#!/usr/bin/env python3
"""Lossless bounded-memory archives for the exact three-root SAT inputs.

SHA-256 checks transport integrity only. Mathematical results come from
graph comparisons and proof checking, never from these digests.
"""
import argparse
import gzip
import hashlib
import json
import lzma
from pathlib import Path
import tempfile
import time


def pack(source, destination, names):
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'archive.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'schema': 'astra-exact-input-archive-v1', 'hash_role': 'integrity only', 'files': []}
    entries = {item['name']: item for item in manifest['files']}
    for name in names:
        raw_path = source / name
        opener = raw_path.open
        if not raw_path.exists() and (source / (name + '.gz')).exists():
            raw_path = source / (name + '.gz')
            opener = lambda mode: gzip.open(raw_path, mode)
        if not raw_path.exists():
            raise FileNotFoundError(raw_path)
        start = time.monotonic()
        digest, size = hashlib.sha256(), 0
        with tempfile.TemporaryDirectory(prefix='astra-pack-') as tmp:
            compressed = Path(tmp) / 'archive.xz'
            with opener('rb') as incoming, lzma.open(compressed, 'wb', preset=3) as outgoing:
                while chunk := incoming.read(1 << 20):
                    digest.update(chunk)
                    size += len(chunk)
                    outgoing.write(chunk)
            # Independently decompress before publishing any archive entry.
            replay_digest, replay_size = hashlib.sha256(), 0
            with lzma.open(compressed, 'rb') as replay:
                while chunk := replay.read(1 << 20):
                    replay_digest.update(chunk)
                    replay_size += len(chunk)
            assert replay_size == size and replay_digest.digest() == digest.digest()
            parts = []
            with compressed.open('rb') as incoming:
                index = 0
                while chunk := incoming.read(4 << 20):
                    part = f'{name}.xz.part{index:03d}'
                    (destination / part).write_bytes(chunk)
                    parts.append(part)
                    index += 1
            entry = {'name': name, 'codec': 'xz', 'raw_bytes': size, 'raw_sha256': digest.hexdigest(),
                     'compressed_bytes': compressed.stat().st_size, 'parts': parts, 'seconds': time.monotonic() - start}
            entries[name] = entry
            manifest['files'] = list(entries.values())
            manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
            print(json.dumps(entry, sort_keys=True), flush=True)
    return manifest


def chunks(folder, name):
    manifest = json.loads((folder / 'archive.json').read_text())
    item = next(item for item in manifest['files'] if item['name'] == name)
    decoder = lzma.LZMADecompressor()
    digest, size = hashlib.sha256(), 0
    for part in item['parts']:
        with (folder / part).open('rb') as incoming:
            while block := incoming.read(1 << 20):
                data = decoder.decompress(block, max_length=1 << 20)
                while True:
                    if data:
                        digest.update(data)
                        size += len(data)
                        yield data
                    if decoder.needs_input or decoder.eof:
                        break
                    data = decoder.decompress(b'', max_length=1 << 20)
    assert decoder.eof and not decoder.unused_data
    assert size == item['raw_bytes'] and digest.hexdigest() == item['raw_sha256']


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('pack')
    p.add_argument('source', type=Path)
    p.add_argument('destination', type=Path)
    p.add_argument('names', nargs='+')
    p = sub.add_parser('verify')
    p.add_argument('folder', type=Path)
    p = sub.add_parser('unpack')
    p.add_argument('folder', type=Path)
    p.add_argument('destination', type=Path)
    args = parser.parse_args()
    if args.command == 'pack':
        pack(args.source, args.destination, args.names)
        return
    if args.command == 'unpack':
        args.destination.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.folder / 'archive.json').read_text())
    for item in manifest['files']:
        if args.command == 'unpack':
            with (args.destination / item['name']).open('wb') as out:
                for chunk in chunks(args.folder, item['name']):
                    out.write(chunk)
        else:
            for chunk in chunks(args.folder, item['name']):
                pass
        print('ARCHIVE_INTEGRITY_PASS', item['name'], flush=True)


if __name__ == '__main__':
    main()
