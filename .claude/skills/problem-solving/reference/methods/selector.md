# Method selector

Choosing the method is itself a decision driven by evidence: **what shape the
problem has, and what data exists**. Use these tables to (1) tell the user
where they stand, (2) recommend a method with the reason, (3) name the
alternatives, and (4) say what this plugin can run now.

**Most-used in knowledge work, in order:** is a weekly/monthly measure
changing? (XmR chart) · which categories dominate? (Pareto) · did a pilot
change a rate? (two proportions) · are times/costs shorter or lower now?
(rank-based comparison). Reach for the rest only when these do not fit.

Status column: **run** = computed by a bundled script · **guided** = the skill
walks the user through it, no script · **later** = planned tool; guide the user
and do not compute by hand · **elsewhere** = point to a specialist or tool.

Sources for each table are in `sources.md` in this folder.

---

## A. What shape is the problem?

| The user describes… | Shape | Start with | Status |
|---|---|---|---|
| Something went wrong once (an incident, a complaint) | One-off event | Learning review of that event — not an improvement project | guided (`reference/people/guide.md` if a person's action is central) |
| The same kind of error keeps happening | Recurring defect | Collect occurrences (mistake log), then causes → evidence ledger | guided |
| It takes too long, too many steps, bounces around | Flow problem | Process walk: waiting vs work, handoffs, motion | run (`flow_metrics.py`) |
| A target with nothing "broken" ("save $2M", "cut lead time 20%") | Gap to a target | Cascade the target with a Pareto to the biggest slice (`rules/problem-framing.md`) | guided |
| Choosing between options | Decision | Criteria-based comparison with sensitivity (G below) | guided |
| A fix worked and must stay fixed | Sustain | Control plan and handover (H below) | guided |

**Is it a structured improvement project (DMAIC-style) at all?** Only if: the
process repeats, there is a measurable output with a customer requirement, the
cause is not already known, there is (or can be) data on it, and someone owns
it. A one-off, or a cause everyone can already see and fix, does not need one —
just fix it and check.

## B. What evidence exists? → how to find causes

| Evidence available | Typical methods | What they give you | Status |
|---|---|---|---|
| **Stories only** — people's accounts, no records | Structured brainstorm of causes (fishbone by people / methods / machines / materials / measurement / environment), 5 Whys on a specific occurrence | A list of **hypotheses**, not causes | guided |
| **Rough counts or opinions** — tallies, votes, rankings | Pareto of cause categories (`stats_tools.py pareto`); weighting candidate causes or fixes in a matrix | Priorities among hypotheses | run (Pareto) / guided |
| **Records** — timestamps, measurements, logs for dozens to hundreds of items | Measure → graph → compare (C, D below); stratify by candidate causes | Which candidates are **associated** with the problem, and how strongly. A cause is established only by a design that rules out other explanations (a controlled trial, a before/after with a comparison group, or a confirmed mechanism) | run (flow, stats) |
| **Large datasets** — thousands of rows, many variables | Data-analytic screening (regression trees, random forests) to shortlist variables, then confirm with a designed check | Candidate drivers to confirm | elsewhere (a data analyst) |

Moving right in this table is usually cheaper than it looks: a two-week tally
turns stories into counts. Say that when the user has only stories.

## C. How far to take the analysis? (practical → graphical → analytical)

Stop at the first rung that answers the question.

1. **Practical** — use what already exists: system exports, logs, prior incident notes. Check data quality before anything else (typos, wrong area, duplicate records).
2. **Graphical** — plot it: time series, histogram, box plot by group, Pareto, scatter. Often this shows where to look (a shift after a change, two groups that differ) — an association to check, not proof of cause: other things may have changed at the same time (volume, mix, season, staff).
3. **Analytical** — a statistical test when the picture is ambiguous and the decision matters (D below).
4. **Multivariable** — only when several causes interact: multiple regression (inputs roughly independent), a designed experiment (you can set the inputs), multivariate analysis (inputs move together).

A picture that shows **two humps** usually means two processes mixed together
(two machines, shifts, suppliers): split the data before any statistic.

## D. Which statistical test? (by the output's data type and the comparison)

Script: `python3 SKILL_DIR/scripts/stats_tools.py <command>`. Report the
difference and its range first, in plain words (`rules/voice.md`); test names
and p-values only if the user asks. If the script returns
`"status": "error"`, say the analysis could not be run and why — never fill in.

Choose in this order: (1) **what quantity matters for the decision** — a
typical value, an average or total (e.g. total cost), or a proportion;
(2) **the design** — independent groups, the same items twice, one group vs a
target; (3) only then the data's shape.

| Output (Y) is… | Question | Test | Status |
|---|---|---|---|
| Measured, skewed (waiting time, lead time) — question about the **typical** case | Two independent groups | **Rank-based comparison** (Mann–Whitney) — `ranks` | run |
|  | Same items before vs after | Wilcoxon signed-rank — `ranks --paired --a --b` | run |
| Measured, skewed — question about the **average or total** (e.g. total cost) | Two groups | Welch t on means, flagged as approximate if small — `ttest` | run |
| Measured, roughly symmetric | One group vs a target | One-sample t — `ttest --mu` | run |
|  | Two independent groups | Two-sample t (Welch) — `ttest --a --b` | run |
|  | Same items before vs after | Paired t — `ttest --paired` | run |
|  | Three or more groups | One-way ANOVA — `anova` | run |
|  | Is the spread different? | F-test / Levene | later |
|  | Does Y move with X? | Correlation and regression | later |
|  | Is it roughly normal? | Plot first (histogram) | guided |
| Counted (yes/no, defective, late) | Two proportions (pilot vs before, team A vs B) | **Two-proportion test** + Fisher exact — `prop --x1 --n1 --x2 --n2` | run |
|  | Proportion vs a target | One-proportion test — `prop --x1 --n1 --p0` | run |
|  | Categories vs categories (error type by shift) | Chi-square test of association — `chisq` | run |
|  | Counts vs an expected pattern | Chi-square goodness of fit | later |

Ask the user only what picks the row: is the output measured or counted, how
many groups, independent or the same items twice, how many data points.
Report what the result means for the decision, not "p < 0.05" alone.

**Skewed data** (waiting times, costs): plot first; use the rank-based test in
the table or a transformation; ask someone who knows the process what shape is
normal for it.

## E. Is it stable over time? (control charts)

Script: `stats_tools.py chart imr|p|u data.csv --svg chart.svg` (rules 1–2 by default).

| Data | How it arrives | Chart | Status |
|---|---|---|---|
| **One number per period** (weekly lead time, monthly % late, daily tickets) | One value at a time | **Individuals and moving range (XmR / I-MR)** — the general-purpose chart for management data — `chart imr` | run |
| Counted: defective items, with the sample size each period | Sample size varies or constant | p chart — `chart p` (columns label,count,n) | run |
| Counted: defects per unit, with units each period | Varies or constant | u chart — `chart u` | run |
| Measured in subgroups (2–9 / 10+ per sample) | Production sampling | X̄-R / X̄-S | elsewhere |

When only percentages are available, an XmR chart of the percentages is a
reasonable start — say so; a p chart is better once the counts are known.

An XmR chart checks both the individual values and the moving ranges; report
both. **"No signal" is not "fine".** Control limits describe what the process
does, not what the customer needs: a process can be perfectly stable and still
miss the target or SLA every week. Always compare the level with the
requirement, and keep improving if it misses.

**Signals that something changed** (special causes): a point beyond the limits;
a run of points on one side of the centre line; a steady trend up or down;
points alternating up and down. Turning on every rule raises false alarms —
start with the first two.

**Before trusting any chart, check the measurement.** If two people measuring
the same item get different results, or the gauge cannot tell good from bad,
the variation you see may be the measurement, not the process (measurement
system analysis: bias, repeatability, reproducibility, resolution). Status: guided.

## F. How much data?

State what you are trying to do, then size it:
- **Estimate** a mean or a proportion to within ± a margin → sample size from the margin and the spread (or the expected proportion).
- **Detect** a difference of a given size → power calculation.
- A histogram of six points is not a histogram; proportions need far more data than measurements.

Script: `stats_tools.py size mean --sd --margin` · `size proportion --p --margin`
· `size two-proportions --p1 --p2` (per group, 80% power). Status: run.

## G. How to test changes and choose between options

| Situation | Method | Status |
|---|---|---|
| One or two candidate fixes, easy to reverse | Trial with before/after measurement on the same basis | guided (flow: run) |
| Several factors may matter; you can set them | Designed experiment: screening (fractional factorial) first, then full factorial on the few that matter | elsewhere / later |
| Changing one factor at a time | Avoid when factors interact — it misses interactions and gives no prediction | — |
| "It worked, but only at one exact setting" | Look for a robust setting (performance *and* its variation), not a spike | elsewhere |
| Choosing among options with several criteria | Decision matrix against a baseline; show the scoring evidence and whether the winner changes when weights change | guided |

## H. How to make it stay fixed

Pick the control by how bad the failure is and how easy it is to detect:
- **Make the error impossible or obvious** (mistake-proofing) when the failure is serious or hard to detect later.
- **Monitor with a chart** when the process drifts slowly and is measured regularly.
- **Inspect a sample** when neither is practical — and know that inspection finds problems, it does not prevent them.

A control plan names, for each critical input: the specification, how it is
measured, how often and by whom, and **what to do when it goes wrong**
(reaction plan), plus an owner. Check the gain still holds after the project
team steps back and after people return from leave.

## I. People and mistakes

See `reference/people/guide.md`: the kind of error decides the countermeasure
(slips and lapses → change the work; rule-based mistakes → fix and teach the
rule; knowledge-based → support for unusual situations; deliberate deviations
→ fix why the rule is bypassed).

## J. Counting the benefit

Separate: cash out of the P&L vs cost avoided; one-time vs every unit from now
on; labour hours freed vs headcount actually reduced. Freed hours are not cash
until someone decides what to do with them. Status: guided.
