# Project Architecture Rules (Non-Obvious Only)

- The repo is intentionally flat: no packages, no shared library — each experiment is a self-contained `run.py` script. Do not introduce shared modules unless multiple experiments genuinely need them.
- JSONL schema is the integration contract between experiments and any analysis scripts. Fields: `task_id`, `depth`, `question`, `answer`, `model`, `seed`, `condition`, `prompt`, `raw_output`, `predicted_answer`, `valid`, `correct`, `generated_tokens`, `latency_s`.
- Experiments are numbered and slugged (`01_sequential_arithmetic`, `02_...`) — numbering is intentional for ordering in analysis; don't rename existing directories.
- Token budget asymmetry (`direct=32`, `reasoning=256`) is a design choice, not a default — document any change to these defaults in the experiment's own README.
- Results are write-once JSONL (no updates, no deletes) — any re-run appends a new timestamped file; analysis must handle multiple files per experiment.
