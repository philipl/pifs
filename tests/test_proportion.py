import math
import unittest
from fractions import Fraction

from pifs.proportion import (
    CellRange,
    contained_cells,
    contained_range,
    decimal_medium_resonance,
    decimal_zero_certifying_cells,
    exact_binary_quaternary_cell,
    intersect_range,
    intersecting_cells,
    logarithmic_resonance_pairs,
    required_depth_cover,
    resonance_ratio,
    sector_proportion,
    sector_ratio,
    transform_sector,
)


class ProportionTests(unittest.TestCase):
    def test_binary_quaternary_exact_identity(self):
        for depth in range(1, 8):
            for cell in range(4**depth):
                self.assertEqual(exact_binary_quaternary_cell(cell, depth), cell)
                transform = transform_sector(cell, 4, depth, 2, 2 * depth)
                self.assertEqual(transform.intersect, CellRange(cell, cell))
                self.assertEqual(transform.contained, CellRange(cell, cell))
                self.assertEqual(transform.boundary, 0)
                self.assertEqual(list(intersect_range(cell, 4, depth, 2, 2 * depth)), [cell])
                self.assertEqual(list(contained_range(cell, 4, depth, 2, 2 * depth)), [cell])

    def test_decimal_1000_zeros_to_quaternary_cert_cell(self):
        self.assertEqual(required_depth_cover(10, 1000, 4), 1661)
        transform = decimal_zero_certifying_cells(1000, target_base=4)
        self.assertEqual(transform.target_depth, 1661)
        self.assertEqual(transform.contained, CellRange(0, 0))
        self.assertEqual(transform.intersect, CellRange(0, 1))
        self.assertEqual(transform.boundary, 1)
        self.assertEqual(list(intersect_range(0, 10, 1000, 4, 1661)), [0, 1])
        self.assertEqual(list(contained_range(0, 10, 1000, 4, 1661)), [0])

    def test_decimal_small_zero_blocks(self):
        cases = {
            1: (2, CellRange(0, 0), CellRange(0, 1)),
            2: (4, CellRange(0, 1), CellRange(0, 2)),
            3: (5, CellRange(0, 0), CellRange(0, 1)),
            4: (7, CellRange(0, 0), CellRange(0, 1)),
            5: (9, CellRange(0, 1), CellRange(0, 2)),
            6: (10, CellRange(0, 0), CellRange(0, 1)),
        }
        for digits, (depth4, contained, intersect) in cases.items():
            transform = decimal_zero_certifying_cells(digits, target_base=4)
            self.assertEqual(transform.target_depth, depth4)
            self.assertEqual(transform.contained, contained)
            self.assertEqual(transform.intersect, intersect)

    def test_against_bruteforce_small_grids(self):
        for q, depth, q2, depth2 in [
            (3, 2, 4, 3),
            (10, 1, 4, 2),
            (5, 2, 2, 5),
            (4, 3, 10, 2),
        ]:
            source_den = q**depth
            target_den = q2**depth2
            for cell in range(source_den):
                brute_intersect = [
                    b
                    for b in range(target_den)
                    if b * source_den < (cell + 1) * target_den and (b + 1) * source_den > cell * target_den
                ]
                brute_contained = [
                    b
                    for b in range(target_den)
                    if b * source_den >= cell * target_den and (b + 1) * source_den <= (cell + 1) * target_den
                ]
                self.assertEqual(intersecting_cells(cell, q, depth, q2, depth2).to_list(), brute_intersect)
                self.assertEqual(contained_cells(cell, q, depth, q2, depth2).to_list(), brute_contained)

    def test_sector_ratio_and_proportion(self):
        self.assertEqual(sector_ratio(1, 4, 1), Fraction(1, 4))
        self.assertEqual(sector_proportion(1, 4, 1), (1, 4))

    def test_medium_decimal_resonance(self):
        resonance = decimal_medium_resonance()
        self.assertEqual(resonance["K"], 1221)
        self.assertEqual(resonance["N"], 2456)
        self.assertLess(abs(resonance["ratio_minus_1_approx"] - 0.0002011206), 1e-8)

    def test_logarithmic_resonance_pairs_contains_medium_pair(self):
        pairs = logarithmic_resonance_pairs(math.pi, 10, max_terms=16)
        self.assertTrue(any(pair["K"] == 1221 and pair["N"] == 2456 for pair in pairs))
        self.assertEqual(resonance_ratio(math.pi, 10, 1300), Fraction(2456, 1221))
        self.assertEqual(resonance_ratio(math.pi, 10, 100), Fraction(175, 87))


if __name__ == "__main__":
    unittest.main()
