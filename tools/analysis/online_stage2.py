"""online_stage2.py: ONLINE-STAGE2 (zero calls; CPU readout; certified-split leg NOT included) -- leave one union member out and
stream its items past the other five members' cells with FROZEN means; an item is buffered iff its max-cos to the five-member cells
is below a threshold calibrated on GATE for a 0.80 catch rate (nested leave-one-out over the in-members); the buffer cells are
refit from scratch every 100 buffered items; each held-out EVAL item is filed AT ARRIVAL (prequential) over the five-member cells
plus the buffer cells of the last rebuild, and compared with the batch AF-U on the same items (OS1); the catch rate per held-out
member decides OS2. A per-source k-means arm runs the same procedure. ZERO calls: no judge, no LLM, no embedding call, no
construction, no Gradle. Readers only (every DB mode=ro, through online_replay_lomo's loaders).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — ONLINE-STAGE2: with FROZEN leaf means, an OOS-only
  buffer whose threshold is calibrated on GATE ..." SECTION SPAN L24054-L24068 (_as_of 56093589, parent e18fe595): OS1, OS2, Support
  (a)-(g), P1-P4, F-OS. Results record docs/agents/results/ONLINE-STAGE2.json. --run REFUSES unless a LINE of the programme starts
  with the registered heading (REG_RE, line-anchored).

INSTRUMENT (imported unchanged; LF git blob asserted BEFORE import, another blob REFUSES):
  tools/analysis/online_replay_lomo.py blob:fb3a956369ad2e921b61202d4d9ff460c53eab03 (ORL; it asserts union_af_route.py
      bf3f17db and g13_breakdown.py c29fa1c3 before importing them). Used: ORL.load_parts (the inputs manifest 53021e26..., every
      pinned AF-U / inputs file re-hashed, the bundle, the GATE items by the side export, every vector by rp12_pairing's reader,
      [ORL-VEC]); ORL.build_world (the identities: flatLeaf 256-d = af_cells on EVAL, eval_fl, P_fl 0.7346 / 0.7265 symmetric,
      K_0 labels = k_cells_s0, P(US_0) 0.7368 / 0.7289; the C-1 init; the policy); ORL.replay (stage 1, recomputed as the reference
      and identity-checked); ORL.ol1_of (OL1's TOST form, one place: point +/- 1.645 SE strictly inside +/-0.020, DIFFERENT iff
      |D| > 0.020 AND point +/- 1.96 SE excludes 0); ORL._model (policy lookup); ORL.ORDER_SEED (20261003); GB.ukm_fit (seed 0),
      GB.majority, GB.stat (whole-component bootstrap, B 2,000, seed 20260929), GB.pool_check_v2 (B0-2 pv2 pool check).

LAUNCH SEQUENCE (the run-operator; zero calls; never beside a construction or site null (rule 7): every mode except --selftest /
--mutants is a pool reader):
  python tools/analysis/online_stage2.py --selftest
  python tools/analysis/online_stage2.py --mutants
  python tools/analysis/online_stage2.py --dry-run     # POOL line first; pins; denominators; identities; GATE calibration per
                                                       #   replay and arm (tau_m, per-j shares); writes nothing; no EVAL statistic
  python tools/analysis/online_stage2.py --run         # the outcome of record, WRITE-ONCE (mode "x"):
       experiment_results/online_stage2/outcome.txt and online_stage2_items.csv (never committed: sha256 + backup to E: with
       SHA256SUMS.txt)
  --data-root <dir>: the root under which experiment_results/ and the DBs are read and the outputs written (default: the checkout
  holding this file); applied inside this process before the readers import.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, nothing written):
  (1) POOL line; write-once paths absent (refused before any read); B0-2 pool check pv2_1575de61bb20e977 (rc != 0 REFUSES); the
      registered heading present.
  (2) ORL.load_parts + ORL.build_world (all of ORL's identities; [ORL-*] refusals).
  (3) STAGE-1 IDENTITY ([OS-STAGE1] otherwise): stage 1's pooled D recomputed by ORL.replay (init mean) equals the recorded
      -0.0386 (tree) / -0.0687 (k-means) "%+.4f" (ONLINE-REPLAY-LOMO outcome, POSTRUN_online_replay_lomo.md VALID).
  (4) six replays x two arms: calibration, stream, INTEGRITY ([OS-INTEGRITY]: any nonzero in-member churn = INVALID, refused);
      OS1, OS2, F-OS, P1-P4, descriptive lines; outcome + items CSV written mode "x".

READINGS (stated for the READY to confirm or refuse; none chosen silently):
  OS-R1 Calibration (step 1). For held-out m and each in-member j != m: j's GATE items scored by max-cos to the unit cells of the
        other in-members (sources minus {m, j}; four on the real data; the one-cell IFEVAL cell is a cell like any other).
        share_j(t) = #{score < t} / n_j (strict). Candidates t = the observed calibration scores (union over the j); tau_m = the
        SMALLEST candidate with median_j share_j(t) >= 0.80 (numpy median; five j: the middle one). The set {t : median >= 0.80}
        is open at its infimum (strict <), so "the smallest threshold" is read as the smallest observed score attaining it (the
        order-statistic convention of OB.threshold / OL-R2). No candidate attains it -> [OS-CAL] REFUSED. Per arm (OL-R2's
        per-arm thresholds): the k-means arm calibrates on its own K_0 cells.
  OS-R2 Stream (step 2). The five in-members' cells keep their unit means for ever (no update; the arrays are compared before /
        after: INTEGRITY). Order = stage 1's (ORL.ORDER_SEED, fresh per replay: permutation of m's TRAIN, then of m's EVAL). An item
        is BUFFERED iff max-cos to the five-member cells < tau_m (strict; equality files). A non-buffered TRAIN item is filed by
        flatLeaf over the five-member cells (the cells the trigger read) and counts for OL-R5 naming only; buffer cells are named
        only at a rebuild.
  OS-R3 Rebuilds. When the buffer count reaches a multiple of 100 (after appending the arriving item), the buffer cells are refit
        from scratch on ALL buffered items so far (TRAIN and EVAL: transduction, disclosed) by GB.ukm_fit(seed 0, k = min(L_m,
        buffer size)); names = TRAIN majority of the buffered TRAIN items each fit label assigns (tie: the smaller class name; none
        -> <empty>, never correct); purity = share of buffered items whose label equals their buffer cell's name. Before the first
        rebuild there are no buffer cells.
  OS-R4 Filing (step 3), PREQUENTIAL: each EVAL item of m is filed WHEN IT ARRIVES (before the buffer decision about it, so before
        it can enter the buffer or trigger a rebuild): argmax cos over the five-member cells (current OL-R5 names) plus the buffer
        cells of the last rebuild. Names of existing cells change only on TRAIN absorption (OL-R5: an absorbed class strictly above
        the batch majority count renames; incumbent keeps a tie); TRAIN streams first, so every EVAL item sees the final names.
  OS-R5 OS1: D item-paired against ORL's DECIDING batch arm (C-2 symmetric: flatLeaf over all six members' cells; 0.7265 / 0.7289),
        pooled over the 6 replays (each EVAL item held out once; checked); TOST form = ORL.ol1_of on GB.stat (SE = bootstrap SD).
  OS-R6 OS2: catch_m = buffered / streamed over m's TRAIN + EVAL; the median over the six members = numpy median (mean of the
        middle two); CALIBRATED iff median >= 0.70, else UNDER-CATCH. Per-member binomial SE printed beside (no SE is claimed for
        the median: Support (g)).
  OS-R7 INTEGRITY: churn = in-member EVAL items whose flatLeaf cell over the five-member cells differs between before the stream
        and after it, computed on the arrays the stream used; nonzero in any replay / arm, or a changed array -> [OS-INTEGRITY]
        REFUSED (the run is INVALID; nothing written).
  OS-R8 Descriptive: false buffering = share of the in-members' own EVAL items with max-cos to the five-member cells < tau_m (P3 =
        its median over the six replays, numpy); end-of-stream (transductive) filing = one refit on all buffered items at the end
        (k = min(L_m, buffer size), seed 0) and the final names; all-cells churn and decision churn (ORL._model, UNION-AF-ROUTE's
        frozen TRAIN policy; absent -> NOT COMPUTED) against the five-member cells plus the last rebuild's buffer cells; D over the
        five split members (IFEVAL out); stage 1's D (ORL.replay) beside, with no attribution (two changes at once).
  OS-R9 Predictions: numeric bands HELD iff the point lies in the closed interval; OS1 probabilities by Brier over the four named
        outcomes (NEITHER 0.45, LOSS 0.35, EQUIVALENT 0.20, GAIN 0.00); OS2 CALIBRATED 0.60 by Brier over the two named outcomes
        (CALIBRATED 0.60, UNDER-CATCH 0.40 implied), stage 1's one-term form printed beside.
  Not applicable (stated): no judge verdict enters (declared-class keyed): no wrong(established), no tie convention A / B, no call
  cache, no --pilot / truncation guard.

SELFTEST / MUTANTS: see the block above MUTANTS (cases, fixtures with known answers, the mutant table).
"""
import os
import sys


def _preparse_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _preparse_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import io            # noqa: E402
import re            # noqa: E402
import shutil        # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import tempfile; import scratch_dir      # noqa: E402
import contextlib    # noqa: E402
from collections import Counter, defaultdict  # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[OS2]"
TEST_ID = "ONLINE-STAGE2"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


ORL_PIN = ("online_replay_lomo.py", "fb3a956369ad2e921b61202d4d9ff460c53eab03")
if blob_lf(os.path.join(HERE, ORL_PIN[0])) != ORL_PIN[1]:
    refuse("%s is blob:%s, not the pinned blob:%s" % (ORL_PIN[0], blob_lf(os.path.join(HERE, ORL_PIN[0])), ORL_PIN[1]))
import online_replay_lomo as ORL  # noqa: E402  (asserts union_af_route bf3f17db and g13_breakdown c29fa1c3 before importing them)
UA, GB = ORL.UA, ORL.GB

POOL = ORL.POOL
OUT_REL = "experiment_results/online_stage2"
OUTCOME, ITEMS_CSV = "outcome.txt", "online_stage2_items.csv"
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = ("## Registered 2026-10-03 (before any code or call) — ONLINE-STAGE2: with FROZEN leaf means, an OOS-only buffer "
               "whose threshold is calibrated on GATE")
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — ONLINE-STAGE2: with FROZEN leaf '
            'means, ..." L24054-L24068 (_as_of 56093589, parent e18fe595)')
TARGET = 0.80
OS2_BAR = 0.70
REBUILD = 100
BUF_SEED = 0
MARGIN = 0.020
Z90, Z95 = ORL.Z90, ORL.Z95
EMPTY = -1
ARMS = ("tree", "km")
ARM_NAME = {"tree": "AF-U tree", "km": "per-source k-means K_0"}

# Registered Support (planning numbers, printed beside the measured)
SUPPORT = dict(n=6139, comp=5628, deff=1.263, n_eff=4861, se=0.00641, disc=0.20, tost_reach=0.0041, diff_reach=0.0254, os2_mde=0.03)
PRED_P1 = (-0.015, -0.035, 0.005)
PROB_OS1 = {"NEITHER": 0.45, "LOSS": 0.35, "EQUIVALENT": 0.20, "GAIN": 0.00}
PRED_P2 = (0.75, 0.55, 0.88)
PROB_OS2 = {"CALIBRATED": 0.60, "UNDER-CATCH": 0.40}
PRED_P3 = (0.30, 0.15, 0.50)
PRED_P4 = (-0.020, -0.045, 0.005)

# registered / recorded constants of THIS test (the selftest swaps in its fixture's); ORL's own constants stay in ORL._REG
REG2 = dict(id_s1_tree="-0.0386", id_s1_km="-0.0687", n_replays=6)
_REG2 = [REG2]


def reg2():
    return _REG2[0]


HIT = Counter()


def hit(name):
    HIT[name] += 1


def P(rel):
    return os.path.join(UA._ROOT[0], *rel.split("/"))


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ── calibration (step 1) ─────────────────────────────────────────────────────────────────────────────────────────────────

def cal_tau(score_lists, target=TARGET):
    """OS-R1: the smallest observed score t with median_j #{s_j < t} / n_j >= target -> (t, [share_j(t)])."""
    srt = [np.sort(np.asarray(s, dtype=np.float64)) for s in score_lists]
    if not srt or any(len(s) == 0 for s in srt):
        hit("REFUSE.CAL")
        refuse("[OS-CAL] an in-member holds no GATE item: no catch rate to calibrate")
    cand = np.unique(np.concatenate(srt))
    shares = np.vstack([np.searchsorted(s, cand, side="left") / float(len(s)) for s in srt])   # j x candidates, strict <
    med = np.median(shares, axis=0)
    ok = np.flatnonzero(med >= target)
    if len(ok) == 0:
        hit("REFUSE.CAL")
        refuse("[OS-CAL] no observed GATE score attains a median catch rate >= %.2f (max %.4f)" % (target, float(med.max())))
    k = int(ok[0])
    return float(cand[k]), [float(x) for x in shares[:, k]]


def calibrate(W, arm, m):
    A = W["arms"][arm]
    inm = [s for s in W["sources"] if s != m]
    lists, rows = [], []
    for j in inm:
        other = (A["src"] != m) & (A["src"] != j)
        g = W["gsrc"] == j
        sc = (W["Xg"][g] @ A["mu"][other].T).max(axis=1) if g.any() else np.zeros(0)
        lists.append(sc)
        rows.append((j, int(g.sum()), int(other.sum())))
    tau, shares = cal_tau(lists)
    return dict(tau=tau, per=[(j, n, nc, sh) for (j, n, nc), sh in zip(rows, shares)],
                med=float(np.median(shares)))


