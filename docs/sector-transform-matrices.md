# Sector Transform Matrices for pi-fs

This note extends the phase-sector index with a matrix layer between different
circle partitions. The point is not to translate between numeral systems as
strings. The point is to translate between sector grids on the same unit circle.

In the phase model:

```text
string -> sector
index -> point on the circle
locate -> first point inside a sector
```

Different bases and depths are different partitions of the same interval
`[0, 1)`, or equivalently the same circle.

## 1. Sector Vector Spaces

For base `Q` and depth `L`, the circle is divided into `Q^L` sectors:

```text
I_a^(Q,L) = [ a / Q^L, (a + 1) / Q^L )
a = 0, 1, ..., Q^L - 1
```

Define the sector vector space:

```text
V_(Q,L) = R^(Q^L)
```

The basis vector:

```text
e_a^(Q,L)
```

represents the sector `I_a^(Q,L)`.

A string `S` of length `L` in base `Q` is usually the basis vector:

```text
e_A_S^(Q,L)
```

where `A_S = int_Q(S)`. If the index was built at a deeper level `L_max`, the
same target becomes a range of basis vectors.

Dense vectors of size `Q^L` are only a mathematical notation. Real pi-fs storage
should keep sparse ranges, sparse maps, or prefix-tree nodes.

## 1.1. Proportional Sector Arithmetic

The matrix formulas are just schoolbook proportions written on exact integer
grids. A source sector id `A` in `(Q, L)` represents the ratio:

```text
A : Q^L
```

A target sector id `B` in `(Q', L')` represents:

```text
B : Q'^L'
```

So target translation compares:

```text
A / Q^L  <->  B / Q'^L'
```

and avoids floating point by cross multiplication.

For overlap, find every `B` whose target sector intersects source sector `A`:

```text
B / Q'^L' < (A + 1) / Q^L
(B + 1) / Q'^L' > A / Q^L
```

Equivalently:

```text
B Q^L < (A + 1) Q'^L'
(B + 1) Q^L > A Q'^L'
```

Therefore the half-open target range is:

```text
B_min^cap = floor(A Q'^L' / Q^L)
B_max^cap = ceil((A + 1) Q'^L' / Q^L) - 1
```

For containment, require a stronger condition:

```text
I_B^(Q',L') subset I_A^(Q,L)
```

which is:

```text
B Q^L >= A Q'^L'
(B + 1) Q^L <= (A + 1) Q'^L'
```

Therefore:

```text
B_min^subset = ceil(A Q'^L' / Q^L)
B_max^subset = floor((A + 1) Q'^L' / Q^L) - 1
```

This is the same overlap/containment matrix layer, but expressed as
proportions. The helper [`../pifs/proportion.py`](../pifs/proportion.py) exposes
these exact integer formulas directly. A shorter standalone description lives in
[`proportional-sector-arithmetic.md`](proportional-sector-arithmetic.md).

Two proportional machines should stay separate:

```text
linear sector proportion:      A : Q^L <-> B : Q'^L'
logarithmic resonance ratio:   N log(pi) ~= K log(10)
```

The first translates sectors and certificates. The second translates scales and
addresses, such as `pi^2456 ~= 10^1221` and `M = 1221q + r`.

## 2. Overlap Matrix

Given two sector systems `(Q, L)` and `(Q', L')`, define the unnormalized overlap
matrix:

```text
O_ba^((Q,L)->(Q',L')) = | I_a^(Q,L) intersect I_b^(Q',L') |
```

The normalized column-stochastic version is:

```text
C_ba^((Q,L)->(Q',L')) =
  | I_a^(Q,L) intersect I_b^(Q',L') | / | I_a^(Q,L) |
```

This maps a source sector distribution into the target grid by measure.

The boolean intersection matrix is:

```text
C_bool,ba = 1 iff I_a^(Q,L) intersects I_b^(Q',L')
```

For exact arithmetic, compute intersections with rational endpoints:

