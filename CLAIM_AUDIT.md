# Hostile claim audit

## Audit standard

`THEOREM` means a general proof with its hypotheses stated.  `EXACT-BOUNDED`
means exhaustive only in the stated finite domain.  `REPLAYABLE` means code is
committed but no immutable result artifact is.  `INDEPENDENT` requires a
second implementation that does not simply call the discovery routine.
`SHA-CONDITIONED` means a cryptographic digest can affect completeness even
though every reported collision receives an exact replay.  Passing unit tests
is not independent reproduction of a large census.

## Headline computation ledger

| Commit / session | Exact domain and normalization | Raw states | Canonical / retained states | Verification and controls | Certificate or data | Independent? | Audit disposition |
|---|---|---:|---:|---|---|---|---|
| `baae75a`, First Strike | All deletion-fixed local maps, order 4; none | 1,296 | none | exact union-find classes and colored backtracking; audit replay gives class histogram `440,524,250,69,12,1` | no frozen output; script and tests | order 4 replayed; same implementation | `EXACT-BOUNDED` |
| `baae75a`, First Strike | All deletion-fixed local maps, order 5; original raw product | 7,962,624 | none | same stack; multiplicity tested indirectly through realizations | no frozen output | later `sigma_dfs.c` is a genuinely separate C route: 1,658,880 conjugacy-normalized leaves, zero hits | `EXACT-BOUNDED`; independently reproduced for existence of a globalizer |
| `2076a75`, Length-2 Frontier | Order 6; every row a 3-cycle or double transposition; anchor a row of the available type and reject nonminimal prefixes under its centralizer | 53,281,250 anchored | 8,849,705 leaves | union-find plus exact colored backtracking; n=5 is the small control | no output artifact; `LENGTH2_PERMUTATION_FRONTIER.md` | no; later scripts reuse the same enumerator and canonicalizer | counts are `REPLAYABLE`, not independently certified; no-globalizer conclusion superseded by all-map order-6 census |
| `7919b80` / `d1c04e3`, Resilient lifts | Nonidentity leaves from the preceding census, quotient by full relabeling and side reversal; lift using every exact globalizer as row 7 | 3,181 source leaves | 467 primitive orbits; 11,410 lifts | same source stack; all 5,040 parent permutations used on lifts; tiny witnesses in tests | no machine-readable census output | no | `EXACT-BOUNDED`, single stack; structure not superseded |
| `930f41c`, Incidence joins | Six cycle-insertion choices per old row and four outside rows | 186,624 | 128 signatures; 47 joined arrays | union-find, incidence criterion, raw `S7` replay; regression trichotomy | markdown only | partial: two join representations, shared model | `EXACT-BOUNDED` for this insertion family |
| `ab55889`, Universal rescuer | All `6!` deletion-fixed rows for six deletions, filtered to preserve six old classes | 4,320 | 84 compatible rows; 78 effects; 5 terminals | union-find CSP and bitset DP; raw 5,040-permutation terminal replay | markdown only | partially independent state engine, shared row model | `EXACT-BOUNDED`; not a theorem for merged classes or other primitives |
| `dae7492`, Single merge | All 15 old-class pair merges and all deletion-fixed rows | 64,800 row trials | 1,524 compatible; 1,254 effects; 89 terminals | union-find and bitset DP; all minimum terminals replayed over `S7` | no frozen JSON | partially independent state engine | `EXACT-BOUNDED`; minimum is two globalizers |
| `d4eeb5f`, Double Goldilocks | 36 pairwise joins plus simultaneous two-merge row CSP | 4,320 row trials in simultaneous CSP | 432 compatible; 150 effects; 54 terminals | union-find, separate bitset joins/DP, raw `S7` replay | `docs/DOUBLE_GOLDILOCKS_CERTIFICATE.json` | strongest local evidence; algorithms still share definitions | `EXACT-BOUNDED`; one identity globalizer remains |
| `669c8dc` / `d556e08`, Covers | Fixed 12-class order-8 pseudosimilar base family; all asymmetric connected bases; gauge-normalized listed voltage ranks | 84,096 `C2`; 6,912 `C3`; 3,456 `S3`; 10,896 `S4` | 5,256; 218; 49; 681 digest buckets called parent/deck classes | exact canonical decks and separate parent backtracker after SHA-256 bucket selection; one representative retained per digest | `docs/COVERING_SPACE_CERTIFICATE.json` is summary-level | no external backend in committed replay | `SHA-CONDITIONED BOUNDED`; reported collisions are replayed exactly, but a digest collision can suppress a true later collision; does not close covers or pseudosimilarity |
| `8366214`, CFI / outer `S6` | All nontrivial cube subsets in dimensions 2–4 under odd cube isometries | 10; 246; 65,518 | zero release codes | exact subset/isometry check; general pure-translation proof separately | `docs/DELETION_FRAGILE_PARITY_CERTIFICATE.json` | tests call same routine | bounded isometry result; pure-translation mechanism is `THEOREM-CLOSED` |
| `79a3577`, exceptional `S6` | All invariant graphs on `6+6+15+15` under diagonal `S6`; no quotient by masks | 32,768 | 14,912 stable-deck-quotient buckets | stable quotient rejects; every collision-bucket pair mapped by an explicit carrier swap | `docs/EXCEPTIONAL_S6_DIRECT_CERTIFICATE.json` | purported raw verifier calls the primary classifier and swap-map code | `EXACT-BOUNDED`; 22,848 pairs are isomorphic-parent pairs, not nonisomorphic near-hits |
| `79a3577`, subgroup census | All subgroup conjugacy classes of `S6` by generator-chain closure | finite subgroup lattice | 56 classes; one unordered outer-balanced nonconjugate `V4` pair | exhaustive group closure and conjugation | summary in same JSON | no separate package | `EXACT-BOUNDED`; degree-180 Gassmann pair is a primitive, not a CE |
| `c36cc2a`, 12-column Gassmann | All `64 x 64` invariant incidence matrices on degree-180 rows | 4,096 | 284 bideck collisions | exact multiset-of-row isomorphism under arbitrary column permutations; all 284 parents isomorphic | no frozen output | audit replay reproduced counts using same code | `EXACT-BOUNDED` |
| `c36cc2a`, Johnson anchor | All 512 masks each side passing degree separation in parent and representative cards | 228,480 eligible pairs | 308 bideck collisions | exact canonicalization under the proved `S6` anchor automorphisms | no frozen output | audit replay reproduced counts using same code | `EXACT-BOUNDED`; parent order is 201 |
| `c36cc2a`, random matrix bideck | Seeded near-identity `7x7` local-map samples | 10,000 and 100,000 | 1,127 and 154 information-retaining | exact globalizer test; binary search skipped because all globalize | no data artifact | no | `HEURISTIC`; no architectural closure |
| `c36cc2a`, crossed holonomy | All 5,040 conjugates of one fixed order-7 primitive | 5,040 | maximum 19 classes; zero zero-globalizer | exact matrix globalizer search; unit test reruns domain | no output artifact | no | `EXACT-BOUNDED` for conjugates only |
| `ee6e32f`, Kocay trades | Kocay `n=3,4` source pairs and complete six-module `n=3` residue trade space | 64 labeled trade members | 40 parent types; six induced-deck collisions; zero trace/block/dual collisions | exact point permutation; split-graph regression retains repeated columns | `data/kocay_n3_pair.json` freezes source only | partial independent split-graph check at `n=3` | `EXACT-BOUNDED`; induced hypergraph deletion does not transfer |
| `6a84904`, all local maps | All local-map systems at orders 6 and 7; normalize `sigma_0` by conjugacy, prefix prune once a persistent globalizer appears | enormous implicit product | `n=6`: 7,362,848 nodes, 7,274,610 prunes, 26,880 leaves; `n=7`: 1,016,467,932 nodes, 1,015,056,170 prunes, zero leaves | C backtracker; order-5 full normalized control; chunk sums checked | no frozen output | no independent implementation | strongest campaign local-map frontier; `EXACT-BOUNDED`, single stack |
| `abdd07d`, STS screen | Two STS(13) and 79 Pasch-containing STS(15) reached by trade walk | 81 designs | all decks distinct | nauty-based deck comparison | no committed outputs | no | complete only for the named design list; not all incidence trades |
| `43313c1` onward, card fibres | All one-vertex extensions of each enumerated card, with automorphism-orbit reduction | varies: e.g. 7,997,524 cards through 16 edges; several sampled or interrupted families | silent fibres | nauty canonical forms reduced to 64-bit hashes | scratch outputs lost or partial | tournament positive control is strong, but graph dedup and parent equality are hash-dependent | downgrade from exact theorem to computational evidence |
| `16718cc` onward, deck-fixed SAT | Fixed `G`, existential full-deck mate `H`; exact blocking for small card-class group, custom lex-leader+CEGAR otherwise | many batches, sampled and exact subfamilies | UNSAT or seven unresolved order-20 cases | SAT plus pynauty and Python replay on SAT; dropped-card positive control caught an earlier unsound degree-group symmetry | mostly scratch output and log lines | no independent UNSAT proof/certificate | evidence only when custom lex-leader used; exact-blocking small-`W` runs are stronger |

