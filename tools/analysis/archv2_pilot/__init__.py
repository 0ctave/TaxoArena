"""archv2_pilot: the stage-1 anchor draw (ARCH-V2-STAGE1-ANCHOR-DRAW), the per-stratum supply-json builder and the k = 46
pilot (ARCH-V2-PILOT-K46), built on the split of record through data_v2 and judge_v2 (zero calls in this package; a run
posts only through rejudge_reasoning.call_judge_full, injected by the CLI).

NEW CODE ONLY. The frozen G22 / G23 instrument (the 11 files of g22.INSTRUMENT_FILES, instrument_lf16 876d01413318bd7b)
is IMPORTED read-only (design.choose_strata, design.schedule_stratum as the identity reference of the scheduler,
streams.Streams, cert, bt, data.edges_fast, report.write_once / need / hit, g22.RecordStore) and never edited; every CLI
prints instrument_lf16 and refuses when it differs.
[AMENDED 2026-09-25 (0761cfa, docs/judge_v2_program.md L16787-L16992), insertion only: the pilot runs at k = 37 (the 46
ACTIVE minus the 9 BANNED_MODELS entries); its ID and code identifiers keep "K46".]
"""
