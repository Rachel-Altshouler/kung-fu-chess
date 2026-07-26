import unittest

from server.command_parser import parse_compact_command
from server.squares import coords_to_square, square_to_coords


class TestCommandParser(unittest.TestCase):
    def test_square_conversion(self):
        self.assertEqual(square_to_coords("e2"), (6, 4))
        self.assertEqual(square_to_coords("a8"), (0, 0))
        self.assertEqual(coords_to_square(6, 4), "e2")

    def test_parse_wqe2e5_style(self):
        parsed = parse_compact_command("WQd1d2")
        self.assertEqual(parsed["token"], "wQ")
        self.assertEqual(parsed["source"], (7, 3))
        self.assertEqual(parsed["destination"], (6, 3))

    def test_parse_rejects_bad_command(self):
        with self.assertRaises(ValueError):
            parse_compact_command("Qe2e5")


if __name__ == "__main__":
    unittest.main()
