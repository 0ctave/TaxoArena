"""REF-QUAL-GATE3-COND (Block 1, zero calls) — correctness-conditional agreement on the Kimi JSON cache.

Registered by reference (docs/plan_2026-09-15.md) to docs/design/FRAMEWORK.md at commit 8d77f7b, item 12:

    12. REF-QUAL-GATE3-COND. Correctness-conditional agreement on the Kimi JSON cache per frontier contestant.
        Registered readout; prediction: gemini's +0.071 marginal gain falls inside the incumbents' spread on
        the both-wrong stratum. 0 calls.

The record it reads (judge_v2_program.md, REF-QUAL-KIMI-JSON, ledger v100): gate (3) as registered is marginal
answer-agreement, and it FAILED at +0.071 on gemini (0.858 with the candidate against 0.787 with the incumbent;
arx +0.027, iask +0.016, gpt-4o +0.004). The record's (c) proposes comparing agreement CONDITIONAL on
correctness — among questions both get right vs both get wrong — to separate "agrees because right" from
"agrees because correlated". FRAMEWORK L189 states the form: the contestant's answer-agreement with the
reference among questions both get wrong and among questions both get right, against the incumbents'
distribution.

WHAT IS COMPUTED. On a single-key multiple-choice item, both-right agreement is 1 and mixed-stratum agreement
is 0 by construction, so the marginal agreement decomposes exactly as
        A(c, r) = P(both right) + P(both wrong) * a_bw(c, r)
and the only non-trivial conditional quantity is a_bw: the share of questions BOTH the contestant c and the
reference r get wrong on which they pick the SAME wrong option. The +0.071 marginal gain (Kimi minus grok)
splits into an accuracy-coupling term (the change in the both-right share) and a both-wrong term.

TWO READINGS OF "the both-wrong stratum" — the item is under-specified here and both are printed.
    PER-REFERENCE (the record's literal wording): a_bw(c, Kimi) is read on {c wrong, Kimi wrong} and
        a_bw(c, grok) on {c wrong, grok wrong}; these are DIFFERENT question sets (Kimi is more accurate, so its
        wrong set is smaller and harder), and the gain a_bw(c, Kimi) - a_bw(c, grok) still carries a composition
        term: harder questions have fewer live distractors, so wrong answerers agree more on them.
    COMMON (paired): both a_bw are read on the same questions {c wrong, Kimi wrong, grok wrong}; the gain is
        then a paired difference on identical items, with an exact McNemar count (b = c agrees with Kimi only,
        c = c agrees with grok only) attached. This is the reading that isolates "agrees because correlated"
        from "agrees because right", which is what the record's (c) asks the conditional form to do.
    The instruction for this block is to take the reading hardest on the programme's own claim (the prediction)
    and say so. The COMMON reading is harder: the composition term that inflates the per-reference gain for the
    most accurate contestant is removed. PRIMARY = GAIN on the COMMON stratum against the FRONTIER-3 spread.
    DISCLOSURE: the first draft of this script (on disk before this run) declared the PER-REFERENCE gain
    against FRONTIER-3 as primary before reading any number; the COMMON reading was added on this run after
    both sets of numbers had been seen, under the block's hardest-reading rule. Both readings are scored below
    and the point-check label differs between them; the verdict at support does not.

STATISTICS AND SPREADS. "Incumbents" is read as the existing roster contestants (FRAMEWORK L189's usage); gemini
is the flagged contestant and the other eleven are the incumbents.
    statistic  GAIN-PR   = a_bw(c, Kimi) - a_bw(c, grok), per-reference strata
    statistic  GAIN-COM  = a_bw(c, Kimi) - a_bw(c, grok), common stratum          <- PRIMARY statistic
    statistic  LEVEL     = a_bw(c, Kimi), per-reference stratum (sensitivity; not the item's statistic)
    spread     FRONTIER-3 = [min, max] over arx, iask, gpt-4o (narrowest; the item says "per frontier contestant")
    spread     ROSTER-11  = [min, max] over the other eleven contestants (FRAMEWORK L189's literal reading)
The item registers a readout and one prediction, no bar: each verdict row scores the PREDICTION on that reading.

POPULATION OF RECORD. experiment_results/judge_solve/refqual_Kimi_K2_6_json_mt32768.db, the 523 answers with
finish_reason 'stop' (a truncated answer is not an answer and cannot agree with anything); this is the
population on which the record's +0.071 / +0.027 / +0.016 / +0.004 reproduce exactly. Sensitivity: all 552
answered questions with the 29 truncations scored as wrong-and-disagreeing (the record's gate-(1)
truncation-as-wrong reading; marginal gain on gemini +0.051 there; a degenerate reading of agreement, since a
non-answer agrees with nothing by construction). Contestant answers are eval_results.pred (rubric_p8.ARENA12,
twelve models; Meta-Llama-3-70B-Instruct is not in the roster and is asserted absent); incumbent answers are
judge_solve/grok-reasoning.db through rejudge_reference.references(). Paired denominator per contestant:
questions with a Kimi answer, a grok answer and a contestant prediction.

KEY DENOMINATOR AND THE McNEMAR RULE. Every question is in pool p2dca21ab5f4ef3ae and keyed (gt from
eval_results); the stratum labels are key correctness, not judge directions. No wrong-direction count is
scored by this test, so the McNemar-established rule (systematic_budget.mcnemar_edge / established on the
anchor's judged questions) is vacuous here and is stated as such. The paired exact McNemar printed on the
COMMON stratum is the same exact binomial test (rejudge_reference.mcnemar_p), applied to agreement flips, not
to key directions.

UNCERTAINTY. Question bootstrap, B = 2000, Random(42), over the population of record: percentile intervals
for gemini's GAIN-PR, GAIN-COM and LEVEL, for gemini minus the FRONTIER-3 mean, and the share of replicates in
which gemini lies inside each spread. The both-wrong stratum for gemini holds ~50 questions (44 common); the
intervals are wide and are printed so that no reading is called on a point estimate alone.

    python tools/analysis/refqual_gate3_cond.py
Output: experiment_results/x12_crossdomain/refqual_gate3_cond.txt. Zero LLM calls; no DB is written.
"""
import os, sys, sqlite3, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
import ref_qualify as rq
import rejudge_reference as rref
import rubric_p8 as p8

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refqual_gate3_cond.txt")
CANDIDATE = "Kimi-K2.6"
FRONTIER = ("gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06")
FLAGGED = "gemini-3.1-pro_5-shots"
OTHER_FRONTIER = tuple(m for m in FRONTIER if m != FLAGGED)
B_BOOT = 2000
SEED = 42
STATS = ("GAIN-COM", "GAIN-PR", "LEVEL")
SPREADS = (("FRONTIER-3", OTHER_FRONTIER), ("ROSTER-11", None))
PRIMARY = ("GAIN-COM", "FRONTIER-3")
L = []


