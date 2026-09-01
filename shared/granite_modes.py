"""Granite 4.2 thinking-mode helpers.

Granite 4.2 supports three inference modes controlled via a system prompt
or model-specific tokens.  This module wraps the three modes so every
experiment script can select a mode by name without duplicating the logic.

Modes
-----
non_thinking   No explicit chain-of-thought.  Fastest, lowest token cost.
low_thinking   Budget-constrained thinking (low_effort=True equivalent).
full_thinking  Unrestricted chain-of-thought before the final answer.

Usage
-----
    from shared.granite_modes import MODES, generate

    raw_output, n_tokens, latency = generate(
        model, tokenizer, prompt, mode="full_thinking", max_new_tokens=512
    )
"""

from __future__ import annotations

import time
from typing import Literal

ThinkingMode = Literal["non_thinking", "low_thinking", "full_thinking"]

MODES: tuple[ThinkingMode, ...] = ("non_thinking", "low_thinking", "full_thinking")

# System prompts that activate each Granite 4.2 reasoning mode.
# Adjust these if IBM changes the official prompt format.
_SYSTEM_PROMPTS: dict[ThinkingMode, str] = {
    "non_thinking": "You are a helpful assistant.",
    "low_thinking": (
        "You are a helpful assistant. "
        "Think briefly before answering, but keep your reasoning concise."
    ),
    "full_thinking": (
        "You are a helpful assistant. "
        "Think step by step, showing all intermediate work before giving your final answer."
    ),
}

_MAX_NEW_TOKENS_DEFAULT: dict[ThinkingMode, int] = {
    "non_thinking": 64,
    "low_thinking": 256,
    "full_thinking": 1024,
}


def build_messages(prompt: str, mode: ThinkingMode) -> list[dict[str, str]]:
    """Return a chat-template message list for the given mode."""
    return [
        {"role": "system", "content": _SYSTEM_PROMPTS[mode]},
        {"role": "user", "content": prompt},
    ]


def generate(
    model,
    tokenizer,
    prompt: str,
    mode: ThinkingMode,
    max_new_tokens: int | None = None,
) -> tuple[str, int, float]:
    """Run greedy inference under the specified Granite 4.2 thinking mode.

    Returns
    -------
    (decoded_text, n_generated_tokens, latency_seconds)
    """
    if max_new_tokens is None:
        max_new_tokens = _MAX_NEW_TOKENS_DEFAULT[mode]

    messages = build_messages(prompt, mode)
    rendered = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(rendered, return_tensors="pt").to(model.device)

    t0 = time.perf_counter()
    output = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
    )
    latency_s = time.perf_counter() - t0

    generated_ids = output[0, inputs["input_ids"].shape[1]:]
    decoded = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return decoded, len(generated_ids), latency_s
