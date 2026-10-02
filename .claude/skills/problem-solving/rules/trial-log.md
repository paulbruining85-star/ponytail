# Trial log

A trial only teaches something if the user comes back and checks it against
what was decided before it started. Keep the log at `problem-notes/trials.md`
in the user's working folder.

## When a trial starts

When the user agrees to run a trial you proposed, offer to log it. On a yes,
append an entry (where you cannot write files, give the entry for the user to
save):

```markdown
## T<n> — <short name>   status: running
- Started: <date>   Check on: <date>
- Problem: <symptom in measurable terms>
- Hypothesis: <what we think is going on>
- Change: <what is different>   Control kept: <check that stays, or "none affected">
- Measure: <what number, from which record, collected how>
- Baseline: <value> — source: <record, period>; command: <script command, if derived>
- Success if: <threshold, decided now>
- Result: —
- Decision: —
```

The success threshold is set before the trial starts. Do not move it after
seeing the result.

## When the user comes back

1. If `problem-notes/trials.md` exists, read it first and list the running
   trials in one line each.
2. Take the new data and compute the result the same way as the baseline —
   same measure, same record, same script. Use `stats_tools.py` to compare
   before and after, and report the difference with its interval.
3. Compare with the threshold that was set, not with a new one — and compare
   its **range**, not just the point: compute the new rate with its interval
   (`stats_tools.py prop --x1 --n1 --p0 <threshold>`). If the range still
   crosses the threshold, say the target is not yet clearly met, even when the
   point estimate is past it. Do not open with "yes, it hit the target" unless
   the whole range is past the threshold.
4. Name anything else that changed during the trial (volume, mix, staff,
   attention). Until those are ruled out, the claim level is *associated*,
   not *cause* (evidence rule 6).
5. Update the entry: result (with the command), claim level, decision (keep /
   extend / stop / run longer), status.
