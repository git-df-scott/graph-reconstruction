# SOL_6 — Exceptional-S6 direct strike

```text
GRC CE: NO
```

The direct exceptional-`S6` lead has been decided exactly.

On the natural 15-element duad carrier there are only two unordered-pair
orbitals and four invariant graphs.  Outer twisting does not change the
permutation group, and every transitive orbital graph is regular, hence
reconstructible from one card.

The minimal irregular extension uses all four natural carriers

```text
6 points + 6 totals + 15 duads + 15 synthemes = 42 vertices.
```

Its diagonal `S6` action has 15 pair orbitals.  All `2^15 = 32,768` invariant
simple graphs were classified.  There are 14,912 stable deck-quotient
classes and 22,848 exact deck-collision pairs, but every collision has an
explicit parent isomorphism: 3,840 swap only the 15-carriers, 3,520 swap only
the 6-carriers, and 15,488 use the full semilinear swap.  There are zero
nonisomorphic deck collisions.

The structural obstruction is general.  For a group automorphism `alpha`,

```text
gH -> alpha(g) alpha(H)
```

is an ordinary vertex bijection carrying every functorial outer-twisted
relation to its mate.  Thus outer-action nonconjugacy is killed by a graph
isomorphism outside the intended group action.

The exact `S6` subgroup classification nevertheless found a stronger
survivor.  Among all 56 subgroup conjugacy classes there is exactly one
unordered outer-balanced nonconjugate pair:

```text
H = <(0 1)(2 3), (0 2)(1 3)>
K = <(0 1)(2 3), (0 1)(4 5)>.
```

Both are `V4`, with the identity and three double transpositions.  They are
almost conjugate but not conjugate: `H` has two common fixed points and `K`
has none.  Their coset actions have degree 180.  This is a genuine
Gassmann/Sunada primitive, not a counterexample; direct coset orbital graphs
remain regular and reconstructible.

The next exact address is a degree-balanced partial coupling on

```text
S6/H + ordinary 6-anchor + exotic 6-anchor
```

versus the corresponding `S6/K` carrier, at order 192.  The partial coupling
must break the full semilinear swap while keeping all deletion types
indistinguishable.  Its variables are stabilizer double cosets and cross
orbitals, not arbitrary graph edges.

Complete proofs, counts, reproduction commands, and resource data are in
`docs/EXCEPTIONAL_S6_DIRECT_STRIKE.md`.
