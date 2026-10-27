"""ARCH-V2-PILOT-K46 --analyze: the orchestration of archv2_pilot.analysis's readouts over a verdict store (read-only).
The order is the registration's: C0 first (any failure: UNDETERMINED BY VALIDITY, no reading); C1 computed and WRITTEN
(<out>.C1.txt, write-once) BEFORE the key is unsealed; then C3 (key), C1b, C1c, C2, the predictions and the falsifier.
A store with pending slots is not a complete cache: the output goes to <out>_PARTIAL.txt and C0 fails on completeness.
[READY 65a9173, insertion] K4: before C1 NOTHING loads the leak material (the loader reads gt_raw / answer_text /
is_correct): C0 (d) splits into part 1 before C1 (verdict coverage by count, the payload anchor in (c)) and part 2 after C1
is written (the payload rebuild and the leak re-scan on 100%), whose failure VOIDS the reading; the witness line prints the
loads counted (pilot.KEY_MATERIAL_LOADS) and a load before C1 REFUSES. C0 (f) reads the write-ahead journal (K1): ledger ==
journal invocations, orphans and raised invocations disclosed. C1b, beta_matched, the projections and P2b follow the K5 /
K6 / K7 rulings (analysis.py). The K8 mask lines print beside C1.
[AMENDED 2026-09-25 BEFORE ANY CODE (0761cfa, docs/judge_v2_program.md L16787-L16992), insertion only; k = 37: C0 (b)
reads the 37-roster rule (registry 47 / ACTIVE 46, the 9 dropped present, ACTIVE and absent from the roster, the roster
sha256-text 3a3204cc...6f91, ARENA12 inside and not dropped, 0 rows outside the roster, 0 EMPTY raw outputs on the
scheduled cells); C0 (h) is new (matches before the trim <= 2 x N x C(37,2) = 2,664, t = 0); C1 and beta_matched are
read against THE EXACT M bar (pilot.exact_bar_M); the arx_0314 DISCLOSURE prints beside C1 and C1b; C2 adds the per-model
EMPTY / SHORT (< 40) raw-output table over the scheduled cells; the roster sha is written into the outcome (the REUSE
CONDITION (v)) and into the store manifest (<store>.launch.json, pilot.launch).]
[RE-PINNED 2026-09-25, insertion only (the author's pre-decided fallback, programme L16994-L17006; record pending): the
header prints "rubric slot: GENERIC_RUBRIC (author's pre-decided fallback 2026-09-25; INDUCE-RUBRIC-1/-2/-3 NOT ADOPTED)"
with the GENERIC_RUBRIC, persona and system-turn shas (pilot.rubric_slot_lines); C0 (c) reads the judge pins of MAIN
b653b0a (pilot.JUDGE_V2_PINS_LABEL; each of the seven also = main's blob) and names the slot; its condition is unchanged.]
[L7' 2026-09-25, AFTER the run and BEFORE --analyze (READY 1f58df5 L7'), insertion only: (F2) the match-level bootstrap
(analysis.match_bootstrap, stream "deff/mboot", same B as C1's, key-blind, before C1 is written) and the measured DEFF /
n_eff / MDE printed in the support lines, deciding nothing; (F3) P3a / P3b scored by the registrar's ruling
(analysis.p3_lines), printed UNDETERMINED in both C0-failure branches too; (G1) P5's posted = journal + prior, as C0 (f);
(F4) the READY 286a1b0 F4 disclosure printed verbatim beside C1 and C1b; (F8) the out-of-roster counts of the BOARD rows
(before C1) and of the LOADED specs (after C1) printed separately, beside C0 (b). CODE IDENTITY: analysis.py and
outcome.py are in common.PACKAGE_FILES, so this analysis's package lf16 differs from the posting build's; --analyze never
compares it with the store's recipe identity (writer.IDENTITY_KEYS is checked by JudgeWriter.open, i.e. a --pilot / --run
relaunch only), so the store of record is READ, not refused; the header prints the store's script_blob, the launch
manifest's archv2_pilot_lf16 and this analysis's lf16 side by side, as disclosure. A relaunch of --run from this code
WOULD refuse ("the recipe identity differs"): the run resumes only from the posting build.]
"""
import json
import math
import os
from collections import defaultdict

import numpy as np

from . import analysis as A
from . import common as C
from . import pilot as PL
from archv2_arena import cert, design, report
from archv2_arena import data as AD
from archv2_arena.report import hit


def read_store(path):
    from judge_v2 import writer as W
    c = PL.open_store_ro(path)
    try:
        sched = c.execute("SELECT match_id, presentation_order, variant_id, contestant_a, contestant_b, batch_id FROM"
                          " schedule").fetchall()
        verd = c.execute("SELECT match_id, presentation_order, vote, payload_sha256 FROM verdict").fetchall()
        att = c.execute("SELECT COUNT(*), SUM(error_class IS NOT NULL) FROM attempt").fetchone()
        meta = dict(c.execute("SELECT key, value FROM run_meta"))
    finally:
        c.close()
    mv = {x["match_id"]: x for x in W.match_verdicts(path)}
    return {"schedule": sched, "verdicts": verd, "attempts": int(att[0] or 0), "errors": int(att[1] or 0), "meta": meta,
            "match": mv}


