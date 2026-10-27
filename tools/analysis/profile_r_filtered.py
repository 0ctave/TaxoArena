"""PROFILE-R-FILTERED (registered 2026-09-18 before any code or call, commit 5bd56bb; zero calls) - does the anchor
profile's reliability survive the answer-disagreement filter that halves the newcomer bill?

  python tools/analysis/profile_r_filtered.py --selftest    # synthetic verdicts and predictions; nothing of record is opened
  python tools/analysis/profile_r_filtered.py --dry-run     # pool id, the two cache row counts, kept counts per cache under
                                                            # both conventions, filtered q_distinct per anchor; no R
  python tools/analysis/profile_r_filtered.py --run         # write-once outcome (+ _anchors.csv) from complete caches
      [--anchors-convention A|B|both]   per-anchor intervals for one or both conventions (default both; ~1-2 CPU-h each)

THE REGISTRATION (docs/judge_v2_program.md "Registered 2026-09-18 (before any code or call) - PROFILE-R-FILTERED"; the
last bracket in the programme file wins over this copy), condensed:
  Question: on the merged board restricted to matches whose extracted answers disagree, is the split-half R of the
  within-anchor model order, with its jackknife interval, within the unfiltered value's reach, and which anchors change
  class? The value of the answer is a BILL (~1,550 -> ~800 matches per newcomer), not a claim about any model.
  Hygiene: caches mode=ro, rows pinned x12 9,142 (2,811 judged q) + x20 12,394 (2,646 q) = 21,536, 20 models; x20 never
  read alone; pool p2dca21ab5f4ef3ae first line; only JUDGED questions; anchors = the 14 bareq512_s42 anchors. The filter
  = the two contestants' extracted answers in eval_results.pred DIFFER; INVALID or missing extractions count as
  "disagree" under convention A and are excluded under convention B, both printed; kept counts per cache reconciled by
  name against AGGREGATE's 5,276 of 9,142 and TOPIC-DIFFICULTY's 65.7% differing (~6,007), which do not agree; this
  script's count with its convention is the number of record. No key is read for the filter. Only R is compared, never
  theta levels (PLACEBO-ENTRY: +13% scale under the filter).
  Instrument: PROFILE-INTERVAL-ALL's split-half estimator unchanged (profile_reliability.reliability, 40 halvings,
  random.Random(7), per half jf.board_from -> rj.mm_fit prior 0.5, model-demeaned, Spearman-Brown) on (a) the unfiltered
  merged board (must reproduce 0.7183 to 4 dp: the reproduction gate) and (b) the filtered merged board; board R with the
  leave-one-anchor-out jackknife and halving SD, fixed and re-halved; per anchor the class on the LOWER of the recentred
  question bootstrap (B = 125) and the delete-one-question jackknife (PROFILE-INTERVAL-ALL C2's instrument). Support
  rule: filtered q_distinct < 120 -> counts printed, class UNDETERMINED. Beside (b): the key-built rows on the same
  filtered questions (descriptive) and the filtered / unfiltered q_distinct ratio per anchor (the bill).
  (C1) board R filtered vs unfiltered with intervals and halving SD; (C2) per-anchor class under the filter beside
  PROFILE-INTERVAL-ALL C2's merged classes (PASS Physics 0.9148, Math 0.8833; PASS-WITH-INTERVAL Law 0.7923, Psychology
  0.7882, Business 0.7701, Chemistry 0.7604, Philosophy 0.7334, Other 0.7090, History 0.7063; FAIL Engineering 0.6866,
  Biology 0.3987, Computer science 0.3054, Economics 0.1431, Health -0.0710).
  P1 |R_f - 0.7183| <= 0.05 at the point; P2 no anchor moves more than one class step (UNDETERMINED-by-support is not a
  step); P3 >= 3 anchors read UNDETERMINED by support. Registrar's addition: the filtered R's jackknife interval still
  contains 0.70 (PASS-WITH-INTERVAL or better, not FAIL at the point). Falsifier: R_f < 0.60 at the point (the bill
  cannot be halved; FRAMEWORK L189 step 5 keeps ~1,550; L405 "untested" -> "tested, FAIL"). If R_f >= 0.60 and P1 FAILS:
  "halved at a measured reliability cost of <delta>", no rule changes.
  Outputs: experiment_results/x12_crossdomain/profile_r_filtered_outcome.txt once (+ profile_r_filtered_anchors.csv).

IMPLEMENTATION, and the READINGS CHOSEN where the registration is silent (each stated here before the run):
  * The filter rule of record is the SHIPPED one (src/main/kotlin/taxonomy/arena/MatchFilter.kt AnswerDisagreementFilter):
    trimmed, case-insensitive comparison of the two eval_results.pred strings; a missing or blank prediction is
    UNDETERMINED and KEPT. That is convention A (the filter the deployed scheduler would actually buy) and the PRIMARY
    reading of every criterion. Convention B keeps a match iff both predictions are present and differ, and its
    denominator is the matches with both predictions present (AGGREGATE / SELECTIVE-ORDER's `pa and pb and pa != pb`,
    which compared the FIRST CHARACTER upper-cased; the count of matches where the two normalisations disagree is
    printed, expected 0 on single-letter predictions). "INVALID" as a literal prediction string, if present, is listed
    among the non-letter values and treated as missing under both conventions (it is not an answer).
  * The filtered board: rows = merged verdicts kept by the filter; an anchor's filtered cell = its judged questions with
    >= 1 kept verdict (q_distinct); the halvings are of those questions; a half-profile is the 20-model BT fit on the
    kept verdicts of that half. Cells below 2 x min_cell (50) cannot be halved and print n/a (the estimator's own floor).
  * Board-level intervals: leave-one-anchor-out, 14 folds, SE on the R scale, z = 1.96, centred on the full R; RE-HALVED
    primary, FIXED halvings beside (ANCHOR-PROFILE-INTERVAL). The registrar's addition ("the interval still contains
    0.70, i.e. PASS-WITH-INTERVAL or better, not FAIL at the point") is read on the re-halved interval as HELD iff the
    interval reaches 0.70 (hi >= 0.70; an interval entirely above 0.70 is PASS, better than contained); the literal
    containment lo <= 0.70 <= hi and the board class are printed beside it.
  * Per-anchor instrument = profile_interval_all section (3), reading (i) PROFILE (half-profiles model-demeaned across
    the anchors, r_a = Pearson across the 20 models inside anchor a), SB, mean over 40 halvings; the question bootstrap
    B = 125 x 16 halvings, split on distinct questions, percentile 2.5 / 97.5 RECENTRED on the point (bias printed);
    the delete-one-question jackknife on the first 10 fixed halvings; class on the lower of the two lower bounds
    (classify: PASS lo >= 0.70; PASS-WITH-INTERVAL point >= 0.70; else FAIL); the raw-order reading (ii) printed beside.
    The unfiltered per-anchor CLASSES are the recorded ones (PROFILE-INTERVAL-ALL C2, hard-coded with their source); the
    unfiltered per-anchor R_prof POINTS are recomputed on the fixed halvings and checked against the recorded values to
    4 dp (a second reproduction check, not a gate).
  * Class step = |index(recorded) - index(filtered)| on (PASS, PASS-WITH-INTERVAL, FAIL); an UNDETERMINED-by-support or
    n/a anchor contributes no step. Support rule: filtered q_distinct < 120 (History is 119 UNFILTERED, so it reads
    UNDETERMINED under any filter; stated in the output).
  * Key-built rows: the 20-model key (eval_results.is_correct, the merged roster) on the same filtered questions: board R
    (model-demeaned, 40 halvings) and per-anchor R_prof points; descriptive, no class.
  * McNemar-established rule: no wrong-direction count exists here (nothing is compared to the key's direction); stated,
    not applied. KEY DENOMINATOR: each anchor's judged questions, unfiltered 119-304 / filtered as printed, halved.
  * --selftest opens nothing of record (rule 7 window); --dry-run reads the caches and the eval DB mode=ro and prints
    counts only; --run refuses if either outcome file exists (write-once).
"""
import os, sys, math, random, json, csv, time, argparse, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import profile_reliability as pr
import profile_interval_all as pia

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_r_filtered_outcome.txt")
OUT_CSV = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "profile_r_filtered_anchors.csv")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "prf")
TREE = "bareq512_s42"
POOL = "p2dca21ab5f4ef3ae"
EXCLUDE = "Meta-Llama-3-70B-Instruct"
SEED = 7
REPS = pr.REPS
Z = 1.96
BAR = 0.70
SUPPORT = 120
RECORDED_R = 0.7183
RECORDED_KEY20 = 0.9139
RECORDED_JK = (0.6076, 0.8291)
PIN = dict(n12=9142, n20=12394, n=21536, models=20, q=2811, q20=2646, anchors=14)
RECORDED_COUNTS = {"Philosophy": 132, "Psychology": 260, "Economics": 178, "Other": 211, "Business": 174, "Math": 304,
                   "Computer science": 162, "Law": 271, "Health": 129, "Biology": 181, "History": 119, "Chemistry": 269,
                   "Engineering": 162, "Physics": 259}
