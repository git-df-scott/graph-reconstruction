# Literature check, 2026-09-01

Scope: what is actually known about the Kelly-Ulam graph reconstruction
conjecture as of September 2026, organised by what it constrains for a
counterexample hunt.  Companion to `GRC_AUDIT_2026-08-31.md`.  Every claim
below carries its source; items marked *not verified* could not be read in
full during this check.

## 1. The two-thirds barrier is gone

Bowler, Brown and Fenner (J. Graph Theory 63, 2010) built families of trees
and unicyclic graphs whose nonisomorphic members share `2 floor((n-1)/3)`
cards, and conjectured this is the maximum for `n >= 44`.

Ivanov (arXiv:2608.11930, 12 August 2026) refutes this.  An explicit
connected pair on 78 vertices shares at least 51 cards (the conjectured
maximum is 50), and for every even `r >= 4` there are families whose
overlap fraction tends to `1 - 1/r`.  Verified with nauty for `r=4, t=14`
(51 cards), `r=5, t=10` (54 cards), `r=5, t=100` (531 cards versus 352).

Mechanism.  `r` "ports" are blown up into independent false-twin classes of
sizes `(t+1, t+2, ..., t+r)` in `G` and `(t+2, t+1, t+3, ..., t+r)` in `H`.
A fixed selector gadget (`r` ports, `C(r,2)` pair vertices, `r!/(2(r/2)!)`
selector vertices) admits only even permutations of the ports.  `G` and `H`
differ by the odd transposition `(1 2)`, hence are nonisomorphic.  Deleting a
vertex from class `P_j`, `j >= 2`, makes two class sizes coincide, so the
forbidden transposition can be composed with a harmless one and becomes
even; those cards match.  Deleting from `P_1` produces a size vector with no
repeated entry, so matching would need an odd permutation, which the
selector forbids.  The selector and pair vertices also fail.  The unmatched
set is therefore one whole twin class of size about `n/r` plus `O(1)` gadget
vertices.

This is exactly the construction reproduced in `docs/FIRST_STRIKE.md` (78
vertices, 51 of 78; 234 vertices, 155 of 234), whose 27 unmatched deletions
are 15 from one port class, 6 pair vertices and 6 selector vertices.  The
obstruction to closing it is a deletion-released odd permutation, which is
the "deletion-fragile parity" problem attacked in `SOL_5.md`.

## 2. Computational verification

McKay, "Reconstruction of small graphs and digraphs", Australas. J. Combin.
83 (2022), arXiv:2102.01942.  Proves reconstruction (and Harary's set
reconstruction) for:

| class | verified through |
|---|---:|
| all graphs | 13 vertices |
| triangle-free | 16 |
| girth at least 5 | 20 |
| no 4-cycle | 19 |
| bipartite | 17 |
| bipartite, girth at least 6 | 24 |
| maximum degree at most 3 | 22 |
| degrees in `[0,5]` | 14 |
| degrees in `[5,6]` or `[6,7]` | 14 |
| degrees in `[0,4]` or `[4,5]` | 15 |
| degrees in `[3,4]` | 16 |

Cost: more than `6 x 10^13` graphs, about 1.5 CPU-years.  Method: canonical
construction path (geng) with parents grouped so that graphs with equal
reduced decks are children of the same parent; hash on edges and triangles
of cards, then degree-sequence invariant of the deck, then full card
isomorphism.  Tournaments verified through 13 vertices, digraphs through 8,
2-cycle-free digraphs through 9, posets through 13 points; semi-regular
tournaments on 14 vertices; no new digraph counterexamples.  Number of
graphs on 13 vertices: 50,502,031,367,952.

Consequence for an order-14 counterexample: it has a triangle, is not
bipartite, has maximum degree at least 6, and its degree set is not
contained in `{5,6}` or `{6,7}`.

Stolee checked edge reconstruction through 12 vertices.

## 3. Reductions

- Yang (JGT 1988): true if true for all 2-connected graphs.
- Ramachandran and Monikandan (2009): true iff true for 2-connected `G`
  with `diam(G) = 2` or `diam(G) = diam(complement) = 3`.  Separable
  graphs of diameter 2 are reconstructible.
- Gupta, Mangal, Paliwal (2013): diameter 2 is recognizable.
- Radius reduction (Monikandan, IntechOpen 2021 survey): true if all
  2-connected graphs of radius 2 are reconstructible.
- Aravind and Monikandan (arXiv:2601.00620, January 2026): domination
  number 2 is recognizable; reduction to 2-connected graphs with stated
  diameter and domination conditions, via new vertex-pair parameters.

