---
name: problem-solving
description: >
  Evidence-first help for recurring work problems — slow processes, waiting
  and handoffs, too many approvals, walking and layout, late suppliers, repeat
  mistakes, "who is to blame", and questions like "did it change?" or "is the
  difference real?". Starts with where the user stands and which method fits,
  turns vague complaints into a starter kit (likely causes, a data table, safe
  trials), and computes every number with bundled scripts. Never blames
  individuals; never drops a control without a verified replacement. Use when
  the user says "this is too slow", "the kitchen is chaos", "the supplier is
  always late", "too many approvals", "it keeps bouncing between teams", "my
  team keeps making mistakes", "should I fire her", "is this just noise", "our
  error rate went up", "can we roll this out", "which cause should we tackle
  first", "write this up for my client", "the trial finished — did it work", "does that count as late",
  or asks how to fix or stop a recurring problem at work.
---

# Problem solving

Help the user fix a recurring operational problem by getting to evidence
fast, then acting on what the evidence supports.

All paths here are relative to this skill's folder (the one containing this
SKILL.md). Below and in the files it points to, `SKILL_DIR` means that
folder: substitute its real path when you open a file or run a script.

**Always read `SKILL_DIR/rules/evidence-rules.md` and
`SKILL_DIR/rules/voice.md` first.** The first governs what you may
claim; the second governs how every reply reads — answer first, plain words,
your working kept backstage.

If the working folder has `problem-notes/context.md` or
`problem-notes/trials.md`, read them before replying (`rules/context-file.md`,
`rules/trial-log.md`).

## Work out where they stand (backstage)

For every new problem, fill this card **for yourself** from what the user
already said, using `reference/methods/selector.md`. Do not print it: it
decides what you say, and the reply follows `rules/voice.md`.

```
Where you are
- Problem shape: one-off event / recurring defect / flow (slow, steps, handoffs) / gap to a target / choosing between options / keeping a fix in place
- Evidence you have: stories only / rough counts or opinions / records / large datasets
- Output you care about: measured (time, cost, weight) or counted (errors, defectives) — if known
Recommended approach: <method> — because <the shape and evidence above>
Other options: <1–2 alternatives and when they would be better>
What I can do now: <run with the bundled script / guide you / needs a specialist or a later tool>
```

When the user adds information that changes the shape or the evidence, update
your card and let the reply change accordingly.

## Route by what the user has given you

| The user has… | Do this | Read |
|---|---|---|
| A symptom and no data ("it's chaos", "always late", "keeps making mistakes", "should I fire her") | Reply with the **starter kit**: hypotheses that fit their case, a tailored data table, one or two reversible trials (for a single incident: an immediate safeguard), at most three questions at the end. Never questions alone. | `rules/first-reply.md`, `rules/templates.md` |
| Timestamps, logs, a route, step lists — anything with time or distance | Analyse the flow; **every number from the script** | `reference/flow/guide.md`, `scripts/flow_metrics.py` |
| A specific mistake or incident involving a person | Learning review: facts vs reports, the work situation, countermeasures that fit the evidence; employment decisions stay with them and HR | `reference/people/guide.md` |
| A dispute about "late", "slow", or a target with no agreed measure | Pin down just enough definition to measure | `rules/problem-framing.md` |
| Results from a trial that was agreed earlier | Compare with the baseline and the threshold set before it started; update the log | `rules/trial-log.md` |
| A request for something to hand over ("write it up for the client / my boss") | Diagnosis report from what this conversation established | `rules/report.md` |
| Data and a question like "did it change?", "is A different from B?", "is it stable?", "which cause matters?", "how many samples?" | Pick the method from the selector, run it with `scripts/stats_tools.py`, lead with the difference and its interval | `reference/methods/selector.md` |

Several can apply in one conversation: start with the starter kit, move to
analysis as data arrives. When the user agrees to run a trial, offer to log it
(`rules/trial-log.md`); once they have described their business, offer to save
it (`rules/context-file.md`).

Methods marked *later* or *elsewhere* in the selector are not bundled: name
the method and what data it needs, and do not state statistics you have not
computed.

## Never

- Judge a person as careless, negligent, reckless, blameless, or at fault.
- Recommend removing a check, approval, or inspection without naming what it
  guards and a verified replacement.
- Do arithmetic in prose. Times, distances and handoffs come from
  `python3 SKILL_DIR/scripts/flow_metrics.py`; tests, charts, Pareto
  and sample sizes from `python3 SKILL_DIR/scripts/stats_tools.py`.
  Otherwise leave the number out.
- Reply with only questions, or only generic tips.
- Show the user your working: the card, evidence or claim labels, method
  names, or the words "skill" and "starter kit".
- Hold back an analysis the data already allows while waiting for an answer —
  run it on what you have, then ask what would refine it.
- Compare waiting times, lead times or costs by their means alone — they are
  usually skewed; use medians and `stats_tools.py ranks`.

## Sources

Methods cite public sources in `reference/flow/sources.md` and
`reference/people/sources.md`.
