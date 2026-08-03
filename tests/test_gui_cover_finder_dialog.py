from gui.cover_finder_dialog import format_candidate_line, pick_best_candidate
from repair.cover_finder import CoverCandidate


def make_candidate(
    source="openlibrary",
    width=1000,
    height=1500,
    image_format="JPEG",
    score=100,
    issues=None,
    is_duplicate=False,
):

    candidate = CoverCandidate(
        source=source,
        width=width,
        height=height,
        format=image_format,
        quality_score=score,
        is_duplicate=is_duplicate,
    )
    candidate.issues = issues or []

    return candidate


def test_format_candidate_line_shows_ok_status_for_valid_candidate():

    line = format_candidate_line(1, make_candidate())

    assert line.startswith("[1] openlibrary")
    assert "1000x1500" in line
    assert "JPEG" in line
    assert "score=100" in line
    assert "ok" in line
    assert "invalid" not in line


def test_format_candidate_line_shows_invalid_status_and_issues():

    candidate = make_candidate(issues=["Resolution too low: 100x150 (minimum 300x300)"])

    line = format_candidate_line(1, candidate)

    assert "invalid" in line
    assert "Resolution too low" in line


def test_format_candidate_line_flags_duplicate():

    line = format_candidate_line(1, make_candidate(is_duplicate=True))

    assert "duplicate of existing cover" in line


def test_pick_best_candidate_returns_highest_score_among_valid_non_duplicates():

    candidates = [
        make_candidate(score=50),
        make_candidate(score=90),
        make_candidate(score=70),
    ]

    chosen = pick_best_candidate(candidates)

    assert chosen.quality_score == 90


def test_pick_best_candidate_skips_invalid_candidates():

    candidates = [
        make_candidate(score=100, issues=["Corrupt or unreadable image"]),
        make_candidate(score=60),
    ]

    chosen = pick_best_candidate(candidates)

    assert chosen.quality_score == 60


def test_pick_best_candidate_skips_duplicates():

    candidates = [
        make_candidate(score=100, is_duplicate=True),
        make_candidate(score=60),
    ]

    chosen = pick_best_candidate(candidates)

    assert chosen.quality_score == 60


def test_pick_best_candidate_returns_none_when_nothing_eligible():

    candidates = [
        make_candidate(score=100, is_duplicate=True),
        make_candidate(score=60, issues=["bad"]),
    ]

    assert pick_best_candidate(candidates) is None


def test_pick_best_candidate_returns_none_for_empty_list():

    assert pick_best_candidate([]) is None