# ── one replay (steps 2-3) ───────────────────────────────────────────────────────────────────────────────────────────────

def _fit_buffer(W, buf, Lm, classes):
    kb = min(Lm, len(buf))
    Xb = np.vstack([W["Xt"][i] if sd == "T" else W["Xe"][i] for sd, i in buf])
    fit, _t = GB.ukm_fit(Xb, kb, BUF_SEED)
    Cb, blab = np.asarray(fit["centers"], dtype=np.float64), np.asarray(fit["labels"], dtype=int)
    tmask = np.array([sd == "T" for sd, _i in buf])
    ybuf = np.array([int(W["yt"][i]) if sd == "T" else int(W["ye"][i]) for sd, i in buf])
    bnames = np.array([GB.majority(ybuf[tmask & (blab == j)], classes) for j in range(kb)], dtype=int)
    purity = float(np.mean(bnames[blab] == ybuf))
    return Cb, bnames, dict(size=len(buf), k=kb, purity=purity, n_train=int(tmask.sum()), n_eval=int((~tmask).sum()))


def stream(W, arm, m, tau):
    A = W["arms"][arm]
    classes = W["classes"]
    keep = np.flatnonzero(A["src"] != m)
    ids = [A["ids"][j] for j in keep]
    U = A["mu"][keep].copy()                                   # FROZEN unit means (never written below)
    U_ref = U.copy()
    names = A["name"][keep].copy()
    cdom = A["cdom"][keep]
    ein, eout = np.flatnonzero(W["esrc"] != m), np.flatnonzero(W["esrc"] == m)
    tout = np.flatnonzero(W["tsrc"] == m)
    before = np.argmax(W["Xe"][ein] @ U.T, axis=1)
    rng = np.random.default_rng(ORL.ORDER_SEED)
    order = [("T", int(i)) for i in rng.permutation(tout)] + [("E", int(i)) for i in rng.permutation(eout)]
    Lm = int(W["ksrc"][m])
    epos = {int(i): k for k, i in enumerate(eout)}
    online_ok = np.zeros(len(eout), dtype=np.int64)
    fm = [""] * len(eout)
    buffered = []
    maxcos = []
    absorbed = defaultdict(Counter)
    buf, rebuilds, filed, renamed = [], [], 0, set()
    Cb, bnames = np.zeros((0, U.shape[1])), np.zeros(0, dtype=int)
    bids = []
    for side, i in order:
        x = W["Xt"][i] if side == "T" else W["Xe"][i]
        s = U @ x
        if side == "E":                                        # PREQUENTIAL: filed at arrival, before the buffer decision
            sc = np.concatenate([s, Cb @ x])
            a = int(np.argmax(sc))
            nm = names[a] if a < len(U) else bnames[a - len(U)]
            online_ok[epos[i]] = int(nm == W["ye"][i])
            fm[epos[i]] = ids[a] if a < len(U) else bids[a - len(U)]
        j1 = int(np.argmax(s))
        top1 = float(s[j1])
        maxcos.append(top1)
        if top1 < tau:
            buf.append((side, i))
            buffered.append(1)
            if len(buf) % REBUILD == 0:
                Cb, bnames, info = _fit_buffer(W, buf, Lm, classes)
                bids = ["BUF:%s:%s:r%03d:%03d" % (arm, m, len(rebuilds) + 1, j) for j in range(len(Cb))]
                rebuilds.append(info)
            continue
        buffered.append(0)
        filed += 1
        if side == "T":
            cnt = absorbed[j1]
            cnt[int(W["yt"][i])] += 1
            top = max(cnt.values())
            cbest = min((k for k, v in cnt.items() if v == top), key=lambda k: classes[k])
            if top > cdom[j1]:
                if names[j1] != cbest:
                    renamed.add(j1)
                names[j1] = cbest
    after = np.argmax(W["Xe"][ein] @ U.T, axis=1)
    churn = (after != before).astype(np.int64)
    moved = not np.array_equal(U, U_ref)
    # descriptive: end-of-stream (transductive) filing; all-cells churn and decision churn against the last rebuild's cells
    if buf:
        Ce, be, einfo = _fit_buffer(W, buf, Lm, classes)
    else:
        Ce, be, einfo = np.zeros((0, U.shape[1])), np.zeros(0, dtype=int), None
    allE = np.vstack([U, Ce])
    nE = np.concatenate([names, be]).astype(int)
    eos_ok = (nE[np.argmax(W["Xe"][eout] @ allE.T, axis=1)] == W["ye"][eout]).astype(np.int64)
    allL = np.vstack([U, Cb])
    after_all = np.argmax(W["Xe"][ein] @ allL.T, axis=1)
    churn_all = (after_all != before).astype(np.int64)
    lids = ids + bids
    if A.get("policy") is not None:
        dch = np.array([int(ORL._model(A, ids[b]) != ORL._model(A, lids[a])) for b, a in zip(before.tolist(), after_all.tolist())],
                       dtype=np.int64)
    else:
        dch = None
    fb = float(np.mean((W["Xe"][ein] @ U.T).max(axis=1) < tau)) if len(ein) else float("nan")
    n_tr = len(tout)
    bt = np.asarray(buffered, dtype=np.int64)
    return dict(m=m, arm=arm, ids=ids, tau=tau, ein=ein, eout=eout, order=order, n_train=n_tr, n_stream=len(order), n_buf=len(buf),
                buf_train=int(bt[:n_tr].sum()), buf_eval=int(bt[n_tr:].sum()), catch=len(buf) / max(len(order), 1), filed=filed,
                renamed=len(renamed), rebuilds=rebuilds, eos_info=einfo, Lm=Lm, online_ok=online_ok, fm=fm, eos_ok=eos_ok,
                churn=churn, moved=moved, churn_all=churn_all, dch=dch, false_buf=fb, buffered=bt, maxcos=np.asarray(maxcos))


_STREAM = [stream]


def integrity(reps):
    bad = [(r["arm"], r["m"], int(r["churn"].sum()), r["moved"]) for r in reps if r["moved"] or int(r["churn"].sum()) != 0]
    if bad:
        hit("REFUSE.INTEGRITY")
        refuse("[OS-INTEGRITY] in-member churn is not 0 (%s): the run is INVALID (frozen means were not frozen); nothing written"
               % "; ".join("%s -%s churn %d moved %s" % b for b in bad))


# ── the readout ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def os2_word(catches, bar=OS2_BAR):
    return "CALIBRATED" if float(np.median(np.asarray(catches, dtype=np.float64))) >= bar else "UNDER-CATCH"


def f_os(os1):
    return os1 == "LOSS"


def in_band(x, lo, hi):
    return lo <= x <= hi


def brier(probs, outcome):
    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items()))


def stage1_identity(W, say):
    got = {}
    for arm in ARMS:
        diff = np.zeros(len(W["ye"]), dtype=np.float64)
        for m in W["sources"]:
            r = ORL.replay(W, arm, m)
            diff[r["eout"]] = r["online_ok"] - W["batch"][arm][r["eout"]]
        got[arm] = diff
    s_t, s_k = "%+.4f" % got["tree"].mean(), "%+.4f" % got["km"].mean()
    if s_t != reg2()["id_s1_tree"] or s_k != reg2()["id_s1_km"]:
        hit("REFUSE.STAGE1")
        refuse("[OS-STAGE1] stage 1 recomputed by ORL.replay: D tree %s / k-means %s, not the recorded %s / %s" % (
            s_t, s_k, reg2()["id_s1_tree"], reg2()["id_s1_km"]))
    say("IDENTITY (stage 1, ORL.replay init mean): pooled D tree %s, k-means %s = the recorded %s / %s (ONLINE-REPLAY-LOMO VALID)" % (
        s_t, s_k, reg2()["id_s1_tree"], reg2()["id_s1_km"]))
    return got


def compute(W, s1):
    R = dict(arms={}, n=len(W["ye"]), G=len(set(W["ecomp"].tolist())))
    allreps = []
    for arm in ARMS:
        cals = {m: calibrate(W, arm, m) for m in W["sources"]}
        reps = {m: _STREAM[0](W, arm, m, cals[m]["tau"]) for m in W["sources"]}
        allreps.extend(reps.values())
        diff = np.zeros(len(W["ye"]), dtype=np.float64)
        deos = np.zeros(len(W["ye"]), dtype=np.float64)
        online = np.full(len(W["ye"]), -1, dtype=np.int64)
        seen = np.zeros(len(W["ye"]), dtype=np.int64)
        for m, r in reps.items():
            diff[r["eout"]] = r["online_ok"] - W["batch"][arm][r["eout"]]
            deos[r["eout"]] = r["eos_ok"] - W["batch"][arm][r["eout"]]
            online[r["eout"]] = r["online_ok"]
            seen[r["eout"]] += 1
        if not np.all(seen == 1):
            refuse("%d EVAL item(s) were not held out exactly once" % int(np.sum(seen != 1)))
        st = GB.stat(diff, W["ecomp"])
        split = ~np.isin(W["esrc"], list(W["single"]))
        st_split = GB.stat(diff[split], W["ecomp"][split]) if split.any() and not split.all() else None
        per = {}
        for m, r in reps.items():
            per[m] = dict(d=GB.stat(diff[r["eout"]], W["ecomp"][r["eout"]]), p_on=float(r["online_ok"].mean()),
                          p_b=float(W["batch"][arm][r["eout"]].mean()), d_eos=float(deos[r["eout"]].mean()),
                          d_s1=float(s1[arm][r["eout"]].mean()), churn_all=float(r["churn_all"].mean()),
                          dch=float(r["dch"].mean()) if r["dch"] is not None else None)
        catches = [reps[m]["catch"] for m in W["sources"]]
        R["arms"][arm] = dict(cals=cals, reps=reps, per=per, diff=diff, st=st, ol1=ORL.ol1_of(st), st_split=st_split,
                              p_on=float(online.mean()), p_b=float(W["batch"][arm].mean()), st_eos=GB.stat(deos, W["ecomp"]),
                              d_s1=float(s1[arm].mean()), catches=catches, med_catch=float(np.median(catches)),
                              os2=os2_word(catches), fb_med=float(np.median([reps[m]["false_buf"] for m in W["sources"]])))
    integrity(allreps)
    R["tmk"] = GB.stat(R["arms"]["tree"]["diff"] - R["arms"]["km"]["diff"], W["ecomp"])
    return R


def fs(st):
    return ORL.fs(st)


def os1_lines(a, deciding):
    st = a["st"]
    d, se = st["d"], st["se"]
    L = ["  D = P_fl(ONLINE-S2, prequential) %.4f - P_fl(BATCH) %.4f = %+.4f; TOST 90%% [%+.4f, %+.4f], 95%% [%+.4f, %+.4f] (point +/- z"
         " SE, SE %.5f); percentile 95%% [%+.4f, %+.4f] (beside)" % (a["p_on"], a["p_b"], d, d - Z90 * se, d + Z90 * se, d - Z95 * se,
                                                                  d + Z95 * se, se, st["lo"], st["hi"]),
         "  " + fs(st)]
    w = a["ol1"]
    tag = "OS1" if deciding else "OS1-form (k-means arm, DESCRIPTIVE)"
    if w == "EQUIVALENT":
        hit("OS1.EQUIVALENT")
        L.append("%s: EQUIVALENT: the 90%% interval [%+.4f, %+.4f] lies inside +/-%.3f (within %.3f of the batch rebuild, never"
                 " 'equal'; transductive, see DISCLOSURE)" % (tag, d - Z90 * se, d + Z90 * se, MARGIN, MARGIN))
    elif w == "LOSS":
        hit("OS1.LOSS")
        L.append("%s: DIFFERENT (LOSS): |D| %.4f > %.3f and the 95%% interval [%+.4f, %+.4f] lies below 0: online filing of the"
                 " held-out member falls below the batch rebuild" % (tag, abs(d), MARGIN, d - Z95 * se, d + Z95 * se))
    elif w == "GAIN":
        hit("OS1.GAIN")
        L.append("%s: DIFFERENT (GAIN): |D| %.4f > %.3f and the 95%% interval [%+.4f, %+.4f] lies above 0: online filing of the"
                 " held-out member exceeds the batch rebuild" % (tag, abs(d), MARGIN, d - Z95 * se, d + Z95 * se))
    else:
        hit("OS1.NEITHER")
        L.append("%s: NEITHER: the 90%% interval [%+.4f, %+.4f] is not inside +/-%.3f and DIFFERENT does not hold (|D| %.4f, 95%%"
                 " [%+.4f, %+.4f]); reads 'not shown'" % (tag, d - Z90 * se, d + Z90 * se, MARGIN, abs(d), d - Z95 * se, d + Z95 * se))
    if a["st_split"] is not None:
        hit("OS1.SPLIT_ONLY")
        L.append("  BESIDE (DESCRIPTIVE): D over the split members' replays only (one-cell IFEVAL out): %s" % fs(a["st_split"]))
    L.append("  BESIDE (DESCRIPTIVE): end-of-stream (fully transductive) filing D %s" % fs(a["st_eos"]))
    L.append("  BESIDE (DESCRIPTIVE, reference): stage 1 (mean refit + stage 1's trigger; ORL.replay) D %+.4f; stage 2 minus stage 1"
             " %+.4f (two changes at once: no difference is attributed to one of them)" % (a["d_s1"], d - a["d_s1"]))
    return L


