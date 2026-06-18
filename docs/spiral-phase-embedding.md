# Spiral Embedding of the Phase Orbit

The circle model records phase. The spiral model records phase plus index.

```text
circle = phase
spiral = phase + time
```

For a base dynamic `B`, the one-indexed phase is:

```text
u_m = { B^(m - 1) pi }
```

For resonance formulas it is often cleaner to use the zero-based index:

```text
M = m - 1
```

The circle embedding uses a fixed radius:

```text
p_m = R (cos(2 pi u_m), sin(2 pi u_m))
```

The spiral embedding lets the radius depend monotonically on the index:

```text
z_m = R(m) exp(2 pi i { B^(m - 1) pi })
```

Possible radius choices:

```text
R(m) = m
R(m) = log(m + 1)
R(q, r) = q in resonance coordinates
```

If `R` is monotone, the first occurrence of a target is the innermost
intersection of the pi spiral with the target wedge.

## 1. Strings as Wedges

For a string `S` of length `L` in alphabet/base `Q`:

```text
A_S = int_Q(S)
I_S = [ A_S / Q^L, (A_S + 1) / Q^L )
```

In angular coordinates:

```text
theta_- = 2 pi A_S / Q^L
theta_+ = 2 pi (A_S + 1) / Q^L
```

The target is the wedge:

```text
W_S = { r exp(i theta) : r >= 0, theta_- <= theta < theta_+ }
```

The locate problem becomes:

```text
m_S = min { m : z_m in W_S }
```

On the circle, all hits in `I_S` are phase-equivalent. On the spiral, the first
hit is geometrically the closest hit to the center.

## 2. Decimal `1000`-Zero Wedge

For `1000` decimal zeros:

```text
B = 10
Q = 10
L = 1000
A_S = 0
I_S = [0, 10^-1000)
```

The wedge is:

```text
0 <= theta < 2 pi 10^-1000
```

The central target vector is:

```text
v = (cos(pi / 10^1000), sin(pi / 10^1000))
```

The decimal spiral point for index `M` is:

```text
z_M = R(M) exp(2 pi i { 10^M pi })
```

The block exists iff:

```text
exists M: z_M in W_0^1000
```

The first decimal index is:

```text
M_0^1000 = min { M : z_M in W_0^1000 }
```

So the `1000`-zero problem is the first intersection of the decimal pi spiral
with a microscopic wedge around the positive x-axis.

## 3. Resonance Arms

Choose a resonance:

```text
pi^N ~= B^K
rho = pi^N / B^K
```

Decompose:

```text
m - 1 = q K + r
```

Then:

```text
B^(m - 1) pi = B^r pi^(N q + 1) rho^(-q)
u_q,r = { B^r pi^(N q + 1) rho^(-q) }
```

The spiral point, using radius as a function of zero-based index `M`, is:

```text
z_q,r = R(q K + r) exp(2 pi i u_q,r)
```

For a fixed residue `r`, varying `q = 0, 1, 2, ...` gives one spiral arm:

```text
gamma_r(q) = z_q,r
```

So a resonance with modulus `K` decomposes the spiral into `K` arms.

For the decimal medium resonance:

```text
K = 1221
N = 2456
rho = pi^2456 / 10^1221 ~= 1.0002011206
```

we get `1221` resonance arms:

```text
z_q,r = R(1221 q + r)
  exp(2 pi i { 10^r pi^(2456 q + 1) rho^(-q) })
```

This explains why residue-only experiments did not produce meaningful lift:

```text
r = arm number
q = position along that arm
```

A residue histogram only chooses arms. It ignores where the target wedge is
intersected along each arm.

## 4. Locate by Spiral-Arm Intersection

The zero-based resonance-arm formulation of locate is:

```text
M_S = min_r (r + K min { q : gamma_r(q) in W_S })
m_S = M_S + 1
```

with:

```text
gamma_r(q) = R(q K + r)
  exp(2 pi i { B^r pi^(N q + 1) rho^(-q) })
```

A useful candidate generator should therefore approximate arm-wedge
intersections, not only residue frequencies.

A possible search pipeline:

1. choose a resonance `(K, N)`;
2. split the orbit into arms `r = 0, ..., K - 1`;
3. estimate intervals of `q` where `gamma_r(q)` may intersect the target wedge;
4. check only those intervals;
5. certify with interval arithmetic or the chord test.

## 5. Spiral Sector State Space

The circular sector space is angular only:

```text
V_(Q,L) = R^(Q^L)
```

A spiral index also has radial bins:

```text
h = 0, 1, 2, ..., H
```

so the state space becomes:

```text
V_(Q,L,H) = R^(H x Q^L)
```

A basis element:

```text
e_h,a
```

means radial layer `h` and angular sector `a`.

The index state is:

```text
m -> (h_m, a_m)
h_m = radial_bin(R(m))
a_m = floor(Q^L { B^(m - 1) pi })
```

A string target is the same angular sector across radial layers. The first
occurrence is the smallest radial layer, then the smallest index inside that
layer, that contains a hit.

## 6. Matrix-Resonance Locate Algebra

