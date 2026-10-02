# Problem framing — just enough, at the point of use

Read `evidence-rules.md` first.

Most "the process is slow / the supplier is late / people keep making mistakes"
requests arrive without an agreed definition of the problem. You do **not**
need a full project charter. Pin down only what the current step needs, and
carry the rest as open items.

## The five questions

Answer what you can from the user's own words and state reasonable
assumptions for the rest. Ask at most two or three, only when the answer would
change the plan — and never as the whole reply: give the starter kit from
`first-reply.md` first.

1. **Compared with what?** "Slow" or "late" against which promise, standard, or
   customer need? Who set it?
2. **From when to when?** The start and stop events that define the measure
   (submitted → approved; shipped → received). Two parties using different
   events will both be right and still disagree.
3. **Which items?** Scope: which orders, products, shifts, sites, time period —
   and what is deliberately out of scope.
4. **How is it counted?** The unit and the denominator (per order, per line, per
   day; late orders ÷ all orders or ÷ orders due).
5. **What must not get worse?** The side effects the fix may not buy speed with:
   errors, compliance, safety, customer experience, cost.

## When the "problem" is a target, not a defect

"Deliver $2M savings", "grow margin 3%", "cut lead time" — nothing is broken,
but there is a gap to a target. The target *is* the problem statement once it
is cascaded:

1. **Break it down with data.** Pareto the base the target applies to (spend by
   category → supplier → item; volume by product; lead time by step) and pick
   the slice where the addressable gap is biggest. Say what data to pull.
2. **Define the measure for that slice** — unit price vs index, total cost of
   ownership, price variance, lead time — with start/stop and denominator.
3. **Look behind the number.** A supplier's price is our input but the output
   of their process: specs, tolerances, order sizes and frequency, forecast
   quality, logistics, payment terms and our own late changes all drive it.
   Savings come from those drivers as well as from negotiation.
4. Each slice becomes its own small project with its own owner.

## One main result, plus guard metrics

If the user names several goals, keep one main result for the analysis and list
the others as *must-not-worsen* guard metrics. Two unrelated outcomes usually
mean two separate problems with different causes.

## Output: a short problem card

The card is for your thinking. Show the user only the lines they need, in
plain words and after your answer (`voice.md`).

```
Problem card
- Customer / who is affected:
- Main result (measure, start → stop event, unit):
- Compared with: (target or standard, and who set it)      [verified | reported | unknown]
- Scope in / out:
- Must not worsen:
- Current evidence: (what we have, with source)
- Open items: (what is unknown and which conclusion it holds back)
```

Leave unknowns as unknowns. Do not invent a baseline or approve a target on the
user's behalf. A hunch about the cause does not belong in the problem card.

Method basis: the Define and Measure phases of DMAIC — identify the customer and
their requirements, the problem, scope, and an operational definition of the
measure (see `reference/flow/sources.md`).
