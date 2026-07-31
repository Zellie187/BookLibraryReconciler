"""
Response Cache

Simple file-based cache for provider HTTP responses, keyed by URL.
Avoids hammering a free public API for the same lookup repeatedly, and
lets a provider work in "offline" mode from previously-cached results.
"""

import hashlib
import json
import time
from pathlib import Path


class ResponseCache:

    def __init__(self, cache_dir, ttl_seconds):

        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds

    # ---------------------------------------------------------

    def _path_for(self, url):

        key = hashlib.sha256(url.encode("utf-8")).hexdigest()

        return self.cache_dir / f"{key}.json"

    # ---------------------------------------------------------

    def get(self, url):

        path = self._path_for(url)

        if not path.exists():
            return None

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        if time.time() - payload.get("cached_at", 0) > self.ttl_seconds:
            return None

        return payload.get("data")

    # ---------------------------------------------------------

    def set(self, url, data):

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        payload = {"cached_at": time.time(), "data": data}

        self._path_for(url).write_text(json.dumps(payload), encoding="utf-8")
