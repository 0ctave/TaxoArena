"""TOPIC-DIFFICULTY — does a difficulty axis inside a cell change the judge's behaviour and the model order
(zero judge calls; registered 2026-09-17 in docs/judge_v2_program.md before this readout is run).

  python tools/analysis/topic_difficulty.py --dry-run          # pool id first; caches inspected read-only; denominators,
                                                               #   stratum sizes per cell; NO outcome number is printed
  python tools/analysis/topic_difficulty.py --selftest         # the statistics on SYNTHETIC rows (no cache of record is read)
  python tools/analysis/topic_difficulty.py --run [--boot 300] [--perm 200] [--out <path>]
                                                               # the readout; refuses to run unless --run is given

CLAIM UNDER TEST. Inside a cell of the tree a difficulty axis (roster accuracy on the key) changes both the judge's
behaviour and the model order, so a per-cell board hides a difficulty confound: verification fidelity, tie rate and
length preference differ between easy and hard strata, and the within-cell order on hard questions is not the
order on easy ones. Falsifier: per-cell boards are difficulty-INVARIANT (no stratum contrast survives its interval
and the easy-vs-hard order is not below the within-cell permutation null).

INSTRUMENT (a judgment-time artefact of the judged question; nothing is induced; TRAIN-ONLY rule untouched).
  difficulty(q) = fraction of the keyed roster correct on q in eval_results (every model_name with a row for q,
  Meta-Llama-3-70B-Instruct excluded by the standing rule), computed only over the judged questions of pool
  p2dca21ab5f4ef3ae. Secondary instrument: the same fraction over the NON-CONTESTANT roster (models never on the
  merged board), so the strata are not built from the contestants' own key rows. The eval<->mmlu_pro identity is
  checked through the OPTIONS key (json-normalised options_json == mmlu_pro.options), NEVER question_text
  (rule 6); the key used for every accuracy is eval_results.is_correct exactly as systematic_budget.build() reads it.
  Strata: rank terciles WITHIN each cell over the cell's judged questions (ties in difficulty broken by qid so
  the terciles are balanced; the cut values are printed), assigned once per question and shared by every arm.
  Cells: the 14 depth-1 anchors of bareq512_s42 (the tree the boards of record group by: systematic_budget.build()
  and budget_transfer.edges_from route every judged question with r512.primary_routing("bareq512_s42") and take
  r512.anchor_fn; the caches' own `anchor` column is asserted equal to that), and the leaves of the same tree that
  pass the support rule (>= 45 judged questions and >= 20 key-decidable merged-board matches in EVERY tercile).

CACHES OF RECORD (all opened mode=ro; counts pinned; a count mismatch refuses the readout):
  MISTRAL-X12     experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db   9,142 verdicts, 2,811 questions
  MISTRAL-MERGED  + experiment_results/x12_crossdomain/stack_v2_promptv2_x20.db     +12,394 = 21,536 (the board of record)
  GROK-CALIB      experiment_results/x12_crossdomain/grok_calib.db                  9,142 (the x12 schedule, grok judge)
  KOTLIN          experiment_results/judge_wiring/board/kotlin_c0d3f708cbc3930e.db 9,123 (the production path)
  Rule 10: a row whose finish_reason (where recorded) is length / content_filter / empty is NON_TERMINATED = INVALID,
  never a verdict, never a tie; the count of rows this reclassifies is printed.

READOUTS per (arm, cell, tercile): key-decidable accuracy under A (ties / INVALID / non-terminated wrong) and B
(committed verdicts only); tie rate on key-decidable and on all valid matches; INVALID rate; reference-correct
rate and accuracy A within reference-correct / reference-wrong; the record's length fit (bias_audit.h3:
logistic P(winner = a) ~ 1 + (len_a - len_b)/1000 + (key_a - key_b), decisive verdicts only, lengths =
len(eval_results.model_output) as bias_audit._lengths_gt reads them) as beta_len with its SE; the per-stratum
question-clustered Bradley-Terry board (jf.board_from = rj.mm_fit, Jeffreys prior 0.5; B question-resampling draws
within the stratum; a stratum whose comparison graph is disconnected is REFUSED) with the raw certificate per
edge (c_raw = max(p, 1-p) at 0.975), wrong(established) by systematic_budget.mcnemar_edge over the STRATUM's
judged questions, nominal = sum(1 - c_raw) over called edges and the status word by the power rule
(FRAMEWORK.md L101: nominal < 3 -> UNDETERMINED). Per (arm, anchor): Spearman between the easy- and hard-stratum
orders with a question-bootstrap percentile interval AND a within-cell permutation null (tercile labels shuffled
over the cell's questions, sizes preserved), the key's own easy-vs-hard order Spearman beside it (the part of the
shift that is capability, not judge), and Spearman(judge order, key order) per tercile. Pooled contrasts hard -
easy over the 14 anchors with a question-clustered bootstrap interval (questions resampled within each
(anchor, tercile) cell). Residue block: the four established wrong-direction edges of the merged per-anchor board
(KTD-CHECK: Law Llama-3.1-70B vs gpt-4o-mini / deepseek-v2.5 / Qwen1.5-72B, Philosophy Llama-3.1-70B vs
gpt-4o-mini) read per tercile. Deployability line: Spearman between the difficulty instrument (key-derived, NOT
deployable on unkeyed cells) and the key-free plurality agreement of the roster's predicted letters.

OUTPUT. experiment_results/topic_difficulty/topic_difficulty_outcome.txt (+ _rows.csv), written only from the
complete caches; --dry-run writes nothing.
"""
import os, sys, csv, math, json, random, sqlite3, argparse, time
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import pool_guard
import rejudge_grok as rj
import judge_free_tests as jf
import rubric_512 as r512
import systematic_budget as sb
import bias_audit as ba

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

