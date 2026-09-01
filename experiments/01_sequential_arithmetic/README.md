# Experiment A — Sequential arithmetic

## Purpose

Test whether asking the model to reason explicitly improves exact arithmetic accuracy as the number of dependent operations grows.

## Independent variables

- **Chain depth:** number of sequential operations, for example 2, 4, 6, or 8.
- **Prompt condition:**
  - `direct` — return only the final number.
  - `reasoning` — work through the operations, then return a marked final number.

## Controlled factors

- Same generated tasks in both conditions.
- Integer addition, subtraction, and multiplication only.
- Deterministic decoding.
- Fixed seed.
- Identical model and maximum output budget.

## Measurements

- Exact-answer accuracy.
- Valid-answer rate.
- Latency.
- Generated-token count.
- Accuracy degradation as chain depth increases.

## First analysis

For each chain depth, compare `direct` and `reasoning` accuracy. Thinking helps when its accuracy advantage is positive and reproducible; it becomes counterproductive when it adds tokens or latency without improving accuracy.

Run from the repository root:

```bash
python experiments/01_sequential_arithmetic/run.py \
  --model <granite-4.2-model-id> \
  --samples-per-depth 50 \
  --depths 2 4 6 8
```

