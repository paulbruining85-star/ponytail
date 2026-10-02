#!/usr/bin/env python3
"""Statistics for the problem-solving skill. Stdlib only — no numpy/scipy.

Every test statistic, p-value, interval, control limit and sample size the skill
reports comes from here, never from the model's own arithmetic.

  pareto    counts (or a weight such as cost) by category, sorted, with cumulative share
  ranks     rank-based comparison: Mann-Whitney (two independent groups) or,
            with --paired, Wilcoxon signed-rank (same items before/after)
  ttest     one-sample, two-sample (Welch) or paired t-test on measured data
  prop      one-proportion or two-proportion comparison (+ Fisher exact for 2x2)
  chisq     chi-square test of association on a table of counts
  anova     one-way ANOVA on measured data in groups
  chart     control chart: imr (individual values), p (defectives/sample), u (defects/unit)
  size      sample size: estimate a mean or proportion, or detect a difference in proportions
  selftest  run the built-in checks

Every output is JSON with "status": "ok" or "error". On error nothing else is
reported — the skill must say the analysis could not be run, never guess.
Decisions in `plain` are made on unrounded values; numbers are rounded for display only.
"""
import argparse
import csv
import html
import json
import math
import statistics
import sys
from statistics import NormalDist

Z = NormalDist()


class InputError(Exception):
    pass


def fail(msg):
    raise InputError(msg)


# ---------- special functions ----------

def _betacf(a, b, x):
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c; c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c; c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def gammainc_upper(s, x):
    if x <= 0:
        return 1.0
    if x < s + 1:
        term = total = 1.0 / s
        n = s
        for _ in range(5000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                return 1 - total * math.exp(-x + s * math.log(x) - math.lgamma(s))
        raise ArithmeticError("incomplete gamma series did not converge")
    tiny = 1e-300
    b = x + 1 - s
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 5000):
        an = -i * (i - s)
        b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-16:
            return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    raise ArithmeticError("incomplete gamma fraction did not converge")


def t_sf2(t, df):
    """Two-sided p-value for a t statistic."""
    return betainc(df / 2, 0.5, df / (df + t * t))


def t_ppf(q, df):
    """Quantile of the t distribution for q in (0.5, 1): bracket, then bisect."""
    if not 0.5 < q < 1:
        fail("t quantile needs 0.5 < q < 1")
    hi = 1.0
    while 1 - t_sf2(hi, df) / 2 < q:
        hi *= 2
        if hi > 1e12:
            raise ArithmeticError("t quantile out of range")
    lo = hi / 2 if hi > 1 else 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf2(mid, df) / 2 < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def chi2_sf(x, df):
    return gammainc_upper(df / 2, x / 2)


def f_sf(f, d1, d2):
    return betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


# ---------- validation ----------

def finite(values, what):
    out = []
    for v in values:
        try:
            x = float(v)
        except (TypeError, ValueError):
            fail(f"{what}: '{v}' is not a number")
        if not math.isfinite(x):
            fail(f"{what}: non-finite value '{v}'")
        out.append(x)
    return out


def count(v, what):
    try:
        x = float(v)
    except (TypeError, ValueError):
        fail(f"{what}: '{v}' is not a count")
    if not math.isfinite(x) or x < 0 or x != int(x):
        fail(f"{what}: '{v}' must be a whole number ≥ 0")
    return int(x)


def need(n, k, what):
    if n < k:
        fail(f"{what}: need at least {k} values, got {n}")


def r(v, k=4):
    return None if v is None else round(v, k)


def skewness(x):
    n, m = len(x), statistics.mean(x)
    s = statistics.pstdev(x)
    return 0.0 if s == 0 or n < 3 else sum((v - m) ** 3 for v in x) / n / s ** 3


# ---------- tests ----------

