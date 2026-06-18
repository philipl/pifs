# A Phase-Sector Index Theory for `pi-fs locate`

Proposed by Ivan Proskurakov.

This note sketches a possible `locate` model for pi-fs. The central point is
that the index should not be built as a dictionary from strings to positions.
It should be built over the phase orbit of pi on the unit circle:

```text
m -> u_m = { B^(m - 1) pi }
```

Every index `m` gives a phase point. Every finite digit string gives a sector
of the circle. A `locate` query is therefore:

```text
which minimum m lands in this sector?
```

So the pi-fs index is fundamentally:

```text
circle sector -> min m
```

The practical result is a sparse finite index over computed phase cells, plus a
resonance layer that can generate candidates beyond the computed horizon.

## 1. Choose the Layer

There are two different use cases.

For real digits of pi in a conventional base, use the same base for the phase
dynamics and the sectors:

```text
B = Q
```

Examples:

```text
binary bits of pi       B = 2,  Q = 2
quaternary bit pairs    B = 4,  Q = 4
decimal digits of pi    B = 10, Q = 10
hex digits of pi        B = 16, Q = 16
```

For a binary `hello world` payload, `B = 4` and `Q = 4` is a good first layer
because one quaternary digit is two bits.

For an internal pi-fs address layer, one can also experiment with:

```text
B = 4 pi, Q = 4
```

That is no longer an index over ordinary binary or decimal digits of pi. It is
an internal pi-calibrated quaternary oscillograph layer. For real digit lookup,
start with `B = Q`.

## 2. Index the Phase, Not the String

For each index up to a finite horizon:

```text
m = 1, 2, 3, ..., M_max
```

compute:

```text
u_m = { B^(m - 1) pi }
```

and, optionally, the circle point with radius `R` (`R = 1` is enough for
the normal index):

```text
p_m = R (cos(2 pi u_m), sin(2 pi u_m))
```

For the index itself it is usually enough to store `u_m` after quantizing it to
a sector depth `L_max`:

```text
a_m = floor(Q^L_max u_m)
```

Then:

```text
a_m in { 0, 1, ..., Q^L_max - 1 }
```

For a target such as `0_4 + hello world`, the string has length `L = 45` in
base 4, so the exact finite sector index needs at least:

```text
L_max >= 45
```

## 3. What the Finite Index Stores

For each computed `m`, store a sparse record:

```text
(a_m, m, margin_m)
```

where:

```text
a_m = floor(Q^L_max u_m)
```

and `margin_m` is the distance to the nearest cell boundary:

```text
margin_m = min(
  u_m - a_m / Q^L_max,
  (a_m + 1) / Q^L_max - u_m
)
```

The margin helps certification: a phase point far from a boundary is cheaper to
confirm than one sitting near a sector edge.

There are two useful storage modes:

```text
a -> min { m : a_m = a }
```

for the first hit per cell, or:

```text
a -> [m_1, m_2, m_3, ...]
```

when all hits are needed.

The index should be sparse. At depths such as `L_max = 45`, materializing all
`Q^L_max` cells is not practical. Store only visited cells, sorted by `a`, and
build a range-minimum structure over the corresponding `m` values.

## 4. Query as a Sector Range

Let a query string be:

```text
S = s_1 s_2 ... s_L
```

in base `Q`, and let:

```text
A_S = int_Q(S)
```

The string sector is:

```text
I_S = [ A_S / Q^L, (A_S + 1) / Q^L )
```

If the finite index was built to depth `L_max`, the query becomes a cell range:

```text
a_min = A_S Q^(L_max - L)
a_max = (A_S + 1) Q^(L_max - L) - 1
```

Then:

```text
locate(S) = min { m : a_m in [a_min, a_max] }
```

So locating a string becomes an ordinary range-min query over occupied phase
cells.

For a sorted sparse sector index:

1. binary-search the first occupied cell `>= a_min`;
2. binary-search the last occupied cell `<= a_max`;
3. run RMQ over the `m` values in that slice.

## 5. Complexity

Building records up to `M_max` costs:

```text
O(M_max log M_max)
```

if records are sorted after generation. A streaming sparse map can collect
per-cell minima in expected `O(M_max)`, but a queryable range-min structure is
still needed for arbitrary sector ranges.

A string query costs:

```text
O(L + log U)
```

where `U` is the number of occupied cells in the sparse index. With a sector
prefix tree, the same query can be `O(L)`.

The honest constraint is:

```text
this is fast after the index has been built to the required horizon
```

A finite index answers exactly inside `M_max`. It does not prove anything about
all later digits of pi.

## 6. Chord Certification

A string sector can also be represented geometrically as a chord.

For string `S`:

```text
c_S = (A_S + 1/2) / Q^L
theta_S = 2 pi c_S
v_S = (cos(theta_S), sin(theta_S))
delta_S = pi / Q^L
tau_S = R cos(delta_S)
```

For candidate `m`:

```text
p_m = R (cos(2 pi u_m), sin(2 pi u_m))
score_S(m) = p_m . v_S
```

A hit satisfies:

```text
score_S(m) >= tau_S
```

This is useful after the range index has returned a candidate. Define:

```text
mu_S(m) = p_m . v_S - tau_S
```

If the point has Euclidean error bound `e`:

```text
mu_S(m) > e    -> certified hit
mu_S(m) < -e   -> certified miss
|mu_S(m)| <= e -> refine precision
```

The equivalent interval certificate is:

```text
[u_hat_m - E, u_hat_m + E] subset I_S -> certified hit
```

or disjoint from `I_S` for a certified miss.

## 7. Target Vector Example: 1000 Decimal Zeros

There are two separate statements:

```text
the target vector exists
```

and:

```text
the pi phase orbit eventually lands in that vector's sector
```

The first is always true for any finite digit string. The second is the actual
existence problem for a block inside pi.

For any sequence:

```text
S = s_1 s_2 ... s_L
A_S = int_Q(S)
```

its sector is:

```text
I_S = [ A_S / Q^L, (A_S + 1) / Q^L )
```

with center:

```text
c_S = (A_S + 1/2) / Q^L
theta_S = 2 pi c_S
```

and exact target vector:

```text
v_S = (cos(theta_S), sin(theta_S))
```

For `1000` decimal zeros:

```text
S = 00...0
L = 1000
Q = 10
A_S = 0
```

so:

```text
I_0^1000 = [0, 10^-1000)
c_0^1000 = 1 / (2 * 10^1000)
theta_0^1000 = pi / 10^1000
```

and the vector is:

```text
v_0^1000 = (cos(pi / 10^1000), sin(pi / 10^1000))
```

It is almost the positive x-axis, but not exactly. It points to the middle of
the tiny sector `[0, 10^-1000)`:

```text
v_0^1000 ~= (1, pi / 10^1000)
```

For a decimal position `M`, the phase point is:

```text
u_M = { 10^M pi }
p_M = R (cos(2 pi u_M), sin(2 pi u_M))
```

With the radius convention `R = 2`:

```text
p_M = 2 (cos(2 pi {10^M pi}), sin(2 pi {10^M pi}))
```

The half-width of the `1000`-zero sector is:

```text
delta = pi / 10^1000
```

and the chord threshold is:

```text
tau = R cos(delta)
```

For `R = 2`:

```text
tau = 2 cos(pi / 10^1000)
```

Therefore `M` hits the `1000`-zero sector exactly when:

```text
p_M . v_0^1000 >= 2 cos(pi / 10^1000)
```

The first such decimal index, if it exists, is:

```text
M_0^1000 = min { M >= 0 : p_M . v_0^1000 >= 2 cos(pi / 10^1000) }
```

and the digit position after the decimal point is:

```text
m_0^1000 = M_0^1000 + 1
```

Equivalently, define the hit margin:

```text
mu(M) = p_M . v_0^1000 - 2 cos(pi / 10^1000)
```

Then:

```text
mu(M) > 0    -> hit
mu(M) < 0    -> miss
mu(M) ~= 0   -> near the sector boundary; refine precision
```

The best candidate up to a finite horizon `H` is:

```text
M*(H) = argmax_0<=M<=H p_M . v_0^1000
```

If `mu(M*(H)) >= 0`, the block has been found inside the horizon. If not, it has
not been found inside `H`, but it may still occur later.

In resonance coordinates, choose:

```text
pi^N ~= 10^K
rho = pi^N / 10^K
M = q K + r
```

Then:

```text
10^M pi = 10^r pi^(N q + 1) rho^(-q)
u_q,r = { 10^r pi^(N q + 1) rho^(-q) }
p_q,r = 2 (cos(2 pi u_q,r), sin(2 pi u_q,r))
```

