# Detailed engineering decision charter

Use this reference for consequential design work. It is a decision aid, not a
license to expand a local request into a redesign.

## Make the real promise true

- An operation that says it wrote and verified something must do both. Do not turn
  an unknown state into a plausible success result.
- Resolve real ambiguity from the requested outcome, repository evidence, and
  explicit user decisions. Record an assumption only where a future reader needs
  it to understand behavior.
- Prefer a failure with an actionable recovery over a quiet fallback that changes
  meaning.
- Verify the identity, scope, and freshness of a target before a hard-to-reverse
  operation when that evidence is available. If it is not available, report that
  limit rather than pretending to have found a contradiction.

## Generalize only across real variation

Do not hardcode paths, credentials, host names, user names, installed-tool paths,
or machine capacity when the intended environments vary. Prefer this order:

1. detect an authoritative fact;
2. accept deliberate configuration when detection is ambiguous; or
3. report an honest unsupported limitation.

For a product that genuinely encounters many evolving inputs or environments,
prefer discovery plus a stable common interface over an ever-growing case list.
For a bounded internal task, do not invent discovery, persistence, or extension
systems merely because they would be generally elegant.

## Make interfaces usable

For a public API, command, schema, or operational tool, document enough for a
new user to succeed without reading its implementation:

- purpose and correct use case;
- inputs, units, defaults, and one normal example;
- output or success criteria;
- realistic failure modes and recovery; and
- compatibility or migration consequences when callers depend on it.

Private helpers need names, structure, and nearby tests that make their purpose
clear; they do not need public-product documentation.

## Keep one home per responsibility

Place detection, validation, configuration interpretation, and externally visible
policy in a predictable single location. Do not scatter the same rule across
callers. Prefer names and units that remain consistent across a contract.

Do not retain dead branches, commented-out experiments, or speculative settings.
But preserve existing working behavior outside the requested scope: tidiness is
not authority to create unrelated churn.

## Guard mistakes without nannying the user

Start with the actual trust and authority boundary. A trusted caller may still
choose the wrong target, rely on stale state, misunderstand a result, or retry a
failure indefinitely. Catch those credible mistakes when a small check can prove
a mismatch or stop a harmful thrash loop.

Do not add adversarial-input defenses for an attacker the product cannot receive.
Do not block an explicitly authorized, correctly targeted risky operation just
because it is risky. The distinction is:

- **verified contradiction or likely unintended target:** guard and explain it;
- **authorized, correctly targeted risk:** perform it and report what happened;
- **unverified suspicion:** do not assert a mismatch you cannot prove.

Every limit, timeout, cap, and retry bound needs a concrete basis: a protocol,
resource, safety obligation, observed failure mode, or practical recovery need.
Avoid magic thresholds that merely make the system feel safer.

## Resolve tensions deliberately

| Tension | Decision rule |
| --- | --- |
| Simplicity vs. portability | Choose the simplest design that supports intended environments; detection is often cheaper than abstraction. |
| Generality vs. correctness | A novel case never justifies guessing. Verify it or state the uncertainty. |
| Correctness vs. convenience | Correct behavior and honest reporting win, then remove incidental complexity. |
| Safety guard vs. user authority | Prevent verified mistakes; permit intended, correctly targeted risk. |
| Edge case vs. maintenance cost | Handle realistic failure modes and explicit obligations; leave contrived cases out unless the trust boundary or evidence makes them real. |

## Architecture completion questions

Before accepting a consequential design, ask:

1. Does it make the promised behavior true and observable?
2. Does it use the fewest durable concepts that solve the actual case?
3. Are environmental differences detected, configured, or honestly limited?
4. Can a caller understand success, failure, and recovery?
5. Is each new guard justified by a real mistake or boundary?
6. Are assumptions, non-goals, and irreversible choices visible?
7. Can a maintainer find each responsibility in one clear place?
