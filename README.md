# Graph Reconstruction Campaign

Exact, reproducible tooling for the Kelly--Ulam graph reconstruction
conjecture.  The repository distinguishes three outcomes sharply:

- `CE`: two nonisomorphic finite simple graphs with identical vertex decks;
- `THEOREM`: a proved reconstruction result or reduction;
- `SEARCH`: finite evidence only.

The initial instrument is dependency-free Python.  It contains two independent
decision paths: an individualization/refinement canonical form for deck cards,
and a separate adjacency-preserving backtracker for parent nonisomorphism.

Run the controls with:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/exhaustive_small.py --vertices 6
python3 scripts/exhaustive_local_maps.py --vertices 4 --progress 0
python3 scripts/analyze_n6_obstruction.py
python3 scripts/exhaustive_transposition_systems.py --allow-identity --representatives 0
python3 scripts/exhaustive_length2_frontier.py --family mixed --three-count 2
python3 scripts/analyze_primitive_couplings.py
python3 scripts/analyze_partial_overlap_couplings.py
```

No hash equality is ever accepted as a certificate.

`docs/CONSTRUCTION_FORMALISM.md` separates the local-map, edge-class, and
binary-realization layers and gives the exact assignment-specific parent
permutation condition.

See `docs/FIRST_STRIKE.md` for the current construction frontier and the exact
order-five local-gluing census.