def c2_lines(plan, loaded):
    out = ["", "=== C2 SCHEDULE (descriptive, simulator-free) ==="]
    kept_by = defaultdict(int)
    uses = defaultdict(lambda: defaultdict(int))
    for m in plan.kept:
        kept_by[m["anchor"]] += 1
        uses[m["anchor"]][m["item_id"]] += 1
    for a in sorted(plan.stats):
        s = plan.stats[a]
        u = sorted(uses[a].values())
        out.append("  anchor %-18s filtered matches before the trim %d, after %d | exhausted pairs %d of %d | questions"
                   " used %d of %d, uses per question min %d / median %.1f / max %d" % (
                       a, s["matches_before_trim"], kept_by[a], s["exhausted_pairs"], s["pairs"], len(u), s["questions"],
                       u[0] if u else 0, float(np.median(u)) if u else 0.0, u[-1] if u else 0))
    out.append("  total: before the trim %d, after %d (trim t %d, %d pairs removed)" % (
        len(plan.before), len(plan.kept), plan.t, len(plan.removed)))
    out += PL.mask_lines(plan.stats, plan.cfg)
    by_model, by_var = PL.class_tables(plan.kept, plan.klass)
    tot = defaultdict(int)
    for k in plan.klass.values():
        tot[k] += 1
    if loaded is None:
        out.append("  reference classes over the scheduled matches (predicted from free data; the loader is not run): %s"
                   % json.dumps(dict(sorted(tot.items()))))
    else:
        cnt = loaded.manifest["counts"]
        out.append("  reference classes over the scheduled matches: %s (loader realised: ONE %d, NONE %d, excluded %s)" % (
            json.dumps(dict(sorted(tot.items()))), cnt["reference_ONE"], cnt["reference_NONE"],
            json.dumps({k: v for k, v in sorted(cnt.items()) if k.startswith("excluded_")})))
    out.append("  per model (scheduled matches by reference class):")
    for mo in sorted(by_model):
        out.append("    %-40s %s" % (mo, ", ".join("%s %d" % kv for kv in sorted(by_model[mo].items()))))
    nv = sum(1 for v in by_var.values() if any(k.startswith("excluded") for k in v))
    nn = sum(1 for v in by_var.values() if "NONE" in v)
    out.append("  per variant: %d variants scheduled; %d carry an excluded match; %d carry a reference-NONE match (the"
               " per-variant table: records c2_variants)" % (len(by_var), nv, nn))
    out += raw_output_lines(plan)
    return out, by_var


def raw_output_lines(plan):
    """[0761cfa] C2: per model of the roster, the EMPTY (length 0) and SHORT (< 40, empty included) RAW outputs
    (zlib-decompressed response.output_zlib, UTF-8, stripped, BEFORE robust_trace), over that model's scheduled cells (the
    denominator printed beside); short non-empty separately; then the arx_0314 line."""
    rc = plan.raw_counts
    tot = {k: sum(v[k] for v in rc.values()) for k in ("cells", "empty", "short", "short_nonempty")}
    out = ["  raw outputs per model over its scheduled cells (length = code points after strip, before robust_trace):"
           " EMPTY / SHORT (< %d, empty included) / short non-empty / cells; all models: %d / %d / %d / %d" % (
               PL.SHORT_CHARS, tot["empty"], tot["short"], tot["short_nonempty"], tot["cells"])]
    for mo in sorted(rc):
        v = rc[mo]
        out.append("    %-40s empty %d, short %d, short non-empty %d, of %d cells" % (mo, v["empty"], v["short"],
                                                                                   v["short_nonempty"], v["cells"]))
    a = rc.get(A.DISCLOSED_MODEL)
    if a is None:
        out.append("  %s: no scheduled cell" % A.DISCLOSED_MODEL)
    else:
        out.append("  %s (DISCLOSED; ARENA12): empty %d, short %d (%.1f%%), short non-empty %d, of %d scheduled cells" % (
            A.DISCLOSED_MODEL, a["empty"], a["short"], 100.0 * a["short"] / max(1, a["cells"]), a["short_nonempty"],
            a["cells"]))
    return out


MUTANT = None       # SELFTEST-ONLY: "load_early" (the loader's key material read before C1 is written; K4)
# [L7'] SELFTEST-ONLY: "deff_off" (leg A of the DEFF inertness proof: the match-level bootstrap not run, deff None),
# "deff_question_draws" (the DEFF's denominator taken from C1's own question-clustered records: DEFF 1), "p5_journal_only"
# (P5's posted = the run2 journal only, the pre-L7' G1 defect)