# PROFILE-INTERVAL-ALL C2, merged 20-model board, profile reading (experiment_results/x12_crossdomain/profile_interval_all.txt L237-250)
RECORDED_C2 = {"Physics": (0.9148, "PASS"), "Math": (0.8833, "PASS"), "Law": (0.7923, "PASS-WITH-INTERVAL"),
               "Psychology": (0.7882, "PASS-WITH-INTERVAL"), "Business": (0.7701, "PASS-WITH-INTERVAL"),
               "Chemistry": (0.7604, "PASS-WITH-INTERVAL"), "Philosophy": (0.7334, "PASS-WITH-INTERVAL"),
               "Other": (0.7090, "PASS-WITH-INTERVAL"), "History": (0.7063, "PASS-WITH-INTERVAL"),
               "Engineering": (0.6866, "FAIL"), "Biology": (0.3987, "FAIL"), "Computer science": (0.3054, "FAIL"),
               "Economics": (0.1431, "FAIL"), "Health": (-0.0710, "FAIL")}
PRIOR_READINGS = dict(aggregate_kept=5276, aggregate_total=9142, td_same_x12=0.343, td_same_x20=0.482)
CLASS_IDX = {"PASS": 0, "PASS-WITH-INTERVAL": 1, "FAIL": 2}
LETTERS = set("ABCDEFGHIJ")
sb = pr.sb


# ----------------------------------------------------------------------------------------------- the filter
def norm_shipped(p):
    """MatchFilter.kt: trim, case-insensitive; None/blank = missing."""
    if p is None: return None
    s = str(p).strip()
    if not s or s.upper() == "INVALID": return None
    return s.upper()


def norm_record(p):
    """SELECTIVE-ORDER / systematic_budget: (pred or '').strip().upper()[:1]; '' = missing."""
    s = (p or "").strip().upper()[:1]
    return s or None


def verdict(pa, pb):
    """AGREE / DISAGREE / UNDETERMINED on the shipped normalisation."""
    a, b = norm_shipped(pa), norm_shipped(pb)
    if a is None or b is None: return "UNDETERMINED"
    return "AGREE" if a == b else "DISAGREE"


def split_rows(rows, P):
    """rows: (a, b, q, w). Returns {'A': kept rows, 'B': kept rows, 'counts': {...}} for one cache."""
    c = defaultdict(int); A = []; B = []; norm_mismatch = 0
    for a, b, q, w in rows:
        pa, pb = P.get(q, {}).get(a), P.get(q, {}).get(b)
        v = verdict(pa, pb); c[v] += 1
        ra, rb = norm_record(pa), norm_record(pb)
        v_rec = "UNDETERMINED" if (ra is None or rb is None) else ("AGREE" if ra == rb else "DISAGREE")
        if v_rec != v: norm_mismatch += 1
        if v != "AGREE": A.append((a, b, q, w))
        if v == "DISAGREE": B.append((a, b, q, w))
    n = len(rows); both = c["AGREE"] + c["DISAGREE"]
    return dict(A=A, B=B, n=n, agree=c["AGREE"], disagree=c["DISAGREE"], undetermined=c["UNDETERMINED"], both=both,
                keptA=len(A), keptB=len(B), shareA=len(A) / n if n else float("nan"), shareB=len(B) / both if both else float("nan"),
                same_share=c["AGREE"] / n if n else float("nan"), norm_mismatch=norm_mismatch)


# ----------------------------------------------------------------------------------------------- builders and readers
def jb_for(by, models):
    import judge_free_tests as jf
    def jb(cqs):
        rs = [r for q in cqs for r in by[q]]
        if len({r[2] for r in rs}) < 10: return None
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs], models)
    return jb


def kb_for(K, models):
    def kb(cqs):
        d = {}
        for m in models:
            v = [K[q][m] for q in cqs if q in K and m in K[q]]
            if v: d[m] = sum(v) / len(v)
        return d if len(d) == len(models) else None
    return kb


def board_level(cells, qsel, build, models, progress=None):
    """R on fixed halvings (with sides kept for the per-anchor jackknife), halving SD, LOAO jackknife fixed and re-halved."""
    anchors = list(cells); sides = []
    per_rep = pia.halvings_fixed(cells, qsel, build, models, random.Random(SEED), sides=sides)
    r, sd, n = pia.mean_r(per_rep)
    R = sb(r)
    loo_fx = [sb(pia.mean_r(per_rep, a)[0]) for a in anchors]
    loo_re = []
    for a in anchors:
        sub = {c: v for c, v in cells.items() if c != a}
        r_i, _, _ = pr.reliability(sub, qsel, build, models, random.Random(SEED))
        loo_re.append(sb(r_i))
        if progress: progress("drop %s r_-i %.4f" % (a, r_i))
    se_fx, lo_fx, hi_fx = pia.jack(R, loo_fx); se_re, lo_re, hi_re = pia.jack(R, loo_re)
    return dict(r=r, sd=sd, n=n, R=R, lo_fx=lo_fx, hi_fx=hi_fx, se_fx=se_fx, lo_re=lo_re, hi_re=hi_re, se_re=se_re,
                loo_re=dict(zip(anchors, loo_re)), loo_fx=dict(zip(anchors, loo_fx)), per_rep=per_rep, sides=sides)