def support_lines(a):
    st = a["st"]
    se = st["se"]
    return ["SUPPORT (OS1, measured beside registered): n %d (registered %d), components %d (registered %d), mean cluster size %.3f;"
            " SE %.5f (registered %.5f at discordance %.2f); DEFF %.3f (registered %.3f, measured on OL1); n_eff %.0f (registered %d);"
            " discordance %.4f; MDE80 %.4f" % (st["n"], SUPPORT["n"], st["G"], SUPPORT["comp"], st["n"] / st["G"], se, SUPPORT["se"],
                                               SUPPORT["disc"], st["deff"], SUPPORT["deff"], st["n_eff"], SUPPORT["n_eff"], st["disc"],
                                               st["mde"]),
            "  reach at the measured SE: TOST |D_true| < %.4f (0.020 - 2.487 SE; registered %.4f); DIFFERENT |D_true| >= %.4f"
            " (0.020 + 0.842 SE; registered %.4f)" % (MARGIN - 2.487 * se, SUPPORT["tost_reach"], MARGIN + 0.842 * se,
                                                      SUPPORT["diff_reach"]),
            "  VERDICT LINE (registered (f)): OS1 is DESCRIPTIVE-ONLY at the prediction (-0.015 lies in the NEITHER zone); the"
            " classification above is read as registered"]


def os2_lines(W, a, deciding):
    L = []
    for m in W["sources"]:
        r, c = a["reps"][m], a["cals"][m]
        se = (r["catch"] * (1 - r["catch"]) / max(r["n_stream"], 1)) ** 0.5
        L.append("  -%s: catch %.4f = %d of %d streamed buffered (TRAIN %d of %d, EVAL %d of %d; binomial SE %.4f) at tau_m %.5f" % (
            m, r["catch"], r["n_buf"], r["n_stream"], r["buf_train"], r["n_train"], r["buf_eval"], r["n_stream"] - r["n_train"], se,
            r["tau"]))
    med = a["med_catch"]
    tag = "OS2" if deciding else "OS2-form (k-means arm, DESCRIPTIVE)"
    if a["os2"] == "CALIBRATED":
        hit("OS2.CALIBRATED")
        L.append("%s: CALIBRATED: the median over the %d held-out members' catch rates %.4f >= %.2f (target %.2f minus 0.10)" % (
            tag, len(W["sources"]), med, OS2_BAR, TARGET))
    else:
        hit("OS2.UNDER")
        L.append("%s: UNDER-CATCH: the median over the %d held-out members' catch rates %.4f < %.2f (target %.2f minus 0.10); it"
                 " limits the GATE calibration's transport to new domains and does not fire F-OS" % (
                     tag, len(W["sources"]), med, OS2_BAR, TARGET))
    if deciding:
        L.append("  SUPPORT (OS2): distance |median - 0.70| %.4f (registered MDE80 about %.2f); no sampling SE is claimed for the"
                 " median: six sources, not a sampled population of domains (Support (g))" % (abs(med - OS2_BAR), SUPPORT["os2_mde"]))
    return L


def falsifier_lines(R):
    T = R["arms"]["tree"]
    if f_os(T["ol1"]):
        hit("FOS.FIRES")
        L = ["F-OS FIRES: OS1 reads DIFFERENT (LOSS), D %+.4f: even with frozen means, a GATE-calibrated OOS buffer and periodic"
             " buffer rebuilds, online filing of a new member falls more than 2pp below a batch rebuild; memo v3's online-evolution"
             " design (L84-L87) is not filing-neutral; the online claim narrows to 'stable ids at a filing cost; rebuild"
             " periodically'" % T["st"]["d"]]
    else:
        hit("FOS.NOT_FIRED")
        L = ["F-OS NOT FIRED: OS1 reads %s (F-OS fires only on DIFFERENT (LOSS))" % T["ol1"]]
    if T["os2"] == "UNDER-CATCH":
        hit("FOS.UNDER_NOTE")
        L.append("  OS2 UNDER-CATCH does not fire F-OS (registered): it limits the GATE calibration's transport to new domains")
    return L


def pred_lines(W, R):
    T, K = R["arms"]["tree"], R["arms"]["km"]
    L = []
    d = T["st"]["d"]
    if in_band(d, PRED_P1[1], PRED_P1[2]):
        hit("P1.HELD")
        L.append("PREDICTION P1 D %+.3f [%+.3f, %+.3f]: observed %+.4f -> HELD" % (PRED_P1 + (d,)))
    else:
        hit("P1.FAILED")
        L.append("PREDICTION P1 D %+.3f [%+.3f, %+.3f]: observed %+.4f -> FAILED" % (PRED_P1 + (d,)))
    L.append("PREDICTION P1 OS1 probabilities (NEITHER 0.45, LOSS 0.35, EQUIVALENT 0.20, GAIN 0.00): observed %s; Brier %.4f" % (
        T["ol1"], brier(PROB_OS1, T["ol1"])))
    med = T["med_catch"]
    if in_band(med, PRED_P2[1], PRED_P2[2]):
        hit("P2.HELD")
        L.append("PREDICTION P2 OS2 median catch rate %.2f [%.2f, %.2f]: observed %.4f -> HELD" % (PRED_P2 + (med,)))
    else:
        hit("P2.FAILED")
        L.append("PREDICTION P2 OS2 median catch rate %.2f [%.2f, %.2f]: observed %.4f -> FAILED" % (PRED_P2 + (med,)))
    ev = 1.0 if T["os2"] == "CALIBRATED" else 0.0
    L.append("PREDICTION P2 CALIBRATED 0.60: observed %s; Brier %.4f (two named outcomes; stage 1's one-term form %.4f beside)" % (
        T["os2"], brier(PROB_OS2, T["os2"]), (PROB_OS2["CALIBRATED"] - ev) ** 2))
    fb = T["fb_med"]
    if in_band(fb, PRED_P3[1], PRED_P3[2]):
        hit("P3.HELD")
        L.append("PREDICTION P3 in-members' false-buffer share at tau_m, median over replays, %.2f [%.2f, %.2f] (descriptive):"
                 " observed %.4f -> HELD" % (PRED_P3 + (fb,)))
    else:
        hit("P3.FAILED")
        L.append("PREDICTION P3 in-members' false-buffer share at tau_m, median over replays, %.2f [%.2f, %.2f] (descriptive):"
                 " observed %.4f -> FAILED" % (PRED_P3 + (fb,)))
    dk = K["st"]["d"]
    if in_band(dk, PRED_P4[1], PRED_P4[2]):
        hit("P4.HELD")
        L.append("PREDICTION P4 k-means arm D %+.3f [%+.3f, %+.3f] (descriptive): observed %+.4f -> HELD" % (PRED_P4 + (dk,)))
    else:
        hit("P4.FAILED")
        L.append("PREDICTION P4 k-means arm D %+.3f [%+.3f, %+.3f] (descriptive): observed %+.4f -> FAILED" % (PRED_P4 + (dk,)))
    return L


def replay_lines(W, R, arm):
    a = R["arms"][arm]
    L = []
    for m in W["sources"]:
        r, p, c = a["reps"][m], a["per"][m], a["cals"][m]
        rb = r["rebuilds"]
        rbs = ", ".join("%d:%.3f" % (x["size"], x["purity"]) for x in rb) if rb else "none"
        dc = ("decision churn %.4f" % p["dch"]) if p["dch"] is not None else "decision churn NOT COMPUTED (policy absent)"
        L.append("  -%s (%s): calibration %s -> tau_m %.5f (median share %.4f); streamed %d (TRAIN %d, EVAL %d); buffered %d (catch"
                 " %.4f); filed %d; renamed cells %d; rebuilds %d (k %s; size:purity %s); P_fl online %.4f vs batch %.4f, D_m %s;"
                 " end-of-stream D_m %+.4f; stage 1 D_m %+.4f; in-member false-buffer share %.4f; all-cells churn %.4f; %s" % (
                     m, ARM_NAME[arm], "; ".join("j=%s GATE %d vs %d cells share %.4f" % (j, n, nc, sh) for j, n, nc, sh in c["per"]),
                     c["tau"], c["med"], r["n_stream"], r["n_train"], r["n_stream"] - r["n_train"], r["n_buf"], r["catch"], r["filed"],
                     r["renamed"], len(rb), "min(L_m %d, size)" % r["Lm"], rbs, p["p_on"], p["p_b"], fs(p["d"]), p["d_eos"], p["d_s1"],
                     r["false_buf"], p["churn_all"], dc))
    return L


def outcome_lines(W, R, pre):
    T, K = R["arms"]["tree"], R["arms"]["km"]
    L = list(pre)
    say = L.append
    say("")
    say("=== %s: OS1, OS2, F-OS, P1-P4 (%s) ===" % (TEST_ID, REG_TEXT))
    say("DENOMINATOR (OS1): the held-out members' EVAL items pooled over %d replays = %d items in %d CK-CLOSE components (each held"
        " out once; registered %d / %d)" % (len(W["sources"]), R["n"], R["G"], SUPPORT["n"], SUPPORT["comp"]))
    say("DENOMINATOR (OS2): streamed items (TRAIN + EVAL) per held-out member %s; the median is over %d members" % (
        ", ".join("-%s %d" % (m, T["reps"][m]["n_stream"]) for m in W["sources"]), len(W["sources"])))
    say("LIKE WITH LIKE: | ONLINE-S2 tree | five frozen AF-U trees + buffer k-means | TRAIN-majority naming only | BATCH AF-U | six"
        " AF-U trees (flatLeaf over all cells, C-2) | naming only | ONLINE-S2 k-means | five frozen per-source K_0 + buffer k-means |"
        " naming only | BATCH k-means | six per-source K_0 | naming only | stage 1 (reference) | five AF-U + mean refit + buffer |"
        " naming only |; online-vs-batch is the same cell type on both sides; tree-vs-k-means and stage-2-vs-stage-1 are DESCRIPTIVE")
    say("DISCLOSURE (TRANSDUCTION, registered): filing is PREQUENTIAL: each held-out EVAL item is filed when it arrives, before it"
        " can enter the buffer, but earlier EVAL items shape the buffer cells later EVAL items see; the batch rebuild never sees"
        " EVAL. The buffer's k = min(L_m, buffer size) uses the held-out member's batch leaf count L_m (an ORACLE k; it favours the"
        " online arm). The end-of-stream filing is fully transductive and DESCRIPTIVE")
    say("DISCLOSURE (Support (g), stated before data): the nested calibration scores each in-member against FOUR members' cells"
        " while the stream faces FIVE, so the realised catch rate is expected below the 0.80 target")
    say("DISCLOSURE (ORL D-5 residual): 15 TRAIN / 14 EVAL MATH / MMLU_PRO_LB text-shared multi-class items left the bundle but"
        " stayed in the MMLU_PRO_LB tree's fit")
    say("INTEGRITY (not a criterion; cannot fail by design): in-member churn over the five frozen cells before vs after = 0 in all"
        " %d replays x %d arms (%s); frozen arrays unchanged" % (len(W["sources"]), len(ARMS), ", ".join(
            "%s -%s 0/%d" % (arm, m, len(R["arms"][arm]["reps"][m]["ein"])) for arm in ARMS for m in W["sources"])))
    say("NOT APPLICABLE: no judge verdict (declared-class keyed): no wrong(established), no tie convention A / B; zero calls")
    say("")
    say("--- OS1 (DECIDING; the interval decides; OL1's TOST form, margin 0.020) ---")
    L.extend(os1_lines(T, True))
    L.extend(support_lines(T))
    say("--- OS2 (DECIDING; the point decides: median catch rate over the held-out members >= 0.70) ---")
    L.extend(os2_lines(W, T, True))
    say("--- F-OS ---")
    L.extend(falsifier_lines(R))
    say("--- PREDICTIONS ---")
    L.extend(pred_lines(W, R))
    say("--- DESCRIPTIVE: the k-means arm (same procedure from K_0, own calibration) ---")
    L.extend(os1_lines(K, False))
    L.extend(os2_lines(W, K, False))
    say("  tree-minus-k-means paired (D_tree - D_K, per item): %s (DESCRIPTIVE; not tree-over-k-means superiority)" % fs(R["tmk"]))
    say("--- DESCRIPTIVE: per replay ---")
    for arm in ARMS:
        L.extend(replay_lines(W, R, arm))
    say("WILL NOT SHOW (registered): any certified new split (leg excluded; waits on CERT-PC-K2-KNOWN); real traffic or drift;"
        " tree-over-k-means superiority; which of the two changes from stage 1 caused any difference; stable ids for buffer cells;"
        " anything beyond these six sources and one draw")
    return L


def items_text(W, R):
    rows = ["item_id,replay,arm,side,stream_pos,maxcos_five,buffered,cell_at_arrival,online_ok,batch_ok,eos_ok"]
    for arm in ARMS:
        a = R["arms"][arm]
        for m in W["sources"]:
            r = a["reps"][m]
            ek = {int(i): k for k, i in enumerate(r["eout"])}
            for pos, (sd, i) in enumerate(r["order"]):
                if sd == "T":
                    rows.append("%s,%s,%s,TRAIN,%d,%.6f,%d,,,," % (W["titems"][i], m, arm, pos, r["maxcos"][pos], r["buffered"][pos]))
                else:
                    k = ek[i]
                    rows.append("%s,%s,%s,EVAL,%d,%.6f,%d,%s,%d,%d,%d" % (W["eitems"][i], m, arm, pos, r["maxcos"][pos], r["buffered"][pos],
                                                                        r["fm"][k], r["online_ok"][k], W["batch"][arm][i], r["eos_ok"][k]))
    return "\n".join(rows) + "\n"


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

_LOAD = [ORL.load_parts]
_POOL = [GB.pool_check_v2]
_PROG = [PROGRAMME]


