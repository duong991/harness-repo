---
name: test-walkthrough
description: Explain what selected test files actually exercise by tracing setup, actions, assertions, and dependency behavior to production symbols. Use for read-only test comprehension of a test file, changed tests, tests related to a source symbol/module, or a bounded set of PR/commit tests; do not use for test adequacy findings, approval, severity, or formal review, which belong to code-review.
---

# Test Walkthrough

Provide a compact, behavior-first digest of tests so a developer can decide
what to read without opening every test case. This is explanatory work only:
it does not approve the implementation, judge overall adequacy, assign
severity, modify tests, create plans or Harness state, or replace
`code-review`.

## Routing boundary

Use this skill after `work-router` when the user wants to understand tests:

- what a test file checks;
- which production code a test calls;
- what tests in a diff, commit, branch, PR, module, or source symbol protect;
- a concise test digest without reading every test case.

Route these requests to `code-review`, which may create a test digest first:

- whether tests are sufficient, correct, safe, or compliant;
- whether important tests are missing;
- review of unit-test quality;
- whether a change can be approved or released.

Keep the distinction explicit:

- `test-walkthrough`: “Chưa chứng minh.”
- `code-review`: decides whether a gap is a formal finding.
- `verification-before-completion`: proves whether commands actually ran and
  passed.

Typical trigger phrases include “file test này kiểm tra gì”, “giải thích unit
test”, “tôi không muốn đọc hết test”, “tóm tắt các file test”, “test này gọi
code nào”, “các test trong PR đang bảo vệ gì”, and “cho tôi test digest”.

## Target and investigation

Resolve targets in this order, stopping at the narrowest scope that answers
the request:

1. One named test file.
2. Test files in the current diff.
3. Tests related to a named source file or symbol.
4. Tests in a commit, branch, or PR.
5. Tests for one module.
6. The whole repository only when explicitly requested.

Read the relevant production source before or alongside the tests. For each
consequential behavior, inspect the test's:

- arrange/input/state;
- action or method call;
- direct and negative assertions;
- mock, fixture, fake, and dependency behavior;
- production boundary and symbol actually reached.

Do not infer behavior from a filename, `describe()`/`it()` name, imports,
coverage report, snapshot alone, or a passing command. If tests were not run,
say so. If fresh output exists, report it separately from the digest; an exit
code of zero does not establish adequacy.

## Grouping and scoring

Do not list every test case by default. Group cases that prove the same
observable behavior, including equivalent names such as “rejects missing
file” and “rejects absent file”. Split groups only when they differ in output,
state transition, side effect, permission, error policy, or recovery behavior.

The digest may group equivalent cases, but count only consequential,
behavior-mapped test cases when assigning the compact assessment. Exclude
setup, fixture helpers, duplicate parameters that add no behavior, skipped
tests, and tests that cannot be mapped to production behavior.

- **Direct**: calls a meaningful boundary, asserts the observable contract
  directly, covers an important side effect or negative path when relevant,
  and would fail for a realistic implementation error.
- **Partial**: proves one part of the outcome but leaves a consequential
  detail unasserted, such as error type, state, repository call, event, or
  rollback.
- **Superficial**: mainly checks definedness, generic rejection, no throw, mock
  call count, or an unexamined snapshot without proving the relevant contract.

Never turn a missing assertion into a confirmed bug. Describe it under
`Chưa chứng minh`.

## Reading priority

Choose priority from risk and proof gaps, not line count or test count:

- **Rất cao**: permission/security, transaction, concurrency, important state
  transition, persistence, rollback, many Partial/Superficial groups, or a
  mismatch between the test name and its assertions.
- **Cao**: core business rule, file/package validation, API contract, error
  policy, or primary lifecycle behavior.
- **Trung bình**: controller boundary, mapping, adapter, serialization, or
  module wiring.
- **Thấp**: simple DTO, fixture, builder, pure utility, generated
  compatibility test, or low-risk behavior with clear proof.

When many files are supplied, give full blocks to consequential `Rất cao` and
`Cao` files, summarize repetitive helper/fixture/generated files as a group,
and identify the small set of files worth manual reading. Do not produce
hundreds of test-case entries.

For a grouped helper, fixture, or generated set, use the same six labels with a
group target instead of a file target:

```text
## `<group: generated compatibility tests>`

Mục đích:
<Why these files are grouped and what shared behavior they represent.>

Code được gọi:
- `<shared symbol or helper>`

Hành vi được bảo vệ:
- <Shared behavior established by the group.>

Chưa chứng minh:
- <Important behavior not established by the group.>

Bằng chứng:
<n> Direct · <n> Partial · <n> Superficial

Mức ưu tiên đọc:
Thấp | Trung bình | Cao | Rất cao
```

Only group files when they do not add independent consequential behavior; keep
separate blocks for files that differ in contract, side effect, state, risk, or
proof strength.

## Required output

Use one block for each important test file. Keep the first four sections
compact: purpose is one or two sentences, called symbols no more than seven,
protected behavior no more than eight bullets, and unproven gaps no more than
five. Use exactly these labels:

```text
## `<test-file>`

Mục đích:
<Một hoặc hai câu.>

Code được gọi:
- `<Class.method()>`
- `<function()>`

Hành vi được bảo vệ:
- <Behavior directly established by setup, action, and assertions.>

Chưa chứng minh:
- <Important behavior not established by this file.>

Bằng chứng:
<n> Direct · <n> Partial · <n> Superficial

Mức ưu tiên đọc:
Rất cao | Cao | Trung bình | Thấp
```

End with one shared conclusion:

```text
## Kết luận

Các file test đang kiểm tra:
<Scope of code and behavior.>

Khoảng trống quan trọng nhất:
- <Gap 1>
- <Gap 2>

Có cần đọc test thủ công không?
Có | Không | Chỉ cần đọc một phần

Nên đọc:
- <File or group> — <Reason>
```

Do not add Mermaid, a test matrix, formal severity, approval language, a
review report, or a line-by-line `it()` inventory by default. If execution
evidence is available, append a short separate note after the conclusion that
states the command, exit code, and what it did not establish.
