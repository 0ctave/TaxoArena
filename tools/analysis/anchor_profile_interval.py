"""ANCHOR-PROFILE-INTERVAL (registered 2026-09-15, zero calls) - is the 0.7183 pass a pass?

  python tools/analysis/anchor_profile_interval.py

REGISTRATION (docs/judge_v2_program.md, "### E. ANCHOR-PROFILE-INTERVAL"), quoted:
  PROFILE-RELIABILITY-X20 passed the 0.70 bar at 0.7183 on the merged board, a point estimate with a wide
  interval. Register the interval: leave-one-anchor-out jackknife on the 40-halving mean r, Spearman-Brown to
  R, on x12 (0.6728) and on the merged board (0.7183). And decompose the gain: anchor R on the merged board
  for the profile restricted to the 12 original models (same verdicts, 12 rows) against all 20, so "more
  verdicts on the same pairs" is separated from "more models in the profile".
  CRITERIA: (1) the jackknife 95% interval on the merged board, and whether its LOWER bound clears 0.70. If
  it does not, the registered consequence is amended: RESOLVE may publish per-anchor claims on a board of
  this size WITH the interval, not as a bare pass. (2) The decomposition.
  PREDICTION: the lower bound does NOT clear 0.70 (interval roughly [0.55, 0.85]); the gain over x12 is
  mostly "more verdicts", not "more models". FALSIFIER: a lower bound above 0.70 makes the pass unqualified.

IMPLEMENTATION, as constrained by the registration and the run notes:
  * The statistic is profile_reliability.reliability (40 disjoint half-splits of each anchor's questions,
    model-demeaned Pearson r between the two half-profiles, mean over halvings) with the SAME seed the two
    recorded runs used at the anchor level, random.Random(7); Spearman-Brown sb(r) -> R.
  * Leave-one-anchor-out: for each of the 14 anchors, drop that anchor's cell and recompute the statistic
    from scratch (fresh Random(7), so the halvings of the remaining cells are drawn exactly as reliability()
    would draw them on that cell set). Jackknife SE on the R scale, SE = sqrt((n-1)/n * sum (R_-i - R_bar)^2);
    PRIMARY interval R_full +- 1.96*SE. READING CHOICES where the registration is silent, chosen to be the
    hardest on the programme's own claim (the pass): (a) the jackknife is also reported with the t(13)
    quantile 2.160 and with the SE taken on the r scale and the endpoints Spearman-Brown transformed, and with
    the halvings held FIXED (the same 40 halvings, the dropped anchor's points removed) so re-halving noise is
    separated from the anchor effect; if any of these readings disagrees with the primary on the 0.70
    boundary, criterion (1) is UNDETERMINED, not PASS. (b) The bias-corrected jackknife estimate is printed
    but the interval is centred on R_full, as the recorded 0.7183 is what the pass rests on.
  * Decomposition, three numbers: (A) x12 board, 12 models, 12 rows [recorded 0.6728]; (B) MERGED board, the
    20-model fit on every merged verdict, profile restricted to the 12 original models (same verdicts, 12
    rows); (C) MERGED board, 20 rows [recorded 0.7183]. "more verdicts" = B - A, "more models" = C - B, each
    with a paired leave-one-anchor-out jackknife interval.
  * McNemar-established rule: this test produces NO wrong-direction counts (nothing is compared to the key's
    direction), so there is nothing for the rule to attach to; the key denominator of the instrument itself
    is named in the output (the anchor's JUDGED questions, halved).
  * Meta-Llama-3-70B-Instruct is excluded everywhere (it is in neither cache's model set; checked).
"""
import os, sys, math, random, json, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import pool_guard
import profile_reliability as pr
import x20_merged as xm

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "anchor_profile_interval.txt")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "bigpic")
TREE = "bareq512_s42"
POOL = "p2dca21ab5f4ef3ae"
BAR = 0.70
SEED = 7            # profile_reliability.py and x20_merged.py both call reliability(..., random.Random(7)) at the anchor level
REPS = pr.REPS      # 40
Z = 1.96
T13 = 2.160         # t quantile, 13 df, two-sided 95%
EXCLUDE = "Meta-Llama-3-70B-Instruct"


def jack(full, loo, scale=Z):
    """Jackknife SE and interval of `full` from leave-one-out values `loo`."""
    n = len(loo); mean = sum(loo) / n
    se = math.sqrt((n - 1) / n * sum((v - mean) ** 2 for v in loo))
    bc = n * full - (n - 1) * mean
    return se, full - scale * se, full + scale * se, bc