POOL = pool_guard.MMLU_PRO_POOL                   # p2dca21ab5f4ef3ae
TREE = "bareq512_s42"
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
CACHES = {
    "MISTRAL-X12": (os.path.join(X12DIR, "stack_v2_promptv2_x12all.db"), 9142),
    "X20":         (os.path.join(X12DIR, "stack_v2_promptv2_x20.db"), 12394),
    "GROK-CALIB":  (os.path.join(X12DIR, "grok_calib.db"), 9142),
    "KOTLIN":      (os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db"), 9123),
}
ARMS = ["MISTRAL-X12", "MISTRAL-MERGED", "GROK-CALIB", "KOTLIN"]
PRIMARY_ARM = "MISTRAL-MERGED"
OUT_DIR = os.path.join(ROOT, "experiment_results", "topic_difficulty")
OUT = os.path.join(OUT_DIR, "topic_difficulty_outcome.txt")
TERCILES = ["easy", "mid", "hard"]
THRESH = sb.THRESH                                 # 0.975, the certificate of record
LEAF_MIN_Q = 45                                    # support rule for a leaf cell (dry-run 2026-09-17: 13 of 87 leaves pass; at 60/30 only 1)
LEAF_MIN_DEC = 20                                  #   ... key-decidable merged-board matches in EVERY tercile (= MIN_DEC_STRATUM)
MIN_DEC_STRATUM = 20                               # a stratum below this prints its counts and no accuracy
NON_TERMINATED = {"length", "content_filter", ""}
RESIDUE = [("Law", "Meta-Llama-3_1-70B-Instruct", "gpt-4o-mini"), ("Law", "Meta-Llama-3_1-70B-Instruct", "deepseek-chat-v2_5"),
           ("Law", "Meta-Llama-3_1-70B-Instruct", "Qwen1.5-72B-Chat"), ("Philosophy", "Meta-Llama-3_1-70B-Instruct", "gpt-4o-mini")]
RESIDUE_MODEL = "Meta-Llama-3_1-70B-Instruct"      # KTD-CHECK: the residue is model-anchored (every established wrong edge is this model, under-rated)
RESIDUE_ANCHORS = ["Law", "Philosophy"]            # C5 is scored on this block (every opponent); the four named edges are support-limited (dry-run: 47 matches)


def ro(path):
    if not os.path.isfile(path):
        raise SystemExit("[TOPIC-DIFFICULTY] cache not found: %s" % path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# ── the fit of record, vectorised (asserted equal to rj.mm_fit in --selftest) ─────────────────────────────────────

def mm_fit_np(agg, models):
    """Same algorithm as rj.mm_fit (MM for Bradley-Terry with PRIOR = 0.5 pseudo-match per side per observed pair,
    2000 iterations, 1e-12 stop, mean-centred log-strength); numpy inner loop so 10^4 refits are affordable."""
    idx = {m: i for i, m in enumerate(models)}; M = len(models)
    W = np.zeros(M); N = np.zeros((M, M))
    for (a, b), (wa, n) in agg.items():
        i, j = idx[a], idx[b]
        W[i] += wa + rj.PRIOR; W[j] += (n - wa) + rj.PRIOR
        N[i, j] += n + 2 * rj.PRIOR; N[j, i] += n + 2 * rj.PRIOR
    p = np.ones(M); mask = N != 0
    for _ in range(2000):
        S = p[:, None] + p[None, :]
        den = np.where(mask, N / S, 0.0).sum(axis=1)
        new = np.where(den > 0, W / np.where(den > 0, den, 1.0), p)
        new = new / (new.sum() / M)
        if np.max(np.abs(new - p)) < 1e-12:
            p = new; break
        p = new
    th = np.log(np.maximum(p, 1e-300)); th -= th.mean()
    return {m: float(th[idx[m]]) for m in models}


def agg_from(rows):
    """rows: (a, b, q, w) with w in {a, b, 'TIE'} -> {(min, max): (winsMin, n)} exactly as jf.board_from aggregates."""
    agg = defaultdict(lambda: [0.0, 0.0])
    for a, b, _, w in rows:
        wa = 0.5 if w == "TIE" else (1.0 if w == a else 0.0)
        if a > b:
            a, b, wa = b, a, 1.0 - wa
        rec = agg[(a, b)]; rec[0] += wa; rec[1] += 1.0
    return {k: tuple(v) for k, v in agg.items()}


def connected(agg, models):
    parent = {m: m for m in models}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for (a, b), (_, n) in agg.items():
        if n > 0:
            parent[find(a)] = find(b)
    return len({find(m) for m in models}) == 1


# ── data ─────────────────────────────────────────────────────────────────────────────────────────────────────

class Data:
    """Every object the readout touches, loaded once; nothing here is an outcome number."""

    def __init__(self, log):
        self.log = log
        # tree of record for the boards (CONTEXT.md S3: promoted bareq512_s42; systematic_budget.build routes by it)
        snap = r512.snapshot_id(TREE); nodes = r512.load_graph(snap)
        self.route = r512.primary_routing(TREE); anchor_of = r512.anchor_fn(nodes)
        self.leaf_of = dict(self.route); self.anchor_of_leaf = {l: anchor_of(l) for l in set(self.route.values())}
        self.anchor_of_q = {q: self.anchor_of_leaf[l] for q, l in self.route.items()}
        log("tree %s snapshot %s | %d nodes, %d leaves, %d routed pool questions, %d anchors"
            % (TREE, snap, len(nodes), len(self.anchor_of_leaf), len(self.route), len(set(self.anchor_of_leaf.values()))))
        # caches, read-only, counts pinned
        self.raw = {}
        for name, (path, pinned) in CACHES.items():
            con = ro(path)
            cols = [c[1] for c in con.execute("PRAGMA table_info(verdicts)")]
            has_fin = "finish1" in cols
            q = ("SELECT match_id, model_a, model_b, qid, winner, invalid, ref_correct" + (", finish1, finish2" if has_fin else ", NULL, NULL")
                 + " FROM verdicts")
            rows = con.execute(q).fetchall(); con.close()
            if len(rows) != pinned:
                raise SystemExit("[TOPIC-DIFFICULTY] %s holds %d verdict rows, the record pins %d: refusing" % (name, len(rows), pinned))
            reclass = 0; out = []
            for mid, a, b, qid, w, inv, rc, f1, f2 in rows:
                inv = int(inv or 0)
                if has_fin and ((f1 or "") in NON_TERMINATED or (f2 or "") in NON_TERMINATED) and not inv:
                    inv = 1; reclass += 1               # rule 10: never a verdict, never a tie
                if inv:
                    w = "INVALID"
                out.append((mid, a, b, int(qid), w, inv, -1 if rc is None else int(rc)))
            self.raw[name] = out
            log("cache %-12s %s | %d rows (pinned %d) | INVALID %d | finish columns %s | rule-10 reclassified %d"
                % (name, os.path.relpath(path, ROOT), len(out), pinned, sum(r[5] for r in out), "yes" if has_fin else "no", reclass))
        # KOTLIN records no ref_correct; the reference kit is the same cached solve -> take it from the x12 cache by match_id
        rc12 = {r[0]: r[6] for r in self.raw["MISTRAL-X12"]}
        self.raw["KOTLIN"] = [(mid, a, b, q, w, inv, rc12.get(mid, -1)) for mid, a, b, q, w, inv, _ in self.raw["KOTLIN"]]
        self.arms = {"MISTRAL-X12": self.raw["MISTRAL-X12"], "MISTRAL-MERGED": self.raw["MISTRAL-X12"] + self.raw["X20"],
                     "GROK-CALIB": self.raw["GROK-CALIB"], "KOTLIN": self.raw["KOTLIN"]}
        q12 = {r[3] for r in self.raw["MISTRAL-X12"]}; q20 = {r[3] for r in self.raw["X20"]}
        qk = {r[3] for r in self.raw["KOTLIN"]}; qg = {r[3] for r in self.raw["GROK-CALIB"]}
        log("judged questions: x12 %d | x20 %d (not in x12: %d) | grok %d (delta x12: %d) | kotlin %d (delta x12: %d); matches kotlin not in x12: %d"
            % (len(q12), len(q20), len(q20 - q12), len(qg), len(qg ^ q12), len(qk), len(qk - q12),
               len({r[0] for r in self.raw["KOTLIN"]} - {r[0] for r in self.raw["MISTRAL-X12"]})))
        self.judged = sorted(q12 | q20 | qk | qg)
        pool_guard.assert_scored_subset(POOL, self.judged, out=sys.stdout)
        unrouted = [q for q in self.judged if q not in self.anchor_of_q]
        if unrouted:
            raise SystemExit("[TOPIC-DIFFICULTY] %d judged questions have no route in %s" % (len(unrouted), TREE))
        # the caches' anchor column must be the tree's anchor
        for name, (path, _) in CACHES.items():
            con = ro(path); bad = 0
            for qid, anc in con.execute("SELECT qid, anchor FROM verdicts"):
                if self.anchor_of_q.get(int(qid)) != anc:
                    bad += 1
            con.close()
            log("anchor column check %-12s %d rows disagree with anchor_fn(route[qid]) on %s" % (name, bad, TREE))
            if bad:
                raise SystemExit("[TOPIC-DIFFICULTY] anchor column mismatch in %s" % name)
        self.contestants = sorted({r[1] for r in self.arms["MISTRAL-MERGED"]} | {r[2] for r in self.arms["MISTRAL-MERGED"]})
        # key, predictions, lengths (eval_results), the difficulty instrument
        ev = ro(rj.EVAL_DB)
        jset = set(self.judged)
        self.K = defaultdict(dict); self.P = defaultdict(dict); self.L = {}
        roster = set()
        for q, m, pr, c, out in ev.execute("SELECT question_id, model_name, pred, is_correct, model_output FROM eval_results"):
            if m in EXCLUDED:
                continue
            roster.add(m)
            if q in jset:
                self.K[q][m] = int(c or 0); self.P[q][m] = (pr or "").strip().upper()[:1]; self.L[(q, m)] = len(out or "")
        self.roster = sorted(roster); self.outside = sorted(roster - set(self.contestants))
        self.diff = {q: sum(self.K[q].values()) / len(self.K[q]) for q in self.judged if self.K[q]}
        self.diff_out = {q: (sum(self.K[q][m] for m in self.outside if m in self.K[q]) / max(1, sum(1 for m in self.outside if m in self.K[q])))
                         for q in self.judged if any(m in self.K[q] for m in self.outside)}
        dens = [len(self.K[q]) for q in self.judged]
        log("difficulty instrument: keyed roster %d models (%s excluded; %d contestants on the merged board, %d outside models for the "
            "secondary instrument) | per-question denominator min %d / median %d / max %d over %d judged questions | %d judged questions "
            "without any key row" % (len(self.roster), ", ".join(sorted(EXCLUDED)), len(self.contestants), len(self.outside),
                                     min(dens), int(np.median(dens)), max(dens), len(self.judged), sum(1 for d in dens if d == 0)))
        # key-free plurality agreement of the roster's predicted letters (the deployable proxy candidate)
        self.plur = {}
        for q in self.judged:
            letters = [v for v in self.P[q].values() if v]
            if letters:
                self.plur[q] = Counter(letters).most_common(1)[0][1] / len(letters)
        # eval <-> mmlu_pro identity through the OPTIONS key (never question_text), on the judged questions only
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
        log("OPTIONS-key join eval_results -> mmlu_pro on the %d judged questions: 1:1 %d | multi %d | none %d | gt_answer == mmlu_pro.answer on %d of %d matched"
            % (len(self.judged), matched, multi, none, agree, matched))
        self.join_fidelity = (matched, multi, none, agree)
        # strata: rank terciles within each cell, one assignment per question, shared by every arm
        self.cells = {}                                 # cell name -> sorted judged questions
        by_anchor = defaultdict(list); by_leaf = defaultdict(list)
        for q in self.judged:
            if q in self.diff:
                by_anchor[self.anchor_of_q[q]].append(q); by_leaf[self.leaf_of[q]].append(q)
        self.tercile = {}                               # (cell, q) -> tercile
        self.cuts = {}
        for kind, groups in (("anchor", by_anchor), ("leaf", by_leaf)):
            for c, qs in groups.items():
                name = c if kind == "anchor" else "leaf:" + c
                self.cells[name] = sorted(qs)
                order = sorted(qs, key=lambda q: (self.diff[q], q))
                n = len(order); b1, b2 = n // 3, (2 * n) // 3
                for i, q in enumerate(order):
                    self.tercile[(name, q)] = "easy" if i >= b2 else ("mid" if i >= b1 else "hard")
                self.cuts[name] = (self.diff[order[b1]] if n > b1 else float("nan"), self.diff[order[b2]] if n > b2 else float("nan"))
        self.anchors = sorted(by_anchor)
        self.leaves = sorted("leaf:" + l for l in by_leaf)

    # ── row selection ──
    def rows(self, arm, cell, terc=None):
        qs = set(self.cells[cell])
        out = [r for r in self.arms[arm] if r[3] in qs and (terc is None or self.tercile[(cell, r[3])] == terc)]
        return out

    def decidable(self, r):
        ka, kb = self.K[r[3]].get(r[1]), self.K[r[3]].get(r[2])
        return ka is not None and kb is not None and ka != kb

    def leaf_qualifies(self, leaf):
        if len(self.cells[leaf]) < LEAF_MIN_Q:
            return False
        for t in TERCILES:
            if sum(1 for r in self.rows(PRIMARY_ARM, leaf, t) if not r[5] and self.decidable(r)) < LEAF_MIN_DEC:
                return False
        return True


# ── per-stratum statistics ─────────────────────────────────────────────────────────────────────────────────

def stratum_basic(d, rows):
    """Counts and rates on one (arm, cell, tercile) slice. Returns a dict; rates None when the slice is too small."""
    valid = [r for r in rows if not r[5]]
    dec = [r for r in valid if d.decidable(r)]
    dec_all = [r for r in rows if d.decidable(r)]              # A's denominator includes INVALID / non-terminated
    ok = sum(1 for r in dec if r[4] == (r[1] if d.K[r[3]][r[1]] else r[2]))
    committed = [r for r in dec if r[4] in (r[1], r[2])]
    ok_c = sum(1 for r in committed if r[4] == (r[1] if d.K[r[3]][r[1]] else r[2]))
    res = dict(nq=len({r[3] for r in rows}), nm=len(rows), ninv=len(rows) - len(valid), ndec=len(dec_all), ndec_valid=len(dec),
               ties_dec=sum(1 for r in dec if r[4] == "TIE"), ties_all=sum(1 for r in valid if r[4] == "TIE"),
               ncommitted=len(committed), okA=ok, okB=ok_c)
    res["accA"] = ok / len(dec_all) if len(dec_all) >= MIN_DEC_STRATUM else None
    res["accB"] = ok_c / len(committed) if len(committed) >= MIN_DEC_STRATUM else None
    res["tie_dec"] = res["ties_dec"] / len(dec) if dec else None
    res["tie_all"] = res["ties_all"] / len(valid) if valid else None
    res["inv_rate"] = res["ninv"] / len(rows) if rows else None
    # reference strata
    for flag, tag in ((1, "refok"), (0, "refwrong")):
        sub = [r for r in dec_all if r[6] == flag]
        okf = sum(1 for r in sub if r[4] == (r[1] if d.K[r[3]][r[1]] else r[2]))
        res["n_" + tag] = len(sub); res["accA_" + tag] = okf / len(sub) if len(sub) >= MIN_DEC_STRATUM else None
    res["ref_rate"] = res["n_refok"] / (res["n_refok"] + res["n_refwrong"]) if (res["n_refok"] + res["n_refwrong"]) else None
    # length fit of record (bias_audit.h3): decisive verdicts only
    X, Y = [], []
    for r in valid:
        if r[4] not in (r[1], r[2]):
            continue
        la, lb = d.L.get((r[3], r[1])), d.L.get((r[3], r[2]))
        if la is None or lb is None:
            continue
        X.append(((la - lb) / 1000.0, d.K[r[3]].get(r[1], 0) - d.K[r[3]].get(r[2], 0))); Y.append(1.0 if r[4] == r[1] else 0.0)
    res["n_len"] = len(Y)
    if len(Y) >= 50 and 0 < sum(Y) < len(Y):
        try:
            b, s = ba._logit3(X, Y)
            res["beta_len"], res["se_len"], res["beta_gt"] = b[1], s[1], b[2]
        except Exception:
            res["beta_len"] = res["se_len"] = res["beta_gt"] = None
    else:
        res["beta_len"] = res["se_len"] = res["beta_gt"] = None
    return res


def stratum_board(d, rows, models, B, rng):
    """Question-clustered BT on one slice: point board, B question-resampling draws, edges with the raw certificate,
    wrong(established) by sb.mcnemar_edge on the slice's judged questions. None when the graph is disconnected."""
    valid = [(r[1], r[2], r[3], r[4]) for r in rows if not r[5]]
    if not valid:
        return None
    present = sorted({a for a, _, _, _ in valid} | {b for _, b, _, _ in valid})
    ms = [m for m in models if m in present]
    agg = agg_from(valid)
    if len(ms) < 3 or not connected(agg, ms):
        return dict(refused=True, models=ms, n=len(valid))
    theta = mm_fit_np(agg, ms)
    qs = sorted({q for _, _, q, _ in valid}); byq = defaultdict(list)
    for r in valid:
        byq[r[2]].append(r)
    draws = []
    for _ in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        sub = [r for q in pick for r in byq[q]]
        draws.append(mm_fit_np(agg_from(sub), ms))
    la = {}
    for m in ms:
        v = [d.K[q].get(m) for q in qs if d.K[q].get(m) is not None]
        if v:
            la[m] = sum(v) / len(v)
    edges = []
    for i, a in enumerate(ms):
        for b in ms[i + 1:]:
            if a not in la or b not in la or la[a] == la[b]:
                continue
            dd = np.array([dr[a] - dr[b] for dr in draws]); p = float((dd > 0).mean())
            edges.append(dict(anchor="S", a=a, b=b, p=p, m=float(dd.mean()), s=float(dd.std(ddof=1)) if B > 1 else 0.0,
                              right=((p > 0.5) == (la[a] > la[b]))))
    aq = {"S": qs}
    called = [e for e in edges if sb.craw(e) >= THRESH]
    wrong = [e for e in called if not e["right"]]
    est = [e for e in wrong if sb.mcnemar_edge(e, d.K, aq)[0] < 0.05]
    nominal = sum(1 - sb.craw(e) for e in called)
    return dict(refused=False, models=ms, theta=theta, draws=draws, keyacc=la, nq=len(qs), n=len(valid), edges=len(edges),
                called=len(called), wrong=len(wrong), wrong_est=len(est), nominal=nominal, status=power_status(nominal, len(wrong)),
                wrong_list=[(e["a"], e["b"]) for e in est])


def power_status(nominal, wrong):
    """FRAMEWORK.md L101, the status word; 'calibrated' is never emitted."""
    if nominal < 3:
        return "UNDETERMINED (nominal < 3)"
    if nominal < 9:
        return "UNDETERMINED (power: 2x undetectable)"
    from scipy.stats import poisson
    return "NOT DETECTABLY MISCALIBRATED" if poisson.sf(wrong - 1, nominal) > 0.05 else "MISCALIBRATED"


def spearman_common(t1, t2):
    ms = sorted(set(t1) & set(t2))
    if len(ms) < 4:
        return float("nan"), len(ms)
    return rj.spearman([t1[m] for m in ms], [t2[m] for m in ms]), len(ms)


def order_block(d, arm, cell, models, B, nperm, rng, boards=None):
    """Easy-vs-hard order per cell: point Spearman, question-bootstrap interval (both strata resampled independently),
    within-cell permutation null (tercile labels shuffled over the cell's questions, sizes preserved), the key's own
    easy-vs-hard Spearman and the judge-vs-key Spearman per tercile. `boards` = the stratum boards already fitted."""
    if boards is None:
        boards = {t: stratum_board(d, d.rows(arm, cell, t), models, B, rng) for t in TERCILES}
    out = dict(boards=boards)
    if any(b is None or b["refused"] for b in boards.values()):
        out["refused"] = True; return out
    out["refused"] = False
    e, h, m_ = boards["easy"], boards["hard"], boards["mid"]
    out["rho_eh"], out["n_eh"] = spearman_common(e["theta"], h["theta"])
    out["rho_em"], _ = spearman_common(e["theta"], m_["theta"]); out["rho_mh"], _ = spearman_common(m_["theta"], h["theta"])
    out["key_eh"], _ = spearman_common(e["keyacc"], h["keyacc"])
    out["jk"] = {t: spearman_common(boards[t]["theta"], boards[t]["keyacc"])[0] for t in TERCILES}
    # bootstrap interval: pair draw i of easy with draw i of hard (independent resamples of the two strata)
    bs = [spearman_common(e["draws"][i], h["draws"][i])[0] for i in range(min(len(e["draws"]), len(h["draws"])))]
    bs = [x for x in bs if not math.isnan(x)]
    out["ci_eh"] = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if bs else (float("nan"), float("nan"))
    # permutation null within the cell
    qs = list(d.cells[cell]); labels = [d.tercile[(cell, q)] for q in qs]
    rows_all = d.rows(arm, cell); null = []
    for _ in range(nperm):
        perm = labels[:]; rng.shuffle(perm); lab = dict(zip(qs, perm))
        te = [(r[1], r[2], r[3], r[4]) for r in rows_all if not r[5] and lab[r[3]] == "easy"]
        th = [(r[1], r[2], r[3], r[4]) for r in rows_all if not r[5] and lab[r[3]] == "hard"]
        ae, ah = agg_from(te), agg_from(th)
        me = [m for m in models if m in {a for a, _, _, _ in te} | {b for _, b, _, _ in te}]
        mh = [m for m in models if m in {a for a, _, _, _ in th} | {b for _, b, _, _ in th}]
        if len(me) < 3 or len(mh) < 3 or not connected(ae, me) or not connected(ah, mh):
            continue
        r_, _ = spearman_common(mm_fit_np(ae, me), mm_fit_np(ah, mh))
        if not math.isnan(r_):
            null.append(r_)
    out["null_n"] = len(null)
    out["null_p5"] = float(np.percentile(null, 5)) if null else float("nan")
    out["null_p50"] = float(np.percentile(null, 50)) if null else float("nan")
    out["null_pval"] = (sum(1 for x in null if x <= out["rho_eh"]) + 1) / (len(null) + 1) if null else float("nan")
    out["below_null"] = bool(null) and out["rho_eh"] < out["null_p5"]
    return out


def pooled_contrast(d, arm, cells, stat, B, rng):
    """hard - easy on the statistic pooled over the cells (each question's tercile assigned within its own cell), with a
    question-clustered bootstrap interval: questions resampled within every (cell, tercile) slice. stat in {'accA', 'tie_dec'}."""
    def value(slices):
        num = den = 0
        for rows in slices:
            for r in rows:
                if stat == "accA":
                    if d.decidable(r):
                        den += 1; num += int(r[4] == (r[1] if d.K[r[3]][r[1]] else r[2]))
                elif stat == "tie_dec":
                    if not r[5] and d.decidable(r):
                        den += 1; num += int(r[4] == "TIE")
        return num / den if den else float("nan"), den
    by = {t: [d.rows(arm, c, t) for c in cells] for t in ("easy", "hard")}
    pe, ne = value(by["easy"]); ph, nh = value(by["hard"])
    diffs = []
    byq = {t: [defaultdict(list) for _ in cells] for t in by}
    for t in by:
        for i, rows in enumerate(by[t]):
            for r in rows:
                byq[t][i][r[3]].append(r)
    for _ in range(B):
        res = {}
        for t in by:
            sl = []
            for i in range(len(cells)):
                qs = list(byq[t][i]); pick = [qs[rng.randrange(len(qs))] for _ in qs] if qs else []
                sl.append([r for q in pick for r in byq[t][i][q]])
            res[t] = value(sl)[0]
        diffs.append(res["hard"] - res["easy"])
    return dict(easy=pe, n_easy=ne, hard=ph, n_hard=nh, diff=ph - pe,
                ci=(float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))))


