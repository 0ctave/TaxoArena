"""lcb_power_resim.py: LCB-STAGE0-POWER-RESIM, G1's power at the MEASURED design of LCB-STAGE0-INTERACTION. ZERO calls.

REGISTRATION OF RECORD: docs/judge_v2_program.md, "## Registered 2026-09-30 (before any code or call) — LCB-STAGE0-POWER-RESIM: at
the MEASURED design of LCB-STAGE0-INTERACTION ..." (L22208-L22228 _as_of 7ea9ec1). It CANNOT change the STOP (G1 FAILS, p_T 0.0300
> 0.01); it licenses or replaces the STOP sentence's power words only (the closed LCB judged-stage line is not reopened).

THE TAG'S CODE, IMPORTED UNEDITED: tools/analysis/lcb_stage0/{stats.py blob:813d2d6d..., analysis.py blob:e3144692..., fixture.py
blob:10437edb...} at tag lcb-stage0-outcome-of-record (3bcc9ab), from --tag-root (a checkout AT the tag: HEAD and the three LF
blobs are verified before the import; nothing there is edited or written). Nothing of the analysis is re-implemented: the
measured design is CAPTURED from the tag's own analysis.analyse (its first stats.run_null call, the primary TRAIN object, and its
first stats.strata_primary call; the module attributes are wrapped for the one call and restored), and every world runs the
tag's stats functions: informative_mask, fit_null, fit_rasch, strata_primary, run_null (G1 only: with_g2=False; G2 draws no
random number, so p_T is the record path's, which the identity gate checks).

STEPS (registration INSTRUMENT 1-4):
  (1) IDENTITY GATE: analysis.analyse on the real inputs (B 2,000) must print T = 96.689 and p_T = 0.0300, AND the captured
      primary object re-run through the G1-only path must give the SAME T and p_T; else REFUSED (C0: VOIDS, never an outcome).
  (2) the registered null fit (stats.fit_null, the amended marginal rank-1 fit) on the captured TRAIN Y: a_m, s_m and
      delta_p = the fit's EAP of each problem's latent position (its "eap").
  (3) per world w and tau: G[m, k] ~ N(0, tau) iid over the M models x the K real regions; each model file's outcomes
      Binomial(n_m, expit(a_m + s_m delta_p + G[m, region_p])) / n_m on the real informative TRAIN problems (the captured 548;
      region_p = the routed region of the record; the real files n_m); world stream stats.rng_of("LCB-POWER-RESIM:<tau>:<w>").
  (4) the registered G1 unchanged per world: informative mask, fit_null (a non-converged fit = a FIT REFUSAL, counted), Rasch
      dhat, the 10 format x dhat-quintile strata, B 2,000 family-block permutations on the registered stream (C.PERM_SEED), the
      family-majority labelling, the bar p_T <= 0.01.
  Grid tau in {0, 0.15, 0.20, 0.25, 0.30}; W = 400 worlds per tau (2,000); at most 20 processes, OMP / OPENBLAS / MKL = 1.
  Printed beside (C2): per world the true count of model pairs with a 10pp reversal (region means of the TRUE probabilities:
  some region with a difference >= +0.10 and another <= -0.10), its mean at tau80.

READOUTS (C0 validity VOIDS; C1 the criterion, the INTERVAL decides; C2 descriptive): as registered, printed verbatim by render().
HYGIENE: TRAIN only; the EVAL sealed DB (manifest name, sha256 74ea30e5...) is never opened: its FILE sha256 is printed before
and after (a change REFUSES); GATE is read by the tag's analyse only as it always did (its sub-objects), never by a world.

  python tools/analysis/lcb_power_resim.py --selftest
  python tools/analysis/lcb_power_resim.py --dry-run --tag-root <checkout at the tag> --build-dir <lcb build worktree> \\
         --run-dir <build>/experiment_results/lcb_stage0/lcb_af_bareq512_s42/seed_42 --snapshot-id 20260925_121944_Headless_Run_Auto_ge \\
         --site-null <build>/experiment_results/lcb_stage0/site_null_lcb_af512.csv [--procs 20]
      (the identity gate, the null fit, 10 worlds at tau 0.20 TIMED; the projected wall for 2,000 worlds at --procs; REFUSED if
      the projection exceeds 60 min; writes nothing)
  python tools/analysis/lcb_power_resim.py --run ... [--procs 20]        # resumable: one JSON line per (tau, w), meta pinned
  python tools/analysis/lcb_power_resim.py --analyze ...                 # REFUSES unless all 2,000 worlds are present; write-once
TAXOARENA_LCB_ROOT is set in the process environment (the tag's convention). Outputs under
experiment_results/lcb_stage0/power_resim/ of THIS checkout: worlds.jsonl, meta.json, lcb_power_resim_outcome.txt (mode x).

SELFTEST MUTANTS (harness: one temporary edit at a time, reverted, then --selftest; 12/12 killed, the control survives):
  L0  control (a comment)                                 survived (expected)
  L1  identity: the G1-only comparison removed            killed  (1) identity gate
  L2  the world stream ignores tau                        killed  (3)-(4) worlds
  L3  HELD admits lo just below 0.80                      killed  C1 at the Wilson observables 336 / 304
  L4  the 20-process cap removed                          killed  the timing gate
  L5  a partial store analysed                            killed  --analyze end to end
  L6  the size bar 13 of 400                              killed  --analyze end to end (C0)
  L7  G added to the wrong model rows                     killed  (3) the simulation model
  L8  the files' n ignored (n = 1)                        killed  (3) the simulation model
  L9  the bar strict (p_T < 0.01)                         killed  (3)-(4) worlds
  L10 the 60-min timing limit ignored                     killed  the timing gate
  L11 an edited tag file imported                         killed  the tag's blobs verified
  L12 F1 fires on UNDETERMINED                            killed  --analyze end to end (render)
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import sys
import io
import json
import math
import time
import hashlib
import argparse
import tarfile
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import subprocess
import contextlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

TAG = "[LCB-RESIM]"
TAG_NAME = "lcb-stage0-outcome-of-record"
TAG_COMMIT = "3bcc9ab34937ea6ea4991d514b04b8c2870d91a2"
TAG_BLOBS = {"stats.py": "813d2d6dd1581883c41d10e0ebb7869a7be21122", "analysis.py": "e3144692177ce48b3adf95a112c210c667f25538",
             "fixture.py": "10437edbef903068f1842e36ccfbdb5feedd8176"}
IDENTITY = ("96.689", "0.0300")
TAUS = (0.0, 0.15, 0.20, 0.25, 0.30)
W_PER_TAU = 400
B = 2000
ALPHA = 0.01
MAX_PROCS = 20
DRY_WORLDS = 10
WALL_LIMIT_MIN = 60.0
BAR = 0.80
SIZE_MAX, FIT_REFUSAL_MAX = 12, 20
REVERSAL = 0.10
P1, P2, P3, P4 = (0.50, 0.88), (0.22, 0.62), (0.72, 0.97), (0.003, 0.025)
OUT_DIR = os.path.join(ROOT, "experiment_results", "lcb_stage0", "power_resim")


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise SystemExit(2)


def tau_str(t):
    return "%.2f" % t


# ── the tag's code ──────────────────────────────────────────────────────────────────────────────────────────────────

def _blob(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def extract_tag(dest, repo=ROOT):
    """The tag's tools/analysis tree (git archive; lcb_stage0 imports its pinned siblings), for the SELFTEST only (a real run uses a checkout at the tag)."""
    data = subprocess.run(["git", "archive", "--format=tar", TAG_NAME, "tools/analysis", "experiment_configs/lcb_stage0"], cwd=repo,
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        t.extractall(dest)
    return dest


def load_tag(tag_root, require_head=True):
    """Verify (HEAD = the tag's commit when require_head; the three LF blobs) and import the package. -> (ST, A, C)."""
    pkg = os.path.join(tag_root, "tools", "analysis", "lcb_stage0")
    for f, b in TAG_BLOBS.items():
        got = _blob(os.path.join(pkg, f))
        if got != b:
            refuse("%s/%s is blob:%s, not the tag's blob:%s" % (pkg, f, got, b))
    if require_head:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tag_root, capture_output=True, text=True).stdout.strip()
        if head != TAG_COMMIT:
            refuse("--tag-root %s is at %s, not the tag's commit %s" % (tag_root, head, TAG_COMMIT))
    ana = os.path.join(tag_root, "tools", "analysis")
    for m in [k for k in sys.modules if k == "lcb_stage0" or k.startswith("lcb_stage0.")]:
        del sys.modules[m]
    sys.path.insert(0, ana)
    from lcb_stage0 import stats as ST, analysis as A, common as C
    if os.path.normcase(os.path.dirname(ST.__file__)) != os.path.normcase(pkg):
        refuse("lcb_stage0 imported from %s, not %s" % (os.path.dirname(ST.__file__), pkg))
    return ST, A, C


