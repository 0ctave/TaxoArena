"""TaxoArena ARCH-v2 E-J: the v2 judge writer (payload builder, full-payload leakage scan, writer, combiner, rubric induction).

ZERO CALLS. Nothing in this package posts to any API by itself: the writer posts only through a poster the caller injects,
and the selftest injects a fake. Built ON the E-D data layer (tools/analysis/data_v2, DEV build 5618b78): the verdict
store (data_v2.verdicts: R6 six-way enum, R7 slot key, append-only), the stage-gated openers (data_v2.views:
open_generation / open_eval) and the read-only opener (data_v2.ro). Those files are copied UNCHANGED from the E-D branch
and pinned by blob in judge_v2/_base.py; a different blob is refused at import.

Modules:
  _base.py      paths, pins (blob / sha256 of the recipe components), the shared imports of record
  payload.py    the v2 verify-first payload, one question-level reference keyed by VARIANT (R9), dual order,
                temperature OMITTED, cap 8192, the full body + its sha + its zlib copy; the G6 Kotlin-parity TODO hook
  leakage.py    the pre-call FULL-PAYLOAD leakage scan (every message of the body, not the task statement only)
  combiner.py   the dual-order match verdict (TIE on a flip); its flip leg is table- and AST-tested against
                rejudge_grok.combine_orders (E-D ruling 9)
  writer.py     the judge writer: schedule, pre-scan of 100% of payloads, drain through an injected poster into the
                data_v2 verdict DB, per-row provenance; NON_TERMINATED / CONTENT_FILTER never become TIE
  induction.py  rubric induction per corpus type, reading ONLY through open_generation("induce"); every input is
                asserted by content key to be a TRAIN / GATE item (no EVAL item, no sentinel); the model call is
                injected (a stub in the selftest; no live induction is built)
  selftest.py   python tools/analysis/judge_v2/selftest.py   (and under python -O); synthetic, no DB of record opened
[ADDED 2026-09-24 on READY_archv2_EJ (2aba3ab), insertion only: the E-D files are no longer copied into this branch;
judge_v2 pins MAIN's data_v2 (d98b247) and is merged by path alone. Two modules added:
  loader.py     eval_view -> MatchInputs + LeakMaterial through open_eval("judge") ONLY; choose_reference (the
                reference-row ruling); a provenance token the writer requires (C3 / C4)
  lint_opens.py refuses any data_v2.ro opener call or corpus_v2 / view connect outside data_v2/ (C4)]
"""
