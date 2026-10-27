"""KEY-TIE-DECLINE — a product rule wherever a key exists (registered 2026-09-15 at commit 60cb7f3, zero calls).

  python tools/analysis/key_tie_decline.py

REGISTRATION (docs/judge_v2_program.md, "### B. KEY-TIE-DECLINE"), quoted:
  "Decline any separation whose pair's key direction is not established (exact McNemar p >= 0.05 on the cell's
  judged questions), on top of the raw certificate and on top of the budget. Measure on x12 (891 edges) and on
  the merged 20-model board: calls surrendered, wrong calls removed, and what remains.
  CRITERIA: (1) PRIMARY: on the merged board, the decline rule removes at least 6 of the 8 within-tier wrong
  separations for no more than 15% of across-tier calls surrendered. (2) Combined with the widener on x12, the
  remaining wrong calls at 0.975 are all key-established (the residue is real error, not noise). (3) Report the
  rule's cost in calls at every threshold 0.90-0.995.
  PREDICTION: (1) holds - it removes 7 of 8 - at about 10% of across-tier calls; (2) holds with 2 remaining.
  FALSIFIER: if it costs more than 25% of across-tier calls to remove the within-tier errors, the rule is too
  blunt for a product and the widener alone is the recommendation."

IMPLEMENTATION, fixed before the run:
  * x12: systematic_budget.build() -> the 891 edges with key gap >= 0.02 and anchor_qs (the anchor's JUDGED
    questions). Decline iff systematic_budget.mcnemar_edge(e, K, anchor_qs)[0] >= 0.05. Bases: the raw
    certificate craw(e) and the shipped widener cbud(e, -3.2326, 3.3133) (budget_transfer.B0/B1).
  * merged 20-model board, two objects, both reported:
      (a) PER-ANCHOR edges from budget_transfer.load() + edges_from(r12 + r20, ...), same rule, same function,
          denominator = the anchor's judged questions;
      (b) the POOLED board of record (x20_merged's TIER-HONEST object: 400 draws, seed 42, over all 2,811 judged
          questions), denominator = all judged questions, passed through the SAME mcnemar_edge via one
          pseudo-anchor. Its raw-certificate counts must reproduce x20_merged.txt before any stratum is read.
    Tiering for within/across: x20_replications.key_tiers at the 0.017 gap on key accuracy over the judged
    questions, exactly as x20_merged.py.
  * thresholds 0.90, 0.95, 0.975, 0.99, 0.995 on both bases; "called" = base certificate >= threshold; a
    "separation" on the pooled board at CONF is the same thing (p >= CONF or p <= 1-CONF <=> craw >= CONF).
  * every wrong count carries its McNemar-established count from systematic_budget.established(); by
    construction the residue's wrong calls are ALL established (the rule declines exactly the unestablished
    edges), so criterion (2) is a tautology of the rule and is reported as such together with the count.
  * DATA-OBJECT NOTE: the registration's "8 within-tier wrong separations" does not exist on the merged board of
    record. x20_merged.txt has within-tier 6/7 separated, 3 wrong (1 established); the sparse, superseded board
    (x20_replications.txt) had 8/9 separated, 6 wrong. The "8" is the sparse board's SEPARATED count. Criterion
    (1) is scored on the object that exists and its verdict is stated against the registered wording.
  * Meta-Llama-3-70B-Instruct is excluded everywhere (it is in neither verdict cache; asserted).
  * no network, no LLM calls; intermediate tables are pickled under the session scratchpad (bigpic/).
"""
import os, sys, math, random, pickle, time
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import pool_guard
import rubric_p8 as p8
import judge_free_tests as jf
import systematic_budget as sb
import budget_transfer as bt
import x20_replications as xr

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "key_tie_decline.txt")
CACHE = os.environ.get("KTD_CACHE", os.path.join(
    r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena",
    "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "bigpic"))
THRESHOLDS = (0.90, 0.95, 0.975, 0.99, 0.995)
ALPHA = 0.05
EXCLUDE = "Meta-Llama-3-70B-Instruct"
B0, B1 = bt.B0, bt.B1          # the shipped widener, applied cold


def log(msg):
    print("[ktd %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def cached(name, fn):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        log("cache hit %s" % name)
        return pickle.load(open(p, "rb"))
    log("building %s" % name)
    v = fn()
    pickle.dump(v, open(p, "wb"))
    return v


def base_c(e, base):
    return sb.craw(e) if base == "raw" else sb.cbud(e, B0, B1)


def decline_table(L, edges, K, aq, title, tier_of=None):
    """The rule at every threshold on both bases. Returns {(base, t): stats}."""
    pv = {id(e): sb.mcnemar_edge(e, K, aq)[0] for e in edges}
    dec = {k: (v >= ALPHA) for k, v in pv.items()}
    n_est = sum(1 for e in edges if not dec[id(e)])
    L.append("")
    L.append("=== %s ===" % title)
    L.append("  edges %d | key direction established (McNemar p < %.2f) %d | unestablished %d | wrong-direction %d(%d)"
             % (len(edges), ALPHA, n_est, len(edges) - n_est,
                sum(1 for e in edges if not e["right"]), sum(1 for e in edges if not e["right"] and not dec[id(e)])))
    L.append("  wrong counts are all(McNemar-established). 'surr' = calls the rule declines; 'right surr' = correct")
    L.append("  calls given up; residue = calls that survive; residue wrong is established by construction.")
    hdr = "  %-8s %6s %7s %7s %10s %13s %12s %14s" % ("base", "thr", "called", "surr", "right surr", "wrong removed", "residue", "residue wrong")
    L.append(hdr)
    out = {}
    for base in ("raw", "widener"):
        for t in THRESHOLDS:
            called = [e for e in edges if base_c(e, base) >= t]
            surr = [e for e in called if dec[id(e)]]
            res = [e for e in called if not dec[id(e)]]
            cw = [e for e in called if not e["right"]]
            rw = [e for e in res if not e["right"]]
            rem = [e for e in surr if not e["right"]]
            st = dict(called=len(called), surr=len(surr), right_surr=sum(1 for e in surr if e["right"]),
                      called_wrong=len(cw), called_wrong_est=len(sb.established(cw, K, aq)),
                      removed=len(rem), removed_est=len(sb.established(rem, K, aq)),
                      residue=len(res), residue_wrong=len(rw), residue_wrong_est=len(sb.established(rw, K, aq)))
            out[(base, t)] = st
            L.append("  %-8s %6.3f %7d %7d %10d %8d(%d)/%d(%d) %12d %10d(%d)"
                     % (base, t, st["called"], st["surr"], st["right_surr"], st["removed"], st["removed_est"],
                        st["called_wrong"], st["called_wrong_est"], st["residue"], st["residue_wrong"], st["residue_wrong_est"]))
    if tier_of is not None:
        L.append("")
        L.append("  by KEY TIER (x20_merged tiering, 0.017 gap over the judged questions):")
        L.append("  %-8s %6s | %-38s | %-42s" % ("base", "thr", "ACROSS-tier: called, surr (%), wrong->residue wrong",
                                                 "WITHIN-tier: called, surr, wrong->residue wrong"))
        for base in ("raw", "widener"):
            for t in THRESHOLDS:
                called = [e for e in edges if base_c(e, base) >= t]
                ac = [e for e in called if tier_of[e["a"]] != tier_of[e["b"]]]
                wi = [e for e in called if tier_of[e["a"]] == tier_of[e["b"]]]
                a_s = [e for e in ac if dec[id(e)]]; w_s = [e for e in wi if dec[id(e)]]
                a_w = [e for e in ac if not e["right"]]; w_w = [e for e in wi if not e["right"]]
                a_rw = [e for e in a_w if not dec[id(e)]]; w_rw = [e for e in w_w if not dec[id(e)]]
                st = out[(base, t)]
                st.update(across_called=len(ac), across_surr=len(a_s),
                          across_frac=(len(a_s) / len(ac)) if ac else float("nan"),
                          across_wrong=len(a_w), across_wrong_est=len(sb.established(a_w, K, aq)),
                          across_res_wrong=len(a_rw),
                          within_called=len(wi), within_surr=len(w_s), within_wrong=len(w_w),
                          within_wrong_est=len(sb.established(w_w, K, aq)), within_res_wrong=len(w_rw),
                          within_removed=len(w_w) - len(w_rw))
                L.append("  %-8s %6.3f | %5d, %4d (%5.1f%%), %2d(%d) -> %2d | %4d, %3d, %2d(%d) -> %2d"
                         % (base, t, len(ac), len(a_s), 100.0 * st["across_frac"] if ac else float("nan"),
                            len(a_w), st["across_wrong_est"], len(a_rw),
                            len(wi), len(w_s), len(w_w), st["within_wrong_est"], len(w_rw)))
    return out, pv


def list_wrong(L, edges, K, aq, base, t, label):
    called = [e for e in edges if base_c(e, base) >= t and not e["right"]]
    if not called:
        L.append("  %s: no wrong calls" % label); return
    L.append("  %s (%d):" % (label, len(called)))
    for e in sorted(called, key=lambda e: sb.mcnemar_edge(e, K, aq)[0]):
        p_, b_, c_ = sb.mcnemar_edge(e, K, aq)
        L.append("    %-16s %-26s vs %-26s c=%.4f gap=%.4f A=%.3f McNemar %d:%d p=%.4f -> %s"
                 % (e["anchor"][:16], e["a"][:26], e["b"][:26], base_c(e, base), e["gap"], e["agree"], b_, c_, p_,
                    "KEPT (established)" if p_ < ALPHA else "declined"))


def pooled_merged(rows, models, K, P, qs_judged):
    """x20_merged's TIER-HONEST object: 400 draws, seed 42, same draw order; plus m, s, agreement per pair."""
    rng = random.Random(42)
    byq = defaultdict(list)
    for r in rows:
        byq[r[2]].append(r)
    boards = []
    for i in range(xr.B):
        pick = [qs_judged[rng.randrange(len(qs_judged))] for _ in qs_judged]
        sub = [r for q in pick for r in byq[q]]
        boards.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                     for a, b, _, w, _iv in sub], models))
        if i % 100 == 99:
            log("pooled draw %d/%d" % (i + 1, xr.B))
    acc = {m: sum(K[q][m] for q in qs_judged if m in K.get(q, {})) / max(1, sum(1 for q in qs_judged if m in K.get(q, {})))
           for m in models}
    edges = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            d = np.array([dr[a] - dr[b] for dr in boards])
            p = float((d > 0).mean())
            both = [q for q in qs_judged if P[q].get(a) and P[q].get(b)]
            agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both) if both else 0.0
            edges.append(dict(anchor="POOLED", a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                              right=((p > 0.5) == (acc[a] > acc[b])), agree=agree, gap=abs(acc[a] - acc[b]), n=len(both)))
    return edges, acc