# ── (1) the identity gate and the captured design ───────────────────────────────────────────────────────────────────

def capture_design(ST, A, inp, tree, site_null, b=B):
    """analysis.analyse on the inputs, capturing the primary object's run_null and strata_primary arguments. -> (R, design)."""
    cap = {}
    rn, sp = ST.run_null, ST.strata_primary

    def w_rn(*a, **k):
        cap.setdefault("run_null", (a, k))
        return rn(*a, **k)

    def w_sp(*a, **k):
        cap.setdefault("strata", a)
        return sp(*a, **k)
    ST.run_null, ST.strata_primary = w_rn, w_sp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            R = A.analyse(inp, tree, B=b, site_null=site_null, out=lambda *x, **y: None)
    finally:
        ST.run_null, ST.strata_primary = rn, sp
    if "run_null" not in cap or R.get("g") is None:
        refuse("(1) the analysis made no primary run_null call (the null fit did not converge)")
    (Y, pi, reg, K, fam, strata, n_models, seed), kw = cap["run_null"][0][:8], cap["run_null"][1]
    fmt, dhat = cap["strata"]
    design = dict(Y=np.asarray(Y), reg=np.asarray(reg), K=int(K), fam=list(fam), fmt=list(fmt), n_models=list(n_models),
                  seed=seed, B=int(kw.get("B", b)))
    return R, design


