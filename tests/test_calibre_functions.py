import pytest

from core.calibre_functions import calculate_title_sort


@pytest.mark.parametrize(
    "title,expected",
    [
        ("The Maze of Bones by Rick Riordan", "Maze of Bones by Rick Riordan, The"),
        ("The Tombs - Cussler, Clive", "Tombs - Cussler, Clive, The"),
        ("Doctor Sleep", "Doctor Sleep"),
        ("A Study in Scarlet", "Study in Scarlet, A"),
        ("An American Tragedy", "American Tragedy, An"),
        ("", ""),
        (None, None),
    ],
)
def test_calculate_title_sort(title, expected):

    assert calculate_title_sort(title) == expected
