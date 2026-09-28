# ADR-0005 — Measure the refusal gap, not answer quality

## Context

"How much does groundedrag reduce hallucination?" is the natural question for
a benchmark to answer, but "hallucination" isn't a binary a script can
check — scoring it well would need either human review or an LLM-as-judge,
both of which introduce their own bias and cost, and neither of which
would be reproducible in CI on every push.

## Decision

`scripts/benchmark.py` measures something narrower and exactly countable:
on a set of questions with **no matching documentation at all**, what
fraction of the time does each pipeline produce an answer instead of
refusing? A pipeline without a gate has no refusal path — it retrieves
whatever is closest in its index, however unrelated, and generates from it
unconditionally, so its answer rate on out-of-scope questions is 100% by
construction. groundedrag's coverage check happens before the LLM is ever
called, so its answer rate on the same questions is 0% whenever the gate
is implemented correctly — `tests/test_benchmark.py` asserts exactly that,
making the number itself a regression check, not just a demo.

## Alternatives considered

**LLM-as-judge scoring of answer quality.** Would produce a more nuanced
number (e.g., a 1-5 faithfulness score) but isn't reproducible run to run,
costs an API call per question per judge, and answers a different
question than the one this project's core claim is actually about — it's
not "how good are the answers," it's "does the system ever answer when it
shouldn't."

**Human-labeled hallucination dataset.** More rigorous, but out of scope
for a benchmark that ships in the repository and runs in under a second
offline; a labeled dataset is a reasonable Phase 5+ addition once there's
a community to help build and maintain one.

## Consequences

- The benchmark is fast, deterministic, and requires no API key by
  default — it can run in CI on every push without cost or flakiness (it
  currently isn't wired into CI as a separate job, only as an ordinary
  test in the suite; a dedicated benchmark job that publishes the numbers
  as a CI artifact is a reasonable Phase 4+ addition).
- It says nothing about answer *quality* on in-scope, documented
  questions — a separate concern from the gate's job, and not what this
  benchmark claims to measure.
- The optional live example (`ANTHROPIC_API_KEY` set) is illustrative, not
  part of the measured rate — it exists to make the abstract "100% vs 0%"
  concrete by showing one real fabricated-sounding answer next to it.

## What would invalidate this

If groundedrag's scope grows to include claims about answer *quality* (e.g.,
"citations reduce factual error rate by X%"), that would need its own
benchmark with its own methodology — this ADR only covers the refusal-gap
claim the project currently makes.
