"""
Text Normalization

Shared helper for recognizing "the same words, different formatting"
across titles, author names, etc.
"""

import re


def name_signature(text):
    """
    Word-set signature - "Berry, Steve", "Steve Berry", and "Berry
    Steve" all produce the same signature, regardless of punctuation
    or word order.
    """

    return tuple(sorted(re.findall(r"\w+", (text or "").lower())))
