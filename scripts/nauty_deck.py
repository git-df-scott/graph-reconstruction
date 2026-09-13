"""Exact deck engine for the graph reconstruction conjecture (Kelly-Ulam).

A card of G is an unlabelled one-vertex-deleted subgraph G-v; the deck is the
multiset of all n cards.  The conjecture says the deck determines G up to
isomorphism for n >= 3.  A counterexample is a pair of non-isomorphic graphs
with equal decks -- self-certifying, with no search bound, no numerical
tolerance and no topology involved.

Certificates are exact canonical forms computed by nauty's labelg, not hashes,
so a reported deck collision is a real collision and never a birthday accident.

NOTE: python-igraph 1.0.0's Graph.canonical_permutation() does NOT return a
canonical form -- two labellings of the 4-vertex path give different answers.
That is why nauty is used here and igraph is not.

Controls (see SOL_9.md): zero deck collisions over every non-isomorphic graph
on 3..9 vertices, and exactly one collision at n = 2, the classical K2
exception.
"""
import subprocess

# ---------------------------------------------------------------- graph6 I/O

def g6_decode(s):
    """graph6 string -> (n, set of edges).  Short and long (n <= 258047) forms."""
    s = s.strip()
    d = [ord(c) - 63 for c in s]
    if d[0] == 63:                      # long form: '~' then 3 bytes of n
        n = (d[1] << 12) | (d[2] << 6) | d[3]
        rest = d[4:]
    else:
        n = d[0]
        rest = d[1:]
    bits = []
    for x in rest:
        bits.extend((x >> k) & 1 for k in range(5, -1, -1))
    edges, i = set(), 0
    for col in range(1, n):
        for row in range(col):
            if bits[i]:
                edges.add((row, col))
            i += 1
    return n, edges


def g6_encode(n, edges):
    """(n, iterable of (u,v)) -> graph6 string.  Short and long (n <= 258047) forms."""
    e = {(min(u, v), max(u, v)) for u, v in edges}
    bits = [1 if (row, col) in e else 0 for col in range(1, n) for row in range(col)]
    bits += [0] * (-len(bits) % 6)
    if n <= 62:
        out = [chr(n + 63)]
    else:
        out = [chr(126), chr(((n >> 12) & 63) + 63), chr(((n >> 6) & 63) + 63),
               chr((n & 63) + 63)]
    for i in range(0, len(bits), 6):
        x = 0
        for b in bits[i:i + 6]:
            x = (x << 1) | b
        out.append(chr(x + 63))
    return ''.join(out)


def cards(g6):
    """The n one-vertex-deleted subgraphs of a graph6 string, as graph6."""
    n, edges = g6_decode(g6)
    out = []
    for v in range(n):
        relab = {u: (u if u < v else u - 1) for u in range(n) if u != v}
        out.append(g6_encode(n - 1, [(relab[a], relab[b]) for a, b in edges
                                     if a != v and b != v]))
    return out

# ------------------------------------------------------------ canonical form

def canon_many(g6_list, chunk=200000):
    """Exact canonical graph6 for each input, via nauty labelg.  Order preserved."""
    out = []
    for i in range(0, len(g6_list), chunk):
        part = g6_list[i:i + chunk]
        p = subprocess.run(['nauty-labelg', '-q'], input='\n'.join(part) + '\n',
                           capture_output=True, text=True, check=True)
        res = p.stdout.split()
        if len(res) != len(part):
            raise RuntimeError('labelg returned %d of %d' % (len(res), len(part)))
        out.extend(res)
    return out


def decks(g6_list):
    """Deck (sorted tuple of canonical cards) for each graph, batched through nauty."""
    flat, spans = [], []
    for g in g6_list:
        c = cards(g)
        spans.append((len(flat), len(c)))
        flat.extend(c)
    canon = canon_many(flat)
    return [tuple(sorted(canon[o:o + k])) for o, k in spans]

# ------------------------------------------------------------------- search

def geng(n, *extra):
    """Every non-isomorphic simple graph on n vertices, as graph6, via nauty-geng."""
    p = subprocess.Popen(['nauty-geng', '-q', str(n), *map(str, extra)],
                         stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    for line in p.stdout:
        line = line.strip()
        if line:
            yield line
    p.wait()


def find_collisions(g6_list):
    """Group by deck; return {deck: {distinct canonical graphs}} for groups with >1.

    A non-empty result is a counterexample to the reconstruction conjecture.
    """
    ds = decks(g6_list)
    cs = canon_many(g6_list)
    buckets = {}
    for d, c in zip(ds, cs):
        buckets.setdefault(d, set()).add(c)
    return {d: v for d, v in buckets.items() if len(v) > 1}
