# granite-finreason-lab

How far can Granite 4.2 3B reliably reason? This repo will be gradually adding expriments to test model's boundaries.

It will be about: the boundary between genuine multi-step reasoning and reasoning that becomes unreliable as complexity increases.

Detailed question: how does Granite 4.2 3B accuracy change as the number of required reasoning operations increases?

---

## Project structure

```
granite-finreason-lab/
│
├── shared/                          # Utilities shared across experiments
│   ├── generators.py                # Synthetic problem generators (A–D)
│   ├── evaluate.py                  # Answer extraction and scoring
│   └── granite_modes.py             # Granite 4.2 thinking-mode helpers
│
├── experiments/
│   ├── 01_sequential_arithmetic/    # Experiment A — integer operation chains
│   ├── 02_symbol_swaps/             # Experiment B — symbolic variable swaps
│   ├── 03_object_tracking/          # Experiment C — object/box swap tracking
│   └── 04_logical_chains/           # Experiment D — linear implication chains
│
├── results/                         # JSONL output files (gitignored)
│   └── .gitkeep
│
├── AGENTS.md                        # Project coding rules for agents
└── requirements.txt
```

---

## Experiment map

| ID | Script | What it isolates | Depths | Samples/depth |
|----|--------|-----------------|--------|---------------|
| A | `experiments/01_sequential_arithmetic/run.py` | Sequential numerical state | 2–32 | 100 |
| B | `experiments/02_symbol_swaps/run.py` | Symbolic state (no arithmetic) | 2–32 | 100 |
| C | `experiments/03_object_tracking/run.py` | Working-memory / object locations | 2–32 | 100 |
| D | `experiments/04_logical_chains/run.py` | Inference depth (modus ponens) | 2–24 | 100 |

All four tasks use the **same depth variable** so failure curves can be compared across task families.

### Planned second-phase experiments

| Experiment | What it adds |
|-----------|-------------|
| Long-context control | Pad short prompts to match long-prompt token counts — isolates depth vs context length |
| Distractor condition | Add irrelevant rules/operations — separates reasoning depth from selective attention |
| Representation control | Natural-language vs symbolic notation for the same operations |
| Model comparison | Run the same suite on Granite 4.2 3B / 8B / 30B |

---

## Granite 4.2 thinking modes

Every experiment runs the same fixed problem set under all three modes:

| Mode | System prompt behaviour |
|------|------------------------|
| `non_thinking` | No explicit chain-of-thought |
| `low_thinking` | Brief reasoning, constrained token budget |
| `full_thinking` | Full step-by-step chain before the answer |

This lets you quantify **accuracy gained per additional reasoning token** rather than simply saying "thinking mode is better."

---

## Running an experiment

Always run from the **repository root**:

```bash
python experiments/01_sequential_arithmetic/run.py \
  --model ibm-granite/granite-4.2-3b-instruct \
  --depths 2 4 8 12 16 24 32 \
  --samples-per-depth 100

python experiments/02_symbol_swaps/run.py \
  --model ibm-granite/granite-4.2-3b-instruct \
  --depths 2 4 8 12 16 24 32 \
  --samples-per-depth 100

python experiments/03_object_tracking/run.py \
  --model ibm-granite/granite-4.2-3b-instruct \
  --depths 2 4 8 12 16 24 32 \
  --samples-per-depth 100

python experiments/04_logical_chains/run.py \
  --model ibm-granite/granite-4.2-3b-instruct \
  --depths 2 4 8 12 16 24 \
  --samples-per-depth 100
```

Results are written to `results/exp_<letter>_<UTC-timestamp>.jsonl`, one JSONL record per inference call.

### Common flags

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | (required) | Hugging Face model identifier |
| `--depths` | varies | Space-separated list of depths |
| `--samples-per-depth` | 100 | Number of unique problems per depth |
| `--seed` | 42 | RNG seed — same seed → same problems |
| `--modes` | all three | Subset of thinking modes to run |
| `--output` | auto | Override output path |

---

## Output record schema

Every JSONL line follows this schema (additional fields in Experiment A):

```json
{
  "task_id": "arith_depth08_0042",
  "task_type": "arithmetic",
  "depth": 8,
  "prompt": "...",
  "expected": 73,
  "model": "ibm-granite/granite-4.2-3b-instruct",
  "seed": 42,
  "thinking_mode": "full_thinking",
  "raw_output": "...",
  "predicted": 73,
  "correct": true,
  "generated_tokens": 412,
  "latency_s": 1.832
}
```

---

## Central hypotheses

**H₁:** Granite 4.2 3B will maintain near-ceiling accuracy for short reasoning chains, followed by a nonlinear deterioration beyond a task-dependent depth.

**H₂:** Full-thinking mode will move this transition to greater depth, but will not eliminate it.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


<img width="750" height="750" alt="image" src="https://github.com/user-attachments/assets/9bf8bd56-b764-4ea0-8636-9f59f30fdb13" />

