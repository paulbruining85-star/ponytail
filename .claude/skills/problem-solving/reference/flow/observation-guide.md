# Observation guide

For users who have no data yet. The aim is a few honest observations of the
real process, not a perfect study.

## Before you go

- Pick **one item** to follow from start event to stop event (one order, one
  sample, one invoice, one table's order in a kitchen).
- Tell the people involved what you are doing and why: you are looking at the
  process, not grading them. People change how they work when watched; say so,
  and plan to observe more than once.
- Bring a sketch of the area (for physical flow) or a list of the systems and
  inboxes the item passes through (for paperwork).

## Observation sheet

One row per step. Leave blanks rather than guessing.

| # | Step (what happens) | Who | Where (zone, or x,y on the sketch) | Start time | End time | Waiting before it? (min) | Handoff to | Rework / loop back? | Notes (what people said) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |

For movement, also note each turn and each trip back to fetch something — the
distance calculation only knows the points you record.

Convert to CSV for the script:

- movement → `trip, x, y, label` (one row per point, in order)
- time → `case, time, state` where state is what the item was doing from that
  moment: `queue`, `work`, `transport`, `rework`… and `done` at the end

## Question bank for the people doing the work

Pick five to eight that fit. Ask, then listen; do not argue with the answer.

**The flow**
1. Walk me through what you do when this item reaches you.
2. Where do you usually wait, and what are you waiting for?
3. What do you have to go and fetch, and how far is it?
4. When does this come back to you to be redone? Why?
5. What do you do that you think nobody downstream uses?

**The workarounds**
6. Is there a step you do differently from the written procedure? Why does
   your way work better?
7. What do new people get wrong here in their first weeks?
8. What would you change first if it were up to you?

**The controls**
9. Which checks here have actually caught a problem? What was it?
10. Which checks do you think never catch anything? How would we know?

**The data**
11. Where is this recorded, if anywhere? Who could export it?
12. Is a normal day different from a bad day? What makes a bad day?

## After the walk

- Put each answer next to the step it concerns, marked *reported* with who said it.
- Mark what you timed or traced yourself as *observed*.
- One walk is a lead. Two or three on different days or shifts start to show a pattern.