def say(s=""):
    print(s); L.append(s)


def load():
    rq.PROTOCOL = "json"; rq.MAXTOK = 32768
    pool, K, P, META, disc, weak, anchor_of, route = rq.population()
    path = rq.cache_path(CANDIDATE)
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    rows = con.execute("SELECT question_id, answer, gt, finish FROM answers").fetchall()
    con.close()
    kimi_all = {q: ((a or "").strip().upper()[:1], (g or "").strip().upper()[:1], f) for q, a, g, f in rows}
    assert all(q in pool for q in kimi_all), "a cache question is outside the pool of record"
    assert all(kimi_all[q][1] == META[q][2] for q in kimi_all if q in META), "cache gt disagrees with eval_results"
    assert all((a != "") == (f == "stop") for a, g, f in kimi_all.values()), "parsed/terminated mismatch in the cache"
    rref.set_reference("grok-reasoning"); inc = rref.references()
    grok = {q: v[0] for q, v in inc.items()}
    roster = list(p8.ARENA12)
    assert "Meta-Llama-3-70B-Instruct" not in roster and len(roster) == 12
    return path, kimi_all, grok, P, META, roster, disc, weak


def stats(qs, kimi, grok, P, META, roster):
    """Per contestant: per-reference marginal/both-right/both-wrong statistics for each reference, plus the
    COMMON both-wrong stratum (c wrong, Kimi wrong, grok wrong) with its paired agreement counts."""
    out = {}
    for c in roster:
        acc = {r: dict(n=0, agree=0, nbr=0, nbw=0, agree_bw=0) for r in ("kimi", "grok")}
        ncom = ak = ag = b = cc = 0
        for q in qs:
            cp = P[q].get(c, "")
            if not cp or q not in kimi or q not in grok: continue   # paired denominator
            gt = META[q][2]; cr = cp == gt
            for rname, ra in (("kimi", kimi[q]), ("grok", grok[q])):
                d = acc[rname]; d["n"] += 1
                rr_ = ra == gt
                if cp == ra: d["agree"] += 1
                if cr and rr_: d["nbr"] += 1
                elif (not cr) and (not rr_):
                    d["nbw"] += 1
                    if cp == ra: d["agree_bw"] += 1
            if (not cr) and kimi[q] != gt and grok[q] != gt:
                ncom += 1
                k_ = cp == kimi[q]; g_ = cp == grok[q]
                ak += k_; ag += g_; b += (k_ and not g_); cc += (g_ and not k_)
        for rname, d in acc.items():
            n = d["n"]
            out[(c, rname)] = dict(n=n, A=d["agree"] / n if n else float("nan"), pbr=d["nbr"] / n if n else float("nan"),
                                   nbw=d["nbw"], pbw=d["nbw"] / n if n else float("nan"),
                                   abw=d["agree_bw"] / d["nbw"] if d["nbw"] else float("nan"), agree_bw=d["agree_bw"])
        out[(c, "com")] = dict(n=ncom, ak=ak, ag=ag, b=b, c=cc,
                               abw_k=ak / ncom if ncom else float("nan"), abw_g=ag / ncom if ncom else float("nan"),
                               gain=(ak - ag) / ncom if ncom else float("nan"))
    return out