# ── dry-run ────────────────────────────────────────────────────────────────────────────────────────────────

def dry_run():
    print("reserved_pool_id=%s" % POOL)
    pool_guard.assert_pool_of_record(POOL)
    print("[DRY-RUN] TOPIC-DIFFICULTY | zero judge calls | caches opened mode=ro | nothing written | no outcome number below")
    d = Data(lambda s: print("  " + s))
    print("  arms: %s (primary %s)" % (", ".join(ARMS), PRIMARY_ARM))
    print("  models on the merged board (%d): %s" % (len(d.contestants), ", ".join(d.contestants)))
    print("  outside roster for the secondary instrument (%d): %s" % (len(d.outside), ", ".join(d.outside)))
    print("  difficulty instrument (primary, %d-model roster) over the %d judged questions: mean %.3f | quartiles %.3f / %.3f / %.3f"
          % (len(d.roster), len(d.diff), float(np.mean(list(d.diff.values()))), *[float(np.percentile(list(d.diff.values()), p)) for p in (25, 50, 75)]))
    print("  strata per ANCHOR (tercile cuts: hard < c1 <= mid < c2 <= easy, rank-based (c = first value of the next tercile); per arm: matches / key-decidable matches per tercile):")
    hdr = "  %-17s %5s %6s %6s | " % ("anchor", "nq", "c1", "c2") + " | ".join("%-27s" % a for a in ARMS)
    print(hdr)
    for c in d.anchors:
        cells = []
        for arm in ARMS:
            parts = []
            for t in TERCILES:
                rows = d.rows(arm, c, t); nd = sum(1 for r in rows if d.decidable(r))
                parts.append("%d/%d" % (len(rows), nd))
            cells.append("%-27s" % " ".join(parts))
        print("  %-17s %5d %6.3f %6.3f | %s" % (c, len(d.cells[c]), d.cuts[c][0], d.cuts[c][1], " | ".join(cells)))
    print("  questions per tercile per anchor: %s" % ", ".join("%s %s" % (c, "/".join(str(sum(1 for q in d.cells[c] if d.tercile[(c, q)] == t)) for t in TERCILES)) for c in d.anchors))
    ql = [l for l in d.leaves if d.leaf_qualifies(l)]
    print("  LEAF cells: %d leaves carry judged questions; %d pass the support rule (>= %d questions and >= %d key-decidable %s matches in every tercile)"
          % (len(d.leaves), len(ql), LEAF_MIN_Q, LEAF_MIN_DEC, PRIMARY_ARM))
    for l in ql:
        parts = []
        for t in TERCILES:
            rows = d.rows(PRIMARY_ARM, l, t); parts.append("%d/%d" % (len(rows), sum(1 for r in rows if d.decidable(r))))
        print("    %-40s anchor %-16s nq %4d cuts %.3f/%.3f | %s: %s" % (l[5:], d.anchor_of_leaf[l[5:]], len(d.cells[l]), d.cuts[l][0], d.cuts[l][1], PRIMARY_ARM, " ".join(parts)))
    print("  residue edges (KTD-CHECK, merged per-anchor board) matches / key-decidable per tercile on %s:" % PRIMARY_ARM)
    for anc, a, b in RESIDUE:
        parts = []
        for t in TERCILES:
            rows = [r for r in d.rows(PRIMARY_ARM, anc, t) if {r[1], r[2]} == {a, b}]
            parts.append("%d/%d" % (len(rows), sum(1 for r in rows if d.decidable(r))))
        print("    %-11s %s vs %-20s %s" % (anc, a, b, " ".join(parts)))
    for anc in RESIDUE_ANCHORS:
        parts = []
        for t in TERCILES:
            rows = [r for r in d.rows(PRIMARY_ARM, anc, t) if RESIDUE_MODEL in (r[1], r[2])]
            dec = [r for r in rows if d.decidable(r)]
            parts.append("%d/%d/%d" % (len(rows), len(dec), sum(1 for r in dec if d.K[r[3]][RESIDUE_MODEL])))
        print("    %-11s %s vs every opponent (C5 block): matches / key-decidable / key gives it, per tercile: %s" % (anc, RESIDUE_MODEL, " ".join(parts)))
    relaxed = sum(1 for l in d.leaves if len(d.cells[l]) >= 45 and all(sum(1 for r in d.rows(PRIMARY_ARM, l, t) if not r[5] and d.decidable(r)) >= MIN_DEC_STRATUM for t in TERCILES))
    print("  leaves at a relaxed bar (>= 45 questions, >= %d key-decidable per tercile): %d of %d - leaf-level strata are support-limited on this board" % (MIN_DEC_STRATUM, relaxed, len(d.leaves)))
    print("  the length fit of record: bias_audit.h3 (_logit3: P(winner = a) ~ 1 + dlen/1k + dkey, decisive only); the BT fit of record: "
          "jf.board_from -> rj.mm_fit (prior %.1f), reproduced by mm_fit_np (asserted in --selftest); wrong(established): systematic_budget.mcnemar_edge; "
          "certificate %.3f raw" % (rj.PRIOR, THRESH))
    print("[DRY-RUN] done: no outcome computed. Run with --run after the registration is committed.")


