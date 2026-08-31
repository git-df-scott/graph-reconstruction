# Universal-rescuer strike

Date: 2026-08-31

## Verdict

`GRC CE: NO`

Level 1 is UNSAT in the complete compatible-row domain defined below.  No
binary realization was run.

## Exact domain and forcing condition

Embed the certified six-class order-six primitive partition in the old-edge
slots of

```text
Omega_7 = {G,H} x E(K_7),
```

leaving the twelve slots for edges incident to the new vertex 6 initially
free.  For every old deletion `i=0,...,5`, allow every permutation in `S_7`
fixing `i`, and add its complete deletion-row equations.  Retain a partial or
complete choice exactly when the six embedded old classes remain pairwise
distinct.  This is the precise meaning of old-six-class compatibility in this
strike.  No cycle-insertion, fixed-6, or row-shape restriction is imposed.

For deletion 6, any of the four certified old globalizers extended by fixing
6 adds no equation beyond the embedded old partition, so this choice does not
change the incidence state.

The old partition already satisfies the globalizer equation for

```text
r1 = (1,3,2,0,4,5,6)
```

on every old edge.  Consequently `r1` globalizes a completed extension if and
only if the following six cross-edge relations all hold:

```text
W_v: (G,{6,v}) ~ (H,{6,r1(v)}),  v=0,...,5.
```

This is a necessary-and-sufficient condition.  The six relations are an
irredundant witness set at the partition level: after fixing all old-edge
relations, joining any five `W_v` leaves the omitted pair distinct and makes
the `r1` globalizer equation fail exactly there.

## Complete row vocabulary

Each deletion has `6! = 720` raw deletion-fixed permutations.  Direct exact
filtering gives:

| Deleted row | Raw | Compatible | Distinct exact incidence effects |
|---:|---:|---:|---:|
| 0 | 720 | 9 | 9 |
| 1 | 720 | 9 | 9 |
| 2 | 720 | 9 | 9 |
| 3 | 720 | 9 | 9 |
| 4 | 720 | 24 | 21 |
| 5 | 720 | 24 | 21 |
| **Total** | **4,320** | **84** | **78** |

The effect quotient is exact: two rows are identified only when adjoining
them to the old seed produces the identical partition of all 42 slots.  No
unproved residual-symmetry quotient is used.

Every compatible single row leaves at least its deleted cross-edge witness
unconnected, so all 84 compatible rows kill `r1` as partial systems.  The
obstruction arises only when the six deletion rows are made simultaneous.

## Direct witness-repair matrix

Entries count compatible raw rows which directly connect witness `W_v` when
adjoined to the seed.

| Row | W0 | W1 | W2 | W3 | W4 | W5 |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 2 | 2 | 0 | 9 | 9 |
| 1 | 0 | 0 | 2 | 2 | 9 | 9 |
| 2 | 9 | 9 | 0 | 9 | 9 | 9 |
| 3 | 2 | 0 | 2 | 0 | 9 | 9 |
| 4 | 9 | 9 | 9 | 9 | 0 | 24 |
| 5 | 9 | 9 | 9 | 9 | 24 | 0 |

Indirect repairs produced by joins are included by the CSP and independent
dynamic program; the table is not used as a substitute for connectivity.

## Six-row CSP

The discovery solver performs union-find propagation, immediately rejecting
old-class mergers and repair of the currently forbidden `r1` witness.  It
checked all six possible forbidden witnesses.

```text
status:                         LEVEL_1_UNSAT
CSP nodes:                      90
old-class-merge prunes:        676
forbidden-witness prunes:       50
```

An independent bit-set partition implementation, sharing no union-find or DFS
logic, enumerated reachable states layer by layer:

```text
1, 9, 7, 3, 3, 4, 5.
```

There are exactly five complete compatible partitions.  Every one reconnects
all six witnesses.

## Minimal UNSAT cores

The inclusion-minimal row subsets already forcing all six witnesses, while
preserving all six old classes, are:

```text
{0,2}, {1,2}, {2,3}, {2,4}, {2,5}, {0,1,3}.
```

The central mechanism is row 2.  Every compatible row-2 effect repairs
`W_0,W_1,W_3,W_4,W_5`; it cannot touch `W_2` because vertex 2 is deleted.
Combining row 2 with any other required deletion row repairs `W_2` as well.
The `{0,1,3}` core gives an independent route when row 2 is absent.

Thus survival was not an accident of cycle insertion.  It is forced by the
simultaneous deletion rows plus preservation of all six old class
distinctions.

## Complete terminal classification

| Classes | Exact globalizers | Terminal partitions |
|---:|---:|---:|
| 9 | 4 | 1 |
| 8 | 4 | 2 |
| 7 | 8 | 2 |

All five terminals retain all four certified old A4 globalizers.  The minimum
unavoidable globalizer count is therefore four.  There is no old-rescue kill,
no emergent-only rescue case, and no zero-globalizer system.

## Theorem status

- **Proved generally:** once the old-edge globalizer equations are fixed,
  `r1` survival is equivalent to the six stated cross-edge relations; those
  relations are partition-level irredundant.
- **Computationally exhaustive in the exact domain:** all 4,320 raw rows, all
  84 compatible rows, all 78 exact row effects, the six-row CSP, five terminal
  partitions, minimal row cores, and minimum globalizer count four.
- **Not claimed:** a theorem for extensions allowed to merge old primitive
  classes, or for a different primitive.

## Verification and resources

The discovery union-find CSP and independent bit-set dynamic program agree.
All five terminal partitions were checked by exact colored-graph
backtracking and by raw enumeration of every one of the 5,040 permutations in
`S_7`.  Every enumerated row was independently checked to be a genuine
permutation fixing its deleted vertex.

The complete strike uses about 0.81 seconds wall time and 13,184 KiB peak RSS
on this host.  No binary assignment, generic graph enumeration, or order
scaling was performed.

## Next strike

Relax exactly one hypothesis: permit a controlled merge of one pair of the
six old classes, and enumerate which single merge destroys the row-2 forcing
core while avoiding the known S4/S5 side-symmetry regimes.  This is the
smallest successor because the present theorem identifies preservation of all
six distinctions as the condition making `r1` unavoidable.
