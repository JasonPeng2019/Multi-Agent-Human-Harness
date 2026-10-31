---
name: api-design
description: Design or review a public API, CLI, configuration schema, event/message format, protocol, library surface, or integration boundary before implementation. Use when callers or compatibility matter; not for ordinary private helpers.
---

# Design a public contract

Define observable behavior before code:

- callers and ownership boundary;
- inputs, units, validation, defaults, and examples;
- outputs, errors, exit/status behavior, and recovery;
- compatibility and migration requirements;
- idempotency, concurrency, retries, ordering, and timeouts where relevant;
- stable identifiers and persistence rules where relevant;
- security/trust boundary and sensitive-data handling where relevant;
- deliberate non-goals.

Inspect existing repository contracts and conventions first. Prefer the smallest
surface that supports current requirements. Reuse standard types and protocols
when they fit; do not invent versioning, extension points, or configuration knobs
without a concrete consumer.

Call out irreversible or expensive choices explicitly. Include at least one normal
example and the important failure/recovery path. End with acceptance criteria a
caller can observe without knowing the implementation.
