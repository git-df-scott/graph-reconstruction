# SOL_7 — Blue-LED incidence reset

```text
GRC CE: NO
```

The search was moved out of direct graph orbitals into deletion-faithful
two-sorted incidence matrices.  This produced three exact closures and one
new live construction address.

- Degree-180 `S6/H` versus `S6/K` on a 12-column ordinary/exotic anchor:
  4,096 pairs, 284 bideck collisions, all parent-isomorphic.
- The same Gassmann rows on a rigid 21-vertex point-duad Johnson anchor:
  228,480 degree-separated pairs, 308 bideck collisions, all
  parent-isomorphic.
- Stockmeyer's order-eight tournament card maps: all nine map choices collapse
  to two or four undirected classes and every one has an exact globalizer.
- First legal-order `7 x 7` bideck systems: 110,000 random near-identity
  systems and all 5,040 crossed holonomy conjugates; zero zero-globalizer
  systems.  The crossed systems retained up to 19 incidence classes but used
  only four rescues, and targeted joins regenerated identity or another core
  rescue.

The strongest new theorem is that a full group-invariant row family on a
rigid anchor cannot work: equality after one row deletion forces the invariant
row multiplicity functions to agree, restoring a parent isomorphism.

The next credible address is a non-invariant incidence/design trade whose
symmetry appears only after deletion, balanced under both point deletion and
block deletion.  Known nonreconstructible 3-uniform hypergraphs are the
source primitive to audit; their incidence graphs become ordinary GRC
candidates exactly when the dual/block-deletion decks also agree.

Full methods, counts, structural proofs, and reproduction commands are in
`docs/BLUE_LED_INCIDENCE_STRIKE.md`.