def boot_split(cells, rng):
    cut1 = {}; cut2 = {}
    for c, cqs in cells.items():
        n = len(cqs); draw = [cqs[rng.randrange(n)] for _ in range(n)]
        mult = defaultdict(int)
        for q in draw: mult[q] += 1
        ids = sorted(mult); rng.shuffle(ids)
        s1 = []; s2 = []; acc = 0
        for q in ids:
            if acc < n / 2: s1.extend([q] * mult[q]); acc += mult[q]
            else: s2.extend([q] * mult[q])
        cut1[c] = s1; cut2[c] = s2
    return cut1, cut2


def anchor_jackknife(anchors, per_rep, sides, build, models, H):
    """profile_interval_all section (3): delete-one-question jackknife of the per-anchor split-half r on H fixed halvings."""
    out = {}
    for a in anchors:
        loo_p = defaultdict(list); loo_r = defaultdict(list)
        for h in range(min(H, len(per_rep))):
            P = per_rep[h]
            if a not in sides[h]: continue
            s1, s2 = sides[h][a]
            others = [p for p in P if p[0] != a]
            d1 = {m: x for c, m, x, y in P if c == a}; d2 = {m: y for c, m, x, y in P if c == a}
            for side_idx, side in ((0, s1), (1, s2)):
                for q in side:
                    new = build([x for x in side if x != q])
                    if not new: continue
                    if side_idx == 0: pa_ = [(a, m, new[m], d2[m]) for m in models if m in new and m in d2]
                    else: pa_ = [(a, m, d1[m], new[m]) for m in models if m in d1 and m in new]
                    rp, rr, _ = pia.per_anchor_r(others + pa_)[a]
                    loo_p[q].append(rp); loo_r[q].append(rr)
        qs_a = sorted(loo_p)
        th_p = [sb(pia.mean_sd(loo_p[q])[0]) for q in qs_a]; th_r = [sb(pia.mean_sd(loo_r[q])[0]) for q in qs_a]
        th_p = [t for t in th_p if t == t]; th_r = [t for t in th_r if t == t]
        se_p = pia.jack(0.0, th_p)[0] if len(th_p) > 1 else float("nan")
        se_r = pia.jack(0.0, th_r)[0] if len(th_r) > 1 else float("nan")
        out[a] = (se_p, se_r, len(qs_a))
    return out


def per_anchor(cells, bl, build, models, boot_b, boot_h, jack_h, progress=None):
    """Per-anchor R_prof / R_raw points on the fixed halvings, recentred question bootstrap, delete-one-question
    jackknife, class on the lower of the two lower bounds. Returns {anchor: row}."""
    anchors = list(cells); per_rep = bl["per_rep"]; sides = bl["sides"]
    pa = defaultdict(lambda: ([], [], []))
    for P in per_rep:
        for c, (r1, r2, r3) in pia.per_anchor_r(P).items():
            pa[c][0].append(r1); pa[c][1].append(r2); pa[c][2].append(r3)
    point = {c: (pia.mean_sd(v[0]), pia.mean_sd(v[1]), pia.mean_sd(v[2])) for c, v in pa.items()}
    t0 = time.time()
    jk = anchor_jackknife(anchors, per_rep, sides, build, models, jack_h)
    if progress: progress("jackknife done %.0fs" % (time.time() - t0))
    rngb = random.Random(2026)
    boot = defaultdict(lambda: ([], []))
    for b in range(boot_b):
        acc = defaultdict(lambda: ([], []))
        for h in range(boot_h):
            cut1, cut2 = boot_split(cells, rngb)
            P = []
            for c in anchors:
                d1 = build(cut1[c]); d2 = build(cut2[c])
                if not d1 or not d2: continue
                for m in models:
                    if m in d1 and m in d2: P.append((c, m, d1[m], d2[m]))
            for c, (r1, r2, _) in pia.per_anchor_r(P).items():
                acc[c][0].append(r1); acc[c][1].append(r2)
        for c in acc:
            boot[c][0].append(sb(pia.mean_sd(acc[c][0])[0])); boot[c][1].append(sb(pia.mean_sd(acc[c][1])[0]))
        if progress and b % 25 == 0: progress("boot %d %.0fs" % (b, time.time() - t0))
    rows = {}
    for c in anchors:
        if c not in point:
            rows[c] = dict(q=len(cells[c]), R_prof=float("nan"), cls="n/a"); continue
        Rp = sb(point[c][0][0]); Rr = sb(point[c][1][0])
        plo, phi = pia.pct(boot[c][0], 0.025), pia.pct(boot[c][0], 0.975); pmu = pia.mean_sd(boot[c][0])[0]
        rlo, rhi = pia.pct(boot[c][1], 0.025), pia.pct(boot[c][1], 0.975); rmu = pia.mean_sd(boot[c][1])[0]
        bias_p = pmu - Rp; bias_r = rmu - Rr
        cplo, cphi = plo - bias_p, phi - bias_p; crlo, crhi = rlo - bias_r, rhi - bias_r
        se_p, se_r, nq = jk.get(c, (float("nan"), float("nan"), 0))
        jlo_p, jhi_p = Rp - Z * se_p, Rp + Z * se_p; jlo_r, jhi_r = Rr - Z * se_r, Rr + Z * se_r
        lows_p = [x for x in (cplo, jlo_p) if x == x]; lows_r = [x for x in (crlo, jlo_r) if x == x]
        low_p = min(lows_p) if lows_p else float("nan"); low_r = min(lows_r) if lows_r else float("nan")
        rows[c] = dict(q=len(cells[c]), r_prof=point[c][0][0], R_prof=Rp, sd_prof=point[c][0][1], boot_prof=(cplo, cphi),
                       boot_prof_raw=(plo, phi), bias_prof=bias_p, jk_prof=(jlo_p, jhi_p), se_jk_prof=se_p, low_prof=low_p,
                       cls=pia.classify(Rp, low_p) if low_p == low_p else "n/a",
                       R_raw=Rr, boot_raw=(crlo, crhi), jk_raw=(jlo_r, jhi_r), low_raw=low_r,
                       cls_raw=pia.classify(Rr, low_r) if low_r == low_r else "n/a", nq_jk=nq)
    return rows


def per_anchor_points(cells, per_rep):
    """R_prof points only (fixed halvings), for the unfiltered reproduction check and the key rows."""
    pa = defaultdict(list)
    for P in per_rep:
        for c, (r1, _, _) in pia.per_anchor_r(P).items(): pa[c].append(r1)
    return {c: sb(pia.mean_sd(v)[0]) for c, v in pa.items()}


def class_step(rec, new):
    if rec not in CLASS_IDX or new not in CLASS_IDX: return None
    return abs(CLASS_IDX[rec] - CLASS_IDX[new])


