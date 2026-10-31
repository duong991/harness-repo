---
name: teach
description: Teach the user a skill, concept, or repository module over multiple sessions in an explicitly approved teaching workspace. Use only when the user invokes $teach or explicitly asks for a teaching flow; use implementation-walkthrough for a one-off large implementation explanation.
---

# Teach

Teach for durable understanding, not merely for one correct answer. This is an
explicit-only productivity skill. It owns the pedagogical sequence and the
learning-workspace records; it does not own routing, repository workflow,
product authority, implementation, review, or completion proof.

## Safety and scope

- Do not write teaching artifacts into a repository root. If the user has not
  named an approved teaching workspace, ask for a separate workspace path
  before creating `MISSION.md`, `RESOURCES.md`, `NOTES.md`, or any teaching
  directory.
- A teaching workspace may be a dedicated subdirectory or an external
  directory, but it must be explicit when it lives inside a repository. Keep
  teaching artifacts separate from product, architecture, decision, plan, and
  code authority.
- Do not modify product code, tests, CI, dependencies, Harness state, or Git
  state as part of teaching. Opening a lesson is optional; provide a file link
  rather than executing an OS-specific open command unless the user asks.
- The teaching workspace is not repository authority. If a lesson reveals a
  product or architecture decision, report it and return control to the normal
  repository workflow.
- Do not create a new work type, parallel router, plan system, review system,
  or orchestration lifecycle. For a large completed implementation, hand off to
  `implementation-walkthrough`.

## Teaching workspace

All paths below are relative to the explicitly approved teaching workspace:

- `MISSION.md`: why the user wants to learn and what observable success means.
  Use [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `RESOURCES.md`: curated, annotated high-trust sources. Use
  [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `GLOSSARY.md`: canonical terms the learner has demonstrated they understand.
  Use [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `lessons/*.html`: short, self-contained lessons. Name them
  `0001-<dash-case-name>.html`, incrementing the number for each lesson.
- `reference/*.html`: compressed reference documents that remain useful after
  a lesson is finished.
- `learning-records/*.md`: durable records of non-obvious understanding. Name
  them `0001-<dash-case-name>.md` and use
  [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `assets/*`: reusable lesson components such as styles, quiz widgets,
  simulators, or diagram helpers.
- `NOTES.md`: user teaching preferences and temporary teaching notes.

Create directories lazily. Do not create the workspace or any file until its
path and write authority are clear.

## Start with the mission

If `MISSION.md` is missing or vague, first ask why the user wants to learn the
topic. A useful mission describes a concrete real-world outcome, not merely
"understand X". Confirm with the user before changing an existing mission; when
the mission changes, add a learning record describing the shift.

## Knowledge, skills, and wisdom

Before teaching, populate or inspect `RESOURCES.md`. Prefer primary sources,
recognized experts, peer-reviewed work, repository code, tests, and well-
moderated communities. Never present an uncertain claim as established fact.
Annotate lesson claims with links to the relevant source or repository path.

Separate three learning goals:

- **Knowledge**: accurate information required for the next skill.
- **Skills**: flexible performance through retrieval, practice, and feedback.
- **Wisdom**: judgment tested against real-world use or a high-signal community.

## Lessons

Each lesson should:

1. Teach one tightly scoped thing tied to the mission and the learner's current
   zone of proximal development.
2. Give one tangible win and remain short enough to complete quickly.
3. Use a feedback loop: ask the learner to retrieve, predict, classify, trace,
   or perform before revealing the answer.
4. Link to related lessons and reference documents.
5. Recommend the strongest relevant primary source.
6. Invite follow-up questions.

Use desirable difficulty for retention: retrieval practice, spacing across
sessions, and interleaving when practicing related skills. For quizzes, keep
answer choices equally shaped so formatting does not reveal the answer.

Before creating a lesson, inspect `assets/` and reuse existing components.
Create a new reusable component in `assets/` instead of duplicating markup or
styles across lessons. A shared stylesheet is the first component to add when
the workspace has more than one lesson.

## Teaching a repository module

When the topic is a module in a repository, use the repository as the primary
source of truth while keeping the work explanatory:

1. Confirm the module path, the learner's mission, and the desired depth.
2. Map the public boundary, callers, data/state transitions, side effects,
   error paths, and relevant tests.
3. Turn that map into progressive lessons, beginning with the module boundary
   and then tracing one concrete runtime path.
4. Ask the learner to predict the next call, output, state change, or failure
   before showing the source.
5. Record only demonstrated understanding, prior knowledge, corrected
   misconceptions, or mission changes in `learning-records/`; coverage alone is
   not evidence of learning.

Do not invent behavior that the code, tests, or accepted repository documents
do not support. A teaching explanation does not approve the module, identify
formal review findings, or authorize a code change.

## Zone of proximal development

Read existing learning records before choosing the next lesson. Teach the most
relevant next step that is challenging enough to require effort but small
enough to complete. If the learner names a specific concept, teach that
concept while preserving the mission and known prerequisites.
