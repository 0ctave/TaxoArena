"""The per-stratum EVAL supply JSON for archv2_g22_sim.py --supply-json, from the split of record (zero calls, read-only).

INPUT FOR ruling 2 (v) (the real-supply re-run of the D1 designs and the stop leg). The method and the format are
archv2_pilot.supply (its docstring): {"mmlu": {anchor: n}, "union": {"source/domain": n}}, corpus_version named on every
count, ids asserted distinct; --count items|judgeable is REQUIRED; --only-anchors <stage-1 record> restricts "mmlu" to the
REGISTERED 7 (for a D1-stage1-only run of the frozen simulator). The file is write-once; its sha256 is printed and
recorded in the sidecar <out>.manifest.json (write-once).

LAUNCH SEQUENCE (the operator):
  python tools/analysis/archv2_supply_json.py --selftest
  python tools/analysis/archv2_supply_json.py --count judgeable --dry-run
  python tools/analysis/archv2_supply_json.py --count judgeable --out experiment_configs/archv2_supply_REG_judgeable.json
  python tools/analysis/archv2_supply_json.py --count judgeable --only-anchors experiment_configs/archv2_stage1_anchors.json \
      --out experiment_configs/archv2_supply_REG_judgeable_stage1.json
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from archv2_pilot import common as C  # noqa: E402
from archv2_pilot import supply as SU  # noqa: E402


def run(view_path, count_kind, out_path=None, dry_run=False, dev=False, only_anchors=None, say=print):
    record = not dev
    say("ARCH-V2 SUPPLY JSON (%s; count kind %s)" % ("DRY-RUN" if dry_run else ("of the split of record" if record else
                                                                               "DEV, NOT OF RECORD"), count_kind))
    say("  frozen instrument lf16 %s (read-only) | archv2_pilot lf16 %s" % (C.check_instrument(), C.package_lf16()))
    conn, sha, _meta = C.open_view("arena", view_path, C.EVAL_VIEW_SHA256 if record else None, say)
    try:
        supply, man = SU.build(conn, count_kind, record=record, only_anchors=only_anchors, out=say)
    finally:
        conn.close()
    txt = C.canonical_json(supply)
    digest = C.sha256_text(txt)
    man.update({"eval_view_sha256_bytes": sha, "supply_sha256": digest})
    say("  supply JSON sha256 %s (%s)" % (digest, ", ".join("%s %d strata / %d" % (k, len(v), sum(v.values()))
                                                             for k, v in sorted(supply.items()))))
    if dry_run:
        say("  DRY-RUN: nothing written")
        return supply, man
    C.need(out_path, "--out is required")
    from archv2_arena import report
    report.write_once(out_path, txt)
    msha = C.write_once_json(out_path + ".manifest.json", man)
    say("  WRITTEN %s sha256 %s | manifest %s.manifest.json sha256 %s" % (out_path, digest, out_path, msha))
    return supply, man


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--eval-view", default=None)
    ap.add_argument("--count", choices=("items", "judgeable"))
    ap.add_argument("--only-anchors", default=None)
    ap.add_argument("--out")
    ap.add_argument("--dev", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        from archv2_pilot import selftest
        return selftest.main(["--part", "supply"])
    if not a.count:
        C.refuse("--count items|judgeable is required (the builder does not choose)")
    run(a.eval_view or C.default_view_path(), a.count, a.out, a.dry_run, a.dev, a.only_anchors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
