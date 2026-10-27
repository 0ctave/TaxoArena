"""ARCH-V2-STAGE1-ANCHOR-DRAW: draw the 7 stage-1 anchors of 14 from the split of record (zero calls, read-only).

REGISTRATION: docs/judge_v2_program.md L15985-L15994 (the arena-specialist's ruling on ARCH-V2-PILOT-K46 open item 2,
recorded at 53eccb6): 7 of the 14 MMLU-Pro anchors, stratified by size exactly as design.choose_strata does (per-anchor
EVAL item count of pool pv2_6f78aece2bf9a612, descending, ties by name; 7 consecutive groups of 2; one anchor per group),
master "ARCHV2-STAGE1-ANCHORS-1:229687736d52902c3741e48ebc83be62efed488c", stream "stage1-anchors", seed =
sha256(master | name)[:8] big-endian, numpy PCG64. Run and recorded BEFORE the pilot's dry-run; NEVER redrawn.
The method is archv2_pilot.stage1 (its docstring); the eval_view is opened only through data_v2.views.open_eval.

LAUNCH SEQUENCE (the operator, after a READY; this build ran only the selftest):
  python tools/analysis/archv2_stage1_anchor_draw.py --selftest          (python and python -O)
  python tools/analysis/archv2_stage1_anchor_draw.py --dry-run          (reads the view, prints the counts, their digest
                                                                         and the draw; writes nothing)
  python tools/analysis/archv2_stage1_anchor_draw.py --out experiment_configs/archv2_stage1_anchors.json
                                                                        (the record: write-once JSON; the pilot reads it)
[RAN ONCE, committed at 1463759, insertion: the record is
experiment_results/archv2/stage1_anchor_draw/archv2_stage1_anchors.json, sha256-bytes
08cdff0e314dce5520bca8316e3a74a94845c64850fe8956c99b6d875ffb6140; anchors business, history, math, other, philosophy,
physics, psychology. The --out path above was the build's suggestion, not the path of record.]
[RE-DRAW REGISTERED 5b89159 (L16193-L16200), insertion: ARCH-V2-STAGE1-ANCHOR-DRAW-2 on the split of record 5a3e756, master
"ARCHV2-STAGE1-ANCHORS-2:e2623b4b69e664a9f222abc8b1121dc19d92cceb" (the default). The runner is pinned inside the output
JSON ("runner"), and a DRY-RUN TRANSCRIPT is committed before the record run (--transcript, write-once):
  python tools/analysis/archv2_stage1_anchor_draw.py --dry-run \
      --transcript experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2_dryrun.txt
  (commit the transcript), then ONCE:
  python tools/analysis/archv2_stage1_anchor_draw.py --out experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2.json \
      --transcript experiment_results/archv2/stage1_anchor_draw_2/archv2_stage1_anchors_2_run.txt]
[RAN ONCE 2026-09-24 (e4f0658), insertion: the record is experiment_results/archv2/stage1_anchor_draw_2/
archv2_stage1_anchors_2.json, blob:7b7a41d8d7b285b663eba3fbf4ba2d8bb38c883c / sha256-lf 777e2f6a4cd8ee0d...; its "runner"
block pins THE CLI THAT RAN (blob:90cf17a7... / sha256-lf16:e0474092c8708940). This file changed AFTER the draw (READY
a254a1d LOW-3 only: a refusal's text is appended to the --transcript, then re-raised); the draw rule, the master and the
record's fields are unchanged, and the draw is never re-run.]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from archv2_pilot import common as C  # noqa: E402
from archv2_pilot import stage1 as S1  # noqa: E402


def run(view_path, out_path=None, dry_run=False, dev=False, master=S1.MASTER, say=print):
    record = not dev
    if record and master != S1.MASTER:
        C.refuse("a record draw uses the registered master %r" % S1.MASTER)
    say("%s: %s | master %s | split of record %s" % (
        S1.REGISTRATION, "DRY-RUN (writes no record; a --transcript is its only file)" if dry_run else
        ("RECORD DRAW" if record else "DEV, NOT OF RECORD"), master, C.SPLIT_LABEL))
    say("  runner (pinned in the output): %s" % S1.runner_pins())
    say("  frozen instrument lf16 %s (read-only; design.choose_strata imported) | archv2_pilot lf16 %s" % (
        C.check_instrument(), C.package_lf16()))
    conn, sha, _meta = C.open_view("arena", view_path, C.EVAL_VIEW_SHA256 if record else None, say)
    try:
        pool = C.pool_of(conn, C.CV_MMLU, C.POOL_MMLU if record else None)
        say("  [POOL] %s (scope %s): %d EVAL components, %d EVAL items (v2 pool: pool_guard's p-ids do not apply)" % (
            pool["pool_id"], pool["scope"], pool["n_components"], pool["n_items"]))
        anchor_of, counts, raw = C.anchor_of_items(conn, C.CV_MMLU, pool)
        jm = C.judgeable_items(conn, C.CV_MMLU)
    finally:
        conn.close()
    judg = {}
    for iid, a in anchor_of.items():
        if iid in jm:
            judg[a] = judg.get(a, 0) + 1
    chosen, groups, st = S1.draw(counts, master)
    say(*S1.lines(counts, groups, chosen))
    say("  (judgeable EVAL items per anchor, printed beside; the draw stratifies on the EVAL item count: %s)" % ", ".join(
        "%s %d" % (a, judg.get(a, 0)) for a in sorted(counts)))
    # READY 65a9173 (LOW): st.summary() names a .streams.tsv that this tool never writes; the log is in the record
    say("  RANDOM STREAMS (master %r): %d named stream(s) (%s, seed %d, numpy PCG64), log sha256 %s; recorded in the JSON"
        " record (seed, streams_digest); no .streams.tsv is written" % (st.master, len(st.log), S1.STREAM,
                                                                       st.seed(S1.STREAM), st.digest()))
    rec = S1.make_record(counts, chosen, groups, st, view_path, sha, pool, record, judgeable=judg)
    if dry_run:
        say("  DRY-RUN: nothing written")
        return rec
    C.need(out_path, "--out is required (the record is a write-once JSON)")
    digest = C.write_once_json(out_path, rec)
    say("  WRITTEN %s (write-once) sha256 %s" % (out_path, digest))
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--eval-view", default=None)
    ap.add_argument("--out")
    ap.add_argument("--dev", action="store_true", help="a fixture draw: unpinned view, DEV master admitted, NOT of record")
    ap.add_argument("--master", default=S1.MASTER)
    ap.add_argument("--transcript", default=None, help="write every printed line to this path (write-once)")
    a = ap.parse_args(argv)
    if a.selftest:
        from archv2_pilot import selftest
        return selftest.main(["--part", "stage1"])
    if a.transcript:
        C.need(not os.path.exists(a.transcript), "%s exists: a transcript is written once" % a.transcript)
    lines = []

    def say(*xs):
        for x in xs:
            print(x, flush=True)
            lines.append(x)
    try:
        run(a.eval_view or C.default_view_path(), a.out, a.dry_run, a.dev, a.master, say=say)
    except SystemExit as e:
        # READY a254a1d LOW-3: a refusal's text goes INTO the transcript (it went to stderr only), then re-raised
        lines.append("  REFUSED: %s" % (e.code if e.code is not None else ""))
        raise
    finally:
        if a.transcript:
            from archv2_arena import report
            report.write_once(a.transcript, "\n".join(lines) + "\n")
            print("  TRANSCRIPT %s (write-once) sha256 %s" % (a.transcript, C.sha256_text("\n".join(lines) + "\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
