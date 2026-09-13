# SOL_9 — Coloured-parity carrier and the Ivanov selector

```text
GRC CE: NO
```

Two results. Ivanov's August 2026 near-miss family is reproduced exactly and
its true deficit computed, which closes it. That closure yields a gadget
condition identical in logical form to SOL_5's mechanism but on a carrier the
SOL_5 theorem does not cover; that carrier is swept to order seven and is
empty.

## Ledger gap closed

`GRC_AUDIT_2026-08-31.md` predates

- S. Ivanov, *Nonisomorphic Graphs Can Share an Arbitrarily Large Fraction of
  Their Vertex-Deleted Cards*, [arXiv:2608.11930](https://arxiv.org/abs/2608.11930),
  12 August 2026

by nineteen days, and the source ledger does not carry it. It refutes the
Bowler–Brown–Fenner conjecture and builds, for every even `r >= 4`, families
whose common-card fraction tends to `1 - 1/r`. It is the strongest explicit
near-miss in the literature and it is legal order.

## Ivanov's family is closed on the deficit

`scripts/ivanov_selector.py` rebuilds the gadget from the Lemma 2.1 adjacency
and reproduces Theorem 2.2 independently: `n = 78`, equal degree sequences,
parents nonisomorphic, and

```text
b(G,H) = 51    exactly
```

The paper proves only `b >= 51`. The bound is tight: deleting a selector
vertex does **not** restore the odd port permutation, so every selector card
stays unmatched.

Scanning port-class sizes `1..6` gives 360 valid nonisomorphic pairs:

```text
minimum deficit n - b : 13, at sizes (1,2,3,4), n = 22, b = 9
deficits attained     : 13,14,...,23
deficit 0             : never
```

The floor is the gadget. Its twelve vertices always contribute unmatched
cards, so no member of this family reaches deficit zero. **The fraction is the
wrong statistic.** As `t` grows the fraction rises toward `1 - 1/r` while the
absolute deficit diverges: for `r = 4` it is at most 14 at `t = 1` and at most
1013 at `t = 1000`. A counterexample needs deficit exactly zero, and every
construction that improves the fraction makes the deficit worse.

## The condition this forces, and its relation to SOL_5

For a pair of Ivanov shape to reach deficit zero its gadget must

```text
(a) forbid the odd port permutation        -- else the parents are isomorphic
(b) admit it after every single deletion   -- else that gadget card is unmatched
```

This is exactly the SOL_5 mechanism: a global parity obstruction that
dissolves after every single vertex deletion. SOL_5 closed the **binary CFI
code** carrier. The **port-coloured** carrier is the same logical form and is
not covered by that theorem.

Write a gadget as `(S, sigma)` with `sigma : V(S) -> {0,+,-}` and `tau0`
flipping `+` and `-`. Then (a) says `(S,sigma)` is not isomorphic to
`(S,tau0.sigma)` and (b) says their coloured decks are equal as multisets.

## Proved: equal coloured decks force `#(+) = #(-)`

Every vertex lies in exactly `m-1` cards, so summing colour counts over the
deck gives `(m-1)` times the parent's colour count. The coloured multiset is
therefore deck-reconstructible. `X` has `(p,q,z)` and `Y` has `(q,p,z)`, so
equal decks force `p = q`. Used as an exact prune, worth 4.8x at `m = 5`.

The same argument shows **Kelly's Lemma holds verbatim in the coloured
category**. The coloured gadget problem is therefore not a weaker problem than
GRC; it is GRC's difficulty at smaller order. What it buys is only that
McKay's `n <= 13` verification says nothing about coloured graphs, so small
`m` is genuinely unsearched.

## Coloured-parity sweep

`scripts/coloured_parity_gadget.py`, exhaustive over `geng` output, with the
`p = q` prune applied:

| m | gadgets tested (cumulative) | hits |
|---:|---:|---:|
| 2 | 2 | 0 |
| 3 | 14 | 0 |
| 4 | 113 | 0 |
| 5 | 963 | 0 |
| 6 | 11,883 | 0 |
| 7 | 216,507 | 0 |

Coloured canonical forms go through nauty by a faithful pendant-path encoding
whose lengths exceed the gadget order, so no pendant is confusable with gadget
structure. No hash equality is accepted as a certificate.

## Correction to an earlier sweep in this session

A first version of the gadget search demanded an automorphism of `S - v`,
matching card `v` only to card `v`. Deck equality needs `S - v` isomorphic to
`S - w` for **some** `w`. That sweep (570,825 gadgets, `m <= 4`) was strictly
too narrow and its negative is weaker than it looked. The table above is the
corrected condition. The error is recorded rather than silently replaced.

## Controls

The engine reproduces the literature before being trusted: zero deck
collisions over every nonisomorphic graph on `3..9` vertices, and exactly one
collision at `n = 2`, the classical `K2` exception. It therefore finds real
collisions and invents none.

Cai–Fürer–Immerman pairs were tested as counterexample candidates over eight
base graphs, `n = 12..60`: every pair shares **0** of `n` cards. Bounded
Weisfeiler–Leman indistinguishability buys nothing against a deck. That axis
is closed.

A direct deck-collision scan over false-twin blowups of cores with at most six
vertices, `n = 10..16`, found no collisions (520,333 blowups at `n = 16`,
108,588 distinct after canonicalisation). Caveat: that family cannot contain
Ivanov-shaped pairs, whose core exceeds sixteen vertices, so its negative is
weak evidence.

## Theorem status

- **Proved generally:** equal coloured decks force `#(+) = #(-)`; Kelly's
  Lemma holds in the coloured category.
- **Computationally exhaustive:** `b(G,H) = 51` for Ivanov's `n = 78` pair;
  minimum deficit 13 over the size-`1..6` selector family; zero coloured
  parity gadgets through `m = 7`.
- **Not claimed:** any statement for `m >= 8`, for `r > 4` ports, for more
  than one swapped pair of colours, or for selectors outside Ivanov's shape.

## Exactly one next strike

Extend the coloured sweep to `m = 8` under the proved `p = q` prune, and in
parallel allow **two** independent swapped colour pairs rather than one. The
single-pair carrier is now closed through seven; a second pair is the smallest
hypothesis relaxation not already covered, and it is the coloured analogue of
the complementary-merge coupling SOL_3 closed on the merge carrier.

Realization stays forbidden until a gadget satisfying (a) and (b) exists.
