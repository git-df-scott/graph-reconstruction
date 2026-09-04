# Canonical GRC campaign state — 2026-09-04

## Binding verdict

No counterexample has been produced.  In particular, the repository contains
no explicit nonisomorphic simple graphs of order at least three whose complete
vertex-deleted decks are equal as multisets.

The hostile audit merged the two divergent continuations
`claude/grc-counterexample-35nwgv` and
`claude/grc-counterexample-campaign-7ls9wm`.  Claims below are classified by
what the committed record actually supports, not by their original wording.

## Strongest external frontier

- McKay's published computation verifies the ordinary conjecture for every
  graph through order 13.  The published larger-class frontiers remain the
  controlling external computational bounds; this campaign did not extend
  the unrestricted order frontier.
- No post-2022 unrestricted census was found in the targeted 2025–September
  2026 update search.
- Ivanov's 2026 construction gives nonisomorphic graphs with deck overlap
  arbitrarily close to one, but never a complete equal deck.

## Strongest campaign results that survived audit

1. **Local-map implication is sound.**  A complete family of deletion maps
   generates edge-equality classes.  Every binary assignment has equal decks
   with multiplicity.  An exact-label globalizer is a parent isomorphism for
   every assignment.  Its absence is necessary, not sufficient, for a CE.
2. **All local-map systems at orders 4 and 5 globalize.**  The original raw
   domains contain 1,296 and 7,962,624 systems.  The order-4 run was replayed
   during this audit.  A separate C implementation replayed the complete
   order-5 domain after a valid conjugacy normalization: 1,658,880 normalized
   leaves, zero hits.
3. **All local-map systems at orders 6 and 7 globalize in the later branch.**
   `sigma_dfs.c` records complete prefix-pruned searches with zero hits.  This
   supersedes the restricted order-6 length-two census as a no-globalizer
   result, but the output was not frozen and the implementation has not been
   independently reproduced.
4. **The length-two structural data remain useful.**  In the 3-cycle/double-
   transposition order-6 domain: 53,281,250 raw anchored states, 8,849,705
   residual-canonical leaves, 3,181 nonidentity-rescued leaves, 467 full
   relabeling/side-reversal orbits, and 11,410 legitimate order-7 lifts.  No
   zero-globalizer object was reported.  These numbers are replayable but
   share one enumeration/canonicalization stack and lack frozen raw output.
5. **The fixed Goldilocks carrier is exhausted only in stated subclasses.**
   Universal-rescuer, one-merge, and two-merge searches bottom out at four,
   two, and one exact-label globalizers respectively.  They do not prove an
   obstruction for other primitives or carriers.
6. **Several legal-order structured domains produced bounded negatives.**
   The exceptional-`S6` orbital unions, two Gassmann incidence anchors, and
   the 64-member Kocay residue trade space contain no CE in their exact stated
   domains.  The fixed pseudosimilar-base voltage runs are SHA-256-conditioned:
   exact decks are compared after digest bucketing, but only one representative
   is retained per digest, so a digest collision could suppress a later true
   collision.  The audit repaired that storage logic for future runs but did
   not rerun the closed campaign.  None closes voltage covers,
   pseudosimilarity, Gassmann constructions, or incidence trades in general.
7. **Three general obstruction proofs survive.**  Pure odd-translation CFI
   deletion release forces a singleton code; transitive orbital graphs are
   regular and reconstructible; a functorial outer twist is defeated by the
   semilinear coset bijection.

## Audit corrections that are now binding

- The linked branch was not the complete record.  It omitted the later
  continuation through `8870938`; the histories are now merged.
- The order-8 named-colour census was stopped below two percent after a revised
  estimate of three to four CPU-weeks.  Order 7, not order 8, is the completed
  frontier.
- Seven order-20 bi-circulants remain unresolved after the CEGAR limit.  They
  are timeouts, not negatives and not candidates.
- The large self-complementary-card, 18-edge sparse-card, and several
  order-13 cycle-type fibre runs were interrupted or incomplete.
- `card_fibre.c` is not collision-safe.  A 64-bit FNV value is used both to
  deduplicate card isomorphism types and to treat parents as the same.  A hash
  collision can suppress a candidate.  Silent-fibre claims are evidence, not
  exact finite theorems, until this is repaired or collision-freedom is
  certified.
- The large `deck_fixed_sat.py` negative batches depend on a custom
  adjacent-row lex-leader whose orbit-preservation is not proved in the
  repository.  It passed exhaustive tiny controls through order 6 in this
  audit, but large UNSAT claims remain single-stack computational evidence.
- Blue-LED's claimed pair/triple/four-way joins and additional 50,000-system
  asymmetric run have no committed implementation, certificate, or data.
  They are not binding.

## Canonical CE gate

The independent checker is `scripts/hostile_ce_checker.py`.  A future claim
must serialize both graphs and receive `VERIFIED_COUNTEREXAMPLE` from this
checker, followed where practical by nauty/Traces replay.  `CEC` is reserved
for explicit `G,H` with deck equality already established and exactly one
independent verification step outstanding.  No current object is CEC.

See `CLAIM_AUDIT.md`, `CLOSED_LANES.md`, `VERIFIER_AUDIT.md`,
`LITERATURE_DELTA.md`, `OPEN_ARCHITECTURES.md`, and `ASTRA_HANDOFF.md` for the
evidence and continuation protocol.
