# Experiment D — Logical Implication Chains

## Purpose

Measure how accuracy on **linear modus-ponens inference** decays with chain length, and whether the decay is due to reasoning depth or prompt length.

## Task

A shuffled set of rules of the form "If X is true, then Y is true." forms a linear chain.  Given that the first node is true, the model must decide whether the last node is also true.  Rules are presented in random order to prevent positional shortcuts.

The correct answer is always **yes** for a pure chain.  Phase 2 (planned) will add distractor rules to separate reasoning depth from selective-attention capacity.

## Independent variable

**Depth** — number of implication steps (2 → 4 → 8 → 12 → 16 → 24).

## Controlled factors

- Same generated problems across all three Granite 4.2 thinking modes.
- No arithmetic; failures indicate inference-depth limits.
- Rules presented in random order to prevent positional shortcuts.
- Deterministic decoding.
- Fixed seed.

## Measurements

- Exact-answer accuracy per depth per thinking mode.
- Generated-token count.
- Latency.

## Run

```bash
python experiments/04_logical_chains/run.py \
  --model <granite-4.2-model-id> \
  --depths 2 4 8 12 16 24 \
  --samples-per-depth 100
```
