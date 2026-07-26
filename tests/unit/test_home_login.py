import tempfile
import unittest
from pathlib import Path

from server.elo import pair_result_scores, update_elo
from server.user_db import DEFAULT_RATING, UserDatabase


class TestUserDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = UserDatabase(Path(self.tmp.name) / "users.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_starts_at_1200(self):
        result = self.db.authenticate_or_register("alice", "secret")
        self.assertTrue(result["ok"])
        self.assertTrue(result["created"])
        self.assertEqual(result["rating"], DEFAULT_RATING)

    def test_wrong_password_denied(self):
        self.db.authenticate_or_register("alice", "secret")
        result = self.db.authenticate_or_register("alice", "wrong")
        self.assertFalse(result["ok"])

    def test_correct_password_login(self):
        self.db.authenticate_or_register("alice", "secret")
        result = self.db.authenticate_or_register("alice", "secret")
        self.assertTrue(result["ok"])
        self.assertFalse(result["created"])
        self.assertEqual(result["rating"], 1200)

    def test_set_rating(self):
        self.db.authenticate_or_register("alice", "secret")
        self.db.set_rating("alice", 1234)
        self.assertEqual(self.db.get_rating("alice"), 1234)


class TestElo(unittest.TestCase):
    def test_winner_gains_points(self):
        new_a = update_elo(1200, 1200, 1.0)
        new_b = update_elo(1200, 1200, 0.0)
        self.assertGreater(new_a, 1200)
        self.assertLess(new_b, 1200)

    def test_draw_keeps_equal_ratings_close(self):
        new_a = update_elo(1200, 1200, 0.5)
        self.assertEqual(new_a, 1200)

    def test_pair_result_scores(self):
        self.assertEqual(pair_result_scores("w", False), (1.0, 0.0))
        self.assertEqual(pair_result_scores("b", False), (0.0, 1.0))
        self.assertEqual(pair_result_scores(None, True), (0.5, 0.5))


if __name__ == "__main__":
    unittest.main()
