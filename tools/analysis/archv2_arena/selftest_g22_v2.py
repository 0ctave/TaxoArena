"""Selftest for the rulings of 83f431b (docs/judge_v2_program.md L15341-L15365), called from selftest_g22. Synthetic
worlds only; single process; every new branch executed; every mutant must be KILLED (the check it targets must fail
while the mutant is active). Mutant switches are module-level MUTANT variables, None in every real run, set and
restored here only."""
import hashlib
import json
import os

import numpy as np

from . import cert, data, design, g22, g23, report, synth
from . import verdict_model as vmod
from .report import HITS
from .streams import Streams

GOLDEN_V1_TEXT_SHA256 = "f9ff45c78a4f0249a501b4e0daa5b82870d051fd0081e9f5525d2416fc16e0c3"   # computed at 4c2d2b5
GOLDEN_V1_VM_DIGEST = "f0dc035085378c4ddffb5410b91d82ca9c0d384c8f733c3644ea1747bb08de29"
GOLDEN_SPLIT_H1_SHA256 = "0b0310668e58e3fc2aeb5d238423649cc0c93f96107141c4276ccd587977d84d"  # fixture, ARCHV2-G22-V2-HALF-1, at ca84e44


def board_world(seed, G=10, M=12, qn=150, per_pair=8, eps_sd=0.34, w_sd=0.32, beta=4.74):
    """A board-shaped synthetic world (after the arena-specialist's DEV diag_beta_synth.py): the true judge's total effect
    u_true = beta * (skill - anchor mean) + eps_m + w_gm; the fit sees MODEL-LEVEL keyacc from the key. Returns the v2
    observations and the ORACLE PROJECTION of u_true (centred per anchor) on the centred model-level keyacc."""
    skill = np.linspace(0.18, 0.91, M)
    rng = np.random.default_rng(seed)
    K = (rng.random((G, qn, M)) < skill[None, None, :]).astype(int)
    KA = design.model_level_keyacc(K.sum(axis=1), np.full(G, qn), np.ones((G, M), bool))
    eps = rng.normal(0, eps_sd, M); w = rng.normal(0, w_sd, (G, M))
    u_true = beta * (skill - skill.mean())[None, :] + eps[None, :] + w
    uc = u_true - u_true.mean(axis=1, keepdims=True)
    oracle = float((uc * KA).sum() / (KA * KA).sum())
    g, a, b_, q = [], [], [], []
    for gi in range(G):
        for i in range(M):
            for j in range(i + 1, M):
                for _ in range(per_pair):
                    x, y = (i, j) if rng.random() < .5 else (j, i)
                    g.append(gi); a.append(x); b_.append(y); q.append(rng.integers(qn))
    g, a, b_, q = map(np.array, (g, a, b_, q))
    ka_, kb_ = K[g, q, a], K[g, q, b_]
    t = np.where(ka_ != kb_, 0, np.where(rng.random(g.size) < .4, 1, 2))
    S = dict(g=g, a=a, b=b_, t=t, kd=(ka_ - kb_).astype(float), dl=rng.normal(0, 1, g.size))
    tv = vmod.VerdictModel(G, M); tv.kappa, tv.pi, tv.lam = 1.64, 0.18, 0.16
    tv.gamma = np.log(np.array([0.105, 0.663, 0.459])); tv.u = u_true
    sim = tv.simulate(S, rng, mode="fixed")
    ms = [dict(g=int(g[k]), a=int(a[k]), b=int(b_[k]), t=int(t[k]), kd_ab=float(S["kd"][k]), dl_ab=float(S["dl"][k]),
               v1=vmod.Y_VOTE[int(sim["y1"][k])], v2=vmod.Y_VOTE[int(sim["y2"][k])]) for k in range(g.size)]
    return dict(O=vmod.obs_v2_from(vmod.obs_from_matches(ms), KA), oracle=oracle, G=G, M=M)


def _loads(path):
    try:
        g22.load_token(path, need_v2=True)
        return True
    except SystemExit:
        return False


