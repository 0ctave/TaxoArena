"""ARCH-V2-PILOT-K46: the key-blind nominal per anchor at k = 46 on 2 anchors of the split of record, and the exponent
beta-hat between its k = 12 and k = 46 sub-boards (zero calls in this build; a run posts at most 8,000).
[AMENDED 2026-09-25 BEFORE ANY CODE (0761cfa, docs/judge_v2_program.md L16787-L16992; the author's decision (2)), insertion
only: k = 37, not 46 -- the nominal nu_2(37) and beta-hat between the k = 12 and k = 37 sub-boards; the roster is the 46
ACTIVE minus the 9 EvalIngestValidator.BANNED_MODELS entries (roster sha256-text 3a3204cc...6f91); at most 2,664 matches /
5,328 calls (no trim). The ID, the CLI, the store path, the run id and the "K46-" match ids are UNCHANGED.]

REGISTRATION: docs/judge_v2_program.md L15913-L15955 (3a12115), amended BEFORE ANY CODE L15975-L15983 (2296877: C1 = the
exponent, SCOREABLE; the trim keeps ARENA12 pairs; C1b / C1c descriptive); open item 1 (the rubric slot) ruled
L15957-L15962 (INDUCE-RUBRIC-1, L15964-L15973); items 2 (the anchors: 2 of the REGISTERED stage-1 7) and 3 (the frozen
GROK-CALIB unfiltered pair, a planning scale only; C3 decides nothing) ruled L15985-L15994 (53eccb6). The author's cap:
at most 8,000 calls (Amendment 18, L15909-L15911). The method: archv2_pilot.pilot (schedule, trim, judged path, guards),
archv2_pilot.analysis + archv2_pilot.outcome (C0-C3), archv2_pilot.accounting (the ceiling and the day cap).

LAUNCH SEQUENCE (the operator, after a READY; FLOW build -> READY -> dry-run -> pilot 12 -> run -> post-run review ->
outcome; the posting day must be 2026-09-25 or later; every mode needs the stage-1 record and the rubric artefact named
by BOTH shas):
  python tools/analysis/archv2_pilot_k46.py --selftest                                       (python and python -O)
  python tools/analysis/archv2_pilot_k46.py --dry-run --stage1 S1.json --rubric-artefact R.json \
      --rubric-artefact-sha256 <a> --rubric-sha256 <r>          (full schedule, counts, the payload scan on 100% of the
                                                                 payloads, the anchor / order / payload-anchor shas; posts
                                                                 nothing, writes nothing unless --out)
  python tools/analysis/archv2_pilot_k46.py --pilot 12 --go ... --expect-payload-anchor <p> --expect-order-sha <o>
  python tools/analysis/archv2_pilot_k46.py --run --go ... --expect-payload-anchor <p> --expect-order-sha <o>
  python tools/analysis/archv2_pilot_k46.py --analyze ... --out experiment_results/archv2/pilot_k46/PILOT_K46_outcome.txt
      [--workers 4]   (C0 first; C1 written before the key is unsealed; _PARTIAL output from an incomplete cache)
Without --go a launch prints the accounting and what it would post, and posts nothing.
[RE-PINNED to the split of record 5a3e756, insertion: --stage1 now defaults to the RE-DRAW's output
experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json (ARCH-V2-STAGE1-ANCHOR-DRAW-2); its sha256 and
anchors are pinned after that draw (until then a record run refuses). The 1463759 values below are superseded.]
[READY 65a9173, insertion] --stage1 defaults to the committed record (1463759)
experiment_results/archv2/stage1_anchor_draw/archv2_stage1_anchors.json under the MAIN checkout, sha256-bytes
08cdff0e314dce5520bca8316e3a74a94845c64850fe8956c99b6d875ffb6140, pinned in record mode (anchors business, history, math,
other, philosophy, physics, psychology); --ledger-dir defaults to the MAIN checkout's experiment_results/ and a record launch
refuses any other (K9); every post goes through the write-ahead journal <store>.invocations.db (K1); the judge pins are
f5bbbda's with induction.py = INDUCE-RUBRIC-1's blob, which must also be main's (K2).
[RE-PINNED 2026-09-24, insertion: the stage-1 re-draw ran once (e4f0658); --stage1's record is pinned by sha256-lf
777e2f6a4cd8ee0d1ce92659f8c3ad4f72a45319d166135dd918575d0ace5e43 (LF rendering, CRLF -> LF; READY a254a1d MEDIUM-1) and
blob:7b7a41d8d7b285b663eba3fbf4ba2d8bb38c883c, anchors chemistry, computer science, economics, health, math, other,
philosophy. The judge pins are MAIN 06a17be's: f5bbbda's with judge_v2/_base.py blob:6f25e4ce... and judge_v2/induction.py
blob:f4d65f59... (the merged INDUCE-RUBRIC-1 D1 amendment, not 0de6153f), induction.py also = main's (K2).]
[RE-PINNED 2026-09-25, insertion only; the author's PRE-DECIDED FALLBACK (docs/judge_v2_program.md L16994-L17006; the
-3 registration's FALLBACK L17072), the registrar's record of the INDUCE-RUBRIC-3 outcome PENDING: ARCH-V2-INDUCE-RUBRIC-3
was read UNFIT (checklist reader B, K8 and K3b) -> NOT ADOPTED, so the rubric slot holds GENERIC_RUBRIC
(rubric_value_contrast.GENERIC_RUBRIC, sha256-text 67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc),
imported and checked by sha (pilot.load_generic_rubric): NO rubric argument is needed, --rubric-sha256 is an optional
witness (refused when it differs), and a record run REFUSES --rubric-artefact / --rubric-artefact-sha256. The launch
sequence above reads without the three rubric arguments. The judge pins are MAIN b653b0a's (induction.py
blob:147e6874..., a layer-identity pin; the other six unchanged), each also = main's actual blob (K2).]
[2026-09-25, after the pilot-12 transport incident (insertion only; incident copy
experiment_results/archv2/pilot_k46_incident_2026-09-25/): every mode except --analyze / --selftest loads the credentials
from the DATA ROOT's .env (TAXOARENA_DATA_ROOT, else the main checkout; pilot.load_transport, values never printed) and
runs pilot.transport_preflight ("TRANSPORT PREFLIGHT: OK (endpoint host=..., deployment=...)") BEFORE the plan, the store,
the journal and the ledger; the dry-run runs it too. --store defaults to pilot_k46_verdicts_run2.db; the retired
pilot_k46_verdicts.db is REFUSED in record mode; its journal's 24 booked invocations (sha256 995087c3...) are counted on
the journal side of every ledger == journal check (pilot.PRIOR_JOURNALS).]
[ADDED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239), insertion only:
--post-workers N (default 1) is the POSTING pool's in-flight bound, passed to pilot.launch(workers=N); --workers stays the
--analyze option it was (a different knob; not renamed). At 1 the launch is today's. The dry-run and a launch without --go
print the [POOL] line (workers, the journal's max_inflight). A first live use at N > 1 is registered as that run's own
launch parameter (0.4 (4)); the K46 run itself finishes on its build of record 5e9de0f and is never relaunched by this one.
The RATE CONTROL (judge_v2.pool; the coordinator's requirements of 2026-09-25): --max-rpm R (a global token bucket over
all workers; default 20 on a pooled launch), --request-timeout-s T (default 120), --breaker-k K (default 8). Any of the
three makes the launch POOLED even at --post-workers 1 (the single poster rate-controlled, on a journal v2); none of them
and --post-workers 1: today's launch.]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from archv2_pilot import common as C  # noqa: E402

# [2026-09-25 incident] the first store (pilot_k46_verdicts.db) is RETIRED (pilot.check_store_path refuses it in record
# mode); the store of record is run2
DEFAULT_STORE = os.path.join(C.ROOT, "experiment_results", "archv2", "pilot_k46", "pilot_k46_verdicts_run2.db")


def streams_lines(st):
    """The stream log's count and sha (no .streams.tsv is claimed: only --analyze writes one)."""
    return ["  RANDOM STREAMS (master %r): %d named streams, log sha256 %s (seed = sha256(master|name)[:8] big-endian;"
            " the log is not written by this mode)" % (st.master, len(st.log), st.digest())]