def ttest(a, b=None, mu=None, paired=False, alpha=0.05):
    """a, b are already filtered (paired: jointly by row, same items in the same order)."""
    level = int(round((1 - alpha) * 100))
    if paired:
        if b is None or len(a) != len(b):
            fail("paired t-test needs two columns with a value for every kept row")
        sample, target, kind = [x - y for x, y in zip(a, b)], 0.0, "paired"
        need(len(sample), 2, "paired t-test")
    elif b is None:
        sample, target, kind = a, (mu or 0.0), "one-sample"
        need(len(sample), 2, "one-sample t-test")
    else:
        need(len(a), 2, "group A"); need(len(b), 2, "group B")
        kind = "two-sample (Welch)"
    if kind != "two-sample (Welch)":
        n, s = len(sample), statistics.stdev(sample)
        if s == 0:
            fail("all values are identical: no variation to test")
        se, df = s / math.sqrt(n), n - 1
        diff = statistics.mean(sample) - target
        groups = [sample]
    else:
        n1, n2 = len(a), len(b)
        v1, v2 = statistics.variance(a) / n1, statistics.variance(b) / n2
        if v1 + v2 == 0:
            fail("all values are identical: no variation to test")
        se = math.sqrt(v1 + v2)
        df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1))
        diff = statistics.mean(a) - statistics.mean(b)
        groups = [a, b]
    t = diff / se
    p = t_sf2(t, df)
    q = t_ppf(1 - alpha / 2, df)
    lo, hi = diff - q * se, diff + q * se
    excl = lo > 0 or hi < 0
    out = {"status": "ok", "test": kind + " t-test", "estimand": "difference in means",
           "n": [len(g) for g in groups] if len(groups) > 1 else len(groups[0]),
           "mean": [r(statistics.mean(g)) for g in groups] if len(groups) > 1 else r(statistics.mean(groups[0])),
           "difference": r(diff), "t": r(t), "df": r(df, 2), "p_two_sided": r(p), f"ci_{level}": [r(lo), r(hi)],
           "plain": (f"Difference in means {r(diff, 3)} ({level}% interval {r(lo, 3)} to {r(hi, 3)}). "
                     + ("The interval excludes 0: chance alone is an unlikely explanation."
                        if excl else "The interval includes 0: the data cannot rule out no difference."))}
    sk = [skewness(g) for g in groups]
    out["skewness"] = [r(v, 2) for v in sk]
    if any(abs(v) > 1 for v in sk) and min(len(g) for g in groups) < 30:
        out["note"] = ("Skewed and small: the t interval may be off. If the question is about the typical value, "
                       "`ranks` answers that (use `ranks --paired` for before/after on the same items); if it is about "
                       "the average or total (e.g. total cost), the mean is still the right target — call it approximate.")
    return out


def pareto(counts):
    if not counts:
        fail("no categories")
    total = sum(counts.values())
    if total <= 0:
        fail("total is zero")
    cum, rows, top = 0.0, [], None
    for i, (k, v) in enumerate(sorted(counts.items(), key=lambda kv: -kv[1])):
        cum += v
        if top is None and cum / total >= 0.8 - 1e-12:
            top = i + 1
        rows.append({"category": k, "value": r(v, 2), "share_pct": r(100 * v / total, 1),
                     "cumulative_pct": r(100 * cum / total, 1)})
    return {"status": "ok", "total": r(total, 2), "rows": rows, "categories_to_80_pct": top,
            "plain": f"{top} of {len(rows)} categories account for at least 80% of the total "
                     f"({', '.join(rw['category'] for rw in rows[:top])})."}


def _ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks, ties, i = [0.0] * len(values), 0.0, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    return ranks, ties


def mann_whitney(a, b):
    need(len(a), 2, "group A"); need(len(b), 2, "group B")
    n1, n2 = len(a), len(b)
    ranks, ties = _ranks(a + b)
    u1 = sum(ranks[:n1]) - n1 * (n1 + 1) / 2
    n = n1 + n2
    mu = n1 * n2 / 2
    sigma = math.sqrt(max(0.0, n1 * n2 / 12 * ((n + 1) - ties / (n * (n - 1)))))
    z = 0.0 if sigma == 0 or u1 == mu else (u1 - mu - math.copysign(0.5, u1 - mu)) / sigma
    pv = 2 * (1 - Z.cdf(abs(z)))
    gt = sum(1 for x in a for y in b if x > y) / (n1 * n2)
    eq = sum(1 for x in a for y in b if x == y) / (n1 * n2)
    out = {"status": "ok", "test": "Mann-Whitney rank-sum (independent groups, normal approx.)",
           "estimand": "whether values in A tend to be larger than in B — not a difference in means",
           "n": [n1, n2], "median": [r(statistics.median(a)), r(statistics.median(b))], "U": r(u1, 1), "z": r(z),
           "p_two_sided": r(pv), "share_pairs_a_greater": r(gt, 3), "share_pairs_tied": r(eq, 3),
           "interval": "not computed",
           "plain": (f"Medians {r(statistics.median(a), 3)} vs {r(statistics.median(b), 3)}. In {r(gt * 100, 1)}% of "
                     f"A-B pairs the A value is larger ({r(eq * 100, 1)}% tied). "
                     + ("A consistent difference." if pv < 0.05 else "Not a consistent difference on this data."))}
    if min(n1, n2) < 8:
        out["warning"] = "Fewer than 8 in a group: the normal approximation is rough."
    return out


