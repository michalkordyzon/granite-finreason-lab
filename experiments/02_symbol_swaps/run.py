"""Experiment B — symbolic variable swaps.

Research question
-----------------
Does accuracy on pure symbolic state tracking (no arithmetic) degrade
with depth in the same way as sequential arithmetic?

Independent variable
--------------------
Depth = number of variable-swap operations.

Task
----
Three variables (A, B, C) each assigned a distinct colour.  After
*depth* swap operations the model must report the value of one variable.

No arithmetic is involved.  Failures here indicate symbolic state loss
rather than numerical execution errors.

Thinking modes
--------------
Runs all three Granite 4.2 modes (non_thinking / low_thinking / full_thinking)
against the same fixed problem set so the token cost of thinking can be
weighed against any accuracy gain.

Run from the repository root:

    python experiments/02_symbol_swaps/run.py \\
        --model <hf-model-id> \\
        --depths 2 4 8 12 16 24 32 \\
        --samples-per-depth 100
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from the repo root regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.evaluate import extract_answer, is_correct
from shared.generators import make_symbolic
from shared.granite_modes import MODES, generate

from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experiment B — symbolic variable swaps"
    )
    parser.add_argument("--model", required=True, help="Hugging Face model identifier")
    parser.add_argument(
        "--depths", nargs="+", type=int, default=[2, 4, 8, 12, 16, 24, 32]
    )
    parser.add_argument("--samples-per-depth", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=MODES,
        default=list(MODES),
        help="Thinking modes to run (default: all three)",
    )
    parser.add_argument(
        "--max-new-tokens", type=int, default=None,
        help="Override token budget for all modes"
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    problems = [
        make_symbolic(rng, depth, idx)
        for depth in args.depths
        for idx in range(args.samples_per_depth)
    ]

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, device_map="auto", torch_dtype="auto"
    )
    model.eval()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output or Path("results") / f"exp_b_{timestamp}.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(problems) * len(args.modes)
    written = 0

    with output_path.open("w", encoding="utf-8") as fh:
        for problem in problems:
            for mode in args.modes:
                raw_output, n_tokens, latency_s = generate(
                    model, tokenizer, problem.prompt, mode,
                    max_new_tokens=args.max_new_tokens,
                )
                predicted = extract_answer(raw_output, task_type=problem.task_type)
                correct = is_correct(predicted, problem.expected, problem.task_type)
                record = {
                    **asdict(problem),
                    "model": args.model,
                    "seed": args.seed,
                    "thinking_mode": mode,
                    "raw_output": raw_output,
                    "predicted": predicted,
                    "correct": correct,
                    "generated_tokens": n_tokens,
                    "latency_s": latency_s,
                }
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                fh.flush()
                written += 1
                print(
                    f"[{written}/{total}] {problem.task_id} mode={mode}"
                    f" pred={predicted!r} correct={correct}"
                )

    print(f"\nSaved {written} records → {output_path}")


if __name__ == "__main__":
    main()
