# Finite Matrix-Sector Locate Engine

This note records the practical MVP layer for `pi-fs locate`.

The goal is deliberately modest: do not predict the first index in the infinite
expansion of pi. Build a finite, strict locate engine inside a chosen horizon:

```text
target -> sector transform -> sparse finite index -> certificate -> resonance coordinates
```

This is the engineering core that later candidate generators can call into.

## Proof-of-Concept Status

The proof of concept is the closed finite `pi-fs locate` contour, not a formula
for the first occurrence of an arbitrary string in the infinite expansion of
pi. The validated contour is:

```text
target -> proportion -> finite phase index -> certificate -> resonance address
```

In operational terms, a query follows this path:

```text
S -> I_S -> proportional cells -> finite phase index -> M -> (q, r)
```

where the resonance annotation uses the decimal chart:

```text
M = 1221q + r.
```

Experiment 010 exhaustively checked `111100` decimal patterns of lengths `2..5`
inside the first `500000` decimal positions of pi. Intersect-cell lookup plus
verification matched direct search for every found pattern, while contained
cells remained strict certificates.

What this PoC supports:

- strict finite-horizon locate inside a built index;
- exact proportional target transforms between sector grids;
- cross-base containment certificates, including quaternary certificates for
  decimal targets;
- resonance coordinates as address metadata for located positions.

What it does not support yet:

- a formula for the first occurrence of any string in infinite pi;
- a proof that `1000` decimal zeros occur in pi;
- a beyond-horizon predictor with robust lift over random or suffix/FM-index
  baselines.

## Model

For a source orbit base `B` and a certification grid `(Q, Lmax)`, every scanned
zero-based position `M` gives a phase

```text
u_M = {B^M pi}
```

and a finite grid cell

```text
a_M = floor(Q^Lmax u_M).
```

The sparse index stores the earliest position for each visited cell:

```text
a -> min M.
```

A pattern `S` in source base `B` defines a source sector

```text
I_S = [A_S / B^D, (A_S + 1) / B^D),
```

where `D = len(S)` and `A_S = int_B(S)`. A sector transform maps that source
sector into intersecting and contained cells of the index grid.

The contained cells are certificates: if a phase point lands in one of those
cells, the point is guaranteed to lie inside `I_S`.

## MVP Layer

Experiment 005 used the mixed layer

```text
B = 10, Q = 4
```

so the orbit remains the real decimal phase orbit

```text
u_M = {10^M pi},
```

while the index/certificate grid is quaternary:

```text
a_M = floor(4^Lmax u_M).
```

This is useful because decimal targets can be certified through quaternary
containment cells.

## Locate Flow

For a decimal pattern `S`:

1. Compute `A_S = int_10(S)` and `D = len(S)`.
2. Transform the decimal sector into quaternary cells at depth `Lmax`.
3. Query the sparse index for the earliest occupied contained cell.
4. If contained lookup returns a hit, return a strict cross-base certificate.
5. Also return resonance coordinates for the zero-based position `M`:

```text
M = 1221 q + r.
```

Boundary/intersecting cells may still be used as candidates, but they require a
second interval or chord refinement step before acceptance.

## Experiment 005 Status

The experiment built a finite index with:

```json
{
  "B": 10,
  "Q": 4,
  "Lmax": 16,
  "H_decimal_positions": 500000,
  "N4_cells_total": 4294967296,
  "occupied_cells": 499975,
  "occupancy_fraction": 0.00011640950106084347,
  "decimal_guard_digits_P": 34,
  "gen_seconds": 2.983380079269409,
  "build_seconds": 0.7973825931549072
}
```

It checked 19 locate queries: zero blocks from `0` through `00000000`, plus
ordinary decimal patterns such as `14`, `314`, `2718`, `9999`, `12345`,
`314159`, `000001`, and `987654`.

Summary:

```json
{
  "queries_total": 19,
  "direct_found": 15,
  "contained_returned": 15,
  "intersect_returned": 15,
  "contained_precision": 1.0,
  "intersect_precision": 1.0,
  "intersect_matches_direct_first_fraction": 1.0
}
```

Within the scanned horizon, finite matrix-sector locate matched direct search
for every found pattern. For patterns not present in the first `500000` decimal
positions, the index correctly returned `not found within horizon`.

## Experiment 010: Closed Locate Contour

Experiment 010 closed the whole finite locate contour:

```text
target -> proportion -> finite phase index -> certificate -> resonance address
```

It used the same mixed interpretation as the MVP:

```text
B = 10, Q = 4
u_M = {10^M pi}
a_M = floor(4^11 u_M)
```

with:

```json
{
  "H_decimal_positions": 500000,
  "Lmax4": 11,
  "N4_cells": 4194304,
  "occupied_cells": 471113,
  "occupancy_fraction": 0.11232209205627441,
  "K_resonance": 1221,
  "N_resonance": 2456
}
```

The check was exhaustive for all decimal patterns of lengths `D = 2..5`, for
`111100` total target patterns. Each pattern was handled by:

1. direct search in the decimal digit dump;
2. proportional transform from `I_A^(10,D)` to cells of `(4,11)`;
3. sparse finite phase-index lookup;
4. contained/intersect certificate logic;
5. resonance address annotation `M = 1221q + r`.

Summary:

```text
D  patterns  direct found  locate found  exact match rate
2  100       100           100           1.0
3  1000      1000          1000          1.0
4  10000     10000         10000         1.0
5  100000    99347         99347         1.0
```

For every pattern found inside the horizon, intersect-cell locate plus
verification returned the same first occurrence as direct search. There were no
false misses and no false hits when direct search had no match.

Contained-cell precision was also `1.0`. Contained lookup is stricter than
intersect lookup, so it can miss the first direct occurrence when that occurrence
lands in a boundary cell. In this run, contained recall of the direct first hit
was:

```text
D = 2: 1.0000
D = 3: 0.9990
D = 4: 0.9972
D = 5: 0.9761
```

That is the intended split:

```text
contained cell  -> strict certificate
boundary cell   -> candidate requiring verification
```

The proportional transform also shrank the candidate set at the expected scale:

```text
D = 2: mean intersect candidates ~= 5000
D = 3: mean intersect candidates ~= 500
D = 4: mean intersect candidates ~= 50
D = 5: mean intersect candidates ~= 5
```

This confirms the finite contour as an executable locate engine inside the built
horizon. It still does not prove a beyond-horizon first-index predictor.

## Experiment 011: Anchor-Relative Addressing

Experiment 011 tested relative reads around repeated anchors. The address mode is:

```text
(anchor pattern, occurrence number, relative offset, length) -> data
```

The experiment used the first `1000000` decimal digits and first `1000000`
base-4 digits of pi. It searched for later repeats of the initial prefix and
then verified reads with negative offsets around those repeated anchors.

Decimal prefix repeats inside the horizon:

```text
L = 2: 9874 repeats excluding the initial prefix
L = 3: 1005 repeats
L = 4: 93 repeats
L = 5: 15 repeats
L = 6: 1 repeat
L = 7: 0 repeats
```

Base-4 prefix repeats inside the horizon:

```text
L = 2: 62195 repeats excluding the initial prefix
L = 3: 15468 repeats
L = 4: 3887 repeats
L = 5: 947 repeats
L = 6: 220 repeats
L = 7: 50 repeats
L = 8: 16 repeats
L = 9: 1 repeat
L = 10: 1 repeat
L = 11: 0 repeats
```

All sampled relative reads matched direct slices. The useful result is not a
first-occurrence predictor. It is a file-system address mode: after an anchor is
located and certified, data can be read relative to that anchor, including at
negative offsets, inside the computed horizon.

A proof object for this mode should include:

```text
anchor sector certificate
occurrence number
relative offset
direct phase/index slice certificate
```

## Experiment 013: Boundary Continuation

Experiment 013 tested a continuation contour at artificial cutoffs:

```text
known_tail_100
-> unique boundary anchor
-> 10 candidate digits
-> negative-context alignment certificate
-> independent next-digit certificate
```

The cutoffs were:

```text
10000, 50000, 100000, 500000, 1000000, 1500000
```

For each cutoff, the 100-digit tail was unique in the known prefix. The next
`100` hidden digits were reconstructed one digit at a time. Each step considered
exactly `10` candidate digits, for `1000` candidate checks per cutoff. In every
cutoff, exactly one candidate was accepted at each step, and the reconstructed
`100` digits matched the actual next `100` digits.

The important boundary is that negative-context alignment alone cannot choose
the next digit: all `10` candidates align with the boundary. The independent
certificate is the information source that selects the correct candidate. In
the backtest, that certificate was simulated by already-computed future digits.
In a real beyond-horizon setting, it would have to come from interval arithmetic,
an independent digit algorithm, or another certified oracle.

So the confirmed architecture is:

```text
constant-size candidate set + boundary alignment + independent certificate
```