def _refuses(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def mutant_killed(mod, name, fn):
    saved = mod.MUTANT
    mod.MUTANT = name
    try:
        ok = bool(fn())
    except SystemExit:
        ok = False
    finally:
        mod.MUTANT = saved
    return not ok


def v1_golden(check, v1_out, v1_tok, witness_before):
    h = hashlib.sha256(v1_out.text().encode("utf-8")).hexdigest()
    check(h == GOLDEN_V1_TEXT_SHA256 and v1_tok["vm_digest"] == GOLDEN_V1_VM_DIGEST,
          "v1 BYTE-IDENTICAL: the registered v1 validity readout on the fixture hashes to the golden computed at 4c2d2b5"
          " (%s; vm digest %s)" % (h[:16], v1_tok["vm_digest"][:16]))
    d1 = data.WITNESS.get("validity.v1_path", 0) - witness_before.get("validity.v1_path", 0)
    d2 = data.WITNESS.get("validity.v2_path", 0) - witness_before.get("validity.v2_path", 0)
    check(d1 > 0 and d2 == 0, "v1 EXECUTION WITNESS: the edited validity_leg ran its v1 path (%d) and never its v2 path (%d)"
          % (d1, d2))


def run(tmp, sb, check, expect_exit):
    print("--- rulings of 83f431b: fresh-judge v2, BBH / MuSR missing, called residue, ties as a set, (d) under Holm, nu ---")
    # ------------------------------------------------------------------ the v2 model: beta, sigma_eps_LOMO, simulation
    W = synth.make_world(seed=13, n_models=6, per_pair=40, u_sd=0.8, q_per_anchor=50, beta=4.0, kappa=1.5)
    b = W["board"]
    anchors, S, obs, meta = g22.board_matrix(b, floor=200)
    KA = g22.keyacc_matrix(b, anchors)
    # RULING A (4b25059): keyacc is MODEL-LEVEL (pooled over all anchors' judged questions, centred per anchor)
    def ka_expected():
        pooled = {m: sum(W["K"][q][m] for anc in anchors for q in sorted({r[2] for r in b.by[anc]}))
                  / sum(len({r[2] for r in b.by[anc]}) for anc in anchors) for m in b.models}
        row = np.array([pooled[m] for m in b.models])
        return np.repeat((row - row.mean())[None, :], len(anchors), axis=0)
    ka_ok = lambda: np.abs(g22.keyacc_matrix(b, anchors) - ka_expected()).max() < 1e-12
    check(ka_ok() and mutant_killed(design, "keyacc_cell", ka_ok),
          "v2 ruling A: keyacc is MODEL-LEVEL (pooled over all anchors, broadcast, centred per anchor); mutant keyacc_cell KILLED")
    dk = lambda: np.allclose(design.model_level_keyacc(np.array([[3, 1], [1, 3]]), np.array([4, 4]), np.ones((2, 2), bool)), 0.0)
    check(dk() and mutant_killed(design, "keyacc_cell", dk),
          "v2 ruling A: the design-leg keyacc pools over the whole EVAL supply (two strata cancel); mutant keyacc_cell KILLED")

    def fit_v2():
        return g22.fit_verdict_model_v2(b, anchors, g22.with_ka(S, KA), obs, KA)
    vm2 = fit_v2()
    print("\n".join(vm2.lines(b.models)))
    # RULING A (iv): beta-hat is compared with the ORACLE PROJECTION of the generator's own total effect (never with the
    # generator's beta), in board-shaped worlds (12 models x 10 anchors), 3 seeds, |beta-hat - oracle| < 0.5 in each.
    # [CORRECTED 2026-09-24 by ruling A (4b25059): the a944d22 reading "beta and u are collinear; identified only through
    # the ridge" is withdrawn: at the MAP beta is the least-squares projection of the anchor-centred total effect on keyacc.]
    oracle_rows = [board_world(seed) for seed in (1, 2, 3)]
    fit_or = lambda row: vmod.VerdictModelV2(row["G"], row["M"]).fit(row["O"]).beta
    or_ok = lambda: all(abs(fit_or(r) - r["oracle"]) < 0.5 for r in oracle_rows)
    got = [(round(fit_or(r), 3), round(r["oracle"], 3)) for r in oracle_rows]
    check(or_ok() and mutant_killed(vmod, "beta_unfit", or_ok),
          "v2 ruling A: beta-hat within 0.5 of the ORACLE projection in 3 board-shaped worlds (12 x 10), (beta-hat, oracle)"
          " = %s; mutant beta_unfit (beta pinned at 0) KILLED" % got)
    check(any("DIAGNOSTICS (ruling A (v)" in x and "corr(u-hat, keyacc)" in x for x in vm2.lines(b.models)),
          "v2 ruling A (v): beta-hat, sigma_eps_LOMO, the LOMO errors and corr(u-hat, keyacc) printed, deciding nothing")
    lomo_ok = lambda: fit_v2().sigma_eps_lomo > 0.01 and len(fit_v2().lomo_errors) == 6
    check(lomo_ok() and mutant_killed(vmod, "lomo_zero", lomo_ok),
          "v2: sigma_eps_LOMO > 0 over 6 held-out models (%.4f); mutant lomo_zero KILLED" % vm2.sigma_eps_lomo)
    Sk = g22.with_ka(S, KA)

    def quality_pref():
        rng = np.random.default_rng(5)
        wins = []
        for _ in range(20):
            sim = vm2.simulate(Sk, rng, mode="random")
            sel = (Sk["t"] != 0) & (np.abs(Sk["ka"]) > 0.05)
            wins.append(np.where(Sk["ka"][sel] > 0, sim["wa"][sel], 1 - sim["wa"][sel]).mean())
        return float(np.mean(wins)) > 0.55
    check(quality_pref() and mutant_killed(vmod, "beta_zero", quality_pref),
          "v2: the fresh-judge v2 simulation keeps the quality-aligned preference on non-key-decided matches (> 0.55);"
          " mutant beta_zero (beta dropped from the simulation) KILLED")
    rt = vmod.VerdictModel.from_params(json.loads(json.dumps(vm2.params())))
    check(isinstance(rt, vmod.VerdictModelV2) and rt.digest() == vm2.digest(), "v2: params round-trip to the v2 class (dispatch)")
    expect_exit(lambda: vm2.order_probs(dict(S), vm2.u), "no keyacc", "v2: a schedule without keyacc refuses")
    # ------------------------------------------------------------------ the v2 validity leg: FAIL, PASS, half_same
    real, aq = data.edges_fast(b, 20, Streams("V2FIX"), "x", floor=200)
    data.mark_established(real, b.K, aq, sb)
    est = {(e["anchor"], e["a"], e["b"]) for e in real if e["est"]}
    m = g22.cert_metrics(real, est, min_est=5)
    edge_t = dict(f=m["f_n"], u=m["u_n"], est=m["est_n"])
    tA = dict(f_raw_called=m["f_raw_called"])
    o1 = report.Out(None, echo=False)
    t1, recs1 = g22.validity_v2_leg(o1, b, sb, Streams("SELFTEST-V2-A"), R=8, B=20, family_alpha=1e-9, floor=200,
                                    targets=tA, ddev_targets=(), edge_targets=edge_t, min_est=5, record_B=20)
    print("\n".join(o1.lines[-24:]))
    check(t1["mode"] == vmod.V2_MODE and t1["label"] == vmod.POST_HOC, "v2 validity: the token carries the v2 mode and the label")
    check(all(vmod.POST_HOC in s for s in o1.lines if s.startswith(("=== (a')", "  VALIDITY", "  (a'-B)", "  MODE:"))),
          "v2 validity: every v2 heading and verdict line carries POST-HOC-SPECIFIED")
    check(any("ONE SHOT" in s for s in o1.lines) and any("H2 targets (builder of record" in s for s in o1.lines),
          "v2 validity: the one-shot rule and the H2 targets from the builder of record are printed")
    check(any("disjoint YES" in s for s in o1.lines), "v2 validity: the halves are disjoint under the registered seed")
    med = {k: float(np.median([x[k] for x in recs1])) for k in g22.H2_TARGET_KEYS}
    run2 = lambda st_name: g22.validity_v2_leg(report.Out(None, echo=False), b, sb, Streams(st_name), R=8, B=20,
                                               family_alpha=1e-9, floor=200, targets=tA, ddev_targets=(),
                                               edge_targets=edge_t, min_est=5, h2_targets=med,
                                               h2_edge_targets=t1.get("h2_edge_targets"))
    t2, _ = run2("SELFTEST-V2-A")
    check(t2["partB"] == "PASS", "v2 validity: part B PASSES when every H2 target is inside its interval (the medians)")
    check(t2["status"] == ("PASS" if t2["partA"] == "PASS" else "FAIL"), "v2 validity: status = part A AND part B")
    killed = mutant_killed(g22, "half_same", lambda: run2("SELFTEST-V2-A")[0]["partB"] == "PASS")
    check(killed and HITS.get("VALIDITY_V2.HALVES_OVERLAP", 0) > 0,
          "v2 validity: mutant half_same (H2 = H1) KILLED: overlapping halves void part B")
    o3 = report.Out(None, echo=False)
    t3, _ = g22.validity_v2_leg(o3, b, sb, Streams("SELFTEST-V2-A"), R=8, B=20, family_alpha=1e-9, floor=200, targets=tA,
                                ddev_targets=(), edge_targets=edge_t, min_est=5, h2_targets=dict(med, f_raw_called=10 ** 6),
                                h2_edge_targets=None)
    check(t3["status"] == "FAIL" and any("THIS FAIL IS FINAL" in s for s in o3.lines),
          "v2 validity: an H2 target outside its interval FAILS, printed as final (one shot)")
    check(HITS.get("VALIDITY_V2.PASS", 0) + HITS.get("VALIDITY_V2.FAIL", 0) >= 3, "v2 validity: the verdict branches executed")
    # ------------------------------------------------------------------ READY 5dfc825 D1: the deciding mechanics of v2
    split_sha = lambda: hashlib.sha256(",".join(map(str, sorted(g22.half_split(b)[0]))).encode()).hexdigest()
    check(split_sha() == GOLDEN_SPLIT_H1_SHA256 and mutant_killed(g22, "half_seed", lambda: split_sha() == GOLDEN_SPLIT_H1_SHA256),
          "D1 (R3): the half split under ARCHV2-G22-V2-HALF-1 equals its golden (sha256 of sorted H1 %s...); mutant half_seed KILLED"
          % GOLDEN_SPLIT_H1_SHA256[:16])
    complete_ok = lambda: (lambda h1, h2: g22.half_split_check(b, h1, h2)[:2] == (True, True))(*g22.half_split(b)[:2])
    check(complete_ok() and mutant_killed(g22, "half_drop", complete_ok),
          "D1 (R4): H1 and H2 are disjoint AND H1 u H2 = the judged set (no question dropped); mutant half_drop KILLED")
    voided = mutant_killed(g22, "half_drop", lambda: run2("SELFTEST-V2-A")[0]["partB"] == "PASS")
    check(voided and HITS.get("VALIDITY_V2.HALVES_INCOMPLETE", 0) > 0, "D1 (R4): an incomplete split VOIDS part B in the leg")
    check(t1.get("h2_exact_witness", 0) > 0 and any("exact-builder witness +" in x for x in o1.lines),
          "D1 (R5): part B's H2 targets carry a positive edges_exact witness (+%d boards)" % t1.get("h2_exact_witness", 0))
    h2_ok = lambda: g22.record_count_targets(g22.board_by_questions(b, g22.half_split(b)[1], "H2"), sb, B=12)[0] is not None
    check(h2_ok() and mutant_killed(g22, "h2_fast", h2_ok), "D1 (R5): the fast builder for the H2 targets is REFUSED; mutant h2_fast KILLED")
    t2_ok = lambda: (lambda t: t["T2"] == 12 and t["level2"] == g22.bonferroni_level(12, 1e-9))(run2("SELFTEST-V2-A")[0])
    check(t2_ok() and mutant_killed(g22, "t2_offbyone", t2_ok),
          "D1 (R6): T2 = 12 and level2 = 1 - alpha / 12 written into the token and checked; mutant t2_offbyone KILLED")
    leak_ok = lambda: fit_v2().lomo_leak_obs == 0
    check(leak_ok() and mutant_killed(vmod, "lomo_leak", leak_ok),
          "D1 (R8): every LOMO refit excludes model m's observations (0 leaked); mutant lomo_leak KILLED")
    fresh_ok = lambda: (lambda t: t["h2_fresh_u_sd"] > 0 and t["partB"] == "PASS")(run2("SELFTEST-V2-A")[0])
    check(fresh_ok() and mutant_killed(g22, "u_zero", fresh_ok) and HITS.get("VALIDITY_V2.NOT_FRESH", 0) > 0,
          "D1 (R9): part B simulates a FRESH judge (drawn u, SD > 0); mutant u_zero KILLED (part B VOID)")
    check(any("H2 edge IDENTITIES" in x and "MATCH" in x for x in o1.lines), "D12: the H2 edge IDENTITIES (key sets) are compared: MATCH")
    check(any("rulings 83f431b (ruling 1), 4b25059 (rulings A, B), 97f3a1f (P7)" in x for x in o1.lines)
          and any("v2 PART A (the 14 full-board targets)" in x for x in o1.lines),
          "D10: the v2 heading cites 83f431b, 4b25059, 97f3a1f; part A's inner line reports part A only")
    check(all(k in t1["timing"] for k in ("fixed_s", "per_rep_s")) and t1["timing"]["per_rep_s"] > 0,
          "D4: the v2 token carries the fixed-stage and per-replicate timings (%.2f s fixed, %.3f s per replicate)"
          % (t1["timing"]["fixed_s"], t1["timing"]["per_rep_s"]))
    # D5: the diagnostics beside the verdict, deciding nothing; the fresh-draw share against a hand computation
    k3 = np.array([-0.1, 0.0, 0.1])
    check(abs(g22.fresh_draw_share(2.0, k3, 0.1) - (4 * (0.02 / 3)) / (4 * (0.02 / 3) + 0.01)) < 1e-12
          and abs(g22.fresh_draw_share(2.0, k3, 0.1) - 0.7272727272727273) < 1e-12,
          "D5: the fresh-draw share beta^2 var(k) / (beta^2 var(k) + sigma^2) equals the hand computation 0.72727")
    T3 = 2.0 * k3 + np.array([0.05, -0.1, 0.05])
    check(abs(g22.in_sample_share(2.0, k3, T3) - np.var(2.0 * k3) / np.var(T3)) < 1e-12, "D5: the in-sample share by hand")
    check(any("D5 DIAGNOSTICS" in x for x in o1.lines) and any("FRESH-DRAW" in x and "0.933" in x for x in o1.lines)
          and any("LOMO prediction errors vs keyacc_m (DESCRIPTIVE, n = 6)" in x for x in o1.lines)
          and any("stability across question halves, NOT independent (H1 is a subset)" in x for x in o1.lines)
          and any("OPTIMISER CHECK" in x and ": OK" in x for x in o1.lines),
          "D5: shares (with the v1 DEV R^2 0.933 beside), LOMO errors vs keyacc, beta-hat H1 vs full, and corr(u, keyacc) as"
          " an optimiser check (OK) printed beside the v2 verdict")
    # ------------------------------------------------------------------ READY 5dfc825 D2: the sealed record token gate
    rec_like = dict(t2, status="PASS", partA="PASS", partB="PASS", master=g22.REC_MASTER_G22, R=1000, T=14, T2=12,
                    label=vmod.POST_HOC, record=True)
    p_rec = os.path.join(tmp, "tok_rec.json"); report.write_once(p_rec, json.dumps(g22.seal_token(rec_like), default=str))
    tr, vr = g22.load_token(p_rec, need_v2=True)
    check(isinstance(vr, vmod.VerdictModelV2) and HITS.get("TOKEN.RECORD_ADMITTED", 0) > 0,
          "D2: a sealed record-shaped v2 PASS token (master REC-1, R 1,000, label, T 14 / T2 12, parts PASS) is admitted")
    forged = dict(t2, status="PASS", partA="PASS", partB="PASS", master="DEV-ANY", R=3, label="anything", record=False)
    p_forged = os.path.join(tmp, "tok_forged.json"); report.write_once(p_forged, json.dumps(g22.seal_token(forged), default=str))
    forged_refused = lambda: (lambda: False)() if _loads(p_forged) else True
    check(forged_refused() and mutant_killed(g22, "gate_presence_only", forged_refused),
          "D2: a forged DEV token (master DEV-ANY, R 3, status PASS) is REFUSED by the record gate; mutant gate_presence_only KILLED")
    tampered = g22.seal_token(rec_like); tampered["status"] = "PASS"; tampered["partB"] = "FAIL"
    p_tam = os.path.join(tmp, "tok_tampered.json"); report.write_once(p_tam, json.dumps(tampered, default=str))
    expect_exit(lambda: g22.load_token(p_tam, need_v2=True), "whole-token digest", "D2: a field altered after the seal is refused")
    other = dict(g22.seal_token(rec_like)); other["instrument_lf16"] = "0" * 16
    other["token_digest"] = g22._token_digest(other)
    p_oth = os.path.join(tmp, "tok_other.json"); report.write_once(p_oth, json.dumps(other, default=str))
    expect_exit(lambda: g22.load_token(p_oth, need_v2=True), "another instrument", "D2: a token from another instrument is refused")
    # ------------------------------------------------------------------ READY 5dfc825 D3: ONE SHOT enforced
    marker = os.path.join(tmp, "oneshot", "G22_validity_v2.ONE_SHOT.json")
    g22.one_shot_claim(os.path.join(tmp, "first.txt"), g22.REC_MASTER_G22, path=marker)
    second = lambda: _refuses(lambda: g22.one_shot_claim(os.path.join(tmp, "other_out.txt"), g22.REC_MASTER_G22, path=marker))
    check(second() and mutant_killed(g22, "one_shot_off", second),
          "D3: a second record v2 launch is REFUSED whatever --out says; mutant one_shot_off KILLED")
    # the gate: designs and stop run ONLY IF v2 PASSES (the selftest token is a DEV token, admitted with dev=True only)
    tokp = g22.seal_token(dict(t2, status="PASS", record=False))
    p_v2 = os.path.join(tmp, "tok_v2.json"); report.write_once(p_v2, json.dumps(tokp, default=str))
    expect_exit(lambda: g22.load_token(p_v2, need_v2=True), "not a record fresh-judge v2 PASS",
                "D2: a DEV (selftest) v2 token is refused by the record gate")
    p_v1 = os.path.join(tmp, "tok_v1_pass.json")
    report.write_once(p_v1, json.dumps(dict(status="PASS", verdict_model=g22.VerdictModel(1, 2).params(),
                                            vm_digest=g22.VerdictModel(1, 2).digest()), default=str))
    expect_exit(lambda: g22.load_token(p_v1, need_v2=True), "ONLY IF the fresh-judge v2",
                "gate: a v1 PASS token refuses the designs / stop legs (run order (3))")
    tv, vmv = g22.load_token(p_v2, need_v2=True, dev=True)
    check(isinstance(vmv, vmod.VerdictModelV2) and HITS.get("TOKEN.DEV_ADMITTED", 0) > 0,
          "gate: a sealed DEV v2 PASS token loads the v2 model under --dev only")
    # designs with the v2 model: keyacc over the EVAL supply, the hypothetical union part, D0 beside 79,600, (d) under Holm
    kv = W["keyview"]
    pools = {}
    for q, s_ in kv.cat.items():
        pools.setdefault(s_, []).append(q)
    pools = {s_: sorted(v) for s_, v in pools.items()}
    spec = {"D0": [dict(corpus="union", roster="r6", strata=3, N=3)],
            "T1": [dict(corpus="syn", roster="r6", strata=3, N=3)]}
    st = Streams("SELFTEST-V2-DESIGNS")
    dz = g22.resolve_designs(["D0", "T1"], {"r6": W["models"]}, {"syn": {s_: 50 for s_ in pools}, "union": {s_: 50 for s_ in pools}},
                             {"syn": pools, "union": pools}, st, spec=spec)
    o4 = report.Out(None, echo=False)
    g22.designs_leg(o4, tv, vmv, dz, {"syn": kv, "union": kv}, st, R=2, B=12, floor=0, deff_reps=0, bar=0.01, min_est=3)
    print("\n".join(o4.lines))
    check(any("TRACE-LESS / HYPOTHETICAL" in s for s in o4.lines), "designs: a union part prints TRACE-LESS / HYPOTHETICAL")
    check(any("BESIDE the memo's 79,600 and the cap 79,560" in s for s in o4.lines), "designs: D0 printed beside 79,600 and 79,560")
    check(any("under HOLM-established labels" in s and "UNADJUSTED" in s for s in o4.lines),
          "designs: (d) printed under Holm labels beside the unadjusted, which decide")
    check(any("POST-HOC-SPECIFIED" in s for s in o4.lines), "designs: readings labelled as readings of a post-hoc-specified simulator")
    # ------------------------------------------------------------------ Holm flags
    fx = [dict(anchor="A", a="x", b="y", mc_p=p, est=p < 0.05) for p in (0.01, 0.04, 0.03)]
    holm_ok = lambda: sum(g22.holm_flags(fx)) == 1 and sum(e["est"] for e in fx) == 3
    check(holm_ok() and mutant_killed(g22, "holm_off", holm_ok),
          "(d) Holm: 3 unadjusted -> 1 Holm-established on the fixture; mutant holm_off KILLED")
    # ------------------------------------------------------------------ ties as a set
    from collections import Counter
    inc = Counter({"a": 2, "b": 2, "c": 1})
    ties_ok = lambda: g22.top_set(inc) == (2, ["a", "b"])
    check(ties_ok() and mutant_killed(g22, "ties_broken", ties_ok), "ties: printed as the SET {a, b}; mutant ties_broken KILLED")
    line = g22.set_line("set", 2, ["a", "b"], ["a"])
    check("a IN" in line and "b NOT IN" in line, "ties: the set line prints roster membership per model")
    # ------------------------------------------------------------------ the called residue (ruling 4)
    def E(anc, a_, b_, p, right, est=True, agree=0.5):
        return dict(anchor=anc, a=a_, b=b_, p=p, m=(3.0 if p > 0.9 else 0.1), s=0.3, agree=agree, right=right, est=est,
                    gap=0.1, mc_p=0.001)
    edges = [E("A1", "X", "m1", 0.6, False), E("A2", "X", "m2", 0.6, False), E("A3", "X", "m3", 0.6, False),
             E("A1", "Y", "m1", 1.0, False), E("A2", "Y", "m2", 1.0, True), E("A3", "m1", "m2", 1.0, True),
             E("A1", "m2", "m3", 1.0, True), E("A2", "m1", "m3", 1.0, True)]
    fit = lambda E_, x0=(-3.0, 3.0): (-50.0, 0.0)          # the IN-SAMPLE widener, printed beside only (ruling B)
    res_ok = lambda: g22.top_set(g22.called_residue(edges, "x12", "exact", fit)["inc"])[1] == ["Y", "m1"]
    check(res_ok() and mutant_killed(g22, "residue_all_wrong", res_ok),
          "residue: the CALLED wrong(established) population decides ({Y, m1}), not the all-wrong one (X); mutant"
          " residue_all_wrong KILLED")

    class _B:
        label = "fixture"
    o5 = report.Out(None, echo=False)
    r5 = g22.overdispersion_leg(o5, _B(), edges, Streams("SELFTEST-OD-V2"), perms=20, roster_models=["Y", "m1", "m2"],
                                all_models=["Y", "m1", "m2", "X"], fit=fit, board_key="x12")
    print("\n".join(o5.lines))
    check(r5["residue"] == ["Y", "m1"] and any("THE DECIDING DEFINITION" in s for s in o5.lines)
          and any("ALL-WRONG population" in s and "{X}" in s for s in o5.lines),
          "overdispersion: the called residue decides, the all-wrong set printed under its own name")
    o6 = report.Out(None, echo=False)
    r6 = g23.residue_leg(o6, sb, edges, edges, "fixture-M", "fixture-G", fit=fit, mistral_key="x12")
    print("\n".join(o6.lines))
    check(r6["top"] == ["Y", "m1"] and r6["top_all"] == ["X"], "G23 residue: the called definition decides; all-wrong beside")
    # ------------------------------------------------------------------ RULING B: the certificate of record
    pair_ok = lambda: (g22.record_pair("x12")[0] == (-3.2326, 3.3133) and g22.record_pair("merged")[0] == (-3.2326, 3.3133)
                       and g22.record_pair("grok")[0] == (-3.5451, 3.3854))
    check(pair_ok() and mutant_killed(g22, "wrong_pair", pair_ok),
          "ruling B: the shipped pairs per (board, judge_model): x12 / merged -3.2326 +3.3133, grok -3.5451 +3.3854;"
          " mutant wrong_pair KILLED")
    expect_exit(lambda: g22.record_pair("kotlin"), "no stored widener pair", "ruling B: a board with no stored pair refuses")
    cold_ok = lambda: g22.record_certificate(edges, "x12", fit)["pair"] == (-3.2326, 3.3133)
    check(cold_ok() and mutant_killed(g22, "widener_refit", cold_ok),
          "ruling B: the pair is applied COLD (never the in-sample refit); mutant widener_refit KILLED")
    rcx = g22.record_certificate(edges, "x12", fit)
    check(rcx["called"] == 5 and rcx["wrong"] == 1 and rcx["insample"] == (-50.0, 0.0),
          "ruling B: widener + key-tie decline at 0.975 on the gap >= 0.02 edges: 5 called, 1 wrong(est); the in-sample"
          " widener kept beside (%s)" % ((rcx["called"], rcx["wrong"], rcx["insample"]),))
    lines_b = g22.record_certificate_lines(g22.called_residue(edges, "x12", "exact", fit), "x12")
    check(any("in-sample widener (a DIFFERENT OBJECT" in x for x in lines_b) and any("SHIPPED pair COLD" in x for x in lines_b),
          "ruling B: the certificate and the in-sample widener beside are printed")
    pre_fail = lambda: not g22.called_residue(edges, "merged", "exact", fit)["precondition_ok"]
    check(pre_fail() and mutant_killed(g22, "precondition_skipped", pre_fail),
          "ruling B precondition: on merged, counts other than KTD-CHECK's 1,714 / 4(4) STOP the residue readout;"
          " mutant precondition_skipped KILLED")
    check(not g22.called_residue(edges, "merged", "fast", fit)["precondition_ok"],
          "ruling B precondition: the fast builder on merged fails the precondition")
    rcm = g22.record_certificate(edges, "merged", fit)
    check(g22.called_residue(edges, "merged", "exact", fit, expect=(rcm["called"], rcm["wrong"], rcm["wrong_est"]))["precondition_ok"],
          "ruling B precondition: the MET branch executes when the counts equal the expected ones")
    o8 = report.Out(None, echo=False)
    r8 = g22.overdispersion_leg(o8, _B(), edges, Streams("SELFTEST-OD-V2B"), perms=20, fit=fit, board_key="merged")
    check(r8["residue"] == "STOPPED" and any("FAILED PRECONDITION" in x for x in o8.lines),
          "ruling B: overdispersion on merged with a failed precondition prints no residue model")
    o8b = report.Out(None, echo=False)
    g22.overdispersion_leg(o8b, _B(), edges, Streams("SELFTEST-OD-V2C"), perms=5, fit=fit, board_key="merged",
                           roster_models=["Y"], all_models=["Y", "Meta-Llama-3_1-70B-Instruct"])
    check(not any("{S, T, O" in x for x in o8b.lines) and any("NOT READ (failed precondition)" in x for x in o8b.lines),
          "D7: a STOPPED residue prints 'NOT READ (failed precondition)', never the characters {S, T, O, P, P, E, D}")
    check(any("-> N/A" in x for x in g22.record_certificate_lines(g22.called_residue(edges, "x12", "exact", fit), "x12")),
          "D8: a board with no registered precondition prints N/A, not MET")
    o9 = report.Out(None, echo=False)
    r9 = g23.residue_leg(o9, sb, edges, edges, "fixture-M", "fixture-G", fit=fit, mistral_key="merged")
    check(r9["word"].startswith("FAILED PRECONDITION"), "ruling B: the G23 residue on merged with a failed precondition is not read")
    # ------------------------------------------------------------------ BBH / MuSR missing (ruling 2)
    db = os.path.join(tmp, "union_fixture.db")
    con = data.ro.REAL_CONNECT(db)
    con.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, pred TEXT, is_correct INTEGER, "
                "model_output TEXT, category TEXT)")
    con.execute("CREATE TABLE corpus_questions (question_id INTEGER, source TEXT, domain TEXT)")
    for q, src in ((1, "BBH"), (2, "MUSR"), (3, "GPQA")):
        con.execute("INSERT INTO corpus_questions VALUES (?,?,?)", (q, src, "d"))
        for mname, pr, ok in (("ma", "{'arg_0': 'x'}" if src == "BBH" else "Desk", 1), ("mb", "{'arg_0': 'y'}" if src == "BBH" else "Drawer", 1)):
            con.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?)", (q, mname, pr if src != "GPQA" else "A", ok, "", src))
    con.commit(); con.close()
    miss_ok = lambda: (lambda kt: kt.P[1]["ma"] == "" and kt.P[2]["mb"] == "" and kt.P[3]["ma"] == "A" and kt.n_missing == 4)(
        data.KeyTable(db, stratum="source_domain", missing_sources=("BBH", "MUSR")))
    check(miss_ok() and mutant_killed(data, "bbh_not_missing", miss_ok),
          "BBH / MuSR: extracted answers set MISSING, GPQA untouched; mutant bbh_not_missing KILLED")
    check(vmod.match_type(1, 1, "", "") == 2, "BBH / MuSR: equal keys with missing answers type NONDEC (convention A keeps the match)")
    # ------------------------------------------------------------------ nu readings
    o7 = report.Out(None, echo=False)
    g22.nu_leg(o7, W["board"], Streams("SELFTEST-NU-V2"), cert.FROZEN_GROK_UNFILTERED, [4, 5, 6], [2], reps=2, B=12,
               floor=0, boot=50)
    check(any("CI resamples: 2,000" in s for s in o7.lines) and any("AS WRITTEN (VACUOUS" in s for s in o7.lines)
          and any("POST-DATA" in s and "reading P" in s for s in o7.lines),
          "nu: both readings printed (the '>= 0.9' as written, the reach-to-P POST-DATA) and the resample count 2,000")
    # ------------------------------------------------------------------ P7 scoring
    N = g22.P7_NAMED
    roster = [N, "Qwen1.5-72B-Chat", "gpt-4o-mini", "deepseek-chat-v2_5"]
    base = {"merged": dict(residue=[N], n_called_wrong=4),
            "x12": dict(residue=sorted([N, "Qwen1.5-72B-Chat"]), n_called_wrong=1),
            "grok": dict(residue=sorted([N, "Qwen1.5-72B-Chat"]), n_called_wrong=1)}
    l1, v1 = g22.p7_score(base, roster)
    print("\n".join(l1))
    check(v1["identity"].startswith("HELD") and v1["roster_ok"] and v1["reading_a"] and not v1["reading_b"]
          and sum("UNRESOLVED (one-edge tie)" in x for x in l1) == 2 and any("POST-DATA" in x for x in l1),
          "P7: merged unique -> HELD; x12 / grok one-edge ties UNRESOLVED; roster ok; POST-DATA (a) yes, (b) no")
    x12_ok = lambda: g22.p7_score(base, roster)[1]["identity"].startswith("HELD")
    check(x12_ok() and mutant_killed(g22, "p7_x12_scored", x12_ok),
          "P7: identity scored on MERGED ONLY (the x12 one-edge tie never scored); mutant p7_x12_scored KILLED")
    tie = dict(base, merged=dict(residue=sorted([N, "gpt-4o-mini"]), n_called_wrong=3))
    tie_ok = lambda: g22.p7_score(tie, roster)[1]["identity"].startswith("NOT HELD")
    check(tie_ok() and mutant_killed(g22, "p7_tie_held", tie_ok), "P7: a tie on merged is NOT HELD; mutant p7_tie_held KILLED")
    out_g = dict(base, grok=dict(residue=sorted([N, "outsider-model"]), n_called_wrong=1))
    ros_ok = lambda: not g22.p7_score(out_g, roster)[1]["roster_ok"]
    check(ros_ok() and mutant_killed(g22, "p7_roster_merged_only", ros_ok),
          "P7: a residue member outside the roster on grok fires the falsifier (checked on ALL boards); mutant"
          " p7_roster_merged_only KILLED")
    stopped = dict(base, merged=dict(residue="STOPPED", n_called_wrong=0))
    check(g22.p7_score(stopped, roster)[1]["identity"].startswith("UNDETERMINED"),
          "P7: merged not read (failed precondition) -> UNDETERMINED")
    for br in ("TOKEN.REFUSED_NOT_RECORD", "TOKEN.REFUSED_SEAL", "TOKEN.REFUSED_INSTRUMENT", "ONE_SHOT.REFUSED",
               "ONE_SHOT.CLAIMED", "VALIDITY_V2.H2_BUILDER_REFUSED", "P7.IDENTITY_HELD", "P7.IDENTITY_NOT", "P7.IDENTITY_UNDETERMINED", "P7.ONE_EDGE_TIE", "P7.ROSTER_OK",
               "P7.ROSTER_FALSIFIER", "RECORD_CERT.PRECONDITION_FAILED", "RECORD_CERT.PRECONDITION_MET", "RECORD_CERT.REFUSED_BOARD",
               "RESIDUE.PRECONDITION_FAILED", "VALIDITY_V2.HALVES_OVERLAP", "TOKEN.REFUSED_NOT_V2", "DESIGNS.HYPOTHETICAL", "DESIGNS.HOLM_PRINTED",
               "OVERDISP.CALLED_RESIDUE", "RESIDUE.CALLED_DEFINITION", "NU.READINGS"):
        check(HITS.get(br, 0) > 0, "branch executed: %s" % br)