def wilcoxon_signed(a, b):
    """Paired rank test on differences (zeros dropped); normal approx. with tie and continuity correction."""
    d = [x - y for x, y in zip(a, b) if x != y]
    need(len(d), 2, "non-zero paired differences")
    ranks, ties = _ranks([abs(v) for v in d])
    wplus = sum(rk for rk, v in zip(ranks, d) if v > 0)
    n = len(d)
    mu = n * (n + 1) / 4
    sigma = math.sqrt(max(0.0, n * (n + 1) * (2 * n + 1) / 24 - ties / 48))
    z = 0.0 if sigma == 0 or wplus == mu else (wplus - mu - math.copysign(0.5, wplus - mu)) / sigma
    pv = 2 * (1 - Z.cdf(abs(z)))
    med = statistics.median([x - y for x, y in zip(a, b)])
    out = {"status": "ok", "test": "Wilcoxon signed-rank (paired, normal approx.)",
           "estimand": "whether paired differences tend to be positive or negative",
           "pairs": len(a), "zero_differences_dropped": len(a) - n, "median_difference": r(med),
           "W_plus": r(wplus, 1), "z": r(z), "p_two_sided": r(pv), "interval": "not computed",
           "plain": f"Median paired difference {r(med, 3)}. "
                    + ("A consistent shift." if pv < 0.05 else "Not a consistent shift on this data.")}
    if n < 10:
        out["warning"] = "Fewer than 10 non-zero differences: the normal approximation is rough."
    return out


def fisher_2x2(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d

    def lpmf(x):
        return (math.lgamma(r1 + 1) + math.lgamma(n - r1 + 1) + math.lgamma(c1 + 1) + math.lgamma(n - c1 + 1)
                - math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(r1 - x + 1)
                - math.lgamma(c1 - x + 1) - math.lgamma(n - r1 - c1 + x + 1))
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    l0 = lpmf(a)
    return min(1.0, sum(math.exp(lpmf(x)) for x in range(lo, hi + 1) if lpmf(x) <= l0 + 1e-7))


def wilson(x, n, z=1.959964):
    p = x / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def newcombe(x1, n1, x2, n2):
    """Newcombe (1998) hybrid score interval for p1 - p2, built from Wilson intervals."""
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1)
    l2, u2 = wilson(x2, n2)
    d = p1 - p2
    return d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def prop_test(x1, n1, x2=None, n2=None, p0=None):
    x1, n1 = count(x1, "x1"), count(n1, "n1")
    if n1 == 0 or x1 > n1:
        fail("need 0 ≤ x1 ≤ n1 and n1 > 0")
    if x2 is None:
        if p0 is None or not 0 < p0 < 1:
            fail("one-proportion test needs 0 < p0 < 1")
        p = x1 / n1
        z = (p - p0) / math.sqrt(p0 * (1 - p0) / n1)
        pv = 2 * (1 - Z.cdf(abs(z)))
        lo, hi = wilson(x1, n1)
        out = {"status": "ok", "test": "one-proportion z-test", "p_hat": r(p), "p0": p0, "z": r(z), "p_two_sided": r(pv),
               "ci_95_wilson": [r(lo), r(hi)],
               "plain": f"Observed {r(p * 100, 2)}% (95% interval {r(lo * 100, 2)}% to {r(hi * 100, 2)}%) against {p0 * 100}%."}
        if n1 * p0 < 5 or n1 * (1 - p0) < 5:
            out["warning"] = "Expected counts below 5: the z-test is unreliable; rely on the Wilson interval."
        return out
    x2, n2 = count(x2, "x2"), count(n2, "n2")
    if n2 == 0 or x2 > n2:
        fail("need 0 ≤ x2 ≤ n2 and n2 > 0")
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se0 if se0 else 0.0
    pz = 2 * (1 - Z.cdf(abs(z))) if se0 else 1.0
    pf = fisher_2x2(x1, n1 - x1, x2, n2 - x2)
    lo, hi = newcombe(x1, n1, x2, n2)
    sparse = min(x1, x2, n1 - x1, n2 - x2) < 5
    decide_p = pf if sparse else pz
    out = {"status": "ok", "test": "two-proportion comparison", "p1": r(p1), "p2": r(p2), "difference": r(p1 - p2),
           "ci_95_difference_newcombe": [r(lo), r(hi)], "z": r(z), "p_two_sided_z": r(pz), "fisher_exact_p": r(pf),
           "decision_based_on": "fisher_exact_p" if sparse else "p_two_sided_z", "n": [n1, n2]}
    if x1 == x2 == 0 or (x1 == n1 and x2 == n2):
        out["warning"] = "No events (or all events) in both groups: the data say little about a difference yet."
    elif sparse:
        out["warning"] = "Some counts below 5: the conclusion uses Fisher's exact test, not the z-test."
    out["plain"] = (f"{r(p1 * 100, 2)}% vs {r(p2 * 100, 2)}%, difference {r((p1 - p2) * 100, 2)} points "
                    f"(95% interval {r(lo * 100, 2)} to {r(hi * 100, 2)}). "
                    + ("The difference is unlikely to be chance alone." if decide_p < 0.05
                       else "The data cannot rule out no difference."))
    return out


