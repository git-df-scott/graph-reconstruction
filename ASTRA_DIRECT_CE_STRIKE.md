# Astra direct counterexample strike — 2026-09-04

## Result

```text
CE FOUND: NO
CEC FOUND: NO
NEW CE ARCHITECTURE: YES
TARGETED SEARCH EXECUTED: YES
INDEPENDENT VERIFIER: PASS
```

The new construction is a refinement of the audited shared-card architecture:
**root migration through double-deletion overlaps**, followed by a two-root
auxiliary repair at the same parent order. It is not a claimed new solution
or a claim that all shared-card constructions fail.

Twenty-three explicitly specified shared-card fibres were exhausted. A
stronger two-root construction on 22 vertices also returned UNSAT, with its
full proof independently accepted by DRAT-trim. No nonisomorphic equal-deck
graph pair was emitted.

The next direct target is already specified: three-root repair on **the same
22 vertices**, with 120 unknown edge bits and 8,745,408 possible parent maps.
That is the single recommended continuation. Stop condition C is reached at
this larger, precisely defined construction problem.

## Branch reconciliation

- Work began at local audit commit `8672265` on
  `claude/grc-counterexample-35nwgv`.
- The actual remote branch was still `e81cb8b`, an ancestor of the audit.
  The audit's merge of the divergent continuation was retained, not discarded.
- The chronological commit log, original construction formalism, successive
  obstruction records, and all eight requested audit/handoff sources were
  consulted. No literature review or historical census was rerun.
- All September-4 downgrades remain in force. This strike does not upgrade
  the historical order-6/7, hash-dependent fibre, cover, or Blue-LED claims.

Git transport lacked credentials, so publication used the authenticated
GitHub connector. The merge and audit were recreated with **identical Git
trees**, preserving both remote parents. Their published IDs and tree checks
are in `data/astra_direct/publication.json`. The original local merge and
`8672265` audit objects are preserved losslessly in
`data/astra_direct/inherited_audit.bundle`; their commit identities can be
recovered with `git fetch data/astra_direct/inherited_audit.bundle
astra-inherited-audit:astra-original-audit`.

## The construction reduction

Fix an ordinary graph `C` on `m` vertices. Let `G=C+x` and `H=C+y`, with
unknown neighborhoods `A,B subset V(C)`. Their root-deletion cards agree.
If their full decks agree, subtract that one common occurrence of `C` from
each multiset. The other `m` deletion occurrences still admit a bijection.

Every isomorphism in such a matching has one of two forms.

### Root fixed

A map `G-u -> H-v` sending `x` to `y` restricts to an isomorphism
`f:C-u -> C-v`, and requires

```text
A[a] = B[f(a)]  for every a != u.
```

The SAT model includes every such isomorphism, chooses exactly one for each
source and target deletion occurrence, and preserves multiplicities. It
requires `A,B` to be in different `Aut(C)` orbits by explicit XOR clauses
for **every** automorphism. This is a necessary condition for unrooted parent
nonisomorphism, not a sufficient one. Any SAT assignment is still checked
as an ordinary unrooted graph pair. Only an actually isomorphic assignment
may be blocked. No such residual SAT assignments occurred in the 23 runs.

Every root-fixed UNSAT has a frozen CNF and DRUP proof, checked by
`scripts/astra_drup_verify.py`, which imports no SAT solver or discovery code.

### Root moved: exactly three free bits

Suppose a card map sends `x -> t`, with `t` in `C`, and some `s` in `C`
to `y`. Necessarily `s != u` and `t != v`. Restriction gives

```text
theta : C-{u,s} -> C-{v,t}.
```

All extension bits except three are determined:

```text
A[a]        = C[t,theta(a)]   for a outside {u,s}
B[theta(a)] = C[s,a]          for a outside {u,s}
A[s]        = B[t].
```

The free bits are `A[u]`, `B[v]`, and the common value `A[s]=B[t]`.
Thus each overlap map and choice of removed-vertex orientations gives exactly
eight explicit parent pairs. Conversely each of these eight pairs has the
stated card isomorphism, edge by edge.

For every unordered pair of double-deletion subsets with isomorphic induced
graphs, the program enumerates **all** isomorphisms, both orientations of
each removed pair, and all eight completions. Reversing the order of the two
subsets only interchanges `G,H`; that is the sole pair-order omission.

Every pair is immediately tested for parent edge/degree agreement, ordinary
parent nonisomorphism, and complete deck equality. Nauty's full canonical
adjacency bytes are compared, not truncated or cryptographic hashes.

**Completeness for fixed C.** If any nonisomorphic equal-deck extension pair
exists, either its residual deck matching can be chosen root-fixed and the
SAT branch finds it, or a moving map occurs and the eight-completion branch
contains it. Cross-card transition maps are not required to globalize; no
extra cocycle-flatness restriction is imposed.