```text
left = max(a / Q^L, b / Q'^L')
right = min((a + 1) / Q^L, (b + 1) / Q'^L')
overlap = max(0, right - left)
```

For large depths, do not materialize the matrix. For a single source sector or
range, enumerate only the target cells whose endpoints intersect the source
interval.

## 3. Containment Matrix

For strict certificates, intersection is not enough. We also need containment.
For a target sector `a` in `(Q, L)` and a candidate cell `b` in `(Q', L')`, use:

```text
D_ba^((Q',L')->(Q,L)) = 1 iff I_b^(Q',L') subset I_a^(Q,L)
```

If `D_ba = 1`, then a hit in candidate cell `b` automatically certifies a hit in
target sector `a`.

This orientation is useful for cross-base certification. For example, a
quaternary cell that lies completely inside a decimal zero-block sector
certifies the decimal block without recomputing the target in decimal form.

The dual question is coverage:

```text
I_a^(Q,L) subset union of selected I_b^(Q',L')
```

which certifies that a selected candidate-cell set fully covers a target sector.

## 4. Dynamics Matrix

The phase dynamics is:

```text
f_B(u) = { B u }
```

For a finite sector system `(Q, L)`, define a transition matrix by preimage
measure:

```text
T_ba^(B;Q,L) = | { u in I_a^(Q,L) : f_B(u) in I_b^(Q,L) } | / | I_a^(Q,L) |
```

This is the safest probabilistic definition. Using only
`|f_B(I_a) intersect I_b| / |I_a|` can overcount when `f_B` stretches intervals.

For integer `B`, this matrix describes the digit-shift dynamics on the sector
partition. For non-integer `B`, such as the internal `B = 4*pi` layer, compute it
with interval arithmetic over monotone pieces separated by wrap points:

```text
u = k / B
```

The `B = 4*pi, Q = 4` layer is not digit conversion. It is a phase-coordinate
transform for the internal pi-calibrated oscillograph.

## 5. Chord-Vector Matrix

Every sector has a center angle:

```text
theta_a = 2 pi (a + 1/2) / Q^L
```

and a central vector:

```text
v_a = (cos(theta_a), sin(theta_a))
```

Collect all central vectors into a matrix:

```text
V_(Q,L) =
  [ v_0^T
    v_1^T
    ...
    v_(Q^L-1)^T ]
```

For a phase point:

```text
p_m = R (cos(2 pi u_m), sin(2 pi u_m))
```

all chord scores are:

```text
s_m = V_(Q,L) p_m
```

A sector `a` is hit when:

```text
s_m[a] >= R cos(pi / Q^L)
```

This is a rank-2 object in practice: the rows are just sampled cosines and
sines. For large `Q^L`, compute only candidate rows or use vectorized numeric
kernels. Do not store a dense `Q^L x 2` matrix unless the level is small.

## 6. Exact Binary and Quaternary Conversion

The conversion between `(4, L)` and `(2, 2L)` is exact:

```text
0_4 = 00_2
1_4 = 01_2
2_4 = 10_2
3_4 = 11_2
```

Because:

```text
4^L = 2^(2L)
```

the sector partitions are identical. A quaternary cell id is the same integer as
the corresponding grouped binary cell id under canonical numeric ordering.

So the transform matrix between `(4, L)` and `(2, 2L)` is a permutation matrix,
or the identity matrix if both sides use the same numeric cell order.

For `0_4 + hello world`:

```text
45 quaternary symbols = 90 binary bits
```

with no ambiguity.

## 7. Decimal Zero Blocks to Quaternary Cells

The decimal block of `1000` zeros is:

```text
I = [0, 10^-1000)
```

To express it in a quaternary grid, choose `L_4` so that a quaternary cell is no
larger than the decimal sector:

```text
4^-L_4 <= 10^-1000
L_4 >= 1000 log_4(10)
```

Therefore:

```text
L_4 >= 1661
```

At depth `L_4`, a quaternary cell `a` is fully inside the decimal zero sector
when:

