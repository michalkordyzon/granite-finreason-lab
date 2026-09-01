For **Point 1: Difficulty Scaling**, I would build a controlled experiment whose goal is not merely to ask whether Granite 4.2 3B can solve reasoning problems, but to identify **where reliability starts to collapse as required reasoning depth increases**.

The key idea is simple:

> Keep the underlying skill constant. Increase only the amount of reasoning required.

That gives us something much more useful than a benchmark score.

## 1. Research question

Primary question:

> **How does Granite 4.2 3B accuracy change as the number of required reasoning operations increases?**

Secondary questions:

* Is degradation gradual or sudden?
* Does full-thinking mode move the failure boundary?
* Does the model lose intermediate state, make arithmetic mistakes, misunderstand instructions, or prematurely shortcut?
* Is the limit different for arithmetic, symbolic reasoning and state tracking?
* Does more generated reasoning actually help?

Our independent variable is therefore approximately:

$$
\text{reasoning depth}
$$

And our main dependent variable:

$$
\text{accuracy}
$$

---

# 2. Do not start with GSM8K

For this experiment, I would **not start with GSM8K, MATH or GPQA**.

Those benchmarks mix together too many things:

```text
knowledge
language understanding
reasoning
arithmetic
problem familiarity
training contamination
reasoning depth
```

If Granite fails a MATH problem, we don't know why.

Instead, build **synthetic problems with precisely controlled complexity**.

This follows a long tradition in benchmarks such as BIG-bench, which includes programmatically generated arithmetic, algorithmic, state-tracking and logical tasks specifically suited to controlled evaluation. ([GitHub][1])

---

# 3. Experiment A — sequential arithmetic

This should be our first experiment because it is extremely clean.

Example depth = 2:

```text
Start with 7.

1. Multiply it by 3.
2. Subtract 4.

What is the final value?
```

Answer:

$$
7\times3-4=17
$$

Now depth = 4:

```text
Start with 7.

1. Multiply it by 3.
2. Subtract 4.
3. Double the result.
4. Add 9.

What is the final value?
```

Then:

```text
2 steps
4 steps
8 steps
12 steps
16 steps
24 steps
32 steps
48 steps
64 steps
```

But there is an important experimental detail.

## Keep the arithmetic itself easy

We don't want:

```text
8473 × 1937
```

because then we're testing multiplication ability.

Use operations such as:

```text
+ 3
- 7
× 2
÷ 2
+ 11
```

and constrain generated values to remain, say:

$$
-1000 < x < 1000
$$

Now the individual operation is trivial.

What gets difficult is maintaining the computation through many transformations.

That is much closer to **reasoning depth / state maintenance**.

---

# 4. Generate many problems at every depth

Never test:

```text
one problem at depth 4
one problem at depth 8
one problem at depth 16
```

Random luck would dominate the result.

I'd start with:

**100 unique problems per depth.**

For:

```text
depths = [2, 4, 8, 12, 16, 24, 32]
```

that's:

$$
7\times100=700
$$

problems.

If the test is cheap enough, use **200 per depth**.

This gives us an actual distribution rather than anecdotes.

---

# 5. Generate answers programmatically

The test harness itself calculates the correct answer.

For example:

```python
value = 7

value *= 2
value += 5
value -= 3
value *= 2
```

The generator then produces both:

```json
{
  "prompt": "...",
  "answer": 42,
  "depth": 4
}
```

This is extremely useful because:

* we can generate thousands of unseen problems;
* there is effectively no benchmark memorization;
* labels are exact;
* evaluation is automatic;
* difficulty is controlled.

This is one reason synthetic tasks are so useful in model research.

---

# 6. But arithmetic alone is not enough

Arithmetic depth might expose a weakness in arithmetic rather than general reasoning capacity.

So build several **task families with the same depth variable**.

I would use four.

## A. Arithmetic transformations

Tests:

**sequential numerical state**

Example:

```text
Start with 13.

add 4
double it
subtract 6
halve it
add 3

Final value?
```

---

## B. Symbolic transformations

This removes arithmetic almost entirely.

Example:

```text
Initial state:

A = red
B = blue
C = green

Perform:

swap A and B
swap B and C
swap A and C

What color is B?
```

Depth can be increased indefinitely.

Example:

```text
2 swaps
4 swaps
8 swaps
16 swaps
32 swaps
```

Now the model has to preserve symbolic state.

No arithmetic knowledge is involved.

---

