"""ARCH-V2 E-A / gate G22: the arena simulator. ZERO judge calls; no DB written; no tree built.

REGISTRATION: NONE YET. G22 needs its own registration (criteria and a Support section) before any readout is of
record (author decisions docs/judge_v2_program.md L15070-L15084, "EACH GATE GETS ITS OWN REGISTRATION BEFORE CODE";
the engineering item ARCH-V2-E-A builds the instrument). Every bar below is the synthesis's (section 4, G22) or the
budget memo's (section 5) WORD, carried as a parameter and printed "provisional ... NOT registered". Outputs go only to
an explicit --out path, write-once (mode "x"), with the random-stream log beside (<out>.streams.tsv).

[REGISTERED 2026-09-24 at d6129cf (ARCH-V2-G22, docs/judge_v2_program.md L15208-L15265), inserted by the engine-coder;
the sentences above are kept as written and read with this bracket: the bars are now REGISTERED (c) P(nominal >= 9) >= 0.8,
(d) identification >= 0.8, (e) P(MISCALIBRATED | calibrated) <= 0.05, each read by its Wilson 95% interval; validity is
every target inside its central (1 - 0.05 / T) interval (Bonferroni, T printed); both counts printed and neither decides
the status word (author decision 8 open). A RECORD RUN uses --master ARCHV2-G22-REC-1 (the default) and R = 1,000 (the
default); any other master or R refuses unless --dev (not of record) or, for R, --r-registration "<programme ref>" naming
a smaller R registered before the run. --dry-run prints its extrapolated wall time at R = 1,000.]

LEGS (budget memo section 5 numbering in brackets)
  --leg validity        (a) [5.1] fitted on the grok calibration cache (grok_calib.db, x12 schedule, 12 models): must
                        reproduce raw 733 / 7 on 891 edges, the LOAO counts (667 / 2 (1) / 1.11; 920: 653 / 2 (1) / 1.24)
                        and a delta-deviance range covering 4.47 (GROK-CALIB) and 2.26 (the Kotlin draw, JUDGE-WIRING-BOARD).
                        Writes the VALIDITY TOKEN (<out>.validity.json). A FAIL token makes (c), (d), (e) refuse.
  --leg nu              (b) [5.2] nu(k, N) by SUBSAMPLING the merged Mistral board (x12 + x20, 20 models) or grok_calib
                        (12), k = 8 ... max, N = 2 / 3 / 5 / full; exponent with a bootstrap CI. Model-free.
  --leg designs         (c) [5.3] P(nominal >= 9) for D0, D4, D1-stage1, D1-full, D2 at the DEV split's EVAL supply
                        (the E-D DEV manifest, read by `git show`, or --supply-json); (d) [5.4] b1 identification rate
                        under the filter over re-draws; (g) [5.7] DEFF at the designs' reuse (D1: about 8.4).
  --leg stop            (e) [5.5] the key-blind stop: P(MISCALIBRATED | calibrated simulated judge) <= 0.05, and the
                        map frozen-pair nominal -> LOAO-refit nominal.
  --leg overdispersion  (f) [5.6] wrong(established) across models and anchors on grok_calib / x12 / merged; DEFF of the
                        wrong indicator; the residue model RESOLVED FROM THE DATA and its roster membership.
  --leg coverage        (h) [5.8] D_c >= 0.95 per anchor for the 46-model roster; the frontier band from key tiers.
  --selftest            every leg and every decision branch on SYNTHETIC worlds in a temp dir; opens no DB of record;
                        single process; passes under python and python -O.

LAUNCH SEQUENCE (heavy legs run ONLY in a CPU window admitted by rule 7; each is a pool reader)
  python tools/analysis/archv2_g22_sim.py --selftest
  python tools/analysis/archv2_g22_sim.py --leg validity --out <dir>/G22_validity.txt [--R 200 --B 300 --workers N]
  python tools/analysis/archv2_g22_sim.py --leg nu --board merged --out <dir>/G22_nu_merged.txt
  python tools/analysis/archv2_g22_sim.py --leg designs --token <dir>/G22_validity.txt.validity.json --out ...
  python tools/analysis/archv2_g22_sim.py --leg stop --token ... --out ...
  python tools/analysis/archv2_g22_sim.py --leg overdispersion --out ...
  python tools/analysis/archv2_g22_sim.py --leg coverage --out ...
  (TAXOARENA_DATA_ROOT must name the checkout that holds the DBs when run from a worktree.)

HYGIENE. First printed line: pool_guard.assert_pool_of_record(p2dca21ab5f4ef3ae) (legs that read the MMLU-Pro key). Every
DB through archv2_arena.ro.open_ro (the -wal / -journal refusal, then mode=ro&immutable=1); a process-wide connect guard
refuses any other open; snapshots_frozen.db and the 20NG DB are refused by name; stack_judge is never imported (a
stub stands in; systematic_budget's functions of record are imported behind it). Every random stream is named and
seeded from --master; the log is written beside the output.
"""
import argparse
import contextlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from archv2_arena import ro  # noqa: E402

