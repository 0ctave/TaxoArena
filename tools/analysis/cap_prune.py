"""CAP-PRUNE (registered 2026-09-18 in docs/judge_v2_program.md L6159-L6232, commit e803cf4, BEFORE any code or
call).  ZERO judge calls, ZERO constructions, NEVER a gate: a post-hoc readout of CAP-GATE-POSTHOC's 69 split sites
on the anchor-free tree af/seed_42.  First printed line = the pool of record (p2dca21ab5f4ef3ae), which is SCORED
NOWHERE here.

  python tools/analysis/cap_prune.py --selftest      # synthetic data only, opens NO database: a planted site that
                                                     #   survives both columns, one that fails its own null, one that
                                                     #   fails held-out; the scoring rules on planted counts
  python tools/analysis/cap_prune.py --dry-run       # pool id, artefact sha256s, the 69 / 16 / 5,602 / 2,193 counts
                                                     #   asserted, per-site n_train / n_heldout; NO gain computed
  python tools/analysis/cap_prune.py --run           # the readout; write-once to
         [--reps 200] [--boot 500]                   #   experiment_results/anchorfree/cap_prune_outcome.txt and
         [--out ...] [--sites-csv ...]               #   experiment_results/anchorfree/cap_prune_sites.csv (69 rows)

RULE 7 WINDOW.  --dry-run and --run open mmlu_pro_dataset_cache_v2.db (mode=ro: eval_results keys, reserved_pool
rows of the tree's own split p8a29d8f3ff75aa55) and embeddings_cache.db (mode=ro).  snapshots.db is NOT opened (the
tree is read from its dag_snapshots.jsonl on disk, as CAP-GATE-POSTHOC and the checker read it); the registration's
"reads snapshots.db" is therefore satisfied vacuously, but the night chain's builds WRITE reserved_pool rows into the
mmlu_pro cache, so both modes run ONLY in window W2, never beside a construction or a site null.  --selftest opens
nothing.

QUESTION (registration L6160-L6174).  CAP-GATE-POSTHOC found that a capability gate accepts a DIFFERENT set from the
geometric certificate at every threshold; its t = 0 line is not a zero line (the checker's within-site null reads a
LOMO median of -0.54 / 1000, -0.93 below n = 150); on the tree's own held-out side minus p2dca (2,193 q) the trunk
replicates and the two strongest depth-4 sites flip sign.  Claim under test (the lens's): a capability rule that must
REPLICATE out of sample as a PRUNE (keep a site iff its gain beats its own train-side null AND is positive held-out)
keeps only the trunk, so the "different sites" the gate accepts are small, deep sites whose gains do not replicate,
and the capability-gated construction line can be closed at zero builds.

INPUTS (read-only; sha256 printed).  experiment_results/anchorfree/af/seed_42 (dag_snapshots.jsonl, gate_ids.json,
diagnostics/run_manifest.json, validation/*.csv), experiment_results/anchorfree/site_null_af_s42.csv (the 69 sites,
16 certified at cert_site_p95), experiment_results/anchorfree/cap_gate_posthoc_sites.csv (the reproduction target),
the keyed rows of mmlu_pro_dataset_cache_v2.db (free_tests_f4_f7.keyed_questions: 46 models, >= 95 % coverage,
Meta-Llama-3-70B-Instruct excluded, mmlu_pro <-> eval joined by the OPTIONS key, 10,925 keyed questions).

SITES, MEMBERSHIP, TRAIN-SIDE GAIN: cap_gate_posthoc.py's own code path, IMPORTED (load_tree, sites_of, scored_set,
route_members, site_members, site_gains, boot_ci), not re-implemented.  A site = one accepted split = a site-null
row; membership by nearest-leaf routing of the first-256 slice (the flatLeaf rule); a question belongs to a site iff
the site is on its leaf's ancestor chain, its child = the next node down.  Train side = keyed AND not in the tree's
own pool p8a29d8f3ff75aa55 AND not in p2dca = 5,602 q (asserted).  Held-out side = keyed AND in p8a29 AND not in
p2dca = 2,193 q (asserted): questions the construction never saw and the arena pool does not contain.

INSTRUMENT (registration L6188-L6197), per site s of the 69, every gain LOMO key-only Brier x 1000:
  (1) g_train(s)   = mean over the site's train-side members of g_lomo (site_gains: parent LOO mean vs child LOO
                     mean, the child's offset fit on 45 models and scored on the 46th).  Asserted to reproduce
                     cap_gate_posthoc_sites.csv's g_lomo (and g_in) for all 69 sites to 4 dp BEFORE anything else is
                     computed; the run refuses otherwise.
  (2) null_p95(s)  = the 95th percentile of g_train under the within-site null: the site's train members randomly
                     re-assigned to its children at the observed child sizes (numpy Generator seed 42, one stream in
                     site order; rng.permutation of the child-index vector, exactly the checker's relabelling),
                     --reps >= 200; the null median and p(null >= observed) printed beside.
  (3) g_heldout(s) = the same LOMO gain on the site's held-out members with the cells FIT on the train members (no
                     LOO: parent = train mean, child = train child mean, an empty child falls back to the parent; the
                     LOMO offset fit on the other 45 models' train-side child-parent differences) and SCORED on the
                     held-out questions: free_tests_f4_f7.loo_imp's `fit` design, asserted equal to loo_imp(fit =
                     train members) for the in-roster part; the checker's heldout_gains.  Question bootstrap of the
                     site mean, --boot >= 500, Generator seed 42, percentile 2.5 / 97.5 (plug-in on the per-question
                     values, CAP-GATE's convention).
  KEEP RULE (the PRUNE): keep s iff g_train(s) > null_p95(s) AND g_heldout(s) > 0.  Never a gate: nothing here is
  read by any construction; no snapshot, config or artefact is modified.

READOUTS (C1, C2) and SCORING, exactly as registered (L6198-L6214):
  C1  survivor count under the keep rule; null_p95 and g_heldout written per site for all 69 (denominator 69).
  C2  Jaccard between the kept set and the certified 16 (denominator: their union), with the joint count.
  P1  4-6 survivors of 69 (the plan's A7).            HELD iff 4 <= survivors <= 6.
  P2  Jaccard ~0.25, scored as [0.15, 0.35].          HELD iff 0.15 <= J <= 0.35.
  R1  registrar's blind addition: the trunk's four sites (root n00000001, the two depth-1 sites, n00000163) all kept.
  R2  registrar's blind addition: no kept site with n_train < 150.
  FALSIFIER  survivors <= 4: the capability-gated construction line closes at zero builds.  At exactly 4, P1 is HELD
             and the falsifier FIRES, both as written; the consequence is the falsifier's.  Above 6 the plan's claim
             FAILS and the kept set (depths, overlap with the certificate) is the outcome.
  Beside, not scored: the kept set at the null MEDIAN instead of the p95; the kept set's depth distribution; the
  Spearman of g_train with g_heldout and the medians of the null and held-out columns (continuity with the
  checker's -0.54 / +0.45).
  Both conventions do not apply (no verdicts read); wrong(established) does not apply (no order read).

The tree is STRUCTURAL EVIDENCE: nothing is judged, induced, promoted or handed to the arena.  F2-CLEAN caveat on
the train column: the split boundaries were CHOSEN on these questions; LOO removes a question from its cell mean,
not from the choice of the boundary.  The held-out column has no such caveat (its questions were never seen by the
construction), which is why the PRUNE requires it.
"""
import os, sys, csv, argparse, math, hashlib, time, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import cap_gate_posthoc as CG                       # noqa: E402  the code path of record (imported, not re-implemented)
import free_tests_f4_f7 as F                        # noqa: E402  keyed_questions, loo_imp
import anchor_free_readout as AFR                   # noqa: E402  full_vectors

