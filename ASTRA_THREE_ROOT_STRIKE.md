# Astra three-root direct counterexample strike

```text
CE FOUND: NO
CEC FOUND: NO
NEW CE ARCHITECTURE: YES
TARGETED SEARCH EXECUTED: YES
INDEPENDENT VERIFIER: NOT APPLICABLE
```

The CE verifier flag concerns a genuine candidate pair: none was found.
Independent map, symbolic-card and small UNSAT controls passed separately.

Continuation of published commit `19e3b8666d583493887ceddb08f9690c139fcabf`.
The target is two ordinary finite simple undirected nonisomorphic graphs,
each of order 22, with identical full vertex-deleted decks as multisets.

## Exact construction

Use precisely the 19-vertex core frozen in
`data/astra_direct/next_three_root/specification.json`. It is obtained from
the selector card at weights `(1,1,3,4)` by removing vertices 9 and 15.
Each parent consists of that core plus three vertices, and every edge
incident with an added vertex is free. This is 60 edge bits per parent,
120 in total. Edges between the 19 core vertices remain fixed.

The solver chooses a bijection of the 22 deletion occurrences and an
unrestricted 21-vertex isomorphism for every matched pair of cards.
No fixed vertex matching, degree ordering, or prescribed card map is assumed.
Multiplicity is enforced by the deletion-occurrence bijection.

The third free vertex permits pair and selector attachments to change
together. No graph-order increase or generic graph census is involved.

## Complete parent-isomorphism exclusion

A parent map sends exactly k core vertices into the three target added
vertices. Its restriction is an isomorphism `D-A -> D-B`, with
`|A|=|B|=k`. After that restriction is fixed, every bijection of the omitted
vertices is enumerated, retaining precisely those sending A into target
added vertices. Thus k ranges from 0 to 3 and covers every possible parent
isomorphism, including maps exchanging the core and the added vertices.

| k | Full parent permutations |
|---:|---:|
| 0 | 864 |
| 1 | 59,616 |
| 2 | 1,184,544 |
| 3 | 7,500,384 |
| Total | 8,745,408 |

`astra_fast_preblock.cpp` accelerates only this finite expansion and literal
lookup. Each permutation receives the same edge-disagreement clause as
`Encoder.block_isomorphism`. It applies no extra graph restrictions.
The complete permutation stream is preserved losslessly as `parent_maps.bin`
in the split XZ archive under `three_root_strike`.

The independent `astra_three_root_maps_verify.py` uses NetworkX VF2 and a
separate completion enumeration. It reconstructed all 8,745,408 maps and
compared sorted full permutation bytes, including duplicate checks.
Result: PASS, 67.20 seconds. No digest equality is used as a substitute
for permutation equality.

The baseline formula has 35,158 variables and 10,403,299 clauses.
Construction took 147.17 seconds. The 120 edge bits are the graph search
variables; the remaining SAT variables describe maps and logical auxiliaries.

## Stronger encoding of the same construction

For any n >= 3, the sum of edge counts of the vertex-deleted cards equals
`(n-2)|E(G)|`. Therefore equal full decks imply equal parent edge counts.
For a matched deletion u -> v, card edge-count equality then gives
`deg_G(u)=deg_H(v)`.

`astra_degree_constraints.py` encodes these two necessary identities with
exact unary threshold circuits. The circuits encode both directions of
each equivalence. They do not assume a degree sequence, distinct degrees,
or a canonical ordering of vertices. The admissible graph-pair domain is
unchanged.

The third encoding also records the number of triangles through each vertex.
For n >= 4, the sum of triangle counts of the cards is `(n-3)T(G)`, hence
the parent triangle count is reconstructible from the full deck. Subtracting
the triangle count of a matched card gives equal triangle counts through the
matched deleted vertices. All indicator and counting circuits are exact in
both directions. This adds necessary equations without selecting a particular
triangle count.

## Ten exact root-type representatives

Let a,b,c be the three edge bits among the added vertices of one parent.
Permuting the three added vertices induces all permutations of these three
edge positions. Every assignment therefore has a representative satisfying
`a <= b <= c`, one of `000,001,011,111`. This uses two clauses per parent.
Exchanging the parents then orders the two root-edge counts, implemented by
three coordinatewise implications. There are exactly ten resulting type pairs.

This normalization is proved, not a guessed lex leader: the independent
root permutations fix D pointwise, transport every card map and the deletion
matching, and preserve parent nonisomorphism. Parent exchange preserves the
target as well. Thus every CE in the full domain has a representative meeting
these seven clauses. No claim about automorphisms of the completed parents
is needed. The control covers all 64 labeled root-edge patterns explicitly.