ro.install_global_guard()
from archv2_arena import cert, data, design, g22, report  # noqa: E402
from archv2_arena.streams import Streams  # noqa: E402

MANIFEST_DEV = "worktree-agent-a11f8bf63949fabe0:data_v2/manifests/DEV_DEV-20260923-ED1.json"
MODULES = ("archv2_g22_sim.py", "archv2_arena/__init__.py", "archv2_arena/streams.py", "archv2_arena/ro.py",
           "archv2_arena/bt.py", "archv2_arena/cert.py", "archv2_arena/verdict_model.py", "archv2_arena/data.py",
           "archv2_arena/design.py", "archv2_arena/g22.py", "archv2_arena/report.py", "archv2_arena/synth.py",
           "archv2_arena/selftest_g22.py", "archv2_arena/selftest_g22_v2.py", "archv2_arena/g23.py",
           "archv2_arena/selftest_g22_rebind.py")


def identity_lines():
    out = ["  instrument identity (git blob / sha256-lf16 of the LF rendering; working tree state):"]
    for m in MODULES:
        i = data.file_identity(os.path.join(HERE, m))
        out.append("    %-34s blob:%s sha256-lf16:%s (%s)" % (m, i["blob"], i["sha256_lf16"], i["worktree"]))
    return out


def header(say, args, needs_pool=True):
    if needs_pool:
        import pool_guard
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pid = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
        # [FIX 2026-09-24, engine-coder, before any record output: assert_pool_of_record RETURNS the id and prints
        # nothing, so the first line was empty of the pool id; it is now printed from the returned value.]
        say("[POOL] %s: pool_guard.assert_pool_of_record PASSED (the id file and the reserved_pool rows both hash to it;"
            " the guard's own read-only open of the eval DB is not in the DB-open log below)" % pid)
        for line in buf.getvalue().rstrip("\n").split("\n"):
            if line:
                say(line)
    say("=== ARCH-V2 G22 SIMULATOR, leg %s: %s ===" % (args.leg, record_word(args)), report.argv_line(),
        "  master %r | data root %s | started %s" % (args.master, data.DATA_ROOT, time.strftime("%Y-%m-%d %H:%M:%S")))
    say(*identity_lines())


REC_MASTER = "ARCHV2-G22-REC-1"
REC_R = 1000
RATE_LEGS = ("validity", "validity-v2", "designs", "stop")


def record_word(args):
    rec = getattr(args, "rec_master", REC_MASTER)
    name = getattr(args, "reg_name", "ARCH-V2-G22")
    if getattr(args, "dev", False) or args.master != rec:
        return "DEV RUN, NOT OF RECORD (master %r)" % args.master
    if getattr(args, "dry_run", False):
        return ("DRY-RUN (writes nothing; R 1 per unit) of a leg registered as %s at d6129cf (programme L15208-L15265)%s,"
                " master %s" % (name, "; v2 under rulings 83f431b, 4b25059, 97f3a1f" if getattr(args, "leg", "") == "validity-v2"
                                else "", args.master))
    return ("RUN UNDER THE REGISTRATION %s at d6129cf (programme L15208-L15265)%s, master %s%s%s"
            % (name, "; v2 under rulings 83f431b, 4b25059, 97f3a1f" if getattr(args, "leg", "") == "validity-v2" else "",
               args.master, (", R %d" % args.R) if getattr(args, "R", None) else "",
               (", R registered by: %s" % args.r_registration) if getattr(args, "r_registration", None) else ""))