POOL = pool_guard.MMLU_PRO_POOL                     # p2dca21ab5f4ef3ae: never scored here
RUN_DIR = "experiment_results/anchorfree/af/seed_42"
SITE_NULL = "experiment_results/anchorfree/site_null_af_s42.csv"
TARGET_CSV = "experiment_results/anchorfree/cap_gate_posthoc_sites.csv"
OUT_DEFAULT = os.path.join("experiment_results", "anchorfree", "cap_prune_outcome.txt")
SITES_DEFAULT = os.path.join("experiment_results", "anchorfree", "cap_prune_sites.csv")
EXPECT = dict(sites=69, cert=16, train=5602, heldout=2193)
REPS_MIN, BOOT_MIN = 200, 500
NULL_SEED, BOOT_SEED = 42, 42
REPRO_TOL = 5e-5                                    # "to 4 dp" on the x1000 Brier scale
TRUNK_LITERAL = "n00000164"                         # the fourth trunk site of record after the 2026-09-18 bracket (Concept #163 = node n00000164; the registration wrote n00000163)
TRUNK_BESIDE = "n00000163"                          # printed beside: the checker's scratch report names this id as the
                                                    # replicating depth-5 site (train +13.98 -> held-out +15.93)
P1_RANGE, P2_RANGE, FALSIFIER_MAX, SMALL_N = (4, 6), (0.15, 0.35), 4, 150


# ----------------------------------------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def artefact_shas():
    rd = os.path.join(ROOT, RUN_DIR)
    files = [os.path.join(rd, "dag_snapshots.jsonl"), os.path.join(rd, "gate_ids.json"),
             os.path.join(rd, "diagnostics", "run_manifest.json")]
    files += sorted(glob.glob(os.path.join(rd, "validation", "*.csv")))
    files += [os.path.join(ROOT, SITE_NULL), os.path.join(ROOT, TARGET_CSV)]
    out = []
    for p in files:
        if not os.path.exists(p):
            raise SystemExit("[CAP-PRUNE] missing input %s" % p)
        out.append((os.path.relpath(p, ROOT).replace("\\", "/"), sha256(p)))
    return out