def identity_gate(ST, R, design, expected=IDENTITY):
    """(1): the record's T / p_T to the printed digits, and the G1-only path on the captured object gives the same numbers."""
    t_rec, p_rec = "%.3f" % R["g"]["T"], "%.4f" % R["g"]["p_T"]
    fm = ST.fit_null(design["Y"])
    fr = ST.fit_rasch(design["Y"])
    r = ST.run_null(design["Y"], fm["pi"], design["reg"], design["K"], design["fam"], ST.strata_primary(design["fmt"], fr["d"]),
                    design["n_models"], design["seed"], B=design["B"], with_g2=False)
    line = ("(1) IDENTITY: the tag's analyse prints T = %s, p_T = %s (B %d); the G1-only path on the captured object T = %.3f,"
            " p_T = %.4f; registered T = %s, p_T = %s" % (t_rec, p_rec, design["B"], r["T"], r["p_T"], expected[0], expected[1]))
    if (t_rec, p_rec) != tuple(expected) or r["T"] != R["g"]["T"] or r["p_T"] != R["g"]["p_T"]:
        refuse(line + " -> NOT REPRODUCED: C0 VOIDS the run")
    return line + " -> REPRODUCED", fm


# ── (2)-(4) the worlds ──────────────────────────────────────────────────────────────────────────────────────────────

def null_params(fm):
    return dict(a=np.asarray(fm["a"], dtype=float), s=np.asarray(fm["s"], dtype=float), delta=np.asarray(fm["eap"], dtype=float))


def true_probs(ST, params, reg, G):
    return ST.expit(params["a"][:, None] + params["s"][:, None] * params["delta"][None, :] + G[:, reg])


def true_reversals(P, reg, K):
    """Model pairs with a true 10pp reversal: region means of the TRUE probabilities differ by >= +0.10 in one region and <= -0.10
    in another."""
    means = np.stack([P[:, reg == k].mean(1) if np.any(reg == k) else np.full(P.shape[0], np.nan) for k in range(K)], axis=1)
    M = P.shape[0]
    n = 0
    for i in range(M):
        d = means[i][None, :] - means[i + 1:]
        n += int(np.sum((np.nanmax(d, axis=1) >= REVERSAL) & (np.nanmin(d, axis=1) <= -REVERSAL)))
    return n


def world_seed(tau, w):
    return "LCB-POWER-RESIM:%s:%d" % (tau_str(tau), w)


def simulate(ST, design, params, tau, w):
    """(3): G ~ N(0, tau) iid over models x regions; Y = Binomial(n_m, expit(a + s delta + G[m, region])) / n_m. -> (Y, P)."""
    rng = ST.rng_of(world_seed(tau, w))
    n_m = np.asarray(design["n_models"])
    M, K = len(n_m), design["K"]
    G = rng.normal(0.0, tau, (M, K)) if tau > 0 else np.zeros((M, K))
    P = true_probs(ST, params, design["reg"], G)
    Y = rng.binomial(n_m[:, None], P) / n_m[:, None]
    return Y, P


def world(ST, C, design, params, tau, w, b=B):
    """One world: simulate, then the registered G1 unchanged. -> dict (never raises for a fit failure: refused = True)."""
    n_m = np.asarray(design["n_models"])
    K = design["K"]
    Y, P = simulate(ST, design, params, tau, w)
    inf = ST.informative_mask(Y)
    idx = np.where(inf)[0]
    Yi, ri = Y[:, inf], design["reg"][inf]
    fi, mi = [design["fam"][i] for i in idx], [design["fmt"][i] for i in idx]
    rev = true_reversals(P, design["reg"], K)
    fm = ST.fit_null(Yi)
    if not fm["converged"]:
        return {"tau": tau_str(tau), "w": w, "refused": True, "n_informative": int(inf.sum()), "reversals": rev}
    fr = ST.fit_rasch(Yi)
    r = ST.run_null(Yi, fm["pi"], ri, K, fi, ST.strata_primary(mi, fr["d"]), list(n_m), C.PERM_SEED, B=b, with_g2=False)
    return {"tau": tau_str(tau), "w": w, "refused": False, "n_informative": int(inf.sum()), "T": r["T"], "p_T": r["p_T"],
            "reject": bool(r["p_T"] <= ALPHA), "reversals": rev}


_WORKER = {}


def _init_worker(tag_root, require_head, design, params, b):
    _WORKER["ST"], _WORKER["A"], _WORKER["C"] = load_tag(tag_root, require_head)
    _WORKER.update(design=design, params=params, b=b)


def _work(job):
    tau, w = job
    return world(_WORKER["ST"], _WORKER["C"], _WORKER["design"], _WORKER["params"], tau, w, _WORKER["b"])


def run_worlds(jobs, tag_root, require_head, design, params, procs, b=B, sink=None):
    """Worlds in <= MAX_PROCS processes (1 = in-process); each finished world goes to sink (the resumable store)."""
    procs = max(1, min(int(procs), MAX_PROCS))
    out = []
    if procs == 1:
        _init_worker(tag_root, require_head, design, params, b)
        for j in jobs:
            r = _work(j)
            out.append(r)
            if sink:
                sink(r)
        return out
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(procs, initializer=_init_worker, initargs=(tag_root, require_head, design, params, b)) as pool:
        for r in pool.imap_unordered(_work, jobs):
            out.append(r)
            if sink:
                sink(r)
    return out


def projection(per_world_s, procs, n_worlds=len(TAUS) * W_PER_TAU):
    procs = max(1, min(int(procs), MAX_PROCS))
    return per_world_s * n_worlds / procs / 60.0


def timing_gate(per_world_s, procs, limit=WALL_LIMIT_MIN):
    wall = projection(per_world_s, procs)
    line = ("TIMING: %.2f s per world (%d-world dry run at tau 0.20, one process) -> %d worlds at %d processes: projected wall"
            " %.1f min (limit %.0f)" % (per_world_s, DRY_WORLDS, len(TAUS) * W_PER_TAU, max(1, min(procs, MAX_PROCS)), wall, limit))
    if wall > limit:
        refuse(line + ": OVER the limit, the run is refused")
    return line + ": within the limit"


# ── readouts ────────────────────────────────────────────────────────────────────────────────────────────────────────

def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def summarise(worlds):
    by = {}
    for r in worlds:
        by.setdefault(r["tau"], []).append(r)
    out = {}
    for t in (tau_str(x) for x in TAUS):
        rs = by.get(t, [])
        ok = [r for r in rs if not r["refused"]]
        k = sum(1 for r in ok if r["reject"])
        lo, hi = wilson(k, len(rs))
        out[t] = dict(n=len(rs), refused=len(rs) - len(ok), k=k, power=(k / len(rs)) if rs else float("nan"), lo=lo, hi=hi,
                      reversals=float(np.mean([r["reversals"] for r in rs])) if rs else float("nan"))
    return out


def c1_verdict(s):
    if s["lo"] >= BAR:
        return "HELD"
    if s["hi"] < BAR:
        return "FAILED"
    return "UNDETERMINED"


def tau80(summ):
    for t in (tau_str(x) for x in TAUS[1:]):
        if summ[t]["lo"] >= BAR:
            return t
    return "> 0.30"


def band(x, b):
    return "HELD" if b[0] <= x <= b[1] else "FAILED"


def render(summ, meta):
    o = []
    say = o.append
    say("%s LCB-STAGE0-POWER-RESIM | registration docs/judge_v2_program.md L22208-L22228 (7ea9ec1) | zero calls" % TAG)
    for k in sorted(meta):
        say("  %s: %s" % (k, meta[k]))
    say("GRID (W %d per tau, B %d, bar p_T <= %.2f):" % (W_PER_TAU, B, ALPHA))
    for t in (tau_str(x) for x in TAUS):
        s = summ[t]
        say("  tau %s: %d of %d reject -> power %.4f, Wilson 95%% [%.4f, %.4f]; fit refusals %d; mean true 10pp-reversal pairs %.2f"
            % (t, s["k"], s["n"], s["power"], s["lo"], s["hi"], s["refused"], s["reversals"]))
    voids = [t for t in summ if summ[t]["refused"] > FIT_REFUSAL_MAX]
    size_k = summ[tau_str(0.0)]["k"]
    c0 = size_k <= SIZE_MAX and not voids
    say("C0 VALIDITY: identity REPRODUCED; size at tau 0 = %d of %d (bar <= %d); fit refusals per tau %s (> %d VOIDS that tau)%s -> %s"
        % (size_k, summ[tau_str(0.0)]["n"], SIZE_MAX, {t: summ[t]["refused"] for t in sorted(summ)}, FIT_REFUSAL_MAX,
           ("; VOID taus %s" % voids) if voids else "", "PASS" if c0 else "FAILED (the run is VOID, never an outcome)"))
    if not c0:
        return o, None
    s20 = summ[tau_str(0.20)]
    if tau_str(0.20) in voids:
        say("C1: tau 0.20 is VOID (fit refusals); no C1 verdict")
        return o, None
    v = c1_verdict(s20)
    say("C1 THE POWER WORDS (the INTERVAL decides; the point decides nothing): power(0.20) = %.4f (%d of %d), Wilson 95%% [%.4f, %.4f]"
        " against 0.80 -> %s" % (s20["power"], s20["k"], s20["n"], s20["lo"], s20["hi"], v))
    if v == "HELD":
        say("  the sentence's power clause stands with \"(measured design, plug-in null, iid structure)\" replacing \"(synthetic"
            " calibration ...)\"")
    elif v == "FAILED":
        say("  the clause is replaced by C2's tau80")
    else:
        say("  the clause keeps its D2 \"synthetic, unverified\" bracket with the measured point and interval added")
    t80 = tau80(summ)
    say("C2 tau80 (DESCRIPTIVE, no bar): %s; mean true 10pp-reversal pairs at tau80: %s"
        % (t80, "%.2f" % summ[t80]["reversals"] if t80 in summ else "n/a (no grid tau reaches 0.80)"))
    say("P1 power(0.20) = 0.70 [0.50, 0.88]: observed %.4f -> %s" % (s20["power"], band(s20["power"], P1)))
    say("P2 power(0.15) = 0.42 [0.22, 0.62]: observed %.4f -> %s" % (summ["0.15"]["power"], band(summ["0.15"]["power"], P2)))
    say("P3 power(0.25) = 0.88 [0.72, 0.97]: observed %.4f -> %s" % (summ["0.25"]["power"], band(summ["0.25"]["power"], P3)))
    say("P4 size at tau 0 = 0.010 [0.003, 0.025]: observed %.4f -> %s" % (summ["0.00"]["power"], band(summ["0.00"]["power"], P4)))
    say("P5 C1 (HELD 0.25, FAILED 0.45, UNDETERMINED 0.30): observed %s" % v)
    say("P6 tau80 = 0.25 (0.45; 0.20: 0.25; 0.30: 0.20; > 0.30: 0.10): observed %s" % t80)
    say("F1: %s" % ("FIRES: the STOP sentence's power clause is re-bracketed with tau80 (the STOP, G1's FAIL, LCB's F1 and the closed"
                    " line stand)" if v == "FAILED" else "does not fire (C1 is not FAILED)"))
    say("WORDS: power UNDER THE PLUG-IN NULL (a_m, s_m, delta_p fitted on the same TRAIN data) with iid interactions on the FIXED"
        " real regions; the two-group structure is not run (C1 conservative for it)")
    return o, v


