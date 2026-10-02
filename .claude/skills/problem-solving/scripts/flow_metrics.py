#!/usr/bin/env python3
"""Flow metrics for the problem-solving skill (flow analysis). Stdlib only.

Every distance, duration and handoff count the skill reports comes from here,
never from the model's own arithmetic.

  path      Distance along recorded points (spaghetti chart) + optional SVG.
  timeline  Time in each state (queue / work / rework / ...) per case, and — with
            an `actor` column — handoffs between people, teams or systems.
  selftest  Run the built-in checks.

path CSV:     trip (optional), x, y, label (optional) — rows in walk order
timeline CSV: case, time (ISO 8601), state[, actor] — the item is in `state`
              (held by `actor`) from `time` until the next row of the same case.
              A case is complete when its last state is a done state
              (done, completed, closed, finished, 完成, 已完成, 结束, 关闭 — or --done-states).

Every output is JSON with "status": "ok" or "error". On error nothing else is reported.
"""
import argparse
import csv
import html
import json
import math
import statistics
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime

DONE_STATES = {"done", "completed", "complete", "closed", "finished", "完成", "已完成", "结束", "关闭"}
UNSPLIT = {"open", "unknown", "in_progress"}


class InputError(Exception):
    pass


def fail(msg):
    raise InputError(msg)


def num(v, what):
    try:
        x = float(v)
    except (TypeError, ValueError):
        fail(f"{what}: '{v}' is not a number")
    if not math.isfinite(x):
        fail(f"{what}: non-finite value '{v}'")
    return x


# ---------- path ----------

def path_metrics(rows, unit=None):
    trips = OrderedDict()
    for i, r in enumerate(rows):
        trips.setdefault(r.get("trip") or "1", []).append(
            (num(r.get("x"), f"row {i + 2} x"), num(r.get("y"), f"row {i + 2} y"), r.get("label", "")))
    out = {"status": "ok", "unit": unit, "trips": [], "basis": (
        "Sum of straight segments between the recorded points. Equals the real walked "
        "distance only if every turn was recorded; otherwise it is a lower bound.")}
    total = 0.0
    for trip, pts in trips.items():
        along = sum(math.dist(a[:2], b[:2]) for a, b in zip(pts, pts[1:]))
        straight = math.dist(pts[0][:2], pts[-1][:2]) if len(pts) > 1 else 0.0
        total += along
        out["trips"].append({"trip": trip, "points": len(pts), "distance_along_points": round(along, 3),
                             "start_to_end_straight_line": round(straight, 3)})
    out["total_distance_along_points"] = round(total, 3)
    if unit is None:
        # ponytail: no scale means no real-world distance; we still return geometry units
        out["warning"] = "No unit/scale given: numbers are drawing units, NOT metres or feet. Do not report them as distance walked."
    return out


