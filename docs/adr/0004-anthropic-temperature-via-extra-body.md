# ADR-0004 — Anthropic's `temperature` rides `extra_body`

## Context

`AnthropicProvider.generate()` originally passed `temperature` directly to
`client.messages.create(temperature=...)`, mirroring the OpenAI provider.
Manually exercising the CLI's `ask` command against the installed
`anthropic` package (1.7.0) raised `TypeError: Messages.create() got an
unexpected keyword argument 'temperature'` — confirmed by inspecting the
installed SDK's actual signature, which no longer exposes `temperature` as
a typed parameter (its generation controls have moved toward an
`output_config` object with an `effort` field instead). This was caught by
manually running the CLI end to end, not by the mocked provider unit
tests — mocking the SDK client verifies groundedrag builds the *call it
intends to make* correctly, not that the real SDK still accepts that call.

## Decision

Pass `temperature` via `extra_body={"temperature": temperature}`, the
SDK's documented escape hatch for body fields not in its typed surface.
Verified against the real API (with an invalid key, to confirm the request
reaches the server and fails on auth rather than on request shape): the
call now returns `AuthenticationError`, not `TypeError`.

## Consequences

- If the Anthropic API stops accepting `temperature` in the request body
  at all (not just in the typed SDK signature), this call will need to
  change again — there is no way to detect that ahead of time other than
  the API's own error message.
- This is a reminder that mocked SDK tests (`tests/test_providers.py`)
  verify groundedrag's request-building logic, not the vendor SDK's current
  contract. A lightweight, opt-in "real API" smoke test (skipped unless an
  API key is present in the environment) would catch this class of drift
  automatically instead of relying on someone noticing during manual use —
  worth adding in a follow-up rather than deferred indefinitely.