For fixed 100-digit tails, extending `n` digits requires `O(n)` candidate rounds.
With tail length chosen as `O(log H)`, the alignment work is `O(n log H)`. This
confirms a continuation workflow, not a way to create new digits from no
information.

## External Sector Certificates

The continuation object needed after Experiment 013 is an external sector
certificate. Here, external means external to the already known decimal prefix,
not external to mathematics. It can come from another base, interval arithmetic,
a binary or hexadecimal extraction method, a phase certificate, or any other
independent certified computation.

Let `x = frac(pi)` and let the known decimal prefix of length `n` be:

```text
P_n = floor(10^n x).
```

The known prefix gives only the interval:

```text
I_n = [P_n / 10^n, (P_n + 1) / 10^n).
```

An external certificate is an interval or sector `J` such that:

```text
x in J
```

and `J` narrows the position of `x` more than the prefix interval alone.

### One-Digit Extraction Lemma

The ten possible next-digit cells are:

```text
I_d = [(10 P_n + d) / 10^(n+1), (10 P_n + d + 1) / 10^(n+1)),
d in {0, ..., 9}.
```

If there is exactly one digit `d` such that:

```text
J subset I_d,
```

then the next decimal digit is `d`. This is just interval containment: the
subcells `I_0, ..., I_9` partition the known prefix interval, and `J` contains
the actual value `x`.

### Concrete `99 + y` Formula

A useful concrete case is `99` known decimal digits plus one unknown digit:

```text
P_99 = int_10(d_1 ... d_99)
y in {0, ..., 9}
A_100 = 10 P_99 + y.
```

Let an external certificate in base `Q` at depth `L` be:

```text
C = floor(Q^L alpha_s)
J_C^(Q,L) = [C / Q^L, (C + 1) / Q^L),
```

where `alpha_s = {10^s pi}` is the local phase at the boundary being continued.
Translate this external cell to decimal depth `100`:

```text
A_min = floor(C 10^100 / Q^L)
A_max = ceil((C + 1) 10^100 / Q^L) - 1.
```

The known 99 digits allow only the ten cells:

```text
10 P_99 <= A <= 10 P_99 + 9.
```

So the surviving candidate range is:

```text
A_low  = max(A_min, 10 P_99)
A_high = min(A_max, 10 P_99 + 9).
```

If `A_low = A_high`, then there is one surviving decimal cell and the next digit
is:

```text
y = A_low - 10 P_99.
```

Equivalently, in digit-candidate form:

```text
y_min = max(0, A_min - 10 P_99)
y_max = min(9, A_max - 10 P_99).
```

If `y_min = y_max`, the digit is certified as:

```text
y = y_min = y_max.
```

Geometrically, the known 99-digit sector is split into ten smaller decimal
sectors. The external sector, expressed in another grid, certifies the next
digit exactly when its proportional decimal image intersects only one of those
ten sectors.

The operational point is:

```text
known_tail_100 -> boundary alignment
external sector certificate -> digit selection
```

The known tail proves that the continuation procedure is aligned at the intended
boundary. It does not choose the digit. The external certificate chooses the
digit by eliminating all but one candidate cell.

### Block Extraction

For a block of `k` future decimal digits, write the candidate block as
`Y in {0, ..., 10^k - 1}` and the depth-`n+k` decimal cell as:

```text
A = 10^k P_n + Y.
```

If `J` is contained in exactly one decimal cell at depth `n+k`, then:

```text
Y = A - 10^k P_n.
```

This is the block version of the same lemma.

### Cross-Base Certificate

If the external certificate is a cell in another sector grid,

```text
J_C^(Q,L) = [C / Q^L, (C + 1) / Q^L),
```

then its intersecting decimal cells at depth `n+k` are computed by exact
proportions:

```text
A_min = floor(C 10^(n+k) / Q^L)
A_max = ceil((C + 1) 10^(n+k) / Q^L) - 1.
```

The known prefix allows only:

```text
10^k P_n <= A <= 10^k (P_n + 1) - 1.
```

If the intersection of these two integer ranges contains exactly one value
`A`, then the certified continuation block is:

```text
Y = A - 10^k P_n.
```

So the next digit or block is not guessed. It is extracted as the remainder
after proportional intersection of an external sector certificate with the
known prefix interval.

## Experiment 014: Algebraic Suffix Recovery

Experiment 014 tested the block version of external sector certificates. For a
boundary `H`, it used:

```text
start = H - n
known prefix = pi[start : H]
hidden suffix = pi[H : H + k]
```

The full decimal cell at depth `D = n + k` is:

```text
A = int(pi[start : H + k]).
```