def path_svg(rows, title, schematic):
    xs = [float(r["x"]) for r in rows]
    ys = [float(r["y"]) for r in rows]
    pad, size = 40, 600
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    k = (size - 2 * pad) / span

    def p(x, y):  # flip y so up is up
        return pad + (x - min(xs)) * k, size - pad - (y - min(ys)) * k

    trips = OrderedDict()
    for r in rows:
        trips.setdefault(r.get("trip") or "1", []).append(r)
    colors = ["#1f6feb", "#d1242f", "#1a7f37", "#9a6700", "#8250df", "#bf3989"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size + 30}" font-family="sans-serif" font-size="12">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{pad}" y="20" font-size="14">{html.escape(title)}</text>']
    if schematic:
        parts.append(f'<text x="{pad}" y="{size + 20}" fill="#d1242f">SCHEMATIC - not to scale</text>')
    for i, (trip, pts) in enumerate(trips.items()):
        c = colors[i % len(colors)]
        xy = " ".join("%.1f,%.1f" % p(float(r["x"]), float(r["y"])) for r in pts)
        parts.append(f'<polyline points="{xy}" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>')
        for r in pts:
            x, y = p(float(r["x"]), float(r["y"]))
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}"/>')
            if r.get("label"):
                parts.append(f'<text x="{x + 6:.1f}" y="{y - 6:.1f}">{html.escape(r["label"])}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---------- timeline ----------

def parse_time(s, where):
    try:
        return datetime.fromisoformat((s or "").strip().replace("Z", "+00:00"))
    except ValueError:
        fail(f"{where}: cannot read time '{s}' (use ISO format, e.g. 2026-09-24 09:30)")


def timeline_metrics(rows, done_states=DONE_STATES):
    cases = OrderedDict()
    for i, r in enumerate(rows):
        case, state = (r.get("case") or "").strip(), (r.get("state") or "").strip().lower()
        if not case or not state:
            fail(f"row {i + 2}: every row needs case and state")
        cases.setdefault(case, []).append((parse_time(r.get("time"), f"row {i + 2}"), state, (r.get("actor") or "").strip()))
    has_actor = any("actor" in r for r in rows)
    out = {"status": "ok", "unit": "minutes", "cases": [], "basis": (
        "Each state lasts from its timestamp to the next timestamp of the same case. Only cases whose last state "
        "is a done state count as completed; open cases report time observed so far. State time is time in that "
        "state, not hours anyone actually worked.")}
    for case, evs in cases.items():
        evs.sort(key=lambda e: e[0])
        if len(evs) < 2:
            fail(f"case {case}: needs at least a start and an end row")
        by_state = defaultdict(float)
        for (t0, s, _), (t1, _s, _b) in zip(evs, evs[1:]):
            by_state[s] += (t1 - t0).total_seconds() / 60
        complete = evs[-1][1] in done_states
        item = {"case": case, "complete": complete, "elapsed": round((evs[-1][0] - evs[0][0]).total_seconds() / 60, 2),
                "_t0": evs[0][0], "_t1": evs[-1][0],
                "start": evs[0][0].strftime("%a %Y-%m-%d %H:%M"), "end": evs[-1][0].strftime("%a %Y-%m-%d %H:%M"),
                "by_state": {k: round(v, 2) for k, v in by_state.items()}}
        if not complete:
            item["warning"] = "Not complete: elapsed is time observed so far, not a lead time."
        elif set(by_state) <= UNSPLIT:
            item["warning"] = "Only start and end are known: this is lead time, not processing time."
        if has_actor:
            item["handoffs"] = handoff_metrics([a for _, _, a in evs])
        out["cases"].append(item)
    out["summary"] = summarize(out["cases"])
    if has_actor:
        out["handoff_summary"] = handoff_summary(out["cases"])
    for c in out["cases"]:
        del c["_t0"], c["_t1"]
    return out


def summarize(cases, top=3):
    """Completed cases only for lead time and state split; open cases and cases with an
    unknown split are listed separately and never mixed in."""
    def stats(vals):
        vals = list(vals)
        if not vals:
            return {"n": 0}
        return {"n": len(vals), "total": round(sum(vals), 1), "mean": round(statistics.mean(vals), 1),
                "median": round(statistics.median(vals), 1), "min": round(min(vals), 1), "max": round(max(vals), 1)}

    done = [c for c in cases if c["complete"]]
    open_ = {c["case"]: c["elapsed"] for c in cases if not c["complete"]}
    unknown = {c["case"]: c["elapsed"] for c in done if set(c["by_state"]) <= UNSPLIT}
    split = [c for c in done if c["case"] not in unknown]
    per = defaultdict(dict)
    for c in split:
        for k, v in c["by_state"].items():
            per[k][c["case"]] = v
    s = {"cases": len(cases), "completed": len(done),
         "period": {"first_start": min(cases, key=lambda c: c["_t0"])["start"],
                    "last_end": max(cases, key=lambda c: c["_t1"])["end"],
                    "calendar_days": (max(c["_t1"] for c in cases).date() - min(c["_t0"] for c in cases).date()).days + 1},
         "lead_time_completed": stats(c["elapsed"] for c in done),
         "by_state": {k: stats(v.values()) for k, v in per.items()},
         "open_cases_observed_so_far": open_,
         "split_unknown": {"cases": unknown, "note": "Completed, but only start/finish known: in lead time, not in by_state."}}
    if open_:
        s["open_note"] = ("Open cases are excluded from lead time. If many are open, completed-only figures "
                          "understate the backlog — say so.")
    grand = sum(sum(v.values()) for v in per.values())
    if grand:
        s["share_of_split_time_pct"] = {k: round(100 * sum(v.values()) / grand, 1) for k, v in per.items()}
    when = {c["case"]: (c["start"], c["end"]) for c in cases}
    s["largest"] = {}
    for k, v in per.items():
        ranked = sorted(v.items(), key=lambda kv: -kv[1])[:top]
        tot = sum(v.values())
        s["largest"][k] = {
            "cases": [{"case": c, "minutes": round(m, 1), "start": when[c][0], "end": when[c][1]} for c, m in ranked],
            "their_share_pct": round(100 * sum(m for _, m in ranked) / tot, 1) if tot else 0,
            "without_them": stats(m for c, m in v.items() if c not in dict(ranked))}
    return s


def handoff_metrics(actors):
    """Who held the item, in order. A change between two known holders is a handoff.
    A blank holder is a gap: no handoff is inferred across it."""
    seq, gaps = [], 0
    for a in actors:
        if not a:
            if seq and seq[-1] is not None:
                gaps += 1
                seq.append(None)
        elif not seq or seq[-1] != a:
            seq.append(a)
    while seq and seq[-1] is None:
        seq.pop()
    pairs = [(x, y) for x, y in zip(seq, seq[1:]) if x is not None and y is not None]
    known = [a for a in seq if a is not None]
    ping = sum(1 for i in range(len(seq) - 2) if seq[i] is not None and seq[i] == seq[i + 2] and seq[i + 1] is not None)
    return {"sequence": [a if a is not None else "?" for a in seq], "handoffs": len(pairs),
            "distinct_actors": len(set(known)), "returns_to_earlier_actor": len(known) - len(set(known)),
            "ping_pong": ping, "unknown_holder_gaps": gaps}


def handoff_summary(cases):
    hs = [c["handoffs"] for c in cases]
    edges = defaultdict(int)
    for h in hs:
        for a, b in zip(h["sequence"], h["sequence"][1:]):
            if a != "?" and b != "?":
                edges[(a, b)] += 1
    n = [h["handoffs"] for h in hs]
    return {"cases": len(hs), "handoffs": {"mean": round(statistics.mean(n), 1), "median": statistics.median(n), "max": max(n)},
            "cases_with_ping_pong": sum(1 for h in hs if h["ping_pong"]),
            "cases_with_unknown_holder": sum(1 for h in hs if h["unknown_holder_gaps"]),
            "edges": [{"from": a, "to": b, "count": k} for (a, b), k in sorted(edges.items(), key=lambda e: -e[1])],
            "basis": "A handoff is a change between two known holders on consecutive rows of a case; "
                     "blank holders are gaps, not handoffs. Use roles or IDs rather than names where possible."}


def handoff_mermaid(summary):
    ids = {}
    for e in summary["edges"]:
        for k in (e["from"], e["to"]):
            ids.setdefault(k, f"n{len(ids) + 1}")
    lines = ["flowchart LR"]
    for name, nid in ids.items():
        label = name.replace('"', "'").replace("\n", " ")
        lines.append(f'  {nid}["{label}"]')
    for e in summary["edges"]:
        lines.append(f'  {ids[e["from"]]} -->|{e["count"]}| {ids[e["to"]]}')
    return "\n".join(lines)


def wide_to_events(rows, states):
    """One row per case: first column = id, then one timestamp column per boundary, in order.
    With states [queue, work] the columns mean: start of queue, start of work, done.
    A blank middle timestamp makes the split unknown (lead time only); times must not go backwards."""
    out = []
    for i, r in enumerate(rows):
        vals = list(r.values())
        case, stamps = vals[0], vals[1:]
        if len(stamps) != len(states) + 1:
            fail(f"row {i + 2} ({case}): expected {len(states) + 1} timestamp columns for states {states}")
        if not stamps[0] or not stamps[-1]:
            fail(f"row {i + 2} ({case}): first and last timestamps are required")
        known = [(j, parse_time(t, f"row {i + 2} ({case})")) for j, t in enumerate(stamps) if t]
        for (j0, t0), (j1, t1) in zip(known, known[1:]):
            if t1 < t0:
                fail(f"row {i + 2} ({case}): column {j1 + 2} is earlier than column {j0 + 2} — check the log")
        if all(stamps):
            for t, s in zip(stamps, states + ["done"]):
                out.append({"case": case, "time": t, "state": s})
        else:
            out.append({"case": case, "time": stamps[0], "state": "open"})
            out.append({"case": case, "time": stamps[-1], "state": "done"})
    return out


# ---------- cli ----------

def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
    except OSError as e:
        fail(f"cannot read {path}: {e}")
    if not rows:
        fail("CSV has no data rows")
    return rows


def expect_error(fn):
    try:
        fn()
    except InputError:
        return
    raise AssertionError("bad input accepted")


def selftest():
    m = path_metrics([{"x": "0", "y": "0"}, {"x": "0", "y": "4"}, {"x": "3", "y": "4"}], unit="m")
    assert m["total_distance_along_points"] == 7.0 and m["trips"][0]["start_to_end_straight_line"] == 5.0, m
    assert "warning" in path_metrics([{"x": "0", "y": "0"}, {"x": "3", "y": "4"}])
    t = timeline_metrics([
        {"case": "A", "time": "2026-09-24T09:00", "state": "queue"},
        {"case": "A", "time": "2026-09-24T09:50", "state": "work"},
        {"case": "A", "time": "2026-09-24T10:00", "state": "done"}])
    c = t["cases"][0]
    assert c["elapsed"] == 60 and c["by_state"] == {"queue": 50, "work": 10} and c["complete"], c
    # open case: not in lead time, reported separately
    o = timeline_metrics([
        {"case": "A", "time": "2026-09-24T09:00", "state": "queue"},
        {"case": "A", "time": "2026-09-24T10:00", "state": "done"},
        {"case": "B", "time": "2026-09-24T09:00", "state": "queue"},
        {"case": "B", "time": "2026-09-24T10:00", "state": "work"}])["summary"]
    assert o["lead_time_completed"]["n"] == 1 and o["open_cases_observed_so_far"] == {"B": 60.0}, o
    # Chinese done state is recognised
    zh = timeline_metrics([{"case": "A", "time": "2026-09-24T09:00", "state": "排队"},
                           {"case": "A", "time": "2026-09-24T10:00", "state": "完成"}])
    assert zh["cases"][0]["complete"], zh
    # wide: split unknown kept apart; inverted times rejected
    s = timeline_metrics(wide_to_events([
        {"id": "A", "sub": "2026-09-24 09:00", "start": "2026-09-24 09:50", "end": "2026-09-24 10:00"},
        {"id": "B", "sub": "2026-09-24 09:00", "start": "2026-09-24 09:20", "end": "2026-09-24 09:40"},
        {"id": "C", "sub": "2026-09-24 09:00", "start": "", "end": "2026-09-24 11:00"}], ["queue", "work"]))["summary"]
    assert s["by_state"]["queue"]["total"] == 70 and s["split_unknown"]["cases"] == {"C": 120.0}, s
    assert s["share_of_split_time_pct"] == {"queue": 70.0, "work": 30.0} and s["period"]["calendar_days"] == 1, s
    assert s["largest"]["queue"]["cases"][0]["start"] == "Thu 2026-09-24 09:00", s
    expect_error(lambda: wide_to_events([{"id": "X", "sub": "2026-09-24 10:00", "start": "2026-09-24 09:00",
                                          "end": "2026-09-24 11:00"}], ["queue", "work"]))
    expect_error(lambda: timeline_metrics([{"case": "A", "time": "not a time", "state": "queue"}]))
    expect_error(lambda: path_metrics([{"x": "nan", "y": "0"}]))
    # handoffs, incl. a blank holder that must not become an Alice -> Bob edge
    h = timeline_metrics([
        {"case": "PO1", "time": "2026-09-01T09:00", "state": "work", "actor": "Requester"},
        {"case": "PO1", "time": "2026-09-01T10:00", "state": "queue", "actor": "Buyer"},
        {"case": "PO1", "time": "2026-09-01T12:00", "state": "rework", "actor": "Requester"},
        {"case": "PO1", "time": "2026-09-01T13:00", "state": "queue", "actor": "Buyer"},
        {"case": "PO1", "time": "2026-09-01T15:00", "state": "done", "actor": "Buyer"}])
    hc = h["cases"][0]["handoffs"]
    assert hc["handoffs"] == 3 and hc["ping_pong"] == 2 and hc["distinct_actors"] == 2, hc
    g = timeline_metrics([
        {"case": "X", "time": "2026-09-01T09:00", "state": "work", "actor": "Alice"},
        {"case": "X", "time": "2026-09-01T10:00", "state": "work", "actor": ""},
        {"case": "X", "time": "2026-09-01T11:00", "state": "done", "actor": "Bob"}])
    assert g["cases"][0]["handoffs"]["handoffs"] == 0 and g["handoff_summary"]["edges"] == [], g
    mm = handoff_mermaid({"edges": [{"from": "A B", "to": "A_B", "count": 1}]})
    assert 'n1["A B"]' in mm and 'n2["A_B"]' in mm, mm
    assert "&lt;script&gt;" in path_svg([{"x": "0", "y": "0", "label": "<script>"}, {"x": "3", "y": "4"}], "t", True)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("path")
    p.add_argument("csv")
    p.add_argument("--unit", help="real-world unit of x/y, e.g. m or ft. Omit if the layout is a sketch.")
    p.add_argument("--svg", help="write a spaghetti chart SVG here")
    p.add_argument("--title", default="Spaghetti chart")
    t = sub.add_parser("timeline")
    t.add_argument("csv")
    t.add_argument("--mermaid", help="write a handoff graph (Mermaid) here; needs an actor column")
    t.add_argument("--wide", metavar="STATES",
                   help="one row per case (id, then timestamps in order); name the states between consecutive "
                        "timestamps, e.g. --wide queue,work")
    t.add_argument("--done-states", help="comma-separated states that mean the case is finished")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    try:
        rows = read_csv(a.csv)
        if a.cmd == "path":
            res = path_metrics(rows, a.unit)
            if a.svg:
                with open(a.svg, "w", encoding="utf-8") as f:
                    f.write(path_svg(rows, a.title, schematic=a.unit is None))
                res["svg"] = a.svg
        else:
            done = DONE_STATES if not a.done_states else {s.strip().lower() for s in a.done_states.split(",")}
            if a.wide:
                rows = wide_to_events(rows, [s.strip() for s in a.wide.split(",")])
            res = timeline_metrics(rows, done | {"done"})
            if a.mermaid and "handoff_summary" in res:
                with open(a.mermaid, "w", encoding="utf-8") as f:
                    f.write(handoff_mermaid(res["handoff_summary"]) + "\n")
                res["mermaid"] = a.mermaid
    except InputError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(res, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
