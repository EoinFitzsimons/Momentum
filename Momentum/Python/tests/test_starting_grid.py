import unittest
import sys
import os

# Ensure the package root (Momentum/Python) is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GUI import gui_race_visual


class DummyCar:
    def __init__(self, driver_id, s):
        self.driver_id = driver_id
        self.s = s


class DummyTrackWidget:
    def __init__(self, cars):
        self.cars = cars


class StartingGridTest(unittest.TestCase):
    def test_prefers_visual_order_when_sets_match(self):
        # starting grid recorded in reverse order
        starting_grid = [4, 3, 2, 1]
        # visual cars are in ascending s (1..4)
        cars = [DummyCar(1, 0.0), DummyCar(2, 10.0), DummyCar(3, 20.0), DummyCar(4, 30.0)]
        tw = DummyTrackWidget(cars)
        corrected = gui_race_visual.compute_canonical_starting_grid(starting_grid, tw)
        self.assertEqual(corrected, [1, 2, 3, 4])

    def test_returns_original_when_sets_differ(self):
        starting_grid = [5, 6, 7]
        cars = [DummyCar(1, 0.0), DummyCar(2, 10.0), DummyCar(3, 20.0)]
        tw = DummyTrackWidget(cars)
        corrected = gui_race_visual.compute_canonical_starting_grid(starting_grid, tw)
        self.assertEqual(corrected, starting_grid)


if __name__ == '__main__':
    unittest.main()