def header(say, mode):
    say("POOL %s (%s; %s; the first line of every mode)" % (POOL, TEST_ID, mode))
    say("%s | registration %s" % (TEST_ID, REG_TEXT))
    me = os.path.abspath(__file__)
    with open(me, "rb") as f:
        raw = f.read()
    say("  script %s blob:%s sha256-lf16:%s (LF rendering of record)%s" % (
        os.path.basename(me), blob_lf(me), hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16],
        "; working tree CRLF sha256-crlf16:%s" % hashlib.sha256(raw).hexdigest()[:16] if b"\r\n" in raw else "; working tree LF"))
    say("  imported %s blob:%s (pinned, asserted before import); through it %s" % (
        ORL_PIN[0], ORL_PIN[1], ", ".join("%s blob:%s" % p for p in ORL.PINS)))
    say("  data root %s; threads OMP/OPENBLAS/MKL = 1; zero calls; DBs mode=ro (ORL's readers)" % UA._ROOT[0])
    say("  registered constants: catch-rate target %.2f, OS2 bar %.2f, rebuild every %d buffered items, buffer seed %d, order seed %d,"
        " margin %.3f" % (TARGET, OS2_BAR, REBUILD, BUF_SEED, ORL.ORDER_SEED, MARGIN))


def pool_line(say):
    rc, msg = _POOL[0](POOL)
    say("POOL CHECK (B0-2, replaces pool_guard for pv2 pools): rc %d | %s" % (rc, msg))
    if rc != 0:
        hit("REFUSE.POOL")
        refuse("the B0-2 pool check failed: %s" % msg)


def denominators(say):
    say("DENOMINATORS (registered): OS1 %d held-out EVAL items in %d components pooled over %d replays (DEFF %.3f measured on OL1,"
        " n_eff %d, SE %.5f at discordance %.2f); OS2 the median over %d held-out members' catch rates (1,000-5,000 streamed items"
        " each)" % (SUPPORT["n"], SUPPORT["comp"], reg2()["n_replays"], SUPPORT["deff"], SUPPORT["n_eff"], SUPPORT["se"],
                    SUPPORT["disc"], reg2()["n_replays"]))


def out_paths(out_dir=None):
    d = out_dir or P(OUT_REL)
    return os.path.join(d, OUTCOME), os.path.join(d, ITEMS_CSV)


def dry_run(out=print, out_dir=None):
    say = out
    header(say, "--dry-run")
    pool_line(say)
    denominators(say)
    prog = _PROG[0]
    found = bool(REG_RE.search(open(prog, encoding="utf-8").read())) if prog and os.path.isfile(prog) else False
    say("REGISTRATION heading %s in %s" % ("FOUND" if found else "NOT FOUND (--run would refuse)", prog))
    po, pc = out_paths(out_dir)
    say("OUTPUTS (write-once, mode x): %s %s; %s %s" % (po, "EXISTS (--run would refuse)" if os.path.exists(po) else "absent",
                                                        pc, "EXISTS (--run would refuse)" if os.path.exists(pc) else "absent"))
    W = ORL.build_world(_LOAD[0](say), say)
    say("CELLS: tree %d; k-means %d; per-source k %s" % (len(W["arms"]["tree"]["ids"]), len(W["arms"]["km"]["ids"]),
                                                         ", ".join("%s %d" % (s, W["ksrc"][s]) for s in W["sources"])))
    for s in W["sources"]:
        say("  source %-12s EVAL %d (components %d), TRAIN %d, GATE %d; streamed if held out %d" % (
            s, int((W["esrc"] == s).sum()), len(set(W["ecomp"][W["esrc"] == s].tolist())), int((W["tsrc"] == s).sum()),
            int((W["gsrc"] == s).sum()), int((W["tsrc"] == s).sum() + (W["esrc"] == s).sum())))
    say("CALIBRATION (GATE only; nested leave-one-out; no EVAL statistic, no catch rate of a held-out member):")
    for arm in ARMS:
        for m in W["sources"]:
            c = calibrate(W, arm, m)
            say("  %s -%s: tau_m %.5f (median share %.4f >= %.2f); %s" % (
                ARM_NAME[arm], m, c["tau"], c["med"], TARGET,
                "; ".join("j=%s GATE %d vs %d cells share %.4f" % (j, n, nc, sh) for j, n, nc, sh in c["per"])))
    say("DRY-RUN: nothing written; no OS1 / OS2 statistic computed or printed; the stage-1 identity is checked by --run.")
    hit("DRY.DONE")
    return 0