def heldout_gains(Ytr, chtr, k, Yho, chho):
    """Cells FIT on the train members (no LOO), SCORED on held-out questions: the `fit` design of
    free_tests_f4_f7.loo_imp (asserted equal in --selftest and in --run for the in-roster part).
    Ytr (M x n_tr) 0/1, chtr (n_tr,) in 0..k-1; Yho (M x n_ho), chho (n_ho,).  Returns per-held-out-question
    in-roster and LOMO gains (Brier, positive = children predict better than the parent)."""
    Ytr = np.asarray(Ytr, dtype=np.float64); Yho = np.asarray(Yho, dtype=np.float64)
    M, n_tr = Ytr.shape
    if n_tr < 1 or Yho.shape[1] < 1 or M < 2:
        raise ValueError("heldout_gains needs >= 1 train member, >= 1 held-out member and >= 2 models")
    A = Ytr.mean(axis=1)                                            # parent train mean (M,)
    nc = np.bincount(chtr, minlength=k).astype(np.float64)
    C = np.zeros((M, k))
    for c in range(k):
        C[:, c] = Ytr[:, chtr == c].sum(axis=1)
    cm = np.where(nc[None, :] > 0, C / np.maximum(nc, 1)[None, :], A[:, None])   # child train mean; empty -> parent
    Bq = cm[:, chho]                                                # (M, n_ho)
    Aq = A[:, None]
    err_p = (Aq - Yho) ** 2
    g_in = (err_p - (Bq - Yho) ** 2).mean(axis=0)
    D = Bq - Aq
    delta = (D.sum(axis=0, keepdims=True) - D) / (M - 1)            # offset fit on the other M-1 models
    P = np.clip(Aq + delta, 0.0, 1.0)
    g_lomo = (err_p - (P - Yho) ** 2).mean(axis=0)
    return g_in, g_lomo


def null_lomo(Y, ch, k, reps, rng):
    """The within-site null: members relabelled into children of the same sizes (rng.permutation of the child-index
    vector), the site's mean LOMO gain x 1000 per rep."""
    out = np.empty(reps)
    for b in range(reps):
        chb = rng.permutation(ch)
        _, gl, _, _ = CG.site_gains(Y, chb, k)
        out[b] = 1000.0 * float(gl.mean())
    return out


def prune(rows, cert_ids, col="null_p95"):
    """Keep iff g_train > null column AND g_heldout > 0.  Returns (kept ids, joint, union size, jaccard)."""
    kept = {r["node_id"] for r in rows
            if not math.isnan(r["g_train"]) and not math.isnan(r[col]) and not math.isnan(r["g_heldout"])
            and r["g_train"] > r[col] and r["g_heldout"] > 0.0}
    joint = kept & set(cert_ids)
    union = kept | set(cert_ids)
    return kept, len(joint), len(union), (len(joint) / len(union)) if union else float("nan")


