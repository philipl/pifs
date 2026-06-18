# Add finite matrix-sector locate engine

## Summary

This branch adds the first closed `pi-fs locate` proof-of-concept contour:

```text
target -> proportion -> finite phase index -> certificate -> resonance address
```

The branch includes:

- phase-sector locate theory;
- generalized real-carrier formulation where `pi-fs` is the `alpha = pi` case;
- proportional sector arithmetic;
- sector transform matrices;
- finite matrix-sector locate engine notes;
- reference modules under `pifs/`;
- tests for proportional transforms and the finite locate contour.

## What Is Confirmed

This PR is not a claim that we can predict arbitrary first occurrences in
infinite pi.

It confirms a finite-horizon locate engine:

```text
pattern -> sector -> proportional transform -> sparse phase index -> certificate -> resonance coordinates
```

Inside a built finite horizon, the locate path can reproduce direct search and
attach proof/certificate metadata. The docs also generalize the phase-sector
formulation from `pi` to an arbitrary real carrier `alpha`; the current PoC uses
`alpha = pi` as the tested carrier.

## Key Certificate Example

For `1000` decimal zeros:

```text
[0, 4^-1661) subset [0, 10^-1000)
```

Therefore:

```text
floor(4^1661 * {10^M pi}) = 0
    => 1000 decimal zeros at position M + 1
```

This is exact proportional arithmetic, not a heuristic.

## Resonance Address Annotation

The located zero-based position `M` can be annotated by the medium decimal
resonance chart:

```text
M = 1221 q + r
pi^2456 ~= 10^1221
```

This is an address coordinate, not a standalone predictor.

## Experimental Status

The docs record the experimental boundary:

- finite sector/quadtree index works;
- proportional target transforms work;
- contained cells provide strict certificates;
- closed finite locate contour was checked against direct search for decimal
  patterns of lengths `2..5` inside `H = 500000`;
- anchor-relative addressing works around certified repeated anchors inside a
  computed horizon;
- boundary continuation works as a 10-candidate loop when an independent
  next-digit certificate is available;
- external sector certificates formalize how the next digit or block is extracted
  from a certified sector that is narrower than the known decimal prefix;
- the concrete `99 + y` corollary records the exact one-digit formula
  `y = A - 10 P_99` after proportional intersection leaves one candidate;
- algebraic suffix recovery and next-digit recovery collapse candidates to one
  value when a sufficiently deep cross-base certificate is supplied;
- Experiment 016 validates the external sector certificate lemma over `256`
  boundaries, certificate bases `2`, `4`, `8`, and `16`, and suffix lengths up
  to `100`;
- simple residue, drift, spiral, and walk-forward predictors did not show robust
  beyond-horizon lift;
- boundary continuation does not generate new digits without an independent
  certificate;
- Experiment 014/015/016 certificates were simulated from already-computed
  future digits, so they validate the algebra but not a certificate generator.

## Scope

This PR should be treated as the first locate MVP foundation:

```text
exact finite locate + proof object
```

Future work can add candidate generators or continuation oracles, but acceptance
should go through this same sector certificate layer. The continuation path still
needs an external sector certificate; it does not infer future digits from the
known tail alone.

## Local Verification

```sh
python3 -m unittest discover -s tests
```

Smoke checks:

```py
from pifs.proportion import decimal_zero_certifying_cells

t = decimal_zero_certifying_cells(1000, target_base=4)
assert t.target_depth == 1661
assert t.contained.to_list() == [0]
assert t.intersect.to_list() == [0, 1]
```

```py
from pifs.locate import locate_decimal_digits

digits = "14159265358979323846264338327950288419716939937510"
result = locate_decimal_digits(
    digits,
    "14",
    cert_base=4,
    horizon=len(digits) - 2,
    mode="intersecting",
)
assert result.found
assert result.record.m_zero_based == 0
```