# 7. Experiment C — object tracking

This is especially valuable.

BIG-bench already contains tasks such as **tracking shuffled objects**, algorithms and logical reasoning, so this kind of controlled state tracking has precedent in LLM evaluation. ([GitHub][1])

Example:

```text
There are three boxes:

Box A: apple
Box B: book
Box C: coin

Swap the contents of A and C.
Swap the contents of B and C.
Swap the contents of A and B.

What is now inside Box C?
```

Then increase:

```text
2 swaps
4
8
12
16
24
32
```

This tests something fundamental for reasoning:

> Can the model maintain an evolving internal representation?

A small model may eventually start losing state.

---

# 8. Experiment D — logical implication chains

Example depth 2:

```text
If A, then B.
If B, then C.

A is true.

Is C true?
```

Depth 8:

```text
A → B
B → C
C → D
D → E
E → F
F → G
G → H
H → I

A is true.

Is I true?
```

You can complicate it later with distractors:

```text
X → Y
P → Q
M → N
```

which are irrelevant.

Then we separate:

### reasoning depth

from

### context complexity.

That distinction will become very important.

---

# 9. Depth should initially be the ONLY thing changing

This is perhaps the most important methodological rule.

Suppose depth 4 looks like:

```text
A → B
B → C
C → D
D → E
```

Depth 16 should not suddenly introduce:

* harder vocabulary,
* larger numbers,
* negation,
* longer sentences,
* more variables,
* unfamiliar concepts.

Otherwise we cannot attribute the failure to depth.

Initially:

> **Only N changes.**

That's the experiment's internal validity.

---

# 10. Establish very easy baselines first

Start at:

```text
depth = 1
depth = 2
depth = 4
```

We want Granite essentially at ceiling:

```text
~98–100%
```

If it gets only 80% at depth 2, something is wrong with the task or prompt.

Then scale:

```text
1
2
4
8
12
16
24
32
48
64
```

We don't know in advance where the cliff is.

This exponential-ish progression finds it efficiently.

Once we locate the boundary, zoom in.

Suppose:

```text
8   → 99%
12  → 97%
16  → 91%
24  → 58%
32  → 31%
```

Then run:

```text
16
18
20
22
24
26
```

with many samples.

Now we can estimate the transition properly.

---

# 11. Define the capacity boundary before seeing results

This prevents us from moving the goalposts.

For example, define:

### Reliable

$$
accuracy \geq 95\%
$$

### Degrading

$$
80\% \le accuracy <95\%
$$

### Unreliable

$$
50\% \le accuracy <80\%
$$

### Failure regime

$$
accuracy <50\%
$$

Then define:

> **Reliable reasoning depth = largest N for which accuracy remains ≥95%.**

You could also report:

$$
D_{95}
$$

$$
D_{80}
$$

$$
D_{50}
$$

where:

```text
D95 = maximum depth with ≥95% accuracy
D80 = maximum depth with ≥80% accuracy
D50 = point around 50% accuracy
```

This would give us a nice compact result.

---

# 12. The graph is the central result

We want:

```text
Accuracy
100% ┤●────●────●────●
 90% ┤               ╲
 80% ┤                ●
 70% ┤                  ╲
 60% ┤                   ●
 50% ┤
 40% ┤                       ●
     └────────────────────────────
       2    4    8   16   24   32
              reasoning depth
```

That curve tells us far more than:

> "Granite scored 73.4%."

We can literally see where reasoning becomes unstable.

---

# 13. Test Granite's three reasoning modes separately

This is where the Granite experiment becomes particularly interesting.

Run exactly the same dataset under:

```text
non-thinking
low-thinking
full-thinking
```

Do **not** regenerate questions.

Same input set, same conditions.

Then we may get:

| Depth | No thinking |  Low | Full |
| ----: | ----------: | ---: | ---: |
|     4 |         99% | 100% | 100% |
|     8 |         93% |  98% |  99% |
|    16 |         61% |  82% |  94% |
|    24 |         29% |  54% |  78% |
|    32 |         12% |  28% |  43% |

Those numbers are hypothetical, of course.

But look at what we'd learn.

It would let us quantify:

$$
\text{value of reasoning tokens}
$$

rather than merely saying:

> "thinking mode seems better."

---

# 14. Measure token usage too

For every response record:

```text
input_tokens
output_tokens
reasoning_tokens if exposed
latency
correct/incorrect
```

Then we can study:

$$
\text{accuracy vs reasoning tokens}
$$

and:

$$
\text{accuracy vs latency}
$$

This matters because perhaps full thinking improves:

```text
61% → 94%
```

but requires:

```text
8× more output tokens.
```

Then we can calculate something like:

> accuracy gained per additional inference token.

That makes the analysis relevant not just academically, but operationally.

---

# 15. Temperature should initially be deterministic

First experiment:

```text
temperature = 0
```

or the closest Granite serving stack permits.

Why?

Because first we want:

> deterministic competence.

Not sampling variance.

Later we run a second experiment with repeated sampling.

For initial capacity mapping:

```text
same model
same weights
same prompt
same decoding configuration
```

Everything except reasoning depth remains fixed.

---

# 16. Force an exact final-answer format

Otherwise evaluation becomes messy.

Prompt could end:

```text
Return the final result using exactly:

ANSWER: <value>
```

Then our evaluator extracts:

```regex
ANSWER:\s*(-?\d+)
```

For symbolic tests:

```text
ANSWER: C
```

or:

```text
ANSWER: blue
```

The benchmark scorer should **never ask another LLM whether the answer is correct** when exact matching is possible.

Deterministic evaluation is much better.

---

# 17. Do not evaluate chain-of-thought correctness initially

This is subtle but important.

The primary metric should be:

> **final-answer accuracy.**

Why?

Because written chain-of-thought isn't guaranteed to be a faithful representation of the model's internal computation. Research has repeatedly shown that models can produce plausible-looking reasoning that doesn't causally explain the final prediction. ([Anthropic][2])

So:

```text
Primary:
final answer correctness

Secondary:
reasoning trace characteristics
```

Don't reverse those.

---

# 18. But save the complete reasoning trace

For every test store:

```json
{
  "task_id": "arith_depth16_0042",
  "task_type": "arithmetic",
  "depth": 16,
  "prompt": "...",
  "expected": 73,
  "response": "...",
  "predicted": 73,
  "correct": true,
  "output_tokens": 412,
  "latency_ms": 1832,
  "thinking_mode": "full"
}
```

Why save the trace?

Because later we can classify failure modes.

---

# 19. Failure classification is where the research gets interesting

Suppose the correct sequence is:

```text
7
14
19
38
35
70
```

but Granite produces:

```text
7
14
19
38
31
62
```

We can find:

> First failure occurred at operation 5.

Across hundreds of runs, calculate:

$$
P(\text{failure at step }n)
$$

Then perhaps we'll discover something such as:

```text
steps 1–10 → almost zero errors
11–15      → occasional
16–22      → rapidly increasing
23+        → state increasingly unstable
```

That's much more interesting than final accuracy alone.

---

# 20. Distinguish four types of failure

I'd manually or programmatically classify errors into:

### A. Local operation error

It computes:

$$
17+8=24
$$

instead of 25.

That's arithmetic execution failure.

### B. State loss

Correct current state was:

```text
42
```

but the model suddenly resumes from an older state.

This is closer to a working-memory failure.

### C. Instruction omission

There are 16 operations.

Model performs 15.

This may indicate sequence-tracking limits.

### D. Hallucinated operation

Model introduces something not in the prompt.

Example:

```text
"Now multiply by 2"
```

even though no multiplication was specified.

That's particularly interesting in long reasoning chains.

---

# 21. Introduce distractors only in a second phase

Once we establish pure depth performance, add irrelevant information.

Example:

```text
A → B
B → C

Z → Y
P → Q
K → L

C → D
D → E
```

Question:

```text
If A is true, is E true?
```

Now we have two variables:

$$
\text{reasoning depth}
$$

and:

$$
\text{distractor count}
$$

Possible grid:

| Depth | 0 distractors |  4 |  8 | 16 |
| ----: | ------------: | -: | -: | -: |
|     4 |               |    |    |    |
|     8 |               |    |    |    |
|    16 |               |    |    |    |
|    24 |               |    |    |    |

This begins separating **reasoning capacity** from **attention/filtering capacity**.

---

# 22. Control prompt length separately

Very important.

A 32-step problem naturally has more tokens than a 4-step problem.

Therefore a critic could say:

> Maybe Granite isn't failing because of reasoning depth. Maybe it's failing simply because the prompt is longer.

So create a control condition.

For the 4-step problem, add meaningless but harmless filler until its prompt has approximately the same token count as the 32-step problem.

Compare:

```text
32 real reasoning steps
```