## Exact construction domains actually searched

| Fixed-card family | Cards | Parent order | Overlap maps | Completion presentations* | Distinct neighborhood pairs, summed by card | Nonisomorphic parent-pair presentations checked against full decks |
|---|---:|---:|---:|---:|---:|---:|
| Two phase terminals | 18 | 16 | 2,946 | 94,272 | 50,108 | 1,913 |
| Three deletion-equivalent terminals | 4 | 21 | 10,128 | 324,096 | 47,836 | 3,036 |
| Nonuniform selector split | 1 | 22 | 29,412 | 941,184 | 6,185 | 213 |
| **Total** | **23** | | **42,486** | **1,359,552** | **104,129** | **5,162** |

\* Each map has four removed-pair orientations and eight **three-bit**
completions, hence 32 presentations. These are streamed; most are duplicate
presentations induced by automorphisms. The counts are not numbers of distinct
unlabeled graph pairs across different cards. Every one of the 5,162
nonisomorphic pair presentations failed exact full-deck equality.

### Two phase terminals

The core is the circulant on `Z/13Z` with differences `+/-S`, where

```text
S in {{1,3}, {1,4}, {1,3,4}}.
W = {0,1,3,5,8,9}.
shift in {1,2,3}.
terminal edge in {absent,present}.
```

Terminal 1 sees `W`; terminal 0 sees `W+shift`. Deleting terminal 0 or 1
gives isomorphic cards by a core rotation. All 18 fixed cards are asymmetric.
Every neighborhood of one additional vertex is permitted, not only symmetric
or phase-uniform neighborhoods. The complete domain is these 18 cards,
not all cyclic-core constructions or all words `W`.

### Three deletion-equivalent terminals

The core has vertices `F_17`; two are adjacent iff their nonzero difference
is a square. Add terminals at the clique `{0,1,2}`. Their neighborhoods in
the core are either all open or all closed neighborhoods of those ports;
the three terminals are either independent or a clique. These four choices
are the complete tested family.

All three terminal-deletion cards are isomorphic. In the intact card,
terminal 17 cannot be carried to terminal 18 by any automorphism. This is an
actual graph-level failure to extend some local maps. With independent
terminals the full automorphism group has order 2. With clique terminals it
has order 16 and every card type is repeated, with multiplicities
`6,2,2,2,2,2,2,2`. This specifically tests a cycle of local identifications
and a case without a unique card occurrence.

### Nonuniform selector split

Use the inherited selector construction at port weights `(1,1,3,4)`:

```text
C graph6 = T??????oDoO{]?PwF{??q?DK?Qw?[w?R{?F^
```

`C` has 21 vertices. The inherited unequal parents at weights `(2,1,3,4)`
and `(1,2,3,4)` both extend it. The mutation allows **all `2^21` extension
neighborhoods**, including arbitrary splits inside each twin class and
arbitrary attachments to all pair/selector vertices. Thus the old uniform
weighted-vector condition is removed. Only this fixed card fibre is closed.

## Same-order two-root auxiliary repair

Remove `q_{01}` (vertex 9) from that 21-vertex shared card. Freeze the remaining
20-vertex graph `D`, serialized in
`data/astra_direct/two_root_certified/core.json`. On each side add two vertices
with all incident edges free. There are `2*20+1=41` edge bits per parent,
**82 total**, and both parents still have order 22.

The SAT model has a variable bijection between all 22 deletion occurrences,
and a complete unrestricted vertex map on every card. Only the common core
edges are fixed. No deletion matching is normalized to the identity and no
unproved symmetry leader is used.

The initial CEGAR run timed out after 60 solver seconds and 767 actual
isomorphic models. This was an unresolved run, not a candidate. Its learned
solver state was not retained; it was superseded by full parent-map blocking.

For any parent isomorphism, exactly `k=0,1,2` core vertices map to the target's
two added vertices. Its restriction is an isomorphism `D-A -> D-B`, with
`|A|=|B|=k`. Enumerating these restrictions and the remaining images yields
the complete possible parent-isomorphism universe:

| Core vertices moved into new vertices | Possible parent maps |
|---:|---:|
| 0 | 288 |
| 1 | 14,400 |
| 2 | 160,416 |
| **Total** | **175,104** |

All maps are excluded by explicit edge-disagreement clauses. Any satisfying
assignment of the resulting formula would therefore be two nonisomorphic
parents with equal full decks, by construction. A separate VF2 implementation
recreated and compared the **entire set of 175,104 permutation byte strings**.