```text
(a + 1) / 4^L_4 <= 10^-1000
```

It intersects the decimal zero sector when:

```text
a / 4^L_4 < 10^-1000
```

For `L_4 = 1661`, Experiment 003 reported exactly two intersecting quaternary
cells for the decimal `1000`-zero sector:

```text
[0, 10^-1000) -> cells {0, 1} at depth 1661
```

The first cell is fully contained:

```text
[0, 4^-1661) subset [0, 10^-1000)
```

The second cell is a boundary candidate. Therefore, a phase hit in the first
quaternary cell at depth `1661` is already a strict certificate for `1000`
decimal zeros. The boundary cell still requires interval or chord refinement.

This gives a strict conversion path:

```text
decimal zero-block sector -> quaternary candidate cells -> exact certificate
```

## 8. Integration With the Phase-Sector Index

The phase-sector index already gives:

```text
m -> u_m = { B^(m - 1) pi }
a_m = floor(Q^L_max u_m)
S -> [a_min, a_max]
locate(S) = min { m : a_m in [a_min, a_max] }
```

Sector transform matrices add cross-grid target translation:

```text
target string
-> sector vector
-> matrix transform
-> candidate cells in another grid
-> finite sector locate
-> chord or interval certificate
```

This lets pi-fs move targets between binary, quaternary, decimal, hexadecimal,
and internal phase-coordinate layers without pretending that all of those layers
are the same kind of digit stream.

## 9. What This Does and Does Not Accelerate

The matrix layer does not magically produce the first index outside the built
horizon. It helps with three concrete tasks.

First, exact target translation:

```text
decimal 00...0 -> quaternary cells
binary payload -> quaternary sector
hex payload -> binary or quaternary cells
```

Second, strict containment certificates:

```text
I_b^(Q',L') subset I_a^(Q,L)
```

means a hit in candidate cell `b` automatically certifies a hit in target sector
`a`.

Third, sparse candidate pruning:

```text
target_(Q',L') = C target_(Q,L)
```

then intersect the resulting target-cell set with the finite index in the target
grid.

The open problem remains the same: predicting useful candidates beyond the
finite horizon requires a real phase predictor, not only a change of basis.

## 10. Experiment 003 Status

Experiment 003 tested matrix transforms rather than resonance compression. The
confirmed results are:

```text
binary/quaternary transform = exact permutation

decimal/quaternary transform = sparse overlap

containment cells provide strict cross-base certificates
```

For `(4, L) <-> (2, 2L)`, the transform was exact for all tested depths
`L = 1..12`:

```text
fraction exact one-to-one = 1.0
```

For decimal targets transformed into quaternary grids, the overlap stayed small.
At the minimal depth:

```text
L_4 = ceil(D log_4(10))
```

for decimal length `D`, each decimal sector intersects only a small number of
quaternary cells. For `D = 6`:

```text
L_4 = 10
mean intersecting quaternary cells ~= 4.19
boundary ambiguity ~= 2 cells
```

The typical shape is therefore:

```text
several contained cells + about two boundary cells
```

For `1000` decimal zeros:

```text
D = 1000
L_4 = ceil(1000 log_4(10)) = 1661
intersecting quaternary cells = 2
fully contained quaternary cells = 1
boundary quaternary cells = 1
```

The certificate consequence is:

```text
[0, 4^-1661) subset [0, 10^-1000)
```

so a hit in the first quaternary cell at depth `1661` certifies `1000` decimal
zeros.

The dynamics matrix check also matched the model:

```text
B = 4, Q = 4      -> each source sector maps to 4 target sectors
B = 4*pi, Q = 4   -> each source sector spreads across roughly 12-14 target cells
```

The latter is the expected internal oscillograph behavior because
`4*pi ~= 12.566`.

Finally, same-orbit sector queries through a base-4 index were demonstrated, but
with the important limitation:

```text
this is not decimal digit search in pi
```

