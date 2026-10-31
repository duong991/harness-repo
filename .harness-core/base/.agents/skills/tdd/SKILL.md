---
name: tdd
description: Apply a conditional red-green-refactor loop to business logic, data mapping, state transitions, permissions, API contracts, graph/layout algorithms, and testable regressions. Use after work-router classifies a tiny fix or bounded change with a valuable automated seam, or when the user requests test-first development; do not force TDD onto pure color, spacing, one-off prototype, or visual-only work without a suitable test harness.
---

# Test-Driven Development

Use tests to drive one observable behavior at a time. Read repository
instructions, accepted authority, existing test conventions, and actual test
commands before choosing a seam.

## Decide whether TDD fits

Prefer TDD for business rules, mappers, state machines, permissions, API
contracts, deterministic algorithms, and regression bugs. Skip it for pure
color/spacing changes, disposable prototypes, and visual-only behavior without
a credible automated harness.

Skip TDD ceremony for glue code, simple CRUD, and heavy I/O wiring (database,
message queues, network clients) where test-first requires mock-heavy scaffolding.
Mocks break on refactoring while proving nothing about real behavior. In those
cases, write the direct implementation and verify with fresh executable checks
under `verification-before-completion`. When skipping, state the reason and choose
direct runtime validation.

Test through a public interface or stable observable boundary. Do not ask the
user to choose a seam that repository evidence already establishes. Stop for a
decision only when materially different test boundaries would encode different
contracts.

Read [tests.md](tests.md) for behavioral test examples and
[mocking.md](mocking.md) when a system boundary may need isolation.

## Red

1. Select one behavior and one valuable seam.
2. Write the smallest test that expresses the expected observable result from
   accepted authority.
3. Run the focused test with a fresh command.
4. Confirm it fails for the expected missing or incorrect behavior, not because
   of syntax, setup, fixture, or environment failure.

If the test passes before implementation, improve the assertion or verify that
the behavior already exists. Do not continue with a non-red test.

## Green

1. Implement only enough production code to satisfy the red test.
2. Run the same focused command.
3. Confirm the test passes and no targeted neighboring behavior regressed.
4. Avoid speculative cases, abstractions, or cleanup not required by the test.

## Refactor

Refactor only after green. Improve names, duplication, boundaries, and clarity
without changing behavior. Rerun the focused test after each coherent refactor,
then run the relevant broader suite. Return to red for the next behavior.

## Test quality rules

- Assert behavior users or callers can observe, not private methods, internal
  call counts, or current implementation shape.
- Derive expected values independently from the implementation.
- Mock only true system boundaries; prefer realistic test databases or adapters
  when practical.
- Work in vertical slices: one red test, one minimal implementation, one
  refactor. Do not write a horizontal batch of speculative tests.
- Do not add tautological, snapshot-only, or low-value tests merely to increase
  coverage.
- Keep test names in the repository's domain language.

Record each red, green, refactor, and broader validation command with its exit
code and relevant result. Use `verification-before-completion` before claiming
the behavior or suite passes. Do not create active plans, Harness CLI stories,
or sub-agents from this skill.