The inherited selector pair is also frozen in these coordinates. It has
nonisomorphic parents and exactly 9 of 22 common cards. The hostile checker
independently rejects it for a deck mismatch. Its edge values are used only
as preferred solver phases, after the proved normalization; no attachment
bits are fixed to that seed.

One further attempt isolates root types `(2,2)`, meaning P3 on the three
added vertices in each parent. This fixes exactly six bits and leaves 114
free edge bits. It is a specified subcase, not a closure of the full domain.

## Runs and current checkpoint

- Initial full-deck CEGAR pass: 180 solver seconds; 1,296 isomorphic
  models blocked; timeout, unresolved. No candidate. The actual blocking
  permutations and graph6 presentations are retained.
- Complete native parent-map preblocking: full formula built and independent
  map-universe check passed. The 1,800-second solve timed out, unresolved;
  512,307 conflicts and 1,035,195 decisions. No SAT model was returned.
- Degree-strengthened full formula: same graph-pair domain, with a separate
  900-second solve. Timeout, unresolved; 364,962 conflicts, 753,546 decisions.
  Its formula has 40,432 variables and 10,429,319 clauses.
- Degree/triangle identities, ten proved root-type representatives, and
  inherited-pair phase preferences: 71,340 variables, 10,576,938 clauses.
  The 600-second solve timed out, unresolved; 133,209 conflicts and 331,056
  decisions. Its final output was observed before a runtime reset. The exact
  formula archive survived; `observed_result.json` explicitly labels the
  transcribed statistics because the original temporary log was lost.
- The `(2,2)` subcase uses the preceding encoding plus six unit clauses.
  Construction finished (71,340 variables, 10,576,944 clauses); the last
  observation was SOLVING. Its temporary final result was not recovered after
  the runtime reset. This subcase is unresolved, not an UNSAT or timeout claim.

## Controls

- All 4,096 graph-pair assignments at order four agree with an independent
  card-edge-count oracle for the three-root deck encoding.
- Every map and every native blocking clause agrees with the original
  Python definition on the complete small P3-core universe. Full-order
  clause samples cover every residual-isomorphism bucket and k layer.
- Unary threshold circuits checked in both directions for all 64 assignments
  of six inputs.
- Degree matching checked against direct arithmetic for all 4,096 pairs
  at each of two different deletion permutations.
- Triangle matching checked in the same complete small domain against direct
  triangle enumeration.
- Native parent-nonisomorphism clauses checked on all 4,096 order-four pairs
  against canonical labels obtained by enumerating the 24 vertex permutations.
  This includes positive nonisomorphic pairs as well as isomorphic rejections.
- Full order-five three-root control, including the degree constraints and
  native parent blockers: UNSAT; independent DRAT-trim verification PASS.
- Existing overlap controls remain passing.

All 15 focused controls pass. Both the degree-only and combined
degree/triangle/root-type order-five proof controls pass external DRAT-trim.

Proof export now streams the SAT backend's ASCII proof rather than loading
the whole proof into multiple Python lists. The independent proof control
above exercises this export path.

## Lossless input archives

The baseline, degree-strengthened and strongest formulas are frozen in ordered
4 MiB XZ parts with manifests. SHA-256 is used only for transport integrity.
`astra_archive_run.py verify FOLDER` checks every part by decompressing it;
`astra_archive_run.py unpack FOLDER DESTINATION` restores the exact DIMACS
input and, for the baseline, the full parent-map stream. No timeout proof
fragment is represented as an UNSAT certificate.

## Reproduction

```bash
python scripts/astra_two_root_repair.py --roots 3 --preblock \
  --fast-preblock --certify --seconds 1800 \
  --out data/astra_direct/three_root_strike
python scripts/astra_three_root_maps_verify.py data/astra_direct/three_root_strike
python scripts/astra_two_root_repair.py --roots 3 --preblock \
  --fast-preblock --certify --degree-constraints --seconds 900 \
  --out /tmp/grc-three-root-degree
python scripts/astra_two_root_repair.py --roots 3 --preblock \
  --fast-preblock --certify --degree-constraints --triangle-constraints \
  --root-leaders --near-miss-phases --seconds 600 \
  --out /tmp/grc-three-root-strongest
python scripts/astra_two_root_repair.py --roots 3 --preblock \
  --fast-preblock --certify --degree-constraints --triangle-constraints \
  --root-leaders --near-miss-phases --root-case 2 2 --seconds 600 \
  --out /tmp/grc-three-root-case22
python -m unittest discover -s tests -p 'test_astra*.py' -v
```

No CE or CEC is asserted by this checkpoint. Any nonisomorphic SAT pair
must be frozen and immediately passed to the hostile checker and an
independent complete deck/parent implementation before any positive claim.