Decimal digits use the orbit `{10^(m - 1) pi}`, while a base-4 index uses
`{4^(m - 1) pi}`. Cross-grid lookup is valid when the orbit is the same; cross-
orbit digit search needs a separate bridge and certificate.

## 11. Reference Helper API

A small dependency-free reference helper lives in [`../pifs/sector_transform.py`](../pifs/sector_transform.py).
It uses exact rational arithmetic and half-open Python ranges.

Core functions:

```text
sector_interval(q, depth, cell)
cell_range_for_interval(left, right, q, depth)
contained_range_for_interval(left, right, q, depth)
intersect_range(q_from, depth_from, cell_from, q_to, depth_to)
contained_range(q_from, depth_from, cell_from, q_to, depth_to)
transform_target(q_from, depth_from, cell_from, q_to, depth_to)
certifying_cells(q_from, depth_from, cell_from, q_to, depth_to)
```

For the `1000` decimal zero target, the reference check is:

```text
certifying_cells(10, 1000, 0, 4, 1661)
```

which returns:

```text
intersecting = [0, 1]
contained = [0]
boundary = [1]
```

This pins down the certificate:

```text
[0, 4^-1661) subset [0, 10^-1000)
```

The helper is intentionally not wired into the FUSE build; it is a reference
utility for the research notes and experiments.

## 12. Experiment 004 Status

Experiment 004 connected the matrix target transform to the decimal resonance
chart and sector certificate.

For decimal zero blocks `D = 1..6`, the quaternary certifying depth:

```text
L_4 = ceil(D log_4(10))
```

produced small target-cell sets:

```text
D  L_4  intersect cells  contained cells  boundary cells
1  2    2                1                1
2  4    3                2                1
3  5    2                1                1
4  7    2                1                1
5  9    3                2                1
6  10   2                1                1
```

Contained cells had precision `1.0`, while intersecting cells had recall `1.0`
and boundary cells required refinement. This is the desired certificate split:

```text
contained = strict certificate
boundary = candidate requiring interval/chord refinement
```

With the decimal resonance chart:

```text
K = 1221
N = 2456
M = 1221 q + r
rho = pi^2456 / 10^1221
```

the certificate condition is:

```text
floor(4^L_4 { 10^r pi^(2456 q + 1) rho^(-q) }) in C_D
=> D decimal zeros at position m = 1221 q + r + 1
```

where `C_D` is the contained-cell set for the decimal zero sector.

For `D = 1000`:

```text
L_4 = 1661
C_1000 = {0}
```

so:

```text
floor(4^1661 { 10^r pi^(2456 q + 1) rho^(-q) }) = 0
=> 1000 decimal zeros at position m = 1221 q + r + 1
```

This confirms the certificate layer, not automatic candidate discovery.

## 13. Next Matrix Experiments

The next useful checks are:

1. store Experiment 003 and 004 package results as reproducible CSV summaries;
2. translate known decimal first-occurrence targets into quaternary target-cell
   sets through overlap and containment matrices;
3. measure whether containment transforms reduce candidate cells before final
   chord or interval certification;
4. test higher-order or multi-scale spiral-arm candidate generators before the
   matrix-sector certificate; Experiment 006 showed that one-step Markov memory
   at resonance scales is near random baseline;
5. test the internal `B = 4*pi, Q = 4` phase-coordinate layer without presenting
   it as digit conversion.

Success criteria should stay modest and concrete: fewer candidate cells before
certification, exact containment where possible, and no confusion between real
digit layers and internal oscillograph coordinates.

## 14. Summary

The next pi-fs layer is not a generic matrix between numeral systems. It is a
set of matrices between sector partitions of the same circle:

```text
overlap matrix       O or C
boolean intersection C_bool
containment matrix   D
dynamics matrix      T_B
chord-vector matrix  V_(Q,L)
```

These matrices provide a formal way to translate targets, certify containment,
model phase dynamics, and batch chord scores. They make pi-fs a geometric matrix
system over phase sectors rather than a dictionary of digit strings.