def check_record_params(a):
    """A record run uses the registered master and R = 1,000 (d6129cf); anything else is --dev or refuses."""
    if a.dry_run or a.dev:
        return
    if a.master != REC_MASTER:
        report.hit("RECORD.REFUSED_MASTER")
        raise SystemExit("[G22] --master %r is not the registered ARCHV2-G22-REC-1 (d6129cf): refused (use --dev for a run"
                         " that is not of record)" % a.master)
    if a.leg in RATE_LEGS and a.R != REC_R and not a.r_registration:
        report.hit("RECORD.REFUSED_R")
        raise SystemExit("[G22] --R %d is not the registered R = 1,000 (d6129cf): a smaller R must be REGISTERED before the"
                         " run and named with --r-registration \"<programme ref>\"; refused" % a.R)


def input_lines(paths):
    out = ["  inputs (size, mtime; -wal / -journal sizes):"]
    for p in paths:
        st = os.stat(p)
        side = []
        for suf in ("-wal", "-journal"):
            if os.path.exists(p + suf):
                side.append("%s %d B" % (suf, os.path.getsize(p + suf)))
        out.append("    %s | %d B | mtime %s | %s" % (p, st.st_size, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                                                   ", ".join(side) or "no sidecar"))
    return out


def load_board(which):
    import rubric_p8 as p8
    route, anchor_of, snap = data.load_routing()
    if which == "merged":
        r12, _ = data.load_verdicts(data.path("x12"))
        r20, _ = data.load_verdicts(data.path("x20"))
        rows = r12 + r20
        models = sorted({r[0] for r in rows} | {r[1] for r in rows})
        paths = [data.path("x12"), data.path("x20")]
    else:
        rows, has_votes = data.load_verdicts(data.path(which))
        models = sorted(p8.ARENA12)
        paths = [data.path(which)]
    kt = data.KeyTable(data.path("eval"), models=set(models))
    b = data.Board(rows, route, anchor_of, models, kt, which)
    return b, kt, snap, paths + [data.path("eval"), data.path("snapshots")]


def finish(say, out, streams, a=None, planned=None, T0=None):
    say("", "  EXECUTION WITNESS (new code paths): %s" % dict(sorted(data.WITNESS.items())))
    say(*ro.log_lines())
    say(*streams.summary())
    if a is not None and a.dry_run:
        el = time.time() - T0
        say("  DRY-RUN: nothing written; wall %.1f s at R = 1 per unit | EXTRAPOLATED AT THE REGISTERED R = 1,000: about"
            " %.1f h single-process (divide by --workers) | at the requested R %d (nu reps %d): about %.1f h"
            % (el, el * REC_R / 3600.0, planned["R"], planned["nu_reps"],
               el * max(planned["R"], planned["nu_reps"]) / 3600.0))
        return
    p = out.write(streams)
    print("[G22] written: %s (+ .streams.tsv)" % p)


