# Experiment B — Symbolic Variable Swaps

## Purpose

Determine whether accuracy on **pure symbolic state tracking** — with zero arithmetic — degrades with depth in the same way as sequential arithmetic (Experiment A).

## Task

Three variables (A, B, C) are each assigned a distinct colour.  After *depth* swap operations the model must report the current value of one variable.

## Independent variable

**Depth** — number of swap operations (2 → 4 → 8 → 12 → 16 → 24 → 32).

## Controlled factors

- Same generated problems across all three Granite 4.2 thinking modes.
- No arithmetic involved — failures indicate symbolic state loss only.
- Deterministic decoding (`do_sample=False`).
- Fixed seed.

## Measurements

- Exact-answer accuracy per depth per thinking mode.
- Generated-token count (cost of thinking).
- Latency.

## Run

```bash
python experiments/02_symbol_swaps/run.py \
  --model <granite-4.2-model-id> \
  --depths 2 4 8 12 16 24 32 \
  --samples-per-depth 100
```