def chisq(table, row_labels, col_labels):
    table = [[count(v, "table cell") for v in rw] for rw in table]
    keep_r = [i for i, rw in enumerate(table) if sum(rw) > 0]
    keep_c = [j for j in range(len(table[0])) if sum(rw[j] for rw in table) > 0]
    dropped = {"rows": [row_labels[i] for i in range(len(table)) if i not in keep_r],
               "columns": [col_labels[j] for j in range(len(table[0])) if j not in keep_c]}
    t = [[table[i][j] for j in keep_c] for i in keep_r]
    if len(t) < 2 or len(keep_c) < 2:
        fail("need at least 2 non-empty rows and 2 non-empty columns")
    rows, cols = len(t), len(keep_c)
    rt = [sum(rw) for rw in t]
    ct = [sum(t[i][j] for i in range(rows)) for j in range(cols)]
    n = sum(rt)
    exp = [[rt[i] * ct[j] / n for j in range(cols)] for i in range(rows)]
    x2 = sum((t[i][j] - exp[i][j]) ** 2 / exp[i][j] for i in range(rows) for j in range(cols))
    df = (rows - 1) * (cols - 1)
    p = chi2_sf(x2, df)
    out = {"status": "ok", "test": "chi-square test of association", "chi2": r(x2), "df": df, "p": r(p), "n": n,
           "expected": [[r(v, 2) for v in rw] for rw in exp], "dropped_empty": dropped,
           "plain": ("The pattern of counts differs between groups more than chance would usually produce."
                     if p < 0.05 else "The counts are consistent with no association between the two classifications.")}
    small = sum(1 for rw in exp for v in rw if v < 5)
    if small:
        out["warning"] = f"{small} expected counts below 5: unreliable; combine categories or collect more data."
    return out


def anova(groups):
    names = [g for g in groups if groups[g]]
    if len(names) < 2:
        fail("need at least 2 groups")
    for g in names:
        need(len(groups[g]), 2, f"group {g}")
    allv = [v for g in names for v in groups[g]]
    grand = statistics.mean(allv)
    ssb = sum(len(groups[g]) * (statistics.mean(groups[g]) - grand) ** 2 for g in names)
    ssw = sum((v - statistics.mean(groups[g])) ** 2 for g in names for v in groups[g])
    if ssw == 0:
        fail("no variation within groups")
    d1, d2 = len(names) - 1, len(allv) - len(names)
    f = (ssb / d1) / (ssw / d2)
    p = f_sf(f, d1, d2)
    return {"status": "ok", "test": "one-way ANOVA",
            "groups": {g: {"n": len(groups[g]), "mean": r(statistics.mean(groups[g])),
                           "sd": r(statistics.stdev(groups[g]))} for g in names},
            "F": r(f), "df": [d1, d2], "p": r(p),
            "note": "Assumes independent observations and similar spread per group; says only that some mean "
                    "differs, not which.",
            "plain": ("At least one group mean differs." if p < 0.05 else "The data are consistent with equal group means.")}


# ---------- control charts ----------

