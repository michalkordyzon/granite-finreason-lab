# Project Coding Rules (Non-Obvious Only)

- Run all scripts from the **repository root**, not from the experiment subdirectory — paths like `Path("results")` resolve relative to cwd.
- JSONL records are written and flushed **one line at a time** (`handle.flush()` after each write) — preserve this pattern so partial runs are recoverable.
- Serialise dataclass records with `dataclasses.asdict()` directly into `json.dumps(..., ensure_ascii=False)` — do not convert manually.
- Compiled module-level regexes (`FINAL_RE`, `INTEGER_RE`) are the sole answer-extraction mechanism; update them if the output format changes, don't add ad-hoc parsing.
- `from __future__ import annotations` must appear at the top of every new module.
- New experiment scripts must accept `--model`, `--seed`, `--output`, `--samples-per-depth`, and `--depths` CLI flags to stay compatible with the shared run convention.
- `do_sample=False` and `device_map="auto"` are non-negotiable for reproducibility — never add temperature or sampling arguments.
