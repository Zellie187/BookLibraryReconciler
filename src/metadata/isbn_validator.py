"""
ISBN Checksum Validation

Standard ISBN-10 and ISBN-13 checksum algorithms. This only checks
whether an ISBN is *internally consistent* (the check digit matches),
not whether it's real or matches the book - that would need a
provider lookup (see providers/).
"""

import re


def _clean(raw_isbn):

    return re.sub(r"[\s-]", "", raw_isbn or "").upper()


def _is_valid_isbn10(isbn):

    if len(isbn) != 10:
        return False

    total = 0

    for position, char in enumerate(isbn):

        if char == "X" and position == 9:
            value = 10
        elif char.isdigit():
            value = int(char)
        else:
            return False

        total += (10 - position) * value

    return total % 11 == 0


def _is_valid_isbn13(isbn):

    if len(isbn) != 13 or not isbn.isdigit():
        return False

    total = sum(int(digit) * (1 if position % 2 == 0 else 3) for position, digit in enumerate(isbn))

    return total % 10 == 0


def is_valid_isbn(raw_isbn):
    """
    True if raw_isbn is a 10 or 13 character ISBN whose check digit is
    correct. Anything else (wrong length, non-ISBN identifier, blank)
    returns False rather than raising.
    """

    isbn = _clean(raw_isbn)

    if len(isbn) == 10:
        return _is_valid_isbn10(isbn)

    if len(isbn) == 13:
        return _is_valid_isbn13(isbn)

    return False