## Direct construction from a fully migrating card map

Fix core deletions u,v of equal degree. Choose ordered P3 triples A,B in
D-u and D-v. Choose a residual isomorphism
`theta: D-{u,A} -> D-{v,B}` on 15 vertices, which does not extend to a core
automorphism. All three added source vertices map into B; A maps onto the
three added target vertices. This determines both root P3s and every
root-to-ordinary-core attachment. Only nine bridge bits and six bits incident
with the deleted core vertices remain free. The bridge bits are shared
across the two parents through the chosen card map.

Every one of the 32,768 assignments therefore has one guaranteed matching
21-vertex card. Equal parent edge counts retain 10,240 assignments per
template. The search then checks degree multisets, exact parent canonical
forms, a necessary probe card, and finally the complete multiset deck.
A full-deck hit stops the search and invokes the hostile checker immediately.
This constructs parents from local equations; it does not enumerate arbitrary
graphs or assume that the remaining 21 cards match.

The raw domain has 3,876 four-deletion subsets, 951 residual types and
764,280 ordered equal-degree P3 residual-map presentations. Of these,
438,336 extend to core automorphisms and 325,944 do not. These are labeled
presentations, not numbers of distinct graph pairs. The initial 16-template
prefix tested 524,288 assignments and rejected all 8,496 nonisomorphic pairs
that survived the earlier filters through a missing probe card.

`astra_moving_quotient.py` quotients the nonextendable presentations by
independent core automorphisms, the stabilizers of both distinguished deletion
patterns, and parent exchange. Orbit weights sum exactly to 325,944.
The 144-element core automorphism group is independently reproduced by
NetworkX VF2. Removing identical literal families leaves 330 templates.
The previously completed first 64 templates are resumed only after exact
comparison of their frozen input records with regenerated records.

`astra_moving_certificate_verify.py` independently compares affine Boolean
edge expressions under every frozen card map, without importing discovery
code or its canonicalizer. Thus it verifies the built-in single-card equality
for all 2^15 assignments per template. It does not independently certify
negative full-deck enumeration results.

## Single next strike

Retain one added vertex across the selected card map, while the other two
migrate into the core. Fix P3 root types and an isomorphism between the two
16-vertex residual cores. For each compatible template, solve the local
edge equations first. The surviving added vertex permits a shared 16-bit
neighborhood column, alongside four bridge bits and six deletion-incidence
bits: at most 26 free bits. Quotient the templates and attack these equations
with the other card conditions. This is a proposed next construction, not
a tested claim, and the current fully migrating results do not exclude it.


## Completed finite construction result — September 5

All 330 nonextendable quotient families were exhausted, including the first
64 whose frozen inputs and results were reused. The completion invocation
took 141.35 seconds; that is not a timing for rerunning all 330 from scratch.
The raw presentation domain is 325,944; the quotient search examined:

| Gate | Assignments |
|---|---:|
| Total 15-bit assignments | 10,813,440 |
| Rejected by unequal edge count | 7,434,240 |
| Rejected by unequal degree multiset | 2,839,230 |
| Rejected as isomorphic parents | 150,691 |
| Nonisomorphic parents reaching card checks | 389,279 |
| Rejected by a missing probe card | 387,633 |
| Rejected by full multiset deck comparison | 1,646 |
| Full-deck nonisomorphic pairs | 0 |

This is a replayable **single-implementation negative search**, with exact
canonical forms rather than hash decisions. The separate symbolic checker
verified all 69,300 mapped edge identities across the 330 templates; the
15 focused regression controls passed again after the runtime reset.
No general architecture is rigorously closed by this result. In particular,
extendable residual maps, partial migration, unequal deleted core degrees,
other root types and the unrestricted three-root SAT domain remain outside
this completed construction domain.

Reproduce the finite construction and its independent card-identity check:

```bash
python scripts/astra_moving_quotient.py --max-templates 330 --out data/astra_direct/moving_quotient
python scripts/astra_moving_certificate_verify.py data/astra_direct/moving_quotient
```

Use `--resume` to reuse a completed prefix after exact input comparison.
Dependencies are Python 3, NetworkX, NumPy, pynauty, python-sat and a C++17
compiler for the native SAT preblocker. External proof controls additionally
use DRAT-trim. The final regression run used NetworkX 3.6.1, NumPy 2.3.5,
pynauty 2.8.8.1 and python-sat 1.9.dev15.

Stop condition: the selected bounded 15-bit construction is exhausted;
the larger exact SAT problem remains a dedicated-run task. No CE or CEC
is claimed, and no unresolved SAT attempt is treated as a negative proof.