## 4. Reconstructible classes and single-graph sufficient conditions

Classical (Bondy-Hemminger 1977; Lauri 2013 handbook chapter): regular,
trees, disconnected, separable without end vertices, maximal planar,
maximal outerplanar, outerplanar, unicyclic, unit interval, critical
blocks, graphs with a universal vertex.  Recent: bipartite permutation
graphs (2010), interval graphs (arXiv:2504.02353, 2025-26).

Sufficient conditions on one graph:

- Chinn: if the `(n-2)`-vertex subgraphs are pairwise nonisomorphic, or
  some card has pairwise nonisomorphic subcards, then reconstructible.  So
  every card of a counterexample contains two vertices whose deletion gives
  isomorphic subcards.
- Farhadian (arXiv:1611.01609): anchors; any non-vertex-transitive graph has
  a proper induced subgraph unique by structure or attachment; graphs with
  an asymmetric unique subgraph of order `n-2` are reconstructible.
- Wang, Wen, Guo (arXiv:2408.02488, 2024): if some card is controllable
  (walk matrix `[e, Ae, ..., A^{n-2}e]` of full rank), `G` is
  reconstructible; also if some card is almost controllable and has a
  nontrivial automorphism.  O'Rourke and Touri (SIAM J. Control 2016) proved
  Godsil's conjecture that almost all graphs are controllable.  So every card
  of a counterexample has a non-main eigenvalue.
- Liu and Siemons (J. Algebraic Combin. 2021): a walk matrix of rank at
  least `n-1` determines the adjacency matrix; sharp.

## 5. Reconstructible invariants

- Kelly's lemma: every proper subgraph count, induced or not.
- Tutte (1979): characteristic polynomial, chromatic polynomial, rank and
  Tutte polynomials, number of spanning trees, number of Hamiltonian cycles.
  Graphs with irreducible characteristic polynomial are reconstructible.
- Kocay (1981, 1982): every disconnected spanning subgraph count; Kocay's
  lemma gives a linear constraint per sequence of graphs.
- Knierim and Martinsson (arXiv:2112.03366): clique counts from `n-1` cards.
- Groenland et al. (JGT 2021): size from any `n-2` cards; Myrvold: degree
  sequence from any `n-1` cards.
- Kim and Lee (arXiv:2501.19081, 2025): matching polynomial of `k`-uniform
  hypergraphs, and the number of `F`-factors of a graph.
- Spier (arXiv:2503.17853, 2025): efficient reconstruction of the
  characteristic polynomial.
- Arvind, Köbler, Verbitsky (arXiv:2406.09351): connectedness is
  determined even when cards are given only up to color-refinement
  equivalence.

Open: Kocay's question whether the number of spanning trees of each
isomorphism type is reconstructible (cited by Thatte, EJC 2005 and JGT
2020).  Whether hypomorphic graphs are always fractionally isomorphic (same
color-refinement partition) was not found stated anywhere.

Derived necessary condition, not found stated explicitly in the literature
but immediate from Tutte plus complementation: a counterexample pair is
generalized cospectral.  Johnson and Newman then give a rational orthogonal
`Q` with `Q^T A Q = B` and `Q e = e`.  Wang's theorem: if
`det W / 2^{floor(n/2)}` is odd and square-free the graph is determined by
its generalized spectrum; a counterexample must violate this.

## 6. Algebraic formulations

- Thatte and Oliveira (JGT 2016, arXiv:1301.4121): reconstruction holds at
  order `n` iff `psi(n) = d(n)` (graphs versus decks); `d(n)` is at least
  the real rank of any matrix of Kocay covering numbers.  No numerical ranks
  are reported.  A small-order computation of the "Kocay kernel" appears not
  to exist in the literature.
- Thatte (EJC 2005): the N-matrix of induced subgraph types determines the
  characteristic polynomial, rank polynomial and spanning tree count;
  Ulam's conjecture is equivalent to the N-matrix being a complete invariant.
  Thatte (arXiv:math/0609574; JGT 2020): subgraph posets, connected
  partition lattice.
- Stark (arXiv:2509.02604, 2025): generalizes Kocay's lemma to abstract
  systems and to 2-edge-coloured graphs; states that the conjecture is
  equivalent to reconstructing using Kocay sums alone, with no bound on
  the number of applications.
- Dufresne, Jeronimo, Kenkel, Lindo, Villamizar (arXiv:2604.16567, April
  2026): expository invariant-theory framing; no new theorem.
- Bowler et al. survey of reconstruction numbers; Bollobás: almost every
  graph is determined by three cards; Myrvold: adversary reconstruction
  number 3 for almost all graphs.

## 7. Coloured and relational variants