def run_rules(values, centre, sigma, rules):
    """Nelson rules 1-4; each hit is reported at the point that completes the pattern."""
    hits, n = {}, len(values)
    if 1 in rules:
        hits["1_beyond_3_sigma"] = [i for i, v in enumerate(values) if sigma[i] and abs(v - centre[i]) > 3 * sigma[i]]
    if 2 in rules:
        side = [0 if v == c else (1 if v > c else -1) for v, c in zip(values, centre)]
        hits["2_nine_same_side"] = [i for i in range(8, n) if abs(sum(side[i - 8:i + 1])) == 9]
    if 3 in rules:
        hits["3_six_trending"] = [i for i in range(5, n)
                                  if all(values[k] < values[k + 1] for k in range(i - 5, i))
                                  or all(values[k] > values[k + 1] for k in range(i - 5, i))]
    if 4 in rules:
        idx = []
        for i in range(13, n):
            dd = [values[k + 1] - values[k] for k in range(i - 13, i)]
            if all(dd[k] * dd[k + 1] < 0 for k in range(12)):
                idx.append(i)
        hits["4_fourteen_alternating"] = idx
    return hits


def chart(kind, rows, rules=(1, 2)):
    if not rows:
        fail("no data rows")
    labels = [rw.get("label") or str(i + 1) for i, rw in enumerate(rows)]
    extra = {}
    if kind == "imr":
        x = finite([rw.get("value") for rw in rows], "value")
        need(len(x), 3, "individuals chart")
        mr = [abs(b - a) for a, b in zip(x, x[1:])]
        mrbar = statistics.mean(mr)
        if mrbar == 0:
            fail("no point-to-point variation: limits cannot be set")
        sigma = mrbar / 1.128
        c = statistics.mean(x)
        pts, cl, sg = x, [c] * len(x), [sigma] * len(x)
        ucl, lcl = [c + 3 * sigma] * len(x), [c - 3 * sigma] * len(x)
        mr_ucl = 3.267 * mrbar
        limits = {"centre": r(c), "ucl": r(ucl[0]), "lcl": r(lcl[0]), "mr_bar": r(mrbar), "mr_ucl": r(mr_ucl)}
        extra["mr_beyond_ucl"] = [labels[i + 1] for i, v in enumerate(mr) if v > mr_ucl]
        basis = "Individuals chart: sigma = average moving range / 1.128; moving-range chart UCL = 3.267 × average MR."
    elif kind in ("p", "u"):
        cnt = [count(rw.get("count"), "count") for rw in rows]
        n = finite([rw.get("n") for rw in rows], "n")
        if any(m <= 0 for m in n):
            fail("every n must be > 0")
        if kind == "p" and any(c > m for c, m in zip(cnt, n)):
            fail("p chart: count cannot exceed n (defective items out of items inspected)")
        pbar = sum(cnt) / sum(n)
        if pbar == 0:
            fail("no defects at all: limits cannot be set")
        pts = [c / m for c, m in zip(cnt, n)]
        cl = [pbar] * len(pts)
        sg = [math.sqrt(pbar * (1 - pbar) / m) if kind == "p" else math.sqrt(pbar / m) for m in n]
        ucl = [pbar + 3 * s for s in sg]
        if kind == "p":
            ucl = [min(1.0, u) for u in ucl]
        lcl = [max(0.0, pbar - 3 * s) for s in sg]
        limits = {"centre": r(pbar), "ucl_by_point": [r(u) for u in ucl], "lcl_by_point": [r(v) for v in lcl]}
        basis = ("p chart: proportion defective per sample; limits vary with sample size, clipped to [0, 1]."
                 if kind == "p" else "u chart: defects per unit; limits vary with units, clipped at 0.")
    else:
        fail("chart kind must be imr, p or u")
    hits = run_rules(pts, cl, sg, set(rules))
    signals = {k: [labels[i] for i in v] for k, v in hits.items()}
    signals.update(extra)
    flagged = sorted({lab for v in signals.values() for lab in v}, key=labels.index)
    out = {"status": "ok", "chart": kind, "points": len(pts), "limits": limits, "rules_checked": sorted(rules),
           "signals": signals, "basis": basis,
           "limits_are": "exploratory — computed from these same data; freeze a baseline before monitoring new data",
           "not_a_spec": "Control limits describe what the process does, not what the customer needs. A stable "
                         "process can still miss the requirement — compare the level with the target or SLA."}
    if len(pts) < 20:
        out["warning"] = f"Only {len(pts)} points: limits are rough; 20-25 points is the usual minimum."
    out["plain"] = (f"Signal at: {', '.join(flagged)}." if flagged
                    else "No signal on the rules checked: the variation looks routine for this process. "
                         "That says nothing about whether the level is acceptable.")
    return out, pts, cl, ucl, lcl, labels


