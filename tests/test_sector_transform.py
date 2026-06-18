import unittest

from pifs.certificate import certify_cell_containment
from pifs.transform import boundary_cells, contained_cells, intersecting_cells
from pifs.sector_transform import sector_count


class SectorTransformTests(unittest.TestCase):
    def test_decimal_1000_zeros_to_quaternary_certifying_cell(self):
        self.assertEqual(list(intersecting_cells(10, 1000, 0, 4, 1661)), [0, 1])
        self.assertEqual(list(contained_cells(10, 1000, 0, 4, 1661)), [0])
        self.assertEqual(boundary_cells(10, 1000, 0, 4, 1661), [1])
        self.assertTrue(certify_cell_containment(10, 1000, 0, 4, 1661, 0))
        self.assertFalse(certify_cell_containment(10, 1000, 0, 4, 1661, 1))

    def test_binary_quaternary_exact_mapping(self):
        for depth in range(1, 13):
            total = sector_count(4, depth)
            for cell in (0, total // 2, total - 1):
                self.assertEqual(list(intersecting_cells(4, depth, cell, 2, 2 * depth)), [cell])
                self.assertEqual(list(contained_cells(4, depth, cell, 2, 2 * depth)), [cell])
                self.assertEqual(boundary_cells(4, depth, cell, 2, 2 * depth), [])


if __name__ == "__main__":
    unittest.main()
