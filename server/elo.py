from __future__ import annotations


def expected_score(rating_a: int, rating_b: int) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

#זו הפונקציה שמחשבת את הדירוג החדש של שחקן A, אחרי שהמשחק הסתיים
def update_elo(rating_a: int, rating_b: int, score_a: float, k: int = 32) -> int:
    """Return new rating for player A. score_a: 1 win, 0.5 draw, 0 loss."""
    expected = expected_score(rating_a, rating_b)
    return int(round(rating_a + k * (score_a - expected)))


def pair_result_scores(winner_color: str | None, is_stalemate: bool) -> tuple[float, float]:
    """Return (white_score, black_score) for ELO update."""
    if is_stalemate or winner_color is None:
        return 0.5, 0.5
    if winner_color == "w":
        return 1.0, 0.0
    if winner_color == "b":
        return 0.0, 1.0
    return 0.5, 0.5