The final formula has **33,201 variables and 1,595,879 clauses**. The run
without proof output completed in 117.72 seconds including construction.
The proof-emitting replay completed in 134.87 seconds and produced 1,622,516
proof lines. External proof verification: **VERIFIED**, in 166.338 seconds.
The checker reports zero RAT lemmas. The exact verified formula and original
proof are preserved as `formula.cnf.gz` and 31 ordered parts of the
`unsat.drup.gz` stream, sized for the connector's transport. Compression and
splitting were checked byte for byte; the replay script joins the parts.
The machine-readable result is
`data/astra_direct/two_root_certified/certificate.json`.

This finite result concerns exactly the stated fixed `D`. It does not close
two-root constructions over other cores or the general reconstruction problem.

## Independent verification and controls

- Independent NetworkX/VF2 regeneration of all double-overlap maps, all
  completion pairs, and their rejection for one phase card, the repeated-card
  clique-terminal card, and the selector card. The corresponding exact pair
  sets have sizes 2,503, 14,808, and 6,185. No discovery or nauty code is
  imported by that verifier.
- Independent full-set verification of the 175,104 two-root parent maps.
- External DRAT-trim verification of the complete two-root UNSAT proof;
  a deliberately false empty-clause proof is rejected by the same executable.
- All 23 root-fixed UNSAT proofs checked by the standalone DRUP checker.
- Existing hostile CE checker: all multiplicity, order, corruption, and
  parent-isomorphism controls pass. The frozen selector rejection was also
  checked independently and rejected for deck mismatch.
- Full repository suite at its checkpoint: 64 tests passed. The final focused
  suite has six passing tests, including every one of 1,024 tiny two-root
  assignments in each of the full- and partial-deck modes, plus a complete
  permutation-universe comparisons at orders 5 and 6.
- Dropping card constraints produces explicit nonisomorphic partial-deck
  positive controls. The full order-4 controls are UNSAT with both CEGAR and
  complete parent-map blocking. These controls are not CECs.

There is no CE verification PASS to claim: no nonisomorphic equal-deck pair
reached that gate. `INDEPENDENT VERIFIER: PASS` above describes the controls,
finite-domain replays, and completed certificate checks.

## Frozen record and reproduction

All construction parameters, exact graph6/edge lists, pair sets, first rejected
pairs, canonical parent/card records, run summaries, CNFs, and proof artifacts
are under `data/astra_direct/`. SHA-256 in the final manifest is only an
integrity check, never a mathematical equality test.

Dependencies used: Python 3.12.13, pynauty 2.8.8.1, NetworkX 3.6.1,
python-sat 1.9.dev15; exact versions are recorded in the run summaries.
External DRAT checker source: `marijnheule/drat-trim`, commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

```bash
python scripts/astra_phase_suite.py
python scripts/astra_paley_tripod.py
python scripts/astra_selector_split.py
python scripts/astra_independent_overlap_verify.py \
  data/astra_direct/phase_suite/s13_shift1_link0 \
  data/astra_direct/paley_tripod/closed0_clique1 \
  data/astra_direct/selector_split
python scripts/astra_parent_maps_verify.py data/astra_direct/two_root_preblocked
python scripts/astra_two_root_repair.py --preblock --certify --seconds 240 \
  --out data/astra_direct/two_root_certified
python -m unittest discover -s tests -p 'test_astra_overlap.py' -v
```

Replay the compressed proof with the pinned DRAT-trim executable:

```bash
python scripts/astra_certificate_replay.py --drat-trim /path/to/drat-trim
```

The checker command and result are frozen with the certificate.

## Single next direct strike: three-root pair/selector repair

Keep the parent order **22**. From the selector shared card remove `q_{01}`
and the first even-path selector `z_0` (vertices 9 and 15), leaving the exact
19-vertex core in `data/astra_direct/next_three_root/specification.json`.
Add three freely attached vertices on each side. This lets a pair-vertex
deletion and a selector-vertex deletion change together with the main twist.

The domain has **120 unknown edge bits**. Its full-deck encoding before parent
blocking has 31,618 variables and 1,643,731 clauses. Exact group-order counting
gives the following possible parent maps:

```text
k=0:         864
k=1:      59,616
k=2:   1,184,544
k=3:   7,500,384
total: 8,745,408
```

These counts define the next workload; no three-root SAT search was executed.
`python scripts/astra_next_specification.py` reproduces the specification.
The parent-map vocabulary is about fifty times the two-root vocabulary, which
is the concrete reason to reserve this construction for a dedicated run.
The generalized constructor is already implemented:

```bash
python scripts/astra_two_root_repair.py --roots 3 --preblock --certify \
  --seconds 1800 --out data/astra_direct/three_root_strike
```

Attack this one specified repair. Preserve the complete parent-map exclusion
when compressing its stabilizer/coset representation. Any SAT result must
immediately freeze the two ordinary graphs and run the hostile CE protocol.
