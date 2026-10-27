"""ARCH-V2-STAGE1-ANCHOR-DRAW (registered 2026-09-24, docs/judge_v2_program.md L15985-L15994, the arena-specialist's
ruling on PILOT-K46 open item 2): 7 of the 14 MMLU-Pro anchors, stratified by size EXACTLY as design.choose_strata does.

  sizes     the per-anchor EVAL item count of the split of record (pool pv2_6f78aece2bf9a612, EVAL side, joined by
            item_id, corpus_version = mmlu-pro-v2 named), read from the sealed eval_view (common.anchor_of_items);
            printed with their digest (common.counts_digest, sha256 over "name TAB count LF" sorted by name)
  order     descending size, ties by name; cut into 7 consecutive groups of 2 (numpy.array_split); one anchor per group
            drawn uniformly: design.choose_strata ITSELF is called (imported from the frozen instrument, not copied)
  stream    master "ARCHV2-STAGE1-ANCHORS-1:229687736d52902c3741e48ebc83be62efed488c", stream "stage1-anchors",
            seed = sha256(master | name)[:8] big-endian, numpy PCG64 (archv2_arena.streams.Streams)
  output    ONE write-once JSON (mode "x"): the 7 anchors (sorted), the groups, the counts and their digest, the seed,
            the eval_view sha, the pool, the code pins. NEVER REDRAWN (a redraw needs a new registered seed and a
            stated reason, both draws disclosed): the file is the record; verify() re-derives the draw from it.

[RE-DRAW REGISTERED 2026-09-24 (5b89159, docs/judge_v2_program.md L16193-L16200), insertion only: entry
ARCH-V2-STAGE1-ANCHOR-DRAW-2, master "ARCHV2-STAGE1-ANCHORS-2:e2623b4b69e664a9f222abc8b1121dc19d92cceb", the same stream and
rule, the counts from pool pv2_41dbd3dbcd399df0 of the NEW split; the first draw (1463759, master ARCHV2-STAGE1-ANCHORS-1)
read the superseded split and is kept as REGISTRATION_1 / MASTER_1 for disclosure (never re-run: its master is refused
here). The record now pins the RUNNER (the CLI's blob and lf16, the package lf16, the frozen instrument lf16).]

verify(record, counts=None, ...) is what the pilot calls: the file must name this registration and master, carry EXACTLY 7
anchors (the pilot never draws from the 14), reproduce under design.choose_strata from its own counts, and (when the
caller passes the view's counts) carry the same counts and digest.
"""
import json
import os

import numpy as np

from . import common as C
from archv2_arena import design, report
from archv2_arena.streams import Streams

REGISTRATION_1 = "ARCH-V2-STAGE1-ANCHOR-DRAW"                                          # superseded (disclosure)
MASTER_1 = "ARCHV2-STAGE1-ANCHORS-1:229687736d52902c3741e48ebc83be62efed488c"
REGISTRATION = "ARCH-V2-STAGE1-ANCHOR-DRAW-2"
MASTER = "ARCHV2-STAGE1-ANCHORS-2:e2623b4b69e664a9f222abc8b1121dc19d92cceb"
STREAM = "stage1-anchors"
N_DRAW = 7
KIND = "archv2-stage1-anchor-draw-1"


def groups_of(counts, n=N_DRAW):
    """The consecutive groups choose_strata cuts (descending size, ties by name)."""
    names = sorted(counts, key=lambda k: (-counts[k], k))
    return [[names[int(i)] for i in g] for g in np.array_split(np.arange(len(names)), n)]


def draw(counts, master=MASTER):
    """-> (the 7 anchors sorted by name, the groups, the Streams used)."""
    C.need(len(counts) == C.N_ANCHORS, "the stage-1 draw needs the %d anchors' counts, got %d" % (C.N_ANCHORS, len(counts)))
    C.need(master != MASTER_1, "the first draw's master %r is never reused (the re-draw is ARCH-V2-STAGE1-ANCHOR-DRAW-2)"
           % MASTER_1)
    st = Streams(master)
    chosen = design.choose_strata(dict(counts), N_DRAW, st.np(STREAM))
    groups = groups_of(counts)
    per = [sorted(set(g) & set(chosen)) for g in groups]
    C.need(all(len(x) == 1 for x in per) and len(chosen) == N_DRAW,
           "the draw did not take exactly one anchor per group: %s" % per)
    return sorted(chosen), groups, st