def script_blob():
    return "blob:%s+archv2_pilot:%s" % (C.dv2ro.git_blob_lf(os.path.abspath(__file__)), C.package_lf16())


def header(cfg, say):
    from archv2_pilot import pilot as PL
    ok, bad = PL.judge_pins_ok(cfg)
    say("ARCH-V2-PILOT-K46: %s" % PL.word(cfg),
        "  code: %s | frozen instrument lf16 %s (read-only) | judge_v2 pins (%s) %s" % (
            script_blob(), C.check_instrument(), cfg.judge_pins, "EQUAL" if ok else "DIFFER: %s" % bad),
        "  persona GENERIC_SYSTEM text sha256 %s" % PL.persona_sha())
    C.need(ok, "C0 (c): the judge layer's pins differ from the expected (%s)" % cfg.judge_pins)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--pilot", type=int)
    g.add_argument("--run", action="store_true")
    g.add_argument("--analyze", action="store_true")
    ap.add_argument("--eval-view", default=None)
    ap.add_argument("--stage1")
    ap.add_argument("--rubric-artefact")
    ap.add_argument("--rubric-artefact-sha256")
    ap.add_argument("--rubric-sha256")
    ap.add_argument("--store", default=DEFAULT_STORE)
    ap.add_argument("--ledger-dir", default=None)
    ap.add_argument("--expect-payload-anchor")
    ap.add_argument("--expect-order-sha")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--post-workers", type=int, default=1)      # [JV2-PARALLEL-POSTING] the posting pool's N
    ap.add_argument("--max-rpm", type=int, default=None)          # [JV2-PARALLEL-POSTING] the global token bucket
    ap.add_argument("--request-timeout-s", type=float, default=None)
    ap.add_argument("--breaker-k", type=int, default=None)
    a = ap.parse_args(argv)
    rate = None
    if a.max_rpm is not None or a.request_timeout_s is not None or a.breaker_k is not None:
        from judge_v2 import pool as POOL
        kw = {k: v for k, v in (("max_rpm", a.max_rpm), ("request_timeout_s", a.request_timeout_s),
                                ("breaker_k", a.breaker_k)) if v is not None}
        rate = POOL.RateConfig(**kw)
    if a.selftest:
        from archv2_pilot import selftest
        return selftest.main(["--part", "all"])
    from archv2_pilot import pilot as PL
    from archv2_pilot import outcome as OC
    from judge_v2 import payload as P
    from judge_v2._base import rr
    cfg = PL.Config()
    header(cfg, lambda *lines: [print(s) for s in lines])     # one line each (was print(*lines): one joined line)
    a.stage1 = a.stage1 or PL.default_stage1_record()
    a.ledger_dir = a.ledger_dir or PL.main_ledger_dir()
    C.need(a.ledger_dir, "no ledger directory: the main checkout could not be located (K9)")
    PL.check_ledger_dir(a.ledger_dir, cfg)
    print("  stage-1 record: %s" % os.path.abspath(a.stage1))
    # [2026-09-25] the slot of record is GENERIC_RUBRIC by sha (the INDUCE-RUBRIC-1 artefact path is disclosure only)
    PL.check_rubric_args(cfg, a.rubric_artefact, a.rubric_artefact_sha256)
    rubric, of_record = PL.load_generic_rubric(record=cfg.record(), rubric_sha256=a.rubric_sha256)
    for s in PL.rubric_slot_lines(rubric):
        print(s)
    print("    of record: %s" % of_record)
    P.configure_rr()
    PL.check_store_path(cfg, a.store)
    if not a.analyze:
        # [2026-09-25 incident] the credentials from the DATA ROOT's .env, then the preflight: BEFORE the plan, the
        # store, the journal and the ledger; the dry-run executes the same preflight (zero calls)
        PL.load_transport()
        PL.transport_preflight()
    view = a.eval_view or C.default_view_path()
    if a.analyze:
        C.need(a.out, "--analyze needs --out (the outcome path; write-once)")
        OC.analyze(cfg, view, a.stage1, a.store, rubric, a.ledger_dir, a.out,
                   expect={"payload_anchor": a.expect_payload_anchor}, workers=a.workers)
        return 0
    plan = PL.make_plan(cfg, view, a.stage1)
    loaded, order_ids = PL.load_plan(plan)
    if a.dry_run:
        rows, n, hits = PL.scan_payloads(loaded, rubric, order_ids)
        anchor = PL.payload_anchor(rows)
        a0, v0, e0 = PL.store_counts(a.store)
        js = PL.ACC.read_journal(PL.journal_path(a.store))
        acc = PL.ACC.guard_day(PL.REGISTRATION, 2 * len(order_ids), a0, a.ledger_dir, refuse=False, what="dry-run",
                               own_journal=js["invocations"])
        lines = ["  DRY-RUN: %d loaded matches (%d scheduled, %d excluded per match), %d payloads scanned, leak hits %d" % (
            len(order_ids), len(plan.kept), len(plan.expected), n, sum(hits.values())),
                 "  anchors sha256 %s | order sha256 %s | PAYLOAD ANCHOR %s" % (plan.digests["anchors_sha"],
                                                                                plan.digests["order_sha"], anchor),
                 "  the pilot 12: %s" % ", ".join(order_ids[:cfg.pilot_n]),
                 "  accounting at the dry-run (not a launch): %s" % ("OK" if not acc["breaches"] else acc["breaches"]),
                 "  " + PL.pool_line(PL.journal_path(a.store), a.post_workers, a.post_workers > 1 or rate is not None)]
        if a.post_workers > 1 or rate is not None:
            from judge_v2 import pool as POOL
            lines.append("  " + (rate or POOL.RateConfig()).line())
        c2, _by_var = OC.c2_lines(plan, loaded)
        lines += c2
        lines += streams_lines(plan.streams)
        for s in lines:
            print(s)
        if a.out:
            from archv2_arena import report
            report.write_once(a.out, "\n".join(lines) + "\n")
        return 0
    mode = "pilot" if a.pilot is not None else "run"
    if mode == "pilot":
        C.need(a.pilot == cfg.pilot_n, "--pilot %d: the registered guard is the first %d matches" % (a.pilot, cfg.pilot_n))
    if a.go:
        os.makedirs(os.path.dirname(os.path.abspath(a.store)), exist_ok=True)
    res = PL.launch(plan, loaded, order_ids, rubric, a.store, a.ledger_dir, rr.call_judge_full, mode,
                    {"payload_anchor": a.expect_payload_anchor, "order_sha": a.expect_order_sha}, script_blob(), go=a.go,
                    workers=a.post_workers, rate=rate)
    print("  %s launch: posted %d" % (mode, res.get("posted", 0)))
    for s in streams_lines(plan.streams):
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