def run(out=print, out_dir=None):
    pre = []

    def say(s_):
        pre.append(s_)
        out(s_)
    header(say, "--run")
    po, pc = out_paths(out_dir)
    for p in (po, pc):
        if os.path.exists(p):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    pool_line(say)
    prog = _PROG[0]
    if not (prog and os.path.isfile(prog) and REG_RE.search(open(prog, encoding="utf-8").read())):
        hit("REFUSE.REG")
        refuse("no line of %s starts with the registered heading %r" % (prog, REG_HEADING[:80]))
    say("REGISTRATION heading FOUND (line-anchored) in %s" % prog)
    denominators(say)
    W = ORL.build_world(_LOAD[0](say), say)
    s1 = stage1_identity(W, say)
    R = compute(W, s1)
    L = outcome_lines(W, R, pre[:])
    os.makedirs(os.path.dirname(po), exist_ok=True)
    with open(po, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(pc, "x", encoding="utf-8", newline="\n") as f:
        f.write(items_text(W, R))
    for ln in L[len(pre):]:
        out(ln)
    out("WROTE (write-once) %s sha256 %s; %s sha256 %s (never committed: pin + backup)" % (po, sha256_bytes(po), pc, sha256_bytes(pc)))
    hit("RUN.DONE")
    return R


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.mutants:
        return run_mutants()
    if a.data_root and os.path.abspath(a.data_root) != os.path.abspath(UA._ROOT[0]):
        refuse("--data-root %s was not applied before the readers imported (UA root %s)" % (a.data_root, UA._ROOT[0]))
    if a.dry_run:
        return dry_run(out)
    run(out)
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
# SELFTEST (--selftest; the real run() / dry_run() executed with the loader hook swapped for a synthetic world built by
# _fx(); ORL.build_world, calibrate(), stream(), compute(), every verdict and print branch real). Fixtures (dim 10; sources AA
# (2 leaves), BB (2), CC (one-cell), DD (1 leaf); counts = base x scale):
#   allbuf15  GATE items sit at cos ~0.41 to every cell, held-out items on their own axes: every streamed item is buffered
#             (catch 1.0000 per member), every member's TRAIN >= 100, so the first rebuild precedes every EVAL item and the
#             buffer k-means recovers the classes: KNOWN ANSWER D +0.0000, OS1 EQUIVALENT, OS2 CALIBRATED, F-OS NOT FIRED,
#             P1 HELD (0 in [-0.035, +0.005]), P2 FAILED (1.0000 > 0.88), P3 FAILED (false buffering 0.0000).
#   allbuf13  the same at scale 13: DD has 91 TRAIN items, so DD's first 100 - 91 = 9 EVAL items arrive before the first rebuild
#             and are filed over the five-member cells (wrong); the 10th triggers the rebuild AFTER being filed: KNOWN ANSWER
#             D = -9 / 416 = -0.0216 in both arms, OS1 DIFFERENT (LOSS), F-OS FIRES (the prequential discriminator).
#   tight     GATE items near their own axes (noise 0.02): tau_m small, held-out items mostly filed: OS2 UNDER-CATCH, the
#             UNDER-CATCH note under F-OS NOT FIRED; values = the oracle's.
#   absorb / rename  BB/c next to AA/b (absorption into existing cells; rename: AA:n2's batch count 3, so absorbed BB/c TRAIN
#             renames it); every tau, per-j share, catch, buffer count, rebuild count, D_m, end-of-stream D, false-buffer share
#             and pooled D equal an INDEPENDENT plain-loop oracle (_oracle).
# Cases: branches (cal_tau by value: strict share, median, smallest candidate, refusal; os2_word / f_os / Brier / print
# branches at the boundaries on synthetic R); toy_stream (hand world: 99 TRAIN + 10 EVAL -> P_fl 0.9000 exactly; 100 TRAIN ->
# 1.0000; tau equality files); e2e_* (above); integrity (a tampered stream -> [OS-INTEGRITY], nothing written); stage1
# (tampered recorded D -> [OS-STAGE1]); write_once / race / refusals (second --run, existing CSV before the pool check, missing
# heading, pool rc 1 with the POOL line first); dry_run (POOL first, denominators, tau = calibrate()'s, no OS1 / OS2 / catch text,
# nothing written); branch_cover (every registered print branch and refusal hit). Added after the first mutant pass: toy_stream
# OL-R5 tie (3 absorbed = batch count 3 keeps the incumbent; 4 renames) and TRAIN-only buffer naming (40 TRAIN ZZ/c + 70 EVAL ZZ/d:
# purity 0.4000, 0 correct); e2e_stiff (tilted tree leaf: tree != k-means; the deciding OS1 / OS2 / P1 / P2 blocks print the TREE
# arm, the k-means block and tree-minus-k-means position-checked); e2e_wide (noisy items: false-buffer shares differ by replay,
# P3 = the median); e2e_se (pooled stat stubbed to SE |D| / 1.5 with a narrow percentile interval: OS1 NEITHER at the SD).
# MUTANTS (--mutants; each edits the instrument above this selftest block in memory and re-runs the selftest), 2026-10-03:
# first pass 47 of 58 KILLED (S04 / S05 / S06 / S14 / S18 / R06 / R07 BAD: patterns also matched the selftest oracle, so the
# search scope was cut at this block and the compute() patterns made unique; S09 TRAIN-only naming, S10 tie renaming, R16 P3
# median, R17 SD vs percentile SURVIVED -> toy naming / tie cases, e2e_wide, e2e_se added); second pass 58 of 58 KILLED, control
# survived. Classes: calibration C01-C11 (strict share, median vs mean / min / max, smallest candidate, target, wrong
# population x3, wrong split side, refusal); stream S01-S19 (strict trigger, frozen means (integrity), prequential filing,
# rebuild period x3 and from-scratch, buffer k, TRAIN-only naming, tie / disabled / EVAL renaming, order, seed, trigger cells,
# filing cells, argmin, end-of-stream deciding, end-of-stream refit); readout R01-R28 (OS2 median / strict / bar, catch
# denominator x2, batch arm x2, pooled first-replay-only, F-OS on GAIN / NEITHER / omitted, deciding block arm swap x2, band,
# Brier, P3 median, SD vs percentile, integrity skipped / churn ignored, write-once x2, pool rc, stage-1 identity x2, heading,
# false-buffer population, UNDER-CATCH note, P2 arm).
# NOT RUN at build: the real --dry-run (and any file-level check on the pinned inputs): GEMMA-OWN-BAR's java null (-DgobArm)
# was running (rule 7: no pool reader beside a construction or site null); the run-operator runs --dry-run first.

FX_SOURCES = ("AA", "BB", "CC", "DD")


def _unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def _fx(variant="allbuf", scale=15, seed=5):
    rng = np.random.default_rng(seed)
    dim = 10
    E = np.eye(dim)
    ax = {"AA/a": E[0], "AA/b": E[1], "BB/c": E[2], "BB/d": E[3], "CC/x": E[4], "DD/y": E[5]}
    if variant in ("absorb", "rename", "stiff"):
        ax["BB/c"] = _unit(E[2] * 0.35 + E[1] * 0.94)
    classes = sorted(ax)
    noise = 0.30 if variant == "wide" else 0.08
    ntr = {"AA/a": 14, "AA/b": 12, "BB/c": 10, "BB/d": 9, "CC/x": 8, "DD/y": 7}
    nev = {"AA/a": 7, "AA/b": 6, "BB/c": 6, "BB/d": 5, "CC/x": 4, "DD/y": 4}
    ngt = {"AA/a": 6, "AA/b": 6, "BB/c": 5, "BB/d": 5, "CC/x": 5, "DD/y": 5}
    allv = _unit(E[:6].sum(axis=0))

    def gate_vec(cls):
        if variant.startswith("allbuf") or variant == "wide":
            return _unit(allv + 0.02 * rng.standard_normal(dim))
        if variant == "tight":
            return _unit(ax[cls] + 0.02 * rng.standard_normal(dim))
        return _unit(ax[cls] + noise * rng.standard_normal(dim))
    Xt, yt, Xe, ye, Xg, yg, titems, eitems, ecomp = [], [], [], [], [], [], [], [], []
    comp = 0
    for cls in classes:
        for _ in range(ntr[cls] * scale):
            Xt.append(_unit(ax[cls] + noise * rng.standard_normal(dim)))
            yt.append(classes.index(cls))
            titems.append("t%05d" % len(titems))
        for k in range(nev[cls] * scale):
            Xe.append(_unit(ax[cls] + noise * rng.standard_normal(dim)))
            ye.append(classes.index(cls))
            eitems.append("e%05d" % len(eitems))
            ecomp.append(comp)
            if k % 3 != 1:
                comp += 1
        comp += 1
        for _ in range(ngt[cls]):
            Xg.append(gate_vec(cls))
            yg.append(classes.index(cls))
    Xt, Xe = np.vstack(Xt), np.vstack(Xe)
    yt, ye = np.array(yt), np.array(ye)
    leaves, leaf_dom = {}, {}
    nid = {"AA/a": "AA:n1", "AA/b": "AA:n2", "BB/c": "BB:n1", "BB/d": "BB:n2", "DD/y": "DD:n1"}
    for cls, u in nid.items():
        msk = yt == classes.index(cls)
        s = Xt[msk].sum(axis=0)
        leaves[u] = (s / np.linalg.norm(s), int(msk.sum()) + 2)
        leaf_dom[u] = (cls, int(msk.sum()))
    leaf_dom["CC:n0"] = ("CC/x", ntr["CC/x"] * scale)
    if variant == "rename":
        leaf_dom["AA:n2"] = ("AA/b", 3)
    if variant == "stiff":                                      # the tree's AA/b leaf tilted: tree and k-means arms differ
        leaves["AA:n2"] = (_unit(leaves["AA:n2"][0] - 0.35 * E[0] + 0.3 * E[2]), leaves["AA:n2"][1])
    single = {"CC": "CC:n0"}
    ksrc = {"AA": 2, "BB": 2, "CC": 1, "DD": 1}
    ids = sorted(leaves)
    M = np.vstack([leaves[u][0] for u in ids])
    cells_af = {}
    for i, it in enumerate(eitems):
        cells_af[it] = "CC:n0" if classes[ye[i]].startswith("CC") else ids[int(np.argmax(Xe[i] @ M.T))]
    for j, it in enumerate(titems):
        cells_af[it] = "CC:n0" if classes[yt[j]].startswith("CC") else ids[int(np.argmax(Xt[j] @ M.T))]
    name = {u: leaf_dom[u][0] for u in list(ids) + ["CC:n0"]}
    efl = np.array([int(name[cells_af[it]] == classes[ye[i]]) for i, it in enumerate(eitems)])
    parts = dict(classes=classes, Xt=Xt, yt=yt, titems=titems, Xe=Xe, ye=ye, eitems=eitems, ecomp=np.array(ecomp), efl=efl,
                 leaves=leaves, leaf_dom=leaf_dom, single=single, ksrc=ksrc, cells_af=cells_af, k0_cells=None,
                 Xg=np.vstack(Xg), yg=np.array(yg), policy=None)
    tsrc = np.array([ORL.src_of(classes[i]) for i in yt])
    C, csrc, cloc, lab, fits = UA.us_fit(ORL.FM.unit_rows(Xt), tsrc, ksrc, FX_SOURCES, ORL.KM_SEED)
    parts["k0_cells"] = {it: "K%d:%s:%03d" % (ORL.KM_SEED, csrc[lab[j]], cloc[lab[j]]) for j, it in enumerate(titems)}
    if variant != "tight":                                      # tight: the absent-policy path
        parts["policy"] = dict(best_single="M0", tree_cell={u: ("M1" if k % 2 else "M2") for k, u in enumerate(list(ids) + ["CC:n0"])},
                               xtree_cell={"K0": {"K0:%s:%03d" % (csrc[g], cloc[g]): ("M1" if g % 2 else "M3") for g in range(len(C))}})
    reg_fx = dict(ORL.REG, sources=FX_SOURCES, members=(), dim=dim, n_eval=len(ye), n_comp=len(set(ecomp)), n_train=len(yt),
                  ksrc=ksrc, id_p_fl="%.4f" % efl.mean())
    # mirrored k-means and symmetric batch identity strings, computed by ORL's selftest oracles (plain loops)
    kok = []
    for i in range(len(ye)):
        so = ORL.src_of(classes[ye[i]])
        cand = [h for h in range(len(C)) if (csrc[h] == so if so in single else csrc[h] not in single)]
        g = max(cand, key=lambda h: float(np.dot(_unit(Xe[i]), C[h])))
        ys = [int(yt[j]) for j in range(len(yt)) if lab[j] == g]
        kok.append(int(GB.majority(ys, classes) == ye[i]))
    reg_fx["id_p_k0"] = "%.4f" % np.mean(kok)
    reg_fx["id_p_fl_all"] = "%.4f" % np.mean(list(ORL._oracle_batch(parts, "tree", reg_fx).values()))
    reg_fx["id_p_k0_all"] = "%.4f" % np.mean(list(ORL._oracle_batch(parts, "km", reg_fx).values()))
    saved = ORL._REG[0]
    ORL._REG[0] = reg_fx
    try:
        W = ORL.build_world(parts, lambda s: None)
    finally:
        ORL._REG[0] = saved
    s1 = {}
    for arm in ARMS:
        diff = np.zeros(len(ye))
        for m in FX_SOURCES:
            r = ORL.replay(W, arm, m)
            diff[r["eout"]] = r["online_ok"] - W["batch"][arm][r["eout"]]
        s1[arm] = "%+.4f" % diff.mean()
    reg2_fx = dict(REG2, id_s1_tree=s1["tree"], id_s1_km=s1["km"], n_replays=len(FX_SOURCES))
    return parts, reg_fx, reg2_fx


_FX_CACHE = {}


def _fxc(variant, scale=15):
    k = (variant, scale)
    if k not in _FX_CACHE:
        _FX_CACHE[k] = _fx(variant, scale)
    return _FX_CACHE[k]


@contextlib.contextmanager
def _swapped(parts, reg_fx, reg2_fx, pool=None, prog=None):
    saved = (_LOAD[0], _POOL[0], _PROG[0], ORL._REG[0], _REG2[0])
    _LOAD[0] = lambda say: parts
    _POOL[0] = pool or (lambda p: (0, "fixture pool check OK"))
    _PROG[0] = prog
    ORL._REG[0] = reg_fx
    _REG2[0] = reg2_fx
    try:
        yield
    finally:
        _LOAD[0], _POOL[0], _PROG[0], ORL._REG[0], _REG2[0] = saved


def _fx_prog(tmp, with_heading=True):
    p = os.path.join(tmp, "prog.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("preamble\n" + (REG_HEADING + " ... (fixture)\n" if with_heading else "## Registered other\n") + "tail\n")
    return p


def _capture(fn, *a, **k):
    buf = []
    r = fn(*a, out=buf.append, **k)
    return "\n".join(buf), r


def _need(text, *needles):
    for nd in needles:
        if nd not in text:
            raise AssertionError("missing %r" % nd)


def _world(parts, reg_fx):
    saved = ORL._REG[0]
    ORL._REG[0] = reg_fx
    try:
        return ORL.build_world(parts, lambda s: None)
    finally:
        ORL._REG[0] = saved


def _oracle(parts, arm, m, reg_fx):
    """Independent plain-loop implementation of the registered calibration, stream, rebuilds and filing (lists and dot products;
    shared only: ORL._oracle_cells (ORL's own selftest oracle for the batch cells), GB.ukm_fit and GB.majority (the registered
    buffer instrument))."""
    classes = parts["classes"]
    Xt = [_unit(v) for v in parts["Xt"]]
    Xe = [_unit(v) for v in parts["Xe"]]
    Xg = [_unit(v) for v in parts["Xg"]]
    yt, ye, yg = list(parts["yt"]), list(parts["ye"]), list(parts["yg"])
    S = lambda c: ORL.src_of(classes[c])    # noqa: E731
    cells = ORL._oracle_cells(parts, arm, reg_fx, "unit")
    srcs = list(reg_fx["sources"])
    inm = [s for s in srcs if s != m]
    assert len(inm) % 2 == 1
    lists = []
    for j in inm:
        oth = [_unit(cl[2]) for cl in cells if cl[1] not in (m, j)]
        lists.append([max(float(np.dot(x, c)) for c in oth) for x, y in zip(Xg, yg) if S(y) == j])
    cand = sorted(set(v for l_ in lists for v in l_))
    tau, shares = None, None
    for t in cand:
        sh = [sum(1 for v in l_ if v < t) / len(l_) for l_ in lists]
        if sorted(sh)[len(sh) // 2] >= TARGET:
            tau, shares = t, sh
            break
    five = [[cl[0], _unit(cl[2]), cl[4], cl[5]] for cl in cells if cl[1] != m]
    eout = [i for i in range(len(ye)) if S(ye[i]) == m]
    ein = [i for i in range(len(ye)) if S(ye[i]) != m]
    tout = [j for j in range(len(yt)) if S(yt[j]) == m]
    rng = np.random.default_rng(ORL.ORDER_SEED)
    order = [("T", int(j)) for j in rng.permutation(np.array(tout, dtype=int))] + \
            [("E", int(i)) for i in rng.permutation(np.array(eout, dtype=int))]
    L = int(reg_fx["ksrc"][m])
    absorbed = [Counter() for _ in five]
    buf, bc, nreb, ok = [], [], 0, {}

    def refit(items):
        Xb = np.vstack([Xt[i] if sd == "T" else Xe[i] for sd, i in items])
        fit, _t = GB.ukm_fit(Xb, min(L, len(items)), BUF_SEED)
        out_ = []
        for g in range(min(L, len(items))):
            ys = [yt[i] for (sd, i), lb in zip(items, fit["labels"]) if sd == "T" and lb == g]
            out_.append((np.array(fit["centers"][g]), GB.majority(ys, classes)))
        return out_
    for sd, i in order:
        x = Xt[i] if sd == "T" else Xe[i]
        sc = [float(np.dot(x, c[1])) for c in five]
        if sd == "E":
            allc = [(c[1], c[2]) for c in five] + bc
            s2 = [float(np.dot(x, c)) for c, _n in allc]
            ok[i] = int(allc[s2.index(max(s2))][1] == ye[i])
        j = sc.index(max(sc))
        if sc[j] < tau:
            buf.append((sd, i))
            if len(buf) % REBUILD == 0:
                bc = refit(buf)
                nreb += 1
            continue
        if sd == "T":
            absorbed[j][yt[i]] += 1
            top = max(absorbed[j].values())
            cb = sorted([k for k, v in absorbed[j].items() if v == top], key=lambda k: classes[k])[0]
            if top > five[j][3]:
                five[j][2] = cb
    eos = {}
    ec = refit(buf) if buf else []
    for i in eout:
        allc = [(c[1], c[2]) for c in five] + ec
        s2 = [float(np.dot(Xe[i], c)) for c, _n in allc]
        eos[i] = int(allc[s2.index(max(s2))][1] == ye[i])
    fb = sum(1 for i in ein if max(float(np.dot(Xe[i], c[1])) for c in five) < tau) / len(ein)
    return dict(tau=tau, shares=shares, ok=ok, eos=eos, n_buf=len(buf), catch=len(buf) / len(order), nreb=nreb, fb=fb,
                n_stream=len(order))


def _run_fx(tmp, variant, scale=15):
    parts, reg_fx, reg2_fx = _fxc(variant, scale)
    out_dir = os.path.join(tmp, "out_%s_%d" % (variant, scale))
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        txt, R = _capture(run, out_dir=out_dir)
    W = _world(parts, reg_fx)
    return parts, reg_fx, txt, R, W, out_dir


def _check_oracle(parts, reg_fx, txt, R, W):
    for arm in ARMS:
        a = R["arms"][arm]
        diff = np.zeros(len(W["ye"]))
        deos = np.zeros(len(W["ye"]))
        catches, fbs = [], []
        for m in FX_SOURCES:
            o = _oracle(parts, arm, m, reg_fx)
            r, c = a["reps"][m], a["cals"][m]
            assert abs(o["tau"] - c["tau"]) < 1e-12, (arm, m, o["tau"], c["tau"])
            assert all(abs(x - y) < 1e-12 for x, y in zip(o["shares"], [p[3] for p in c["per"]])), (arm, m, "shares")
            assert o["n_buf"] == r["n_buf"] and o["nreb"] == len(r["rebuilds"]), (arm, m, o["n_buf"], r["n_buf"], o["nreb"])
            assert abs(o["fb"] - r["false_buf"]) < 1e-12, (arm, m, "false buffer")
            for i, v in o["ok"].items():
                diff[i] = v - int(W["batch"][arm][i])
            for i, v in o["eos"].items():
                deos[i] = v - int(W["batch"][arm][i])
            catches.append(o["catch"])
            fbs.append(o["fb"])
            dm = float(np.mean([diff[i] for i in o["ok"]]))
            _need(txt, "  -%s (%s): calibration" % (m, ARM_NAME[arm]), "-> tau_m %.5f" % o["tau"],
                  "buffered %d (catch %.4f); filed" % (o["n_buf"], o["catch"]), "rebuilds %d (k" % o["nreb"],
                  "in-member false-buffer share %.4f" % o["fb"])
            assert abs(dm - a["per"][m]["d"]["d"]) < 1e-12, (arm, m, dm)
            assert abs(float(np.mean([deos[i] for i in o["eos"]])) - a["per"][m]["d_eos"]) < 1e-12, (arm, m, "eos")
            if arm == "tree":
                _need(txt, "  -%s: catch %.4f = %d of %d streamed buffered" % (m, o["catch"], o["n_buf"], o["n_stream"]))
        d = float(diff.mean())
        assert abs(d - a["st"]["d"]) < 1e-12, (arm, d, a["st"]["d"])
        assert abs(float(deos.mean()) - a["st_eos"]["d"]) < 1e-12, (arm, "eos pooled")
        med = float(np.median(catches))
        assert abs(med - a["med_catch"]) < 1e-12
        assert a["os2"] == ("CALIBRATED" if med >= OS2_BAR else "UNDER-CATCH")
        assert abs(float(np.median(fbs)) - a["fb_med"]) < 1e-12
        assert a["ol1"] == ORL.ol1_word(a["st"]["d"], a["st"]["se"]), (arm, a["ol1"])
        if arm == "tree":
            _need(txt, "= %+.4f; TOST 90%%" % d, "catch rates %.4f" % med)
    return True


def st_branches():
    # cal_tau by value (OS-R1)
    j1 = [x / 10 for x in range(1, 11)]
    tau, sh = cal_tau([j1, j1, [0.5] * 10])
    assert tau == 0.9 and sh == [0.8, 0.8, 1.0], (tau, sh)                 # strict <: at 0.8 only 7 of 10 lie below
    tau, sh = cal_tau([j1, [0.95] * 10, [0.05] * 10])                       # median of (share1, 0/1, 1) = share1 until 0.95
    assert tau == 0.9 and sh == [0.8, 0.0, 1.0], (tau, sh)
    tau, sh = cal_tau([[0.1, 0.2, 0.3, 0.4, 0.5]] * 3, target=0.80)
    assert tau == 0.5 and sh == [0.8, 0.8, 0.8], (tau, sh)
    tau, sh = cal_tau([[0.1, 0.2, 0.3, 0.4, 0.5], [0.6] * 5, [0.7] * 5, [0.01] * 5, [0.02] * 5])   # five j, median = 3rd
    assert tau == 0.5 and sh == [0.8, 0.0, 0.0, 1.0, 1.0], (tau, sh)    # mean 0.56 would not attain 0.80 here
    tau, sh = cal_tau([[0.3, 0.1, 0.2, 0.5, 0.4], [0.31, 0.11, 0.21, 0.51, 0.41], [0.9] * 5])
    assert tau == 0.5 and sh == [0.8, 0.8, 0.0], (tau, sh)                  # the largest-share j does not decide (median)
    for bad in ([[0.5] * 4, [0.5] * 4, [0.5] * 4], [[0.1, 0.2], []]):
        try:
            cal_tau(bad)
            raise AssertionError("cal_tau did not refuse %r" % (bad,))
        except SystemExit as e:
            assert "[OS-CAL]" in str(e)
    # OS2 / F-OS / Brier
    assert os2_word([0.70, 0.70, 0.70]) == "CALIBRATED" and os2_word([0.6999, 0.7, 0.6999]) == "UNDER-CATCH"
    assert os2_word([0.1, 0.65, 0.75, 1.0]) == "CALIBRATED"                 # numpy median of four = mean of the middle two 0.70
    assert os2_word([0.1, 0.64, 0.75, 1.0]) == "UNDER-CATCH"
    assert os2_word([0.0, 0.0, 0.0, 0.9, 0.9, 0.9]) == "UNDER-CATCH"        # mean 0.45; median 0.45
    assert os2_word([0.69, 0.69, 0.69, 0.69, 1.0, 1.0]) == "UNDER-CATCH"   # mean 0.79 would read CALIBRATED
    assert os2_word([0.0, 0.71, 0.71, 0.71, 0.71, 0.71]) == "CALIBRATED"   # mean 0.59 would read UNDER-CATCH
    assert f_os("LOSS") is True and f_os("GAIN") is False and f_os("NEITHER") is False and f_os("EQUIVALENT") is False
    assert abs(brier(PROB_OS1, "LOSS") - (0.45 ** 2 + 0.65 ** 2 + 0.20 ** 2)) < 1e-12
    assert abs(brier(PROB_OS1, "GAIN") - (0.45 ** 2 + 0.35 ** 2 + 0.20 ** 2 + 1.0)) < 1e-12
    assert abs(brier(PROB_OS2, "CALIBRATED") - 0.32) < 1e-12 and abs(brier(PROB_OS2, "UNDER-CATCH") - 0.72) < 1e-12
    # print branches on synthetic R, by value
    W = dict(sources=("AA", "BB", "CC"))

    def st(d, se=0.004, lo=None, hi=None):
        return dict(d=d, lo=d - 0.01 if lo is None else lo, hi=d + 0.01 if hi is None else hi, se=se, deff=1.1, n=100, G=90, n_eff=91,
                    mde=0.01, disc=0.1)
    for ol1, d, se, want in (("EQUIVALENT", 0.001, 0.004, "OS1: EQUIVALENT: the 90% interval [-0.0056, +0.0076] lies inside +/-0.020"),
                             ("LOSS", -0.04, 0.005, "OS1: DIFFERENT (LOSS): |D| 0.0400 > 0.020 and the 95% interval [-0.0498, -0.0302]"),
                             ("GAIN", 0.04, 0.005, "OS1: DIFFERENT (GAIN): |D| 0.0400 > 0.020 and the 95% interval [+0.0302, +0.0498]"),
                             ("NEITHER", -0.019, 0.012, "OS1: NEITHER: the 90% interval [-0.0387, +0.0007] is not inside +/-0.020")):
        assert ORL.ol1_word(d, se) == ol1
        a = dict(st=st(d, se), p_on=0.7, p_b=0.7 - d, ol1=ol1, st_split=st(d + 0.001), st_eos=st(d + 0.003), d_s1=-0.0386)
        _need("\n".join(os1_lines(a, True)), want, "= %+.4f; TOST 90%%" % d, "one-cell IFEVAL out): %+.4f" % (d + 0.001),
              "transductive) filing D %+.4f" % (d + 0.003), "D -0.0386; stage 2 minus stage 1 %+.4f" % (d + 0.0386))
    cal = {m: dict(tau=0.5, per=[], med=0.8) for m in W["sources"]}
    for catches, word, want in (((0.9, 0.7, 0.1), "CALIBRATED", "OS2: CALIBRATED: the median over the 3 held-out members' catch rates 0.7000 >= 0.70"),
                                ((0.9, 0.69, 0.1), "UNDER-CATCH", "OS2: UNDER-CATCH: the median over the 3 held-out members' catch rates 0.6900 < 0.70")):
        reps = {m: dict(catch=c, n_buf=int(c * 100), n_stream=100, buf_train=0, n_train=50, buf_eval=0, tau=0.5)
                for m, c in zip(W["sources"], catches)}
        a = dict(reps=reps, cals=cal, med_catch=float(np.median(catches)), os2=os2_word(catches))
        assert a["os2"] == word
        _need("\n".join(os2_lines(W, a, True)), want, "distance |median - 0.70| %.4f" % abs(float(np.median(catches)) - 0.70))
    for ol1, os2, d, med, fb, dk, wants, nots in (
            ("LOSS", "CALIBRATED", -0.03, 0.75, 0.30, -0.02,
             ("F-OS FIRES: OS1 reads DIFFERENT (LOSS), D -0.0300", "P1 D -0.015 [-0.035, +0.005]: observed -0.0300 -> HELD",
              "observed LOSS; Brier 0.6650", "observed 0.7500 -> HELD", "observed CALIBRATED; Brier 0.3200 (two named outcomes;"
              " stage 1's one-term form 0.1600 beside)", "observed 0.3000 -> HELD", "observed -0.0200 -> HELD"),
             ("F-OS NOT FIRED", "UNDER-CATCH does not fire")),
            ("GAIN", "UNDER-CATCH", 0.03, 0.50, 0.60, 0.01,
             ("F-OS NOT FIRED: OS1 reads GAIN", "OS2 UNDER-CATCH does not fire F-OS", "observed +0.0300 -> FAILED",
              "observed GAIN; Brier 1.3650", "observed 0.5000 -> FAILED", "observed UNDER-CATCH; Brier 0.7200",
              "one-term form 0.3600", "observed 0.6000 -> FAILED", "observed +0.0100 -> FAILED"), ("F-OS FIRES",)),
            ("NEITHER", "CALIBRATED", -0.0351, 0.881, 0.149, -0.0451,
             ("F-OS NOT FIRED: OS1 reads NEITHER", "observed -0.0351 -> FAILED", "observed NEITHER; Brier 0.4650",
              "observed 0.8810 -> FAILED", "observed 0.1490 -> FAILED", "observed -0.0451 -> FAILED"), ("F-OS FIRES", "UNDER-CATCH")),
            ("EQUIVALENT", "CALIBRATED", 0.005, 0.55, 0.50, 0.005,
             ("F-OS NOT FIRED: OS1 reads EQUIVALENT", "observed +0.0050 -> HELD", "observed EQUIVALENT; Brier 0.9650",
              "observed 0.5500 -> HELD", "observed 0.5000 -> HELD", "observed +0.0050 -> HELD"), ("F-OS FIRES",))):
        T = dict(st=st(d), ol1=ol1, os2=os2, med_catch=med, fb_med=fb)
        R = dict(arms=dict(tree=T, km=dict(st=st(dk))))
        txt = "\n".join(falsifier_lines(R) + pred_lines(W, R))
        _need(txt, *wants)
        for nd in nots:
            assert nd not in txt, (ol1, nd)


def _toy_world(n_train, n_eval_d=0):
    """Sources YY (cells on e0, e1; in-member) and ZZ (held out): ZZ's n_train TRAIN items and 10 EVAL items on e2 (one class),
    every one of them buffered at tau 0.5 (cos 0 to the in-member cells): the first rebuild happens at the 100th buffered item."""
    dim = 4
    E = np.eye(dim)
    Xt = np.vstack([E[0]] * 3 + [E[1]] * 3 + [E[2]] * n_train)
    nd = n_eval_d
    ne = 10 if nd == 0 else nd
    Xe = np.vstack([E[2]] * ne + [E[0], E[1]])
    tsrc = np.array(["YY"] * 6 + ["ZZ"] * n_train)
    esrc = np.array(["ZZ"] * ne + ["YY"] * 2)
    yt = np.array([0] * 3 + [1] * 3 + [2] * n_train)
    ye = np.array([2 if nd == 0 else 3] * ne + [0, 1])
    tree = dict(ids=["YY:0", "YY:1"], src=np.array(["YY", "YY"]), mu=np.vstack([E[0], E[1]]), n=np.array([3, 3]), r=np.ones(2),
                name=np.array([0, 1]), cdom=np.array([3, 3]), policy=None, fallback=None)
    return dict(classes=["YY/a", "YY/b", "ZZ/c", "ZZ/d"], sources=("YY", "ZZ"), single={}, ksrc={"YY": 2, "ZZ": 1}, Xt=Xt, yt=yt,
                tsrc=tsrc, Xe=Xe, ye=ye, esrc=esrc, ecomp=np.arange(len(ye)), Xg=np.vstack([E[3]]), gsrc=np.array(["YY"]), arms={"tree": tree},
                titems=["t%d" % i for i in range(len(yt))], eitems=["e%d" % i for i in range(len(ye))])


def st_toy_stream(tmp):
    r = stream(_toy_world(99), "tree", "ZZ", 0.5)
    assert r["n_buf"] == 109 and r["catch"] == 1.0 and len(r["rebuilds"]) == 1, (r["n_buf"], len(r["rebuilds"]))
    assert r["rebuilds"][0]["size"] == 100 and r["rebuilds"][0]["n_eval"] == 1 and r["rebuilds"][0]["purity"] == 1.0
    assert sorted(r["online_ok"].tolist()) == [0] + [1] * 9, r["online_ok"]
    assert float(r["online_ok"].mean()) == 0.9, r["online_ok"]               # the 1st EVAL item is filed BEFORE it triggers
    assert float(r["eos_ok"].mean()) == 1.0 and int(r["churn"].sum()) == 0 and r["false_buf"] == 0.0
    r = stream(_toy_world(100), "tree", "ZZ", 0.5)
    assert float(r["online_ok"].mean()) == 1.0 and len(r["rebuilds"]) == 1 and r["rebuilds"][0]["n_eval"] == 0
    r = stream(_toy_world(250), "tree", "ZZ", 0.5)
    assert len(r["rebuilds"]) == 2 and [x["size"] for x in r["rebuilds"]] == [100, 200], r["rebuilds"]
    r = stream(_toy_world(99), "tree", "ZZ", 0.0)                             # cos exactly 0 = tau: equality FILES (strict)
    # renaming (OL-R5) at tau 0: ZZ's 99 TRAIN items are absorbed into YY:0 (argmax tie -> first) and rename it ZZ/c (99 > 3),
    # so every EVAL item filed there at arrival is correct
    assert r["n_buf"] == 0 and r["filed"] == 109 and r["renamed"] == 1 and float(r["online_ok"].mean()) == 1.0, (r["n_buf"], r["renamed"])
    # OL-R5 tie: 3 absorbed ZZ/c items = YY:0's batch count 3 -> the incumbent keeps the name (no rename, EVAL filed wrong); 4 rename
    r = stream(_toy_world(3), "tree", "ZZ", 0.0)
    assert r["renamed"] == 0 and float(r["online_ok"].mean()) == 0.0, (r["renamed"], r["online_ok"])
    r = stream(_toy_world(4), "tree", "ZZ", 0.0)
    assert r["renamed"] == 1 and float(r["online_ok"].mean()) == 1.0, (r["renamed"], r["online_ok"])
    # buffer naming reads TRAIN only: 40 TRAIN ZZ/c then 70 EVAL ZZ/d, all buffered; the rebuild at 100 (40 TRAIN + 60 EVAL) is
    # named ZZ/c (TRAIN majority), so the 10 later ZZ/d EVAL items are filed wrong; purity 40 / 100; end-of-stream also ZZ/c
    r = stream(_toy_world(40, 70), "tree", "ZZ", 0.5)
    assert len(r["rebuilds"]) == 1 and r["rebuilds"][0]["purity"] == 0.4 and r["rebuilds"][0]["n_eval"] == 60, r["rebuilds"]
    assert int(r["online_ok"].sum()) == 0 and int(r["eos_ok"].sum()) == 0, (r["online_ok"].sum(), r["eos_ok"].sum())


def st_e2e_allbuf15(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "allbuf", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    for m in FX_SOURCES:
        assert T["reps"][m]["catch"] == 1.0 and T["reps"][m]["n_train"] >= 100, (m, T["reps"][m]["catch"])
    assert T["st"]["d"] == 0.0 and T["ol1"] == "EQUIVALENT" and T["os2"] == "CALIBRATED" and R["arms"]["km"]["st"]["d"] == 0.0
    _need(txt, "= +0.0000; TOST 90% [+0.0000, +0.0000]", "OS1: EQUIVALENT: the 90% interval [+0.0000, +0.0000] lies inside +/-0.020",
          "OS2: CALIBRATED: the median over the 4 held-out members' catch rates 1.0000 >= 0.70",
          "F-OS NOT FIRED: OS1 reads EQUIVALENT", "PREDICTION P1 D -0.015 [-0.035, +0.005]: observed +0.0000 -> HELD",
          "observed EQUIVALENT; Brier 0.9650", "PREDICTION P2 OS2 median catch rate 0.75 [0.55, 0.88]: observed 1.0000 -> FAILED",
          "observed 0.0000 -> FAILED", "INTEGRITY (not a criterion", "tree -AA 0/", "DENOMINATOR (OS1): the held-out members' EVAL"
          " items pooled over 4 replays = %d items" % len(W["ye"]), "decision churn 0.0000")
    assert "F-OS FIRES" not in txt and "UNDER-CATCH" not in txt.split("--- PREDICTIONS ---")[0]
    with open(os.path.join(out_dir, OUTCOME), encoding="utf-8") as f:
        body = f.read()
    assert body.splitlines()[0].startswith("POOL %s" % POOL), body.splitlines()[0]
    _need(body, "OS1: EQUIVALENT", "OS2: CALIBRATED", "F-OS NOT FIRED")
    rows = open(os.path.join(out_dir, ITEMS_CSV), encoding="utf-8").read().splitlines()
    assert rows[0] == "item_id,replay,arm,side,stream_pos,maxcos_five,buffered,cell_at_arrival,online_ok,batch_ok,eos_ok"
    assert len(rows) - 1 == 2 * (len(W["ye"]) + len(W["yt"])), (len(rows), len(W["ye"]), len(W["yt"]))


def st_e2e_allbuf13(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "allbuf", 13)
    _check_oracle(parts, reg_fx, txt, R, W)
    T, K = R["arms"]["tree"], R["arms"]["km"]
    n = len(W["ye"])
    assert n == 416 and T["reps"]["DD"]["n_train"] == 91
    assert abs(T["st"]["d"] - (-9.0 / n)) < 1e-12 and abs(K["st"]["d"] - (-9.0 / n)) < 1e-12, (T["st"]["d"], K["st"]["d"])
    assert abs(T["per"]["DD"]["d"]["d"] - (-9.0 / 52)) < 1e-12
    assert T["ol1"] == "LOSS", (T["ol1"], T["st"]["se"])
    _need(txt, "= %+.4f; TOST 90%%" % (-9.0 / n), "OS1: DIFFERENT (LOSS): |D| 0.0216 > 0.020",
          "F-OS FIRES: OS1 reads DIFFERENT (LOSS), D -0.0216", "observed LOSS; Brier 0.6650", "end-of-stream (fully transductive)"
          " filing D +0.0000")


def st_e2e_tight(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "tight", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    assert T["os2"] == "UNDER-CATCH" and T["med_catch"] < OS2_BAR, T["med_catch"]
    _need(txt, "OS2: UNDER-CATCH: the median over the 4 held-out members' catch rates %.4f < 0.70" % T["med_catch"],
          "  OS2 UNDER-CATCH does not fire F-OS (registered)")
    assert txt.count("decision churn NOT COMPUTED (policy absent)") == 2 * len(FX_SOURCES)


def st_e2e_absorb(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "absorb", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    r = R["arms"]["tree"]["reps"]["BB"]
    assert r["filed"] > 0 and 0 < r["n_buf"] < r["n_stream"], (r["filed"], r["n_buf"])


def st_e2e_rename(tmp):
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "rename", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    assert R["arms"]["tree"]["reps"]["BB"]["renamed"] >= 1, R["arms"]["tree"]["reps"]["BB"]["renamed"]


def st_e2e_stiff(tmp):
    """The deciding OS1 / OS2 / F-OS blocks print the TREE arm (tree and k-means differ here), position-checked."""
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "stiff", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    T, K = R["arms"]["tree"], R["arms"]["km"]
    assert T["st"]["d"] != K["st"]["d"] and T["catches"] != K["catches"], (T["st"]["d"], K["st"]["d"])
    b1 = txt.split("--- OS1 (DECIDING")[1].split("--- OS2 (DECIDING")[0]
    _need(b1, "= %+.4f; TOST 90%%" % T["st"]["d"])
    assert "= %+.4f; TOST 90%%" % K["st"]["d"] not in b1
    b2 = txt.split("--- OS2 (DECIDING")[1].split("--- F-OS ---")[0]
    for m in FX_SOURCES:
        _need(b2, "  -%s: catch %.4f = %d of" % (m, T["reps"][m]["catch"], T["reps"][m]["n_buf"]))
    _need(b2, "catch rates %.4f" % T["med_catch"])
    b3 = txt.split("--- PREDICTIONS ---")[1].split("--- DESCRIPTIVE: the k-means")[0]
    _need(b3, "P1 D -0.015 [-0.035, +0.005]: observed %+.4f" % T["st"]["d"], "k-means arm D -0.020 [-0.045, +0.005] (descriptive):"
          " observed %+.4f" % K["st"]["d"], "observed %.4f -> " % T["med_catch"])
    bk = txt.split("--- DESCRIPTIVE: the k-means")[1].split("--- DESCRIPTIVE: per replay")[0]
    _need(bk, "= %+.4f; TOST 90%%" % K["st"]["d"], "catch rates %.4f" % K["med_catch"])
    tm = float(np.mean(T["diff"] - K["diff"]))
    _need(bk, "tree-minus-k-means paired (D_tree - D_K, per item): %+.4f" % tm)


def st_e2e_wide(tmp):
    """Noisy items: the in-members' false-buffer shares differ by replay (median != mean); P3 prints the median."""
    parts, reg_fx, txt, R, W, out_dir = _run_fx(tmp, "wide", 15)
    _check_oracle(parts, reg_fx, txt, R, W)
    T = R["arms"]["tree"]
    fbs = [T["reps"][m]["false_buf"] for m in FX_SOURCES]
    assert abs(float(np.median(fbs)) - float(np.mean(fbs))) > 1e-4, fbs
    _need(txt, "median over replays, 0.30 [0.15, 0.50] (descriptive): observed %.4f -> " % float(np.median(fbs)))


def st_e2e_se(tmp):
    """The OS1 word is read at the bootstrap SD (OL-R7), never from the percentile width: the pooled stat stubbed to SE |D| / 1.5
    with a percentile interval D +/- 0.001 (allbuf13, D -0.0216): TOST / DIFFERENT at the SD -> NEITHER (a width-based SE -> LOSS)."""
    parts, reg_fx, reg2_fx = _fxc("allbuf", 13)
    real = GB.stat
    n_all = len(parts["ye"])

    def fake(diff, comp):
        st = real(diff, comp)
        if st is not None and st["n"] == n_all and abs(st["d"]) > 0.02:
            st = dict(st, se=abs(st["d"]) / 1.5, lo=st["d"] - 0.001, hi=st["d"] + 0.001)
        return st
    out_dir = os.path.join(tmp, "se")
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        GB.stat = fake
        try:
            txt, R = _capture(run, out_dir=out_dir)
        finally:
            GB.stat = real
    T = R["arms"]["tree"]
    assert T["ol1"] == "NEITHER" and abs(T["st"]["se"] - 9.0 / 416 / 1.5) < 1e-12, (T["ol1"], T["st"]["se"])
    _need(txt, "OS1: NEITHER: the 90% interval", "F-OS NOT FIRED: OS1 reads NEITHER")


def st_integrity(tmp):
    parts, reg_fx, reg2_fx = _fxc("allbuf", 15)

    def bad_stream(W, arm, m, tau):
        r = stream(W, arm, m, tau)
        if arm == "km" and m == "BB":
            r["churn"] = r["churn"].copy()
            r["churn"][0] = 1
        return r
    out_dir = os.path.join(tmp, "integ")
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        _STREAM[0] = bad_stream
        try:
            _capture(run, out_dir=out_dir)
            raise AssertionError("nonzero churn not refused")
        except SystemExit as e:
            assert "[OS-INTEGRITY]" in str(e) and "km -BB churn 1" in str(e), str(e)
        finally:
            _STREAM[0] = stream
    assert not os.path.exists(os.path.join(out_dir, OUTCOME))


def st_stage1(tmp):
    parts, reg_fx, reg2_fx = _fxc("allbuf", 15)
    for k in ("id_s1_tree", "id_s1_km"):
        out_dir = os.path.join(tmp, "s1_" + k)
        with _swapped(parts, reg_fx, dict(reg2_fx, **{k: "+0.9999"}), prog=_fx_prog(tmp)):
            try:
                _capture(run, out_dir=out_dir)
                raise AssertionError("stage-1 identity not refused")
            except SystemExit as e:
                assert "[OS-STAGE1]" in str(e), str(e)
        assert not os.path.exists(os.path.join(out_dir, OUTCOME))


def st_write_once(tmp):
    parts, reg_fx, reg2_fx = _fxc("allbuf", 15)
    out_dir = os.path.join(tmp, "wo")
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        _capture(run, out_dir=out_dir)
        before = open(os.path.join(out_dir, OUTCOME), encoding="utf-8").read()
        try:
            _capture(run, out_dir=out_dir)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e)
        assert open(os.path.join(out_dir, OUTCOME), encoding="utf-8").read() == before
    od2 = os.path.join(tmp, "wo2")
    os.makedirs(od2)
    open(os.path.join(od2, ITEMS_CSV), "w").close()
    calls = []
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp), pool=lambda p: (calls.append(p), (0, "x"))[1]):
        try:
            _capture(run, out_dir=od2)
            raise AssertionError("existing items CSV not refused")
        except SystemExit as e:
            assert "write-once" in str(e) and not calls, (str(e), calls)
    assert not os.path.exists(os.path.join(od2, OUTCOME))
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp, with_heading=False)):
        try:
            _capture(run, out_dir=os.path.join(tmp, "wo3"))
            raise AssertionError("missing heading not refused")
        except SystemExit as e:
            assert "registered heading" in str(e)
    buf = []
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp), pool=lambda p: (1, "a writer is open")):
        try:
            run(out=buf.append, out_dir=os.path.join(tmp, "wo4"))
            raise AssertionError("pool rc 1 not refused")
        except SystemExit as e:
            assert "B0-2 pool check failed" in str(e)
    assert buf[0].startswith("POOL %s" % POOL) and any("POOL CHECK (B0-2" in b and "rc 1" in b for b in buf), buf[:3]
    assert not os.path.exists(os.path.join(tmp, "wo4", OUTCOME))
    # race: a file appearing after the pre-check is never overwritten (mode "x")
    od5 = os.path.join(tmp, "race")
    po = os.path.join(od5, OUTCOME)

    def loader(say):
        os.makedirs(od5, exist_ok=True)
        with open(po, "w", encoding="utf-8") as f:
            f.write("PEER\n")
        return parts
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        _LOAD[0] = loader
        try:
            _capture(run, out_dir=od5)
            raise AssertionError("a file appearing after the pre-check was overwritten")
        except FileExistsError:
            pass
    assert open(po, encoding="utf-8").read() == "PEER\n" and not os.path.exists(os.path.join(od5, ITEMS_CSV))


