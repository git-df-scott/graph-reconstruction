# Literature delta — 2025 through 2026-09-04

This is a targeted update, not a new general survey.  Primary papers were
checked for changes to the campaign's frontier.

## Changes that matter

### High-overlap pairs

Ivanov proves that the old proposed upper bound on the number of common cards
is false.  The paper gives a connected nonisomorphic pair on 78 vertices with
51 common cards and, for every even `r >= 4`, families whose common-card
fraction approaches at least `1-1/r`.  It explicitly separates this from the
ordinary Reconstruction Conjecture: none of the pairs has a complete equal
deck.  The paper's finite table also contains compact odd-port computational
checks, including order 81 with 54 common cards and order 531 with 414 common
cards.  [Ivanov, arXiv:2608.11930](https://arxiv.org/abs/2608.11930)

Campaign effect: near-total overlap is no longer evidence of closeness to a
CE unless the unmatched deletion types are repaired by a new mechanism.

### Diameter/connectivity and triangle-free reductions

The August 24, 2026 revision by Clifton, Liu, Mahmoud, and Shantanam proves
reconstructibility for triangle-free graphs in the co-diameter-three class
and for triangle-free diameter-two graphs of connectivity three.  Within the
standard reduction to two-connected graphs of diameter two or simultaneous
diameter/co-diameter three, the remaining triangle-free case is diameter two
with connectivity at least four.  The paper also proves edge-reconstruction
analogues.  [Reconstruction and Edge Reconstruction of Triangle-free
Graphs, arXiv:2210.00338v2](https://arxiv.org/abs/2210.00338)

Campaign effect: any search deliberately restricted to the standard critical
diameter classes should prioritize graphs with triangles, except for the
remaining high-connectivity triangle-free diameter-two case.

### Domination reduction

Aravind and Monikandan prove that domination number two is recognizable and
reduce the conjecture to specified two-connected graphs involving domination
number two or diameter two for a graph and its complement.  They also
introduce reconstructible vertex-pair parameters.  [A Reduction of the
Reconstruction Conjecture using Domination and Vertex Pair Parameters,
arXiv:2601.00620](https://arxiv.org/abs/2601.00620)

Campaign effect: this is a structural targeting constraint, not an order
frontier and not a license to discard all domination-number-two candidates as
reconstructible.

### Newly reconstructed class

Interval graphs are reconstructible; version 2 is dated May 12, 2026.  The
result is a genuine class theorem, not a small-order computation.  [Heinrich,
Kiyomi, Otachi, Schweitzer, arXiv:2504.02353](https://arxiv.org/abs/2504.02353)

Campaign effect: interval-graph candidate feeds are closed by theorem.

### Algebraic reframings

Grochow's 2026 paper identifies reconstruction from `k`-vertex-deleted cards
with identification by invariants of bounded support-degree.  This is a useful
representation-theoretic translation but does not narrow the known simple-
graph order frontier.  [Graph Isomorphism and Representation Theory,
arXiv:2606.26244](https://arxiv.org/abs/2606.26244)

Dufresne, Jeronimo, Kenkel, Lindo, and Villamizar survey an invariant-theory
approach; the abstract presents it as an approach rather than a resolution.
[Shuffling the Deck, arXiv:2604.16567](https://arxiv.org/abs/2604.16567)

Stark generalizes Kocay's lemma and proves a result about multiplicities of
trees as subgraphs.  It does not supply a new unrestricted graph census.
[Generalization and Power of Kocay's Lemma,
arXiv:2509.02604](https://arxiv.org/abs/2509.02604)

## Reconciled baseline, not new delta

- McKay's unrestricted computation still ends at order 13; its larger-order
  results concern specified graph classes.  The arXiv record has not changed
  since January 2022.  [Reconstruction of small graphs and digraphs,
  arXiv:2102.01942](https://arxiv.org/abs/2102.01942)
- Wang, Wen, and Guo's 2024 theorem says a graph is reconstructible when a
  deleted card is almost controllable with a nontrivial automorphism; the
  older Hong controllable-card condition remains a necessary filter for a CE.
  This is a sufficient condition, not a new census.  [arXiv:2408.02488](https://arxiv.org/abs/2408.02488)
- The classical pseudosimilar-vertex constructions remain relevant, but the
  targeted 2025–2026 search found no new result closing pseudosimilarity as a
  CE architecture.

## Negative search findings

The targeted update found no primary source announcing any of the following:

- an unrestricted verification beyond order 13;
- a new bounded-degree census superseding McKay's published bounds;
- a simple-graph counterexample;
- a theorem converting Ivanov's high-overlap families into equal decks;
- a recent closure of pseudosimilar-vertex or trace-incidence architectures.

Absence here means “not located in the targeted update,” not a proof that no
such manuscript exists.

## Corrections to the previous literature notes

- “Strongest near miss” must specify the metric.  The order-78 pair is the
  smallest pair identified by Ivanov that exceeds the old BBF benchmark; the
  paper contains larger absolute overlaps and asymptotic families.
- The finite `r=5` rows in Ivanov's table are computational checks using a
  compact odd-port selector.  The proved general asymptotic theorem stated in
  the paper is for even `r`.
- The 2026 triangle-free revision is a genuine delta missing from the earlier
  repository summary and is now part of the handoff.