The matrix layer can translate targets, but it does not turn `1221` into a
string occurrence index. In this theory:

```text
K = 1221
```

is a resonance scale for:

```text
pi^2456 ~= 10^1221
```

It is a coordinate chart, not a proven occurrence position.

For a sector grid `(Q, L)`, define the sector state of index `m`:

```text
x_m^(B;Q,L) = e_floor(Q^L { B^(m - 1) pi })
```

For a target `S` at the same grid:

```text
y_S = e_A_S
```

A hit is:

```text
y_S^T x_m = 1
```

and:

```text
m_S = min { m : y_S^T x_m = 1 }
```

For `1000` decimal zeros, Experiment 003 gives a certifying quaternary cell:

```text
e_0^(4,1661) => 0^1000_10
```

The dynamics must remain decimal, because the target is about decimal digits:

```text
B = 10
Q = 4
L = 1661
```

With the `K = 1221, N = 2456` chart:

```text
M = q 1221 + r
u_q,r = { 10^r pi^(2456 q + 1) rho^(-q) }
```

The sector state is:

```text
x_q,r = e_floor(4^1661 u_q,r)
```

A strict sufficient certificate for `1000` decimal zeros is:

```text
(e_0^(4,1661))^T x_q,r = 1
```

If this is true, then:

```text
1000 decimal zeros occur at position m = q 1221 + r + 1
```

The chord version uses:

```text
v = (cos(pi / 4^1661), sin(pi / 4^1661))
p_q,r = R (cos(2 pi u_q,r), sin(2 pi u_q,r))
```

and certifies the contained quaternary cell when:

```text
p_q,r . v >= R cos(pi / 4^1661)
```

Because `[0, 4^-1661) subset [0, 10^-1000)`, this also certifies `1000`
decimal zeros.

## 7. Experiment 004 Status

Experiment 004 tested variant C:

```text
matrix target transform
+ proven resonance chart
+ sector certificate
```

This is not an automatic first-index generator. It confirms that, once a
candidate `(q, r)` is available, the matrix-transformed sector state can certify
decimal zero blocks exactly.

For a decimal block of `D` zeros:

```text
[0, 10^-D)
```

use the quaternary certifying depth:

```text
L_4 = ceil(D log_4(10))
```

Experiment 004 reported the following target transforms:

```text
D  L_4  intersect cells  contained cells  boundary cells
1  2    2                1                1
2  4    3                2                1
3  5    2                1                1
4  7    2                1                1
5  9    3                2                1
6  10   2                1                1
```

So the stable shape is:

```text
decimal zero sector -> 1-2 certifying quaternary cells + 1 boundary cell
```

The contained cells had:

```text
precision = 1.0
```

for all tested `D`. That confirms the strict implication:

```text
a_M^(4,L_4) in contained_cells(D)
=> { 10^M pi } < 10^-D
```

The intersecting cells had recall `1.0`: all real zero-block hits landed in the
intersecting quaternary cells. Boundary cells increased recall but required
interval or chord refinement because they partly lie outside the decimal sector.

Using the decimal resonance chart:

```text
K = 1221
N = 2456
rho = pi^2456 / 10^1221
M = 1221 q + r
```

the exact orbit identity is:

```text
10^M pi = 10^r pi^(2456 q + 1) rho^(-q)
```

Therefore the certifying state for `D` decimal zeros is:

```text
floor(4^L_4 { 10^r pi^(2456 q + 1) rho^(-q) }) in C_D
```

where `C_D` is the set of contained quaternary cells for the decimal zero
sector.

If this holds, then:

```text
D decimal zeros occur at position m = 1221 q + r + 1
```

For `D = 1000`, Experiment 003 gives:

```text
L_4 = 1661
C_1000 = {0}
boundary = {1}
[0, 4^-1661) subset [0, 10^-1000)
```

So the sufficient certificate becomes:

```text
floor(4^1661 { 10^M pi }) = 0
=> 1000 decimal zeros
```

and, in the `K = 1221, N = 2456` chart:

```text
floor(4^1661 { 10^r pi^(2456 q + 1) rho^(-q) }) = 0
=> 1000 decimal zeros at position m = 1221 q + r + 1
```

Experiment 004 confirms compatibility between the containment matrix, the
resonance coordinate chart, and the sector-state certificate. It does not
confirm automatic discovery of the first `(q, r)`.

The next unresolved task is still candidate generation:

```text
find likely q,r -> verify by matrix-sector certificate
```

A future spiral-arm experiment should compare:

```text
random windows
residue-only
drift-only
spiral-arm nearest crossing
```

with lift measured over random at equal coverage.

## 8. Experiment 006 Status

Experiment 006 tested whether simple spiral-arm memory can become a candidate
generator beyond the finite index. The tested orbit was decimal and the finite
phase cells were quaternary:

```text
u_M = {10^M pi}
a_M = floor(4^Lmax u_M)
H = 500000
Lmax = 12
K in {1, 2, 5, 87, 1221, 5669}
```

