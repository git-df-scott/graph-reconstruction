# Heterogeneous incidence-join strike

Date: 2026-08-31

## Verdict

`GRC CE: NO`

No zero-globalizer gadget, binary realization, or legal-order parent pair was
found.  This strike closes one new finite heterogeneous extension-row domain;
it does not repeat the closed carrier-twist coupling domains.

## Exact incidence signature

For a complete local-map system `A`, let `P_A` be its equality partition of

```text
Omega = {G,H} x E(K_n).
```

For two systems `A,B`, their colored bipartite incidence multigraph has one
left vertex for every class of `P_A`, one right vertex for every class of
`P_B`, and one incidence edge for every slot `omega in Omega`.  The edge for
`omega` joins its `P_A` and `P_B` classes and retains the full color
`omega=(side,{u,v})`.  The implementation canonically renames the two class
sets from their colored-slot supports.  It does not replace this object by an
intersection-size histogram.

The following facts are immediate and exact.

1. The connected components of the incidence graph are precisely the classes
   of the joined partition `P_A join P_B`.
2. Write `kappa(side,e)` for the component containing slot `(side,e)`.  A
   parent permutation `p` is an exact-label globalizer if and only if

   ```text
   kappa(G,e) = kappa(H,p(e)) for every e in E(K_n).
   ```

3. Identity rescue is exactly the special case `p=id`.
4. An old rescue survives exactly when it satisfies the same component test.
5. Emergent rescues are the permutations satisfying the component test but
   absent from the orientation-correct old rescue intersection.

Thus the colored incidence signature is sufficient to predict joined class
count, both parent-side arrays, identity rescue, every surviving old rescue,
and every emergent rescue.  These are necessary-and-sufficient criteria, not
heuristics.

## Incidence explanation of the certified trichotomy

Three fixed representatives from the already-closed strongest-lift coupling
domain were replayed through the incidence classifier alone.

| Regime | Twist | Components | Exact globalizers | Incidence feature |
|---|---|---:|---:|---|
| Compatible | `(0,1,2,3,4,5,6)` | 9 | 4 | Nine original components remain; the A4 rescue torsor survives. |
| Partial frustration | `(0,1,3,2,4,5,6)` | 7 | 24 | Two asymmetric distinctions merge; the component coloring admits the S4 action and identity. |
| Strong frustration | `(0,1,2,4,3,5,6)` | 4 | 120 | Paired side slots share components, so identity satisfies the component criterion. |

The exact general criterion is the component equation above.  In this
regression object, compatible incidence preserves the nine-component A4
coloring on vertices `{0,1,2,3}`.  In the partial signature the two side
arrays become identical; all six edges inside `{0,1,2,3}` receive one color,
while edges from that set to each of `4,5,6` receive a color depending only on
the fixed endpoint.  This is exactly invariant under S4 on the four-vertex
block, giving 24 globalizers.  In the strong representative the identical
side coloring makes all ten edges inside `{0,1,2,3,4}` one color, edges from
that block to 5 and 6 two further colors, and edge `{5,6}` a fourth.  It is
exactly invariant under S5 on the five-vertex block, giving 120 globalizers.
A successful fourth outcome must have no permutation satisfying the
component equation.  In particular it must destroy the universal survivor
identified below without making `kappa(G,e)=kappa(H,e)` for all edges.

## New heterogeneous domain

Let `sigma_i` be row `i` of the certified six-vertex, six-class primitive.
For each old deletion `i`, insert the new symbol 6 into the cycle notation of
`sigma_i` either as a fixed point or immediately after any of the five old
symbols other than `i`.  There are exactly six choices per row.  Equivalently,
for insertion after `v`, set

```text
tau_i(v)=6, tau_i(6)=sigma_i(v), tau_i(x)=sigma_i(x) otherwise.
```

Every `tau_i` is a genuine permutation fixing `i`, and deleting symbol 6 from
its cycles recovers `sigma_i`.  For deletion 6, each of the four certified old
rescuers is allowed, extended by fixing 6.  The complete raw domain is