against:

```text
4 reasoning steps
+ equivalent-length irrelevant context
```

If:

```text
4-step + long context → 98%
32-step → 48%
```

then prompt length alone cannot explain the collapse.

This is a **very strong experimental control**.

---

# 23. Another control: compress the representation

Compare:

### Natural language

```text
Add four.
Multiply by two.
Subtract seven.
```

with:

### symbolic

```text
+4
×2
-7
```

Same computation.

If symbolic representation performs dramatically better, then part of the limit may come from language processing overhead.

That itself is a useful finding:

> effective reasoning capacity depends on representation efficiency.

---

# 24. Another excellent test: reverse dependency

Instead of:

```text
start → operation → operation → answer
```

we can ask the model to infer the start.

Example:

```text
A number was doubled.
Then 5 was added.
The final value was 19.

What was the initial number?
```

Then scale the transformation chain.

That tests whether Granite's performance is specific to straightforward forward execution.

---

# 25. We should also compare models

Without controls, saying:

> Granite breaks at depth 20

doesn't tell us much.

I'd run exactly the same test against perhaps:

```text
Granite 4.2 3B
Granite 4.2 8B
Granite 4.2 30B
```

If infrastructure permits.

This produces the really interesting curve:

```text
accuracy
100 |                  30B ────────────
    |             8B ──────────────╲
 80 |        3B ──────────╲          ╲
    |                       ╲
 60 |                        ╲
    |
 40 |
    └─────────────────────────────────
       reasoning depth →
```

Now we're directly studying:

$$
\text{model capacity} \rightarrow \text{reasoning depth}
$$

That is much closer to the original research question.

---

# 26. Our first minimal experiment

I would **not build all of this immediately**.

Start extremely cleanly.

### Task

Sequential integer transformations.

### Depths

```text
2
4
8
12
16
24
32
```

### Samples

```text
100 per depth
```

### Modes

```text
non-thinking
low-thinking
full-thinking
```

### Total generations

$$
7\times100\times3
=
2100
$$

### Primary metric

```text
exact answer accuracy
```

### Secondary metrics

```text
output tokens
latency
first-error position
```

### Controls

```text
temperature = 0
same prompt template
same operation distribution
same numeric range
same dataset across modes
```

This would already be a respectable experiment.

---

# 27. Then expand into the real study

If Experiment 1 produces an interesting failure curve, expand to:

| Experiment                 | What it isolates            |
| -------------------------- | --------------------------- |
| Arithmetic transformations | sequential computation      |
| Symbol swaps               | symbolic state              |
| Object tracking            | working state               |
| Logical chains             | inference depth             |
| Long-context control       | depth vs context length     |
| Distractor condition       | selective attention         |
| Representation control     | NL vs symbolic              |
| Thinking modes             | test-time reasoning benefit |
| 3B vs 8B vs 30B            | parameter/capacity effect   |

At that point we aren't merely "testing Granite."

We have a coherent research design around:

> **Scaling limits of reasoning depth in small language models.**

That is a much stronger framing.

One especially important observation from BIG-bench is that **composite tasks requiring several discrete operations often show nonlinear or breakthrough-like behavior rather than smooth scaling**. ([GitHub][3]) That means we should explicitly look for a **cliff**, not assume performance will simply decline linearly.

### The first hypothesis I'd write down

Before running anything:

$$
H_1:
$$

> Granite 4.2 3B will maintain near-ceiling accuracy for short reasoning chains, followed by a nonlinear deterioration beyond a task-dependent depth.

And:

$$
H_2:
$$

> Full-thinking mode will move this transition to greater depth, but will not eliminate it.

Those two hypotheses alone give us a very clean first Granite experiment.

[1]: https://github.com/google/BIG-bench/blob/main/bigbench/benchmark_tasks/keywords_to_tasks.md?utm_source=chatgpt.com "BIG-bench/bigbench/benchmark_tasks/keywords_to_tasks.md at main · google/BIG-bench · GitHub"
[2]: https://www.anthropic.com/research/measuring-faithfulness-in-chain-of-thought-reasoning?utm_source=chatgpt.com "Measuring Faithfulness in Chain-of-Thought Reasoning \ Anthropic"
[3]: https://github.com/google/BIG-bench/blob/main/docs/paper/BIG-bench.tex?utm_source=chatgpt.com "BIG-bench/docs/paper/BIG-bench.tex at main · google/BIG-bench · GitHub"