def score(n_kept, jacc, trunk_kept, small_kept):
    """The registered scoring; returns a list of (label, verdict, detail)."""
    p1 = P1_RANGE[0] <= n_kept <= P1_RANGE[1]
    p2 = (not math.isnan(jacc)) and P2_RANGE[0] <= jacc <= P2_RANGE[1]
    fires = n_kept <= FALSIFIER_MAX
    out = [("P1 (plan A7: 4-6 survivors of 69)", "HELD" if p1 else "FAILED", "survivors %d" % n_kept),
           ("P2 (Jaccard with the certified 16 in [0.15, 0.35])", "HELD" if p2 else "FAILED", "Jaccard %s" % ("n/a" if math.isnan(jacc) else "%.3f" % jacc)),
           ("R1 (registrar: the trunk's four sites all kept)", "HELD" if all(trunk_kept.values()) else "FAILED",
            ", ".join("%s %s" % (k, "kept" if v else "pruned") for k, v in trunk_kept.items())),
           ("R2 (registrar: no kept site with n_train < %d)" % SMALL_N, "HELD" if not small_kept else "FAILED",
            "kept with n_train < %d: %s" % (SMALL_N, sorted(small_kept) if small_kept else "none")),
           ("FALSIFIER (survivors <= 4: the capability-gated construction line closes at zero builds)",
            "FIRES" if fires else "does not fire", "survivors %d" % n_kept)]
    if n_kept == FALSIFIER_MAX:
        out.append(("NOTE (registrar, blind)", "", "exactly 4 survivors: P1 HELD and the falsifier FIRES, both as written; the consequence is the falsifier's"))
    if n_kept > P1_RANGE[1]:
        out.append(("NOTE (registration)", "", "above 6 survivors the plan's claim FAILS; the kept set's depths and its overlap with the certificate are the outcome; a construction arm would need its own registration and the author's go"))
    return out


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    """Synthetic only (no database).  Three planted sites, M = 20 models, 400 train + 120 held-out questions each:
      A  shared child shift on train AND held-out       -> g_train > null p95, g_heldout > 0     : KEPT
      B  identical children (no shift anywhere)         -> g_train inside its own null           : fails the null
      C  shift on train, REVERSED shift on held-out     -> g_train > null p95, g_heldout < 0     : fails held-out
    Also asserted: heldout_gains' in-roster part == free_tests_f4_f7.loo_imp(fit = train members, qs = held-out);
    the null relabelling preserves child sizes; the scoring rules at planted counts (3, 4, 5, 7 survivors)."""
    rng = np.random.default_rng(7)
    M, n_tr, n_ho, k = 20, 400, 120, 2
    base = rng.uniform(0.25, 0.75, M)
    ch_tr = (np.arange(n_tr) >= n_tr // 2).astype(int)
    ch_ho = (np.arange(n_ho) >= n_ho // 2).astype(int)

    def draw(ch, shift):
        p = np.clip(base[:, None] + np.where(ch[None, :] == 1, shift, -shift), 0, 1)
        return (rng.uniform(size=(M, len(ch))) < p).astype(float)
    plant = {"A": (draw(ch_tr, 0.15), draw(ch_ho, 0.15)), "B": (draw(ch_tr, 0.0), draw(ch_ho, 0.0)),
             "C": (draw(ch_tr, 0.15), draw(ch_ho, -0.15))}
    rows = []
    nrng = np.random.default_rng(NULL_SEED); brng = np.random.default_rng(BOOT_SEED)
    for sid, (Ytr, Yho) in plant.items():
        _, gl, _, _ = CG.site_gains(Ytr, ch_tr, k)
        nd = null_lomo(Ytr, ch_tr, k, REPS_MIN, nrng)
        chb = nrng.permutation(ch_tr)
        assert np.bincount(chb, minlength=k).tolist() == np.bincount(ch_tr, minlength=k).tolist(), "relabelling changed the child sizes"
        gi_ho, gl_ho = heldout_gains(Ytr, ch_tr, k, Yho, ch_ho)
        # equality with loo_imp's fit design (in-roster part)
        models = ["m%d" % i for i in range(M)]
        tr_ids = list(range(n_tr)); ho_ids = list(range(n_tr, n_tr + n_ho))
        G = {m: {**{q: int(Ytr[i, q]) for q in tr_ids}, **{q: int(Yho[i, q - n_tr]) for q in ho_ids}} for i, m in enumerate(models)}
        part = {**{q: int(ch_tr[q]) for q in tr_ids}, **{q: int(ch_ho[q - n_tr]) for q in ho_ids}}
        ref = F.loo_imp(part, ho_ids, models, G, fit=tr_ids)
        assert np.allclose(ref, gi_ho, atol=1e-12), "heldout_gains in-roster part != loo_imp(fit=train)"
        lo, hi = CG.boot_ci(gl_ho, BOOT_MIN, brng)
        rows.append(dict(node_id=sid, g_train=1000 * float(gl.mean()), null_median=float(np.median(nd)), null_p95=float(np.percentile(nd, 95)),
                         g_heldout=1000 * float(gl_ho.mean()), ho_lo=1000 * lo, ho_hi=1000 * hi, n_train=n_tr))
    byid = {r["node_id"]: r for r in rows}
    a, b, c = byid["A"], byid["B"], byid["C"]
    assert a["g_train"] > a["null_p95"] and a["g_heldout"] > 0, a
    assert b["g_train"] <= b["null_p95"], b
    assert c["g_train"] > c["null_p95"] and c["g_heldout"] < 0, c
    kept, joint, union, jacc = prune(rows, {"A", "C"})
    assert kept == {"A"} and joint == 1 and union == 2 and abs(jacc - 0.5) < 1e-12, (kept, joint, union, jacc)
    kept_med, _, _, _ = prune(rows, {"A", "C"}, col="null_median")
    assert "A" in kept_med and "C" not in kept_med, kept_med
    for r in rows:
        print("[SELFTEST] site %s: g_train %+.2f | null median %+.2f p95 %+.2f | g_heldout %+.2f [%+.2f, %+.2f] | %s"
              % (r["node_id"], r["g_train"], r["null_median"], r["null_p95"], r["g_heldout"], r["ho_lo"], r["ho_hi"],
                 "KEPT" if r["node_id"] in kept else "pruned"))
    # the scoring rules at planted counts
    def verdicts(n, j=0.25, trunk=True, small=False):
        s = score(n, j, {"root": trunk, "d1a": True, "d1b": True, TRUNK_LITERAL: True}, {"x"} if small else set())
        return {lab.split(" ")[0]: v for lab, v, _ in s if v}
    v3, v4, v5, v7 = verdicts(3), verdicts(4), verdicts(5), verdicts(7)
    assert v3["P1"] == "FAILED" and v3["FALSIFIER"] == "FIRES", v3
    assert v4["P1"] == "HELD" and v4["FALSIFIER"] == "FIRES", v4
    assert v5["P1"] == "HELD" and v5["FALSIFIER"] == "does not fire", v5
    assert v7["P1"] == "FAILED" and v7["FALSIFIER"] == "does not fire", v7
    assert verdicts(5, j=0.10)["P2"] == "FAILED" and verdicts(5, j=0.35)["P2"] == "HELD"
    assert verdicts(5, trunk=False)["R1"] == "FAILED" and verdicts(5, small=True)["R2"] == "FAILED"
    print("[SELFTEST] planted kept set {A} recovered (B fails its own null, C fails held-out); loo_imp(fit=train) equality OK; "
          "child sizes preserved under relabelling; scoring at 3/4/5/7 survivors OK (4: P1 HELD and falsifier FIRES). No database opened.")
    return 0


# ----------------------------------------------------------------------------------------------- data
def load_target():
    p = os.path.join(ROOT, TARGET_CSV)
    rows = [r for r in csv.DictReader(open(p, newline="", encoding="utf-8")) if r["tree"] == "af"]
    if len(rows) != EXPECT["sites"]:
        raise SystemExit("[CAP-PRUNE] %s carries %d af rows, expected %d" % (TARGET_CSV, len(rows), EXPECT["sites"]))
    return {r["node_id"]: dict(g_in=float(r["g_in"]), g_lomo=float(r["g_lomo"]), n_scored=int(r["n_scored"])) for r in rows}


def load_all(run):
    """Everything both modes share: pool id (first line), shas, tree, sites, keyed set, train and held-out sides,
    routed memberships.  Computes NO gain."""
    pid = pool_guard.assert_pool_of_record(POOL)
    print("reserved_pool_id=%s" % pid)                    # first line: the pool that is NEVER scored here
    print("mode=%s | CAP-PRUNE: zero judge calls, zero constructions, never a gate | tree %s (structural evidence only)"
          % ("RUN" if run else "DRY-RUN (no gain computed)", RUN_DIR))
    for rel, h in artefact_shas():
        print("sha256 %s  %s" % (h, rel))
    record_eval = set(pool_guard.eval_ids(pid))
    tree = CG.load_tree(RUN_DIR)
    sites, src = CG.sites_of(tree, SITE_NULL)
    n_cert = sum(1 for s in sites if s["cert"])
    m = tree["manifest"]
    print("tree: snapshot iteration %d | nodes %d leaves %d dim %d | anchorFree=%s | manifest seed %s pool %s train_size %s"
          % (tree["iteration"], len(tree["nodes"]), len(tree["leaves"]), tree["dim"], tree["anchor_free"], m.get("seed"), m.get("reserved_pool_id"), m.get("train_size")))
    print("sites: %s | certified (cert_site_p95) %d" % (src, n_cert))
    if len(sites) != EXPECT["sites"] or n_cert != EXPECT["cert"]:
        raise SystemExit("[CAP-PRUNE] expected %d sites / %d certified, found %d / %d" % (EXPECT["sites"], EXPECT["cert"], len(sites), n_cert))
    keyed = F.keyed_questions()
    models, G, cat, text, qs_all = keyed
    sc = CG.scored_set(keyed, tree, record_eval)
    own = CG.own_pool_eval_ids(sc["own_pool"])
    ho_all = [q for q in qs_all if q in own and q not in record_eval]
    print("roster=%d models (Meta-Llama-3-70B-Instruct excluded) | keyed questions=%d | pool of record eval ids=%d (scored nowhere)" % (len(models), len(qs_all), len(record_eval)))
    print("train side = keyed %d - in own pool %s (%d) - in pool of record (%d; of which also in own pool %d) = %d | asserted %d"
          % (sc["n_keyed"], sc["own_pool"], sc["n_in_own"], sc["n_in_record"], sc["n_own_and_record"], len(sc["qs"]), EXPECT["train"]))
    print("held-out side = keyed AND in own pool %s (%d) - in pool of record (%d) = %d | asserted %d"
          % (sc["own_pool"], sc["n_in_own"], sc["n_own_and_record"], len(ho_all), EXPECT["heldout"]))
    if len(sc["qs"]) != EXPECT["train"] or len(ho_all) != EXPECT["heldout"]:
        raise SystemExit("[CAP-PRUNE] train / held-out counts %d / %d differ from the registered %d / %d" % (len(sc["qs"]), len(ho_all), EXPECT["train"], EXPECT["heldout"]))
    if set(sc["qs"]) & set(ho_all):
        raise SystemExit("[CAP-PRUNE] train and held-out sides overlap")
    if (set(sc["qs"]) | set(ho_all)) & record_eval:
        raise SystemExit("[CAP-PRUNE] the pool of record leaked into a scored side")
    vec = AFR.full_vectors([text[q] for q in sc["qs"] + ho_all])
    qs_tr, leaf_tr = CG.route_members(tree, keyed, sc["qs"], vec)
    qs_ho, leaf_ho = CG.route_members(tree, keyed, ho_all, vec)
    print("routed to a leaf: train %d of %d (no embedding %d) | held-out %d of %d (no embedding %d) | leaves used train %d held-out %d of %d"
          % (len(qs_tr), len(sc["qs"]), len(sc["qs"]) - len(qs_tr), len(qs_ho), len(ho_all), len(ho_all) - len(qs_ho),
             len(set(leaf_tr)), len(set(leaf_ho)), len(tree["leaves"])))
    if len(qs_tr) != EXPECT["train"] or len(qs_ho) != EXPECT["heldout"]:
        raise SystemExit("[CAP-PRUNE] routed counts %d / %d differ from %d / %d (a keyed question without an embedding)" % (len(qs_tr), len(qs_ho), EXPECT["train"], EXPECT["heldout"]))
    mem = {}
    for s in sites:
        mtr, ctr, kids = CG.site_members(tree, s, qs_tr, leaf_tr)
        mho, cho, _ = CG.site_members(tree, s, qs_ho, leaf_ho)
        mem[s["node_id"]] = (mtr, ctr, mho, cho, kids)
    root = [s["node_id"] for s in sites if s["depth"] == 0]
    d1 = [s["node_id"] for s in sites if s["depth"] == 1]
    if len(root) != 1 or len(d1) != 2:
        raise SystemExit("[CAP-PRUNE] expected 1 root site and 2 depth-1 sites, found %s / %s" % (root, d1))
    ids = {s["node_id"] for s in sites}
    if TRUNK_LITERAL not in ids:
        raise SystemExit("[CAP-PRUNE] the registration's trunk site %s is not one of the 69 sites" % TRUNK_LITERAL)
    trunk = [root[0]] + d1 + [TRUNK_LITERAL]
    print("trunk (registration, literal): root %s, depth-1 %s, %s | beside (not scored): %s%s"
          % (root[0], " ".join(d1), TRUNK_LITERAL, TRUNK_BESIDE, "" if TRUNK_BESIDE in ids else " (not a site)"))
    if len(mem[root[0]][0]) != EXPECT["train"] or len(mem[root[0]][2]) != EXPECT["heldout"]:
        raise SystemExit("[CAP-PRUNE] root membership %d / %d differs from %d / %d" % (len(mem[root[0]][0]), len(mem[root[0]][2]), EXPECT["train"], EXPECT["heldout"]))
    return dict(pid=pid, tree=tree, sites=sites, models=models, G=G, mem=mem, trunk=trunk, n_train=len(qs_tr), n_heldout=len(qs_ho))


# ----------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="pool id, shas, the 69 / 16 / 5,602 / 2,193 counts, per-site n; NO gain")
    ap.add_argument("--run", action="store_true", help="the readout; write-once")
    ap.add_argument("--selftest", action="store_true", help="synthetic data only; opens no database")
    ap.add_argument("--reps", type=int, default=REPS_MIN, help="within-site null reps (>= %d)" % REPS_MIN)
    ap.add_argument("--boot", type=int, default=BOOT_MIN, help="held-out question bootstrap B (>= %d)" % BOOT_MIN)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--sites-csv", default=SITES_DEFAULT)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.dry_run or a.run):
        raise SystemExit("[CAP-PRUNE] refused: pass --dry-run (counts only), --run (the readout) or --selftest; see the docstring")
    if a.run and a.reps < REPS_MIN:
        raise SystemExit("[CAP-PRUNE] --reps must be >= %d (registered)" % REPS_MIN)
    if a.run and a.boot < BOOT_MIN:
        raise SystemExit("[CAP-PRUNE] --boot must be >= %d (registered)" % BOOT_MIN)
    op = os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out
    sp = os.path.join(ROOT, a.sites_csv) if not os.path.isabs(a.sites_csv) else a.sites_csv
    if a.run:
        for p in (op, sp):
            if os.path.exists(p):
                raise SystemExit("[CAP-PRUNE] write-once: %s exists; the outcome of record is not overwritten" % p)

    t0 = time.time()
    D = load_all(a.run)
    sites, models, G, mem = D["sites"], D["models"], D["G"], D["mem"]
    target = load_target()

    if a.dry_run:
        print("")
        print("site list (node, label, depth, k, n_site, n_train, n_heldout, children train / held-out, cert, target g_lomo present):")
        for s in sites:
            mtr, ctr, mho, cho, kids = mem[s["node_id"]]
            print("    %-10s %-24s d%d k%d n_site %5d n_train %5d n_heldout %4d  %-18s %-18s %s %s"
                  % (s["node_id"], s["label"][:24], s["depth"], s["k"], s["n_site"], len(mtr), len(mho),
                     [int((ctr == c).sum()) for c in range(len(kids))], [int((cho == c).sum()) for c in range(len(kids))],
                     "CERT" if s["cert"] else "-", "target" if s["node_id"] in target else "NO-TARGET"))
        print("")
        print("[CAP-PRUNE] dry-run complete (%.0f s): %d sites, %d certified, train %d, held-out %d; median n_train %d, median n_heldout %d; no gain computed, nothing written. The readout needs --run (window W2)."
              % (time.time() - t0, len(sites), sum(1 for s in sites if s["cert"]), D["n_train"], D["n_heldout"],
                 int(np.median([len(mem[s["node_id"]][0]) for s in sites])), int(np.median([len(mem[s["node_id"]][2]) for s in sites]))))
        return 0

    # ---- stage A: the train-side column, asserted against CAP-GATE-POSTHOC's file before anything else
    rows = []
    worst = 0.0
    for s in sites:
        mtr, ctr, mho, cho, kids = mem[s["node_id"]]
        k = len(kids)
        Y = np.array([[G[mm][q] for q in mtr] for mm in models], dtype=np.float64)
        g_in, g_lomo, _, _ = CG.site_gains(Y, ctr, k)
        r = dict(node_id=s["node_id"], label=s["label"], depth=s["depth"], k=k, n_site=s["n_site"], n_train=len(mtr), n_heldout=len(mho),
                 n_children_train=[int((ctr == c).sum()) for c in range(k)], n_children_heldout=[int((cho == c).sum()) for c in range(k)],
                 cert=bool(s["cert"]), sep=s["sep"], site_p95=s["p95"],
                 g_in_train=1000 * float(g_in.mean()), g_train=1000 * float(g_lomo.mean()),
                 g_train_target=target[s["node_id"]]["g_lomo"], _Y=Y, _ctr=ctr, _k=k)
        t = target[s["node_id"]]
        d = max(abs(r["g_train"] - t["g_lomo"]), abs(r["g_in_train"] - t["g_in"]))
        worst = max(worst, d)
        if t["n_scored"] != len(mtr) or d > REPRO_TOL:
            raise SystemExit("[CAP-PRUNE] REFUSED: site %s does not reproduce %s (n %d vs %d; g_lomo %.6f vs %.6f; g_in %.6f vs %.6f; tol %g)"
                             % (s["node_id"], TARGET_CSV, len(mtr), t["n_scored"], r["g_train"], t["g_lomo"], r["g_in_train"], t["g_in"], REPRO_TOL))
        rows.append(r)
    print("[CAP-PRUNE] stage A: g_train reproduces %s for all %d sites (max |diff| %.2e on g_lomo and g_in, tol %g) in %.0f s"
          % (TARGET_CSV, len(rows), worst, REPRO_TOL, time.time() - t0))

    # ---- stage B: the within-site null (seed 42, one stream in site order)
    t1 = time.time()
    nrng = np.random.default_rng(NULL_SEED)
    for r in rows:
        nd = null_lomo(r["_Y"], r["_ctr"], r["_k"], a.reps, nrng)
        r.update(null_median=float(np.median(nd)), null_p95=float(np.percentile(nd, 95)), null_p=float((nd >= r["g_train"]).mean()))
    print("[CAP-PRUNE] stage B: within-site null, %d reps per site, seed %d, %.0f s" % (a.reps, NULL_SEED, time.time() - t1))

    # ---- stage C: the held-out column (cells fit on train, scored on the tree's own held-out side minus p2dca)
    t2 = time.time()
    brng = np.random.default_rng(BOOT_SEED)
    for r, s in zip(rows, sites):
        mtr, ctr, mho, cho, kids = mem[s["node_id"]]
        if len(mho) < 1:
            r.update(g_in_heldout=float("nan"), g_heldout=float("nan"), ho_lo=float("nan"), ho_hi=float("nan"), note="no held-out member")
            continue
        Yh = np.array([[G[mm][q] for q in mho] for mm in models], dtype=np.float64)
        gi_ho, gl_ho = heldout_gains(r["_Y"], ctr, r["_k"], Yh, cho)
        part = {**{q: int(c) for q, c in zip(mtr, ctr)}, **{q: int(c) for q, c in zip(mho, cho)}}
        ref = F.loo_imp(part, mho, models, G, fit=mtr)                 # F6's fit design on this site
        if not np.allclose(ref, gi_ho, atol=1e-12):
            raise SystemExit("[CAP-PRUNE] %s: held-out in-roster gain differs from loo_imp(fit=train)" % s["node_id"])
        lo, hi = CG.boot_ci(gl_ho, a.boot, brng)
        r.update(g_in_heldout=1000 * float(gi_ho.mean()), g_heldout=1000 * float(gl_ho.mean()), ho_lo=1000 * lo, ho_hi=1000 * hi,
                 note="" if len(mho) >= 2 else "single held-out member: no interval")
    print("[CAP-PRUNE] stage C: held-out gains with B=%d question bootstrap, seed %d, %.0f s" % (a.boot, BOOT_SEED, time.time() - t2))

    # ---- stage D: the PRUNE, the criteria, the scoring
    cert_ids = {r["node_id"] for r in rows if r["cert"]}
    kept, joint, union, jacc = prune(rows, cert_ids, col="null_p95")
    kept_med, joint_med, union_med, jacc_med = prune(rows, cert_ids, col="null_median")
    for r in rows:
        r["kept"] = r["node_id"] in kept
        r["kept_at_median"] = r["node_id"] in kept_med
    trunk_kept = {t: (t in kept) for t in D["trunk"]}
    small_kept = {r["node_id"] for r in rows if r["kept"] and r["n_train"] < SMALL_N}
    verdicts = score(len(kept), jacc, trunk_kept, small_kept)

    gt = np.array([r["g_train"] for r in rows]); gh = np.array([r["g_heldout"] for r in rows])
    nm = np.array([r["null_median"] for r in rows]); np95 = np.array([r["null_p95"] for r in rows])
    rs, nn = CG.spearman(gt, gh)
    L = ["=== CAP-PRUNE readout (registered 2026-09-18, commit e803cf4; zero judge calls, zero constructions, never a gate) ===",
         "  reserved_pool_id=%s (scored nowhere) | tree %s (structural evidence only) | roster %d models" % (D["pid"], RUN_DIR, len(models)),
         "  sites 69 (site null %s) | certified 16 | train side %d q (keyed, own pool p8a29 and p2dca removed) | held-out side %d q (keyed, in p8a29, p2dca removed)"
         % (SITE_NULL, D["n_train"], D["n_heldout"]),
         "  instrument: g_train = CAP-GATE-POSTHOC's LOMO gain (reproduced to 4 dp, max |diff| %.2e); null = members relabelled into children of the same sizes, %d reps, seed %d; g_heldout = cells fit on train, scored held-out, B=%d bootstrap, seed %d; all gains LOMO key-only Brier x 1000"
         % (worst, a.reps, NULL_SEED, a.boot, BOOT_SEED),
         "  KEEP RULE: g_train > null_p95 AND g_heldout > 0",
         "",
         "  %-10s %-22s d k n_site n_trn n_ho cert |  g_train  null_med null_p95  p_null | g_heldout [   95%% CI    ] | kept kept@med" % ("node", "label")]
    for r in rows:
        L.append("  %-10s %-22s %d %d %6d %5d %4d %4s | %+8.2f %+8.2f %+8.2f  %.3f | %+9.2f [%+7.2f, %+7.2f] | %-4s %s%s"
                 % (r["node_id"], r["label"][:22], r["depth"], r["k"], r["n_site"], r["n_train"], r["n_heldout"], "CERT" if r["cert"] else "-",
                    r["g_train"], r["null_median"], r["null_p95"], r["null_p"], r["g_heldout"], r["ho_lo"], r["ho_hi"],
                    "KEPT" if r["kept"] else ".", "KEPT" if r["kept_at_median"] else ".", ("  (%s)" % r["note"]) if r.get("note") else ""))
    L.append("")
    L.append("=== C1: survivors under the keep rule: %d of 69 (both columns written for all 69 above and in %s) ===" % (len(kept), a.sites_csv))
    L.append("  kept: %s" % (", ".join("%s(d%d,n%d,%s)" % (r["node_id"], r["depth"], r["n_train"], "C" if r["cert"] else "-") for r in rows if r["kept"]) or "none"))
    by_d = {}
    for r in rows:
        by_d.setdefault(r["depth"], [0, 0, 0])
        by_d[r["depth"]][0] += 1; by_d[r["depth"]][1] += int(r["cert"]); by_d[r["depth"]][2] += int(r["kept"])
    L.append("  kept set by depth (sites | certified | kept): " + " | ".join("d%d %d/%d/%d" % (d, *by_d[d]) for d in sorted(by_d)))
    L.append("  trunk (registration, literal: root, the two depth-1 sites, %s): %s" % (TRUNK_LITERAL, ", ".join("%s %s" % (t, "KEPT" if v else "pruned") for t, v in trunk_kept.items())))
    rb = next((r for r in rows if r["node_id"] == TRUNK_BESIDE), None)
    if rb is not None:
        L.append("  beside, not scored: %s (d%d, n_train %d, %s) g_train %+.2f null_p95 %+.2f g_heldout %+.2f -> %s  [the checker's scratch report names this id as the replicating depth-5 site; the registration's sentence says %s]"
                 % (TRUNK_BESIDE, rb["depth"], rb["n_train"], "CERT" if rb["cert"] else "-", rb["g_train"], rb["null_p95"], rb["g_heldout"], "KEPT" if rb["kept"] else "pruned", TRUNK_LITERAL))
    L.append("  kept sites with n_train < %d: %s" % (SMALL_N, sorted(small_kept) if small_kept else "none"))
    L.append("  legs separately: g_train > null_p95 at %d of 69 | g_heldout > 0 at %d of 69 | both %d | g_train > null_median at %d"
             % (int((gt > np95).sum()), int(np.nansum(gh > 0)), len(kept), int((gt > nm).sum())))
    L.append("=== C2: Jaccard(kept, certified 16) = %s (joint %d, union %d) ===" % ("n/a" if math.isnan(jacc) else "%.3f" % jacc, joint, union))
    L.append("  beside, not scored: kept at the null MEDIAN instead of the p95: %d of 69, joint %d, union %d, Jaccard %s"
             % (len(kept_med), joint_med, union_med, "n/a" if math.isnan(jacc_med) else "%.3f" % jacc_med))
    L.append("  continuity with the checker (scratch, 2026-09-17): null median over sites %+.2f (checker -0.54) | null median below n_train 150: %+.2f | held-out median %+.2f (checker +0.45) | Spearman(g_train, g_heldout) %+.3f (checker +0.21) | median n_heldout %d (checker 79)"
             % (float(np.median(nm)), float(np.median([r["null_median"] for r in rows if r["n_train"] < SMALL_N])) if any(r["n_train"] < SMALL_N for r in rows) else float("nan"),
                float(np.nanmedian(gh)), rs, int(np.median([r["n_heldout"] for r in rows]))))
    L.append("")
    L.append("=== scoring (registration L6202-L6214) ===")
    for lab, v, det in verdicts:
        L.append("  %-78s %-14s %s" % (lab, v, det))
    L.append("")
    L.append("  F2-CLEAN caveat (train column only): the split boundaries were CHOSEN on the train-side questions; LOO removes a question from its cell mean, not from the choice of the boundary. The held-out column's questions were never seen by the construction.")
    L.append("  Structural evidence only: nothing judged, induced, promoted or handed to the arena; no snapshot, config or artefact modified; the keep rule is a readout, never an admission gate (FRAMEWORK L53).")
    L.append("  runtime %.0f s total" % (time.time() - t0))
    txt = "\n".join(L)
    print(txt)
    os.makedirs(os.path.dirname(op), exist_ok=True)
    with open(op, "x", encoding="utf-8") as f:                      # 'x': write-once at the OS level too
        f.write(txt + "\n")
    cols = ["node_id", "label", "depth", "k", "n_site", "n_train", "n_heldout", "n_children_train", "n_children_heldout", "cert", "sep", "site_p95",
            "g_in_train", "g_train", "g_train_target", "null_median", "null_p95", "null_p", "g_in_heldout", "g_heldout", "ho_lo", "ho_hi", "kept", "kept_at_median", "note"]
    with open(sp, "x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})
    print("[CAP-PRUNE] outcome written to %s | per-site table (69 rows) written to %s" % (op, sp))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