def supply_from(args, keytabs, strata_pools):
    if args.supply_json:
        sup = json.load(open(args.supply_json, encoding="utf-8"))
        return {c: {k: int(v) for k, v in d.items()} for c, d in sup.items()}, "explicit --supply-json %s" % args.supply_json
    man = design.manifest_from_git(args.manifest_git)
    units, label, of_record = design.manifest_eval_units(man)
    sup = {}
    for corpus, key in (("mmlu", "mmlu-pro-v2"), ("union", "mc6-2026-09-11")):
        if corpus in strata_pools:
            sizes = {s: len(v) for s, v in strata_pools[corpus].items()}
            sup[corpus] = design.allocate(units[key], sizes)
    return sup, ("manifest %s (%s, %s): eval_units %s, ALLOCATED IN PROPORTION TO STRATUM SIZES (arithmetic, not the"
                 " split's per-anchor counts)" % (args.manifest_git, label, of_record, units))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="load everything, run ONE replicate per unit, time it, write nothing")
    ap.add_argument("--leg", choices=("validity", "validity-v2", "nu", "designs", "stop", "overdispersion", "coverage"))
    ap.add_argument("--out")
    ap.add_argument("--master", default=REC_MASTER)
    ap.add_argument("--dev", action="store_true", help="a run that is NOT of record (any master / R)")
    ap.add_argument("--r-registration", default=None, help="the programme reference registering a smaller R")
    ap.add_argument("--R", type=int, default=REC_R)
    ap.add_argument("--B", type=int, default=300)
    ap.add_argument("--floor", type=int, default=200)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--board", default=None, help="validity: grok (default); nu: merged (default) or grok")
    ap.add_argument("--token")
    ap.add_argument("--designs", default="D4,D1-stage1,D1-full,D0,D2")
    ap.add_argument("--manifest-git", default=MANIFEST_DEV)
    ap.add_argument("--supply-json")
    ap.add_argument("--deff-reps", type=int, default=20)
    ap.add_argument("--ks", default=None)
    ap.add_argument("--Ns", default="2,3,5,full")
    ap.add_argument("--nu-reps", type=int, default=20)
    ap.add_argument("--nu-floor", type=int, default=0)
    ap.add_argument("--margins", default="0,1,2,3")
    ap.add_argument("--boards", default="grok,x12,merged")
    ap.add_argument("--builder", choices=("exact", "fast"), default="exact")
    ap.add_argument("--eval-ids")
    ap.add_argument("--replay-record", default=None,
                    help="validity-v2 REPLAY MODE (G22-REBIND-1): the recorded output to reproduce byte for byte; no ONE_SHOT,"
                         " no token; its token of record is <path>.validity_v2.json unless --replay-token is given")
    ap.add_argument("--replay-token", default=None)
    ap.add_argument("--author-d0d2", action="store_true",
                    help="run D0 / D2 on the AUTHOR'S request (ruling 2 (iv)); without it they print NOT RUN")
    a = ap.parse_args(argv)
    if a.selftest:
        from archv2_arena import selftest_g22
        return selftest_g22.run()
    if not a.leg:
        ap.error("--leg or --selftest is required")
    if not a.out and not a.dry_run:
        ap.error("--out is required (write-once; no default path: nothing here is of record)")
    check_record_params(a)
    planned = dict(R=a.R, nu_reps=a.nu_reps)
    if a.dry_run:
        a.out = None
        a.R, a.nu_reps, a.deff_reps = 1, 1, 1
    T0 = time.time()
    out = report.Out(a.out)
    streams = Streams(a.master)
    sb = data.import_sb()
    say = out
    header(say, a, needs_pool=True)

    if a.leg == "validity":
        which = a.board or "grok"
        board, kt, snap, paths = load_board(which)
        say(*input_lines(paths))
        say("  board %s: %d valid verdicts, %d routed, anchors %d, models %d; routing tree %s snapshot %s"
            % (which, board.n_valid, sum(len(v) for v in board.by.values()), len(board.by), len(board.models), data.TREE, snap))
        store = None if a.dry_run else g22.RecordStore(a.out)      # G22-REBIND-1: additive per-replicate storage
        tok, _ = g22.validity_leg(say, board, sb, streams, R=a.R, B=a.B, floor=a.floor,
                                  workers=a.workers, store=store)
        tok.update(board=which, out=a.out, inputs=input_lines(paths))
        if not a.dry_run:
            report.write_once(a.out + ".validity.json", json.dumps(tok, indent=1, sort_keys=True, default=str))
        finish(say, out, streams, a, planned, T0)
        if store is not None:
            store.write_manifest()
        return 0

    if a.leg == "validity-v2":
        # ruling 1 (ii)-(v) of 83f431b: the POST-HOC-SPECIFIED fresh-judge v2 mode, ONE SHOT, run order (2)
        replay = a.replay_record is not None
        record = not (a.dev or a.dry_run or replay)          # a REPLAY never claims the one shot (G22-REBIND-1)
        if record:
            # READY 5dfc825 D3: ONE SHOT ENFORCED: the fixed record path is claimed before anything is computed
            say("  ONE SHOT: claimed %s" % g22.one_shot_claim(a.out, a.master))
        which = a.board or "grok"
        board, kt, snap, paths = load_board(which)
        say(*input_lines(paths))
        say("  board %s: %d valid verdicts, %d routed, anchors %d, models %d; routing tree %s snapshot %s"
            % (which, board.n_valid, sum(len(v) for v in board.by.values()), len(board.by), len(board.models), data.TREE, snap))
        if a.dry_run:
            # READY 5dfc825 D4: a v2 dry-run prints TIMINGS ONLY; every validity figure is suppressed (the one shot stays unseen)
            tok, _ = g22.validity_v2_leg(lambda *lines: None, board, sb, streams, R=1, B=a.B, floor=a.floor, workers=1)
            tm = tok["timing"]
            say("  DRY-RUN v2 (validity figures SUPPRESSED; timings only): fixed stage %.1f s (fits, LOMO refits, the H2 builder"
                " of record: ONCE) | per replicate %.2f s (3 part-A modes + 1 part-B draw) | EXTRAPOLATED AT THE REGISTERED"
                " R = 1,000: about %.2f h single-process = fixed + 1,000 x per replicate (divide the replicate part by"
                " --workers)" % (tm["fixed_s"], tm["per_rep_s"], (tm["fixed_s"] + 1000 * tm["per_rep_s"]) / 3600.0))
            say(*ro.log_lines())
            return 0
        if replay:
            # G22-REBIND-1 ruling 1 (ii): the REPLAY at the recorded master / R / half seed; NO one shot, NO token
            store = g22.RecordStore(a.out)
            rv = g22.replay_v2(say, board, sb, streams, a.replay_record, store, token_path=a.replay_token,
                               R=a.R, B=a.B, floor=a.floor, workers=a.workers)
            finish(say, out, streams, a, planned, T0)
            store.write_manifest()
            return 0 if rv["ok"] else 3
        store = g22.RecordStore(a.out)                            # G22-REBIND-1: additive per-replicate storage
        tok, _ = g22.validity_v2_leg(say, board, sb, streams, R=a.R, B=a.B, floor=a.floor, workers=a.workers, store=store)
        tok.update(board=which, out=a.out, inputs=input_lines(paths), record=record,
                   r_registration=a.r_registration, dev=bool(a.dev))
        tok = g22.seal_token(tok)          # READY 5dfc825 D2: the WHOLE token sealed, bound to the instrument's lf16
        say("  token sealed: instrument lf16 %s | record %s | token_digest (in full) %s"
            % (tok["instrument_lf16"], record, tok["token_digest"]))
        report.write_once(a.out + ".validity_v2.json", json.dumps(tok, indent=1, sort_keys=True, default=str))
        finish(say, out, streams, a, planned, T0)
        store.write_manifest()
        return 0

    if a.leg == "nu":
        which = a.board or "merged"
        board, kt, snap, paths = load_board(which)
        say(*input_lines(paths))
        pair, label = ((cert.FROZEN_MISTRAL_920, "Mistral 920 pair") if which in ("merged", "x12")
                       else (cert.FROZEN_GROK_UNFILTERED, "GROK-CALIB 920 pair"))
        ks = [int(x) for x in a.ks.split(",")] if a.ks else list(range(8, len(board.models) + 1, 2 if len(board.models) > 12 else 1))
        if len(board.models) not in ks:
            ks.append(len(board.models))
        Ns = [x if x == "full" else int(x) for x in a.Ns.split(",")]
        g22.nu_leg(say, board, streams, pair, ks, Ns, reps=a.nu_reps, B=a.B, floor=a.nu_floor, pair_label=label)
        finish(say, out, streams, a, planned, T0)
        return 0

    if a.leg in ("designs", "stop"):
        tok, vm = g22.load_token(a.token, need_v2=True, dev=a.dev)   # run order (3): ONLY IF v2 PASSES (a RECORD token)
        names = g22.declared_deviation(a.designs.split(","), a.author_d0d2, say) if a.leg == "designs" else ["D1-full"]
        need_union = any(p["corpus"] == "union" for n in names for p in design.MEMO_DESIGNS[n])
        keytabs = {"mmlu": data.KeyTable(data.path("eval"))}
        paths = [data.path("eval")]
        if need_union:
            keytabs["union"] = data.KeyTable(data.path("multicorpus"), stratum="source_domain",
                                             missing_sources=("BBH", "MUSR"))       # ruling 2, 83f431b
            paths.append(data.path("multicorpus"))
        rosters = {"mmlu46": [m for m in keytabs["mmlu"].all_models if m != data.QUARANTINED]}
        if "union" in keytabs:
            rosters["union18"] = keytabs["union"].all_models
        if any(p["roster"] == "x20merged" for n in names for p in design.MEMO_DESIGNS[n]):
            r12, _ = data.load_verdicts(data.path("x12")); r20, _ = data.load_verdicts(data.path("x20"))
            rosters["x20merged"] = sorted({r[0] for r in r12 + r20} | {r[1] for r in r12 + r20})
            paths += [data.path("x12"), data.path("x20")]
        say(*input_lines(paths))
        if "union" in keytabs:
            say("  union key: BBH and MuSR extracted answers set MISSING (ruling 2, 83f431b): %d (question, model) answers"
                % keytabs["union"].n_missing)
        say("  rosters: %s" % ", ".join("%s %d" % (k, len(v)) for k, v in rosters.items()),
            "  category data check (MMLU-Pro eval_results): %d question ids carry more than one normalised category;"
            " the anchor is the modal value" % keytabs["mmlu"].cat_conflicts)
        strata_pools = {}
        for c, kt in keytabs.items():
            pools = {}
            for q, s in kt.strata.items():
                if q in kt.K:
                    pools.setdefault(s, []).append(q)
            strata_pools[c] = {s: sorted(v) for s, v in pools.items()}
        supply, sup_label = supply_from(a, keytabs, strata_pools)
        say("  supply: %s" % sup_label)
        for c, d in supply.items():
            say("    %s: %d strata, %d EVAL questions: %s" % (c, len(d), sum(d.values()),
                                                           ", ".join("%s %d" % (k, v) for k, v in sorted(d.items()))))
        designs = g22.resolve_designs(names, rosters, supply, strata_pools, streams)
        if a.leg == "designs":
            store = None if a.dry_run else g22.RecordStore(a.out)
            g22.designs_leg(say, tok, vm, designs, keytabs, streams, R=a.R, B=a.B, floor=a.floor,
                            deff_reps=a.deff_reps, workers=a.workers, store=store)
        else:
            store = None if a.dry_run else g22.RecordStore(a.out)
            g22.stop_leg(say, tok, vm, designs["D1-full"][0], keytabs["mmlu"], streams, R=a.R, B=a.B, floor=a.floor,
                         margins=tuple(float(x) for x in a.margins.split(",")), workers=a.workers, store=store)
        finish(say, out, streams, a, planned, T0)
        if store is not None:
            store.write_manifest()
        return 0

    if a.leg == "overdispersion":
        kt_all = data.KeyTable(data.path("eval"), with_len=False)
        roster46 = [m for m in kt_all.all_models if m != data.QUARANTINED]
        p7_results = {}
        for which in a.boards.split(","):
            board, kt, snap, paths = load_board(which)
            say(*input_lines(paths))
            if a.builder == "exact":
                edges, aq = data.edges_exact(board, B=a.B, floor=a.floor, streams=streams)
                say("  builder: EXACT (build()'s loop, random.Random(42), rj.mm_fit) - the edge objects of record")
            else:
                edges, aq = data.edges_fast(board, a.B, streams, "overdispersion/%s" % which, floor=a.floor)
                say("  builder: FAST (numpy boards, stream overdispersion/%s)" % which)
            data.mark_established(edges, board.K, aq, sb)
            od = g22.overdispersion_leg(say, board, edges, streams, roster_models=roster46, all_models=kt_all.all_models,
                                        fit=lambda E, x0=(-3.0, 3.0): sb.fit(E.edges, x0=x0), board_key=which,
                                        builder=a.builder)
            p7_results[which] = od if od is not None else dict(residue=None, n_called_wrong=0)
        failed = [w for w, r in p7_results.items() if r.get("residue") == "STOPPED"]
        if failed:
            # READY 5dfc825 D6: a FAILED PRECONDITION exits non-zero and writes no readable residue or P7 result
            say("", "  FAILED PRECONDITION on %s (ruling B): NO residue model and NO P7 result are read; exit 2" % ", ".join(failed))
            if out.path is not None:
                out.path = out.path + ".FAILED-PRECONDITION.txt"
            finish(say, out, streams, a, planned, T0)
            return 2
        lines, _ = g22.p7_score(p7_results, roster46)
        say(*lines)
        finish(say, out, streams, a, planned, T0)
        return 0

    if a.leg == "coverage":
        kt_all = data.KeyTable(data.path("eval"), with_len=False)
        roster46 = [m for m in kt_all.all_models if m != data.QUARANTINED]
        say(*input_lines([data.path("eval")]))
        say("  roster: %d models in the eval DB, %d after the quarantine of %s" % (len(kt_all.all_models), len(roster46), data.QUARANTINED),
            "  category data check: %d question ids carry more than one normalised category; the anchor is the modal value"
            % kt_all.cat_conflicts)
        ids = None
        if a.eval_ids:
            ids = set(json.load(open(a.eval_ids, encoding="utf-8")))
        strata_of = {q: s for q, s in kt_all.cat.items() if q in kt_all.K}
        report.need(len(strata_of) > 0, "eval_results carries no category column: the anchors cannot be read")
        g22.coverage_leg(say, kt_all, roster46, strata_of, eval_ids=ids)
        g22.key_tier_lines(say, kt_all, roster46, strata_of)
        finish(say, out, streams, a, planned, T0)
        return 0


if __name__ == "__main__":
    sys.exit(main())