def st_dry_run(tmp):
    parts, reg_fx, reg2_fx = _fxc("absorb", 15)
    out_dir = os.path.join(tmp, "dry")
    with _swapped(parts, reg_fx, reg2_fx, prog=_fx_prog(tmp)):
        txt, rc = _capture(dry_run, out_dir=out_dir)
    W = _world(parts, reg_fx)
    assert rc == 0 and txt.splitlines()[0].startswith("POOL %s" % POOL)
    _need(txt, "POOL CHECK (B0-2", "DENOMINATORS (registered): OS1 6139 held-out EVAL items in 5628 components pooled over 4 replays",
          "REGISTRATION heading FOUND", "CALIBRATION (GATE only", "DRY-RUN: nothing written", "blob:%s" % ORL_PIN[1])
    for bad in ("OS1:", "OS2:", "F-OS", "catch rates 0", "catch 0", "streamed buffered", "PREDICTION", "IDENTITY (stage 1", "D = P_fl"):
        assert bad not in txt, bad
    assert not os.path.exists(out_dir)
    for arm in ARMS:
        c = calibrate(W, arm, "BB")
        _need(txt, "  %s -BB: tau_m %.5f (median share %.4f >= 0.80)" % (ARM_NAME[arm], c["tau"], c["med"]))
    buf = []
    _REG2[0], saved = REG2, _REG2[0]
    denominators(buf.append)
    _REG2[0] = saved
    _need(buf[0], "OS1 6139 held-out EVAL items in 5628 components pooled over 6 replays (DEFF 1.263", "n_eff 4861", "SE 0.00641")