## Contradictions, stale claims, and missing evidence

1. The linked branch ended at `e81cb8b`; another continuation reached
   `8870938`.  Their shared log diverged after `c3f093f`.  The histories have
   now been merged.
2. The first restart reported completed 29,923 quotient-8 blow-ups and 13,691
   Hong-regime graphs.  The second environment regenerated different feeds
   (29,928 and 14,413) and reran them.  These are different sampled batches,
   not one canonical census.
3. The handoff's five-hour estimate for order 8 was invalidated by measured
   chunk cost.  Two aborted runs each covered under two percent.  No order-8
   local-map result exists.
4. Seven dense order-20 bi-circulants reached both time and 100,001-round
   CEGAR limits.  The order-20 sample is not completely decided.
5. The Blue-LED document's targeted joins and further 50,000 asymmetric
   systems have no committed implementation or data.  Only the 5,040
   conjugates are auditable.
6. `verify_exceptional_s6_direct.py` is described as independent, but it calls
   `classify_combined_domain()` and `swap_mask_maps()` from the primary module.
   It is a raw consistency replay, not independent reproduction.
7. `sigma_dfs.c`'s header still says an unpruned order-5 run has `24^5`
   leaves.  After its stated conjugacy normalization the actual leaf count is
   `5*24^4 = 1,658,880`; the later plan gives the correct number.
8. No large census has a content-addressed output manifest.  Most headline
   values are prose plus runnable code; exact reproducibility therefore also
   depends on compiler, nauty, and environment versions not locked by the
   repository.
9. The cover search calls the number of occupied digest buckets
   `parent_deck_classes`.  That label is exact only assuming no SHA-256
   collision: the table retains one representative per digest, so a collision
   between unequal decks could hide a later equal-deck pair.  This audit made
   the implementation retain every exact deck per digest, but did not rerun
   the historical domains; their recorded counts remain SHA-conditioned.

## Conclusions stronger than the computation

- “Pseudosimilarity closed” is false: one fixed deletion map and its voltage
  lifts were tested.
- “Voltage covers closed” is false: four bounded voltage groups/ranks over one
  base family were tested.
- “Gassmann closed” is false: one `S6` pair with two invariant anchors was
  tested.
- “Incidence trades closed” is false: Kocay's induced-deletion source and one
  64-member residue space were tested.
- “Single merge” and “universal rescuer” are theorems only about the frozen
  six-class primitive and their exact compatibility hypotheses.
- Random or annealed sample completion is not exhaustive closure of the
  property used to generate the sample.
