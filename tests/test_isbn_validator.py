import pytest

from metadata.isbn_validator import is_valid_isbn


@pytest.mark.parametrize(
    "isbn",
    [
        "0-306-40615-2",
        "0306406152",
        "978-0-306-40615-7",
        "9780306406157",
    ],
)
def test_valid_isbns(isbn):

    assert is_valid_isbn(isbn) is True


@pytest.mark.parametrize(
    "isbn",
    [
        "0-306-40615-3",
        "978-0-306-40615-8",
        "123",
        "",
        None,
        "not-an-isbn",
        "99999999999999",
    ],
)
def test_invalid_isbns(isbn):

    assert is_valid_isbn(isbn) is False


def test_isbn10_x_check_digit_is_accepted():

    # 0-8044-2957-X is a well-known valid ISBN-10 with an X check digit.
    assert is_valid_isbn("0-8044-2957-X") is True