def lines(counts, groups, chosen):
    out = ["  per-anchor EVAL item counts (descending, ties by name) and the 7 groups of 2:"]
    for k, g in enumerate(groups):
        out.append("    group %d: %s  -> drawn: %s" % (k + 1, ", ".join("%s %d" % (a, counts[a]) for a in g),
                                                     ", ".join(a for a in g if a in chosen)))
    out.append("  counts digest (sha256 over 'name TAB count LF' sorted by name): %s" % C.counts_digest(counts))
    out.append("  STAGE-1 ANCHORS (7, sorted by name): %s" % ", ".join(chosen))
    return out


def runner_pins():
    """The runner pinned inside the output (registration 5b89159): the CLI and the package, hash kinds named."""
    cli = os.path.join(C.ANALYSIS, "archv2_stage1_anchor_draw.py")
    return {"archv2_stage1_anchor_draw.py": "blob:%s sha256-lf16:%s" % (C.dv2ro.git_blob_lf(cli), C.dv2ro.sha256_lf16(cli)),
            "archv2_pilot package_lf16": C.package_lf16(), "frozen instrument_lf16": C.check_instrument()}


def make_record(counts, chosen, groups, st, view_path, view_sha, pool, record, judgeable=None):
    return {"kind": KIND, "registration": REGISTRATION, "master": st.master, "stream": STREAM,
            "seed": st.seed(STREAM), "rng": "numpy.PCG64", "stratifier": "archv2_arena.design.choose_strata",
            "anchors": list(chosen), "groups": groups, "counts": dict(sorted(counts.items())),
            "counts_digest": C.counts_digest(counts), "count_kind": "EVAL items of the pool (side JOIN item, corpus_version"
            " named), by the split's stratum", "judgeable_counts": dict(sorted((judgeable or {}).items())),
            "eval_view": view_path.replace("\\", "/").split("/")[-1], "eval_view_sha256_bytes": view_sha,
            "pool": pool, "of_record": ("REGISTERED DRAW %s (master of record)" % REGISTRATION) if record else
            "DEV, NOT OF RECORD", "streams_digest": st.digest(), "code": C.code_pins(
                ["archv2_pilot/common.py", "archv2_pilot/stage1.py", "archv2_arena/design.py", "archv2_arena/streams.py"]),
            "runner": runner_pins(), "split_of_record": C.SPLIT_LABEL}


def verify(rec, counts=None, view_sha=None, record=True):
    """The pilot's reading of the stage-1 file. Returns the 7 anchors (sorted). REFUSES on anything else."""
    if isinstance(rec, str):
        with open(rec, encoding="utf-8") as f:
            rec = json.load(f)
    C.need(isinstance(rec, dict) and rec.get("kind") == KIND and rec.get("registration") == REGISTRATION,
           "the anchor file is not an %s record" % REGISTRATION)
    if record:
        C.need(rec.get("master") == MASTER, "the anchor file's master %r is not the registered %r" % (rec.get("master"), MASTER))
        C.need(str(rec.get("of_record", "")).startswith("REGISTERED DRAW"), "the anchor file is not of record (%r)"
               % rec.get("of_record"))
    anchors = rec.get("anchors") or []
    C.need(len(anchors) == N_DRAW and len(set(anchors)) == N_DRAW,
           "the anchor file carries %d anchors: the pilot draws its 2 from the REGISTERED 7 (ruling on open item 2),"
           " never from %d" % (len(anchors), len(anchors)))
    rc = {k: int(v) for k, v in rec.get("counts", {}).items()}
    C.need(C.counts_digest(rc) == rec.get("counts_digest"), "the anchor file's counts do not hash to its digest")
    again, _groups, st = draw(rc, rec["master"])
    C.need(again == sorted(anchors), "the anchor file does not reproduce: choose_strata gives %s, the file %s"
           % (again, sorted(anchors)))
    C.need(st.seed(STREAM) == rec.get("seed"), "the anchor file's seed differs from sha256(master|stream)")
    if counts is not None:
        C.need(dict(sorted(counts.items())) == rc, "the eval_view's per-anchor counts differ from the anchor file's")
    if view_sha is not None:
        C.need(rec.get("eval_view_sha256_bytes") == view_sha, "the anchor file was drawn on eval_view %s, not %s"
               % (rec.get("eval_view_sha256_bytes"), view_sha))
    report.hit("STAGE1.VERIFIED")
    return sorted(anchors)
