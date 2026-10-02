---
name: write-sop
description: >
  Write or revise a working procedure — an SOP, checklist or handover note —
  for a named kind of person doing a named task, from rules and material the
  user is allowed to use. Keeps where each rule comes from, the key checks,
  the exceptions and the open questions; never invents or changes a business
  rule. Can show the current way and a proposed way side by side, with the
  proposed one marked as not yet adopted. Invoke explicitly, e.g. "write an
  SOP for…", "turn this into a checklist", "把这个做法写成 SOP", "SOP 写多细才有用".
disable-model-invocation: true
---

# Write a working procedure

A procedure is done when the person it is for can follow it and get the task
right, including the exceptions — not when it looks complete.

## How to talk

Reply in the user's language, in plain words, starting with what you can do
now with what they gave you. Keep method names out of the reply.

## 1. Who and what

Settle, from what the user said (ask only what is missing):
- **Who follows it**: new starter, occasional user, or experienced — and how often they do the task.
- **The task**: where it starts, what "done" means, what comes in and what goes out, and to whom.

## 2. Collect the rules — with their source

Use only material the user gives or points to: a policy, an old SOP, chat or
email threads, their walkthrough of the last real case.
- Every step, limit, deadline and approver keeps its source next to it in your
  notes (document and section, or "the user said").
- **What the material does not say stays an open question.** Never fill it
  with common sense: no invented approver, amount, deadline, order of steps or
  system name.
- Where two sources disagree, show both and ask which one applies.

## 3. Decide how much detail each step needs

Detail follows the user, the task and what happens if it goes wrong:
- **Serious or hard to catch later** → the exact step, the check, one line on
  why, and what to do or whom to tell if it goes wrong. Where you can, make the
  error impossible or obvious (a required field, a system block) rather than
  adding a warning.
- **Routine and easy to spot** → one line.
- **Things the person already does right without help** → leave out.
- Every step or check you add says what it guards. Do not add checks without a
  reason — a long procedure is a procedure nobody reads.
- A procedure cannot stop slips of attention. If the risk is a slip, say that
  the work or the system should change, and keep the step short.

## 4. Write it

- One page where possible. Each step starts with a verb; one action per step.
- Decisions as "if … then …". Exceptions in their own short section.
- Every handoff says to whom, how (system, file, message) and what counts as done.
- Mark the key checks.
- End with: open questions, owner, version and date, and how to report a problem with the procedure.

## 5. Current way vs proposed way

When the user wants a before/after:
- **Current way** — as the work is actually done today (from the walkthrough
  and records), not the policy ideal. Where they differ, note it.
- **Proposed way** — clearly labelled as a trial, not yet adopted. List what
  changes, which check each change touches and what replaces it, and how the
  trial will be judged. Never present the proposed way as in effect.

## 6. Test before calling it done

Suggest this test: someone qualified who does not know the task by heart
follows it on the normal path and on one exception, while you or the owner
watch. Note where they hesitate, guess or ask, and fix those lines. Someone
reading it and saying "clear" is not a test.

## 7. What to hand over

The procedure in the user's language, then a short list: sources used, open
questions, and the test to run. If the user keeps a `problem-notes/` folder,
save it as `problem-notes/sop/<task>-current.md` or `-proposed.md`.

## Never

- Invent or change a rule, limit, approver or deadline.
- Drop a check without naming what it guards and what replaces it.
- Name or blame people; use roles.
- Present a proposed procedure as adopted.

## Sources

- UK HSE, human factors topic "Procedures" (level of detail suited to the user,
  the task and the consequences of failure; involve users; walk through the task)
  — https://www.hse.gov.uk/humanfactors/topics/procedures.htm (OGL v3.0)
- US DOE, *Writer's Guide for Technical Procedures*, DOE-STD-1029-92 (cancelled, archived;
  US government work) — https://www.osti.gov/biblio/308015
- GOV.UK Service Manual, usability testing (observe people completing the task) —
  https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing
