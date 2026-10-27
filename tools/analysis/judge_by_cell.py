"""JUDGE-BY-CELL - is there any cell in which one cheap judge beats another by more than the test-retest floor,
stably across draws? (zero judge calls; registered 2026-09-18 at commit 137cb30 in docs/judge_v2_program.md
L7355-L7493 BEFORE this script was written; the MODEL form of the specialised-judge hypothesis).

  python tools/analysis/judge_by_cell.py --dry-run      # pool id first; the three caches opened mode=ro; row counts, the
                                                        #   common set, per-anchor and per-pairing DENOMINATORS; NO outcome
                                                        #   number; nothing written
  python tools/analysis/judge_by_cell.py --selftest     # the statistics on SYNTHETIC three-judge caches with a planted
                                                        #   per-cell winner (two cells, opposite winners) and null cells;
                                                        #   no cache of record is read; nothing written
  python tools/analysis/judge_by_cell.py --run [--boot 1000] [--splits 100] [--out <path>]
                                                        # the readout; refuses on a row-count mismatch; write-once: refuses
                                                        #   if either output exists; writes
                                                        #   experiment_results/x12_crossdomain/judge_by_cell_outcome.txt
                                                        #   (+ judge_by_cell_cells.csv)

QUESTION (registration). RECIPE-GROK found the recipe, not the judge, carries the gain (aggregate). Nobody has read it
per cell. If one judge family beats the other in some cell by more than the floor and the winner is stable across two
draws of the same judge on identical bytes, a per-cell judge choice is a lever; otherwise judge routing is CLOSED at
zero calls.

DATA OBJECTS (all mode=ro; counts pinned; a count mismatch refuses). Three judge draws of the STACK-v2 recipe on the x12
MAIN schedule: D_M Mistral-Large-3 experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db 9,142; D_GP
grok-4-1-fast-non-reasoning (Python) experiment_results/x12_crossdomain/grok_calib.db 9,142; D_GK the same judge on the
same bytes through the Kotlin production path experiment_results/judge_wiring/board/kotlin_c0d3f708cbc3930e.db 9,123.
Common set = the 9,123 Kotlin matches joined by match_id (the 19 reference-less matches excluded, as JUDGE-WIRING-BOARD
did); (model_a, model_b, qid, anchor) asserted identical across the three caches per match and the anchor asserted equal
to anchor_fn(bareq512_s42 primary routing); key-decidable by eval_results.is_correct on the OPTIONS-key-checked roster
(Meta-Llama-3-70B-Instruct excluded; rule 6: never question_text); rule 10: a row whose finish_reason (where recorded) is
length / content_filter / empty is INVALID, never a verdict, never a tie; the Kotlin cache records no ref_correct, so the
reference grade is taken from the x12 cache by match_id (TOPIC-DIFFICULTY, REF-QUALITY-MONITOR). x20 is Mistral only on
a different schedule and contributes nothing to a judge comparison: excluded by construction. Leaves: ~32 judged
questions per leaf, below the 120 key-decidable-question support rule by construction; no leaf row is written.

INSTRUMENT. Per anchor (14) and pairing (M vs GP, M vs GK, GP vs GK): (i) paired key-decidable accuracy difference under
convention A (TIE / INVALID / NON_TERMINATED wrong; the same key-decidable matches for both judges) and B (the pair's
both-committed key-decidable matches), question-clustered bootstrap 95% percentile CI (B = 1,000, seed 42, questions
resampled within the anchor, one resample shared by the pairings), exact two-sided McNemar on the discordant matches;
wrong(established) per anchor per judge from the judge's question-clustered Bradley-Terry board on the anchor
(topic_difficulty.stratum_board: certificate 0.975, systematic_budget.mcnemar_edge on the anchor's judged questions);
decidable tie rate and flip rate per judge per anchor. (ii) BAR: |delta| > 0.057 AND CI excluding 0, under BOTH
conventions; the empirical floor per anchor is the GP-vs-GK difference, printed beside every M-vs-grok difference with
its 14-cell max. (iii) STABILITY: a cell winner exists only if both grok draws agree on the sign of (M - grok) and both
clear the bar. (iv) LEVER, cross-fitted: the key-decidable questions of each anchor halved by question (seed 42, 100
random halvings, floor(n/2) in half A); the per-cell judge chosen on half A by convention-A accuracy (a tie chooses the
pooled best single judge on half A); the routed accuracy on half B against the best SINGLE judge chosen on half A
(pooled convention-A accuracy on half A); mean gain and the [2.5, 97.5] percentile interval over the halvings; the
in-sample routed gain (chosen and read on the same data) beside it as the optimism bound. The registration's "M or
grok" is read once per grok draw (M vs GP, M vs GK; C2 requires both, the registration's "against BOTH grok draws"
applied to the lever); the three-way choice (M / GP / GK) is printed as supplementary and not scored. (v) Overall: the
three pairings on the common set, A and B, questions resampled over the whole common set.

CRITERIA. C1: at least one anchor with >= 120 key-decidable questions clears (ii) against BOTH grok draws with the same
sign; a cell where C3 fails is UNDETERMINED for C1 whatever M reads. C2: cross-fitted routed gain > 0, the interval over
halvings excluding 0, the point >= +1.0pp (both grok draws). C3: 14-cell max |GP - GK| under A <= 0.057. VERDICT RULE:
judge routing is a lever only if C1 AND C2 hold; otherwise CLOSED at zero calls: "the judge model is interchangeable per
cell to within the floor". PREDICTIONS scored HELD / FAILED: overall M vs GP |delta| <= 1.5pp (A) and <= 1.0pp (B); C1
FAILED; 14-cell max |M - grok| 4-7pp on Business / Philosophy / History with CIs including 0; same-judge max |GP - GK|
2-5pp (C3 HELD); cross-fitted gain -1.0 to +0.5pp with an interval including 0 (C2 FAILED); in-sample gain +1 to +2pp;
Mistral's decidable tie rate lower than grok's in every anchor by 1-3pp. FALSIFIER: C1 AND C2 HELD overturns
RECIPE-GROK's "the recipe, not the judge, carries the gain" at the cell level; then a judged confirmation on FRESH
questions of that cell is the registration to write; otherwise the line closes at zero calls.

HYGIENE. Zero calls, zero builds; three caches mode=ro; the pool id printed first; no cache written; both conventions;
UNDETERMINED for any cell under 120 key-decidable QUESTIONS (printed, not scored); no leaf row; no board, profile or
tier of record changes. Output written ONCE from complete caches; --dry-run and --selftest write nothing.
"""
import os, sys, csv, math, json, random, sqlite3, argparse, time
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import pool_guard
import rejudge_grok as rj
import rubric_512 as r512
import systematic_budget as sb
import topic_difficulty as td            # stratum_board (question-clustered BT, certificate 0.975, wrong(established))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

POOL = pool_guard.MMLU_PRO_POOL          # p2dca21ab5f4ef3ae
TREE = "bareq512_s42"
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
JUDGES = ["M", "GP", "GK"]
CACHES = {
    "M":  (os.path.join(X12DIR, "stack_v2_promptv2_x12all.db"), 9142, "Mistral-Large-3, Python (ARENA-V2 x12all)"),
    "GP": (os.path.join(X12DIR, "grok_calib.db"), 9142, "grok-4-1-fast-non-reasoning, Python (GROK-CALIB)"),
    "GK": (os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db"), 9123,
           "grok-4-1-fast-non-reasoning, Kotlin production path (JUDGE-WIRING-BOARD)"),
}
PAIRINGS = [("M", "GP"), ("M", "GK"), ("GP", "GK")]
FLOOR_PAIR = ("GP", "GK")
LEVER_PAIRS = [("M", "GP"), ("M", "GK")]
N_COMMON = 9123
N_NOREF = 19
BAR = 0.057                              # DECOMP's test-retest floor, the registered bar
B_BOOT = 1000                            # question-clustered bootstrap draws (registered)
SEED = 42
N_SPLITS = 100                           # cross-fitted halvings (registered)
MIN_KD_Q = 120                           # a cell under this many key-decidable QUESTIONS is UNDETERMINED (printed, not scored)
SMALL_ANCHORS = {"Business", "Philosophy", "History"}
NON_TERMINATED = {"length", "content_filter", ""}
OUT = os.path.join(X12DIR, "judge_by_cell_outcome.txt")
CSV_OUT = os.path.join(X12DIR, "judge_by_cell_cells.csv")