# ----------------------------------------------------------------------------------------------- data of record
def load_record(say):
    import rejudge_grok as rj, rubric_p8 as p8, rubric_512 as r512, stack_judge as sj, x20_replications as xr
    assert abs(rj.PRIOR - 0.5) < 1e-12, "rj.PRIOR is %r, the record pins 0.5" % rj.PRIOR
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    x12_path = sj.cache_path()
    con12 = sqlite3.connect("file:%s?mode=ro" % x12_path.replace("\\", "/"), uri=True)
    r12 = [(a, b, q, w) for a, b, q, w, iv in con12.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not iv]
    con12.close()
    con20 = sqlite3.connect("file:%s?mode=ro" % xr.X20.replace("\\", "/"), uri=True)
    r20 = [(a, b, q, w) for a, b, q, w, iv in con20.execute("SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not iv]
    con20.close()
    say("  x12 cache %s: %d valid verdicts (pinned %d), %d judged q" % (os.path.basename(x12_path), len(r12), PIN["n12"], len({r[2] for r in r12})))
    say("  x20 cache %s: %d valid verdicts (pinned %d), %d judged q; never read alone (0 verdicts on the 66 original pairs)"
        % (os.path.basename(xr.X20), len(r20), PIN["n20"], len({r[2] for r in r20})))
    if len(r12) != PIN["n12"] or len(r20) != PIN["n20"] or len({r[2] for r in r20}) != PIN["q20"]:
        raise SystemExit("[PIN] caches are not the board of record")
    rows_m = r12 + r20
    models12 = sorted(p8.ARENA12); models20 = sorted({r[0] for r in rows_m} | {r[1] for r in rows_m})
    if len(models20) != PIN["models"] or EXCLUDE in models20 or not set(models12) <= set(models20):
        raise SystemExit("[PIN] merged model set %d / %s" % (len(models20), EXCLUDE in models20))
    say("  merged board: %d verdicts (pinned %d), %d models, %s absent" % (len(rows_m), PIN["n"], len(models20), EXCLUDE))

    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    K = defaultdict(dict); P = defaultdict(dict); raw_pred = defaultdict(int)
    for q, m, pd, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in models20:
            K[q][m] = int(c or 0); P[q][m] = pd
            s = norm_shipped(pd)
            if s is None or s not in LETTERS: raw_pred[repr(pd)[:24]] += 1
    ev.close()

    route = r512.primary_routing(TREE)
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anc = r512.anchor_fn(nodes)
    bym = defaultdict(list)
    for r in rows_m: bym[r[2]].append(r)
    qs = sorted(set(route) & set(bym)); qsel = set(qs)
    if len(qs) != PIN["q"] or not set(bym) <= pool or len(bym) != PIN["q"]:
        raise SystemExit("[PIN] judged questions: merged %d, routed+judged %d, outside pool %d" % (len(bym), len(qs), len(set(bym) - pool)))
    anc_cells = defaultdict(list)
    for q in qs: anc_cells[anc(route[q])].append(q)          # the recorded dict order (the halvings depend on it)
    usable = {c: v for c, v in anc_cells.items() if len(v) >= 50}
    if {c: len(v) for c, v in usable.items()} != RECORDED_COUNTS:
        raise SystemExit("[PIN] anchor counts differ from the recorded run")
    say("  pool %s: %d routed + judged questions, all in the reserved pool; %d anchors with the recorded counts" % (POOL, len(qs), len(usable)))
    # the filter, per cache
    f12 = split_rows(r12, P); f20 = split_rows(r20, P)
    return dict(r12=r12, r20=r20, rows_m=rows_m, models20=models20, K=K, P=P, usable=usable, qsel=qsel, anc_of=lambda q: anc(route[q]),
                f12=f12, f20=f20, raw_pred=raw_pred)


def filtered_cells(D, conv):
    rows = D["f12"][conv] + D["f20"][conv]
    by = defaultdict(list)
    for r in rows: by[r[2]].append(r)
    cells = {c: [q for q in v if q in by] for c, v in D["usable"].items()}
    return rows, by, cells


def filter_report(D, say):
    f12, f20 = D["f12"], D["f20"]
    say("")
    say("--- THE FILTER (eval_results.pred of the two contestants; the shipped MatchFilter.kt rule; no key read) ---")
    say("  non-letter / missing prediction values seen on the 20-model roster (value: rows): %s"
        % (", ".join("%s: %d" % kv for kv in sorted(D["raw_pred"].items(), key=lambda kv: -kv[1])[:12]) or "none"))
    say("  %-6s %7s %8s %9s %12s | %-28s | %-34s" % ("cache", "matches", "AGREE", "DISAGREE", "UNDETERMINED", "conv A kept (missing = kept)", "conv B kept (missing excluded)"))
    for name, f in (("x12", f12), ("x20", f20)):
        say("  %-6s %7d %8d %9d %12d | %6d of %6d = %5.1f%%       | %6d of %6d (both present) = %5.1f%%"
            % (name, f["n"], f["agree"], f["disagree"], f["undetermined"], f["keptA"], f["n"], 100 * f["shareA"], f["keptB"], f["both"], 100 * f["shareB"]))
    tot = dict(n=f12["n"] + f20["n"], keptA=f12["keptA"] + f20["keptA"], keptB=f12["keptB"] + f20["keptB"], both=f12["both"] + f20["both"])
    say("  %-6s %7d %8s %9s %12s | %6d of %6d = %5.1f%%       | %6d of %6d (both present) = %5.1f%%"
        % ("merged", tot["n"], "", "", "", tot["keptA"], tot["n"], 100 * tot["keptA"] / tot["n"], tot["keptB"], tot["both"], 100 * tot["keptB"] / max(1, tot["both"])))
    say("  normalisation check: matches whose verdict differs between the shipped rule (trim, case-insensitive, whole string) and the")
    say("  record's first-character rule: x12 %d, x20 %d" % (f12["norm_mismatch"], f20["norm_mismatch"]))
    say("  RECONCILIATION against the two prior readings (x12, 9,142):")
    say("    AGGREGATE arm B kept 5,276 (both present and differ, first character): this script's DISAGREE count = %d (%s)"
        % (f12["disagree"], "equal" if f12["disagree"] == PRIOR_READINGS["aggregate_kept"] else "DIFFERS by %+d" % (f12["disagree"] - PRIOR_READINGS["aggregate_kept"])))
    say("    TOPIC-DIFFICULTY 34.3%% same predicted letter -> 65.7%% differing (~6,007): this script's AGREE share = %.1f%% (same letter);"
        % (100 * f12["same_share"]))
    say("    1 - AGREE share = %.1f%% = convention A's kept share (DISAGREE + UNDETERMINED = %d): the two prior figures differ by the"
        % (100 * f12["shareA"], f12["keptA"]))
    say("    %d matches with a missing prediction (kept by the shipped rule, dropped by AGGREGATE's). Convention A's %d of %d"
        % (f12["undetermined"], f12["keptA"], f12["n"]))
    say("    (%.1f%%) is the number of record for THIS test. The 57.7%% vs 65.7%% gap is the missing-prediction convention; the residual"
        % (100 * f12["shareA"]))
    say("    %+.1f pp between this script's same-letter share and TOPIC-DIFFICULTY's 34.3%% (~%d matches) is NOT explained here and is"
        % (100 * f12["same_share"] - 100 * PRIOR_READINGS["td_same_x12"], abs(round(f12["n"] * PRIOR_READINGS["td_same_x12"]) - f12["agree"])))
    say("    left for the checker (candidate: TOPIC-DIFFICULTY's match set or prediction column differs).")
    say("    x20: same letter %.1f%% (TOPIC-DIFFICULTY 48.2%%, residual %+.1f pp), UNDETERMINED %d, conv A kept %.1f%%"
        % (100 * f20["same_share"], 100 * f20["same_share"] - 100 * PRIOR_READINGS["td_same_x20"], f20["undetermined"], 100 * f20["shareA"]))
    say("  KEY DENOMINATOR per anchor (judged questions; unfiltered / conv A q_distinct / conv B q_distinct; kept matches A / B):")
    for conv in ("A", "B"):
        _, by, cells = filtered_cells(D, conv)
        D["cells_" + conv] = cells; D["by_" + conv] = by
    for c in D["usable"]:
        qa = len(D["cells_A"][c]); qb = len(D["cells_B"][c]); nu = sum(len(D["by_m"][q]) for q in D["usable"][c])
        na = sum(len(D["by_A"][q]) for q in D["cells_A"][c]); nb = sum(len(D["by_B"][q]) for q in D["cells_B"][c])
        say("    %-18s %4d / %4d (%.2f) / %4d (%.2f)   matches %5d / %5d (%.2f) / %5d (%.2f)%s"
            % (c, len(D["usable"][c]), qa, qa / len(D["usable"][c]), qb, qb / len(D["usable"][c]), nu, na, na / nu, nb, nb / nu,
               "   <- support rule: q_distinct < %d under A" % SUPPORT if qa < SUPPORT else ""))
    say("  (History is 119 UNFILTERED, below the %d support rule before any filter: it reads UNDETERMINED-by-support under any filter.)" % SUPPORT)


# ----------------------------------------------------------------------------------------------- the readout
def run(D, L, conv_anchors, boot_b, boot_h, jack_h):
    say = L.append
    models = D["models20"]; usable = D["usable"]; qsel = D["qsel"]
    t0 = time.time()
    prog = lambda s: print("   ", s, "%.0fs" % (time.time() - t0), flush=True)
    # ---- reproduction gate
    jb_u = jb_for(D["by_m"], models)
    bl_u = board_level(usable, qsel, jb_u, models, progress=prog)
    gate = "%.4f" % bl_u["R"] == "%.4f" % RECORDED_R
    say("")
    say("=== REPRODUCTION GATE: unfiltered merged board R on the fixed halvings ===")
    say("  R = %.4f (r %.4f, halving SD %.4f, %d halvings) vs recorded 0.7183: %s; jackknife re-halved [%.4f, %.4f] (recorded [0.6076, 0.8291]), fixed [%.4f, %.4f]"
        % (bl_u["R"], bl_u["r"], bl_u["sd"], bl_u["n"], "REPRODUCED" if gate else "NOT REPRODUCED", bl_u["lo_re"], bl_u["hi_re"], bl_u["lo_fx"], bl_u["hi_fx"]))
    kb = kb_for(D["K"], models)
    r_ku, _, _ = pr.reliability(usable, qsel, kb, models, random.Random(SEED))
    say("  key, 20 models, unfiltered: R = %.4f (recorded 0.9139)" % sb(r_ku))
    pts_u = per_anchor_points(usable, bl_u["per_rep"])
    mism = [(c, pts_u[c], RECORDED_C2[c][0]) for c in usable if "%.4f" % pts_u[c] != "%.4f" % RECORDED_C2[c][0]]
    say("  per-anchor R_prof points on the fixed halvings vs PROFILE-INTERVAL-ALL C2 (14 anchors): %s"
        % ("all 14 reproduced to 4 dp" if not mism else "MISMATCH " + ", ".join("%s %.4f vs %.4f" % t for t in mism)))
    if not gate:
        say("  GATE FAILED: nothing below is a number of record.")
        return None
    # ---- filtered boards, both conventions
    res = {}
    say("")
    say("=== C1: board-level R, filtered vs unfiltered (instrument: profile_reliability.reliability, 40 halvings, Random(7), model-demeaned, SB) ===")
    say("  %-34s %6s %8s %8s %8s  %-18s %-18s %s" % ("board", "anchors", "q_total", "r", "R(SB)", "jk RE-HALVED 95%", "jk FIXED 95%", "halvSD"))
    say("  %-34s %6d %8d %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]   %.4f"
        % ("unfiltered merged (recorded 0.7183)", len(usable), sum(len(v) for v in usable.values()), bl_u["r"], bl_u["R"], bl_u["lo_re"], bl_u["hi_re"], bl_u["lo_fx"], bl_u["hi_fx"], bl_u["sd"]))
    for conv in ("A", "B"):
        cells = D["cells_" + conv]; by = D["by_" + conv]
        halvable = {c: v for c, v in cells.items() if len(v) >= 50}
        jb_f = jb_for(by, models)
        bl = board_level(halvable, qsel, jb_f, models, progress=prog)
        r_kf, _, _ = pr.reliability(halvable, qsel, kb, models, random.Random(SEED))
        pts_k = per_anchor_points(halvable, pia.halvings_fixed(halvable, qsel, kb, models, random.Random(SEED)))
        res[conv] = dict(bl=bl, cells=cells, halvable=halvable, jb=jb_f, key_R=sb(r_kf), key_pts=pts_k)
        say("  %-34s %6d %8d %8.4f %8.4f  [%6.4f, %6.4f]   [%6.4f, %6.4f]   %.4f"
            % ("filtered conv %s (%s)" % (conv, "missing kept" if conv == "A" else "missing excluded"), len(halvable), sum(len(v) for v in halvable.values()),
               bl["r"], bl["R"], bl["lo_re"], bl["hi_re"], bl["lo_fx"], bl["hi_fx"], bl["sd"]))
        say("  %-34s %6d %8d %8s %8.4f   (descriptive; unfiltered key-20 %.4f)" % ("  key, 20 models, same filtered q", len(halvable), sum(len(v) for v in halvable.values()), "", sb(r_kf), sb(r_ku)))
        print("board conv", conv, "R %.4f" % bl["R"], flush=True)
    say("  denominators: the 14 anchors' filtered judged questions (listed in the filter table above); anchors below 50 filtered questions")
    say("  cannot be halved and are absent from that board (count printed in 'anchors').")
    for conv in ("A", "B"):
        bl = res[conv]["bl"]
        say("  per-anchor leave-one-out R, conv %s (re-halved): %s" % (conv, ", ".join("drop %s %.4f" % (a, bl["loo_re"][a]) for a in sorted(bl["loo_re"], key=lambda a: bl["loo_re"][a]))))
    # ---- C2 per-anchor classes
    say("")
    say("=== C2: per-anchor class under the filter (profile reading; class on the LOWER of the recentred question bootstrap B = %d x %d and the" % (boot_b, boot_h))
    say("    delete-one-question jackknife on %d fixed halvings), beside PROFILE-INTERVAL-ALL C2's recorded merged classes; support rule q_distinct < %d ===" % (jack_h, SUPPORT))
    convs = ["A", "B"] if conv_anchors == "both" else [conv_anchors]
    table = {}
    for conv in convs:
        rows = per_anchor(res[conv]["halvable"], res[conv]["bl"], res[conv]["jb"], models, boot_b, boot_h, jack_h, progress=lambda s: prog("anchors conv %s %s" % (conv, s)))
        for c in usable:
            if c not in rows: rows[c] = dict(q=len(res[conv]["cells"][c]), R_prof=float("nan"), cls="n/a")
            rows[c]["support"] = rows[c]["q"] >= SUPPORT
            rows[c]["cls_final"] = rows[c]["cls"] if rows[c]["support"] else "UNDETERMINED-by-support"
            rows[c]["step"] = class_step(RECORDED_C2[c][1], rows[c]["cls"]) if rows[c]["support"] else None
        table[conv] = rows
        say("")
        say("  --- filtered, convention %s ---" % conv)
        say("  %-18s %4s %4s  %-30s | %8s %-17s %+6s %-17s %-8s %-24s %4s | %8s %-8s" %
            ("anchor", "q_u", "q_f", "recorded (PROFILE-INTERVAL-ALL C2)", "R_prof", "boot95 recentred", "bias", "jackknife 95%", "low", "class (filtered)", "step", "key R_f", "R_raw"))
        for c in sorted(usable, key=lambda a: RECORDED_C2[a][0]):
            r = rows[c]; rec = RECORDED_C2[c]
            if r["cls"] == "n/a":
                say("  %-18s %4d %4d  %-30s | %8s %-17s %6s %-17s %-8s %-24s %4s | %8s"
                    % (c, len(usable[c]), r["q"], "%.4f %s" % rec, "n/a", "", "", "", "", r["cls_final"], "-", "%.4f" % res[conv]["key_pts"].get(c, float("nan"))))
                continue
            say("  %-18s %4d %4d  %-30s | %8.4f [%6.4f, %6.4f] %+6.3f [%6.4f, %6.4f] %8.4f %-24s %4s | %8.4f %8.4f"
                % (c, len(usable[c]), r["q"], "%.4f %s" % rec, r["R_prof"], r["boot_prof"][0], r["boot_prof"][1], r["bias_prof"], r["jk_prof"][0], r["jk_prof"][1],
                   r["low_prof"], r["cls_final"], "-" if r["step"] is None else str(r["step"]), res[conv]["key_pts"].get(c, float("nan")), r["R_raw"]))
        counts = defaultdict(int)
        for c in usable: counts[rows[c]["cls_final"]] += 1
        say("  classes conv %s: %s (recorded unfiltered: PASS 2 / PASS-WITH-INTERVAL 7 / FAIL 5)" % (conv, dict(counts)))
    return dict(bl_u=bl_u, res=res, table=table, gate=gate, convs=convs)


def verdicts(D, L, R):
    say = L.append
    say("")
    say("=== PREDICTIONS, REGISTRAR'S ADDITION AND FALSIFIER (convention A = the shipped scheduler's rule, PRIMARY; B beside) ===")
    if R is None:
        say("  REPRODUCTION GATE FAILED: nothing is scored."); return
    out = {}
    for conv in ("A", "B"):
        bl = R["res"][conv]["bl"]; Rf = bl["R"]
        p1 = "HELD" if abs(Rf - RECORDED_R) <= 0.05 else "FAILED"
        cls = "PASS" if bl["lo_re"] >= BAR else ("PASS-WITH-INTERVAL" if Rf >= BAR else "FAIL")
        reg = "HELD" if bl["hi_re"] >= BAR else "FAILED"
        contains = bl["lo_re"] <= BAR <= bl["hi_re"]
        fals = Rf < 0.60
        rows = R["table"].get(conv)
        if rows:
            steps = [rows[c]["step"] for c in D["usable"] if rows[c]["step"] is not None]
            undet = [c for c in D["usable"] if not rows[c]["support"]]
            p2 = "HELD" if (steps and max(steps) <= 1) or not steps else "FAILED"
            p3 = "HELD" if len(undet) >= 3 else "FAILED"
            movers = [(c, RECORDED_C2[c][1], rows[c]["cls"], rows[c]["step"]) for c in D["usable"] if rows[c]["step"]]
        else:
            steps = []; undet = [c for c in D["usable"] if len(R["res"][conv]["cells"][c]) < SUPPORT]; p2 = "not read (per-anchor intervals not run for this convention)"
            p3 = "HELD" if len(undet) >= 3 else "FAILED"; movers = []
        say("  --- convention %s: R_f = %.4f, re-halved jk [%.4f, %.4f], fixed jk [%.4f, %.4f], halving SD %.4f; delta vs 0.7183 = %+.4f ---"
            % (conv, Rf, bl["lo_re"], bl["hi_re"], bl["lo_fx"], bl["hi_fx"], bl["sd"], Rf - RECORDED_R))
        say("    P1 |R_f - 0.7183| <= 0.05 at the point: %s" % p1)
        say("    P2 no anchor moves more than one class step (supported anchors only): %s%s"
            % (p2, "" if not movers else "; movers: " + ", ".join("%s %s -> %s (%d)" % m for m in movers)))
        say("    P3 >= 3 anchors UNDETERMINED by support (q_distinct < %d): %s (%d: %s)" % (SUPPORT, p3, len(undet), ", ".join("%s %d" % (c, len(R["res"][conv]["cells"][c])) for c in undet) or "none"))
        say("    registrar's addition, the filtered jackknife interval still reaches 0.70 (class %s): %s (literal containment of 0.70: %s)" % (cls, reg, "yes" if contains else "no"))
        say("    FALSIFIER R_f < 0.60 at the point: %s" % ("FIRES" if fals else "silent"))
        out[conv] = dict(Rf=Rf, p1=p1, p2=p2, p3=p3, reg=reg, cls=cls, fals=fals, undet=undet)
    A = out["A"]
    say("")
    say("=== VERDICT LINES ===")
    say("  C1: unfiltered R %.4f [%.4f, %.4f] (recorded 0.7183 [0.6076, 0.8291], reproduced); filtered conv A R %.4f [%.4f, %.4f], conv B %.4f [%.4f, %.4f];"
        % (R["bl_u"]["R"], R["bl_u"]["lo_re"], R["bl_u"]["hi_re"], A["Rf"], R["res"]["A"]["bl"]["lo_re"], R["res"]["A"]["bl"]["hi_re"], out["B"]["Rf"], R["res"]["B"]["bl"]["lo_re"], R["res"]["B"]["bl"]["hi_re"]))
    say("      key-20 on the same filtered questions: conv A %.4f, conv B %.4f (unfiltered %.4f); kept matches: x12 %d / %d, x20 %d / %d (conv A)"
        % (R["res"]["A"]["key_R"], R["res"]["B"]["key_R"], RECORDED_KEY20, D["f12"]["keptA"], D["f12"]["n"], D["f20"]["keptA"], D["f20"]["n"]))
    for conv in R["convs"]:
        rows = R["table"][conv]; counts = defaultdict(int)
        for c in D["usable"]: counts[rows[c]["cls_final"]] += 1
        say("  C2 conv %s: %s; UNDETERMINED-by-support: %s" % (conv, dict(counts), ", ".join(out[conv]["undet"]) or "none"))
    say("  P1 %s | P2 %s | P3 %s | registrar's addition %s (%s) | FALSIFIER %s   [convention A, primary]" % (A["p1"], A["p2"], A["p3"], A["reg"], A["cls"], "FIRES" if A["fals"] else "silent"))
    say("  conv B beside: P1 %s | P2 %s | P3 %s | registrar's addition %s (%s) | falsifier %s" % (out["B"]["p1"], out["B"]["p2"], out["B"]["p3"], out["B"]["reg"], out["B"]["cls"], "FIRES" if out["B"]["fals"] else "silent"))
    if A["fals"]:
        say("  CONSEQUENCE (registered): the filter destroys the profile; the newcomer's profile-coverage bill is NOT halved; FRAMEWORK L189 step 5")
        say("  keeps ~1,550 unfiltered matches per model; L405 'untested' -> 'tested, FAIL' by insertion. FILTER-BOARD, ORACLE and NEWCOMER-PLACEMENT-LIVE stand.")
    elif A["p1"] == "FAILED":
        say("  CONSEQUENCE (registered): the bill is recorded as 'halved at a measured reliability cost of %+.4f' (R_f %.4f vs 0.7183); no rule changes." % (A["Rf"] - RECORDED_R, A["Rf"]))
    else:
        say("  CONSEQUENCE (registered, C1 HELD and the falsifier silent): FRAMEWORK L189 step 5 may quote the filtered bill by insertion with R_f %.4f beside it;" % A["Rf"])
        say("  UNDETERMINED-by-support anchors (%s) keep the unfiltered density." % (", ".join(A["undet"]) or "none"))
    say("  No model's theta or position was read; only R was compared (PLACEBO-ENTRY: the theta scale is ~13%% wider under the filter).")


def write_csv(D, R, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["anchor", "q_unfiltered", "q_filtered_A", "q_filtered_B", "ratio_A", "ratio_B", "matches_unfiltered", "matches_A", "matches_B",
                    "recorded_R_prof", "recorded_class", "R_prof_A", "boot_lo_A", "boot_hi_A", "jk_lo_A", "jk_hi_A", "low_A", "class_A", "step_A",
                    "R_prof_B", "boot_lo_B", "boot_hi_B", "jk_lo_B", "jk_hi_B", "low_B", "class_B", "step_B", "key_R_prof_A", "key_R_prof_B", "R_raw_A", "R_raw_B"])
        for c in D["usable"]:
            qa = len(R["res"]["A"]["cells"][c]); qb = len(R["res"]["B"]["cells"][c]); qu = len(D["usable"][c])
            nu = sum(len(D["by_m"][q]) for q in D["usable"][c]); na = sum(len(D["by_A"][q]) for q in R["res"]["A"]["cells"][c]); nb = sum(len(D["by_B"][q]) for q in R["res"]["B"]["cells"][c])
            row = [c, qu, qa, qb, "%.3f" % (qa / qu), "%.3f" % (qb / qu), nu, na, nb, "%.4f" % RECORDED_C2[c][0], RECORDED_C2[c][1]]
            for conv in ("A", "B"):
                r = R["table"].get(conv, {}).get(c)
                if not r or r.get("cls") == "n/a":
                    row += ["", "", "", "", "", "", (r or {}).get("cls_final", "not run"), ""]
                else:
                    row += ["%.4f" % r["R_prof"], "%.4f" % r["boot_prof"][0], "%.4f" % r["boot_prof"][1], "%.4f" % r["jk_prof"][0], "%.4f" % r["jk_prof"][1],
                            "%.4f" % r["low_prof"], r["cls_final"], "" if r["step"] is None else r["step"]]
            row += ["%.4f" % R["res"]["A"]["key_pts"].get(c, float("nan")), "%.4f" % R["res"]["B"]["key_pts"].get(c, float("nan"))]
            row += ["%.4f" % R["table"][k][c]["R_raw"] if k in R["table"] and R["table"][k][c].get("cls") != "n/a" else "" for k in ("A", "B")]
            w.writerow(row)


# ----------------------------------------------------------------------------------------------- selftest
def synthetic(seed=3, n_models=20, n_anchors=14, q_per=(150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 100, 100, 100)):
    """Synthetic board: per-anchor true theta = global + planted deviation (strong in the first anchors, none in the last
    ones); ~7 matches per question drawn Bernoulli(logistic(dtheta)); predictions: a letter per (q, m), agreeing with a
    probability that rises with both models' accuracy so the filter has something to cut; some missing / 'INVALID'."""
    rng = random.Random(seed)
    models = ["m%02d" % i for i in range(n_models)]
    glob = [rng.gauss(0, 1.0) for _ in models]
    usable = {}; by = defaultdict(list); P = defaultdict(dict); K = defaultdict(dict); theta = {}
    qid = 0
    for j in range(n_anchors):
        c = "A%02d" % j
        dev_scale = 1.2 if j < 5 else (0.5 if j < 8 else 0.0)      # 0-4 strong, 5-7 moderate, 8-13 none (11-13 small)
        theta[c] = [g + rng.gauss(0, dev_scale) for g in glob]
        usable[c] = []
        for _ in range(q_per[j]):
            qid += 1; usable[c].append(qid)
            for i, m in enumerate(models):
                acc = 1 / (1 + math.exp(-(theta[c][i] * 0.8)))
                right = rng.random() < acc; K[qid][m] = int(right)
                u = rng.random()
                P[qid][m] = "A" if right else (None if u < 0.04 else ("INVALID" if u < 0.06 else rng.choice("BCDEFGHIJ")))
            for _ in range(7):
                a, b = rng.sample(range(n_models), 2)
                pa = 1 / (1 + math.exp(-(theta[c][a] - theta[c][b])))
                w = models[a] if rng.random() < pa else models[b]
                if rng.random() < 0.15: w = "TIE"
                by[qid].append((models[a], models[b], qid, w))
    return dict(models20=models, usable=usable, by_m=by, P=P, K=K, qsel=set(q for v in usable.values() for q in v), theta=theta)


def selftest(boot_b, boot_h, jack_h):
    print("=== PROFILE-R-FILTERED --selftest (synthetic verdicts and predictions; nothing of record is opened) ===")
    S = synthetic(); models = S["models20"]
    rows = [r for q in S["by_m"] for r in S["by_m"][q]]
    f = split_rows(rows, S["P"])
    print("  filter: %d matches: AGREE %d, DISAGREE %d, UNDETERMINED %d; conv A kept %d (%.1f%%), conv B kept %d of %d both-present (%.1f%%); norm mismatches %d"
          % (f["n"], f["agree"], f["disagree"], f["undetermined"], f["keptA"], 100 * f["shareA"], f["keptB"], f["both"], 100 * f["shareB"], f["norm_mismatch"]))
    assert f["keptA"] == f["disagree"] + f["undetermined"] and f["keptB"] == f["disagree"] and f["undetermined"] > 0
    assert verdict(" a ", "A") == "AGREE" and verdict("A", "B") == "DISAGREE" and verdict(None, "A") == "UNDETERMINED" and verdict("INVALID", "A") == "UNDETERMINED"
    # the two normalisations differ exactly on the literal "INVALID" (first character "I" is a letter under the record's rule)
    P_noinv = {q: {m: (None if (p or "") == "INVALID" else p) for m, p in d.items()} for q, d in S["P"].items()}
    f2 = split_rows(rows, P_noinv)
    n_inv = sum(1 for a, b, q, w in rows if "INVALID" in (S["P"][q].get(a), S["P"][q].get(b)))
    print("  normalisation: %d mismatches with literal INVALID planted (%d matches touch one), %d after mapping INVALID to missing" % (f["norm_mismatch"], n_inv, f2["norm_mismatch"]))
    assert f["norm_mismatch"] > 0 and f["norm_mismatch"] <= n_inv and f2["norm_mismatch"] == 0
    D = dict(S); D["f12"] = split_rows(rows[: len(rows) // 2], S["P"]); D["f20"] = split_rows(rows[len(rows) // 2:], S["P"])
    for conv in ("A", "B"):
        _, by, cells = filtered_cells(D, conv); D["cells_" + conv] = cells; D["by_" + conv] = by
    qsel = S["qsel"]
    # board level: the filtered board is close to the unfiltered one on a planted-deviation table
    jb_u = jb_for(S["by_m"], models); bl_u = board_level(S["usable"], qsel, jb_u, models)
    halvA = {c: v for c, v in D["cells_A"].items() if len(v) >= 50}
    bl_a = board_level(halvA, qsel, jb_for(D["by_A"], models), models)
    print("  board R: unfiltered %.4f [%.4f, %.4f], filtered conv A %.4f [%.4f, %.4f] (%d anchors halvable)" % (bl_u["R"], bl_u["lo_re"], bl_u["hi_re"], bl_a["R"], bl_a["lo_re"], bl_a["hi_re"], len(halvA)))
    assert bl_u["R"] > 0.8 and bl_u["lo_re"] < bl_u["R"] < bl_u["hi_re"]
    # gate logic
    assert ("%.4f" % bl_u["R"] == "%.4f" % bl_u["R"]) and not ("%.4f" % bl_u["R"] == "%.4f" % (bl_u["R"] + 0.001))
    # per-anchor classes on a reduced bootstrap: strong-deviation anchors PASS(-WITH-INTERVAL), null anchors FAIL, small ones UNDETERMINED
    t0 = time.time()
    rows_a = per_anchor(halvA, bl_a, jb_for(D["by_A"], models), models, boot_b, boot_h, jack_h)
    cls = {}
    for c in S["usable"]:
        r = rows_a.get(c, dict(q=len(D["cells_A"][c]), R_prof=float("nan"), cls="n/a"))
        r["support"] = r["q"] >= SUPPORT; r["cls_final"] = r["cls"] if r["support"] else "UNDETERMINED-by-support"; cls[c] = r
    print("  per-anchor (conv A, B=%d x %d, jack %d; %.0fs): %s" % (boot_b, boot_h, jack_h, time.time() - t0,
          ", ".join("%s %s %s" % (c, "%.3f" % cls[c]["R_prof"] if cls[c]["R_prof"] == cls[c]["R_prof"] else "nan", cls[c]["cls_final"]) for c in S["usable"])))
    strong = [c for c in list(S["usable"])[:5]]; null = [c for c in list(S["usable"])[8:11]]; small = [c for c in list(S["usable"])[11:]]
    assert all(cls[c]["cls_final"] in ("PASS", "PASS-WITH-INTERVAL") for c in strong), "planted strong anchors must PASS"
    assert all(cls[c]["cls_final"] == "UNDETERMINED-by-support" for c in small), "100-q anchors must read UNDETERMINED-by-support"
    assert sum(1 for c in null if cls[c]["cls_final"] == "FAIL") >= 2, "planted null anchors should mostly FAIL"
    assert class_step("PASS", "FAIL") == 2 and class_step("PASS", "PASS-WITH-INTERVAL") == 1 and class_step("PASS", "n/a") is None
    # write-once
    os.makedirs(SCRATCH, exist_ok=True); tmp = os.path.join(SCRATCH, "selftest_once.txt"); open(tmp, "w").write("x")
    try:
        write_once(tmp, "y"); raise AssertionError("write-once did not refuse")
    except SystemExit:
        pass
    os.remove(tmp)
    print("SELFTEST OK: filter conventions and normalisations agree with MatchFilter.kt; planted deviations PASS, null anchors FAIL,")
    print("  small anchors read UNDETERMINED-by-support; the gate compares to 4 dp; class steps; write-once refuses.")


def write_once(path, txt):
    if os.path.exists(path):
        raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % path)
    open(path, "w", encoding="utf-8").write(txt + "\n")


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--anchors-convention", choices=["A", "B", "both"], default="both")
    ap.add_argument("--boot-b", type=int, default=pia.BOOT_B); ap.add_argument("--boot-h", type=int, default=pia.BOOT_H); ap.add_argument("--jack-h", type=int, default=pia.JACK_H)
    ap.add_argument("--selftest-boot-b", type=int, default=12); ap.add_argument("--selftest-boot-h", type=int, default=4); ap.add_argument("--selftest-jack-h", type=int, default=2)
    a = ap.parse_args()
    if sum(map(bool, (a.dry_run, a.selftest, a.run))) != 1:
        ap.error("exactly one of --dry-run, --selftest, --run")
    if a.selftest:
        print("pool of record (NOT opened by --selftest): %s" % POOL)
        selftest(a.selftest_boot_b, a.selftest_boot_h, a.selftest_jack_h); return
    import pool_guard
    L = []
    L.append("pool of record: %s" % pool_guard.assert_pool_of_record(POOL))
    L.append("=== PROFILE-R-FILTERED: does the anchor profile's reliability survive the answer-disagreement filter? ===")
    L.append("  registered 2026-09-18 (commit 5bd56bb); zero calls; caches mode=ro; %s" % ("DRY RUN, no R is printed" if a.dry_run else "RUN"))
    L.append("")
    L.append("--- DATA CHECK (the object, before any stratum is read) ---")
    D = load_record(L.append)
    D["by_m"] = defaultdict(list)
    for r in D["rows_m"]: D["by_m"][r[2]].append(r)
    filter_report(D, L.append)
    if a.dry_run:
        L.append("")
        L.append("  dry run: the reproduction gate, the boards, the intervals and the per-anchor classes run under --run only; no R printed.")
        txt = "\n".join(L); print(txt); return
    for pth in (OUT, OUT_CSV):
        if os.path.exists(pth): raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % pth)
    if (a.boot_b, a.boot_h, a.jack_h) != (pia.BOOT_B, pia.BOOT_H, pia.JACK_H):
        L.append("  NOTE: bootstrap / jackknife sizes %d x %d / %d differ from the registered 125 x 16 / 10: NOT an outcome of record." % (a.boot_b, a.boot_h, a.jack_h))
    print("\n".join(L), flush=True)
    R = run(D, L, a.anchors_convention, a.boot_b, a.boot_h, a.jack_h)
    verdicts(D, L, R)
    L.append("  KEY DENOMINATOR restated: each anchor's JUDGED questions of pool %s (unfiltered 119-304; filtered as printed), halved; the" % POOL)
    L.append("  per-half profile is the 20-model BT fit (rj.mm_fit via judge_free_tests.board_from, prior 0.5) on that half's (kept) verdicts.")
    L.append("  McNEMAR-ESTABLISHED RULE: no wrong-direction count exists here; stated, not applied.")
    txt = "\n".join(L); print(txt)
    if R is not None:
        write_once(OUT, txt); write_csv(D, R, OUT_CSV)
        os.makedirs(SCRATCH, exist_ok=True)
        json.dump({conv: {c: {k: v for k, v in r.items() if k not in ("boot_prof_all",)} for c, r in rows.items()} for conv, rows in R["table"].items()},
                  open(os.path.join(SCRATCH, "profile_r_filtered_anchors.json"), "w"), indent=1, default=str)
        print("written", OUT, "and", OUT_CSV)
    else:
        write_once(OUT, txt); print("written (gate failed, no numbers of record)", OUT)


if __name__ == "__main__":
    main()
