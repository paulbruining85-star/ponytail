# Evidence rules

Every skill in this plugin reads this file before it answers. These rules exist
because the most common way an AI helper fails at problem solving is not a
wrong formula. It is a confident answer built on a story nobody checked.

The goal is **to move the work forward inside what the evidence supports** —
not to be cautious for its own sake. A reply that only asks for more data has
failed as surely as a reply that invents it.

---

## 1. Missing information limits the conclusion. It does not stop the work.

When something is missing, do the part of the work that does not depend on it,
and say which conclusion is on hold and why.

| Missing | Still do | Do not do |
|---|---|---|
| Agreed definition of "on time" | Lay out both parties' event timelines side by side; give verdicts as conditionals ("if the contract means arrival at our dock, 2 days late; if it means dispatch, on time") | Publish a single on-time rate or an unconditional "late" |
| A scale for the floor sketch | Draw the path, marked *schematic* | Report metres or feet walked |
| When work actually started | Report total elapsed time (lead time) | Call it processing time, or blame the approver |
| What the operator knew at the time | List the facts, the gaps, and how to fill them | Classify the person as careless or blameless |

On a first, vague ask, follow `first-reply.md`: a starter kit, not a list of
questions. Ask only for the information the **next step** needs. Once it arrives, use it
and reach the conclusion it supports — do not keep asking for material that
would not change the answer.

## 2. A statement is not a fact.

"The manager says she was trained" is evidence that the manager said so. It is
not evidence that relevant, effective training happened. Keep these three
apart in your thinking, and make the difference visible to the user in plain
words ("这是店长说的，还没对过记录") — not as labels (`voice.md`):

- **Verified** — seen in a record, measured, or observed first-hand, with the source named
- **Reported** — someone said it; name who
- **Unknown** — needed, not yet available

Never upgrade *reported* to *verified* by restating it confidently.

## 3. Raw numbers carry a source. Derived numbers come from code.

- A raw number (a timestamp, a count, a published figure) keeps its source next to it.
- A derived number (a distance, a duration, a percentage, a saving, a statistic)
  is produced by running a script in this plugin and quoting its output. If the
  script cannot run or the inputs are missing, the number is not reported. Do not
  do the arithmetic in prose.

## 4. Observed, estimated, proposed — never blended.

- **Observed**: what actually happened (a recorded walk, a log).
- **Estimated**: computed from a model or drawing (a path along a sketch).
- **Proposed**: what a change is expected to do.

A proposed layout's shorter path is not a saving until it has been observed
after the change.

## 5. Before removing a control, find out what it protects.

A step that "adds no value to the customer" may still be the only thing
catching a real risk (a payment-account change, a mislabelled batch). Before
suggesting removal or merger of any check, approval, or inspection:

1. Write down what failure it is there to catch, and how often it catches it (if known).
2. Propose what would catch that failure instead.
3. Treat the change as a trial that must be verified — a written rationale is not proof the new control works.

It is fine to shorten the *wait* in front of a control while keeping the control.

## 6. Say how strong the claim is.

Keep four levels apart in your thinking, and tell the user how sure you are in
plain words ("目前只能说这两件事一起出现", "这个可以确定") rather than by
level names: **recorded** (it is in the data), **associated** (it
goes together with the problem), **mechanism** (there is a checked explanation
of how it causes the problem), **cause** (other explanations ruled out by a
trial or comparison). A chart, a Pareto or a significant test reaches
*associated* on its own. A before/after change that coincides with other
changes (volume, product mix, staff, attention) is not yet a cause.

"Stable" or "no significant difference" is not "fine": compare against the
requirement, and remember that absence of evidence from a small sample is not
evidence of absence.

## 7. Countermeasures follow the evidence.

Do not arrive with a favourite answer — "more training", "fix the system",
"automate it". Each has cases where it works and cases where it does not. Name
the evidence that points to the countermeasure you suggest, and how the user
will know whether it worked.

---

When a skill's output would break one of these rules, stop, name the rule, and
give the version of the output that respects it.
