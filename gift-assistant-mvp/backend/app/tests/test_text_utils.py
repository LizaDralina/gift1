from app.utils.text import normalize_text, normalize_list, parse_tags

def test_normalize_text_lowercase_and_strip():
    assert normalize_text("  Космос  ") == "космос"

def test_normalize_text_none():
    assert normalize_text(None) == ""

def test_normalize_list():
    assert normalize_list([" Космос ", "", "Техника", None]) == ["космос", "техника"]

def test_parse_tags_pipe_separator():
    assert parse_tags("космос|книги|наука") == ["космос", "книги", "наука"]

def test_parse_tags_multiple_separators():
    assert parse_tags("космос, книги; техника|спорт") == [
        "космос",
        "книги",
        "техника",
        "спорт",
    ]