def chart_svg(pts, cl, ucl, lcl, labels, title):
    w, h, pad = 700, 320, 50
    lo, hi = min(pts + lcl), max(pts + ucl)
    span = (hi - lo) or 1
    X = lambda i: pad + i * (w - 2 * pad) / max(1, len(pts) - 1)
    Y = lambda v: h - pad - (v - lo) * (h - 2 * pad) / span
    line = lambda vals, col, dash="": ('<polyline fill="none" stroke="%s" stroke-width="1.5" %s points="%s"/>'
                                       % (col, f'stroke-dasharray="{dash}"' if dash else "",
                                          " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="sans-serif" font-size="11">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{pad}" y="20" font-size="13">{html.escape(title)}</text>',
             line(ucl, "#d1242f", "5,4"), line(lcl, "#d1242f", "5,4"), line(cl, "#1a7f37", "2,3"), line(pts, "#1f6feb")]
    for i, v in enumerate(pts):
        out = v > ucl[i] or v < lcl[i]
        parts.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{"#d1242f" if out else "#1f6feb"}">'
                     f'<title>{html.escape(labels[i])}</title></circle>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---------- sample size ----------

def size(kind, margin=None, sd=None, p=None, p1=None, p2=None, alpha=0.05, power=0.8):
    za = Z.inv_cdf(1 - alpha / 2)
    if kind == "mean":
        if not (sd and sd > 0 and margin and margin > 0):
            fail("mean: need sd > 0 (from past data or a pilot) and margin > 0")
        n = math.ceil((za * sd / margin) ** 2)
        basis = "n = (z × sd / margin)^2 (NIST e-Handbook 7.2.2.2); only as good as the sd estimate."
    elif kind == "proportion":
        if p is None or not 0 < p < 1 or not (margin and 0 < margin < 1):
            fail("proportion: need 0 < p < 1 (use 0.5 if unknown; a pilot with 0 events does not mean p = 0) "
                 "and 0 < margin < 1")
        n = math.ceil(za ** 2 * p * (1 - p) / margin ** 2)
        basis = "n = z^2 p(1-p) / margin^2 — a planning approximation."
    elif kind == "two-proportions":
        if p1 is None or p2 is None or not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
            fail("two-proportions: need 0 < p1, p2 < 1 and p1 ≠ p2")
        zb = Z.inv_cdf(power)
        pbar = (p1 + p2) / 2
        n = math.ceil((za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
                      / (p1 - p2) ** 2)
        basis = f"Per group, equal sizes, independent samples: {p1} vs {p2}, alpha {alpha} two-sided, power {power}."
    else:
        fail("kind must be mean, proportion or two-proportions")
    return {"status": "ok", "sample_size": n, "per_group": kind == "two-proportions", "basis": basis}


# ---------- cli ----------

def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in rw.items()} for rw in csv.DictReader(f)]
    except OSError as e:
        fail(f"cannot read {path}: {e}")
    if not rows:
        fail("CSV has no data rows")
    return rows


def paired_columns(rows, a, b, id_col=None):
    """Keep only rows where BOTH values exist; report what was dropped. Never pair across rows."""
    keep, dropped = [], []
    for i, rw in enumerate(rows):
        rid = rw.get(id_col) if id_col else f"row {i + 2}"
        if rw.get(a, "") == "" or rw.get(b, "") == "":
            dropped.append(rid)
        else:
            keep.append((rid, rw[a], rw[b]))
    return finite([k[1] for k in keep], a), finite([k[2] for k in keep], b), [k[0] for k in keep], dropped