- Kelly's lemma holds for edge-coloured graphs (noted in
  arXiv:2308.01671); Stark's Theorem 2 gives Kocay's lemma for
  2-edge-coloured graphs.
- "The double reconstruction conjectures about colored hypergraphs and
  colored directed graphs" (Springer Lecture Notes in Mathematics, mid
  1980s; author and abstract *not verified*, paywalled): two conjectures;
  the first restricted to simple graphs is equivalent to Ulam; Kocay's
  hypomorphic 3-hypergraph pairs do not satisfy its hypotheses; the second
  implies Ulam.
- No published counterexample to reconstruction of edge-coloured complete
  graphs with named colours was located, and no census at orders 6 or 7
  was found.  The order-4 and order-5 censuses in this repository are, as
  far as this check can tell, the only complete data.
- Binary relational structures: Fraïssé, Lopez, Pouzet, Ille on
  `(<= k)`-hypomorphy and `(<= k)`-reconstructibility; Dammak, Lopez,
  Pouzet, Si Kaddour (JCTB 2009) on hypomorphy up to complementation.

## 8. Neighbouring conjectures that fail

- Tournaments and digraphs (Stockmeyer 1977, 1981, 1982, 1988; Kocay 1985):
  pairs at orders 3, 4, 5, 6 and 8; all orders `2^t+1`, `2^t+2`,
  `2^s+2^t`; none at order 7; McKay confirms nothing new through 13.
  Ramachandran's new digraph reconstruction conjecture survives all known
  pairs.  Ramachandran (AKCE 2022) identifies a property shared by nine of
  the ten known infinite families (*details not verified*, paywalled).
- 3-uniform hypergraphs: Kocay (JCTB 1987) infinite family; the smallest
  nonreconstructible 3-hypergraphs have 5 vertices and 5 triples; all with
  at most 8 vertices and 11 triples are classified (Graphs and Combin. 32,
  2016).  Cooper and Okur (arXiv:2312.16152) show Kocay's pairs have
  different characteristic polynomials.
- Infinite graphs (Fisher 1969; Bowler et al. 2017 locally finite trees).
- Smaller decks: Spinoza and West show `P_n` and `C_{n/2} + P_{n/2-1}`
  share every `l`-deck with `l <= n/2`; Kostochka and West survey
  (arXiv:2004.05527) the `l`-reconstruction conjecture.

## 9. Pseudosimilarity

- Kimble, Schwenk, Stockmeyer (JGT 1981): graphs with trivial automorphism
  group in which every vertex is pseudosimilar to another; `k` mutually
  pseudosimilar vertices on `O(k^2)` vertices.
- Godsil and Kocay (JCTB 1982): one construction yields all graphs with a
  pseudosimilar pair.  Lauri: large pseudosimilar sets.  Ellingham (JGT
  1991): vertex-switching and pseudosimilarity.  Lauri and Scapellato,
  *Topics in Graph Automorphisms and Reconstruction*, chapter 5.

## 10. Computer-assisted and AI work

- No published SAT or constraint-programming attack on the vertex
  reconstruction conjecture was found.  SAT-modulo-symmetries has been used
  on other graph conjectures (3-decomposition to 28 vertices).
- Tsoukalas et al. (arXiv:2605.22763, DeepMind, May 2026): Lean proof of a
  "weak bipartite" variant with an incidence-deletion deck, biconnectedness
  and pairwise distinct vertex types; full paper in preparation.
- ProofAtlas (August 2026) lists "deck-to-quadratic-frame" and
  "walk-corank-three" routes as active; *not verified* against primary
  sources.

## 11. Disputed proof claims

O'Shea and Wilkins (Information Sciences 654, 2023; corrigendum 2024);
arXiv:1712.10322; arXiv:1704.01454.  None is accepted; every 2026
specialist source treats the conjecture as open.

## 12. What this changes for the campaign

1. The strongest known near-miss is the one already in
   `docs/FIRST_STRIKE.md`; its unmatched set is a full twin class, and the
   obstruction is a deletion-released odd permutation.  Any repair is the
   `SOL_5` problem in disguise.
2. Two unused hard filters: every card of a counterexample is
   non-controllable, and the pair is generalized cospectral with Wang's
   determinant condition failing.  Both are cheap and were not applied to
   any legal-order search in this repository.
3. Every card of a counterexample has a repeated subcard (Chinn).
4. The Kocay covering-number rank at small orders has not been computed
   anywhere found.
5. Named-colour reconstruction at orders 6 and 7 has no published census.
6. At order 14 the degree-range and girth classes of McKay's Theorem 3.1
   are already closed.
