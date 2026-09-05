#!/usr/bin/env python3
"""Exact native acceleration of the existing parent-isomorphism blockers.

Python generates each D-A -> D-B residual map. C++ expands its at most
36 completions and looks up the *same* edge-difference literals as Encoder.
All emitted maps are retained as full permutation bytes for independent replay.
"""
import ctypes as ct
import gzip
import itertools
from pathlib import Path
import subprocess
import tempfile
import time

from astra_overlap_strike import Overlaps


class Native:
    def __init__(self, enc):
        self.tmp = tempfile.TemporaryDirectory(prefix='astra-parent-blocks-')
        library = Path(self.tmp.name) / 'parent_blocks.so'
        subprocess.run(['g++', '-O3', '-shared', '-fPIC', '-std=c++17',
                        str(Path(__file__).with_suffix('.cpp')), '-o', str(library)], check=True)
        self.lib = ct.CDLL(str(library))
        self.lib.expand.argtypes = [ct.c_int, ct.c_int, ct.POINTER(ct.c_uint8),
                                   ct.POINTER(ct.c_int), ct.POINTER(ct.c_int), ct.POINTER(ct.c_uint8)]
        self.lib.expand.restype = ct.c_int
        self.enc, self.n, self.d = enc, enc.n, enc.d
        assert self.n - self.d == 3
        n = self.n
        entries = []
        for u, v in itertools.combinations(range(n), 2):
            for a in range(n):
                for b in range(n):
                    if a == b:
                        entries.append(2147483647)
                    else:
                        x = enc.difference(enc.slot(0, u, v), enc.slot(1, a, b))
                        entries.append(2147483647 if x is True else 0 if x is False else x)
        self.lookup = (ct.c_int * len(entries))(*entries)
        self.width = enc.edge_variables + 1
        self.clauses = (ct.c_int * (36 * self.width))()
        self.maps = (ct.c_uint8 * (36 * n))()

    def expand(self, theta):
        partial = (ct.c_uint8 * self.n)(*(theta.get(u, 255) for u in range(self.n)))
        count = self.lib.expand(self.n, self.d, partial, self.lookup, self.clauses, self.maps)
        assert 0 < count <= 36, ('native expansion error', count)
        return count

    def close(self):
        self.tmp.cleanup()


def preblock(enc, out):
    start = time.monotonic()
    native = Native(enc)
    counts, templates = {}, 0
    try:
        with gzip.open(out / 'parent_maps.bin.gz', 'wb', compresslevel=1) as fp:
            for k in range(4):
                counts[k] = 0
                overlaps = Overlaps(enc.core, k)
                for bucket in overlaps.buckets.values():
                    for left, right in itertools.product(bucket, repeat=2):
                        for theta in overlaps.maps(left, right):
                            count = native.expand(theta)
                            fp.write(ct.string_at(native.maps, count * enc.n))
                            for i in range(count):
                                offset = i * native.width
                                length = native.clauses[offset]
                                enc.add(native.clauses[offset + 1:offset + 1 + length])
                            counts[k] += count
                            templates += 1
                            if templates % 10000 == 0:
                                print('PARENT_BLOCK_PROGRESS', k, templates, sum(counts.values()),
                                      round(time.monotonic() - start, 3), flush=True)
                print('PARENT_BLOCK_LAYER', k, counts[k], round(time.monotonic() - start, 3), flush=True)
    finally:
        native.close()
    return counts