The test used `K = 1, 2, 5` as short-step positive controls, `K = 87` and
`K = 1221` as decimal resonance charts, and `K = 5669` as a larger resonance
scale.

Three measurements were run.

First, arm coherence:

```text
w_q,r = exp(2 pi i u_q,r)
C_r(lag) = |mean_q w_(q+lag,r) conj(w_q,r)|
```

For resonance scales, pi was close to the random baseline. Example values at
`lag = 1`:

```text
K     pi mean_arm_C   random mean_arm_C
87    0.011766        0.011853
1221  0.043625        0.043086
5669  0.093289        0.095037
```

The larger absolute values at larger `K` are also present in the random control,
so they should not be interpreted as pi-specific structure.

Second, transition memory along arms was measured by mutual information:

```text
I(a_M ; a_(M+K))
```

The short-step controls detected real local structure. For `L_base4 = 4`, pi had
large mutual information at `K = 1` and `K = 2`:

```text
K   pi MI bits   random MI bits
1   4.68115      0.09621
2   1.39289      0.09571
```

But at resonance scales, pi was again close to random:

```text
K     pi MI bits   random MI bits
87    0.09610      0.09552
1221  0.09662      0.09723
5669  0.09767      0.09757
```

For `L_base4 = 5`, the same pattern held: short-step controls worked, while
`K = 87`, `1221`, and `5669` were near baseline.

Third, a one-step Markov predictor was trained on the first half of the data:

```text
P(a_M = target | a_(M-K) = previous)
```

It scored positions in the second half, selected the top `1%`, `5%`, or `10%`,
and measured recall lift over random coverage. Positive controls produced
large lift, proving that the test can detect structure when it exists. For
example, at `L_base4 = 5`:

```text
K   top 1% lift
1   99.951
2   10.058
```

The resonance scales did not show useful lift. At `L_base4 = 4`, top `1%`:

```text
K     pi lift
87    0.966
1221  1.019
5669  1.052
```

At `L_base4 = 5`, top `1%`:

```text
K     pi lift
87    0.853
1221  1.013
5669  0.992
```

These are effectively baseline-level results for candidate generation.

So Experiment 006 confirms the finite index and certificate stack remains the
right acceptance layer, but it does not confirm the simplest spiral-arm
predictor:

```text
one-step Markov memory along resonant arms is not enough
```

This does not falsify the resonance-coordinate model. It says that resonance
arms are useful as an addressing/certification chart, but this low-order memory
feature does not compress locate beyond the built horizon. Future candidate
generators need higher-order, multi-scale, or different features before they can
claim lift over random baselines.

## 9. Experiment 007 Status

Experiment 007 tested walk-forward zero-block prediction on already computed
decimal digits. This is stricter than certification: at each cutoff `T`, a model
may use only zero hits before `T`, then must predict future zero-block starts
after `T`. The computed horizon was:

```text
H = 2000000 decimal positions
D in {3, 4, 5, 6}
K in {87, 1221, 5669}
```

The observed zero-hit counts matched the expected random scale reasonably well:

```text
D   hits   first M   mean gap   random expected gap
3   1920   600       1041.57    1000
4   173    13389     11546.4    10000
5   14     17533     149563     100000
6   1      1699931   n/a        1000000
```

Two non-resonant baselines were used. A random extreme-value window predicts
that a `D`-zero hit appears within width:

```text
T_window = -log(1 - p) 10^D
```

An empirical-gap baseline uses observed train gaps before the cutoff. At nominal
`p = 0.8`, both were competitive:

```text
model                    D=3 hit  D=4 hit  D=5 hit
random 80% window        0.873    0.826    0.667
empirical gap 80% window 0.898    0.863    0.723
```

The resonance-residue predictor selected top residue classes modulo `K` from
train zero hits and measured recall against coverage after the cutoff. It would
be useful only with recall much larger than coverage. For `K = 1221` at top
`10%` coverage, the result was mixed:

```text
D   recall   coverage   lift
3   0.108    0.0999     1.084
4   0.0807   0.0999     0.808
5   0.105    0.0999     1.053
```

Other tested resonance scales were similarly noisy: some small cells showed
lift above `1`, others collapsed to baseline or below it, and the effect was
not stable across `D` and `K`. Therefore the tested residue predictor does not
provide reliable future-position prediction.

The useful conclusion is negative but concrete:

```text
resonance residues are not enough for zero-block prediction
```

The certificate layer still works once a candidate `M` is proposed or computed.
The missing part is a predictor that proposes `M` with robust lift. A better next
target is probably record-low phase prediction rather than all short zero-block
hits, because long zero blocks are extreme-value events:

```text
u_M = {10^M pi} is a new low record
```

## 10. Summary

The current geometry stack is:

```text
phase-sector index
+ sector transform matrices
+ finite locate/certificate engine
+ resonance coordinate annotation
```

The circle tells us where the phase is. The spiral tells us when it got there.
Residue `r` names an arm; locate needs the first intersection of that arm with a
target wedge. Experiments 006 and 007 show that simple one-step arm memory and
resonance-residue prediction do not yet find that intersection better than
random or simple gap baselines at resonance scales.
