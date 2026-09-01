"""Run Experiment A: sequential arithmetic under two prompting conditions."""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer


FINAL_RE = re.compile(r"FINAL:\s*(-?\d+)", re.IGNORECASE)
INTEGER_RE = re.compile(r"-?\d+")


@dataclass(frozen=True)
class Task:
    task_id: str
    depth: int
    question: str
    answer: int


def build_task(rng: random.Random, depth: int, index: int) -> Task:
    """Create a bounded integer task with genuinely dependent operations."""
    value = rng.randint(10, 99)
    steps: list[str] = [f"Start with {value}."]

    for _ in range(depth):
        operation = rng.choice(("add", "subtract", "multiply"))
        operand = rng.randint(2, 12) if operation != "multiply" else rng.randint(2, 4)
        if operation == "add":
            value += operand
            steps.append(f"Add {operand}.")
        elif operation == "subtract":
            value -= operand
            steps.append(f"Subtract {operand}.")
        else:
            value *= operand
            steps.append(f"Multiply the current result by {operand}.")

    steps.append("What is the final value?")
    return Task(
        task_id=f"d{depth:02d}-n{index:04d}",
        depth=depth,
        question=" ".join(steps),
        answer=value,
    )


def prompt_for(task: Task, condition: str) -> str:
    if condition == "direct":
        instruction = "Return only the final integer in the form FINAL: <integer>."
    else:
        instruction = (
            "Work through every operation in order. End with the final integer "
            "in the form FINAL: <integer>."
        )
    return f"{instruction}\n\nProblem: {task.question}"


def extract_answer(text: str) -> int | None:
    marked = FINAL_RE.findall(text)
    if marked:
        return int(marked[-1])
    integers = INTEGER_RE.findall(text)
    return int(integers[-1]) if integers else None


def generate(model, tokenizer, prompt: str, max_new_tokens: int) -> tuple[str, int, float]:
    messages = [{"role": "user", "content": prompt}]
    rendered = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(rendered, return_tensors="pt").to(model.device)

    started = time.perf_counter()
    output = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
    )
    latency_s = time.perf_counter() - started
    generated = output[0, inputs["input_ids"].shape[1] :]
    return tokenizer.decode(generated, skip_special_tokens=True), len(generated), latency_s


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Hugging Face model identifier")
    parser.add_argument("--depths", nargs="+", type=int, default=[2, 4, 6, 8])
    parser.add_argument("--samples-per-depth", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-new-tokens-direct", type=int, default=32)
    parser.add_argument("--max-new-tokens-reasoning", type=int, default=256)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    tasks = [
        build_task(rng, depth, index)
        for depth in args.depths
        for index in range(args.samples_per_depth)
    ]

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, device_map="auto", torch_dtype="auto"
    )
    model.eval()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output or Path("results") / f"exp_a_{timestamp}.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for task in tasks:
            for condition in ("direct", "reasoning"):
                prompt = prompt_for(task, condition)
                token_budget = (
                    args.max_new_tokens_direct
                    if condition == "direct"
                    else args.max_new_tokens_reasoning
                )
                raw_output, generated_tokens, latency_s = generate(
                    model, tokenizer, prompt, token_budget
                )
                predicted = extract_answer(raw_output)
                record = {
                    **asdict(task),
                    "model": args.model,
                    "seed": args.seed,
                    "condition": condition,
                    "prompt": prompt,
                    "raw_output": raw_output,
                    "predicted_answer": predicted,
                    "valid": predicted is not None,
                    "correct": predicted == task.answer,
                    "generated_tokens": generated_tokens,
                    "latency_s": latency_s,
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                print(
                    f"{task.task_id} {condition:9s} "
                    f"pred={predicted!s:>8s} correct={record['correct']}"
                )

    print(f"Saved {len(tasks) * 2} records to {output_path}")


if __name__ == "__main__":
    main()