REGISTERED_BRANCHES = ("OS1.EQUIVALENT", "OS1.LOSS", "OS1.GAIN", "OS1.NEITHER", "OS2.CALIBRATED", "OS2.UNDER", "FOS.FIRES",
                       "FOS.NOT_FIRED", "FOS.UNDER_NOTE", "P1.HELD", "P1.FAILED", "P2.HELD", "P2.FAILED", "P3.HELD", "P3.FAILED",
                       "P4.HELD", "P4.FAILED", "OS1.SPLIT_ONLY", "REFUSE.CAL", "REFUSE.INTEGRITY", "REFUSE.STAGE1",
                       "REFUSE.WRITE_ONCE", "REFUSE.REG", "REFUSE.POOL", "RUN.DONE", "DRY.DONE")


def st_branch_cover():
    miss = [b for b in REGISTERED_BRANCHES if HIT[b] == 0]
    assert not miss, "print branches never hit: %s" % miss


CASES = (("branches", st_branches, False), ("toy_stream", st_toy_stream, True), ("e2e_allbuf15", st_e2e_allbuf15, True),
         ("e2e_allbuf13", st_e2e_allbuf13, True), ("e2e_tight", st_e2e_tight, True), ("e2e_absorb", st_e2e_absorb, True),
         ("e2e_rename", st_e2e_rename, True), ("e2e_stiff", st_e2e_stiff, True), ("e2e_wide", st_e2e_wide, True),
         ("e2e_se", st_e2e_se, True), ("integrity", st_integrity, True), ("stage1", st_stage1, True),
         ("write_once", st_write_once, True), ("dry_run", st_dry_run, True), ("branch_cover", st_branch_cover, False))