A cross-base certificate in base `Q` at depth `L` is:

```text
C = floor(Q^L {10^start pi}).
```

Translating that `Q`-cell to decimal depth `D` and intersecting it with the
known prefix range leaves a candidate set for the hidden suffix. If one value
remains, then:

```text
hidden = A - 10^k P_n.
```

The experiment used `126` cutoffs up to `H_MAX = 2000000`, hidden lengths
`k = 1, 5, 10, 100`, and certificate bases `2`, `4`, and `16`. With sufficient
certificate depth offset, the candidate set collapsed to exactly one value.
Examples from the summary:

```text
known_n = 100, hidden_k = 10, cert_base = 4, L_offset = 4:
  success_rate = 1.0, mean_candidates = 1.0

known_n = 100, hidden_k = 100, cert_base = 4, L_offset = 4:
  success_rate = 1.0, mean_candidates = 1.0

known_n = 100, hidden_k = 10, cert_base = 16, L_offset = 2:
  success_rate = 1.0, mean_candidates = 1.0
```

This validates the algebraic suffix-extraction rule. It does not validate a
source for the certificate: the experiment simulated the cross-base certificate
using already-computed future digits.

## Experiment 015: Next-Digit Recovery

Experiment 015 tested the one-digit version at six artificial boundaries:

```text
H = 10000, 50000, 100000, 500000, 1000000, 1500000.
```

At each boundary, the known 100-digit tail fixed alignment and the external
cross-base certificate selected one of the ten possible next decimal digits.
For base-4 certificates:

```text
offset = 0: success_rate = 1/6, mean_candidates = 1.8333
offset = 1: success_rate = 3/6, mean_candidates = 1.5
offset = 2: success_rate = 1.0, mean_candidates = 1.0
offset = 4: success_rate = 1.0, mean_candidates = 1.0
offset = 8: success_rate = 1.0, mean_candidates = 1.0
```

For base-16 certificates, `offset >= 1` gave `success_rate = 1.0` and
`mean_candidates = 1.0`. The canonical base-4, offset-4 run recovered the next
digit at all six boundaries. At `H = 1000000`, the cross-base certificate was a
base-4 cell at depth `172`, and the proportional intersection left exactly one
candidate digit: `3`.

The result is exactly the external-certificate lemma in the `k = 1` case. It is
not a proof that the known tail alone predicts the next digit.

## Experiment 016: External Sector Certificate Validation

Experiment 016 directly validated the external sector certificate lemma across a
larger grid of cases. It used `256` boundaries up to `H_MAX = 2000000`, known
prefix lengths `20`, `50`, `99`, and `100`, hidden suffix lengths
`1`, `5`, `10`, `50`, and `100`, certificate bases `2`, `4`, `8`, and `16`,
and depth offsets `0`, `1`, `2`, `4`, and `8`.

For a boundary `H`, the experiment used:

```text
known prefix = pi[H-n : H]
hidden suffix = pi[H : H+k]
C = floor(Q^L {10^(H-n) pi})
```

and applied the same proportional intersection rule:

```text
hidden = A - 10^k P_n
```

when exactly one candidate decimal cell survived.

The negative control confirmed that the known decimal prefix alone does not
select the suffix:

```text
k = 1:   10 candidates
k = 5:   100000 candidates
k = 10:  10000000000 candidates
k = 50:  10^50 candidates
k = 100: 10^100 candidates
```

For the next-digit case with `known_n = 100`, candidate collapse improved as the
certificate sector became narrower. Within the tested offsets:

```text
Q = 2,  offset = 8: success_rate = 0.99609375, mean_candidates = 1.00390625
Q = 4,  offset = 8: success_rate = 1.0,        mean_candidates = 1.0
Q = 8,  offset = 8: success_rate = 1.0,        mean_candidates = 1.0
Q = 16, offset = 4: success_rate = 1.0,        mean_candidates = 1.0
```

For block suffix recovery with base-4 certificates and `known_n = 100`,
sufficient depth also collapsed the suffix candidate set:

```text
k = 1,   offset = 8: success_rate = 1.0, mean_candidates = 1.0
k = 5,   offset = 8: success_rate = 1.0, mean_candidates = 1.0
k = 10,  offset = 4: success_rate = 1.0, mean_candidates = 1.0
k = 50,  offset = 8: success_rate = 1.0, mean_candidates = 1.0
k = 100, offset = 4: success_rate = 1.0, mean_candidates = 1.0
```

