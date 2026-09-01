# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

Pure Python research repo. No build system, no test framework, no linter config. Dependencies: `torch`, `transformers`, `accelerate` — installed via `pip install -r requirements.txt` into a `.venv`.

## Shared modules

Reusable code lives in `shared/` at the repository root:

- `shared/generators.py` — synthetic problem generators for all four task families.
- `shared/evaluate.py` — answer extraction (`ANSWER: <value>` marker + integer fallback) and scoring.
- `shared/granite_modes.py` — Granite 4.2 thinking-mode helpers (`non_thinking`, `low_thinking`, `full_thinking`).

Each experiment adds `sys.path.insert(0, ...)` to make these importable when running from the repo root.

## Running experiments

All scripts are run **from the repository root** (not from the experiment directory):

```bash
python experiments/01_sequential_arithmetic/run.py \
  --model <hf-model-id> \
  --samples-per-depth 100 \
  --depths 2 4 8 12 16 24 32

python experiments/02_symbol_swaps/run.py --model <hf-model-id>
python experiments/03_object_tracking/run.py --model <hf-model-id>
python experiments/04_logical_chains/run.py --model <hf-model-id>
```

There are no test, lint, or build commands — this is a scripts-only research project.

## Output convention

- Results write to `results/` as JSONL, one record per line, flushed after each sample.
- Output filename defaults to `results/exp_<letter>_<UTC-timestamp>.jsonl`.
- `results/*.jsonl` is gitignored; `results/.gitkeep` preserves the directory.
- Use `--output <path>` to override the output path.

## Code patterns

- `from __future__ import annotations` is used in all modules (enables PEP 604 `X | Y` type hints on Python <3.10).
- `dataclasses.dataclass(frozen=True)` is the canonical record type; serialised with `dataclasses.asdict()` directly into `json.dumps`.
- Answer extraction: `FINAL_RE` (primary) → `INTEGER_RE` fallback on last integer in output. Both are module-level compiled regexes.
- Model inference uses `do_sample=False` (greedy) and `device_map="auto"` — deterministic by design.
- Token budgets differ by condition: `--max-new-tokens-direct` (default 32) vs `--max-new-tokens-reasoning` (default 256).

## Experimental rules (enforced by convention, not code)

- `temperature=0` / deterministic decoding only.
- Change one variable at a time per experiment.
- Raw outputs must be preserved in JSONL (never aggregate-only).
- Tasks are generated from a fixed seed (`--seed`, default 42); same tasks across both conditions per run.

## Adding new experiments

New experiments live in `experiments/<NN>_<slug>/run.py`. Follow the same CLI pattern (`--model`, `--seed`, `--output`, `--samples-per-depth`, `--depths`) and JSONL record schema to keep results comparable.
