# Gotchas — flow analysis

Ways this skill produces a confident wrong answer. Check before finalising.

---

## 1. Straight-line distance reported as distance walked

**Bad:** Start and end points are 5 m apart, so "the cook walks 5 m".
**Good:** Distance along the recorded points (the route went 4 m, turned, then
3 m = 7 m). If the turns were not recorded, the result is a lower bound — say so.

## 2. Sketch units reported as metres

**Bad:** Coordinates read off an unscaled sketch, reported as "38 m per order".
**Good:** Run `path` without `--unit`; present the chart as schematic; ask for
one known distance (a door width, a bench length) if distance matters.

## 3. Elapsed time reported as processing time

**Bad:** Submitted 09:00, approved 10:00 → "approval takes 60 minutes, the
approver is slow".
**Good:** Without the time work started, 60 minutes is lead time. If the log
shows work started at 09:50, it is 50 minutes waiting and 10 minutes working —
and the fix is the queue, not the approver.

## 4. One observation called a bottleneck

**Bad:** One slow case → "the bottleneck is quality review".
**Good:** One case is a lead. Follow more items, on different days or shifts,
before naming a stable bottleneck.

## 5. Watched processes run better

People work differently while being observed. A single observation right after
announcing a review may look better than a normal day. Observe more than once,
and compare with any records that were produced without an observer.

## 6. A check removed because it "adds no value"

**Bad:** "Second review adds no value to the customer — remove it."
**Good:** Find what it catches (for example, fraudulent payment-account
changes). Keep the function; shorten the wait in front of it or replace it with
something verified to catch the same failure.

## 7. Proposed layout counted as savings

**Bad:** "Moving the fridge saves 1.2 km per shift."
**Good:** "The proposed route computes to X m per trip (proposed). Confirm by
tracing the route after the move."

## 8. Everything classified as waste

If most steps come out as waste, the classification is probably too harsh or
the controls were missed. Re-check each "waste" step for a failure it prevents.

## 9. Folding unknown time into a state

**Bad:** An item has no "work started" time, so its whole 65 minutes is added to
waiting, and the average wait shifts.
**Good:** It stays under `split_unknown`, counts toward lead time only, and is
named in the output. (Seen in testing: this moved a reported mean from 202.7 to
197.2 minutes.)

## 10. Sub-group numbers made up on the spot

**Bad:** "Same-day requests averaged 49 minutes" with no script run behind it.
**Good:** Filter the CSV to same-day requests and run `timeline` again, or leave
the number out. The `largest` / `without_them` block covers the common
"is it a few outliers?" question.

## 11. Weekdays guessed from dates

**Bad:** "Submitted Sunday, reviewed Monday — a weekend hold" when the date was
a Monday. A wrong weekday invents a cause.
**Good:** Use the weekday the script prints next to each timestamp.