def selftest(only=None, quiet=False):
    HIT.clear()
    for nm, fn, needs_tmp in CASES:
        if only and nm not in only:
            continue
        if needs_tmp:
            tmp = tempfile.mkdtemp(prefix="os2_st_")
            try:
                fn(tmp)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            fn()
        if not quiet:
            print("%s selftest %-14s OK" % (TAG, nm))
    if not quiet:
        print("%s SELFTEST PASSED (%d cases)" % (TAG, len(CASES)))


# ── mutants (each edits this file's source above MUTANTS in memory; the selftest must fail) ─────────────────────────────────

MUTANTS = (
    ("C01 calibration share non-strict (<=)", '    shares = np.vstack([np.searchsorted(s, cand, side="left")',
     '    shares = np.vstack([np.searchsorted(s, cand, side="right")'),
    ("C02 calibration mean over j instead of the median", "    med = np.median(shares, axis=0)", "    med = np.mean(shares, axis=0)"),
    ("C03 calibration min over j (min<->max)", "    med = np.median(shares, axis=0)", "    med = np.min(shares, axis=0)"),
    ("C04 calibration max over j", "    med = np.median(shares, axis=0)", "    med = np.max(shares, axis=0)"),
    ("C05 largest attaining candidate instead of the smallest", "    k = int(ok[0])", "    k = int(ok[-1])"),
    ("C06 target catch 0.70 (the OS2 bar) instead of 0.80", "def cal_tau(score_lists, target=TARGET):",
     "def cal_tau(score_lists, target=OS2_BAR):"),
    ("C07 calibration cells include j's own member (wrong population)", "        other = (A[\"src\"] != m) & (A[\"src\"] != j)",
     "        other = (A[\"src\"] != m)"),
    ("C08 calibration cells include the held-out member", "        other = (A[\"src\"] != m) & (A[\"src\"] != j)",
     "        other = (A[\"src\"] != j)"),
    ("C09 calibration on EVAL items (wrong split side)", "        g = W[\"gsrc\"] == j\n        sc = (W[\"Xg\"][g]",
     "        g = W[\"esrc\"] == j\n        sc = (W[\"Xe\"][g]"),
    ("C10 calibration j set includes the held-out member", "    inm = [s for s in W[\"sources\"] if s != m]\n    lists, rows",
     "    inm = list(W[\"sources\"])\n    lists, rows"),
    ("C11 calibration refusal skipped", "    if len(ok) == 0:\n        hit(\"REFUSE.CAL\")",
     "    if len(ok) == 0 and False:\n        hit(\"REFUSE.CAL\")"),
    ("S01 buffer non-strict (<=)", "        if top1 < tau:\n            buf.append((side, i))", "        if top1 <= tau:\n            buf.append((side, i))"),
    ("S02 means updated (stage 1's refit; frozen means broken)", "        filed += 1\n        if side == \"T\":",
     "        filed += 1\n        U[j1] = U[j1] + (x - U[j1]) / 3.0\n        U[j1] = U[j1] / np.linalg.norm(U[j1])\n        if side == \"T\":"),
    ("S03 EVAL filed AFTER the buffer decision (not prequential)", "        if side == \"E\":                                        # PREQUENTIAL",
     "        if False:                                              # PREQUENTIAL"),
    ("S04 rebuild every 101", "            if len(buf) % REBUILD == 0:", "            if len(buf) % (REBUILD + 1) == 0:"),
    ("S05 rebuild every 99", "            if len(buf) % REBUILD == 0:", "            if len(buf) % (REBUILD - 1) == 0:"),
    ("S06 no periodic rebuild (first rebuild only)", "            if len(buf) % REBUILD == 0:", "            if len(buf) == REBUILD:"),
    ("S07 rebuild on the newest 100 items only (not from scratch on all)", "                Cb, bnames, info = _fit_buffer(W, buf, Lm, classes)",
     "                Cb, bnames, info = _fit_buffer(W, buf[-REBUILD:], Lm, classes)"),
    ("S08 buffer k = 1 always", "    kb = min(Lm, len(buf))", "    kb = min(1, len(buf))"),
    ("S09 buffer naming from EVAL labels too", "    bnames = np.array([GB.majority(ybuf[tmask & (blab == j)], classes) for j in range(kb)], dtype=int)",
     "    bnames = np.array([GB.majority(ybuf[blab == j], classes) for j in range(kb)], dtype=int)"),
    ("S10 renaming on ties (>=)", "            if top > cdom[j1]:", "            if top >= cdom[j1]:"),
    ("S11 renaming disabled", "            if top > cdom[j1]:", "            if False:"),
    ("S12 absorbed EVAL items rename cells", "        if side == \"T\":\n            cnt = absorbed[j1]\n            cnt[int(W[\"yt\"][i])] += 1",
     "        if True:\n            cnt = absorbed[j1]\n            cnt[int(W[\"yt\"][i] if side == \"T\" else W[\"ye\"][i])] += 1"),
    ("S13 stream EVAL before TRAIN", "    order = [(\"T\", int(i)) for i in rng.permutation(tout)] + [(\"E\", int(i)) for i in rng.permutation(eout)]",
     "    order = [(\"E\", int(i)) for i in rng.permutation(eout)] + [(\"T\", int(i)) for i in rng.permutation(tout)]"),
    ("S14 order seed varies by replay", "    rng = np.random.default_rng(ORL.ORDER_SEED)\n    order",
     "    rng = np.random.default_rng(ORL.ORDER_SEED + len(ids))\n    order"),
    ("S15 trigger reads the five-member cells plus buffer cells", "        j1 = int(np.argmax(s))\n        top1 = float(s[j1])",
     "        j1 = int(np.argmax(s))\n        top1 = float(max(s[j1], (Cb @ x).max() if len(Cb) else -9.0))"),
    ("S16 filing ignores the buffer cells", "            sc = np.concatenate([s, Cb @ x])", "            sc = np.concatenate([s, -9.0 + 0 * (Cb @ x)])"),
    ("S17 filing by argmin (min<->max)", "            a = int(np.argmax(sc))", "            a = int(np.argmin(sc))"),
    ("S18 end-of-stream filing decides OS1 (stage 1's rule)", "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][arm][r[\"eout\"]]\n            deos",
     "            diff[r[\"eout\"]] = r[\"eos_ok\"] - W[\"batch\"][arm][r[\"eout\"]]\n            deos"),
    ("S19 end-of-stream refit = the last rebuild", "        Ce, be, einfo = _fit_buffer(W, buf, Lm, classes)",
     "        Ce, be, einfo = Cb, bnames, None"),
    ("R01 OS2 mean instead of the median", "    return \"CALIBRATED\" if float(np.median(np.asarray(catches, dtype=np.float64))) >= bar",
     "    return \"CALIBRATED\" if float(np.mean(np.asarray(catches, dtype=np.float64))) >= bar"),
    ("R02 OS2 strict (>)", "dtype=np.float64))) >= bar else", "dtype=np.float64))) > bar else"),
    ("R03 OS2 bar = the 0.80 target", "def os2_word(catches, bar=OS2_BAR):", "def os2_word(catches, bar=TARGET):"),
    ("R04 catch over EVAL only", "catch=len(buf) / max(len(order), 1)", "catch=int(bt[n_tr:].sum()) / max(len(order) - n_tr, 1)"),
    ("R05 catch over TRAIN only", "catch=len(buf) / max(len(order), 1)", "catch=int(bt[:n_tr].sum()) / max(n_tr, 1)"),
    ("R06 OS1 against the mirrored batch", "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][arm][r[\"eout\"]]\n            deos",
     "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch_mir\"][arm][r[\"eout\"]]\n            deos"),
    ("R07 OS1 against the k-means batch", "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][arm][r[\"eout\"]]\n            deos",
     "            diff[r[\"eout\"]] = r[\"online_ok\"] - W[\"batch\"][\"km\"][r[\"eout\"]]\n            deos"),
    ("R08 pooled D over the first replay only", "        for m, r in reps.items():\n            diff[r[\"eout\"]] = r[\"online_ok\"]",
     "        for m, r in list(reps.items())[:1]:\n            diff[r[\"eout\"]] = r[\"online_ok\"]"),
    ("R09 F-OS fires on any DIFFERENT (GAIN too)", "    return os1 == \"LOSS\"", "    return os1 in (\"LOSS\", \"GAIN\")"),
    ("R10 F-OS fires on NEITHER", "    return os1 == \"LOSS\"", "    return os1 in (\"LOSS\", \"NEITHER\")"),
    ("R11 F-OS block omitted", "    L.extend(falsifier_lines(R))\n    say(\"--- PREDICTIONS ---\")", "    say(\"--- PREDICTIONS ---\")"),
    ("R12 deciding OS1 block prints the k-means arm", "    L.extend(os1_lines(T, True))", "    L.extend(os1_lines(K, True))"),
    ("R13 deciding OS2 block prints the k-means arm", "    L.extend(os2_lines(W, T, True))", "    L.extend(os2_lines(W, K, True))"),
    ("R14 P1 band exclusive", "def in_band(x, lo, hi):\n    return lo <= x <= hi", "def in_band(x, lo, hi):\n    return lo < x < hi"),
    ("R15 Brier misses the GAIN term", "    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items()))",
     "    return float(sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in probs.items() if p > 0))"),
    ("R16 P3 mean instead of the median", "fb_med=float(np.median([reps[m][\"false_buf\"]", "fb_med=float(np.mean([reps[m][\"false_buf\"]"),
    ("R17 OS1 SE from the percentile width", "ol1=ORL.ol1_of(st), st_split", "ol1=ORL.ol1_word(st[\"d\"], (st[\"hi\"] - st[\"lo\"]) / 8.0), st_split"),
    ("R18 integrity check skipped", "    integrity(allreps)\n", "\n"),
    ("R19 write-once by overwrite", "    with open(po, \"x\", encoding=\"utf-8\", newline=\"\\n\") as f:",
     "    with open(po, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:"),
    ("R20 write-once pre-check skipped", "        if os.path.exists(p):\n            hit(\"REFUSE.WRITE_ONCE\")",
     "        if False:\n            hit(\"REFUSE.WRITE_ONCE\")"),
    ("R21 pool rc ignored", "    if rc != 0:\n        hit(\"REFUSE.POOL\")", "    if False:\n        hit(\"REFUSE.POOL\")"),
    ("R22 stage-1 identity skipped", "    if s_t != reg2()[\"id_s1_tree\"] or s_k != reg2()[\"id_s1_km\"]:", "    if False:"),
    ("R23 stage-1 identity on the tree arm only", "    if s_t != reg2()[\"id_s1_tree\"] or s_k != reg2()[\"id_s1_km\"]:",
     "    if s_t != reg2()[\"id_s1_tree\"]:"),
    ("R24 registration heading check skipped", "    if not (prog and os.path.isfile(prog) and REG_RE.search(open(prog, encoding=\"utf-8\").read())):",
     "    if False:"),
    ("R25 false buffering on the held-out member's EVAL (wrong population)",
     "    fb = float(np.mean((W[\"Xe\"][ein] @ U.T).max(axis=1) < tau)) if len(ein) else float(\"nan\")",
     "    fb = float(np.mean((W[\"Xe\"][eout] @ U.T).max(axis=1) < tau)) if len(eout) else float(\"nan\")"),
    ("R26 UNDER-CATCH note dropped", "    if T[\"os2\"] == \"UNDER-CATCH\":\n        hit(\"FOS.UNDER_NOTE\")",
     "    if False:\n        hit(\"FOS.UNDER_NOTE\")"),
    ("R27 P2 scored on the k-means arm", "    med = T[\"med_catch\"]\n    if in_band(med", "    med = K[\"med_catch\"]\n    if in_band(med"),
    ("R28 integrity reads only the moved flag (churn ignored)",
     "    bad = [(r[\"arm\"], r[\"m\"], int(r[\"churn\"].sum()), r[\"moved\"]) for r in reps if r[\"moved\"] or int(r[\"churn\"].sum()) != 0]",
     "    bad = [(r[\"arm\"], r[\"m\"], int(r[\"churn\"].sum()), r[\"moved\"]) for r in reps if r[\"moved\"]]"),
)


def run_mutants():
    me = os.path.abspath(__file__)
    full = open(me, encoding="utf-8").read().replace("\r\n", "\n")
    cut = full.index("\n# \u2500\u2500 selftest")
    src, tail = full[:cut], full[cut:]                  # patterns are searched and replaced in the instrument only
    rows, survived = [], []
    for name, old, new in (("X00 control (no edit)", "", ""),) + MUTANTS:
        if old:
            k = src.count(old)
            if k != 1:
                rows.append((name, "BAD (pattern found %d times)" % k))
                survived.append(name)
                continue
            msrc = src.replace(old, new, 1) + tail
        else:
            msrc = full
        g = {"__name__": "os2_mutant", "__file__": me}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(msrc, me, "exec"), g)
                g["selftest"](quiet=True)
            res = "SURVIVED"
        except BaseException as e:      # noqa: BLE001 (SystemExit / AssertionError / anything = killed)
            res = "KILLED (%s: %s)" % (type(e).__name__, str(e).splitlines()[0][:90] if str(e) else "")
        rows.append((name, res))
        if old and res == "SURVIVED":
            survived.append(name)
        if not old and res != "SURVIVED":
            survived.append(name + " (control failed)")
    for n_, r_ in rows:
        print("  %-66s %s" % (n_, r_))
    k = sum(1 for n_, r_ in rows[1:] if r_.startswith("KILLED"))
    print("%s MUTANTS: %d of %d KILLED; control %s" % (TAG, k, len(MUTANTS), rows[0][1]))
    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