# ── the modes ───────────────────────────────────────────────────────────────────────────────────────────────────────

def eval_sealed_sha(C, inp):
    """The sealed EVAL DB's FILE sha256 (never opened as a DB)."""
    e = inp["outcomes_manifest"]["dbs"]["eval_sealed"]
    p = os.path.join(C.lcb_root(), e["db"])
    return (C.file_sha256(p) if os.path.isfile(p) else "ABSENT"), e["sha256"]


def prepare(a):
    ST, A, C = load_tag(a.tag_root)
    for k in ("build_dir", "run_dir", "snapshot_id", "site_null"):
        if not getattr(a, k):
            refuse("--%s is required" % k.replace("_", "-"))
    inp = A.load_inputs(C.lcb_root())
    ev0 = eval_sealed_sha(C, inp)
    print("%s EVAL sealed DB sha256 before %s (manifest %s); never opened" % (TAG, ev0[0], ev0[1]))
    tree = A.load_tree(a.run_dir, os.path.join(a.build_dir, "snapshots.db"), a.snapshot_id)
    tree["emb_db"] = os.path.join(a.build_dir, "embeddings_cache.db")
    R, design = capture_design(ST, A, inp, tree, a.site_null)
    line, fm = identity_gate(ST, R, design)
    print("%s %s" % (TAG, line))
    params = null_params(fm)
    nm = design["n_models"]
    print("%s (2) null fit: M %d, informative %d, K %d; files n: %s; a_m [%.3f, %.3f], s_m [%.3f, %.3f], delta_p [%.3f, %.3f]"
          % (TAG, len(nm), design["Y"].shape[1], design["K"], dict(sorted({n: nm.count(n) for n in set(nm)}.items())),
             params["a"].min(), params["a"].max(), params["s"].min(), params["s"].max(), params["delta"].min(), params["delta"].max()))
    return ST, A, C, inp, design, params, ev0


def check_eval_after(C, inp, ev0):
    ev1 = eval_sealed_sha(C, inp)
    if ev1 != ev0:
        refuse("the EVAL sealed DB changed during the run (%s -> %s)" % (ev0[0], ev1[0]))
    print("%s EVAL sealed DB sha256 after %s: unchanged" % (TAG, ev1[0]))


def design_sha(design, params):
    h = hashlib.sha256()
    for arr in (design["Y"], design["reg"], params["a"], params["s"], params["delta"]):
        h.update(np.ascontiguousarray(arr, dtype=float).tobytes())
    h.update(json.dumps([design["fam"], design["fmt"], design["n_models"], design["K"]]).encode())
    return h.hexdigest()


def dry_run(a, procs):
    ST, A, C, inp, design, params, ev0 = prepare(a)
    t0 = time.perf_counter()
    rs = run_worlds([(0.20, w) for w in range(DRY_WORLDS)], a.tag_root, True, design, params, 1)
    per = (time.perf_counter() - t0) / DRY_WORLDS
    print("%s dry-run worlds (tau 0.20): %d rejections of %d, %d fit refusals (timing only; not an estimate)"
          % (TAG, sum(1 for r in rs if r.get("reject")), len(rs), sum(1 for r in rs if r["refused"])))
    print("%s %s" % (TAG, timing_gate(per, procs)))
    check_eval_after(C, inp, ev0)
    print("%s DRY RUN: nothing written" % TAG)
    return 0


