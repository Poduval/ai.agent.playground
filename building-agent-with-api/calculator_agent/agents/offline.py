"""Tiny rule-based parser so the stack can be tried without any LLM (`--demo`)."""

import re

_NUM = r"(-?\d+(?:\.\d+)?)"
_PATTERNS = [
    ("add", rf"{_NUM}\s*(?:plus|added to|\+)\s*{_NUM}"),
    ("subtract", rf"{_NUM}\s*(?:minus|-)\s*{_NUM}"),
    ("multiply", rf"{_NUM}\s*(?:multiplied by|times|x|\*)\s*{_NUM}"),
    ("divide", rf"{_NUM}\s*(?:divided by|over|/)\s*{_NUM}"),
]


def parse_question(question: str) -> tuple[str, float, float]:
    """'What is 6 times 7?' -> ('multiply', 6.0, 7.0)."""
    for operation, pattern in _PATTERNS:
        if match := re.search(pattern, question, re.IGNORECASE):
            return operation, float(match.group(1)), float(match.group(2))
    raise ValueError("Try: 'What is 6 times 7?', '10 minus 4', '9 divided by 3' or '2 plus 2'.")