and the `1000`-zero condition is:

```text
p_q,r . v_0^1000 >= 2 cos(pi / 10^1000)
```

with:

```text
M = q K + r
m = q K + r + 1
```

This is the core pi-fs geometry in one example: each finite sequence has a
vector and a chord; each index is a point on the circle; search is the first
intersection of the phase orbit with the sector cut out by that chord.

## 8. Two Index Layers

A practical pi-fs index should have two layers.

### A. Exact Finite Sector Index

This is the already computed phase orbit up to `M_max`:

```text
(a_m, m, margin_m)
```

It answers:

```text
S -> [a_min, a_max] -> min m
```

inside the finite horizon.

### B. Resonance Candidate Index

This is an analytic layer for candidates beyond the computed horizon. Use
resonances:

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
u_m = { B^r pi^(N q + 1) rho^(-q) }
```

and check candidates through the chord test:

```text
p_q,r . v_S >= R cos(pi / Q^L)
```

This layer is not a complete proven index by itself. It generates candidate
windows `(q, r)` that must be checked by the exact sector certificate.

## 9. Decimal Resonance Computations

The preprint calculations give a concrete decimal calibration for the resonance
candidate layer. For base 10, the basic resonance is:

```text
pi^N ~= 10^K
N = 2 K + t
```

because `pi^2` is close to `10`. Define:

```text
beta = log_pi(10 / pi^2)
P = 1 / beta = ln(pi) / (ln(10) - 2 ln(pi))
W = pi / P = pi beta
Omega = 2 W
```

The numeric values are:

```text
alpha = log_10(pi)                         0.4971498726941338543512682882909
beta = log_pi(10 / pi^2)                   0.011465867588060938764722047288709
P = 1 / beta                               87.215380111424779037945921458107
W = pi / P                                 0.036021085381685566916079998337866
Omega = 2 W                                0.072042170763371133832159996675733
```

For each integer `t`:

```text
K_t = round(t P)
N_t = 2 K_t + t
epsilon_t = t - K_t / P
pi^N_t / 10^K_t = pi^epsilon_t
```

Selected resonance levels from the preprint:

```text
t        K_t        N_t         epsilon_t        pi^N_t / 10^K_t - 1
1        87         175         0.0024695198     0.0028309327
4        349        702        -0.0015877882    -0.0018159378
5        436        877         0.00088173161    0.0010098541
9        785        1579       -0.00070605663   -0.00080791758
14       1221       2456        0.00017567498    0.00020112062
65       5669       11403      -3.3567175e-6    -3.8425274e-6
3394     296009     595412      1.1256696e-6     1.2885884e-6
6853     597687     1202227    -1.1053783e-6    -1.2653588e-6
10247    893696     1797639     2.029127e-8      2.3228023e-8
560191   48857271   98274733   -9.6497424e-9    -1.1046348e-8
1130629  98608238   198347105   9.9178486e-10    1.1353258e-9
```

The notable medium resonance is:

```text
t = 14
K = 1221
N = 2456
pi^2456 / 10^1221 ~= 1.0002011206
```

The oscillator form is:

```text
z(K) = exp(2 pi i beta K) = exp(2 i W K)
```

A resonance means:

```text
z(K) ~= 1
2 W K ~= 2 pi t
W K ~= pi t
```

with phase-error identities:

```text
epsilon_t = t - K_t / P = t - W K_t / pi
ln(pi^N_t / 10^K_t) = epsilon_t ln(pi)
Delta_theta_t = 2 W K_t - 2 pi t = -2 pi epsilon_t
```

## 10. Shifted Saw Targets

For a target scale `C > 0`, search:

```text
pi^N ~= C 10^K
```

Using `N = 2 K + t`:

```text
pi^(2K + t) / 10^K = pi^(t - beta K)
```

so the shifted saw target is:

```text
t - beta K ~= log_pi(C)
K_t,C = round(P (t - log_pi(C)))
```

Equivalently:

```text
K_t,C = round(t P + delta_C)
delta_C = -P log_pi(C)
```

The preprint also frames simple rational coordinates. For target `p/q`, define:

```text
X_p/q,t = (q / p) 10^(K_t / N_t)
pi / X_p/q,t = (p / q) pi^(epsilon_t / N_t)
```

If `|epsilon_t| / N_t` is small, pi is close to the rational coordinate `p/q`
in that resonance-scaled system.

Examples:

```text
resonance          K          N           d    coordinate                  error from 1/d
medium             1221       2456        2    0.5000000409406362542118    4.0940636e-8
medium             1221       2456        3    0.3333333606270908361412    2.7293758e-8
medium             1221       2456        7    0.1428571545544675012034    1.1697325e-8
medium             1221       2456        10   0.1000000081881272508424    8.1881273e-9
strong             936331413  1883398678  2    0.4999999999999999997801   -2.1992598e-19
strong             936331413  1883398678  3    0.3333333333333333331867   -1.4661732e-19
strong             936331413  1883398678  7    0.14285714285714285708     -6.2835994e-20
strong             936331413  1883398678  10   0.09999999999999999995601  -4.3985196e-20
```

## 11. Decimal Sector Windows

For a non-zero decimal string `S` with integer value `A_S` and length `L`, the
preprint defines the target sector:

```text
I_S = [ A_S / 10^L, (A_S + 1) / 10^L )
```

For the resonance value:

```text
R(K, t) = pi^(t - beta K)
```

requiring `R(K, t) in I_S` gives:

```text
A_S / 10^L <= pi^(t - beta K) < (A_S + 1) / 10^L
```

After taking logarithms, this becomes the finite `K` window:

```text
P (t - log_pi((A_S + 1) / 10^L)) < K
K <= P (t - log_pi(A_S / 10^L))
```

For the zero block `S = 00...0`, the lower logarithm is absent. The one-sided
condition is:

```text
K > P (t + L log_pi(10))
```

If a finite window is needed, use a safe band such as:

```text
[10^-(L + 1), 10^-L)
```

This is the computational meaning of "sector from-to": a string becomes an
interval in the resonance saw coordinate, then candidates are certified with the
exact phase-sector test.

## 12. Decimal Position Bridge

The preprint emphasizes that the resonance value `pi^N / 10^K` is not itself a
real decimal digit position. A real decimal hit is still:

```text
{ 10^M pi } in I_S
M = m - 1
```

Given a resonance:

```text
rho = pi^N / 10^K
M = q K + r, 0 <= r < K
```

there is an exact identity:

```text
10^M pi = 10^r pi^(N q + 1) rho^(-q)
```

So:

```text
m = q K + r + 1
```

is a hit exactly when:

```text
{ 10^r pi^(N q + 1) rho^(-q) } in I_S
```

This is the decimal specialization of the generic candidate formula in the
resonance layer.

## 13. Repunit Scaffold Observation

The preprint also records a computational observation around repunits:

```text
R_m = (10^m - 1) / 9 = 11...1
K_m = R_m R_(m + 1)
```

Examples:

```text
11 * 111 = 1221
111 * 1111 = 123321
1111 * 11111 = 12344321
```

The first value is also the medium resonance `K = 1221` for `t = 14`:

```text
1221 = round(14 P)
```

For the general scaffold, define:

```text
c_m = round(beta K_m)
K_m# = round(c_m / beta)
s_m = K_m# - K_m
```

The observed correction table:

```text
m  K_m                 c_m              s_m   K_m#                beta K_m - c_m
2  1221                14               0     1221                -0.00017567498
3  123321              1414             2     123323              -0.017743173
4  12344321            141538          -31    12344290             0.35005052
5  1234554321          14155236        -33    1234554288           0.37485448
6  123456654321        1415537651      -27    123456654294         0.30959734
7  12345677654321      141553905269    -29    12345677654292       0.32735239
8  1234567887654321    14155391928317   40    1234567887654361    -0.46245591
9  123456789987654321  1415539206845492 8     123456789987654329  -0.096419555
```

This scaffold is an observation, not a theorem. It belongs in the experimental
candidate-generation layer until additional statistical tests show that it
reduces search entropy better than chance.

## 14. Suggested On-Disk Layout

One possible layout:

```text
pi-fs/
  meta.json
  resonance/
    levels.json
    base_B.json
  sectors/
    phase_cells.bin
    rmq_min_position.bin
    margins.bin
  docs/
    model.md
