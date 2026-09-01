# Experiment C — Object Tracking

## Purpose

Test whether the model can maintain an **evolving representation of object locations** as the number of container-swap operations increases.

This task isolates working-memory maintenance from both arithmetic and symbolic reasoning.

## Task

Three named boxes each hold a distinct object.  After *depth* swap operations the model must report the current contents of one box.

## Independent variable

**Depth** — number of swap operations (2 → 4 → 8 → 12 → 16 → 24 → 32).

## Controlled factors

- Same generated problems across all three Granite 4.2 thinking modes.
- No arithmetic; failures indicate state-maintenance failure.
- Deterministic decoding.
- Fixed seed.

## Measurements

- Exact-answer accuracy per depth per thinking mode.
- Generated-token count.
- Latency.

## Run

```bash
python experiments/03_object_tracking/run.py \
  --model <granite-4.2-model-id> \
  --depths 2 4 8 12 16 24 32 \
  --samples-per-depth 100
```