def _store(out_dir):
    return os.path.join(out_dir, "worlds.jsonl"), os.path.join(out_dir, "meta.json")


def run(a, procs, out_dir=OUT_DIR):
    ST, A, C, inp, design, params, ev0 = prepare(a)
    os.makedirs(out_dir, exist_ok=True)
    wp, mp_ = _store(out_dir)
    meta = {"tag": TAG_NAME, "tag_commit": TAG_COMMIT, "blobs": TAG_BLOBS, "script_blob": _blob(os.path.abspath(__file__)),
            "taus": [tau_str(t) for t in TAUS], "W": W_PER_TAU, "B": B, "design_sha256": design_sha(design, params)}
    if os.path.exists(mp_):
        if json.load(open(mp_, encoding="utf-8")) != meta:
            refuse("%s differs from this run's meta (script, design or grid changed); a new directory is needed" % mp_)
    else:
        with open(mp_, "x", encoding="utf-8") as f:
            json.dump(meta, f, sort_keys=True)
    done = set()
    if os.path.exists(wp):
        for l in open(wp, encoding="utf-8"):
            r = json.loads(l)
            done.add((r["tau"], r["w"]))
    jobs = [(t, w) for t in TAUS for w in range(W_PER_TAU) if (tau_str(t), w) not in done]
    print("%s %d worlds done, %d to run at %d processes" % (TAG, len(done), len(jobs), min(procs, MAX_PROCS)))
    with open(wp, "a", encoding="utf-8") as f:
        def sink(r):
            f.write(json.dumps(r, sort_keys=True) + "\n")
            f.flush()
        run_worlds(jobs, a.tag_root, True, design, params, procs, sink=sink)
    check_eval_after(C, inp, ev0)
    return 0


