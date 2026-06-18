# Proportional Sector Arithmetic

This document defines the exact proportional layer used by `pi-fs`.

The guiding idea is simple:

```text
A sector is a proportion.
```

A string in base `Q` of depth `L` is a sector of the unit interval:

```text
I_A^(Q,L) = [ A / Q^L, (A + 1) / Q^L )
```

where `A = int_Q(S)`.

Changing systems is not a symbolic digit conversion. It is a geometric relation between two partitions of the same circle / unit interval.

## 1. Overlap by cross-multiplication

Let the source sector be:

```text
I_A = [ A / M, (A + 1) / M )
M = Q^L
```

and the target grid be:

```text
J_B = [ B / N, (B + 1) / N )
N = Q2^L2
```

`J_B` intersects `I_A` iff:

```text
B / N < (A + 1) / M
(B + 1) / N > A / M
```

By cross-multiplication:

```text
B M < (A + 1) N
(B + 1) M > A N
```

So the intersecting cell range is:

```text
B_min = floor(A N / M)
B_max = ceil((A + 1) N / M) - 1
```

## 2. Containment by cross-multiplication

For strict certification we need:

```text
J_B subset I_A
```

That means:

```text
B / N >= A / M
(B + 1) / N <= (A + 1) / M
```

So:

```text
B_min_contained = ceil(A N / M)
B_max_contained = floor((A + 1) N / M) - 1
```

Cells in this range are certifying cells.

## 3. Decimal zero blocks to quaternary cells

A decimal zero block of length `D` is:

```text
[0, 10^-D)
```

To represent it in a quaternary grid, choose minimal `L4` such that:

```text
4^L4 >= 10^D
```

For `D = 1000`:

```text
L4 = 1661
```

Then:

```text
[0, 4^-1661) subset [0, 10^-1000)
```

Therefore:

```text
floor(4^1661 * {10^M pi}) = 0
    => 1000 decimal zeros at position M + 1
```

The boundary cell `1` intersects the target but requires refinement.

## 4. Binary/quaternary exactness

Because:

```text
0_4 = 00_2
1_4 = 01_2
2_4 = 10_2
3_4 = 11_2
```

the transform:

```text
(4, L) <-> (2, 2L)
```

is exact. The sector cell number is the same integer.

## 5. Resonance as logarithmic proportion

Sector proportions convert targets. Resonance proportions convert scales.

If:

```text
base_from^N ~= base_to^K
```

then:

```text
K / N ~= log_{base_to}(base_from)
```

For the decimal pi resonance:

```text
pi^2456 ~= 10^1221
```

so:

```text
K = 1221
N = 2456
M = 1221 q + r
```

This is an address chart, not a standalone predictor.

## 6. Design rule

Use proportional sector arithmetic for proofs and certificates:

```text
target -> certifying cells
```

Use resonance only as an address annotation or candidate coordinate:

```text
M -> (q, r)
```

The certificate remains exact because it is based on integer proportions.

## 7. Closed finite locate check

Experiment 010 used this proportional layer as the first step of a closed finite
locate contour:

```text
decimal target -> proportional cells in (4, 11) -> sparse phase index
```

The check covered all decimal patterns of lengths `2..5` inside the first
`500000` decimal positions. Intersect-cell lookup plus verification matched the
direct first occurrence for every pattern found inside the horizon. Contained
lookup kept precision `1.0`, but can return a later hit when the first direct
occurrence lies in a boundary cell.

This confirms the proportional layer as an exact target transform for finite
locate. It does not make proportional arithmetic a beyond-horizon predictor.
