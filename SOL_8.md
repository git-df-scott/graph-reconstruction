# SOL_8 — Dual-deck design-trade strike

```text
GRC CE: NO
```

Kocay's smallest explicit nonreconstructible 3-uniform hypergraph pair was
recovered exactly: 9 points, 28 blocks, nonisomorphic parents, and equal
standard induced point decks with multiplicities `1,2,2,2,2`.

The intended incidence transfer fails at a categorical boundary.  Standard
hypergraph point deletion discards incident blocks; matrix row deletion keeps
every block column and only erases the deleted incidence.  Under the required
operation, the Kocay pair has five row-card types on each side and zero types
in common.  At `n=4`, all nine row-card types again disagree.  Complements do
not repair this.

The exact six-generator residue-pair trade algebra around the `n=3` core was
then exhausted: 64 labeled members, 40 parent isomorphism types, six
nonisomorphic collisions under induced deletion, but zero collisions under
incidence-row deletion, block deletion, or both.  In this family, either
required deck separately reconstructs the parent.

The reusable obstruction is: a nonreconstructible uniform hypergraph is a
valid Blue-LED source only if its hypomorphy survives **trace deletion with
all block objects retained**.  Induced hypomorphy is insufficient.

The next credible address is a trace-nonreconstructible set system or a
paired trade that restores discarded incident blocks deletion-compatibly—not
a larger Kocay lift.

Full source data, exact counts, tests, and commands are in
`docs/DUAL_DECK_DESIGN_TRADE_STRIKE.md`.