def ro(path):
    if not os.path.isfile(path):
        raise SystemExit("[JUDGE-BY-CELL] cache not found: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def mcnemar_exact(b, c):
    """Exact two-sided McNemar on discordant counts (b, c): the integer arithmetic of systematic_budget.mcnemar_edge
    (asserted equal in --selftest). Returns p (1.0 when b + c == 0)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n))


def pct(v, p):
    v = sorted(v); n = len(v)
    if n == 0:
        return float("nan")
    i = max(0, min(n - 1, int(round(p * (n - 1)))))
    return v[i]


def sgn(x):
    return 0 if x == 0 else (1 if x > 0 else -1)


# ── data ───────────────────────────────────────────────────────────────────────────────────────────────────────

class Data:
    """Every object the readout touches, loaded once from the caches of record (mode=ro); no outcome number here."""

    def __init__(self, log):
        self.log = log
        snap = r512.snapshot_id(TREE); nodes = r512.load_graph(snap)
        self.route = r512.primary_routing(TREE); anchor_of = r512.anchor_fn(nodes)
        self.anchor_of_q = {q: anchor_of(l) for q, l in self.route.items()}
        self.leaf_of_q = dict(self.route)
        log("tree %s snapshot %s | %d nodes | %d routed pool questions | %d anchors | %d leaves"
            % (TREE, snap, len(nodes), len(self.route), len(set(self.anchor_of_q.values())), len(set(self.route.values()))))
        raw = {}
        for j in JUDGES:
            path, pinned, desc = CACHES[j]
            con = ro(path)
            cols = [c[1] for c in con.execute("PRAGMA table_info(verdicts)")]
            has_fin = "finish1" in cols
            q = ("SELECT match_id, model_a, model_b, qid, winner, invalid, ref_correct, ref_letter, anchor, flip"
                 + (", finish1, finish2" if has_fin else ", NULL, NULL") + " FROM verdicts")
            rows = con.execute(q).fetchall(); con.close()
            if len(rows) != pinned:
                raise SystemExit("[JUDGE-BY-CELL] %s holds %d verdict rows, the record pins %d: refusing" % (j, len(rows), pinned))
            ninv = sum(int(r[5] or 0) for r in rows); reclass = 0; out = {}
            for mid, a, b, qid, w, inv, rc, rl, anc, flip, f1, f2 in rows:
                inv = int(inv or 0)
                if has_fin and ((f1 or "") in NON_TERMINATED or (f2 or "") in NON_TERMINATED) and not inv:
                    inv = 1; reclass += 1                   # rule 10: never a verdict, never a tie
                if inv:
                    w = "INVALID"
                out[int(mid)] = dict(mid=int(mid), a=a, b=b, q=int(qid), w=w, inv=inv, rc=-1 if rc is None else int(rc),
                                     rl=(rl or "").strip().upper(), anc=anc, flip=int(flip or 0))
            raw[j] = out
            log("cache %-3s %-62s %s | %d rows (pinned %d) | INVALID column %d | finish columns %s | rule-10 reclassified %d | questions %d"
                % (j, desc, rel(path), len(out), pinned, ninv, "yes" if has_fin else "no", reclass, len({r["q"] for r in out.values()})))
        # the common set: the Kotlin matches, joined by match_id; identity of (a, b, q, anchor) asserted per match
        common = sorted(raw["GK"])
        if len(common) != N_COMMON:
            raise SystemExit("[JUDGE-BY-CELL] Kotlin carries %d distinct match_ids, the record pins %d" % (len(common), N_COMMON))
        for j in ("M", "GP"):
            miss = [m for m in common if m not in raw[j]]
            if miss:
                raise SystemExit("[JUDGE-BY-CELL] %d Kotlin matches have no row in %s" % (len(miss), j))
            dropped = sorted(set(raw[j]) - set(common))
            noref = sorted(m for m in dropped if raw[j][m]["rc"] < 0)
            log("common set vs %-2s: %d matches of %s not in Kotlin, of which %d reference-less (ref_correct = -1); reference-less in %s overall %d"
                % (j, len(dropped), j, len(noref), j, sum(1 for r in raw[j].values() if r["rc"] < 0)))
            if len(dropped) != N_NOREF or len(noref) != N_NOREF:
                raise SystemExit("[JUDGE-BY-CELL] the matches outside the common set are not the record's %d reference-less matches" % N_NOREF)
        bad_id = bad_anc = 0
        for m in common:
            rm, rp, rk = raw["M"][m], raw["GP"][m], raw["GK"][m]
            if not (rm["a"] == rp["a"] == rk["a"] and rm["b"] == rp["b"] == rk["b"] and rm["q"] == rp["q"] == rk["q"]):
                bad_id += 1
            if not (rm["anc"] == rp["anc"] == rk["anc"]):
                bad_anc += 1
        log("identity on the common set (%d matches): (model_a, model_b, qid) disagree on %d | anchor column disagrees across caches on %d" % (len(common), bad_id, bad_anc))
        if bad_id or bad_anc:
            raise SystemExit("[JUDGE-BY-CELL] the three caches are not the same schedule by match_id: refusing")
        # Kotlin records no ref_correct: the reference kit is the same cached solve -> join from x12 by match_id
        bad_letter = sum(1 for m in common if raw["GK"][m]["rl"] and raw["GK"][m]["rl"] != raw["M"][m]["rl"])
        for m in common:
            raw["GK"][m]["rc"] = raw["M"][m]["rc"]; raw["GK"][m]["rl"] = raw["M"][m]["rl"]
        rc_agree = sum(1 for m in common if raw["GP"][m]["rc"] == raw["M"][m]["rc"])
        log("Kotlin ref_correct joined from x12 by match_id on %d matches | ref_letter disagreements before the join %d | GROK-CALIB ref_correct == x12 ref_correct on %d of %d"
            % (len(common), bad_letter, rc_agree, len(common)))
        if any(raw[j][m]["rc"] < 0 for j in JUDGES for m in common):
            raise SystemExit("[JUDGE-BY-CELL] a reference-less match survived into the common set")
        self.rows = {j: [raw[j][m] for m in common] for j in JUDGES}
        self.common = common
        self.judged = sorted({r["q"] for r in self.rows["M"]})
        pool_guard.assert_scored_subset(POOL, self.judged, out=sys.stdout)
        unrouted = [q for q in self.judged if q not in self.anchor_of_q]
        if unrouted:
            raise SystemExit("[JUDGE-BY-CELL] %d judged questions have no route in %s" % (len(unrouted), TREE))
        bad = sum(1 for r in self.rows["M"] if self.anchor_of_q[r["q"]] != r["anc"])
        if bad:
            raise SystemExit("[JUDGE-BY-CELL] %d rows disagree with anchor_fn(route[qid]) on %s" % (bad, TREE))
        log("anchor column check: every common-set row of every cache equals anchor_fn(route[qid]) on %s" % TREE)
        self.anchors = sorted({self.anchor_of_q[q] for q in self.judged})
        # the key (eval_results.is_correct, roster of record), the OPTIONS-key join checked, never question_text
        ev = ro(rj.EVAL_DB); jset = set(self.judged)
        self.K = defaultdict(dict); self.gt = {}; roster = set()
        for q, m, c, gt in ev.execute("SELECT question_id, model_name, is_correct, gt_answer FROM eval_results"):
            if m in EXCLUDED:
                continue
            roster.add(m)
            if q in jset:
                self.K[q][m] = int(c or 0); self.gt[q] = (gt or "").strip().upper()
        self.roster = sorted(roster)
        def okey(o):
            try:
                return json.dumps(json.loads(o)) if o and o.strip().startswith("[") else o
            except Exception:
                return o
        mm = defaultdict(list)
        for i, o, ans in ev.execute("SELECT id, options, answer FROM mmlu_pro"):
            mm[okey(o)].append((i, (ans or "").strip().upper()))
        matched = multi = none = agree = 0
        for q, o, gt in ev.execute("SELECT question_id, options_json, gt_answer FROM eval_results GROUP BY question_id"):
            if q not in jset:
                continue
            hits = mm.get(okey(o), [])
            if len(hits) == 1:
                matched += 1; agree += int(hits[0][1] == (gt or "").strip().upper())
            elif len(hits) > 1:
                multi += 1
            else:
                none += 1
        ev.close()
        log("key: roster %d models (%s excluded) | OPTIONS-key join eval_results -> mmlu_pro on the %d judged questions: 1:1 %d | multi %d | none %d | gt_answer == mmlu_pro.answer on %d of %d"
            % (len(self.roster), ", ".join(sorted(EXCLUDED)), len(self.judged), matched, multi, none, agree, matched))
        dis = sum(1 for r in self.rows["M"] if (r["rl"] == self.gt.get(r["q"])) != bool(r["rc"]))
        log("hygiene: x12 ref_correct column vs (ref_letter == eval gt_answer) disagree on %d of %d common matches (the column is the kit's grade; used as is)" % (dis, len(common)))
        self.models = sorted({r["a"] for r in self.rows["M"]} | {r["b"] for r in self.rows["M"]})
        self.finish()

    def finish(self):
        """Index the common set: per anchor the rows per judge, the judged questions, the key-decidable matches."""
        self.by = {j: defaultdict(list) for j in JUDGES}
        for j in JUDGES:
            for r in self.rows[j]:
                self.by[j][self.anchor_of_q[r["q"]]].append(r)
        self.anchor_qs = {anc: sorted({r["q"] for r in self.by["M"][anc]}) for anc in self.anchors}
        self.kd_mids = {m["mid"] for m in self.rows["M"] if self.decidable(m)}

    def decidable(self, r):
        ka, kb = self.K[r["q"]].get(r["a"]), self.K[r["q"]].get(r["b"])
        return ka is not None and kb is not None and ka != kb

    def right(self, r):
        return r["w"] == (r["a"] if self.K[r["q"]][r["a"]] else r["b"])


# ── per-cell statistics ────────────────────────────────────────────────────────────────────────────────────────

def cell_table(d, anc):
    """Per question of the anchor: for each judge the convention-A correct count and the key-decidable match count; for
    each pairing the both-committed correct counts and denominator. Returns (questions, matrix Q x ncols, column names)."""
    rows = {j: {r["mid"]: r for r in d.by[j][anc]} for j in JUDGES}
    kd = sorted(m for m in rows["M"] if m in d.kd_mids)
    qs = sorted({rows["M"][m]["q"] for m in kd}); qi = {q: i for i, q in enumerate(qs)}
    cols = ["n"] + ["okA_" + j for j in JUDGES] + ["tie_" + j for j in JUDGES] + ["flip_" + j for j in JUDGES] + ["valid_" + j for j in JUDGES]
    for a, b in PAIRINGS:
        cols += ["nB_%s_%s" % (a, b), "okB1_%s_%s" % (a, b), "okB2_%s_%s" % (a, b)]
    ci = {c: i for i, c in enumerate(cols)}
    S = np.zeros((len(qs), len(cols)))
    for m in kd:
        i = qi[rows["M"][m]["q"]]
        S[i, ci["n"]] += 1
        for j in JUDGES:
            r = rows[j][m]
            S[i, ci["okA_" + j]] += d.right(r)
            if not r["inv"]:
                S[i, ci["valid_" + j]] += 1
                S[i, ci["tie_" + j]] += (r["w"] == "TIE")
                S[i, ci["flip_" + j]] += r["flip"]
        for a, b in PAIRINGS:
            ra, rb = rows[a][m], rows[b][m]
            if ra["w"] in (ra["a"], ra["b"]) and rb["w"] in (rb["a"], rb["b"]):
                S[i, ci["nB_%s_%s" % (a, b)]] += 1
                S[i, ci["okB1_%s_%s" % (a, b)]] += d.right(ra)
                S[i, ci["okB2_%s_%s" % (a, b)]] += d.right(rb)
    return qs, S, ci, kd


def deltas_from(sums, ci):
    """Convention-A and B differences per pairing from a column-sum vector (point or one bootstrap draw)."""
    out = {}
    n = sums[ci["n"]]
    for a, b in PAIRINGS:
        k = "%s_%s" % (a, b)
        out[("A", a, b)] = (sums[ci["okA_" + a]] - sums[ci["okA_" + b]]) / n if n else float("nan")
        nb = sums[ci["nB_" + k]]
        out[("B", a, b)] = (sums[ci["okB1_" + k]] - sums[ci["okB2_" + k]]) / nb if nb else float("nan")
    return out


def bootstrap_deltas(S, ci, B, rng):
    """Question-clustered percentile bootstrap: questions (rows of S) resampled with replacement, one resample shared by
    every pairing and both conventions. Returns {key: (lo, hi)}."""
    Q = S.shape[0]
    if Q == 0:
        return {}
    W = rng.multinomial(Q, np.full(Q, 1.0 / Q), size=B).astype(float)   # B x Q resample weights
    draws = W @ S                                                         # B x ncols
    keys = list(deltas_from(draws[0], ci).keys())
    vals = {k: [] for k in keys}
    for b in range(B):
        dd = deltas_from(draws[b], ci)
        for k in keys:
            vals[k].append(dd[k])
    return {k: (pct([x for x in v if not math.isnan(x)], 0.025), pct([x for x in v if not math.isnan(x)], 0.975)) for k, v in vals.items()}


def mcnemar_pairs(d, anc, kd):
    """Discordant counts per pairing under A (all key-decidable) and B (both-committed): b = first right & second wrong."""
    rows = {j: {r["mid"]: r for r in d.by[j][anc]} for j in JUDGES}
    out = {}
    for a, b in PAIRINGS:
        bA = cA = bB = cB = 0
        for m in kd:
            ra, rb = rows[a][m], rows[b][m]
            xa, xb = d.right(ra), d.right(rb)
            if xa and not xb: bA += 1
            if xb and not xa: cA += 1
            if ra["w"] in (ra["a"], ra["b"]) and rb["w"] in (rb["a"], rb["b"]):
                if xa and not xb: bB += 1
                if xb and not xa: cB += 1
        out[("A", a, b)] = (bA, cA, mcnemar_exact(bA, cA)); out[("B", a, b)] = (bB, cB, mcnemar_exact(bB, cB))
    return out


def judge_board(d, anc, j, B, rng):
    """wrong(established) for one judge on one anchor: topic_difficulty.stratum_board on the judge's valid rows of the
    anchor (question-clustered BT, certificate 0.975, sb.mcnemar_edge on the anchor's judged questions)."""
    rows = [(r["mid"], r["a"], r["b"], r["q"], r["w"], r["inv"], r["rc"]) for r in d.by[j][anc]]
    return td.stratum_board(d, rows, d.models, B, rng)


def analyse_cells(d, B, log, board_B=None):
    """Everything per anchor: counts, accuracies, deltas with CIs and McNemar, tie / flip rates, boards. Returns dict."""
    board_B = B if board_B is None else board_B
    rng = np.random.default_rng(SEED); brng = random.Random(SEED)
    cells = {}
    for anc in d.anchors:
        qs, S, ci, kd = cell_table(d, anc)
        sums = S.sum(axis=0)
        c = dict(anchor=anc, n_match=len(d.by["M"][anc]), n_q=len(d.anchor_qs[anc]), kd_m=int(sums[ci["n"]]), kd_q=len(qs),
                 undetermined=len(qs) < MIN_KD_Q)
        for j in JUDGES:
            n = sums[ci["n"]]; v = sums[ci["valid_" + j]]
            c["accA_" + j] = sums[ci["okA_" + j]] / n if n else float("nan")
            c["okA_" + j] = int(sums[ci["okA_" + j]])
            c["tie_" + j] = sums[ci["tie_" + j]] / v if v else float("nan")
            c["flip_" + j] = sums[ci["flip_" + j]] / v if v else float("nan")
            c["inv_" + j] = sum(1 for r in d.by[j][anc] if r["inv"])
            comm = [r for r in d.by[j][anc] if r["mid"] in d.kd_mids and r["w"] in (r["a"], r["b"])]
            c["nB_" + j] = len(comm); c["accB_" + j] = (sum(1 for r in comm if d.right(r)) / len(comm)) if comm else float("nan")
        pts = deltas_from(sums, ci); cis = bootstrap_deltas(S, ci, B, rng); mc = mcnemar_pairs(d, anc, kd)
        for a, b in PAIRINGS:
            k = "%s_%s" % (a, b)
            c["nB_" + k] = int(sums[ci["nB_" + k]])
            for conv in ("A", "B"):
                key = (conv, a, b)
                c["d%s_%s" % (conv, k)] = pts[key]
                c["lo%s_%s" % (conv, k)] = cis.get(key, (float("nan"), float("nan")))[0]
                c["hi%s_%s" % (conv, k)] = cis.get(key, (float("nan"), float("nan")))[1]
                c["mc%s_%s" % (conv, k)] = mc[key]
                lo, hi = c["lo%s_%s" % (conv, k)], c["hi%s_%s" % (conv, k)]
                c["clear%s_%s" % (conv, k)] = bool(abs(pts[key]) > BAR and not math.isnan(lo) and (lo > 0 or hi < 0))
            c["clear_" + k] = c["clearA_" + k] and c["clearB_" + k]
        for j in JUDGES:
            bd = judge_board(d, anc, j, board_B, brng)
            c["board_" + j] = bd
        cells[anc] = c
        log("  cell %-16s done | kd matches %d | kd questions %d%s" % (anc, c["kd_m"], c["kd_q"], " | UNDETERMINED (< %d kd questions)" % MIN_KD_Q if c["undetermined"] else ""))
    return cells


def analyse_overall(d, B):
    """The three pairings on the whole common set, questions resampled over the common set."""
    tables = [cell_table(d, anc) for anc in d.anchors]
    S = np.vstack([t[1] for t in tables]); ci = tables[0][2]
    sums = S.sum(axis=0); pts = deltas_from(sums, ci)
    cis = bootstrap_deltas(S, ci, B, np.random.default_rng(SEED + 1))
    mc = {}
    for anc, (qs, _, _, kd) in zip(d.anchors, tables):
        for k, (b, c, _) in mcnemar_pairs(d, anc, kd).items():
            bb, cc = mc.get(k, (0, 0)); mc[k] = (bb + b, cc + c)
    mc = {k: (b, c, mcnemar_exact(b, c)) for k, (b, c) in mc.items()}
    out = dict(kd_m=int(sums[ci["n"]]), kd_q=int(S.shape[0]))
    for j in JUDGES:
        out["accA_" + j] = sums[ci["okA_" + j]] / sums[ci["n"]]
        out["tie_" + j] = sums[ci["tie_" + j]] / sums[ci["valid_" + j]]
        out["flip_" + j] = sums[ci["flip_" + j]] / sums[ci["valid_" + j]]
    for a, b in PAIRINGS:
        k = "%s_%s" % (a, b); out["nB_" + k] = int(sums[ci["nB_" + k]])
        out["accB1_" + k] = sums[ci["okB1_" + k]] / sums[ci["nB_" + k]]; out["accB2_" + k] = sums[ci["okB2_" + k]] / sums[ci["nB_" + k]]
        for conv in ("A", "B"):
            out["d%s_%s" % (conv, k)] = pts[(conv, a, b)]; out["ci%s_%s" % (conv, k)] = cis[(conv, a, b)]; out["mc%s_%s" % (conv, k)] = mc[(conv, a, b)]
    return out


# ── the lever test (iv) ────────────────────────────────────────────────────────────────────────────────────────

def lever(d, judges, n_splits, seed):
    """Cross-fitted per-cell judge choice among `judges`. Per halving: each anchor's key-decidable questions are permuted
    and the first floor(n/2) form half A; the per-cell judge is chosen on half A by convention-A accuracy (tie -> the
    pooled best single judge on half A); the routed accuracy on half B is read against the best single judge chosen on
    half A (pooled half-A accuracy). Returns the per-split gains, the choice frequencies and the in-sample bound."""
    per = {}
    for anc in d.anchors:
        qs, S, ci, _ = cell_table(d, anc)
        per[anc] = (np.array([S[:, ci["okA_" + j]] for j in judges]).T, S[:, ci["n"]])   # Q x J, Q
    rng = np.random.default_rng(seed)
    gains = []; routed_acc = []; single_acc = []; choice = {anc: Counter() for anc in d.anchors}; single_choice = Counter()
    for _ in range(n_splits):
        halves = {}
        for anc in d.anchors:
            ok, n = per[anc]; Q = len(n)
            perm = rng.permutation(Q); ha = perm[: Q // 2]; hb = perm[Q // 2:]
            halves[anc] = (ok[ha].sum(axis=0), n[ha].sum(), ok[hb].sum(axis=0), n[hb].sum())
        okA_all = sum(h[0] for h in halves.values()); nA_all = sum(h[1] for h in halves.values())
        single = int(np.argmax(okA_all / nA_all)); single_choice[judges[single]] += 1
        r_ok = r_n = 0.0; s_ok = s_n = 0.0
        for anc in d.anchors:
            okA, nA, okB, nB = halves[anc]
            acc = okA / nA if nA else np.zeros(len(judges))
            best = np.flatnonzero(acc == acc.max())
            j = single if single in best else int(best[0])
            choice[anc][judges[j]] += 1
            r_ok += okB[j]; r_n += nB; s_ok += okB[single]; s_n += nB
        routed_acc.append(r_ok / r_n); single_acc.append(s_ok / s_n); gains.append(r_ok / r_n - s_ok / s_n)
    # in-sample: chosen and read on the same (full) data
    ok_all = sum(per[anc][0].sum(axis=0) for anc in d.anchors); n_all = sum(per[anc][1].sum() for anc in d.anchors)
    single = int(np.argmax(ok_all / n_all))
    ins_ok = 0.0; ins_choice = {}
    for anc in d.anchors:
        ok, n = per[anc]; acc = ok.sum(axis=0) / n.sum(); best = np.flatnonzero(acc == acc.max())
        j = single if single in best else int(best[0]); ins_choice[anc] = judges[j]; ins_ok += ok.sum(axis=0)[j]
    ins_gain = ins_ok / n_all - ok_all[single] / n_all
    return dict(judges=judges, gains=gains, routed=routed_acc, single=single_acc, choice=choice, single_choice=single_choice,
                mean=float(np.mean(gains)), lo=pct(gains, 0.025), hi=pct(gains, 0.975), frac_pos=float(np.mean([g > 0 for g in gains])),
                ins_gain=float(ins_gain), ins_single=judges[single], ins_choice=ins_choice)


# ── the readout ────────────────────────────────────────────────────────────────────────────────────────────────

def fmt_ci(lo, hi):
    return "[%+.3f, %+.3f]" % (lo, hi) if not (math.isnan(lo) or math.isnan(hi)) else "[nan, nan]"


def readout(B, n_splits, out_path, csv_path, d=None, log=None, selftest=False, board_B=None):
    L = []
    def emit(s=""):
        L.append(s); print(s)
    if log is None:
        log = lambda s: emit("  " + s)
    if not selftest:
        for p in (out_path, csv_path):
            if p and os.path.exists(p):
                raise SystemExit("[ONCE] %s exists: the file of record is written once, from complete caches; never overwritten (correct by insertion in the record, not by re-running)" % rel(p))
        emit("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    else:
        emit("reserved_pool_id=%s (selftest: no cache of record is read)" % POOL)
    emit("=== JUDGE-BY-CELL: is there any cell in which one cheap judge beats another by more than the test-retest floor, stably across draws? ===")
    emit("  registered 2026-09-18 (docs/judge_v2_program.md L7355-L7493, commit 137cb30) before this script; zero judge calls; caches mode=ro; %s"
         % ("SYNTHETIC data" if selftest else "run %s" % time.strftime("%Y-%m-%d %H:%M:%S")))
    emit("  bar |delta| > %.3f AND question-clustered 95%% CI excluding 0 under BOTH conventions (A: TIE / INVALID / NON_TERMINATED wrong; B: the pair's both-committed matches)" % BAR)
    emit("  bootstrap B = %d, seed %d, questions resampled within the anchor; boards B = %d; lever halvings %d, seed %d; a cell under %d key-decidable QUESTIONS is UNDETERMINED (printed, not scored)"
         % (B, SEED, B if board_B is None else board_B, n_splits, SEED, MIN_KD_Q))
    emit("")
    emit("--- data objects ---")
    t0 = time.time()
    if d is None:
        d = Data(log)
    emit("  common set: %d matches | %d judged questions | %d key-decidable matches | %d anchors | models %d"
         % (len(d.rows["M"]), len(d.judged), len(d.kd_mids), len(d.anchors), len(d.models)))
    emit("  x20 (Mistral only, a different schedule): excluded by construction; leaves: no leaf row (support rule %d kd questions; ~32 judged per leaf)" % MIN_KD_Q)
    emit("")
    emit("--- (i) per anchor, per judge: key-decidable accuracy, decisiveness, wrong(established) ---")
    emit("  columns: kd matches / kd questions | per judge accA (n = kd matches), accB (n = the judge's committed kd), decidable tie rate, flip rate (valid kd), INVALID rows | board: wrong(established) / wrong / called edges")
    cells = analyse_cells(d, B, log, board_B=board_B)
    emit("")
    emit("  %-16s %5s %5s | %s" % ("anchor", "kd_m", "kd_q", " | ".join("%-3s accA   accB(n)      tie   flip  inv  w_est/w/called" % j for j in JUDGES)))
    for anc in d.anchors:
        c = cells[anc]; parts = []
        for j in JUDGES:
            bd = c["board_" + j]
            bstr = "refused" if (bd is None or bd.get("refused")) else "%d/%d/%d" % (bd["wrong_est"], bd["wrong"], bd["called"])
            parts.append("%-3s %.3f  %.3f(%4d)  %.3f  %.3f  %3d  %s" % (j, c["accA_" + j], c["accB_" + j], c["nB_" + j], c["tie_" + j], c["flip_" + j], c["inv_" + j], bstr))
        emit("  %-16s %5d %5d | %s%s" % (anc, c["kd_m"], c["kd_q"], " | ".join(parts), "  UNDETERMINED" if c["undetermined"] else ""))
    emit("")
    emit("--- (i)-(iii) per anchor, per pairing: paired differences (first minus second), CI, exact McNemar (b / c / p), bar, sign ---")
    emit("  the GP-vs-GK row is the empirical same-judge floor for the cell (identical judge, identical bytes)")
    for anc in d.anchors:
        c = cells[anc]
        emit("  %s (kd matches %d, kd questions %d%s)" % (anc, c["kd_m"], c["kd_q"], "; UNDETERMINED by support" if c["undetermined"] else ""))
        for a, b in PAIRINGS:
            k = "%s_%s" % (a, b)
            emit("    %-8s A %+.3f %s McNemar %3d/%3d p=%.3g %s | B (n=%4d) %+.3f %s McNemar %3d/%3d p=%.3g %s | clears bar under both: %s%s"
                 % ("%s-%s" % (a, b), c["dA_" + k], fmt_ci(c["loA_" + k], c["hiA_" + k]), c["mcA_" + k][0], c["mcA_" + k][1], c["mcA_" + k][2],
                    "CLEAR" if c["clearA_" + k] else "no", c["nB_" + k], c["dB_" + k], fmt_ci(c["loB_" + k], c["hiB_" + k]),
                    c["mcB_" + k][0], c["mcB_" + k][1], c["mcB_" + k][2], "CLEAR" if c["clearB_" + k] else "no",
                    "YES" if c["clear_" + k] else "no", "  <- floor" if (a, b) == FLOOR_PAIR else ""))
    emit("")
    # C3: the floor
    fk = "%s_%s" % FLOOR_PAIR
    floor_abs = {anc: abs(cells[anc]["dA_" + fk]) for anc in d.anchors}
    floor_max_anc = max(floor_abs, key=floor_abs.get); floor_max = floor_abs[floor_max_anc]
    floor_absB = {anc: abs(cells[anc]["dB_" + fk]) for anc in d.anchors}
    c3_fail_cells = sorted(anc for anc in d.anchors if floor_abs[anc] > BAR)
    C3 = floor_max <= BAR
    scored = [anc for anc in d.anchors if not cells[anc]["undetermined"]]
    floor_max_scored = max((floor_abs[anc] for anc in scored), default=float("nan"))
    emit("--- C3: the grok-vs-grok floor ---")
    emit("  14-cell max |GP - GK| under A = %.3f at %s (under B: max %.3f at %s); cells above the bar: %s"
         % (floor_max, floor_max_anc, max(floor_absB.values()), max(floor_absB, key=floor_absB.get), ", ".join(c3_fail_cells) or "none"))
    emit("  beside it (not the registered C3 statistic): max |GP - GK| under A over the %d cells with >= %d kd questions = %.3f" % (len(scored), MIN_KD_Q, floor_max_scored))
    emit("  C3 (max |GP - GK| under A <= %.3f): %s" % (BAR, "HELD" if C3 else "FAILED"))
    emit("")
    # C1: a cell winner
    emit("--- C1: a cell winner (clears the bar under both conventions against BOTH grok draws, same sign; >= %d kd questions; C3 holds in the cell) ---" % MIN_KD_Q)
    winners = []; undetermined = []
    for anc in d.anchors:
        c = cells[anc]
        s1, s2 = sgn(c["dA_M_GP"]), sgn(c["dA_M_GK"])
        both_clear = c["clear_M_GP"] and c["clear_M_GK"] and s1 == s2 and s1 != 0
        status = []
        if c["undetermined"]:
            status.append("UNDETERMINED (kd questions %d < %d)" % (c["kd_q"], MIN_KD_Q))
        if anc in c3_fail_cells:
            status.append("UNDETERMINED for C1 (C3 fails: |GP - GK| = %.3f > %.3f)" % (floor_abs[anc], BAR))
        if status:
            undetermined.append(anc)
        emit("  %-16s M-GP A %+.3f B %+.3f clears %-3s | M-GK A %+.3f B %+.3f clears %-3s | signs agree %-3s | floor |GP-GK| A %.3f | %s"
             % (anc, c["dA_M_GP"], c["dB_M_GP"], "yes" if c["clear_M_GP"] else "no", c["dA_M_GK"], c["dB_M_GK"], "yes" if c["clear_M_GK"] else "no",
                "yes" if (s1 == s2 and s1 != 0) else "no", floor_abs[anc],
                "; ".join(status) if status else ("CELL WINNER: %s" % ("M" if s1 > 0 else "grok") if both_clear else "no winner")))
        if both_clear and not status:
            winners.append((anc, "M" if s1 > 0 else "grok"))
    raw_clear = [anc for anc in d.anchors if cells[anc]["clear_M_GP"] and cells[anc]["clear_M_GK"] and sgn(cells[anc]["dA_M_GP"]) == sgn(cells[anc]["dA_M_GK"]) != 0]
    C1 = len(winners) > 0
    emit("  cells clearing the bar against both draws with the same sign (before the support / C3 rule): %s" % (", ".join(raw_clear) or "none"))
    emit("  cells UNDETERMINED (not scored for C1): %s" % (", ".join(undetermined) or "none"))
    emit("  C1 (at least one scored cell winner): %s%s" % ("HELD" if C1 else "FAILED", " - " + ", ".join("%s (%s)" % w for w in winners) if winners else ""))
    emit("")
    # C2: the lever
    emit("--- C2: the lever, cross-fitted (choose per cell on half A by convention-A accuracy, read on half B; %d halvings, seed %d) ---" % (n_splits, SEED))
    emit("  all %d anchors are routed (the support rule governs C1's scoring, not the lever's arithmetic); gain = routed half-B accuracy - best single judge (chosen on half A) half-B accuracy" % len(d.anchors))
    levers = {}
    for pair in LEVER_PAIRS + [tuple(JUDGES)]:
        lv = lever(d, list(pair), n_splits, SEED); levers[pair] = lv
        tag = "M vs %s" % pair[1] if len(pair) == 2 else "three-way M / GP / GK (supplementary, not scored)"
        emit("  %-52s cross-fitted gain mean %+.4f (%+.2fpp) interval over halvings [%+.4f, %+.4f] | splits with gain > 0: %.0f%% | routed %.4f vs single %.4f | in-sample gain %+.4f (%+.2fpp; single = %s)"
             % (tag, lv["mean"], 100 * lv["mean"], lv["lo"], lv["hi"], 100 * lv["frac_pos"], float(np.mean(lv["routed"])), float(np.mean(lv["single"])),
                lv["ins_gain"], 100 * lv["ins_gain"], lv["ins_single"]))
        emit("      single judge chosen on half A: %s | per-cell choice frequency: %s"
             % (", ".join("%s %d" % kv for kv in lv["single_choice"].most_common()),
                "; ".join("%s %s" % (anc, "/".join("%s %d" % kv for kv in lv["choice"][anc].most_common())) for anc in d.anchors)))
    c2_parts = {}
    for pair in LEVER_PAIRS:
        lv = levers[pair]; c2_parts[pair] = lv["mean"] > 0 and lv["lo"] > 0 and lv["mean"] >= 0.01
    C2 = all(c2_parts.values())
    emit("  C2 per grok draw (mean > 0, interval excluding 0, point >= +1.0pp): %s" % " | ".join("M vs %s %s" % (p[1], "HELD" if v else "FAILED") for p, v in c2_parts.items()))
    emit("  C2 (both grok draws): %s" % ("HELD" if C2 else "FAILED"))
    emit("")
    # (v) overall
    ov = analyse_overall(d, B)
    emit("--- (v) overall on the common set (kd matches %d, kd questions %d; questions resampled over the common set) ---" % (ov["kd_m"], ov["kd_q"]))
    emit("  accA: %s | decidable tie rate: %s | flip rate: %s"
         % (" ".join("%s %.4f" % (j, ov["accA_" + j]) for j in JUDGES), " ".join("%s %.4f" % (j, ov["tie_" + j]) for j in JUDGES), " ".join("%s %.4f" % (j, ov["flip_" + j]) for j in JUDGES)))
    for a, b in PAIRINGS:
        k = "%s_%s" % (a, b)
        emit("  %-6s A %+.4f %s McNemar %d/%d p=%.3g | B (n=%d; %s %.4f vs %s %.4f) %+.4f %s McNemar %d/%d p=%.3g"
             % ("%s-%s" % (a, b), ov["dA_" + k], fmt_ci(*ov["ciA_" + k]), ov["mcA_" + k][0], ov["mcA_" + k][1], ov["mcA_" + k][2], ov["nB_" + k], a, ov["accB1_" + k], b, ov["accB2_" + k],
                ov["dB_" + k], fmt_ci(*ov["ciB_" + k]), ov["mcB_" + k][0], ov["mcB_" + k][1], ov["mcB_" + k][2]))
    emit("")
    # predictions
    emit("--- predictions (registration), scored ---")
    P = {}
    P["P1"] = abs(ov["dA_M_GP"]) <= 0.015 and abs(ov["dB_M_GP"]) <= 0.010
    emit("  P1 overall M vs GP |delta| <= 1.5pp (A) and <= 1.0pp (B): A %+.4f, B %+.4f -> %s (M vs GK beside: A %+.4f, B %+.4f)"
         % (ov["dA_M_GP"], ov["dB_M_GP"], "HELD" if P["P1"] else "FAILED", ov["dA_M_GK"], ov["dB_M_GK"]))
    P["P2"] = not C1
    emit("  P2 no anchor clears the bar under both conventions against both grok draws (C1 FAILED): %s" % ("HELD" if P["P2"] else "FAILED"))
    mg = {}
    for anc in d.anchors:
        for k in ("M_GP", "M_GK"):
            mg[(anc, k)] = abs(cells[anc]["dA_" + k])
    (mx_anc, mx_k), mx = max(mg.items(), key=lambda kv: kv[1])
    mx_ci_incl = cells[mx_anc]["loA_" + mx_k] <= 0 <= cells[mx_anc]["hiA_" + mx_k]
    small_ok = mx_anc in SMALL_ANCHORS
    P["P3"] = (0.04 <= mx <= 0.07) and small_ok and mx_ci_incl
    emit("  P3 14-cell max |M - grok| (A) 4-7pp, on Business / Philosophy / History, CI including 0: max %.3f at %s (%s), CI %s -> range %s, anchor %s, CI incl 0 %s -> %s"
         % (mx, mx_anc, mx_k.replace("_", "-"), fmt_ci(cells[mx_anc]["loA_" + mx_k], cells[mx_anc]["hiA_" + mx_k]),
            "yes" if 0.04 <= mx <= 0.07 else "no", "yes" if small_ok else "no", "yes" if mx_ci_incl else "no", "HELD" if P["P3"] else "FAILED"))
    P["P4"] = (0.02 <= floor_max <= 0.05)
    emit("  P4 same-judge max |GP - GK| (A) 2-5pp (C3 HELD): max %.3f at %s -> %s; C3 %s" % (floor_max, floor_max_anc, "HELD" if P["P4"] else "FAILED", "HELD" if C3 else "FAILED"))
    p5 = {p: (-0.01 <= levers[p]["mean"] <= 0.005 and levers[p]["lo"] <= 0 <= levers[p]["hi"]) for p in LEVER_PAIRS}
    P["P5"] = all(p5.values())
    emit("  P5 cross-fitted routed gain -1.0 to +0.5pp with an interval including 0 (C2 FAILED): %s -> %s; C2 %s"
         % (" | ".join("M vs %s %+.2fpp %s %s" % (p[1], 100 * levers[p]["mean"], fmt_ci(levers[p]["lo"], levers[p]["hi"]), "yes" if v else "no") for p, v in p5.items()),
            "HELD" if P["P5"] else "FAILED", "HELD" if C2 else "FAILED"))
    p6 = {p: (0.01 <= levers[p]["ins_gain"] <= 0.02) for p in LEVER_PAIRS}
    P["P6"] = all(p6.values())
    emit("  P6 in-sample routed gain +1 to +2pp: %s -> %s" % (" | ".join("M vs %s %+.2fpp %s" % (p[1], 100 * levers[p]["ins_gain"], "yes" if v else "no") for p, v in p6.items()), "HELD" if P["P6"] else "FAILED"))
    lower = []; in_band = []
    for anc in d.anchors:
        c = cells[anc]; dgp = c["tie_GP"] - c["tie_M"]; dgk = c["tie_GK"] - c["tie_M"]
        lower.append(dgp > 0 and dgk > 0); in_band.append(0.01 <= dgp <= 0.03 and 0.01 <= dgk <= 0.03)
    P["P7"] = all(in_band)
    emit("  P7 Mistral's decidable tie rate lower than grok's in every anchor by 1-3pp: M lower than both grok draws in %d of %d anchors; within 1-3pp against both in %d of %d -> %s"
         % (sum(lower), len(lower), sum(in_band), len(in_band), "HELD" if P["P7"] else "FAILED"))
    emit("      per anchor (grok - M, decidable tie rate): %s" % "; ".join("%s GP %+.3f GK %+.3f" % (anc, cells[anc]["tie_GP"] - cells[anc]["tie_M"], cells[anc]["tie_GK"] - cells[anc]["tie_M"]) for anc in d.anchors))
    emit("")
    emit("--- criteria and verdict ---")
    emit("  C1 (a cell winner exists): %s" % ("HELD" if C1 else "FAILED"))
    emit("  C2 (routing is a lever, cross-fitted, both grok draws): %s" % ("HELD" if C2 else "FAILED"))
    emit("  C3 (grok-vs-grok floor, 14-cell max |GP - GK| under A <= %.3f): %s (max %.3f at %s)" % (BAR, "HELD" if C3 else "FAILED", floor_max, floor_max_anc))
    emit("  predictions: %s" % ", ".join("%s %s" % (k, "HELD" if v else "FAILED") for k, v in P.items()))
    fired = C1 and C2
    emit("  FALSIFIER (C1 AND C2 HELD overturns RECIPE-GROK's 'the recipe, not the judge, carries the gain' at the cell level): %s" % ("FIRED" if fired else "not fired"))
    if fired:
        emit("  VERDICT: judge routing is a lever at the cell level on %s; the registration to write is a judged confirmation on FRESH questions of that cell (not re-draws), at the FW rate."
             % ", ".join("%s (%s)" % w for w in winners))
    else:
        emit("  VERDICT: judge routing is CLOSED at zero calls; the judge model is interchangeable per cell to within the floor.")
    emit("  no leaf row (sub-anchor line closed); x20 excluded by construction; no board, profile or tier of record changed; zero judge calls; elapsed %.0f s" % (time.time() - t0))
    if selftest:
        return dict(cells=cells, C1=C1, C2=C2, C3=C3, P=P, winners=winners, levers=levers, overall=ov, floor_max=floor_max, floor_max_scored=floor_max_scored)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        head = ["anchor", "n_match", "n_q", "kd_m", "kd_q", "undetermined"]
        for j in JUDGES:
            head += ["accA_" + j, "nB_" + j, "accB_" + j, "tie_" + j, "flip_" + j, "inv_" + j, "wrong_est_" + j, "wrong_" + j, "called_" + j]
        for a, b in PAIRINGS:
            k = "%s_%s" % (a, b)
            head += ["dA_" + k, "loA_" + k, "hiA_" + k, "mcA_b_" + k, "mcA_c_" + k, "mcA_p_" + k, "nB_" + k, "dB_" + k, "loB_" + k, "hiB_" + k, "mcB_b_" + k, "mcB_c_" + k, "mcB_p_" + k, "clear_" + k]
        w.writerow(head)
        for anc in d.anchors:
            c = cells[anc]; row = [anc, c["n_match"], c["n_q"], c["kd_m"], c["kd_q"], int(c["undetermined"])]
            for j in JUDGES:
                bd = c["board_" + j]; ref = bd is None or bd.get("refused")
                row += ["%.4f" % c["accA_" + j], c["nB_" + j], "%.4f" % c["accB_" + j], "%.4f" % c["tie_" + j], "%.4f" % c["flip_" + j], c["inv_" + j],
                        "" if ref else bd["wrong_est"], "" if ref else bd["wrong"], "" if ref else bd["called"]]
            for a, b in PAIRINGS:
                k = "%s_%s" % (a, b)
                row += ["%.4f" % c["dA_" + k], "%.4f" % c["loA_" + k], "%.4f" % c["hiA_" + k], c["mcA_" + k][0], c["mcA_" + k][1], "%.4g" % c["mcA_" + k][2], c["nB_" + k],
                        "%.4f" % c["dB_" + k], "%.4f" % c["loB_" + k], "%.4f" % c["hiB_" + k], c["mcB_" + k][0], c["mcB_" + k][1], "%.4g" % c["mcB_" + k][2], int(c["clear_" + k])]
            w.writerow(row)
    print("[WRITTEN] %s and %s" % (rel(out_path), rel(csv_path)))


# ── dry run ────────────────────────────────────────────────────────────────────────────────────────────────────

def dry_run():
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL))
    print("[DRY-RUN] JUDGE-BY-CELL | zero judge calls | three caches opened mode=ro | nothing written | no outcome number below")
    d = Data(lambda s: print("  " + s))
    print("  common set: %d matches | %d judged questions | %d key-decidable matches | %d anchors | %d contestants"
          % (len(d.rows["M"]), len(d.judged), len(d.kd_mids), len(d.anchors), len(d.models)))
    print("  denominators per anchor (kd = key-decidable; nB = the pairing's both-committed kd matches, convention B's denominator):")
    print("  %-16s %7s %6s %6s %6s %s | %s" % ("anchor", "matches", "q", "kd_m", "kd_q", "support", " ".join("nB_%s-%s" % p for p in PAIRINGS)))
    tot = Counter()
    for anc in d.anchors:
        qs, S, ci, kd = cell_table(d, anc); sums = S.sum(axis=0)
        nb = [int(sums[ci["nB_%s_%s" % p]]) for p in PAIRINGS]
        und = len(qs) < MIN_KD_Q
        print("  %-16s %7d %6d %6d %6d %-13s | %s" % (anc, len(d.by["M"][anc]), len(d.anchor_qs[anc]), int(sums[ci["n"]]), len(qs),
                                                   "UNDETERMINED" if und else "scored", "  ".join("%6d" % x for x in nb)))
        tot["m"] += len(d.by["M"][anc]); tot["q"] += len(d.anchor_qs[anc]); tot["kd_m"] += int(sums[ci["n"]]); tot["kd_q"] += len(qs); tot["und"] += und
        for p, x in zip(PAIRINGS, nb):
            tot["nB_%s_%s" % p] += x
    print("  %-16s %7d %6d %6d %6d %-13s | %s" % ("TOTAL", tot["m"], tot["q"], tot["kd_m"], tot["kd_q"], "%d undetermined" % tot["und"],
                                               "  ".join("%6d" % tot["nB_%s_%s" % p] for p in PAIRINGS)))
    leaf_q = Counter(d.leaf_of_q[q] for q in d.judged)
    kd_q_leaf = Counter(d.leaf_of_q[r["q"]] for r in {m["q"]: m for m in d.rows["M"] if m["mid"] in d.kd_mids}.values())
    print("  leaves: %d carry judged questions (max %d judged, max %d key-decidable per leaf); leaves with >= %d kd questions: %d -> no leaf row"
          % (len(leaf_q), max(leaf_q.values()), max(kd_q_leaf.values()), MIN_KD_Q, sum(1 for v in kd_q_leaf.values() if v >= MIN_KD_Q)))
    print("  INVALID rows on the common set: %s" % ", ".join("%s %d" % (j, sum(1 for r in d.rows[j] if r["inv"])) for j in JUDGES))
    print("  outputs (write-once): %s %s | %s %s" % (rel(OUT), "EXISTS" if os.path.exists(OUT) else "absent", rel(CSV_OUT), "EXISTS" if os.path.exists(CSV_OUT) else "absent"))
    print("[DRY-RUN] done; nothing written; no judge call")


# ── selftest ───────────────────────────────────────────────────────────────────────────────────────────────────

class Synthetic(Data):
    """Synthetic three-judge caches on a planted design: anchor P_M (M 0.95 vs grok 0.75), anchor P_G (M 0.75 vs grok
    0.95), null anchors (every judge 0.85; GP and GK drawn independently at the same rate = the same-judge floor),
    one SMALL anchor (60 questions -> UNDETERMINED by support). 8 models with a planted key; 3 matches per question."""

    def __init__(self, seed=7, n_q=400):
        rng = random.Random(seed)
        self.models = ["m%d" % i for i in range(8)]; keyacc = {m: 0.3 + 0.08 * i for i, m in enumerate(self.models)}
        plan = {"P_M": (0.95, 0.75, n_q), "P_G": (0.75, 0.95, n_q), "N1": (0.85, 0.85, n_q), "N2": (0.85, 0.85, n_q), "Small": (0.85, 0.85, 60)}
        self.anchors = sorted(plan); self.anchor_of_q = {}; self.K = defaultdict(dict); self.rows = {j: [] for j in JUDGES}
        q = 0; mid = 0
        for anc in self.anchors:
            accM, accG, nq = plan[anc]
            for _ in range(nq):
                q += 1; self.anchor_of_q[q] = anc
                for m in self.models:
                    self.K[q][m] = int(rng.random() < keyacc[m])
                for _ in range(3):
                    a, b = rng.sample(self.models, 2); mid += 1
                    for j in JUDGES:
                        acc = accM if j == "M" else accG
                        ka, kb = self.K[q][a], self.K[q][b]
                        u = rng.random()
                        if u < 0.08:
                            w = "TIE"
                        elif ka != kb:
                            w = (a if ka else b) if rng.random() < acc else (b if ka else a)
                        else:
                            w = a if rng.random() < 0.5 else b
                        self.rows[j].append(dict(mid=mid, a=a, b=b, q=q, w=w, inv=0, rc=1, rl="A", anc=anc, flip=int(w == "TIE")))
        self.judged = sorted(self.anchor_of_q); self.leaf_of_q = {}
        self.finish()


def selftest():
    print("reserved_pool_id=%s (selftest: no cache of record is read)" % POOL)
    # [1] the local exact McNemar equals systematic_budget.mcnemar_edge's arithmetic on a constructed edge
    K = {}; b, c = 7, 2
    for i in range(b):
        K[i] = {"a": 1, "b": 0}
    for i in range(b, b + c):
        K[i] = {"a": 0, "b": 1}
    for i in range(b + c, b + c + 5):
        K[i] = {"a": 1, "b": 1}
    p_ref, b_ref, c_ref = sb.mcnemar_edge(dict(anchor="S", a="a", b="b"), K, {"S": list(K)})
    assert (b_ref, c_ref) == (b, c) and abs(mcnemar_exact(b, c) - p_ref) < 1e-12, (p_ref, mcnemar_exact(b, c))
    assert mcnemar_exact(0, 0) == 1.0 and mcnemar_exact(0, 1) == 1.0
    print("  [1] mcnemar_exact(%d, %d) = %.6f == systematic_budget.mcnemar_edge: OK" % (b, c, p_ref))
    # [2] the planted design
    d = Synthetic()
    res = readout(200, 40, None, None, d=d, log=lambda s: print("      " + s), selftest=True, board_B=30)
    cells = res["cells"]
    assert cells["P_M"]["clear_M_GP"] and cells["P_M"]["clear_M_GK"] and cells["P_M"]["dA_M_GP"] > BAR and cells["P_M"]["dA_M_GK"] > BAR, "planted M winner not found"
    assert cells["P_G"]["clear_M_GP"] and cells["P_G"]["clear_M_GK"] and cells["P_G"]["dA_M_GP"] < -BAR and cells["P_G"]["dA_M_GK"] < -BAR, "planted grok winner not found"
    for anc in ("N1", "N2"):
        assert not cells[anc]["clear_M_GP"] and not cells[anc]["clear_M_GK"] and not cells[anc]["clear_GP_GK"], "null cell clears the bar"
    assert cells["Small"]["undetermined"] and not cells["N1"]["undetermined"], "support rule"
    assert set(a for a, _ in res["winners"]) == {"P_M", "P_G"}, res["winners"]
    assert res["C1"] and res["floor_max_scored"] <= BAR, (res["C1"], res["floor_max_scored"])
    assert not res["C3"] and "Small" in [a for a in d.anchors if abs(cells[a]["dA_GP_GK"]) > BAR], "the 60-question cell is expected to fail C3 (its same-judge noise exceeds the bar) and to be UNDETERMINED for C1"
    for p in LEVER_PAIRS:
        lv = res["levers"][p]
        assert lv["mean"] > 0.02 and lv["lo"] > 0 and lv["ins_gain"] >= lv["mean"] - 0.01, (p, lv["mean"], lv["lo"], lv["ins_gain"])
    assert res["C2"]
    assert res["P"]["P2"] is False and res["P"]["P5"] is False
    print("  [2] planted design: P_M winner M, P_G winner grok, N1 / N2 inside the bar, Small UNDETERMINED (support AND C3: same-judge |GP - GK| %.3f > bar), C1 HELD, C2 HELD (cross-fitted gain %+.3f / %+.3f), floor max over scored cells %.3f, falsifier fired on the synthetic data: OK"
          % (res["floor_max"], res["levers"][LEVER_PAIRS[0]]["mean"], res["levers"][LEVER_PAIRS[1]]["mean"], res["floor_max_scored"]))
    # [3] a null-only design: no winner, lever inside the interval
    d0 = Synthetic(seed=11)
    for j in JUDGES:                          # re-draw every verdict at one rate so no cell has a planted winner
        rng = random.Random(100 + JUDGES.index(j))
        for r in d0.rows[j]:
            ka, kb = d0.K[r["q"]][r["a"]], d0.K[r["q"]][r["b"]]
            u = rng.random()
            if u < 0.08:
                r["w"] = "TIE"
            elif ka != kb:
                r["w"] = (r["a"] if ka else r["b"]) if rng.random() < 0.85 else (r["b"] if ka else r["a"])
            else:
                r["w"] = r["a"] if rng.random() < 0.5 else r["b"]
            r["flip"] = int(r["w"] == "TIE")
    d0.finish()
    res0 = readout(200, 40, None, None, d=d0, log=lambda s: print("      " + s), selftest=True, board_B=30)
    assert not res0["C1"] and not res0["winners"], res0["winners"]
    for p in LEVER_PAIRS:
        assert res0["levers"][p]["lo"] <= 0 <= res0["levers"][p]["hi"] or abs(res0["levers"][p]["mean"]) < 0.01, res0["levers"][p]
    assert res0["floor_max_scored"] <= BAR
    print("  [3] null design (every judge 0.85): no cell winner, C1 FAILED, lever interval includes 0 or |gain| < 1pp, verdict CLOSED: OK")
    print("[SELFTEST] OK; nothing written; no cache of record read; no judge call")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--boot", type=int, default=B_BOOT); ap.add_argument("--splits", type=int, default=N_SPLITS)
    ap.add_argument("--out", default=OUT); ap.add_argument("--csv", default=CSV_OUT)
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.dry_run:
        dry_run()
    elif a.run:
        readout(a.boot, a.splits, a.out, a.csv)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