# ── the readout ──────────────────────────────────────────────────────────────────────────────────────────────

def fmt(x, pct=True, nd=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "   n/a"
    return ("%6.1f" % (100 * x)) if pct else ("%+.3f" % x)


def readout(B, nperm, out_path, d=None, log=print, selftest=False):
    L = []
    def w(s=""):
        L.append(s); log(s)
    t0 = time.time()
    rng = random.Random(42)
    if d is None:
        w("reserved_pool_id=%s" % POOL)
        pool_guard.assert_pool_of_record(POOL)
        d = Data(lambda s: w("  " + s))
    w("=== TOPIC-DIFFICULTY readout (zero judge calls) | tree %s | pool %s | B %d | perms %d | certificate %.3f raw | %s ==="
      % (TREE, POOL, B, nperm, THRESH, "SELFTEST ON SYNTHETIC ROWS - NOT A RESULT" if selftest else time.strftime("%Y-%m-%d %H:%M")))
    w("  conventions: A = ties / INVALID / non-terminated wrong on key-decidable; B = committed verdicts only; wrong(established) by exact McNemar on the stratum's judged questions;")
    w("  power rule: nominal < 3 -> UNDETERMINED; a stratum under %d key-decidable matches prints counts and no rate." % MIN_DEC_STRATUM)
    rows_csv = []
    models_of = {arm: sorted({r[1] for r in d.arms[arm]} | {r[2] for r in d.arms[arm]}) for arm in ARMS}
    ql = [l for l in d.leaves if d.leaf_qualifies(l)]
    basic = {}
    for arm in ARMS:
        w(""); w("--- arm %s (%d verdicts, %d models) ---" % (arm, len(d.arms[arm]), len(models_of[arm])))
        w("  %-40s %-4s %4s %5s %5s | accA   accB  | tie_dec tie_all inv | ref%%  accA|ref+ accA|ref- | beta_len (se)   n    | called wrong(est) nominal status"
          % ("cell", "terc", "nq", "nm", "ndec"))
        for cell in d.anchors + (ql if arm == PRIMARY_ARM else []):
            for t in TERCILES:
                rows = d.rows(arm, cell, t)
                s = stratum_basic(d, rows)
                bd = stratum_board(d, rows, models_of[arm], B, rng)
                basic[(arm, cell, t)] = (s, bd)
                if bd is None or bd["refused"]:
                    cert = "REFUSED (disconnected or < 3 models)"
                else:
                    cert = "%3d %3d(%d) %6.2f %s" % (bd["called"], bd["wrong"], bd["wrong_est"], bd["nominal"], bd["status"])
                w("  %-40s %-4s %4d %5d %5d | %s %s | %s %s %s | %s %s %s | %s (%s) %5d | %s"
                  % (cell[:40], t, s["nq"], s["nm"], s["ndec"], fmt(s["accA"]), fmt(s["accB"]), fmt(s["tie_dec"]), fmt(s["tie_all"]), fmt(s["inv_rate"]),
                     fmt(s["ref_rate"]), fmt(s["accA_refok"]), fmt(s["accA_refwrong"]),
                     fmt(s["beta_len"], False), ("%.3f" % s["se_len"]) if s["se_len"] is not None else "n/a", s["n_len"], cert))
                rows_csv.append(dict(arm=arm, cell=cell, tercile=t, **{k: v for k, v in s.items()},
                                     called=None if not bd or bd["refused"] else bd["called"], wrong=None if not bd or bd["refused"] else bd["wrong"],
                                     wrong_est=None if not bd or bd["refused"] else bd["wrong_est"], nominal=None if not bd or bd["refused"] else bd["nominal"]))
            # whole-cell line for reference (the per-cell board as published)
            s = stratum_basic(d, d.rows(arm, cell))
            w("  %-40s %-4s %4d %5d %5d | %s %s | %s %s %s | %s %s %s | %s (%s) %5d | (whole cell, for reference)"
              % (cell[:40], "all", s["nq"], s["nm"], s["ndec"], fmt(s["accA"]), fmt(s["accB"]), fmt(s["tie_dec"]), fmt(s["tie_all"]), fmt(s["inv_rate"]),
                 fmt(s["ref_rate"]), fmt(s["accA_refok"]), fmt(s["accA_refwrong"]), fmt(s["beta_len"], False),
                 ("%.3f" % s["se_len"]) if s["se_len"] is not None else "n/a", s["n_len"]))
        # pooled over anchors
        w("  POOLED over the %d anchors (each question's tercile within its own anchor):" % len(d.anchors))
        for t in TERCILES:
            s = stratum_basic(d, [r for c in d.anchors for r in d.rows(arm, c, t)])
            basic[(arm, "POOLED", t)] = (s, None)
            w("    %-4s nq %4d nm %5d ndec %5d | accA %s accB %s | tie_dec %s tie_all %s inv %s | ref%% %s accA|ref+ %s accA|ref- %s | beta_len %s (%s) n %d"
              % (t, s["nq"], s["nm"], s["ndec"], fmt(s["accA"]), fmt(s["accB"]), fmt(s["tie_dec"]), fmt(s["tie_all"]), fmt(s["inv_rate"]),
                 fmt(s["ref_rate"]), fmt(s["accA_refok"]), fmt(s["accA_refwrong"]), fmt(s["beta_len"], False),
                 ("%.3f" % s["se_len"]) if s["se_len"] is not None else "n/a", s["n_len"]))
        for stat, name in (("accA", "accuracy A (key-decidable)"), ("tie_dec", "tie rate (key-decidable)")):
            pc = pooled_contrast(d, arm, d.anchors, stat, B, rng)
            basic[(arm, "CONTRAST", stat)] = pc
            w("    CONTRAST hard - easy, %s: easy %.3f (n %d) hard %.3f (n %d) diff %+.1fpp, question-clustered bootstrap 95%% [%+.1f, %+.1f]pp"
              % (name, pc["easy"], pc["n_easy"], pc["hard"], pc["n_hard"], 100 * pc["diff"], 100 * pc["ci"][0], 100 * pc["ci"][1]))
        se_, sh_ = basic[(arm, "POOLED", "easy")][0], basic[(arm, "POOLED", "hard")][0]
        if se_["beta_len"] is not None and sh_["beta_len"] is not None:
            z = (sh_["beta_len"] - se_["beta_len"]) / math.sqrt(se_["se_len"] ** 2 + sh_["se_len"] ** 2)
            basic[(arm, "CONTRAST", "beta_len")] = z
            w("    CONTRAST beta_len hard - easy: %+.4f - %+.4f = %+.4f per 1k chars, z %+.2f (independent strata)" % (sh_["beta_len"], se_["beta_len"], sh_["beta_len"] - se_["beta_len"], z))
        # order block per anchor
        w("  ORDER per anchor: Spearman(easy, hard) [question-bootstrap 95%] | within-cell permutation null p5 / p50 (n) p | key's own rho(easy, hard) | rho(judge, key) easy/mid/hard | rho(e,m) rho(m,h)")
        below = 0; rhos = []; keyrhos = []
        for cell in d.anchors:
            ob = order_block(d, arm, cell, models_of[arm], B, nperm, rng, boards={t: basic[(arm, cell, t)][1] for t in TERCILES})
            basic[(arm, cell, "ORDER")] = ob
            if ob["refused"]:
                w("    %-17s REFUSED (a stratum's comparison graph is disconnected)" % cell); continue
            below += int(ob["below_null"]); rhos.append(ob["rho_eh"]); keyrhos.append(ob["key_eh"])
            w("    %-17s rho %+.3f [%+.3f, %+.3f] (%d models) | null p5 %+.3f p50 %+.3f (%d) p %.3f %s | key %+.3f | j-k %+.3f / %+.3f / %+.3f | %+.3f %+.3f"
              % (cell, ob["rho_eh"], ob["ci_eh"][0], ob["ci_eh"][1], ob["n_eh"], ob["null_p5"], ob["null_p50"], ob["null_n"], ob["null_pval"],
                 "BELOW" if ob["below_null"] else "within", ob["key_eh"], ob["jk"]["easy"], ob["jk"]["mid"], ob["jk"]["hard"], ob["rho_em"], ob["rho_mh"]))
        basic[(arm, "ORDER", "summary")] = (below, len(rhos), float(np.median(rhos)) if rhos else float("nan"), float(np.median(keyrhos)) if keyrhos else float("nan"))
        w("    summary: %d of %d anchors BELOW the permutation null's p5 | median rho(easy, hard) judge %+.3f, key %+.3f"
          % (below, len(rhos), basic[(arm, "ORDER", "summary")][2], basic[(arm, "ORDER", "summary")][3]))
    # residue block on the primary arm
    w(""); w("--- residue (KTD-CHECK: four established wrong-direction edges, all %s under-rated) by tercile on %s ---" % (RESIDUE_MODEL, PRIMARY_ARM))
    w("  per tercile: matches | key-decidable | key gives %s | judge gives it on those | judge gives the opponent on those (= wrong direction) | ties on those" % RESIDUE_MODEL[:14])
    def residue_counts(rows, a):
        dec = [r for r in rows if d.decidable(r)]
        ka = [r for r in dec if d.K[r[3]][a]]
        ja = sum(1 for r in ka if r[4] == a); jb = sum(1 for r in ka if r[4] not in (a, "TIE", "INVALID")); jt = sum(1 for r in ka if r[4] == "TIE")
        return [len(rows), len(dec), len(ka), ja, jb, jt]
    res_named = {t: [0] * 6 for t in TERCILES}
    for anc, a, b in RESIDUE:
        parts = []
        for t in TERCILES:
            c = residue_counts([r for r in d.rows(PRIMARY_ARM, anc, t) if {r[1], r[2]} == {a, b}], a)
            for i, v in enumerate(c):
                res_named[t][i] += v
            parts.append("%s %s" % (t, "|".join(str(v) for v in c)))
        w("  %-11s %s vs %-20s %s" % (anc, a, b, "  ".join(parts)))
    w("  %-11s %-55s %s" % ("pooled", "four named edges (support-limited)", "  ".join("%s %s" % (t, "|".join(str(v) for v in res_named[t])) for t in TERCILES)))
    res_tot = {t: [0] * 6 for t in TERCILES}
    for anc in RESIDUE_ANCHORS:
        parts = []
        for t in TERCILES:
            c = residue_counts([r for r in d.rows(PRIMARY_ARM, anc, t) if RESIDUE_MODEL in (r[1], r[2])], RESIDUE_MODEL)
            for i, v in enumerate(c):
                res_tot[t][i] += v
            parts.append("%s %s" % (t, "|".join(str(v) for v in c)))
        w("  %-11s %s vs %-20s %s" % (anc, RESIDUE_MODEL, "every opponent", "  ".join(parts)))
    w("  %-11s %-55s %s" % ("pooled", "%s vs every opponent, Law + Philosophy (C5 block)" % RESIDUE_MODEL[:14], "  ".join("%s %s" % (t, "|".join(str(v) for v in res_tot[t])) for t in TERCILES)))
    basic["residue"] = res_tot; basic["residue_named"] = res_named
    w("  %s on the stratum boards of %s: judge rank / key rank (of n models), established wrong-direction edges naming it:" % (RESIDUE_MODEL, PRIMARY_ARM))
    for anc in RESIDUE_ANCHORS:
        parts = []
        for t in TERCILES:
            bd = basic.get((PRIMARY_ARM, anc, t), (None, None))[1]
            if bd is None or bd["refused"] or RESIDUE_MODEL not in bd["theta"]:
                parts.append("%s REFUSED" % t); continue
            ms = bd["models"]; jr = sorted(ms, key=lambda m: -bd["theta"][m]).index(RESIDUE_MODEL) + 1
            km = [m for m in ms if m in bd["keyacc"]]; kr = sorted(km, key=lambda m: -bd["keyacc"][m]).index(RESIDUE_MODEL) + 1 if RESIDUE_MODEL in bd["keyacc"] else -1
            named = [b if a == RESIDUE_MODEL else a for a, b in bd["wrong_list"] if RESIDUE_MODEL in (a, b)]
            parts.append("%s %d/%d (of %d) wrong(est) vs [%s]" % (t, jr, kr, len(ms), ", ".join(x[:14] for x in named)))
        w("    %-11s %s" % (anc, " | ".join(parts)))
    # deployability
    qs = [q for q in d.judged if q in d.diff and q in d.plur]
    rho_dep = rj.spearman([d.diff[q] for q in qs], [d.plur[q] for q in qs]) if len(qs) > 10 else float("nan")
    qs2 = [q for q in d.judged if q in d.diff and q in d.diff_out]
    rho_inst = rj.spearman([d.diff[q] for q in qs2], [d.diff_out[q] for q in qs2]) if len(qs2) > 10 else float("nan")
    w(""); w("--- instrument ---")
    w("  Spearman(difficulty, key-free plurality agreement of the roster's predicted letters) over %d judged questions: %+.3f (the deployable proxy candidate)" % (len(qs), rho_dep))
    w("  Spearman(primary instrument %d-model roster, secondary instrument %d outside models) over %d questions: %+.3f" % (len(d.roster), len(d.outside), len(qs2), rho_inst))
    w("  OPTIONS-key join fidelity on the judged questions: 1:1 %d | multi %d | none %d | gt_answer == mmlu_pro.answer on %d" % d.join_fidelity)
    # criteria
    w(""); w("--- registered criteria (scored on %s; the other arms are the replication) ---" % PRIMARY_ARM)
    pa = basic[(PRIMARY_ARM, "CONTRAST", "accA")]; pt = basic[(PRIMARY_ARM, "CONTRAST", "tie_dec")]
    c1 = pa["ci"][1] < 0
    w("  C1 accuracy A hard - easy (pooled over anchors) %+.1fpp [%+.1f, %+.1f]: %s (criterion: the interval excludes 0 on the negative side)"
      % (100 * pa["diff"], 100 * pa["ci"][0], 100 * pa["ci"][1], "HELD" if c1 else "FAILED"))
    c2 = pt["ci"][0] > 0
    w("  C2 tie rate hard - easy (key-decidable, pooled) %+.1fpp [%+.1f, %+.1f]: %s (criterion: the interval excludes 0 on the positive side)"
      % (100 * pt["diff"], 100 * pt["ci"][0], 100 * pt["ci"][1], "HELD" if c2 else "FAILED"))
    z = basic.get((PRIMARY_ARM, "CONTRAST", "beta_len"))
    c3 = z is not None and z >= 1.96
    w("  C3 beta_len larger on hard than easy: z %s: %s (criterion: z >= 1.96)" % ("n/a" if z is None else "%+.2f" % z, "HELD" if c3 else "FAILED"))
    below, nanc, medj, medk = basic[(PRIMARY_ARM, "ORDER", "summary")]
    c4 = below >= 7
    w("  C4 easy-vs-hard order below the within-cell permutation null in %d of %d anchors (median rho judge %+.3f, key %+.3f): %s (criterion: >= 7 of 14)"
      % (below, nanc, medj, medk, "HELD" if c4 else "FAILED"))
    supported = [t for t in TERCILES if res_tot[t][2] >= 20]
    rates = {t: (res_tot[t][4] / res_tot[t][2] if res_tot[t][2] else float("nan")) for t in TERCILES}
    w("  C5 residue wrong-direction rate (%s vs every opponent, Law + Philosophy, on pairs the key gives to it) per tercile: %s"
      % (RESIDUE_MODEL[:14], " | ".join("%s %s (n %d)" % (t, fmt(rates[t]), res_tot[t][2]) for t in TERCILES)))
    if len(supported) < 2:
        c5 = False
        w("     UNDETERMINED (support): fewer than two terciles carry >= 20 such pairs (criterion: hardest supported - easiest supported >= 10pp)")
    else:
        te, th = supported[0], supported[-1]
        c5 = rates[th] - rates[te] >= 0.10
        w("     hardest supported (%s) - easiest supported (%s) = %+.1fpp: %s (criterion: >= 10pp; the residue is a harder-stratum effect)"
          % (th, te, 100 * (rates[th] - rates[te]), "HELD" if c5 else "FAILED"))
    replication = []
    for arm in ARMS:
        if arm == PRIMARY_ARM:
            continue
        pa2 = basic[(arm, "CONTRAST", "accA")]; b2 = basic[(arm, "ORDER", "summary")]
        replication.append("%s: accA diff %+.1fpp [%+.1f, %+.1f], order below null %d/%d" % (arm, 100 * pa2["diff"], 100 * pa2["ci"][0], 100 * pa2["ci"][1], b2[0], b2[1]))
    w("  replication arms: " + " | ".join(replication))
    w("  FALSIFIER (per-cell boards are difficulty-invariant): %s" % ("NOT TRIGGERED" if (c1 or c4) else "TRIGGERED - neither the accuracy contrast nor the order shift survives"))
    w("  elapsed %.0f s" % (time.time() - t0))
    if selftest:
        return L, basic
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(out_path[:-4] + "_rows.csv", "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in rows_csv for k in r})
        wr = csv.DictWriter(f, fieldnames=cols); wr.writeheader()
        for r in rows_csv:
            wr.writerow(r)
    log("written %s (+ _rows.csv)" % out_path)
    return L, basic


# ── selftest on synthetic rows (no cache of record is read) ─────────────────────────────────────────────────

def selftest():
    print("[SELFTEST] mm_fit_np vs rj.mm_fit on random aggregates")
    rng = random.Random(1)
    for trial in range(5):
        models = ["m%d" % i for i in range(rng.randint(4, 12))]
        agg = {}
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if rng.random() < 0.8:
                    n = rng.randint(1, 30); agg[(a, b)] = (rng.uniform(0, n), float(n))
        t1 = rj.mm_fit(agg, models); t2 = mm_fit_np(agg, models)
        err = max(abs(t1[m] - t2[m]) for m in models)
        assert err < 1e-8, "mm_fit_np deviates from rj.mm_fit by %g" % err
        print("  trial %d: %d models, %d pairs, max |delta theta| %.2e OK" % (trial, len(models), len(agg), err))
    print("[SELFTEST] synthetic Data with a planted difficulty effect")

    class Fake:
        pass
    d = Fake()
    models = ["A", "B", "C", "D", "E", "F"]; skill = {m: 1.5 - 0.6 * i for i, m in enumerate(models)}
    d.anchors = ["Alpha", "Beta"]; d.leaves = []; d.cells = {}; d.tercile = {}; d.K = defaultdict(dict); d.L = {}; d.P = defaultdict(dict)
    d.diff = {}; d.diff_out = {}; d.plur = {}; d.judged = []; d.roster = models; d.outside = []; d.join_fidelity = (0, 0, 0, 0)
    d.leaf_qualifies = lambda l: False
    d.anchor_of_leaf = {}
    rows = []; mid = 0
    for ci, c in enumerate(d.anchors):
        qs = list(range(1000 * (ci + 1), 1000 * (ci + 1) + 150)); d.cells[c] = qs; d.judged += qs
        for q in qs:
            diff = rng.random(); d.diff[q] = diff; d.diff_out[q] = diff; d.plur[q] = diff
            for m in models:
                d.K[q][m] = int(rng.random() < 0.3 + 0.6 * diff * (skill[m] > 0)); d.L[(q, m)] = rng.randint(200, 3000); d.P[q][m] = "A"
            for _ in range(4):
                a, b = rng.sample(models, 2)
                pa = 1 / (1 + math.exp(-(skill[a] - skill[b]) * (0.5 + diff)))
                r = rng.random()
                if diff < 0.33 and r < 0.35:
                    w = "TIE"
                else:
                    w = a if rng.random() < pa else b
                inv = int(rng.random() < 0.01)
                rows.append((mid, a, b, q, "INVALID" if inv else w, inv, int(rng.random() < 0.5 + 0.4 * diff))); mid += 1
        order = sorted(qs, key=lambda q: (d.diff[q], q)); n = len(order); b1, b2 = n // 3, (2 * n) // 3
        for i, q in enumerate(order):
            d.tercile[(c, q)] = "easy" if i >= b2 else ("mid" if i >= b1 else "hard")
    d.arms = {arm: rows for arm in ARMS}
    d.contestants = models
    d.rows = lambda arm, cell, terc=None: [r for r in d.arms[arm] if r[3] in set(d.cells[cell]) and (terc is None or d.tercile[(cell, r[3])] == terc)]
    def decidable(r):
        ka, kb = d.K[r[3]].get(r[1]), d.K[r[3]].get(r[2]); return ka is not None and kb is not None and ka != kb
    d.decidable = decidable
    global RESIDUE, RESIDUE_MODEL, RESIDUE_ANCHORS
    saved = (RESIDUE, RESIDUE_MODEL, RESIDUE_ANCHORS); RESIDUE = [("Alpha", "A", "F"), ("Beta", "B", "E")]; RESIDUE_MODEL = "B"; RESIDUE_ANCHORS = ["Alpha", "Beta"]
    try:
        L, basic = readout(B=20, nperm=10, out_path=None, d=d, log=lambda s: None, selftest=True)
    finally:
        RESIDUE, RESIDUE_MODEL, RESIDUE_ANCHORS = saved
    print("\n".join(L[-14:]))
    print("[SELFTEST] OK: %d lines produced on synthetic rows (planted: ties on the hard tercile, key noisier on hard); nothing written" % len(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--run", action="store_true"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--boot", type=int, default=300, help="question-resampling draws per stratum board (the record's B)")
    ap.add_argument("--perm", type=int, default=200, help="within-cell permutations of the tercile labels for the order null")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    if a.selftest:
        selftest(); return
    if a.dry_run:
        dry_run(); return
    if not a.run:
        raise SystemExit("TOPIC-DIFFICULTY: the readout runs only with --run (registration first; --dry-run and --selftest post nothing and write nothing)")
    if os.path.exists(a.out):
        raise SystemExit("TOPIC-DIFFICULTY: %s exists; the outcome of record is written once (pass --out for a re-analysis file)" % a.out)
    readout(a.boot, a.perm, a.out)


if __name__ == "__main__":
    main()