def main():
    L = []
    L.append("=== KEY-TIE-DECLINE: decline any separation whose key direction is not established (McNemar p >= %.2f) ===" % ALPHA)
    L.append("  rule applied on top of (i) the raw certificate and (ii) the shipped widener tau(A) = exp(%.4f + %.4f*A)" % (B0, B1))
    L.append("  thresholds %s | wrong counts as all(McNemar-established) | %s excluded" % (", ".join("%.3f" % t for t in THRESHOLDS), EXCLUDE))

    # ---------------- x12: the 891 edges ----------------
    def build_x12():
        models, K, P, by, edges, anchor_qs = sb.build()
        return models, dict(K), dict(P), edges, anchor_qs
    models12, K12, P12, e12_all, aq12 = cached("ktd_x12_edges.pkl", build_x12)
    assert EXCLUDE not in models12
    e12 = [e for e in e12_all if e["gap"] >= sb.GAP]
    L.append("")
    L.append("  DATA CHECK x12: %d models, %d edges with any key gap, %d with gap >= %.2f (the registered 891), %d anchors, judged"
             " questions per anchor min %d / max %d" % (len(models12), len(e12_all), len(e12), sb.GAP, len(aq12),
                                                         min(len(v) for v in aq12.values()), max(len(v) for v in aq12.values())))
    L.append("  key denominator: sb.mcnemar_edge over anchor_qs[anchor] = the anchor's JUDGED questions (not the routed pool).")
    st12, pv12 = decline_table(L, e12, K12, aq12, "x12: 891 per-anchor edges, decline rule on both bases")
    L.append("")
    L.append("  x12 wrong calls at 0.975, widener base:")
    list_wrong(L, e12, K12, aq12, "widener", 0.975, "  widener 0.975")
    L.append("  x12 wrong calls at 0.975, raw base:")
    list_wrong(L, e12, K12, aq12, "raw", 0.975, "  raw 0.975")

    # ---------------- merged board: load once ----------------
    def build_merged():
        r12, r20, models, K, P = bt.load()
        old = set(p8.ARENA12)
        rows = r12 + r20
        e_mg, aq_mg = bt.edges_from(rows, models, K, P, old, "merged")
        qs_judged = sorted({r[2] for r in rows})
        pooled, acc = pooled_merged(rows, models, K, P, qs_judged)
        return models, dict(K), e_mg, aq_mg, qs_judged, pooled, acc, len(r12), len(r20)
    models20, K20, e_mg, aq_mg, qs_judged, pooled, acc, n12, n20 = cached("ktd_merged_edges.pkl", build_merged)
    assert EXCLUDE not in models20
    kt = xr.key_tiers(acc, models20, gap=xr.KEY_GAP)
    tier_of = {m: i for i, t in enumerate(kt) for m in t}
    aq_pool = {"POOLED": qs_judged}

    L.append("")
    L.append("  DATA CHECK merged board: x12 %d + x20 %d = %d verdicts | %d models | %d judged questions | per-anchor edges %d"
             " (gap >= %.2f) on %d anchors | key tiers at %.3f: %d" % (n12, n20, n12 + n20, len(models20), len(qs_judged),
                                                                        len(e_mg), bt.GAP, len(aq_mg), xr.KEY_GAP, len(kt)))
    for i, t in enumerate(kt):
        L.append("    tier %2d: %s" % (i, ", ".join("%s (%.3f)" % (m[:24], acc[m]) for m in t)))
    # reproduce x20_merged's TIER-HONEST counts before reading any stratum
    sep = [e for e in pooled if sb.craw(e) >= xr.CONF]
    wi = [e for e in sep if tier_of[e["a"]] == tier_of[e["b"]]]; ac = [e for e in sep if tier_of[e["a"]] != tier_of[e["b"]]]
    n_wi = sum(1 for e in pooled if tier_of[e["a"]] == tier_of[e["b"]]); n_ac = len(pooled) - n_wi
    wi_w = [e for e in wi if not e["right"]]; ac_w = [e for e in ac if not e["right"]]
    rep = (len(wi), n_wi, len(wi_w), len(sb.established(wi_w, K20, aq_pool)), len(ac), n_ac, len(ac_w), len(sb.established(ac_w, K20, aq_pool)))
    L.append("  pooled board at CONF %.2f: within %d/%d separated, wrong %d(%d) | across %d/%d, wrong %d(%d)" % ((xr.CONF,) + rep))
    ok = rep == (6, 7, 3, 1, 176, 183, 5, 4)
    L.append("  reproduction of x20_merged.txt (6/7, 3(1) | 176/183, 5(4)): %s" % ("OK" if ok else "MISMATCH - strata below are NOT the board of record"))
    L.append("  the registration's '8 within-tier wrong separations' is NOT on this board: the merged board of record has 3 (1")
    L.append("  established); the superseded sparse board had 8/9 SEPARATED and 6 wrong. Criterion (1) is scored on the 3 that exist.")

    # ---------------- merged: pooled board (the TIER-HONEST object) ----------------
    L.append("")
    L.append("  key denominator (pooled): sb.mcnemar_edge with anchor_qs = {'POOLED': all %d judged questions}." % len(qs_judged))
    stP, pvP = decline_table(L, pooled, K20, aq_pool, "MERGED board, POOLED (190 pairs, x20_merged's TIER-HONEST object)", tier_of)
    L.append("")
    L.append("  pooled board: every within-tier separation at 0.95 and what the rule does to it:")
    for e in sorted(wi, key=lambda e: -sb.craw(e)):
        p_, b_, c_ = sb.mcnemar_edge(e, K20, aq_pool)
        L.append("    %-26s vs %-26s raw c=%.4f wid c=%.4f key %.3f/%.3f %s | McNemar %d:%d p=%.4f -> %s"
                 % (e["a"][:26], e["b"][:26], sb.craw(e), sb.cbud(e, B0, B1), acc[e["a"]], acc[e["b"]],
                    "right" if e["right"] else "WRONG", b_, c_, p_, "KEPT" if p_ < ALPHA else "declined"))
    L.append("  pooled board: every across-tier WRONG separation at 0.95:")
    for e in ac_w:
        p_, b_, c_ = sb.mcnemar_edge(e, K20, aq_pool)
        L.append("    %-26s vs %-26s raw c=%.4f wid c=%.4f key %.3f/%.3f | McNemar %d:%d p=%.4f -> %s"
                 % (e["a"][:26], e["b"][:26], sb.craw(e), sb.cbud(e, B0, B1), acc[e["a"]], acc[e["b"]], b_, c_, p_,
                    "KEPT" if p_ < ALPHA else "declined"))

    # ---------------- merged: per-anchor edges ----------------
    L.append("")
    L.append("  key denominator (per-anchor): sb.mcnemar_edge over aq_mg[anchor] = the anchor's judged questions on the merged board.")
    stA, pvA = decline_table(L, e_mg, K20, aq_mg, "MERGED board, PER-ANCHOR edges (budget_transfer.edges_from, gap >= 0.02)", tier_of)

    # ---------------- criteria ----------------
    L.append("")
    L.append("=== REGISTERED CRITERIA ===")
    # (1) on the pooled board of record at CONF 0.95 (the TIER-HONEST operating point) and at 0.975
    L.append("  (1) PRIMARY, as registered: 'removes at least 6 of the 8 within-tier wrong separations for no more than 15% of")
    L.append("      across-tier calls surrendered'. The object '8 within-tier wrong separations' does not exist on the merged")
    L.append("      board of record (3 wrong, 1 established); the criterion as written CANNOT PASS and is UNDETERMINED by data-object")
    L.append("      mismatch. What the rule does on the object that exists:")
    for base in ("raw", "widener"):
        for t in (0.95, 0.975):
            s = stP[(base, t)]
            L.append("        pooled %-8s %.3f: within-tier wrong %d(%d) -> removed %d, residue %d | across-tier calls %d, surrendered %d = %.1f%%"
                     % (base, t, s["within_wrong"], s["within_wrong_est"], s["within_removed"], s["within_res_wrong"],
                        s["across_called"], s["across_surr"], 100 * s["across_frac"]))
    for base in ("raw", "widener"):
        for t in (0.95, 0.975):
            s = stA[(base, t)]
            L.append("        per-anchor %-8s %.3f: within-tier wrong %d(%d) -> removed %d, residue %d | across-tier calls %d, surrendered %d = %.1f%%"
                     % (base, t, s["within_wrong"], s["within_wrong_est"], s["within_removed"], s["within_res_wrong"],
                        s["across_called"], s["across_surr"], 100 * s["across_frac"]))
    sP = stP[("raw", 0.95)]; sA = stA[("raw", 0.975)]
    L.append("      the rule removes exactly the UNESTABLISHED wrong separations and none of the established ones, by")
    L.append("      construction; on the pooled board of record that is %d of 3 within-tier wrong separations at 0.95, leaving %d"
             % (sP["within_removed"], sP["within_res_wrong"]))
    L.append("      (the established arx/iask inversion), at %.1f%% of across-tier calls. On the per-anchor edges it removes %d of %d at"
             % (100 * sP["across_frac"], stA[("raw", 0.975)]["within_removed"], stA[("raw", 0.975)]["within_wrong"]))
    L.append("      0.975 for %.1f%% of across-tier calls (raw) / %.1f%% (widener)." % (100 * sA["across_frac"], 100 * stA[("widener", 0.975)]["across_frac"]))
    # (2)
    s2 = st12[("widener", 0.975)]
    L.append("  (2) x12, widener + decline at 0.975: called %d -> residue %d | wrong %d(%d) -> residue wrong %d, of which established %d"
             % (s2["called"], s2["residue"], s2["called_wrong"], s2["called_wrong_est"], s2["residue_wrong"], s2["residue_wrong_est"]))
    L.append("      -> %s; the residue is established BY CONSTRUCTION of the rule (it declines exactly the unestablished edges), so"
             % ("holds (tautologically)" if s2["residue_wrong"] == s2["residue_wrong_est"] else "FAILS (impossible by construction)"))
    L.append("         the criterion carries no information beyond the count: %d remaining against the predicted 2." % s2["residue_wrong"])
    # (3)
    L.append("  (3) cost in calls at every threshold: tables above (x12, pooled merged, per-anchor merged; raw and widener).")
    # falsifier
    L.append("  FALSIFIER (> 25%% of across-tier calls to remove the within-tier errors): pooled raw 0.95 = %.1f%%, pooled widener 0.975 = %.1f%%,"
             % (100 * stP[("raw", 0.95)]["across_frac"], 100 * stP[("widener", 0.975)]["across_frac"]))
    L.append("      per-anchor raw 0.975 = %.1f%%, per-anchor widener 0.975 = %.1f%% -> %s"
             % (100 * stA[("raw", 0.975)]["across_frac"], 100 * stA[("widener", 0.975)]["across_frac"],
                "FIRES on the per-anchor edges" if max(stA[("raw", 0.975)]["across_frac"], stA[("widener", 0.975)]["across_frac"]) > 0.25
                else ("does not fire on either object" if max(stP[("raw", 0.95)]["across_frac"], stP[("widener", 0.975)]["across_frac"]) <= 0.25
                      else "FIRES on the pooled board")))
    L.append("  PREDICTION ('removes 7 of 8 at about 10%%; (2) holds with 2 remaining'): the 8 do not exist; x12 residue at 0.975 = %d."
             % s2["residue_wrong"])

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