def fixed_halvings(cells, qsel, build, models, rng, reps=REPS, min_cell=25):
    """Line-for-line mirror of profile_reliability.reliability that RETURNS the per-halving profile pairs
    instead of the mean r, so one anchor can be removed without redrawing the halvings."""
    per_rep = []
    for _ in range(reps):
        P = []
        for c, cqs in cells.items():
            cc = [q for q in cqs if q in qsel]
            if len(cc) < 2 * min_cell:
                continue
            cc = sorted(cc); rng.shuffle(cc)
            mid = len(cc) // 2
            d1 = build(cc[:mid]); d2 = build(cc[mid:])
            if not d1 or not d2:
                continue
            for m in models:
                if m in d1 and m in d2:
                    P.append((c, m, d1[m], d2[m]))
        per_rep.append(P)
    return per_rep


def mean_r_from(per_rep, drop=None):
    rs = []
    for P in per_rep:
        Q = [p for p in P if p[0] != drop]
        if len(Q) < 50:
            continue
        D = pr.demean_by_model(Q)
        v = pr.pearson([p[2] for p in D], [p[3] for p in D])
        if v == v:
            rs.append(v)
    return sum(rs) / len(rs) if rs else float("nan")


def main():
    L = []
    os.makedirs(SCRATCH, exist_ok=True)

    # ---------------- data ----------------
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows12 = [r for r in sj.open_cache().execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]
    rows_m, n12, n20 = xm.merged_rows()
    models12 = sorted(p8.ARENA12)
    models20 = sorted({r[0] for r in rows_m} | {r[1] for r in rows_m})
    m12_in_cache = sorted({r[0] for r in rows12} | {r[1] for r in rows12})

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models20 and m != EXCLUDE:
            K[q][m] = int(c or 0)

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    by12 = defaultdict(list); bym = defaultdict(list)
    for a, b, q, w, _ in rows12: by12[q].append((a, b, q, w))
    for a, b, q, w, _ in rows_m: bym[q].append((a, b, q, w))
    qs12 = sorted(set(route) & set(by12)); qsm = sorted(set(route) & set(bym))
    qs = qs12; qsel = set(qs)
    anc_cells = defaultdict(list)
    for q in qs: anc_cells[anc(route[q])].append(q)
    usable = {c: v for c, v in anc_cells.items() if len(v) >= 50}     # same construction and dict order as the two recorded runs
    anchors = list(usable)

    # ---------------- data check (before any stratum is read) ----------------
    L.append("=== ANCHOR-PROFILE-INTERVAL: is the 0.7183 pass a pass? ===")
    L.append("")
    L.append("--- DATA CHECK (the object, before strata are read into it) ---")
    chk = []
    chk.append(("x12 cache verdicts (valid) = 9,142", len(rows12) == 9142, len(rows12)))
    chk.append(("merged = x12 9,142 + x20 12,394 = 21,536", (n12, n20, len(rows_m)) == (9142, 12394, 21536), (n12, n20, len(rows_m))))
    chk.append(("x12 cache model set == ARENA12 (12 models)", m12_in_cache == models12, len(m12_in_cache)))
    chk.append(("merged model set has 20 models and contains ARENA12", len(models20) == 20 and set(models12) <= set(models20), len(models20)))
    chk.append(("%s absent from both caches" % EXCLUDE, EXCLUDE not in models20 and EXCLUDE not in m12_in_cache, EXCLUDE in models20))
    chk.append(("every judged question is in the reserved pool %s" % POOL, set(bym) <= pool, len(set(bym) - pool)))
    chk.append(("merged judged question set == x12 judged question set", set(bym) == set(by12), (len(bym), len(by12))))
    chk.append(("routed & judged questions = 2,811", len(qs12) == 2811 and len(qsm) == 2811, (len(qs12), len(qsm))))
    chk.append(("14 anchors, all >= 50 questions", len(usable) == 14 and len(anc_cells) == 14, (len(anc_cells), len(usable))))
    gap = {m: sum(1 for q in qs if m not in K.get(q, {})) for m in models20}
    gap = {m: n for m, n in gap.items() if n}
    ok = True
    for name, good, val in chk:
        ok &= bool(good)
        L.append("  [%s] %s  (%s)" % ("ok" if good else "FAIL", name, val))
    L.append("  [info] key rows missing on the %d judged questions, by model: %s  (%d questions touched)"
             % (len(qs), gap or "none", sum(1 for q in qs if len(K.get(q, {})) < len(models20))))
    L.append("         Those three are ARENA12 members. The key is a COMPARATOR here, not the statistic under test - the judge")
    L.append("         R never reads it - and the per-half key profile averages over the rows present, exactly as")
    L.append("         profile_reliability.key_build and x20_merged.key_build did for the recorded 0.9135 / 0.9139. Not fatal.")
    qpc = sum(len(v) for v in usable.values()) / len(usable)
    L.append("  anchors (q): " + ", ".join("%s %d" % (c, len(usable[c])) for c in anchors))
    L.append("  q/cell %.1f | halvings %d | seed random.Random(%d) | min_cell 25 (profile_reliability defaults)" % (qpc, REPS, SEED))
    L.append("  KEY DENOMINATOR of the instrument: each anchor's JUDGED questions (the 2,811 routed+judged reserved")
    L.append("  questions, ~201 per anchor), split into two disjoint halves of ~100; the profile on each half is the")
    L.append("  Bradley-Terry fit (rj.mm_fit via judge_free_tests.board_from) on that half's verdicts.")
    L.append("  McNEMAR-ESTABLISHED RULE: this test compares no separation to the key's direction, so there is no")
    L.append("  wrong-direction count for the rule to attach to. Not applicable, stated so.")
    if not ok:
        L.append("  DATA CHECK FAILED - stopping before any stratum is read.")
        txt = "\n".join(L); print(txt); open(OUT, "w", encoding="utf-8").write(txt + "\n"); return

    # ---------------- builders ----------------
    def jb12(cqs):
        rs = [r for q in cqs for r in by12[q]]
        if len({r[2] for r in rs}) < 10: return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models12)

    def jbm(cqs):
        rs = [r for q in cqs for r in bym[q]]
        if len({r[2] for r in rs}) < 10: return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models20)

    def key_build_for(models):
        def kb(cqs):
            d = {}
            for m in models:
                v = [K[q][m] for q in cqs if q in K and m in K[q]]
                if v: d[m] = sum(v) / len(v)
            return d if len(d) == len(models) else None
        return kb

    # (A) x12 board / 12 rows ; (B) merged board / 12 rows (fit on 20, rows restricted) ; (C) merged board / 20 rows
    boards = [("A x12 board, 12 rows", jb12, models12),
              ("B MERGED board, 12 rows (same verdicts, 20-model fit)", jbm, models12),
              ("C MERGED board, 20 rows", jbm, models20)]
    keys = [("key, 12 models", key_build_for(models12), models12),
            ("key, 20 models", key_build_for(models20), models20)]

    cache_path = os.path.join(SCRATCH, "anchor_profile_interval_folds.json")
    res = {}
    for name, build, models in boards + keys:
        r_full, sd_full, n_full = pr.reliability(usable, qsel, build, models, random.Random(SEED))
        loo_r = {}
        for drop in anchors:
            cells = {c: v for c, v in usable.items() if c != drop}
            r_i, _, _ = pr.reliability(cells, qsel, build, models, random.Random(SEED))
            loo_r[drop] = r_i
        # fixed-halving variant: same halvings as the full run, dropped anchor's points removed
        per_rep = fixed_halvings(usable, qsel, build, models, random.Random(SEED))
        r_fixed_full = mean_r_from(per_rep)
        loo_fixed = {drop: mean_r_from(per_rep, drop) for drop in anchors}
        res[name] = dict(r=r_full, sd=sd_full, n=n_full, loo_r=loo_r, r_fixed_full=r_fixed_full, loo_fixed=loo_fixed)
        print("done", name, r_full, pr.sb(r_full), flush=True)
    json.dump(res, open(cache_path, "w"), indent=1)

    # ---------------- (1) the interval ----------------
    L.append("")
    L.append("=== (1) LEAVE-ONE-ANCHOR-OUT JACKKNIFE (14 folds) on the %d-halving mean r, Spearman-Brown to R ===" % REPS)
    L.append("  %-52s %8s %8s %8s  %-18s %-18s %8s" % ("board", "r", "R(SB)", "SE_jk", "95% [z=1.96]", "95% [t13=2.160]", "R_bc"))
    summ = {}
    for name, _, _ in boards + keys:
        d = res[name]
        R_full = pr.sb(d["r"]); loo_R = [pr.sb(d["loo_r"][a]) for a in anchors]
        se, lo, hi, bc = jack(R_full, loo_R)
        _, lo_t, hi_t, _ = jack(R_full, loo_R, T13)
        # r-scale jackknife, endpoints transformed
        se_r, lo_r, hi_r, _ = jack(d["r"], [d["loo_r"][a] for a in anchors])
        # fixed-halving jackknife (R scale)
        Rf = pr.sb(d["r_fixed_full"]); loo_Rf = [pr.sb(d["loo_fixed"][a]) for a in anchors]
        se_f, lo_f, hi_f, _ = jack(Rf, loo_Rf)
        summ[name] = dict(R=R_full, se=se, lo=lo, hi=hi, lo_t=lo_t, hi_t=hi_t, bc=bc,
                          lo_r=pr.sb(lo_r), hi_r=pr.sb(hi_r), Rf=Rf, lo_f=lo_f, hi_f=hi_f, se_f=se_f)
        L.append("  %-52s %8.4f %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]   %8.4f"
                 % (name, d["r"], R_full, se, lo, hi, lo_t, hi_t, bc))
    L.append("  R_bc = bias-corrected jackknife estimate n*R - (n-1)*mean(R_-i); intervals are centred on R (the recorded value).")
    L.append("")
    L.append("  Sensitivity readings (all on the merged 20-row board, the one the pass rests on):")
    C = summ["C MERGED board, 20 rows"]; dC = res["C MERGED board, 20 rows"]
    L.append("    primary,   SE on R after SB, z=1.96 ............ [%.4f, %.4f]" % (C["lo"], C["hi"]))
    L.append("    t(13)=2.160 instead of z ......................... [%.4f, %.4f]" % (C["lo_t"], C["hi_t"]))
    L.append("    SE on r, endpoints SB-transformed, z=1.96 ....... [%.4f, %.4f]" % (C["lo_r"], C["hi_r"]))
    L.append("    halvings FIXED (drop the anchor's points), z=1.96  [%.4f, %.4f]  (full R on fixed halvings %.4f, SE %.4f)"
             % (C["lo_f"], C["hi_f"], C["Rf"], C["se_f"]))
    L.append("    (self-check: fixed-halving full-sample r %.6f vs reliability() r %.6f - identical rng stream)"
             % (dC["r_fixed_full"], dC["r"]))
    L.append("")
    L.append("  Per-anchor leave-one-out R on the merged 20-row board (which anchors carry the pass):")
    for a in sorted(anchors, key=lambda a: pr.sb(dC["loo_r"][a])):
        L.append("    drop %-28s R_-i %.4f  (fixed halvings %.4f)  delta vs full %+.4f"
                 % (a, pr.sb(dC["loo_r"][a]), pr.sb(dC["loo_fixed"][a]), pr.sb(dC["loo_r"][a]) - C["R"]))
    lows = [C["lo"], C["lo_t"], C["lo_r"], C["lo_f"]]
    clears_primary = C["lo"] >= BAR
    agree = all((v >= BAR) == clears_primary for v in lows)
    L.append("")
    L.append("  CRITERION (1): merged-board R = %.4f, jackknife 95%% interval [%.4f, %.4f]; LOWER BOUND %s %.2f"
             % (C["R"], C["lo"], C["hi"], "CLEARS" if clears_primary else "does NOT clear", BAR))
    if clears_primary and agree:
        L.append("  -> PASS (unqualified): every reading's lower bound is above %.2f. The registered FALSIFIER fires:" % BAR)
        L.append("     the pass is unqualified and the prediction (lower bound below 0.70) is FALSIFIED.")
        v1 = "PASS"
    elif (not clears_primary) and agree:
        L.append("  -> FAIL (the pass is qualified): the lower bound is below %.2f on every reading. REGISTERED CONSEQUENCE," % BAR)
        L.append("     as amended in advance: RESOLVE may publish per-anchor claims on a board of this size WITH the interval,")
        L.append("     not as a bare pass. Prediction (lower bound below 0.70) CONFIRMED.")
        v1 = "FAIL"
    else:
        L.append("  -> UNDETERMINED: the readings disagree on the %.2f boundary (lower bounds %s)." % (BAR, ", ".join("%.4f" % v for v in lows)))
        v1 = "UNDETERMINED"
    L.append("  Registered interval guess was roughly [0.55, 0.85]; measured width is %.3f." % (C["hi"] - C["lo"]))
    A = summ["A x12 board, 12 rows"]
    L.append("  For the record, the x12 board: R = %.4f, jackknife 95%% [%.4f, %.4f] (recorded 0.6728)." % (A["R"], A["lo"], A["hi"]))

    # ---------------- (2) the decomposition ----------------
    L.append("")
    L.append("=== (2) DECOMPOSITION: 'more verdicts on the same pairs' vs 'more models in the profile' ===")
    B = summ["B MERGED board, 12 rows (same verdicts, 20-model fit)"]
    L.append("  A  x12 board,    12 models fit, 12 rows ............ R = %.4f  [%.4f, %.4f]" % (A["R"], A["lo"], A["hi"]))
    L.append("  B  MERGED board, 20 models fit, 12 rows ............ R = %.4f  [%.4f, %.4f]" % (B["R"], B["lo"], B["hi"]))
    L.append("  C  MERGED board, 20 models fit, 20 rows ............ R = %.4f  [%.4f, %.4f]" % (C["R"], C["lo"], C["hi"]))
    # paired jackknife on the differences
    nmA, nmB, nmC = [b[0] for b in boards]
    dBA_loo = [pr.sb(res[nmB]["loo_r"][a]) - pr.sb(res[nmA]["loo_r"][a]) for a in anchors]
    dCB_loo = [pr.sb(res[nmC]["loo_r"][a]) - pr.sb(res[nmB]["loo_r"][a]) for a in anchors]
    dCA_loo = [pr.sb(res[nmC]["loo_r"][a]) - pr.sb(res[nmA]["loo_r"][a]) for a in anchors]
    dBA = B["R"] - A["R"]; dCB = C["R"] - B["R"]; dCA = C["R"] - A["R"]
    seBA, loBA, hiBA, _ = jack(dBA, dBA_loo); seCB, loCB, hiCB, _ = jack(dCB, dCB_loo); seCA, loCA, hiCA, _ = jack(dCA, dCA_loo)
    L.append("  'more verdicts'  B - A = %+.4f  (paired jackknife 95%% [%+.4f, %+.4f], SE %.4f)" % (dBA, loBA, hiBA, seBA))
    L.append("  'more models'    C - B = %+.4f  (paired jackknife 95%% [%+.4f, %+.4f], SE %.4f)" % (dCB, loCB, hiCB, seCB))
    L.append("  total            C - A = %+.4f  (paired jackknife 95%% [%+.4f, %+.4f], SE %.4f)" % (dCA, loCA, hiCA, seCA))
    if abs(dCA) > 1e-9:
        share = dBA / dCA
        share_loo = [(x / y) if abs(y) > 1e-9 else float("nan") for x, y in zip(dBA_loo, dCA_loo)]
        share_loo = [s for s in share_loo if s == s]
        if len(share_loo) == len(anchors):
            se_s, lo_s, hi_s, _ = jack(share, share_loo)
            L.append("  share of the gain that is 'more verdicts' = %.2f  (jackknife 95%% [%.2f, %.2f])" % (share, lo_s, hi_s))
        else:
            se_s = lo_s = hi_s = float("nan")
            L.append("  share of the gain that is 'more verdicts' = %.2f  (share interval undefined in %d folds)" % (share, len(anchors) - len(share_loo)))
        if dBA > dCB and lo_s > 0.5:
            v2 = "PASS"; msg = "prediction CONFIRMED with the interval: the gain is mostly 'more verdicts' (share > 0.5, interval excludes 0.5)"
        elif dBA <= dCB and hi_s < 0.5:
            v2 = "FAIL"; msg = "prediction FAILED with the interval: the gain is mostly 'more models'"
        else:
            v2 = "UNDETERMINED"; msg = ("point estimate says mostly '%s' but the jackknife interval on the share includes 0.5"
                                        % ("more verdicts" if dBA > dCB else "more models"))
    else:
        v2 = "UNDETERMINED"; msg = "no total gain to decompose"
    L.append("  CRITERION (2): %s -> %s" % (msg, v2))
    L.append("  (criterion (2) carries no registered bar; its verdict scores the registered prediction and is UNDETERMINED")
    L.append("   whenever the paired jackknife interval on the share includes one half.)")
    L.append("  comparator: key R = %.4f (12 models) / %.4f (20 models); the key's own interval is [%.4f, %.4f] / [%.4f, %.4f]"
             % (summ["key, 12 models"]["R"], summ["key, 20 models"]["R"], summ["key, 12 models"]["lo"], summ["key, 12 models"]["hi"],
                summ["key, 20 models"]["lo"], summ["key, 20 models"]["hi"]))

    L.append("")
    L.append("=== VERDICTS ===")
    L.append("  (1) merged-board jackknife interval [%.4f, %.4f], lower bound vs 0.70: %s" % (C["lo"], C["hi"], v1))
    L.append("  (2) decomposition A %.4f / B %.4f / C %.4f, more-verdicts %+.4f vs more-models %+.4f: %s" % (A["R"], B["R"], C["R"], dBA, dCB, v2))
    L.append("  fold table cached at %s" % cache_path)

    txt = "\n".join(L); print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