```

For real quaternary digits of pi:

```json
{
  "B": "4",
  "Q": 4,
  "L_max": 45,
  "M_max": "...",
  "representation": "quaternary digits of pi",
  "precision_guard_bits": 32
}
```

For the internal oscillograph layer:

```json
{
  "B": "4*pi",
  "Q": 4,
  "R": 2,
  "representation": "pi-calibrated quaternary oscillograph"
}
```

`phase_cells.bin` stores sorted sparse records:

```text
cell_id, position_m
```

where `cell_id = a_m`.

`rmq_min_position.bin` supports:

```text
[a_min, a_max] -> min m
```

`margins.bin` stores distance to the nearest cell boundary for certification.

`resonance/levels.json` stores resonance levels, for example:

```json
[
  {
    "N": 2456,
    "K": 1221,
    "rho": "...",
    "delta": "..."
  }
]
```

## 15. Build Algorithm

```text
build_index(B, Q, L_max, M_max):
    records = []
    for m in 1..M_max:
        u = fractional_part(B^(m - 1) * pi)
        a = floor(Q^L_max * u)
        left = a / Q^L_max
        right = (a + 1) / Q^L_max
        margin = min(u - left, right - u)
        records.append((a, m, margin))

    sort records by a
    build range_min_structure over m
    store records, RMQ, margins, and metadata