```text
6^6 * 4 = 186,624 systems.
```

Each was joined with the certified nine-class fixed-point lift.  All rows were
validated before use.  The four outside-row choices were retained in the raw
replay even where they induce the same incidence result.

## Exhaustive result

The raw 186,624 systems reduce to 128 fixed-carrier colored incidence
signatures and 47 distinct joined parent-side arrays.

Joined class distribution:

```text
1: 54,400   2: 91,080   3: 13,860   4: 25,776   5: 1,012
6:    240   7:    244   8:      8   9:      4
```

Old-rescue intersection distribution:

```text
1:     12
2:  1,284
4: 185,328
0:      0
```

More strongly, rescuer index 1,

```text
(1,3,2,0,4,5,6),
```

survives every one of the 186,624 systems.  The only observed rescue subsets,
using the certified ordering `(r0,r1,r2,r3)`, are

```text
{r1}:                12
{r0,r1}:            428
{r1,r2}:            428
{r1,r3}:            428
{r0,r1,r2,r3}:  185,328
```

This is a computationally exhaustive universal-survivor theorem for the
cycle-insertion domain.  It answers the primary filter before any binary
search: empty old-rescue intersection is impossible here.

The most information-retaining weakened systems have seven joined classes
and two old rescuers (12 systems); all have eight exact globalizers.  The only
one-rescuer systems have two or four joined classes, and their total exact
globalizer counts are respectively 720 and 120.  Thus approaching one old
rescuer in this domain already regenerates much larger symmetry.

For completeness, exact colored-graph backtracking was performed once for
each of the 47 distinct joined side arrays and weighted back to the raw
systems.  Globalizer counts range over

```text
4, 8, 16, 24, 48, 120, 240, 720, 5,040;
```

zero never occurs.  The full joint histogram is emitted deterministically by
`scripts/incidence_join_strike.py`.  A separate `--raw-s7-replay` pass checks
all 5,040 permutations on each of the 47 arrays and must agree exactly with
the backtracking enumerator.

## Status of realization and legal order

Because every system has an exact-label globalizer, binary assignment was
correctly skipped.  There are no realized order-seven parents from this
strike, no zero-globalizer gadget to embed, and no legal-order construction at
order at least 14.

## Proof status

- **Proved generally:** incidence components equal partition joins; the
  component equation is necessary and sufficient for exact globalizers,
  identity rescue, surviving old rescue, and emergent rescue.
- **Computationally exhaustive in the stated finite domain:** all 186,624
  valid cycle-insertion families, 128 signatures, 47 joined arrays, universal
  survival of `r1`, all class/intersection/globalizer distributions, and zero
  zero-globalizer systems.
- **Regression-exact:** the 9/4, 7/24, and 4/120 representatives reproduce the
  compatible/partial/strong trichotomy from incidence data alone.
- **Not claimed:** an analytic proof that `r1` survives outside this finite
  cycle-insertion domain, or any conclusion about arbitrary heterogeneous
  extension rows.

## Verification and resources

The hardened repository suite passes 22/22 tests, including four new tests
for genuine cycle-insertion rows, direct union-find/incidence-join agreement,
the exact globalizer criterion, and the trichotomy regression.  The hostile
raw replay checked all `7!` permutations on all 47 distinct joined side
arrays and agreed with the independent backtracking enumerator.

The raw search plus replay used 24.0 seconds wall time and 16,256 KiB peak RSS
on this host.  No binary SAT, graph realization, generic graph enumeration,
or order scaling was run.

## Next strike

Enumerate **row substitutions that break `r1` individually**: for each
deletion `i`, classify all permutations of seven vertices fixing `i` whose
old-edge equations remain compatible with the six-class primitive, retain
only rows whose colored incidence excludes the universal survivor, and solve
the resulting six-row exact-cover/CSP before constructing complete families.
This is the smallest successor because it attacks the newly certified common
rescuer directly and avoids enumerating the full product of arbitrary rows.
