import unittest

from pifs.finite_index import certifying_depth, describe_result
from pifs.locate import build_decimal_quaternary_index, direct_search_digits, locate_decimal_digits, locate_digits


class FiniteLocateTests(unittest.TestCase):
    def test_locate_zero_block_matches_direct_search(self):
        digits = "314159000012345"
        pattern = "0000"
        depth = certifying_depth(10, len(pattern), 4)
        index = build_decimal_quaternary_index(digits, depth=depth, precision_digits=8)

        result = locate_digits(index, pattern)
        self.assertTrue(result.found)
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.m_zero_based, direct_search_digits(digits, pattern))
        self.assertEqual(result.certificate, "matrix-sector-contained")

        summary = describe_result(result)
        self.assertEqual(summary["position"], direct_search_digits(digits, pattern) + 1)
        self.assertEqual(summary["resonance"]["K"], 1221)
        self.assertEqual(summary["resonance"]["N"], 2456)

    def test_locate_decimal_digits_one_shot(self):
        digits = "314159000012345"
        result = locate_decimal_digits(digits, "0000", precision_digits=8)
        self.assertTrue(result.found)
        self.assertIsNotNone(result.record)
        self.assertEqual(result.record.m_zero_based, digits.find("0000"))

    def test_not_found_within_horizon(self):
        digits = "314159000012345"
        result = locate_decimal_digits(digits, "987654", depth=16, precision_digits=8)
        self.assertFalse(result.found)
        self.assertEqual(result.certificate, "not-found-within-horizon")


if __name__ == "__main__":
    unittest.main()
