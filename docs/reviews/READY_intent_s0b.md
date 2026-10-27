# READY review (delta): INTENT-TRANSFER-S0 code conditions (branch intent-s0b, tip 072f808 on 61d7bfe)

Reviewer: adversarial-reviewer, 2026-09-30. Zero calls: no fetch, no embed, no Ollama post, no --run. Delta review against
docs/reviews/READY_intent_s0.md (0f3591a) C-1..C-8 and the registrar's record prog L22146-L22158 (43502d8). Code the delta does not
touch stands as CONFIRMED in 0f3591a.

## Verdict

- **MERGEABLE** (by path). One file changed: tools/analysis/intent_transfer_s0.py. Main moved past 61d7bfe (8f3b840). Those
  commits touch 5 intent paths: the pins file and 4 ingest logs, all the registrar's and the operator's. None of them is the
  script or one of its imports. main still holds blob 8386a99, so the path merge replaces exactly the reviewed parent.
- **READY for `--embed --go`** for qwen3, nomic and gemma on MASSIVE, CLINC and Banking77 (one DB per embedder). **Then READY for
  `--run`**, after the registrar pins emb.{qwen3,nomic,gemma}. No code is owed: C-2, C-3, C-6 and C-7 are implemented and guarded,
  and C-8 (i)-(iii) are implemented. C-1 and C-4 were bracketed at 43502d8, and the code matches those brackets.
- The code freezes at blob 69e6f400 from now on. Every intent_emb_*.db pins this LF blob through RO.git_blob_lf. Any later edit
  makes all three DBs refuse.

## Pins (the LF blob of record; the CRLF rendering differs in checked-out trees)

| path | blob (LF of record) | sha256-lf16 | CR bytes (blob / CRLF checkout) |
|---|---|---|---|
| tools/analysis/intent_transfer_s0.py | 69e6f4006ff2d43fe95784ebe471594cfd581fdf | 255f4ded47f805ee | 0 / 2,496 |

`RO.git_blob_lf` on the CRLF checkout = 69e6f400, so the self-pin is rendering-independent. Correction to 0f3591a's pin line:
"the working tree is LF" held for the builder's worktree only. The root checkout (autocrlf=true) carries CRLF: 2,308 CR in 8386a99.

## Per-claim table (deciding claims of the delta)

| # | claim | result | reviewer vs claimed | sev |
|---|---|---|---|---|
| 1 | C-1/C-2: the basic interval [2D-q97.5, 2D-q2.5] decides C1. Beside it are printed the bias b, b/SE, D-b and the percentile CI (descriptive) | CONFIRMED | c1_level L770ff: lo/hi = basic_ci(D, draws) feed c1_status (WORSE: D<-bar and hi<0; BETTER: D>bar and lo>0). The 512 lines use the same interval. This matches the bracket at L22146-58. Own RV-7 (basic CI centred on mean(draws)) KILLED; builder's "percentile decides" and "flipped" KILLED | - |
| 2 | C-3: RV-2, RV-4, RV-5 and RV-6 are now killed | CONFIRMED | re-run in the builder's mutant suite (see Mutants below). The independent paired-C1, stratified-C2 and seed-0 C3/C4 recomputations were read: the weights and pairing are rebuilt from SQL stem keys, not taken from the code under test | - |
| 3 | C-4 B2: C1a is HELD iff >= 2 of 3 corpora have a WORSE fine family (either family) | CONFIRMED | c1_verdicts: c1a from `alt` (any family per corpus). The per-family reading is printed NOT OF RECORD. The selftest covers 2 corpora via 2 families -> HELD, and 2 families on 1 corpus -> FAILED. Own RV-8 (a corpus needs BOTH families) KILLED | - |
| 4 | C-4 B3 (seed 0) and B7 (every swappable slot); the swapped slots are printed | CONFIRMED | c4_variants records the slot types. c4_swap_summary and s0_c4_variants.csv carry ids and types only (no text) | - |
| 5 | C-6: the Ollama URL is printed in --dry-run and in every --go header | CONFIRMED | 2 print sites; ST-EMBED and ST-DRY assert them | - |
| 6 | C-7: HM(A, n_pos = in-scope, n_neg = OOS) = 0.00352; x sqrt(1.05) = 0.0036; the registered 0.00573 printed as conservative | CONFIRMED | c2 stores hanley_mcneil(A, n2 = n_in, n1 = n_oos). This agrees with 0f3591a claim 10 and the registrar's HM bracket | - |
| 7 | C-8 (i): --run compares the ingest DB's provenance sha256s with pins["raw"] | CONFIRMED | raw_pin_check runs after the ingest_db pin_check. Against the real study DB: provenance 5 rows, pins 5 keys, 5/5 equal (ro read). Own RV-9 (zero provenance rows read) KILLED, so the check is not vacuous on the fixture | - |
| 8 | C-8 (iii): annot/text mismatches are EXCLUDED from C4 and counted | CONFIRMED | `continue` after the count; the accounting identity includes the mismatch count; a planted mismatch is excluded | - |
| 9 | Pushback 1: "a selftest that the basic interval contains D cannot hold in general" | **CONFIRMED (the builder is right)** | 2D-q97.5 <= D <= 2D-q2.5 iff q2.5 <= D <= q97.5. The basic interval therefore contains D exactly when the percentile interval does. The condition 0f3591a C-2 asked for was wrongly worded. Pinning the formula against an independent paired bootstrap is the correct test | - |
| 10 | Pushback 2: C-8 point 4 (the selftest reads docs/agents/queue.json relative to the cwd) is not reproduced | **CONFIRMED (0f3591a C-8(iv) WITHDRAWN as reviewer error)** | 'queue' appears 0 times in 8386a99, in 69e6f400 and in intent_ingest 33f33f21. Imports: split_side, embedder_arms, intent_ingest, data_v2.ro. The one import-chain hit (embedder_arms -> pool_guard: 2 hits) is comment text. The selftest PASSED 129 from a cwd outside the repo. Mechanism found: a stray `queue.py` in the shared scratchpad (2026-09-25) reads docs/agents/queue.json. When a harness script runs from the scratchpad root, that file shadows stdlib `queue` through sklearn -> joblib. It reproduced here, on my first own-mutant run: the control failed until the harness moved to a subdirectory | - |
| 11 | Tests | CONFIRMED | selftest: SELFTEST PASSED (129 checks), from the worktree root and from a foreign cwd. Builder's mutants: see below. Own mutants: 3 of 3 KILLED, control RV-0 SURVIVED. Root *.db mtimes: 16 files, unchanged before and after | - |

