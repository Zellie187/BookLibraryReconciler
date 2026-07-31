"""
Calibre SQL Function Compatibility

Calibre's metadata.db defines triggers (books_insert_trg,
books_update_trg) that call custom SQL functions Calibre itself
registers at runtime via sqlite3.Connection.create_function() when it
opens the database. Any external tool that writes to a column those
triggers watch must register equivalent functions, or the write fails
with "no such function: <name>" - the trigger body is only evaluated
for rows it actually matches, so this only bites when the write
actually changes a watched column (e.g. updating books.title, but not
books.path).

Currently only title_sort() is needed.
"""

import re

_LEADING_ARTICLE = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)


def calculate_title_sort(title):
    """
    Replicates Calibre's title_sort(): move a leading "The"/"A"/"An"
    to the end - "The Hobbit" -> "Hobbit, The". Verified against real
    sort values already stored in the bundled sample library.
    """

    if not title:
        return title

    match = _LEADING_ARTICLE.match(title)

    if not match:
        return title

    article = match.group(1)
    rest = title[match.end() :]

    return f"{rest}, {article}"
