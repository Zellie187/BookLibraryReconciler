from metadata.author_duplicate_finder import AuthorDuplicateFinder
from models.author import Author


def test_finds_duplicates_regardless_of_punctuation_or_word_order():

    authors = [
        Author(id=1, name="Stephen King"),
        Author(id=5, name="King, Stephen"),
        Author(id=9, name="King Stephen"),
    ]

    groups = AuthorDuplicateFinder().find_duplicates(authors)

    assert len(groups) == 1
    assert groups[0].canonical_author_id == 1
    assert set(groups[0].duplicate_author_ids) == {5, 9}


def test_canonical_id_is_the_lowest():

    authors = [Author(id=10, name="Jim Butcher"), Author(id=3, name="Butcher, Jim")]

    groups = AuthorDuplicateFinder().find_duplicates(authors)

    assert groups[0].canonical_author_id == 3
    assert groups[0].duplicate_author_ids == [10]


def test_no_groups_for_distinct_authors():

    authors = [Author(id=1, name="Stephen King"), Author(id=2, name="Terry Pratchett")]

    assert AuthorDuplicateFinder().find_duplicates(authors) == []


def test_single_author_is_not_a_duplicate():

    authors = [Author(id=1, name="Stephen King")]

    assert AuthorDuplicateFinder().find_duplicates(authors) == []


def test_authors_with_blank_names_are_ignored():

    authors = [Author(id=1, name=""), Author(id=2, name="")]

    assert AuthorDuplicateFinder().find_duplicates(authors) == []


def test_all_author_ids_includes_canonical_and_duplicates():

    authors = [Author(id=1, name="Stephen King"), Author(id=2, name="King, Stephen")]

    group = AuthorDuplicateFinder().find_duplicates(authors)[0]

    assert group.all_author_ids == [1, 2]