This is the strongest validation of the external-certificate algebra so far:
known prefix plus sufficiently narrow external sector certificate determines
the next digit or block by exact proportional arithmetic. It still does not
construct the external certificate. In the experiment, the certificate was
simulated from already-computed future digits; beyond a computed horizon it must
come from an independent interval computation, digit-extraction method, or
verified phase source.

## Zero-Block Certificate

For decimal zero blocks, the source sector is

```text
[0, 10^-D).
```

At a sufficiently deep quaternary grid, contained cells give strict
cross-base certificates. For example, previous sector-transform checks showed
that for `D = 1000`:

```text
L4 = ceil(1000 log_4 10) = 1661
[0, 4^-1661) subset [0, 10^-1000)
```

Therefore:

```text
floor(4^1661 {10^M pi}) = 0
=> 1000 decimal zeros at position M + 1.
```

Using the decimal resonance chart `K = 1221, N = 2456`, write `M = 1221q + r`.
Then the same certificate can be written as:

```text
floor(4^1661 {10^r pi^(2456q + 1) rho^(-q)}) = 0
=> 1000 decimal zeros at position 1221q + r + 1,
```

where

```text
rho = pi^2456 / 10^1221.
```

This is a certificate form, not a method for finding the first `q, r`.

## Code

The reference implementation is intentionally small and dependency-free:

```text
pifs/sector.py          sector geometry helpers
pifs/transform.py       readable sector-transform aliases
pifs/proportion.py      schoolbook sector proportions
pifs/certificate.py     interval and containment certificates
pifs/finite_index.py    sparse finite phase-cell index
pifs/resonance.py       M = qK + r coordinates
pifs/locate.py          minimal locate flow
```

The code is not wired into the historical FUSE build. It is a research helper
for the documentation and experiments.

## Baseline Boundary

A suffix array or FM-index remains the right baseline for ordinary string lookup
in a digit dump. The point of the matrix-sector layer is different:

```text
cross-base target transforms + finite sparse lookup + strict certificates.
```

The finite engine is the acceptance layer. Future candidate generators can be
simple scans, suffix/FM-index candidates, resonance charts, spiral-arm heuristics,
or other methods, but final acceptance should still pass the same sector
certificate.

## Current Boundary

Confirmed:

- finite phase-sector lookup inside a built horizon;
- decimal-to-quaternary sector transforms;
- contained-cell certificates;
- closed finite locate contour with direct-search agreement for exhaustive
  `D = 2..5` decimal targets inside `H = 500000`;
- anchor-relative reads around certified repeated anchors inside a computed
  horizon;
- boundary continuation as a constant-candidate workflow when an independent
  next-digit certificate is available;
- external sector certificates as the object that extracts the next digit or
  block by proportional intersection with the known prefix;
- algebraic suffix recovery from cross-base certificates when the certificate is
  sufficiently deep;
- one-digit boundary recovery at tested cutoffs when a sufficiently narrow
  cross-base certificate is supplied;
- formal validation of the external sector certificate lemma over `256`
  boundaries, multiple certificate bases, and suffix lengths up to `100`;
- resonance coordinate annotation `M = 1221q + r`.

Not confirmed:

- automatic first-index discovery beyond the built horizon;
- resonance or spiral-arm candidate generation with lift over direct baselines;
- generating new digits beyond the horizon without an independent certificate;
- constructing the required external sector certificate for arbitrary future
  positions without a separate certified computation;
- treating the Experiment 014/015/016 backtests as new digit generation, since
  their certificates were simulated from already-computed future digits.

Experiment 006 tested the simplest version of that missing candidate layer: a
one-step Markov predictor along resonance arms `M = qK + r` for `K = 87`,
`1221`, and `5669`. Short-step controls `K = 1` and `K = 2` showed strong lift,
so the test can detect structure when it exists. The resonance-scale predictors
were near random baseline, so the finite locate engine should remain the
acceptance/certificate layer, not be replaced by this low-order predictor.

Experiment 007 moved from in-sample candidate scoring to walk-forward zero-block
prediction over the first `2,000,000` decimal positions. At each cutoff, the
model could use only earlier zero hits and then had to predict future zero-block
positions. Random extreme-value windows and empirical gap windows were used as
honest baselines. Resonance-residue prediction with `K = 87`, `1221`, and `5669`
was noisy and did not show robust lift across `D = 3..5`; for example,
`K = 1221` at top `10%` coverage had lift `1.084` for `D = 3`, `0.808` for
`D = 4`, and `1.053` for `D = 5`. This keeps the current boundary unchanged:
certification is solid, but future-position prediction is still open.
