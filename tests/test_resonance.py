import unittest

from pifs.resonance import resonance_coordinates


class ResonanceTests(unittest.TestCase):
    def test_resonance_coordinates_1221(self):
        coords = resonance_coordinates(13389)
        self.assertEqual(coords.k, 1221)
        self.assertEqual(coords.n, 2456)
        self.assertEqual(coords.q, 10)
        self.assertEqual(coords.r, 1179)
        self.assertEqual(coords.position_one_based, 13390)


if __name__ == "__main__":
    unittest.main()
