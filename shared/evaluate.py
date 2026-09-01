"""Answer extraction and scoring utilities shared across all experiments.

Extraction follows the two-step convention already established in
experiments/01_sequential_arithmetic/run.py:

    1. Look for an explicit ANSWER: <value> marker (primary).
    2. Fall back to the last integer in the response (arithmetic only).
"""

from __future__ import annotations

import re
from typing import Any

# Primary extraction regex — matches the ANSWER: marker used in all prompts.
ANSWER_RE = re.compile(r"ANSWER:\s*(.+?)(?:\n|$)", re.IGNORECASE)

# Fallback: last integer in the output (arithmetic tasks only).
INTEGER_RE = re.compile(r"-?\d+")


def extract_answer(text: str, task_type: str = "arithmetic") -> str | int | None:
    """Return the predicted answer from a model response.

    For arithmetic tasks the return value is an int (or None).
    For all other task types the return value is a lowercased str (or None).
    """
    match = ANSWER_RE.search(text)
    if match:
        raw = match.group(1).strip()
        if task_type == "arithmetic":
            ints = INTEGER_RE.findall(raw)
            return int(ints[-1]) if ints else None
        return raw.lower()

    # Fallback for arithmetic only.
    if task_type == "arithmetic":
        integers = INTEGER_RE.findall(text)
        return int(integers[-1]) if integers else None

    return None


def is_correct(predicted: Any, expected: Any, task_type: str = "arithmetic") -> bool:
    """Compare predicted and expected answers.

    - arithmetic: integer equality.
    - symbolic / object_tracking / logical: case-insensitive string equality.
    """
    if predicted is None:
        return False
    if task_type == "arithmetic":
        return int(predicted) == int(expected)
    return str(predicted).strip().lower() == str(expected).strip().lower()


def accuracy(records: list[dict]) -> float:
    """Fraction of records where correct == True."""
    if not records:
        return float("nan")
    return sum(1 for r in records if r.get("correct")) / len(records)
