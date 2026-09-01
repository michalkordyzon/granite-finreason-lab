"""Synthetic problem generators for controlled reasoning-depth experiments.

Each generator returns a (prompt, expected_answer) pair for a given depth.
All generators keep individual operations trivial so depth — not arithmetic
difficulty — is the sole independent variable.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Common record type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Problem:
    task_id: str
    task_type: str  # "arithmetic" | "symbolic" | "object_tracking" | "logical"
    depth: int
    prompt: str
    expected: int | str  # int for arithmetic, str for others


# ---------------------------------------------------------------------------
# Experiment A — sequential arithmetic transformations
# ---------------------------------------------------------------------------


def make_arithmetic(rng: random.Random, depth: int, index: int) -> Problem:
    """Bounded integer chain: add / subtract / multiply with small operands.

    Values stay in (-1000, 1000) by choosing only +/- for large numbers.
    """
    value = rng.randint(10, 99)
    steps: list[str] = [f"Start with {value}."]

    for _ in range(depth):
        operation = rng.choice(("add", "subtract", "multiply"))
        if operation == "multiply":
            operand = rng.randint(2, 4)
        else:
            operand = rng.randint(2, 12)

        if operation == "add":
            value += operand
            steps.append(f"Add {operand}.")
        elif operation == "subtract":
            value -= operand
            steps.append(f"Subtract {operand}.")
        else:
            value *= operand
            steps.append(f"Multiply the current result by {operand}.")

    steps.append(
        "What is the final value?\n\nReturn the final result using exactly:\nANSWER: <integer>"
    )
    return Problem(
        task_id=f"arith_depth{depth:02d}_{index:04d}",
        task_type="arithmetic",
        depth=depth,
        prompt="\n".join(steps),
        expected=value,
    )


# ---------------------------------------------------------------------------
# Experiment B — symbolic variable swaps
# ---------------------------------------------------------------------------

_COLORS = ("red", "blue", "green", "yellow", "orange", "purple", "white", "black")
_VAR_NAMES = ("A", "B", "C", "D", "E", "F")


def make_symbolic(rng: random.Random, depth: int, index: int) -> Problem:
    """Track variable assignments through a sequence of swap operations.

    Three variables, each holding a distinct colour.  After *depth* swaps,
    query the value of one variable.
    """
    n_vars = 3
    names = _VAR_NAMES[:n_vars]
    colors = list(rng.sample(_COLORS, n_vars))
    state: dict[str, str] = dict(zip(names, colors))

    init_lines = ["Initial state:"] + [f"{k} = {v}" for k, v in state.items()]
    ops: list[str] = []

    for _ in range(depth):
        a, b = rng.sample(names, 2)
        state[a], state[b] = state[b], state[a]
        ops.append(f"Swap {a} and {b}.")

    query_var = rng.choice(names)
    expected = state[query_var]

    prompt = (
        "\n".join(init_lines)
        + "\n\nPerform the following operations:\n"
        + "\n".join(f"{i + 1}. {op}" for i, op in enumerate(ops))
        + f"\n\nWhat is the value of {query_var} after all operations?"
        + "\n\nReturn the final result using exactly:\nANSWER: <value>"
    )
    return Problem(
        task_id=f"symbol_depth{depth:02d}_{index:04d}",
        task_type="symbolic",
        depth=depth,
        prompt=prompt,
        expected=expected,
    )


# ---------------------------------------------------------------------------
# Experiment C — object tracking (box / container swaps)
# ---------------------------------------------------------------------------

_OBJECTS = ("apple", "book", "coin", "key", "pen", "watch", "ring", "stone")
_BOX_NAMES = ("A", "B", "C")


def make_object_tracking(rng: random.Random, depth: int, index: int) -> Problem:
    """Track object positions through a sequence of box-swap operations."""
    n_boxes = 3
    box_names = list(_BOX_NAMES[:n_boxes])
    objects = list(rng.sample(_OBJECTS, n_boxes))
    state: dict[str, str] = {f"Box {b}": o for b, o in zip(box_names, objects)}

    init_lines = ["There are three boxes:"] + [f"{k}: {v}" for k, v in state.items()]
    ops: list[str] = []

    for _ in range(depth):
        a, b = rng.sample(box_names, 2)
        ka, kb = f"Box {a}", f"Box {b}"
        state[ka], state[kb] = state[kb], state[ka]
        ops.append(f"Swap the contents of Box {a} and Box {b}.")

    query_box = f"Box {rng.choice(box_names)}"
    expected = state[query_box]

    prompt = (
        "\n".join(init_lines)
        + "\n\nPerform the following swaps:\n"
        + "\n".join(f"{i + 1}. {op}" for i, op in enumerate(ops))
        + f"\n\nWhat is now inside {query_box}?"
        + "\n\nReturn the final result using exactly:\nANSWER: <object>"
    )
    return Problem(
        task_id=f"obj_depth{depth:02d}_{index:04d}",
        task_type="object_tracking",
        depth=depth,
        prompt=prompt,
        expected=expected,
    )


# ---------------------------------------------------------------------------
# Experiment D — logical implication chains
# ---------------------------------------------------------------------------

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def make_logical_chain(rng: random.Random, depth: int, index: int) -> Problem:
    """Linear implication chain A → B → C → … Query: is the last node true?

    The answer is always 'yes' for a pure chain; distractors will be added
    in a later phase.  Depth equals the number of implication steps.
    """
    # We need depth+1 distinct node names
    if depth + 1 > len(_LETTERS):
        raise ValueError(f"depth {depth} exceeds available node labels")

    nodes = list(_LETTERS[: depth + 1])
    rng.shuffle(nodes)  # randomise label order so position isn't a cue

    chain = list(zip(nodes, nodes[1:]))  # [(A,B), (B,C), ...]
    rng.shuffle(chain)  # present rules in random order

    rule_lines = [f"If {a} is true, then {b} is true." for a, b in chain]
    start = nodes[0]
    end = nodes[-1]

    prompt = (
        "\n".join(rule_lines)
        + f"\n\n{start} is true."
        + f"\n\nIs {end} true?"
        + "\n\nReturn the final result using exactly:\nANSWER: yes or no"
    )
    return Problem(
        task_id=f"logic_depth{depth:02d}_{index:04d}",
        task_type="logical",
        depth=depth,
        prompt=prompt,
        expected="yes",
    )
