# Astra handoff — hostile-audited GRC campaign

## Mission and current state

Find an explicit pair of nonisomorphic finite simple undirected graphs of the
same order at least three with identical complete vertex-deleted decks as
multisets.  No such pair is in the repository.  No current object qualifies
as a counterexample candidate (`CEC`).

Start from `CANONICAL_STATE_2026_09_04.md`, not an older `SOL_*` verdict or
the September 2 handoff.  The two divergent Claude branches have been merged.

## Do not rerun

- generic graph enumeration or blind order increases;
- order-4/5 local-map products;
- the 53,281,250-state order-6 3-cycle/double-transposition census;
- the 3,181-leaf / 467-orbit / 11,410-lift mining pass;
- fixed-carrier resilient couplings, universal-rescuer, single-merge, or
  double-Goldilocks searches;
- the fixed pseudosimilar base with the completed `C2`, `C3`, `S3`, or `S4`
  ranks;
- direct exceptional-`S6` orbital unions on 15 or 42 vertices;
- the two invariant `S6/V4` Gassmann anchors;
- Kocay `n=3,4` induced-hypergraph transfers or the 64-member residue trade;
- Stockmeyer same-carrier threshold rules and committed double covers;
- random near-identity `7x7` incidence systems;
- the existing order-14 Hong, cycle-type, blow-up, or random candidate feeds;
- order-8 named-colour search with the current prune.

Tiny regression runs and independent verifier controls are permitted.

## Exact strongest frontier

- External ordinary-graph frontier: every graph through order 13 (McKay).
- Campaign named-colour/local-map frontier: every local-map system through
  order 7 has an exact-label globalizer; order 6/7 is a replayable single C
  implementation without frozen result output.
- Best frozen local-map obstruction: simultaneous two-Goldilocks CSP retains
  exactly one identity globalizer in its strongest terminal.
- Legal-order bounded negatives: invariant exceptional-`S6` at 42; Gassmann
  incidence families at 192 and 201; and the Kocay-derived trade family.  The
  fixed cover runs at 16/24/32 are SHA-256-conditioned evidence rather than
  logically exact bounded closures.
- No campaign computation extends the unrestricted ordinary-graph order
  frontier.

## Known campaign mistakes

1. The linked branch omitted a later continuation; branch chronology was
   incomplete until this audit.
2. Order-8 named-colour cost was underestimated by roughly two orders of
   magnitude.  Both attempts stopped under two percent.
3. Seven order-20 bi-circulants are CEGAR timeouts, not negative results.
4. `card_fibre.c` can miss objects through 64-bit hash collisions in
   isomorphism-type deduplication and parent equality.  Repair before using a
   silent run as a theorem.
5. `deck_fixed_sat.py`'s custom lex-leader has no committed proof or UNSAT
   certificate route.  Tiny exhaustive controls passed, but large symmetry-
   reduced UNSAT batches are not independent certificates.
6. Blue-LED prose records targeted joins and a further 50,000-system run that
   are absent from code and data.  They are nonbinding.
7. Several “independent” verifiers call primary discovery functions.  Treat
   them as consistency replays.
8. Sample-complete feeds were sometimes described too close to class
   closures.  Preserve the sampled/exhaustive distinction.
9. Stable quotients and digests are filters, not deck certificates.
10. The historical cover search retained one representative per SHA-256 deck
    digest; a digest collision could suppress a true collision even though
    reported collisions were replayed exactly.  The storage logic is repaired
    for future runs; the historical counts were not rerun and remain
    SHA-conditioned.

## Best three remaining architectures

### 1. Shared-card automorphism cocycle

Construct one explicit card `C` with a rich local-isomorphism groupoid.  Solve
exactly for neighborhoods `N,N'` that lie in different `Aut(C)` orbits but
become equivalent after every deletion.  First experiment: build the full
action of card isomorphisms on neighborhood subsets and solve the all-card
CSP.  Stop only after one stated card family is orbit-exhausted or a pair is
emitted.

### 2. Trace-bideck incidence trade

Build a non-invariant paired trade whose row and column trace decks both
match after deletion.  First experiment: two overlapping small trade modules
with a rigid asymmetric anchor; solve module coefficients and local
permutations before binary realization.  Stop on invariant-row collapse,
degree exposure, or exact exhaustion of the named module basis.

### 3. Deletion-local monodromy

Seek locally conjugate, globally nonconjugate representations with a
nonfunctorial anchor.  First experiment: an asymmetric two-orbit partial
anchor over the `S6/V4` control pair, with double-coset variables and explicit
local conjugators.  Stop if the semilinear outer map survives, degrees reveal
carrier types, or the local conjugators globalize.

Details and ranking rationale are in `OPEN_ARCHITECTURES.md`.

## Mandatory CE protocol

When any process claims a hit:

1. stop the discovery run and serialize explicit `G,H` as graph6 and edge
   lists;
2. run `scripts/hostile_ce_checker.py` and save its JSON certificate;
3. require simple undirected parents, equal order at least three;
4. require both parent routes to say nonisomorphic;
5. require both deck routes to say equal with multiplicity;
6. replay parent and all cards with nauty/Traces or another mature independent
   backend where practical;
7. store sorted external canonical card labels with all occurrences;
8. aggressively search for a parent isomorphism after the apparent success;
9. commit the graphs, certificate, tool versions, and exact commands.

Only `VERIFIED_COUNTEREXAMPLE` from the standalone checker plus independent
external replay is a finished CE.  `CEC` means explicit `G,H` already pass
deck equality and await exactly one independent step.  A zero-globalizer,
SAT model, local-map survivor, hash collision, common-card maximum, or
nonisomorphic incidence source is not CEC.

## First commands

```bash
python3 -m unittest discover -s tests -v
python3 scripts/hostile_ce_checker.py --self-test --pretty
git status --short --branch
```

Then choose exactly one open architecture and write its domain and stop
condition before computation.  Do not spend unused budget on a broader
census.
