from models.author import Author
from models.book import Book
from models.format_file import FormatFile
from repair.file_organizer import FileOrganizer, sanitize_component


def make_book(book_id, title, author_name, path, formats=()):

    book = Book(id=book_id, title=title, path=path)

    if author_name:
        book.authors.append(Author(id=book_id, name=author_name))

    book.format_files = [FormatFile(format=fmt, name=name) for fmt, name in formats]

    return book


def test_sanitize_removes_illegal_characters():

    assert sanitize_component('Title: "The Best"?') == "Title The Best"


def test_sanitize_falls_back_when_empty():

    assert sanitize_component("   ") == "Unknown"
    assert sanitize_component("", fallback="Untitled") == "Untitled"


def test_sanitize_strips_trailing_dots_and_spaces():

    assert sanitize_component("Trailing Space. . ") == "Trailing Space"


def test_plan_uses_author_and_title():

    book = make_book(1, "Doctor Sleep", "Stephen King", "Stephen King/Doctor Sleep (1)")

    plans = FileOrganizer().build_plan([book])

    assert plans[0].proposed_path == "Stephen King/Doctor Sleep"
    assert plans[0].folder_changed is True


def test_plan_leaves_already_clean_paths_alone():

    book = make_book(1, "Doctor Sleep", "Stephen King", "Stephen King/Doctor Sleep")

    plans = FileOrganizer().build_plan([book])

    assert plans[0].folder_changed is False
    assert plans[0].has_changes is False


def test_plan_falls_back_to_unknown_author():

    book = make_book(2, "Some Book", None, "Unknown/Some Book (2)")

    plans = FileOrganizer().build_plan([book])

    assert plans[0].proposed_path == "Unknown/Some Book"


def test_plan_disambiguates_folder_collisions():

    book_a = make_book(1, "Same Title", "Same Author", "x")
    book_b = make_book(2, "Same Title", "Same Author", "y")

    plans = FileOrganizer().build_plan([book_a, book_b])

    assert plans[0].proposed_path == "Same Author/Same Title"
    assert plans[1].proposed_path == "Same Author/Same Title (2)"
    assert plans[0].proposed_path != plans[1].proposed_path


def test_plan_includes_format_renames():

    book = make_book(
        1,
        "Doctor Sleep",
        "Stephen King",
        "Stephen King/Doctor Sleep (1)",
        formats=[("EPUB", "Doctor Sleep - Stephen King")],
    )

    plans = FileOrganizer().build_plan([book])
    rename = plans[0].format_renames[0]

    assert rename.old_name == "Doctor Sleep - Stephen King"
    assert rename.new_name == "Doctor Sleep"
    assert rename.changed is True


def test_plans_with_changes_filters_unchanged():

    clean = make_book(1, "Clean", "Author", "Author/Clean")
    messy = make_book(2, "Messy", "Author", "Author/Messy (2)")

    plans = FileOrganizer().plans_with_changes([clean, messy])

    assert len(plans) == 1
    assert plans[0].book_id == 2
