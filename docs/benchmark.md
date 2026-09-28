# Hallucination-rate benchmark

## Run it

```bash
uv sync --extra dev
uv run python scripts/benchmark.py
```

Offline by default — no API key needed. Set `ANTHROPIC_API_KEY` to also
see one live example of what an un-gated pipeline's LLM actually says when
generated from unrelated context.

## What it measures

Judging whether a piece of text is "hallucinated" is inherently fuzzy. The
benchmark measures something narrower and objectively countable instead:
**on a question with no matching documentation, how often does the
pipeline produce an answer anyway, instead of refusing?**

Two pipelines share the same tiny index (a single remote-work policy
chunk) and are asked five questions that policy doesn't cover (home-office
reimbursement, conference expensing, sabbaticals, office pets, contractor
overtime):

- **Naive** — no gate. It has no way to know a question falls outside its
  documentation, so it runs an unfiltered similarity search, gets back the
  closest chunk it has (however unrelated), and generates from it anyway.
- **groundedrag** — the gate checks coverage for the question's topic first.
  With no document mapped to that topic, it refuses before the LLM is
  ever called.

## Results

| Pipeline | Answer rate on out-of-scope questions |
|---|---:|
| Naive (no gate) | 100% |
| groundedrag | 0% |

The naive rate is 100% *by construction* — a pipeline with no concept of
"coverage" has no refusal path at all, so it always attempts an answer.
That is exactly the point: the gap this benchmark makes visible isn't a
subtle accuracy difference, it's a structural one. See
[`tests/test_benchmark.py`](https://github.com/jeffersonwagner/groundedrag/blob/main/tests/test_benchmark.py)
for the automated
check that keeps this table honest, and
[`docs/adr/0005`](adr/0005-hallucination-benchmark-methodology.md) for why
the benchmark is scoped this way instead of trying to score answer quality
with an LLM judge.
