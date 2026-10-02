# Flow analysis (process walk)

Help the user see their process as it really runs, then suggest changes the
evidence supports. The chart is not the deliverable; a checked picture of where
time goes and a short list of changes worth trying is.

**Follows `rules/evidence-rules.md` and `rules/problem-framing.md`; with no data yet, `rules/first-reply.md` and `rules/templates.md`.** They govern everything
below. In particular: unknowns limit conclusions but never stop the work, and
every distance or duration comes from `SKILL_DIR/scripts/flow_metrics.py`.

---

## Step 1 — What kind of flow is it?

Decide from what the user already said; ask only if it is genuinely unclear.

| The work moves… | Use | Needs |
|---|---|---|
| People or materials through a physical space | **Spaghetti chart** | The route as ordered points, and a scale if distance matters |
| Information, documents, approvals, tickets | **Swimlane + timeline** | Who does each step, and timestamps |
| Work passed between people, teams or systems (requests, tickets, email threads) | **Virtual spaghetti**: handoffs instead of metres | A log with `case, time, state, actor` |
| Both (e.g. a lab sample and its paperwork) | Both, linked by step | Both of the above |

Office users rarely have a floor plan. Never ask for one when the problem is
about waiting and handoffs.

Pin down the problem only as far as this step needs (`rules/problem-framing.md`): which
item is being followed, from which start event to which stop event.

## Step 2 — Get facts from the real process

If the user already has records (a log export, timestamps, a sketch with the
route), use them.

If not, the reply is the starter kit from `rules/first-reply.md`: hypotheses that
fit their situation, a tailored data table from `rules/templates.md` (ticket timing,
invoice to payment, approval chain review, supplier on-time with both clocks,
picking and walking), one or two reversible trials, and at most three questions
at the end. Never reply with questions alone. For a physical walk, also read
`reference/flow/observation-guide.md` and hand over:

- **Follow one real item end to end** (one order, one sample, one plate, one
  invoice) — not the process as the manual describes it.
- **The observation sheet** from that file, pre-filled with the steps they
  already mentioned.
- **Five to eight questions for the people doing the work**, picked from the
  question bank to fit their situation. The people doing the work every day
  know things no manager or document shows.

Tell them one observation is a sample, not a pattern: plan to follow a few
items, on different days or shifts, before calling anything the bottleneck.

## Step 3 — Compute, don't estimate

Write the data to CSV and run the script. Never add up distances or minutes yourself.

```bash
python3 SKILL_DIR/scripts/flow_metrics.py path route.csv --unit m --svg spaghetti.svg
python3 SKILL_DIR/scripts/flow_metrics.py timeline events.csv
```

- `path` columns: `trip, x, y, label` in walk order. Omit `--unit` when the
  layout is a sketch — the script then refuses to call the result a distance and
  the SVG is stamped *schematic*.
- `timeline` columns: `case, time, state`. Each state (`queue`, `work`,
  `rework`, `transport`, …) lasts until the next row; end each case with `done`.
  If only start and finish are known, the script reports lead time and warns
  that processing time is unknown. Say exactly that.
- A log with **one row per item** (id, then one timestamp column per step, e.g.
  `request, submitted, review_started, approved`) goes in as-is:
  `timeline log.csv --wide queue,work` — name the state between each pair of
  timestamp columns. Rows with a blank timestamp are kept for lead time and
  listed under `split_unknown`.

**Every average, median, share, and total you report is copied from the
script's `summary` block. Do not compute, combine, or adjust them yourself,
even when it looks easy.**

- `by_state` already excludes items whose split is unknown; they are listed
  under `split_unknown`. Never add their time into a state.
- `largest` gives the few items that dominate each state, their share, the
  statistics `without_them`, and each item's start and end with the weekday —
  use it to answer "is it a few outliers?". Take weekdays and dates from the
  script too; never work out a day of the week yourself.
- Need a number the summary does not have (e.g. only same-day requests, only
  morning shift)? Write the filtered CSV and run the script again on it. If
  you do not run it, do not state the number.

Lead time and the state split cover **completed** cases only; open cases are
in `open_cases_observed_so_far`. If many are open, say the completed-only
figures understate the backlog. Blank holders in a handoff log are gaps, not
handoffs. If a script returns `"status": "error"`, report the error.

Describe the time span from `summary.period` (first start, last end, calendar
days) — never estimate it ("about a month of data"). Name the items in `split_unknown`. Round for the reader: minutes to whole
minutes or one decimal, metres to one decimal.

Quote the script's `basis` line under the numbers. A path through recorded
points is a lower bound on real walking unless every turn was recorded.

With an `actor` column, `timeline` also reports handoffs per item, ping-pong
(A→B→A), distinct actors and the busiest routes (`handoff_summary`), and
`--mermaid` writes the handoff graph. In knowledge work the "distance" is the
number of handoffs and the wait at each one — every handoff is a queue and a
chance for information to get lost.

For a swimlane, emit a Mermaid flowchart with one `subgraph` per role, steps in
order, and handoffs as the edges that cross lanes. Label each handoff with the
waiting time from the timeline where known.

## Step 4 — Sort the steps

Classify each step, and say it is a judgment call:

- **Value-adding** — the customer would pay for it, it changes the product or
  service toward what they need, and it is done right the first time.
- **Required, not value-adding** — the customer would not pay for it, but the
  business currently needs it: legal, safety, financial controls, checks that
  catch real failures.
- **Waste** — neither.

Use the eight wastes as a lens for spotting waste, not as boxes to fill:
defects, overproduction, waiting, unused knowledge of the people doing the
work, transport, inventory, motion, extra processing. `reference/flow/wastes.md` has
one-line tests and office examples for each.

## Step 5 — Candidate changes

For each suggestion give: the waste it targets, the evidence behind it, any
control it touches, and how the user will check it worked.

- **Waiting in front of a check is usually the cheapest win.** Shorten the queue
  (batching, notification, a second approver, clear cut-off times) while
  keeping the check.
- **Touching a control?** Apply evidence rule 5: what failure does it catch,
  what would catch it instead, and run it as a verified trial.
- **Layout moves** (move the fridge, the printer, the tool) come with the
  proposed path computed by the script and labelled *proposed*, not *saved*.
- Order by effort and evidence: quick wins the user can try this week first,
  bigger redesigns after a second round of observation.

Verification is always: measure the same way, on the same kind of item, after
the change.

---

## Output

Start with the answer in plain words (`rules/voice.md`): where most of the
time or distance goes, and what to change first. Then, with plain headings:

1. **What was followed** — item, start → stop event, how many observations, source of each.
2. **Where the time or distance goes** — the script's numbers in a table, each marked as measured or estimated (in plain words), with the basis line. The spaghetti SVG or Mermaid swimlane.
3. **Which steps help and which only wait** — a table: step, owner, adds value / needed / waste (say which kind in plain words), evidence.
4. **Candidate changes** — a table: change, targets, evidence, control affected (and its replacement), how to verify, effort.
5. **Open items** — what is unknown and which conclusion it holds back.

Keep it short enough to act on. If there is only one observation, say that the
findings are a lead to confirm, not a diagnosis.

## Reference files

| File | Load when |
|---|---|
| `reference/flow/observation-guide.md` | The user has no data yet, or asks how to observe |
| `reference/flow/wastes.md` | Classifying steps or explaining a waste |
| `reference/flow/gotchas.md` | Before finalising any number or recommendation |
| `reference/flow/sources.md` | The user asks where a method comes from, or you cite one |