```

Query:

```text
locate(S):
    L = len(S)
    A = int_base_Q(S)
    a_min = A * Q^(L_max - L)
    a_max = (A + 1) * Q^(L_max - L) - 1
    m = range_min_query(a_min, a_max)
    if m not found:
        return NOT_FOUND_WITHIN_HORIZON
    return certify(m, S)
```

Certification:

```text
certify(m, S):
    compute u_m with interval error E
    I_S = [A / Q^L, (A + 1) / Q^L)
    if [u_m - E, u_m + E] subset I_S:
        return CERTIFIED_HIT(m)
    if [u_m - E, u_m + E] is disjoint from I_S:
        return CERTIFIED_MISS
    refine precision
```

## 16. `hello world` in Base 4

For:

```text
0_4 + hello world
```

the quaternary string is:

```text
012201211123012301233020013131233130212301210
```

Its length is:

```text
L = 45
```

So `L_max >= 45`. The query is:

```text
S = 012201211123012301233020013131233130212301210_4
A_S = int_4(S)
```

The index range is:

```text
a_min = A_S 4^(L_max - 45)
a_max = (A_S + 1) 4^(L_max - 45) - 1
```

If `L_max = 45`, this is one exact sector:

```text
a_min = A_S
a_max = A_S
```

and:

```text
locate(S) = min { m : a_m = A_S }
```

The naive expected scale of the first occurrence is about:

```text
2^90 ~= 1.24e27 bits
```

so a finite index must be explicit about its horizon.

## 17. Sector Tree / Quadtree Variant

Instead of a sorted sparse array plus RMQ, the exact finite index can be stored
as a sector prefix tree.

For `Q = 4`, this is a quadtree by angle. Each node at depth `d` corresponds to
a prefix:

```text
S_1:d
```

and a sector:

```text
I_S_1:d
```

Each node stores:

```text
node.min_m
```

among all phase points that landed inside that sector.

For each `m`, compute the depth-`L_max` path:

```text
s_1, s_2, ..., s_L_max
```

where `s_j` is the `j`th base-`Q` digit of `a_m`. Insert that path and update
`node.min_m` on every visited node:

```text
node.min_m = min(node.min_m, m)
```

Then:

```text
locate(S):
    node = root
    for symbol in S:
        node = node.child[symbol]
        if node missing:
            return NOT_FOUND_WITHIN_HORIZON
    return node.min_m
```

This is:

```text
O(|S|)
```

For `Q = 4`, it is a quadtree index. For `Q = 10`, a decatree. For `Q = 16`, a
hex-tree.

The tree should also be sparse: only visited branches need to exist.

## 18. Generalization to a Real Carrier

The phase-sector model is not specific to pi. Pi is the motivating and
experimental carrier, but the same construction works for any real carrier
`alpha` once a phase orbit has been chosen.

For a real number `alpha`, a dynamic base `B > 1`, and a sector base `Q >= 2`,
define the zero-based phase orbit:

```text
u_M^(alpha, B) = { B^M alpha },  M >= 0.
```

At grid depth `L`, the visited cell is:

```text
a_M = floor(Q^L u_M^(alpha, B)).
```

A finite word `S` over alphabet `Q` still defines the sector:

```text
I_S = [ A_S / Q^L, (A_S + 1) / Q^L ),
```

where `A_S = int_Q(S)`. The generalized locate problem is therefore:

```text
locate_(alpha,B,Q)(S)
  = min { M >= 0 : { B^M alpha } in [A_S / Q^L, (A_S + 1) / Q^L) }.
```

The pi-fs case is just `alpha = pi`. Examples:

```text
(pi, 10, 10, L)   decimal digits of pi
(pi, 10, 4, L)    decimal phase orbit, quaternary certificate grid
(pi, 4, 4, L)     quaternary digit-pair layer
(pi, 4*pi, 4, L)  pi-calibrated quaternary oscillograph layer
```

The same notation also applies to carriers such as `sqrt(2)`, `e`, or rational
numbers. The formulas do not imply that every target occurs for every carrier.
For example, rational carriers may have periodic or otherwise degenerate phase
orbits under some bases. The finite index remains an exact statement inside its
built horizon; existence outside the horizon is a separate dynamical question.

### Alpha-Calibrated Sector Systems

For a positive carrier `alpha`, one can define an `alpha`-calibrated system by
choosing:

```text
B = Q alpha
```

when `Q alpha > 1`. Then the carrier itself is an exact normalized sector
anchor:

```text
alpha / (Q alpha) = 1 / Q.
```

For `Q = 4` this gives:

```text
pi      / (4 pi)      = 1/4
sqrt(2) / (4 sqrt(2)) = 1/4
e       / (4 e)       = 1/4
```

So the special role of `pi / (4 pi)` is not a pi-only identity; it is a
coordinate choice. More generally, as a scale identity:

```text
alpha^n / (Q alpha)^n = Q^-n.
```

This means powers of the carrier have exact sector addresses in the calibrated
scale. The carrier value is unchanged; only the coordinate system changes. A
rational number remains rational and an irrational number remains irrational,
but its expansion in an irrational or carrier-calibrated coordinate system may
have a very different structure.

### Universal and Carrier-Specific Layers

The proportional and matrix layers are carrier-independent. They only compare
sector grids:

```text
A : Q^L  <->  B : Q'^L'
```

and produce overlap or containment cells by exact integer arithmetic. The
carrier enters only through the phase orbit:

```text
M -> { B^M alpha }.
```

Thus the broader object is an `alpha`-fs model: a phase-sector address system
over a real carrier. Pi-fs is the first concrete carrier studied here, not the
only possible carrier.

## 19. Comparison

```text
index type                 storage model                 query model
-------------------------  ----------------------------  -------------------------
sorted sector index        sparse (a_m, m) records       range-min over cells
sector tree / quadtree     sparse prefix tree            follow query symbols
suffix automaton           digit stream                  classic substring search
resonance index            (N, K, rho), windows (q, r)   candidate generation
```

For pi-fs, the clean practical shape is:

```text
sector tree for the exact finite index
+
resonance index for distant candidates
```

## 20. Experimental Status

The current confirmed result is not resonance compression. The confirmed core is
the finite phase-sector index:

```text
string -> circle sector
index -> phase point
locate -> range-min query over sector cells
```

Experiment 001 used the first `1,000,000` base-4 fractional digits of pi and
checked all patterns of lengths `6`, `7`, and `8`. The finite sector index
behaved as expected:

```text
L = 6:  4096 / 4096 patterns found
L = 7:  16384 / 16384 patterns found
L = 8:  65536 / 65536 patterns found
```

The mean first occurrence positions were close to the random scale `4^L`:

```text
L = 6:  mean / 4^L ~= 0.989
L = 7:  mean / 4^L ~= 0.998
L = 8:  mean / 4^L ~= 1.003
```

This supports the practical finite-index layer: once the orbit has been computed
to a horizon `M_max`, strings become sector ranges, and `locate` is a sparse
range-min lookup inside that horizon.

The same experiment tested a simple residue-only resonance heuristic: choose a
resonance modulus `K`, look at `(m - 1) mod K`, select high-frequency residue
windows from train data, and measure recall on test data. For `L = 8`, top 5%
windows did not show useful lift:

```text
K kind      K      lift
resonance   109    0.975
resonance   635    0.919
resonance   3284   0.824
resonance   15785  0.620
control     113    0.978
control     641    0.906
control     3251   0.819
control     16001  0.621
```

A random base-4 baseline behaved similarly. The result falsifies only the
simplest candidate generator:

```text
residue class modulo K alone is not enough
```

It does not falsify the phase-sector index, and it does not falsify richer
resonance candidate generation based on chord score, drift, or the full
continuous phase in `(q, r)` coordinates.

Reported follow-up experiments should be recorded with the same separation:

Confirmed:

- finite phase-sector representation;
- sparse sector lookup inside a built horizon;
- sector tree / quadtree query shape;
- chord margin as a certification metric;
- target vector construction for every finite string.

Not confirmed:

- residue-only resonance compression;
- drift-only resonance compression, unless a separate artifact shows lift
  against random and control baselines.

Open:

- approximate chord-score prediction beyond the finite horizon;
- candidate generation in full `(q, r)` resonance coordinates;
- proof or empirical evidence that any resonance feature reduces search entropy
  better than random baselines.

A companion matrix layer for translating targets between sector grids is described in
[`sector-transform-matrices.md`](sector-transform-matrices.md). Experiment 003
confirmed exact binary/quaternary transforms, sparse decimal/quaternary overlap,
and containment-based cross-base certificates.
A spiral embedding that restores index order and resonance arms is described in
[`spiral-phase-embedding.md`](spiral-phase-embedding.md). Experiment 004
confirmed matrix-transformed zero-block certificates in resonance coordinates,
but not automatic first-index discovery. Experiment 006 then tested one-step
Markov memory along resonance arms. The short-step controls showed lift, but
resonance scales `K = 87`, `1221`, and `5669` stayed near random baseline, so
this simple spiral-arm memory model is not a useful beyond-horizon candidate
generator. Experiment 007 tested walk-forward zero-block prediction from past
hits only. Random and empirical gap baselines remained competitive, and
resonance-residue predictors were noisy rather than robust, so the predictor
layer remains unconfirmed. Experiment 009 then reframed resonant indices as
exact read pointers in the quaternary digit stream. The addresses work, but
simple `M = qK` sampling looked close to random quaternary sampling, so it
confirmed the address/read layer rather than a predictive pattern. Experiment
010 closed the finite locate contour itself: target, proportional transform,
sparse phase index, certificate, and resonance address. Exhaustive checks over
`111100` decimal patterns of lengths `2..5` inside the first `500000` decimal
positions matched direct first occurrence for every found pattern, confirming
the finite acceptance engine without claiming beyond-horizon prediction.
Experiment 011 extended the address model to anchor-relative reads: repeated
anchors inside a computed horizon can be used with occurrence numbers and
negative offsets, provided the anchor and slice are certified. Experiment 013
then tested boundary continuation: a unique 100-digit tail gives 10 next-digit
candidates per step, but all 10 align with the boundary, so an independent
certificate is still required to choose the correct digit. This confirms a
continuation workflow, not a way to generate new digits without information. The
central object is an external sector certificate: an interval or sector, external
to the already known decimal prefix, that contains `frac(pi)` and is narrow
enough that proportional intersection with the prefix leaves a single next digit
or block. Experiments 014 and 015 tested that algebra directly: sufficiently
deep cross-base certificates collapse suffix or next-digit candidates to one
value. Experiment 016 then validated the same lemma across `256` boundaries,
certificate bases `2`, `4`, `8`, and `16`, and suffix lengths up to `100`. In
all of these backtests the certificates were simulated from already-known future
digits, so this validates the algebra but not a future certificate generator.

## 21. Summary

Build the finite index as:

```text
m -> u_m = { B^(m - 1) pi }
u_m -> a_m = floor(Q^L_max u_m)
a_m -> min m
```

A query becomes:

```text
S -> I_S
I_S -> [a_min, a_max]
[a_min, a_max] -> min m
```

Certification is either interval-based:

```text
[u_hat_m - E, u_hat_m + E] subset I_S
```

or chord-based:

```text
p_m . v_S - tau_S > e
```

The most natural pi-fs index is therefore a sector tree over the phase orbit of
pi: a geometric map from circle sectors to the earliest computed hit.

It is exact inside the built horizon `M_max`. Searching all infinite digits of
pi still needs either an unbounded index or an additional theorem about phase
returns.