## Mutants

Builder's suite re-run at 072f808: MUTANTS: 73 of 73 KILLED (0 SURVIVED). The decisive four from 0f3591a (RV-2, RV-4, RV-5, RV-6) are all KILLED(assert).

Own mutants (scratchpad rv_s0b/own_mut_b.py, the script's own exec pattern, builder fixture):
- RV-0 identity: SURVIVED (control).
- RV-7 basic CI centred on bmean: KILLED, decisive.
- RV-8 C1a requires both families per corpus: KILLED, decisive.
- RV-9 raw_pin_check reads 0 provenance rows: KILLED, decisive.

## Defects (none blocks)

- **D-1 LOW (registrar; no code).** raw_pin_check iterates the provenance rows only. A pin key that is absent from provenance is
  never checked. This is harmless on the record: 5 = 5 names equal, and the ingest_db sha pin covers the DB bytes. Record it; do not
  edit the code, which is frozen.
- **D-2 LOW (record).** Correct 0f3591a in three places:
  - C-2's "selftest that the basic interval contains D" (claim 9 above);
  - C-8(iv), withdrawn (claim 10);
  - the "working tree is LF" note (see Pins).
- **D-3 LOW (operator hygiene).** The stray scratchpad `queue.py` shadows stdlib `queue` for any Python run from that directory.
  Rename it, or do not run harnesses from the scratchpad root.
- **Registrar's OPEN C-8 (annot_text_mismatch = 0 before embedding).** The code now excludes and counts these rows, so the count is
  descriptive in the C4 readout. It no longer gates embedding.

## Commands (read-only / temp dirs; worktree scratchpad/wt_s0b detached at 072f808)

```
git diff --name-only 61d7bfe..072f808 | wc -l -> 1 ; ... | grep -cE 'application.yml|\.env|\.gitignore' -> 0
git diff --name-only 61d7bfe..main | grep -E 'intent_|embedder_arms|split_side|data_v2/ro' -> pins json + 4 ingest logs (no code)
git rev-parse main:tools/analysis/intent_transfer_s0.py -> 8386a99 (the reviewed parent)
git show 69e6f400 | sha256sum | cut -c1-16 -> 255f4ded47f805ee ; | tr -cd '\r' | wc -c -> 0 ; checkout CR -> 2496
python -c "from data_v2 import ro as RO; print(RO.git_blob_lf('tools/analysis/intent_transfer_s0.py'))" -> 69e6f400...
for b in 8386a99 69e6f400 33f33f21: git show $b | grep -c queue -> 0 0 0
sqlite3 file:intent_transfer_corpora_v1.db?mode=ro: provenance 5 rows, 5/5 == pins["raw"]; items 53,454
python tools/analysis/intent_transfer_s0.py --selftest (worktree root; and from scratchpad/elsewhere) -> PASSED (129 checks) x2
python tools/analysis/intent_transfer_s0.py --mutants -> MUTANTS: 73 of 73 KILLED (0 SURVIVED)
python scratchpad/rv_s0b/own_mut_b.py <copy of the script> -> RV-0 SURVIVED; RV-7/8/9 KILLED
ls -l --time-style=full-iso /z/.../TaxoArena/*.db before/after -> 16 files, identical
```
