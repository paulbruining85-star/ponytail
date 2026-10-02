# Diagnosis report

Use when the user wants something to hand over — to a client, a boss, or a
team: "write this up", "I need a report for the client", "summarise for my
manager". Build it only from what this conversation has established; the report
adds no new claims.

Save it as `problem-notes/report-<YYYY-MM-DD>.md` in the user's working folder
if you can write files; otherwise give it in the reply for them to copy.

## Rules

- Every derived number comes from a script run in this conversation. Put the
  command in the appendix. No number without one.
- Every finding says how sure it is and where it comes from, in plain words
  (evidence rules 2 and 6; `voice.md`). The report body reads for a manager;
  test names and exact statistics go in the appendix.
- Roles, not names. No finding says a person is careless, at fault, or needs
  retraining.
- A proposed change is not a saving until it has been observed after the
  change. Benefits separate cash from cost avoided, and one-time from recurring
  (`reference/methods/selector.md` J).
- Keep what is unknown in its own section. Do not smooth it over to make the
  report look finished.

## Template

```markdown
# <Problem, in the user's words> — diagnosis
Prepared for: <client / team>   Date: <date>   Data period: <from – to>

## 1. The problem
<The symptom in measurable terms, and the definition used, e.g. "on time =
received at our dock by the PO date".>

## 2. What we found
| # | Finding | Where it comes from | How sure |
|---|---|---|---|
| 1 | <finding with its number, in plain words> | <record / export / observation; checked, or someone's account> | <e.g. "in the records", "goes together with the problem", "confirmed by a trial"> |

## 3. What we do not know yet
- <gap> — how to close it: <record, owner, time>

## 4. Recommended next steps
| Trial | What changes | Control kept | Measure | Success if | Check on |
|---|---|---|---|---|---|

## 5. Benefit (only if measured)
<Observed results only; otherwise "not yet measured".>

## Appendix: data and method
- Sources: <exports, logs, observations, with dates>
- Commands run: <script commands, exactly as run>
- Limits: <sample size, missing data, other changes in the period>
```