def _board_rows(plan, st_rec):
    rows_b, unusable = [], 0
    for m in plan.kept:
        if m["match_id"] in plan.expected:
            continue
        comb = st_rec["match"][m["match_id"]]["combiner"]
        if comb == "A":
            w = m["model_a"]
        elif comb == "B":
            w = m["model_b"]
        elif comb == "TIE":
            w = "TIE"
        else:
            unusable += 1
            continue
        rows_b.append((m["anchor"], m["model_a"], m["model_b"], m["item_id"], w))
    return rows_b, unusable


def analyze(cfg, view_path, stage1_record, store_path, rubric, ledger_dir, out_path, expect=None, workers=1, echo=True):
    from archv2_arena import g22
    from . import accounting as ACC
    expect = dict(expect or {})
    loads0 = PL.KEY_MATERIAL_LOADS["n"]
    st_rec = read_store(store_path)
    pend = sum(1 for x in st_rec["match"].values() if x["status"] == "PENDING")
    complete = pend == 0 and len(st_rec["match"]) > 0
    final = out_path if complete else (os.path.splitext(out_path)[0] + "_PARTIAL.txt")
    c1_path = final + ".C1.txt"
    for p in (final, c1_path):
        C.need(not os.path.exists(p), "%s exists: outputs of record are write-once" % p)
    say = report.Out(final, echo=echo)
    pins_ok, pins_bad = PL.judge_pins_ok(cfg)
    say("ARCH-V2-PILOT-K46 OUTCOME: %s" % PL.word(cfg),
        "  run %s | store %s | registration 3a12115 (L15913-L15955), amendment 2296877 (L15975-L15983), rulings b44227f"
        " (rubric) / 53eccb6 (anchors, frozen pair) / the K5-K8 rulings on READY 65a9173 / amendment %s (k 37,"
        " L16787-L16992)" % (
            PL.RUN_ID, os.path.basename(store_path), PL.AMENDMENT_K37),
        "  code: archv2_pilot lf16 %s | frozen instrument lf16 %s (read-only) | judge_v2 pins (%s) %s" % (
            C.package_lf16(), C.check_instrument(), cfg.judge_pins, "EQUAL" if pins_ok else "DIFFER: %s" % pins_bad),
        *PL.rubric_slot_lines(rubric),
        "  cache: %d scheduled matches, %d pending -> %s" % (len(st_rec["match"]), pend,
                                                             "COMPLETE" if complete else "PARTIAL (no reading is made)"))
    plan = PL.make_plan(cfg, view_path, stage1_record, say)
    order_ids = [m["match_id"] for m in plan.kept if m["match_id"] not in plan.expected]
    man_path = store_path + ".launch.json"
    man = {}
    if os.path.exists(man_path):
        with open(man_path, encoding="utf-8") as f:
            man = json.load(f)
    # [L7'] disclosure only: the posting build's code identity beside this analysis's (never a gate; see the docstring)
    cur_lf16 = C.package_lf16()
    man_lf16 = man.get("archv2_pilot_lf16")
    say("  code identity (disclosure, not a gate): the store's run_meta script_blob %s | the launch manifest's"
        " archv2_pilot_lf16 %s | this analysis's archv2_pilot lf16 %s (%s)" % (
            st_rec["meta"].get("script_blob", "ABSENT"), man_lf16 or "ABSENT", cur_lf16,
            "EQUAL to the posting build's" if man_lf16 == cur_lf16 else
            "DIFFERS from the posting build's: the analysis code changed after the run (L7'); --analyze does not compare"
            " the recipe identity"))
    say("", "=== C0 VALIDITY (first; any failure pre-empts every reading) ===")
    checks = []

    def chk(tag, ok, text):
        ok = bool(ok)
        hit("C0.%s.%s" % (tag, "PASS" if ok else "FAIL"))
        checks.append(ok)
        say("  (%s) %s: %s" % (tag, "PASS" if ok else "FAIL", text))
    conn, _sha, _m = C.open_view("arena", view_path, cfg.view_sha if cfg.record() else None, say)
    try:
        ev = C.eval_items(conn, cfg.cv)
        svars = sorted({r[2] for r in st_rec["schedule"]})
        items_of = {}
        for v in svars:
            r = conn.execute("SELECT item_id FROM variant WHERE corpus_version=? AND variant_id=?", (cfg.cv, v)).fetchall()
            items_of[v] = r[0][0] if len(r) == 1 else None
        bad_a = [v for v in svars if items_of[v] is None or items_of[v] not in ev]
        chk("a", not bad_a and svars, "%d judged variants, every item on the EVAL side of %s (variant_id -> item_id,"
            " corpus_version named); off-side / unresolved: %d" % (len(svars), plan.pool["pool_id"], len(bad_a)))
        # [0761cfa] C0 (b) replaced: the 37-roster rule (roster_of refuses before this line on any registry failure)
        n_out_sched = PL.outside_roster(plan.kept, plan.roster)
        n_out_cached = PL.outside_roster([(a, b) for _m, _o, _v, a, b, _x in st_rec["schedule"]], plan.roster)
        n_empty = sum(v["empty"] for v in plan.raw_counts.values())
        chk("b", len(plan.roster) == cfg.roster_n and plan.digests["roster_sha"] == cfg.roster_sha256 and
            cfg.quarantined not in plan.roster and not (set(plan.dropped) & set(plan.roster)) and
            sorted(plan.dropped) == sorted(cfg.dropped) and set(cfg.arena12) <= set(plan.roster) and
            not (set(cfg.arena12) & set(plan.dropped)) and n_out_sched == 0 and n_out_cached == 0 and n_empty == 0,
            "roster %d = ACTIVE %d - %d dropped (dropped_sha %s; each present and ACTIVE; absent from the roster), roster"
            " sha256-text %s (registered %s), registry %d, %s QUARANTINED and absent, ARENA12 inside and not dropped; rows"
            " naming a model outside the roster: scheduled %d, cached %d (required 0); EMPTY raw outputs on the scheduled"
            " cells %d (required 0)" % (len(plan.roster), cfg.active_n, len(plan.dropped), plan.digests["dropped_sha"],
                                       plan.digests["roster_sha"], cfg.roster_sha256, cfg.registry_total, cfg.quarantined,
                                       n_out_sched, n_out_cached, n_empty))
        rows_store = {(m, o): s for m, o, _v, s in st_rec["verdicts"]}
        prow = [(mid, o, rows_store.get((mid, o), "")) for mid in order_ids for o in (1, 2)]
        store_anchor = PL.payload_anchor(prow)
        want_anchor = expect.get("payload_anchor") or man.get("payload_anchor")
        chk("c", pins_ok and want_anchor is not None and store_anchor == want_anchor,
            "judge_v2 pins (%s: %s; each of the seven = main's actual blob) %s; the store's payload anchor %s vs the"
            " dry-run's %s; the payloads' rubric slot GENERIC_RUBRIC sha256-text %s (required %s)" % (
                cfg.judge_pins, PL.JUDGE_V2_PINS_LABEL, "equal" if pins_ok else pins_bad, store_anchor, want_anchor,
                rubric.rubric_sha256, PL.GENERIC_RUBRIC_SHA256))
        covered = all((mid, o) in rows_store for mid in order_ids for o in (1, 2))
        chk("d", len(st_rec["verdicts"]) == 2 * len(order_ids) and covered,
            "part 1 (before C1, without the leak material): %d verdict rows = 2 x %d loaded matches, every slot covered: %s;"
            " part 2 (the payload rebuild and the leak re-scan on 100%%) runs after C1 is written (K4), and its failure"
            " VOIDS the reading" % (len(st_rec["verdicts"]), len(order_ids), covered))
        pilot_ids = man.get("pilot_ids") or order_ids[:cfg.pilot_n]
        g = PL.pilot_guard(store_path, pilot_ids)
        gfile = os.path.exists(store_path + ".pilot_guard.json")
        chk("e", gfile and g["cached_calls"] == 2 * len(pilot_ids) and g["unusable"] == 0,
            "pilot-12 guard file %s; the pilot slots now: cached %d of %d, unusable %d, ERRORED attempts %d (counted, K3)"
            % ("PASS on record" if gfile else "ABSENT", g["cached_calls"], 2 * len(pilot_ids), g["unusable"],
               g["errored_attempts"]))
        js = ACC.read_journal(PL.journal_path(store_path))
        led = ACC.atl.ledger_calls(PL.REGISTRATION, ledger_dir)
        inv = js["invocations"]
        # [2026-09-25 incident] the retired store's booked invocations (sha-pinned; no request left the machine) are
        # counted on the journal side of the equality and against the ceiling
        prior = PL.prior_journals_state(cfg, ledger_dir)
        inv_all = inv + prior["invocations"]
        chk("f", inv_all <= min(cfg.ceiling_calls, ACC.AUTHOR_HARD_CAP) and led == inv_all and st_rec["attempts"] <= inv
            and not js["unresolved"],
            "journal invocations (write-ahead) %d + prior (retired stores) %d = %d <= %d; the ledgers' rows for %s %d"
            " (equal: %s); store attempt rows %d; ORPHANS %d, RAISED %d, unresolved %d (disclosed)" % (
                inv, prior["invocations"], inv_all, min(cfg.ceiling_calls, ACC.AUTHOR_HARD_CAP), PL.REGISTRATION, led,
                led == inv_all, st_rec["attempts"], js["by_outcome"].get("ORPHAN", 0), js["by_outcome"].get("RAISED", 0),
                len(js["unresolved"])))
        sched_set = {(m, v, a, b) for m, _o, v, a, b, _x in st_rec["schedule"]}
        plan_set = {(m["match_id"], m["variant_id"], m["model_a"], m["model_b"]) for m in plan.kept
                    if m["match_id"] not in plan.expected}
        chk("g", sched_set == plan_set and (not man or man.get("digests") == plan.digests),
            "the anchor draw, the question selection and the trim reproduce from the registered streams (%s); the store's"
            " schedule equals the plan: %s" % (json.dumps(plan.digests, sort_keys=True), sched_set == plan_set))
        per_a, bound = PL.schedule_bound(cfg, len(plan.roster), len(plan.stats))
        chk("h", len(plan.before) <= bound and plan.t == 0 and len(plan.kept) == len(plan.before),
            "SCHEDULE BOUND (amendment %s): matches before the trim %d <= %d x N %d x C(%d,2) = %d (%d per anchor); trim"
            " t = %d (required 0); after %d = before" % (PL.AMENDMENT_K37, len(plan.before), len(plan.stats), cfg.N,
                                                         len(plan.roster), bound, per_a, plan.t, len(plan.kept)))
        chk("complete", complete, "every scheduled slot carries a verdict (pending matches %d)" % pend)
        c0_pass = all(checks)
        say("  C0: %s" % ("PASS" if c0_pass else "FAIL -> UNDETERMINED BY VALIDITY: no reading"))
        if not c0_pass:
            hit("C0.UNDETERMINED_BY_VALIDITY")
            say("  PREDICTIONS P3 (the ruling of 2026-09-25): C1 gives no reading", *A.p3_lines(False, []))
            say(*A.falsifier_lines([], c0_pass=False))
            say(*c2_lines(plan, None)[0])
            say(*plan.streams.summary())
            say.write(plan.streams)
            return {"c0": False, "path": final}
        rows_b, unusable = _board_rows(plan, st_rec)
        n_out_board = PL.require_inside([(r[1], r[2]) for r in rows_b], plan.roster, "board")
        say("  (b) [F8] board rows naming a model outside the roster: %d of %d (required 0; require_inside refuses any);"
            " the LOADED specs are counted after C1 is written (K4) [D-5: this count can only print 0: require_inside"
            " REFUSES the analysis on any such row before this line; it witnesses the check, it does not measure]" % (
                n_out_board, len(rows_b)))
        unusable_calls = sum(1 for _m, _o, v, _s in st_rec["verdicts"] if v not in ("FIRST", "SECOND", "TIE"))
        answers = plan.free["A"]
        anchors = sorted(plan.anchors)
        k_hi, k_lo = len(plan.roster), cfg.k_lo
        C.need(tuple(cfg.rungs)[0] == k_lo and tuple(cfg.rungs)[-1] == k_hi, "rungs %s must run from %d to %d" % (
            cfg.rungs, k_lo, k_hi))
        st = plan.streams
        rr_ = st.np("rungs")
        rosters = {k_lo: sorted(cfg.arena12), k_hi: sorted(plan.roster)}
        for k in cfg.rungs[1:-1]:
            rosters[k] = sorted(str(x) for x in rr_.choice(np.array(sorted(plan.roster)), size=k, replace=False))
        if MUTANT == "load_early":
            PL.load_plan(plan, lambda s: None)
        loads = PL.KEY_MATERIAL_LOADS["n"] - loads0
        C.need(loads == 0, "K4: the loader's key material (gt_raw / answer_text / is_correct) was loaded %d time(s) in this"
               " analysis before C1 is written: refused" % loads)
        say("", "=== %s: the exponent beta-hat between the k = %d and k = %d sub-boards (%s) ===" % (
            A.C1_MARK, k_lo, k_hi, A.FROZEN_LABEL),
            "  K4 WITNESS: key-material loads in this analysis before C1: %d; C1's inputs are the verdict rows (a, b,"
            " question, winner), the free answers and the rosters only" % loads,
            "  board: %d usable dual-order matches (%d unusable: INVALID / NON_TERMINATED / CONTENT_FILTER), %d of them"
            " on ARENA12 pairs" % (len(rows_b), unusable, sum(1 for r in rows_b if r[1] in rosters[k_lo] and
                                                                r[2] in rosters[k_lo])),
            "  ties enter the fit as half-wins (the fit of record's convention; a ties-dropped reading is not computed);"
            " tie share %.4f" % (sum(1 for r in rows_b if r[4] == "TIE") / max(1, len(rows_b))),
            "  rung rosters (stream 'rungs'): %s" % json.dumps({str(k): C.sha256_text("\n".join(v))[:16]
                                                                for k, v in sorted(rosters.items())}),
            "  REUSE CONDITION (v) (amendment %s): these verdicts are stage-1 data ONLY IF stage 1's roster sha256-text"
            " equals this pilot's %s (registered %s; %d models; written into the store manifest %s: %s)" % (
                PL.AMENDMENT_K37, plan.digests["roster_sha"], cfg.roster_sha256, len(plan.roster),
                os.path.basename(man_path), man.get("roster_sha256", "ABSENT (a launch before the amendment)")))
        say(*PL.mask_thin_lines(plan.stats))
        e_hi = A.blind_edges(A.make_board(rows_b, rosters[k_hi], answers, "k%d" % k_hi), cfg.B_inner, st,
                             "boot/point/k%02d" % k_hi)
        pair = cfg.frozen_pair
        if A.MUTANT == "refit_pair":
            pair = cert.fit_v(cert.EdgeArrays(e_hi))
        pair = A.check_frozen(pair, cfg)
        e_lo = A.blind_edges(A.make_board(rows_b, rosters[k_lo], answers, "k%d" % k_lo), cfg.B_inner, st,
                             "boot/point/k%02d" % k_lo)
        nu_hi, pa_hi = A.nu2(e_hi, pair, anchors)
        nu_lo, pa_lo = A.nu2(e_lo, pair, anchors)
        beta_hat = A.beta_of(nu_hi, nu_lo, k_hi, k_lo)
        for a in anchors:
            say("  anchor %-18s nominal k %d %.4f (called %d of %d edges) | k %d %.4f (called %d of %d) (%s)" % (
                a, k_hi, pa_hi[a][0], pa_hi[a][1], pa_hi[a][2], k_lo, pa_lo[a][0], pa_lo[a][1], pa_lo[a][2],
                A.FROZEN_LABEL))
        rung_point = {k_hi: nu_hi, k_lo: nu_lo}
        rung_edges = {k_hi: e_hi, k_lo: e_lo}
        for k in cfg.rungs[1:-1]:
            e = A.blind_edges(A.make_board(rows_b, rosters[k], answers, "k%d" % k), cfg.B_inner, st, "boot/point/k%02d" % k)
            rung_point[k] = A.nu2(e, pair, anchors)[0]
            rung_edges[k] = e
        shares = {k: (A.called_share(rung_edges[k], pair, A.DISCLOSED_MODEL) if A.DISCLOSED_MODEL in rosters[k] else None)
                  for k in sorted(rosters)}
        integ = []
        for s in range(cfg.n_integrated):
            a_ = A.nu2(A.blind_edges(A.make_board(rows_b, rosters[k_hi], answers, "i"), cfg.B_inner, st,
                                     "boot/integrated/s%02d/k%02d" % (s, k_hi)), pair, anchors)[0]
            b_ = A.nu2(A.blind_edges(A.make_board(rows_b, rosters[k_lo], answers, "i"), cfg.B_inner, st,
                                     "boot/integrated/s%02d/k%02d" % (s, k_lo)), pair, anchors)[0]
            integ.append({"s": s, "nu_hi": a_, "nu_lo": b_, "beta": A.beta_of(a_, b_, k_hi, k_lo)})
        rows_by_q = defaultdict(list)
        for anc, a, b, q, w in rows_b:
            rows_by_q[(anc, q)].append((a, b, w))
        qs = {anc: sorted({r[3] for r in rows_b if r[0] == anc}) for anc in anchors}
        ctx = {"master": cfg.master, "anchors": anchors, "qs": qs, "rows_by_q": dict(rows_by_q), "answers": answers,
               "rosters": rosters, "k_hi": k_hi, "k_lo": k_lo, "B_rungs": cfg.B_rungs, "B_inner": cfg.B_inner, "pair": pair}
        tasks = A.draw_tasks(ctx, st, cfg.B_outer)
        recs = A.run_bootstrap(ctx, st, cfg.B_outer, workers, tasks=tasks)
        store = g22.RecordStore(final)
        store.put("c1_boot", recs)
        store.put("c1_integrated", integ)
        # [L7' F2] the match-level bootstrap (key-blind; the DEFF's denominator; decides nothing), same B as C1's
        rows_by_anchor = {anc: [(a, b, q, w) for anc2, a, b, q, w in rows_b if anc2 == anc] for anc in anchors}
        if MUTANT == "deff_off":
            deff = None
        else:
            recs_d = (recs if MUTANT == "deff_question_draws" else
                      A.match_bootstrap(dict(ctx, rows_by_anchor=rows_by_anchor), st, cfg.B_outer, workers))
            store.put("deff_match_boot", recs_d)
            deff = A.measured_deff([r["beta"] for r in recs], [r["beta"] for r in recs_d], len(rows_b))
        se_boot, se_dec, lo, hi, n_inf = A.c1_interval(beta_hat, [r["beta"] for r in recs], cfg.between_sd)
        m_exact = PL.exact_bar_M(cfg, k_hi)         # [0761cfa] THE EXACT M; refuses unless cfg.bar_M = round(it, 4)
        words, rl = A.c1_readings(beta_hat, lo, hi, cfg.bar_P, m_exact, n_inf=n_inf)
        say("  %s: nu_2(%d) %.4f | nu_2(%d) %.4f | beta-hat = [ln nu_2(%d) - ln nu_2(%d)] / ln(%d/%d) = %.4f (%s)" % (
            A.C1_MARK, k_hi, nu_hi, k_lo, nu_lo, k_hi, k_lo, k_hi, k_lo, beta_hat, A.FROZEN_LABEL),
            "  bootstrap: B %d (stream 'boot'); n_inf = %d non-finite replicate(s) (K7 ruling: any -> UNDETERMINED);"
            " SE_boot %.4f over the finite ones; SE_dec = sqrt(SE_boot^2 + %.2f^2 / 2) = %.4f; interval beta-hat +- 1.96"
            " SE_dec = [%.4f, %.4f]" % (len(recs), n_inf, se_boot, cfg.between_sd, se_dec, lo, hi),
            "  bars (registered): P EXCLUDED iff lower > %.2f; M EXCLUDED iff upper < THE EXACT M = ln(%d/%d) / ln(%d/%d)"
            " = %.6f, printed %.4f (M bar %.4f (exact, registered); amendment %s)" % (
                cfg.bar_P, k_hi * (k_hi - 1) // 2, k_lo * (k_lo - 1) // 2, k_hi, k_lo, m_exact, m_exact, cfg.bar_M,
                PL.AMENDMENT_K37))
        say(*rl)
        say(*A.disclosure_lines(plan.raw_counts, shares, "beside C1"))
        klass_counts = defaultdict(int)
        for m in plan.kept:
            klass_counts[plan.klass[m["match_id"]]] += 1
        klass_counts = dict(klass_counts)
        system_sha = C.sha256_text(PL.P.build_system(rubric))
        say(*A.f4_disclosure_lines(klass_counts, system_sha, "beside C1"))
        ib = np.array([x["beta"] for x in integ if np.isfinite(x["beta"])])
        if ib.size:
            say("  the integrated reading over %d inner-stream seeds (decides nothing): beta median %.4f, range [%.4f, %.4f]"
                % (len(integ), float(np.median(ib)), float(ib.min()), float(ib.max())))
        else:
            say("  the integrated reading over %d inner-stream seeds (decides nothing): no finite beta" % len(integ))
        n_called = {a: (pa_hi[a][1], pa_lo[a][1]) for a in anchors}
        sstats = {}
        for a in anchors:
            mq = [len(rows_by_q[(a, q)]) for q in qs[a]]
            sstats[a] = {"q_used": len(mq), "matches": sum(mq), "kish_m": (sum(x * x for x in mq) / sum(mq)) if mq else 0.0}
        say(*A.support_lines(se_boot, se_dec, sstats, n_called, deff=deff,
                             n_what="usable dual-order matches on the board (the match-level resample's units; %s)" %
                             ", ".join("%s %d" % (a, len(rows_by_anchor[a])) for a in anchors)))
        if A.MUTANT == "unseal_early":
            A.unseal_key(conn, cfg, set(plan.free["A"]), plan.roster, c1_path)
        report.write_once(c1_path, say.text())
        say("  [C1 WRITTEN] %s (write-once) before any key material is read" % c1_path)
        # ── after C1: the leak material (C0 (d) part 2), then the key
        loaded, order2 = PL.load_plan(plan, say)
        C.need(order2 == order_ids, "the loaded order differs from the plan's")
        n_out_loaded = PL.outside_roster([(s.contestant_a, s.contestant_b) for s in loaded.specs.values()], plan.roster)
        say("  (b) [F8] LOADED specs naming a model outside the roster: %d of %d (required 0; counted after C1, K4); board"
            " rows: %d (above); scheduled %d, cached %d (C0 (b))" % (n_out_loaded, len(loaded.specs), n_out_board,
                                                                   n_out_sched, n_out_cached))
        rows, n, hits = PL.scan_payloads(loaded, rubric, order_ids, say)
        same = all(rows_store.get((m, o)) == s for m, o, s in rows)
        d2 = bool(n == len(st_rec["verdicts"]) == 2 * len(order_ids) and not hits and same)
        hit("C0.d2.%s" % ("PASS" if d2 else "FAIL"))
        say("  (d) part 2 %s: the payload rebuild and the leak re-scan on %d payloads = %d verdict rows (100%% by count),"
            " hits %d, every rebuilt payload's sha equals the posted one: %s" % (
                "PASS" if d2 else "FAIL", n, len(st_rec["verdicts"]), sum(hits.values()), same))
        c2, by_var = c2_lines(plan, loaded)
        store.put("c2_variants", [dict(variant_id=v, **c) for v, c in sorted(by_var.items())])
        if not d2:
            hit("C0.D2_VOID")
            say("  C0 (d) FAILED after C1 was written: UNDETERMINED BY VALIDITY; the C1 file %s is VOID" % c1_path)
            say("  PREDICTIONS P3 (the ruling of 2026-09-25): C1 gives no reading", *A.p3_lines(False, words))
            say(*A.falsifier_lines(words, c0_pass=False))
            say(*c2)
            say(*st.summary())
            say.write(st)
            store.write_manifest()
            return {"c0": False, "path": final, "c1_path": c1_path, "void": True}
        loaded.materials.clear()
        K = A.unseal_key(conn, cfg, set(plan.free["A"]), plan.roster, c1_path)
    finally:
        conn.close()
    sb = AD.import_sb()

    def fitfn(E, x0=(-3.0, 3.0)):
        return sb.fit(E.edges, x0=x0)
    say("", "=== C3 BOTH NOMINALS (decides nothing; the key unsealed after C1 was written) ===")
    res = {}
    ratios = {}
    for k, eb in ((k_hi, e_hi), (k_lo, e_lo)):
        b = A.make_board(rows_b, rosters[k], answers, "c3 k%d" % k, key=K)
        res[k] = A.c3_board(say, b, st, "c3/k%02d" % k, pair, sb, fitfn, k, cfg.B_inner)
        kept_m, n_inf_e, n_fr = A.matched_edges(b, cfg.B_inner, st, "c3/matched/k%02d" % k)
        res[k]["matched_nu"] = A.nu2(kept_m, pair, anchors)[0]
        ratios[k] = (rung_point[k], res[k]["matched_nu"], len(eb), n_inf_e, n_fr)
    for k in (k_hi, k_lo):
        r = res[k]
        ratio = (r["frozen"] / r["loao"]) if r["loao"] > 0 else float("nan")
        say("  frozen / LOAO nominal ratio at k %d: %s (%s)" % (
            k, ("%.3f" % ratio) if np.isfinite(ratio) else "undefined (LOAO nominal 0)", A.FROZEN_LABEL))
    say("  GROK-CALIB's recorded 920-set LOAO nominal %.2f (its k 12, 14-anchor board) beside the k %d reference" % (
        A.GROK_CALIB_LOAO_920, k_lo))
    # ── the matched bootstrap (K5): the SAME question draws, both rungs key-informed
    ctx_m = dict(ctx, key=K)
    recs_m = A.run_bootstrap(ctx_m, st, cfg.B_outer, workers, tasks=tasks)
    store.put("c1b_matched_boot", recs_m)
    mt_hi, mt_lo = res[k_hi]["matched_nu"], res[k_lo]["matched_nu"]
    beta_m = A.beta_of(mt_hi, mt_lo, k_hi, k_lo)
    _seb, _sed, mlo, mhi, m_inf = A.c1_interval(beta_m, [r["beta"] for r in recs_m], cfg.between_sd)
    wm, rlm = A.c1_readings(beta_m, mlo, mhi, cfg.bar_P, m_exact, n_inf=m_inf,
                            what="beta_matched (descriptive; C1 decides)")
    say("", "=== C1b / C1c (descriptive) ===",
        "  beta_matched = [ln nu_2(%d) - ln nu_2(%d)] / ln(%d/%d) on the KEY-INFORMED levels = %.4f; same bootstrap (B %d),"
        " n_inf %d; interval [%.4f, %.4f] (%s)" % (k_hi, k_lo, k_hi, k_lo, beta_m, len(recs_m), m_inf, mlo, mhi,
                                                  A.FROZEN_LABEL))
    say(*rlm)

    def sd(v):
        v = np.array([x for x in v if np.isfinite(x)], dtype=float)
        return float(v.std(ddof=1)) if v.size > 1 else float("nan")
    lines, level_scored = A.c1b_lines(cfg, k_hi, nu_hi, sd([r["nu_k%02d" % k_hi] for r in recs]), mt_hi,
                                      sd([r["nu_k%02d" % k_hi] for r in recs_m]), beta_hat, beta_m, mlo, mhi, ratios)
    say(*lines)
    say(*A.disclosure_lines(plan.raw_counts, shares, "beside C1b"))
    say(*A.f4_disclosure_lines(klass_counts, system_sha, "beside C1b"))
    slopes = [A.slope_of(r, sorted(rosters)) for r in recs[:cfg.B_rungs]]
    rl2, _slope = A.rung_lines(rung_point, slopes)
    say(*rl2)
    say(*c2)
    say(*A.predictions_lines(True, beta_hat, level_scored, words, len(plan.before), len(plan.kept),
                             unusable_calls / max(1, len(st_rec["verdicts"])),
                             inv if MUTANT == "p5_journal_only" else inv_all, cfg,
                             prior=None if MUTANT == "p5_journal_only" else prior["invocations"]))       # [L7' G1] posted = journal + prior, as C0 (f)
    say(*A.falsifier_lines(words))
    say("  NOT SHOWN: a 14-anchor nominal as measured (Support (g)); any board-size decision (the reading sits beside the"
        " simulator and the memo); any certificate, order or calibration claim from the frozen pair off grok_calib's board.")
    say(*st.summary())
    say.write(st)
    store.write_manifest()
    return {"c0": True, "path": final, "c1_path": c1_path, "beta": beta_hat, "interval": (lo, hi), "words": words,
            "nu_hi": nu_hi, "nu_lo": nu_lo, "records": store.files, "beta_matched": beta_m, "matched_words": wm,
            "level_scored": level_scored, "matched_hi": mt_hi, "n_inf": n_inf, "deff": deff}
