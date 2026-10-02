# Starter data templates

Adapt the column names to the user's own words and systems. Keep only the
columns their question needs. Each template says what to collect and how much.

## Ticket / order timing (kitchen, counter, workshop)
Collect: 20–30 tickets across one or two busy services, stopwatch or ticket printer times.

| ticket | ordered | started (station) | station | waited for (ingredient / equipment / person / nothing) | plated | at pass | served | notes |
|---|---|---|---|---|---|---|---|---|

Pair with a floor sketch: mark stations, and for 5–10 tickets trace the cook's route with a pen. Measure one known distance (a bench length) so the route can be scaled.

## Invoice to payment (accounts payable)
Collect: export for the last 50–100 invoices from the accounting/ERP system — **including those still unpaid**, with their age. Paid-only exports hide the backlog.

| invoice | supplier | amount | invoice date | received | entered | matched to PO / receipt | exception? (price / qty / no PO / missing approval) | exception resolved | approved | payment run date | paid | terms (days) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

The waits between columns show where time goes; the exception column usually explains the long tail. Keep matching, approval and bank-detail checks — shorten the waits around them.

## Approval chain review (any multi-step approval)
Collect: one row per step, plus timestamps for 20–30 recent requests.

| step | who | what risk it guards | has it caught anything in the last 6–12 months? | is its output used downstream? | could it be simplified (e.g. the system supplies it)? | typical wait before it | typical work time | keep / eliminate / combine / rearrange / simplify |
|---|---|---|---|---|---|---|---|---|

A step is a candidate to change only when the "risk" and "caught anything" columns say so. Trial removals with a way to spot the guarded failure returning.
The last column is the ECRS question set (eliminate, combine, rearrange,
simplify) — Lean Enterprise Institute, "The Art of Lean: Use These Tools to
Help You Improve a Process, Part 1" —
https://www.lean.org/the-lean-post/articles/the-art-of-lean-use-these-tools-to-help-you-improve-a-process-part-1/

## Supplier on-time delivery (both clocks)
Collect: the last 20–50 orders with that supplier, from purchasing records and goods receipts.

| PO | PO date | supplier's quoted lead time | date we needed it | date promised | shipped | received | qty or spec changed after PO? | late vs promise (days) | late vs need (days) |
|---|---|---|---|---|---|---|---|---|---|

Check our side too: orders placed inside the quoted lead time, or changed late, are not the supplier's lateness. Agree with the supplier which clock (shipped or received, promise or need date) counts.

## Picking / walking (warehouse, stockroom, pharmacy)
Collect: a week of pick data if the system has it; otherwise tally by hand for two days.

| item / SKU | location | picks per week | distance from location to dispatch (m) | picked together with |
|---|---|---|---|---|

Plus 5–10 traced pick routes on a scaled floor plan (`flow_metrics.py path`). Fast movers far from dispatch and items always picked together but stored apart are the usual findings.

## Handoff log (virtual spaghetti: tickets, requests, documents)
Collect: 20–50 recent items from the ticket/workflow system's history or audit trail (most systems export "status changed / assigned to" events); for email-driven work, reconstruct 5–10 threads by hand.

| case | time | actor (person, team or system holding it) | state (work / queue / rework / waiting on someone) |
|---|---|---|---|

`flow_metrics.py timeline log.csv --mermaid handoffs.mmd` gives handoffs per item, ping-pong (A→B→A), how many people touched it, the busiest routes, and a handoff graph. Items bouncing back to the requester usually point at an unclear intake; items bouncing between two approvers point at unclear ownership.

## Mistake log (repeat errors across a team)
Collect: every mistake for the next 2–4 weeks, plus near misses. Record facts, not blame.

| date / time | order or item | task type | step where it went wrong | expected | what happened | how it was detected | role or random ID (not names) | shift | **items handled that shift at this step** | product or rule recently changed? | notes from the person involved |
|---|---|---|---|---|---|---|---|---|---|---|---|

Compare **rates, not counts**: errors per items handled. The person who handles
the most work, takes the hardest cases, or reports most honestly will have the
most entries — that is not a performance signal. Look for clusters by step,
task type, product, shift and "after a change"; analyse the process, never
rank people. Keep the key from ID to name with one responsible person and use
it only if an individual follow-up is genuinely needed. Initials are not
anonymous in a small team.