def selftest():
    close = lambda a, b, tol=1e-3: abs(a - b) < tol
    assert close(t_sf2(2.228139, 10), 0.05) and close(t_ppf(0.975, 10), 2.228139)
    assert close(t_ppf(0.9999, 1), 3183.0988, 0.01), t_ppf(0.9999, 1)
    assert close(chi2_sf(3.841459, 1), 0.05) and close(chi2_sf(18.307038, 10), 0.05)
    assert close(f_sf(4.964603, 1, 10), 0.05)
    assert close(fisher_2x2(3, 1, 1, 3), 0.485714)
    # paired: never pair across rows (review counter-example: true answer 3 pairs, mean diff +2)
    rows = [{"a": "10", "b": "9"}, {"a": "20", "b": ""}, {"a": "", "b": "90"}, {"a": "40", "b": "38"}, {"a": "50", "b": "47"}]
    xa, xb, kept, dropped = paired_columns(rows, "a", "b")
    pt = ttest(xa, xb, paired=True)
    assert pt["n"] == 3 and close(pt["difference"], 2.0) and dropped == ["row 3", "row 4"], (pt, dropped)
    # rounding must not flip the decision when units change
    big, tiny = ttest([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]), ttest([1e-6, 2e-6, 3e-6], [4e-6, 5e-6, 6e-6])
    assert ("excludes" in big["plain"]) == ("excludes" in tiny["plain"]), (big["plain"], tiny["plain"])
    # sparse proportions: conclusion follows Fisher; zero events give a real interval
    sp = prop_test(0, 10, 4, 10)
    assert sp["decision_based_on"] == "fisher_exact_p" and "cannot rule out" in sp["plain"], sp
    zz = prop_test(0, 10, 0, 10)
    lo, hi = zz["ci_95_difference_newcombe"]
    assert lo < 0 < hi and "warning" in zz, zz
    nl, nh = newcombe(56, 70, 48, 80)  # Newcombe (1998) worked example: 0.0524 to 0.3339
    assert close(nl, 0.0524, 2e-3) and close(nh, 0.3339, 2e-3), (nl, nh)
    # I-MR: a moving-range jump must signal even when every point is inside the I limits
    series = [10, 10.5] * 4 + [13, 10.5] + [10, 10.5] * 4
    o = chart("imr", [{"value": v} for v in series])[0]
    assert o["signals"]["mr_beyond_ucl"] and o["plain"].startswith("Signal"), o
    o = chart("imr", [{"value": v} for v in [10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 25]])[0]
    assert o["signals"]["1_beyond_3_sigma"] == ["12"], o
    assert chart("imr", [{"value": v} for v in [1, 0] * 6 + [5] * 9], rules=(2,))[0]["signals"]["2_nine_same_side"]
    # impossible inputs must fail, never succeed
    for bad in (lambda: chart("imr", [{"value": "1"}, {"value": "nan"}, {"value": "2"}]),
                lambda: chisq([[1, -2], [3, 4]], ["r1", "r2"], ["c1", "c2"]),
                lambda: size("proportion", p=0.0, margin=0.05),
                lambda: prop_test(5, 4, 1, 10),
                lambda: chart("p", [{"count": 5, "n": 3}])):
        try:
            bad()
            raise AssertionError("bad input accepted")
        except InputError:
            pass
    # chi-square: an empty column is dropped, not counted in df
    cq = chisq([[10, 0, 20], [20, 0, 10]], ["a", "b"], ["x", "empty", "y"])
    assert cq["df"] == 1 and cq["dropped_empty"]["columns"] == ["empty"] and close(cq["chi2"], 6.6667), cq
    # Pareto threshold on the raw cumulative share (79.96% is not 80%)
    assert pareto({"a": 7996, "b": 3, "c": 2001})["categories_to_80_pct"] == 2
    # Mann-Whitney: all tied -> 0% strictly greater, 100% tied, p = 1
    mw = mann_whitney([1, 1, 1], [1, 1, 1])
    assert mw["share_pairs_a_greater"] == 0 and mw["share_pairs_tied"] == 1 and mw["p_two_sided"] == 1.0
    mw = mann_whitney([6, 7, 8, 9, 10], [1, 2, 3, 4, 5])
    assert mw["U"] == 25 and close(mw["p_two_sided"], 0.0122, 2e-3)
    ws = wilcoxon_signed([5, 6, 7, 8, 9, 10, 11, 12], [1, 2, 3, 4, 5, 6, 7, 8])
    assert ws["median_difference"] == 4 and ws["W_plus"] == 36, ws
    assert size("mean", margin=2, sd=10)["sample_size"] == 97
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("pareto", help="CSV: category[,<weight>] — one row per occurrence, or a count/cost column")
    pa.add_argument("csv"); pa.add_argument("--weight", default="count", help="numeric column to sum, e.g. count or cost")
    rk = sub.add_parser("ranks", help="independent: CSV group,value (two groups) · paired: --paired --a COL --b COL")
    rk.add_argument("csv"); rk.add_argument("--paired", action="store_true")
    rk.add_argument("--a"); rk.add_argument("--b"); rk.add_argument("--id")
    t = sub.add_parser("ttest", help="CSV with one or two numeric columns")
    t.add_argument("csv"); t.add_argument("--a", required=True); t.add_argument("--b")
    t.add_argument("--mu", type=float); t.add_argument("--paired", action="store_true"); t.add_argument("--id")
    pr = sub.add_parser("prop", help="counts: --x1 --n1 [--x2 --n2 | --p0]")
    for k in ("x1", "n1", "x2", "n2"):
        pr.add_argument(f"--{k}")
    pr.add_argument("--p0", type=float)
    c = sub.add_parser("chisq", help="CSV table: first column = row label, other columns = category counts")
    c.add_argument("csv")
    a = sub.add_parser("anova", help="CSV with columns group,value")
    a.add_argument("csv")
    ch = sub.add_parser("chart", help="imr: label,value · p: label,count,n · u: label,count,n")
    ch.add_argument("kind", choices=["imr", "p", "u"]); ch.add_argument("csv")
    ch.add_argument("--rules", default="1,2"); ch.add_argument("--svg"); ch.add_argument("--title", default="Control chart")
    s = sub.add_parser("size")
    s.add_argument("kind", choices=["mean", "proportion", "two-proportions"])
    for k in ("margin", "sd", "p", "p1", "p2"):
        s.add_argument(f"--{k}", type=float)
    s.add_argument("--power", type=float, default=0.8)
    sub.add_parser("selftest")
    x = ap.parse_args()
    if x.cmd == "selftest":
        return selftest()
    try:
        if x.cmd == "pareto":
            counts = {}
            for rw in read_csv(x.csv):
                cat = rw.get("category", "")
                if cat == "":
                    fail("every row needs a category")
                w = finite([rw[x.weight]], x.weight)[0] if rw.get(x.weight, "") != "" else 1.0
                if w < 0:
                    fail(f"{x.weight} must not be negative")
                counts[cat] = counts.get(cat, 0) + w
            res = pareto(counts)
            res["measure"] = x.weight
        elif x.cmd == "ranks":
            rows = read_csv(x.csv)
            if x.paired:
                if not (x.a and x.b):
                    fail("--paired needs --a and --b columns")
                xa, xb, kept, dropped = paired_columns(rows, x.a, x.b, x.id)
                res = wilcoxon_signed(xa, xb)
                res["rows_dropped_incomplete"] = dropped
            else:
                groups = {}
                for rw in rows:
                    if rw.get("value", "") != "":
                        groups.setdefault(rw.get("group", ""), []).append(finite([rw["value"]], "value")[0])
                if rows and not {"group", "value"} <= set(rows[0]):
                    fail(f"independent ranks needs columns group,value; got {','.join(rows[0])}")
                if len(groups) != 2:
                    fail(f"independent ranks needs exactly two groups, got {len(groups)}")
                (ga, a_), (gb, b_) = groups.items()
                res = mann_whitney(a_, b_)
                res["groups"] = [ga, gb]
        elif x.cmd == "ttest":
            rows = read_csv(x.csv)
            if x.paired:
                if not x.b:
                    fail("--paired needs --b")
                xa, xb, kept, dropped = paired_columns(rows, x.a, x.b, x.id)
                res = ttest(xa, xb, paired=True)
                res["rows_dropped_incomplete"] = dropped
            else:
                xa = finite([rw[x.a] for rw in rows if rw.get(x.a, "") != ""], x.a)
                xb = finite([rw[x.b] for rw in rows if rw.get(x.b, "") != ""], x.b) if x.b else None
                res = ttest(xa, xb, x.mu)
        elif x.cmd == "prop":
            if x.x1 is None or x.n1 is None:
                fail("give --x1 and --n1")
            if x.x2 is None and x.p0 is None:
                fail("give --x2 --n2 for two proportions, or --p0 for one")
            res = prop_test(x.x1, x.n1, x.x2, x.n2, x.p0)
        elif x.cmd == "chisq":
            rows = read_csv(x.csv)
            keys = list(rows[0])[1:]
            res = chisq([[rw[k] for k in keys] for rw in rows], [list(rw.values())[0] for rw in rows], keys)
        elif x.cmd == "anova":
            groups = {}
            for rw in read_csv(x.csv):
                if rw.get("value", "") != "":
                    groups.setdefault(rw.get("group", ""), []).append(finite([rw["value"]], "value")[0])
            res = anova(groups)
        elif x.cmd == "chart":
            try:
                rules = tuple(int(v) for v in x.rules.split(","))
            except ValueError:
                fail("--rules like 1,2")
            res, pts, cl, ucl, lcl, labels = chart(x.kind, read_csv(x.csv), rules)
            if x.svg:
                with open(x.svg, "w", encoding="utf-8") as f:
                    f.write(chart_svg(pts, cl, ucl, lcl, labels, x.title))
                res["svg"] = x.svg
        else:
            res = size(x.kind, x.margin, x.sd, x.p, x.p1, x.p2, power=x.power)
    except (InputError, ArithmeticError) as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(res, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
