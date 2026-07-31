import time

from providers.response_cache import ResponseCache


def test_get_returns_none_when_nothing_cached(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=60)

    assert cache.get("https://example.com/a") is None


def test_set_then_get_round_trips(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=60)

    cache.set("https://example.com/a", {"title": "Doctor Sleep"})

    assert cache.get("https://example.com/a") == {"title": "Doctor Sleep"}


def test_different_urls_are_cached_separately(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=60)

    cache.set("https://example.com/a", {"value": 1})
    cache.set("https://example.com/b", {"value": 2})

    assert cache.get("https://example.com/a") == {"value": 1}
    assert cache.get("https://example.com/b") == {"value": 2}


def test_expired_entry_returns_none(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=0.01)

    cache.set("https://example.com/a", {"value": 1})

    time.sleep(0.05)

    assert cache.get("https://example.com/a") is None


def test_corrupted_cache_file_is_treated_as_a_miss(tmp_path):

    cache = ResponseCache(tmp_path / "cache", ttl_seconds=60)

    cache.set("https://example.com/a", {"value": 1})
    path = cache._path_for("https://example.com/a")
    path.write_text("not valid json", encoding="utf-8")

    assert cache.get("https://example.com/a") is None