def stat_value(S, c, name):
    if name == "GAIN-PR": return S[(c, "kimi")]["abw"] - S[(c, "grok")]["abw"]
    if name == "GAIN-COM": return S[(c, "com")]["gain"]
    if name == "LEVEL": return S[(c, "kimi")]["abw"]
    raise KeyError(name)


def inside(x, vals):
    return min(vals) <= x <= max(vals)


def cells_of(S, roster):
    others11 = [m for m in roster if m != FLAGGED]
    out = []
    for st in STATS:
        X = {c: stat_value(S, c, st) for c in roster}
        for sp_name, members in SPREADS:
            mem = list(members) if members else others11
            vals = [X[m] for m in mem]
            out.append(dict(stat=st, spread=sp_name, x=X[FLAGGED], lo=min(vals), hi=max(vals),
                            inside=inside(X[FLAGGED], vals), primary=(st, sp_name) == PRIMARY,
                            members={m: X[m] for m in mem}))
    return out


def readout(label, qs, kimi, grok, P, META, roster, do_boot):
    S = stats(qs, kimi, grok, P, META, roster)
    others11 = [m for m in roster if m != FLAGGED]
    say("=" * 110)
    say("POPULATION: %s  (%d questions)" % (label, len(qs)))
    say("=" * 110)
    say("Per contestant, paired denominator n; reference r in {Kimi candidate, grok-reasoning incumbent}:")
    say("  A = marginal agreement; P(br) = both-right share; n_bw = both-wrong questions; a_bw = same wrong option | both wrong")
    say("  %-28s %5s | %6s %6s %5s %6s | %6s %6s %5s %6s | %7s %7s %7s %7s" % (
        "contestant", "n", "A_kimi", "Pbr_k", "nbw_k", "abw_k", "A_grok", "Pbr_g", "nbw_g", "abw_g",
        "dA", "dPbr", "dBWterm", "GAIN-PR"))
    for c in sorted(roster, key=lambda m: -S[(m, "kimi")]["A"]):
        k, g = S[(c, "kimi")], S[(c, "grok")]
        dA = k["A"] - g["A"]; dp = k["pbr"] - g["pbr"]
        dbw = (k["pbw"] * (k["abw"] if k["nbw"] else 0.0)) - (g["pbw"] * (g["abw"] if g["nbw"] else 0.0))
        say("  %-28s %5d | %6.3f %6.3f %5d %6.3f | %6.3f %6.3f %5d %6.3f | %+7.3f %+7.3f %+7.3f %+7.3f%s" % (
            c[:28], k["n"], k["A"], k["pbr"], k["nbw"], k["abw"], g["A"], g["pbr"], g["nbw"], g["abw"],
            dA, dp, dbw, k["abw"] - g["abw"], "   <- frontier" + (" (flagged)" if c == FLAGGED else "") if c in FRONTIER else ""))
    say("  dA = dPbr + dBWterm exactly (both-right agreement is 1, mixed strata 0, on a single-key item).")
    say("")
    say("COMMON both-wrong stratum (c wrong, Kimi wrong, grok wrong: identical questions for both references; paired):")
    say("  %-28s %5s | %6s %6s %6s | %8s | %3s %3s %8s" % ("contestant", "n_com", "a_kimi", "a_grok", "GAIN", "agreeK/G", "b", "c", "McNemar p"))
    for c in sorted(roster, key=lambda m: -S[(m, "kimi")]["A"]):
        d = S[(c, "com")]
        say("  %-28s %5d | %6.3f %6.3f %+6.3f | %3d/%-4d | %3d %3d %8.3f%s" % (
            c[:28], d["n"], d["abw_k"], d["abw_g"], d["gain"], d["ak"], d["ag"], d["b"], d["c"], rref.mcnemar_p(d["b"], d["c"]),
            "   <- frontier" + (" (flagged)" if c == FLAGGED else "") if c in FRONTIER else ""))
    say("  b = c agrees with Kimi's wrong option but not grok's; c = the reverse; exact two-sided binomial on (b, c).")
    gk, gg = S[(FLAGGED, "kimi")], S[(FLAGGED, "grok")]
    say("")
    say("DECOMPOSITION of gemini's marginal gain %+.3f (n=%d):" % (gk["A"] - gg["A"], gk["n"]))
    say("  accuracy-coupling term (change in both-right share): %+.3f  (%.3f -> %.3f)" % (gk["pbr"] - gg["pbr"], gg["pbr"], gk["pbr"]))
    bwk = gk["pbw"] * gk["abw"]; bwg = gg["pbw"] * gg["abw"]
    say("  both-wrong term P(bw)*a_bw:                            %+.3f  (%.3f -> %.3f; a_bw %.3f on %d -> %.3f on %d)"
        % (bwk - bwg, bwg, bwk, gg["abw"], gg["nbw"], gk["abw"], gk["nbw"]))
    cells = cells_of(S, roster)
    say("")
    say("REGISTERED READOUT on the both-wrong stratum (gemini vs the incumbents' spread):")
    for ce in cells:
        say("  %-9s vs %-11s gemini %+.3f | spread [%+.3f, %+.3f] | %s%s" % (
            ce["stat"], ce["spread"], ce["x"], ce["lo"], ce["hi"], "INSIDE" if ce["inside"] else "OUTSIDE",
            "   <- PRIMARY (hardest reading)" if ce["primary"] else ""))
    for st in STATS:
        say("  spread members, %-8s: " % st + ", ".join("%s %+.3f" % (m[:12], stat_value(S, m, st)) for m in others11))
    boot = None
    if do_boot:
        boot = bootstrap(qs, kimi, grok, P, META, roster)
        say("")
        say("QUESTION BOOTSTRAP (B=%d, seed %d, %d usable replicates) on this population:" % (B_BOOT, SEED, boot["reps"]))
        for st in STATS:
            x = stat_value(S, FLAGGED, st); m3 = sum(stat_value(S, m, st) for m in OTHER_FRONTIER) / 3
            say("  gemini %-8s %+.3f  95%% [%+.3f, %+.3f] | minus FRONTIER-3 mean %+.3f  95%% [%+.3f, %+.3f] | share INSIDE: FRONTIER-3 %.3f, ROSTER-11 %.3f"
                % (st, x, boot[st]["lo"], boot[st]["hi"], x - m3, boot[st]["d3_lo"], boot[st]["d3_hi"],
                   boot[st]["in3"], boot[st]["in11"]))
        say("  gemini stratum sizes across replicates: n_bw(Kimi) median %d [%d, %d]; n_bw(grok) median %d [%d, %d]; n_com median %d [%d, %d]"
            % tuple(boot["sizes"]))
    return S, cells, boot


