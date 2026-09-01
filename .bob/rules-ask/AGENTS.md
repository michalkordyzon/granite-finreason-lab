# Project Documentation Context (Non-Obvious Only)

- There is no test suite, CI, linter, or formatter configured — questions about `pytest`, `ruff`, `black`, etc. don't apply to this project.
- `results/` contains only a `.gitkeep`; actual JSONL output files are gitignored. Reference `results/exp_a_<timestamp>.jsonl` when explaining output paths.
- The two prompting conditions (`direct` vs `reasoning`) share **identical generated tasks** (same RNG seed) — the comparison is fair by construction, not by post-hoc filtering.
- Answer extraction has a two-tier fallback: `FINAL: <integer>` marker first, then last integer in the full output. The `valid` field in JSONL records whether any integer was found; `correct` checks exact match.