def analyze(out_dir=OUT_DIR, meta_extra=None, out=print):
    wp, mp_ = _store(out_dir)
    outp = os.path.join(out_dir, "lcb_power_resim_outcome.txt")
    if os.path.exists(outp):
        refuse("%s exists; the outcome is write-once" % outp)
    if not (os.path.exists(wp) and os.path.exists(mp_)):
        refuse("no world store in %s" % out_dir)
    meta = json.load(open(mp_, encoding="utf-8"))
    worlds = {}
    for l in open(wp, encoding="utf-8"):
        r = json.loads(l)
        worlds[(r["tau"], r["w"])] = r
    want = {(tau_str(t), w) for t in TAUS for w in range(W_PER_TAU)}
    if set(worlds) != want:
        refuse("the store holds %d of %d worlds (missing %d): no outcome is written from a partial store"
               % (len(set(worlds) & want), len(want), len(want - set(worlds))))
    summ = summarise(list(worlds.values()))
    lines, v = render(summ, dict(meta, **(meta_extra or {})))
    with open(outp, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for l in lines:
        out(l)
    return v


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def selftest():
    import shutil
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        try:
            fn()
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %r" % (name, type(e).__name__, e))

    tagdir = tempfile.mkdtemp(prefix="lcbresim_tag_")
    fxdir = tempfile.mkdtemp(prefix="lcbresim_fx_")
    try:
        extract_tag(tagdir)
        ST, A, C = load_tag(tagdir, require_head=False)
        inp, problems = A.fixture_inputs(fxdir)
        tree, site = A.fixture_tree(os.path.join(fxdir, "t0"), inp, problems)
        R, design = capture_design(ST, A, inp, tree, site, b=199)
        fx_ident = ("%.3f" % R["g"]["T"], "%.4f" % R["g"]["p_T"])

        def blobs_and_head():
            assert all(_blob(os.path.join(tagdir, "tools", "analysis", "lcb_stage0", f)) == b for f, b in TAG_BLOBS.items())
            p = os.path.join(tagdir, "tools", "analysis", "lcb_stage0", "stats.py")
            data = open(p, "rb").read()
            open(p, "ab").write(b"# edit\n")
            try:
                load_tag(tagdir, require_head=False)
                raise AssertionError("an edited tag file was imported")
            except SystemExit as e:
                assert e.code == 2
            finally:
                open(p, "wb").write(data)
            try:
                load_tag(tagdir, require_head=True)       # an extraction is no checkout at the tag
                raise AssertionError("a non-tag checkout was admitted")
            except SystemExit as e:
                assert e.code == 2

        def capture_is_primary():
            assert design["Y"].shape == (R["data"]["M"], R["data"]["informative"]), design["Y"].shape
            assert len(design["fmt"]) == design["Y"].shape[1] and design["B"] == 199 and design["seed"] == C.PERM_SEED

        def identity():
            line, fm = identity_gate(ST, R, design, expected=fx_ident)
            assert line.endswith("-> REPRODUCED") and ("T = %s, p_T = %s (B 199)" % fx_ident) in line, line
            try:
                identity_gate(ST, R, design, expected=IDENTITY)       # the fixture is not the record
                raise AssertionError("a wrong identity was admitted")
            except SystemExit as e:
                assert e.code == 2
            bad = dict(design, reg=design["reg"][::-1].copy())       # a capture that is not the record path's object
            try:
                identity_gate(ST, R, bad, expected=fx_ident)
                raise AssertionError("a foreign object passed the identity gate")
            except SystemExit as e:
                assert e.code == 2

        _line, fm0 = identity_gate(ST, R, design, expected=fx_ident)
        params = null_params(fm0)

        def worlds_deterministic():
            r1 = world(ST, C, design, params, 0.20, 3, b=99)
            r2 = world(ST, C, design, params, 0.20, 3, b=99)
            r3 = world(ST, C, design, params, 0.20, 4, b=99)
            assert r1 == r2 and r1 != r3, (r1, r3)
            z = world(ST, C, design, params, 0.0, 0, b=99)
            assert z["tau"] == "0.00" and not z["refused"] and 0 < z["p_T"] <= 1
            assert set(r1) == {"tau", "w", "refused", "n_informative", "T", "p_T", "reject", "reversals"}
            assert world_seed(0.2, 3) == "LCB-POWER-RESIM:0.20:3" and world_seed(0.0, 0) == "LCB-POWER-RESIM:0.00:0"
            assert r1["reject"] == (r1["p_T"] <= 0.01)

        def simulation_model():
            # the probabilities are expit(a + s delta + G[m, region]); G = 0 at tau 0; the binomial uses each model's n
            G = np.zeros((len(design["n_models"]), design["K"]))
            P = true_probs(ST, params, design["reg"], G)
            want = ST.expit(params["a"][:, None] + params["s"][:, None] * params["delta"][None, :])
            assert np.allclose(P, want)
            G2 = np.zeros_like(G); G2[0, 1] = 5.0
            P2 = true_probs(ST, params, design["reg"], G2)
            assert np.all(P2[0, design["reg"] == 1] > P[0, design["reg"] == 1]) and np.allclose(P2[1:], P[1:])
            assert np.allclose(P2[0, design["reg"] != 1], P[0, design["reg"] != 1])
            # the binomial uses each model FILE's n: a design with files n = 1, 10, 4 gives Y on the grid k / n per row
            d3 = dict(design, n_models=[1, 10, 4] + list(design["n_models"][3:]))
            Y, _P = simulate(ST, d3, params, 0.20, 0)
            for i, n in enumerate([1, 10, 4]):
                assert np.allclose(Y[i] * n, np.round(Y[i] * n)), i
            assert np.any((Y[1] > 0) & (Y[1] < 1)) and set(np.unique(Y[0])) <= {0.0, 1.0}
            # reversal counting: two models, two regions: +0.2 in one, -0.2 in the other -> 1 pair
            Pm = np.array([[0.7, 0.7, 0.3, 0.3], [0.5, 0.5, 0.5, 0.5], [0.6, 0.6, 0.5, 0.5]])
            assert true_reversals(Pm, np.array([0, 0, 1, 1]), 2) == 1

        def parallel_equals_serial():
            jobs = [(0.15, 0), (0.15, 1)]
            s = sorted(run_worlds(jobs, tagdir, False, design, params, 1, b=49), key=lambda r: r["w"])
            p = sorted(run_worlds(jobs, tagdir, False, design, params, 2, b=49), key=lambda r: r["w"])
            assert s == p, (s, p)

        def timing():
            assert abs(projection(9.0, 20) - 15.0) < 1e-12 and abs(projection(9.0, 64) - 15.0) < 1e-12   # capped at 20
            assert timing_gate(36.0, 20).endswith("within the limit")                                # exactly 60 min
            try:
                timing_gate(36.1, 20)
                raise AssertionError("an over-limit projection was admitted")
            except SystemExit as e:
                assert e.code == 2

        def verdicts():
            assert wilson(336, 400)[0] >= 0.80 and wilson(335, 400)[0] < 0.80
            assert wilson(304, 400)[1] < 0.80 and wilson(305, 400)[1] >= 0.80
            mk = lambda k: dict(k=k, n=400, power=k / 400, lo=wilson(k, 400)[0], hi=wilson(k, 400)[1])
            assert (c1_verdict(mk(336)), c1_verdict(mk(304)), c1_verdict(mk(320))) == ("HELD", "FAILED", "UNDETERMINED")
            assert (c1_verdict(mk(335)), c1_verdict(mk(305))) == ("UNDETERMINED", "UNDETERMINED")

        def analyze_end_to_end():
            d = tempfile.mkdtemp(prefix="lcbresim_an_")
            try:
                wp, mp_ = _store(d)
                json.dump({"tag": TAG_NAME}, open(mp_, "w"))
                rows = []
                ks = {"0.00": 4, "0.15": 170, "0.20": 300, "0.25": 350, "0.30": 390}
                for t, k in ks.items():
                    for w in range(W_PER_TAU):
                        rows.append({"tau": t, "w": w, "refused": w >= 395 and t == "0.30", "reject": w < k, "p_T": 0.5,
                                     "reversals": 3 if t == "0.25" else 1, "n_informative": 500})
                with open(wp, "w") as f:
                    for r in rows[:-1]:
                        f.write(json.dumps(r) + "\n")
                try:
                    analyze(d, out=lambda s: None)
                    raise AssertionError("a partial store was analysed")
                except SystemExit as e:
                    assert e.code == 2
                with open(wp, "a") as f:
                    f.write(json.dumps(rows[-1]) + "\n")
                lines = []
                v = analyze(d, out=lines.append)
                t = "\n".join(lines)
                assert v == "FAILED", v
                assert "  tau 0.20: 300 of 400 reject -> power 0.7500" in t, t
                assert "C0 VALIDITY: identity REPRODUCED; size at tau 0 = 4 of 400 (bar <= 12)" in t and "-> PASS" in t, t
                assert "C1 THE POWER WORDS" in t and "against 0.80 -> FAILED" in t
                assert "C2 tau80 (DESCRIPTIVE, no bar): 0.25; mean true 10pp-reversal pairs at tau80: 3.00" in t, t
                assert "P1 power(0.20) = 0.70 [0.50, 0.88]: observed 0.7500 -> HELD" in t
                assert "P4 size at tau 0 = 0.010 [0.003, 0.025]: observed 0.0100 -> HELD" in t
                assert "F1: FIRES" in t
                summ_u = summarise([dict(r, reject=(r["w"] < 320) if r["tau"] == "0.20" else r["reject"]) for r in rows])
                lu, vu = render(summ_u, {})
                assert vu == "UNDETERMINED" and "F1: does not fire (C1 is not FAILED)" in lu and \
                    '  the clause keeps its D2 "synthetic, unverified" bracket with the measured point and interval added' in lu, lu
                summ_h = summarise([dict(r, reject=(r["w"] < 336) if r["tau"] == "0.20" else r["reject"]) for r in rows])
                lh, vh = render(summ_h, {})
                assert vh == "HELD" and any(l.startswith("  the sentence's power clause stands") for l in lh)
                try:
                    analyze(d, out=lambda s: None)
                    raise AssertionError("write-once not refused")
                except SystemExit as e:
                    assert e.code == 2
                # C0: size 13 of 400 VOIDS; > 20 fit refusals VOIDS that tau
                summ = summarise([dict(r, reject=(r["w"] < 13) if r["tau"] == "0.00" else r["reject"]) for r in rows])
                lines2, v2 = render(summ, {})
                assert v2 is None and "FAILED (the run is VOID, never an outcome)" in "\n".join(lines2)
                summ3 = summarise([dict(r, refused=(r["w"] < 21) if r["tau"] == "0.20" else r["refused"]) for r in rows])
                lines3, v3 = render(summ3, {})
                assert v3 is None and "VOID taus ['0.20']" in "\n".join(lines3), lines3
            finally:
                shutil.rmtree(d, ignore_errors=True)

        for nm, fn in [("the tag's blobs verified; an edited file or a non-tag checkout refused", blobs_and_head),
                       ("the captured object is the analysis's primary TRAIN object", capture_is_primary),
                       ("(1) identity gate: reproduced on the fixture's own numbers; the record's numbers and a foreign object refused", identity),
                       ("(3)-(4) worlds: deterministic per (tau, w), G1 on the registered stream", worlds_deterministic),
                       ("(3) the simulation model and the reversal count", simulation_model),
                       ("parallel worlds equal serial ones", parallel_equals_serial), ("the timing gate (60 min, 20 processes)", timing),
                       ("C1 at the registered Wilson observables (336 / 304 of 400)", verdicts),
                       ("--analyze end to end: partial refused, the lines by value, write-once, C0 VOIDs", analyze_end_to_end)]:
            case(nm, fn)
    finally:
        shutil.rmtree(tagdir, ignore_errors=True)
        shutil.rmtree(fxdir, ignore_errors=True)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("--selftest", "--dry-run", "--run", "--analyze"):
        g.add_argument(m, action="store_true")
    for k in ("--tag-root", "--build-dir", "--run-dir", "--snapshot-id", "--site-null"):
        ap.add_argument(k)
    ap.add_argument("--procs", type=int, default=MAX_PROCS)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.analyze:
        analyze()
        return 0
    if not a.tag_root:
        refuse("--tag-root (a checkout at %s) is required" % TAG_NAME)
    if a.procs < 1 or a.procs > MAX_PROCS:
        refuse("--procs %d outside [1, %d]" % (a.procs, MAX_PROCS))
    return dry_run(a, a.procs) if a.dry_run else run(a, a.procs)


if __name__ == "__main__":
    sys.exit(main())