def bootstrap(qs, kimi, grok, P, META, roster):
    rnd = random.Random(SEED); qs = list(qs); n = len(qs)
    others11 = [m for m in roster if m != FLAGGED]
    acc = {st: dict(x=[], d3=[], in3=0, in11=0) for st in STATS}
    sizes = {k: [] for k in ("nk", "ng", "nc")}
    reps = 0
    for _ in range(B_BOOT):
        samp = [qs[rnd.randrange(n)] for _ in range(n)]
        S = stats(samp, kimi, grok, P, META, roster)
        X = {st: {c: stat_value(S, c, st) for c in roster} for st in STATS}
        if any(v != v for st in STATS for v in X[st].values()):   # an empty stratum in this replicate: skip it
            continue
        reps += 1
        for st in STATS:
            a = acc[st]; x = X[st][FLAGGED]
            a["x"].append(x); a["d3"].append(x - sum(X[st][m] for m in OTHER_FRONTIER) / 3)
            a["in3"] += inside(x, [X[st][m] for m in OTHER_FRONTIER]); a["in11"] += inside(x, [X[st][m] for m in others11])
        sizes["nk"].append(S[(FLAGGED, "kimi")]["nbw"]); sizes["ng"].append(S[(FLAGGED, "grok")]["nbw"]); sizes["nc"].append(S[(FLAGGED, "com")]["n"])

    def pct(v, p):
        v = sorted(v); m = len(v); return v[min(m - 1, max(0, int(round(p * (m - 1)))))]
    out = dict(reps=reps)
    for st in STATS:
        a = acc[st]
        out[st] = dict(lo=pct(a["x"], .025), hi=pct(a["x"], .975), d3_lo=pct(a["d3"], .025), d3_hi=pct(a["d3"], .975),
                       in3=a["in3"] / reps, in11=a["in11"] / reps)
    out["sizes"] = tuple(pct(sizes[k], p) for k in ("nk", "ng", "nc") for p in (.5, .025, .975))
    return out


