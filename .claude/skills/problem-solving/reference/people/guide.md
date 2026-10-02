# Human error review

Most repeat mistakes are shaped by the work: the procedure, the tools, the
layout, the workload, the handover, the training for *this* task. Some are not.
This skill finds out which, using evidence, and suggests the countermeasure
that fits.

**Follows `rules/evidence-rules.md`; with no incident details yet, `rules/first-reply.md` and the mistake-log template in `rules/templates.md`.** Rules 1, 2, 6 and 7 do most of the work here: keep reported and verified apart,
do not stall, say how strong each claim is, and let the evidence choose the countermeasure.

## What this skill never does

- **It does not judge the person.** No "careless", "negligent", "reckless",
  "blameless", "not their fault". An account from one side is not enough to
  judge anyone, and judging is not the goal: preventing the next occurrence is.
- **It does not assume the answer is "the system" either.** Sometimes the fix
  is training, sometimes supervision, sometimes a conversation. The evidence decides.
- If the user raises deliberate harm, theft, intoxication, or a conduct or
  disciplinary decision, say that is a matter for their HR or legal process,
  offer to keep helping with the learning review, and stop there.

---

## Step 0 — One incident or a pattern?

- **"My team keeps making mistakes", "fix my people"** — a pattern with no
  incidents described yet. Reply with the starter kit: likely places the work
  itself produces the errors (unclear or changed instructions, look-alike items,
  handoffs, rush periods, missing checks), the **mistake log** for the next two
  to four weeks, a quick check you can put at the most error-prone step now,
  and at most three questions. Do not diagnose individuals.
- **A specific incident, few details** ("a new hire deleted an order") — still
  a starter kit, not only questions: the facts to establish (Step 1–2), the
  immediate safeguard that would stop a repeat whoever is at the keyboard
  (confirmation step, undo or soft delete, permissions, a checklist), and how
  to check it works. Then continue with Step 1 as facts arrive.
- **A specific incident with details** — continue with Step 1.

**Privacy.** Mistake logs and incident notes are personal data. Use roles or
random IDs in anything shared, collect only what the review needs, and do not
build per-person error rankings: without the number of items each person
handled, counts mostly measure workload and honesty.

## Step 1 — Sort the account

From what the user said, build three short lists:

- **Verified** — seen in a record or observed first-hand (name the source)
- **Reported** — someone said it (name who). "She was trained" and "he always
  rushes" belong here until checked.
- **Unknown** — needed and not yet available

Then write a plain timeline: what was supposed to happen, what happened, when
the difference appeared, what the consequence was.

## Step 2 — Reconstruct the work situation

Read `reference/people/question-bank.md`. Pick the questions that fit and turn each
unknown into a concrete way to answer it: which record to pull, whom to ask,
what to watch. Cover at least:

- **The task and the instruction** — was there a written procedure for *this*
  task? Was it current, usable at the point of work, and correct? Do other
  people actually do it that way?
- **Tools, labels, layout, interface** — could the wrong action be done easily,
  or the right one missed easily?
- **Conditions** — time pressure, interruptions, staffing, shift, fatigue, noise.
- **Knowledge for this task** — was the person taught *this* rule or change,
  and was their understanding checked? "Trained on the job in general" is not
  the same thing.
- **Handover and communication** — did the needed information reach them, in a
  form they could use?
- **History** — has anyone else made the same or a similar mistake?

Pose the **substitution question** as something to find out, never something
to answer by imagination: *would another person with similar experience, in
the same situation, have been likely to do the same?* Answer it with evidence —
how colleagues do the task, whether the workaround is common, whether others
have had near misses.

## Step 3 — What kind of error does the evidence point to?

Only once there is evidence, and always labelled as a working hypothesis:

| Evidence suggests | Typical signs |
|---|---|
| **Slip or lapse** in a well-practised task | Knew what to do and has done it right many times; attention was pulled away (interruption, distraction, similar-looking items) |
| **Rule-based mistake** | Applied a familiar rule where it did not fit, or misread which situation they were in; a rule recently changed |
| **Knowledge-based mistake** | Unfamiliar situation; worked it out from first principles with an incomplete picture of how the system behaves |
| **Deliberate deviation** | Knowingly did it differently. Ask why it made sense to them: the procedure may be unworkable, slow, or routinely ignored |

If the evidence does not yet separate these, say so and name the one fact that would.

## Step 4 — Countermeasures that fit

Read `reference/people/countermeasures.md`. Suggest two or three, each tied to the
evidence and each with a way to check it worked. In short:

- **Slips and lapses:** change the work, not the person — checklists at the
  point of use, forcing functions and mistake-proofing, fewer interruptions,
  clearer labelling. More training rarely helps a skilled person who knew what to do.
- **Rule-based mistakes:** clarify or fix the rule, make the cue that tells
  situations apart more visible, and train and practise *that specific rule*.
- **Knowledge-based mistakes:** support for unusual situations — escalation
  routes, a second check, practice on rare cases, better information at hand.
- **Deliberate deviations:** fix the reason the rule is bypassed (an unworkable
  step, missing time, conflicting targets), then agree and model the expectation.

Training is a legitimate countermeasure when the evidence shows a knowledge
gap for the specific task. It is the wrong one when the person already knew.

## Step 5 — When the user supplies the missing facts

Use them. Move the hypotheses to findings where the evidence now supports it,
drop the ones it rules out, and give the countermeasure. Do not keep asking for
material that would not change the answer.

---

## Output: learning review card

```
What happened (timeline)
Facts — verified / reported / unknown
Work situation — what we found, what we still need (and how to get it)
Kind of error — hypothesis or finding, with the evidence
Countermeasures — each with: evidence it fits, owner, how we'll know it worked
Not concluding yet — and the fact that would settle it
```

Plain words, no jargon labels unless the user uses them. Short enough to use in
a conversation with the team.

## Reference files

| File | Load when |
|---|---|
| `reference/people/question-bank.md` | Step 2, always |
| `reference/people/countermeasures.md` | Step 4, always |
| `reference/people/gotchas.md` | Before finalising |
| `reference/people/sources.md` | The user asks where this comes from, or you cite a source |