def main():
    path, kimi_all, grok, P, META, roster, disc, weak = load()
    say("[POOL-PIN] pool of record p2dca21ab5f4ef3ae (pool_guard.assert_pool_of_record passed)")
    say("REF-QUAL-GATE3-COND — correctness-conditional agreement on the Kimi JSON cache (FRAMEWORK.md item 12; zero calls)")
    say("cache: %s" % os.path.relpath(path, ROOT))
    term = sorted(q for q, (a, g, f) in kimi_all.items() if a and f == "stop")
    allq = sorted(kimi_all)
    trunc = [q for q in allq if q not in term]
    say("answers %d | terminated (finish='stop', parsed) %d | truncated/unparsed %d | discriminating %d/%d terminated | weak-cell %d/%d terminated"
        % (len(allq), len(term), len(trunc), sum(1 for q in disc if q in term), sum(1 for q in disc if q in kimi_all),
           sum(1 for a in rq.WEAK for q in weak[a] if q in term), sum(1 for a in rq.WEAK for q in weak[a] if q in kimi_all)))
    say("contestants: rubric_p8.ARENA12 (12; Meta-Llama-3-70B-Instruct absent); incumbent reference grok-reasoning (judge_solve/grok-reasoning.db)")
    say("KEY DENOMINATOR: the cache's questions in pool p2dca21ab5f4ef3ae, keyed by eval_results gt; strata are key correctness of")
    say("  contestant and reference. No judge direction is scored, so the McNemar-established rule is vacuous for this test; the")
    say("  exact McNemar printed on the COMMON stratum tests agreement flips between the two references on identical questions.")
    say("READINGS: PER-REFERENCE (record's literal wording; two different both-wrong sets) and COMMON (paired; same questions).")
    say("  PRIMARY = GAIN-COM vs FRONTIER-3, the reading hardest on the prediction (composition term removed, narrowest spread).")
    say("  Disclosure: the first draft on disk declared GAIN-PR vs FRONTIER-3 primary before any number was read; the COMMON reading")
    say("  was added on this run after both were seen, under the block's hardest-reading rule. Both are scored; both are printed.")
    say("")
    kimi_term = {q: kimi_all[q][0] for q in term}
    kimi_tw = {q: kimi_all[q][0] for q in allq}   # truncation -> '' -> wrong and disagreeing with every letter
    S0 = stats(term, kimi_term, grok, P, META, roster)
    say("RECORD REPRODUCTION (marginal gate (3), terminated answers): " + "; ".join(
        "%s %+.3f (%.3f vs %.3f, n=%d)" % (c[:8], S0[(c, "kimi")]["A"] - S0[(c, "grok")]["A"], S0[(c, "kimi")]["A"], S0[(c, "grok")]["A"], S0[(c, "kimi")]["n"])
        for c in FRONTIER))
    rec = S0[(FLAGGED, "kimi")]["A"] - S0[(FLAGGED, "grok")]["A"]
    say("  record says gemini +0.071 (0.858 vs 0.787), arx +0.027, iask +0.016, gpt-4o +0.004 -> %s" % ("REPRODUCED" if abs(rec - 0.071) < 0.0015 else "NOT REPRODUCED"))
    say("")
    S, cells, boot = readout("terminated answers (population of record)", term, kimi_term, grok, P, META, roster, True)
    say("")
    S2, cells2, _ = readout("all 552 answers, truncation scored wrong-and-disagreeing (sensitivity; degenerate for agreement)", allq, kimi_tw, grok, P, META, roster, False)
    say("")
    say("=" * 110)
    say("VERDICT TABLE (the item registers a readout and one prediction; no bar; each row scores the prediction on that reading)")
    say("=" * 110)
    for ce in cells:
        bs = boot[ce["stat"]]["in3" if ce["spread"] == "FRONTIER-3" else "in11"]
        say("  %-9s vs %-11s gemini %+.3f in [%+.3f, %+.3f]: point check %s; re-%s in %.0f%% of resamples%s" % (
            ce["stat"], ce["spread"], ce["x"], ce["lo"], ce["hi"], "HOLDS" if ce["inside"] else "FAILS",
            "holds" if ce["inside"] else "fails", 100 * (bs if ce["inside"] else 1 - bs), "   <- PRIMARY" if ce["primary"] else ""))
    prim = [ce for ce in cells if ce["primary"]][0]
    com = S[(FLAGGED, "com")]
    say("")
    say("PRIMARY (GAIN-COM vs FRONTIER-3, hardest reading): point check %s; gemini %+.3f (%d/%d vs %d/%d on %d common questions;"
        % ("HOLDS" if prim["inside"] else "FAILS", prim["x"], com["ak"], com["n"], com["ag"], com["n"], com["n"]))
    say("  b=%d, c=%d, exact McNemar p=%.3f) vs spread [%+.3f, %+.3f]; bootstrap 95%% [%+.3f, %+.3f]; minus FRONTIER-3 mean [%+.3f, %+.3f];"
        % (com["b"], com["c"], rref.mcnemar_p(com["b"], com["c"]), prim["lo"], prim["hi"], boot["GAIN-COM"]["lo"], boot["GAIN-COM"]["hi"],
           boot["GAIN-COM"]["d3_lo"], boot["GAIN-COM"]["d3_hi"]))
    say("  share of resamples inside %.3f." % boot["GAIN-COM"]["in3"])
    lit = [ce for ce in cells if (ce["stat"], ce["spread"]) == ("GAIN-PR", "FRONTIER-3")][0]
    say("LITERAL (GAIN-PR vs FRONTIER-3, the first draft's primary): point check %s; gemini %+.3f vs [%+.3f, %+.3f]; bootstrap 95%% [%+.3f, %+.3f];"
        % ("HOLDS" if lit["inside"] else "FAILS", lit["x"], lit["lo"], lit["hi"], boot["GAIN-PR"]["lo"], boot["GAIN-PR"]["hi"]))
    say("  share of resamples inside %.3f." % boot["GAIN-PR"]["in3"])
    say("Sensitivity (552, truncation-as-wrong): " + "; ".join("%s/%s %s" % (ce["stat"], ce["spread"], "HOLDS" if ce["inside"] else "FAILS") for ce in cells2))
    gk, gg = S[(FLAGGED, "kimi")], S[(FLAGGED, "grok")]
    say("")
    say("READING. (a) The registered readout is delivered as an exact decomposition, no inference: of gemini's +%.3f marginal gain,"
        % (gk["A"] - gg["A"]))
    say("    %+.3f is the change in the both-right share (accuracy coupling: a more accurate reference is right together with the"
        % (gk["pbr"] - gg["pbr"]))
    say("    most accurate contestant more often) and %+.3f is the both-wrong term. That is the coupling the record named: %.0f%% of"
        % ((gk["pbw"] * gk["abw"]) - (gg["pbw"] * gg["abw"]), 100 * (gk["pbr"] - gg["pbr"]) / (gk["A"] - gg["A"])))
    say("    the marginal gain that failed gate (3) is accounted for by Kimi being right on questions gemini is right on.")
    say("  (b) The prediction is reading-dependent at the point. On the record's literal per-reference stratum gemini's gain %+.3f is"
        % lit["x"])
    say("    inside the frontier-3 spread by %+.3f. On the common (paired) stratum, which removes the composition term, gemini's gain"
        % (lit["hi"] - lit["x"]))
    say("    %+.3f is OUTSIDE the frontier-3 spread [%+.3f, %+.3f] by %+.3f and is the largest in the roster; on the LEVEL statistic"
        % (prim["x"], prim["lo"], prim["hi"], prim["x"] - prim["hi"]))
    say("    gemini's both-wrong agreement with Kimi (%.3f) is the highest in the roster, as it is with the incumbent (%.3f)."
        % (gk["abw"], gg["abw"]))
    say("  (c) At this support none of the readings is a distinguishable difference: the primary gain rests on b=%d against c=%d"
        % (com["b"], com["c"]))
    say("    (exact p=%.3f); its bootstrap interval [%+.3f, %+.3f] and the interval of gemini minus the frontier-3 mean [%+.3f, %+.3f]"
        % (rref.mcnemar_p(com["b"], com["c"]), boot["GAIN-COM"]["lo"], boot["GAIN-COM"]["hi"], boot["GAIN-COM"]["d3_lo"], boot["GAIN-COM"]["d3_hi"]))
    say("    both contain zero; the primary point check re-fails in %.0f%% of resamples and the literal one re-holds in %.0f%%."
        % (100 * (1 - boot["GAIN-COM"]["in3"]), 100 * boot["GAIN-PR"]["in3"]))
    say("    VERDICT on the prediction: FAILS at the point on the hardest reading, HOLDS at the point on the literal reading,")
    say("    UNDETERMINED at support on every reading. The conditional form of gate (3) cannot clear or flag gemini on ~50 both-wrong")
    say("    questions; a conditional gate needs a registered bar and a support rule before it replaces the marginal one.")
    say("  No wrong-direction count exists in this test; the McNemar-established rule is vacuous (stated above). Zero LLM calls.")
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nwritten:", OUT)


if __name__ == "__main__":
    main()
