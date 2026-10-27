# READY review: WIN-MAP (ORACLE-WATERFALL + REGION-STABILITY + release export)

Reviewed: branch `worktree-wf_42805bc7-f2d-4` tip 8d7f172f (parent 375cbcc9, ancestor confirmed);
`tools/analysis/win_map.py` blob:62b88e522d4d9b0b58b4b0afad6c9655439d008d (LF, of record; `git hash-object`), sha256-crlf16
442b6a685da32f28 (working tree, printed by the script's own PIN line). Registration: prog "## Registered 2026-10-08 (before any
code or call) — WIN-MAP: ..." L25066-L25079 and shared rules R1-R6 L25043-L25049 (_as_of 375cbcc9). Reviewer: adversarial, 2026-10-08.
Zero calls. One read of the pool (the script's own `--dry-run`, busy.ps1 exit 1 before; nothing written; view shas equal before/after).

## VERDICT: NOT READY (BLOCKED) — two blockers, both cheap; delta re-review only

The criteria, denominators, twin handling, zero-call property and release columns are as registered (table). Blocking:
B1 four of eight reviewer mutants on deciding paths SURVIVE (the code is correct as read; the tests do not guard it);
B2 the release ships an unlicensed "winner" for every region, including under UNSTABLE-MAP, in a write-once file.

## Per-claim table (deciding claims only)

| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| 1 | WF1 words: REALISATION-GAP iff 95% UPPER of rho < 0.25; NOT EVALUABLE iff O_adj <= B at the point | CONFIRMED | `wf_words` L429-438 reads `iv["rho"][1] < 0.25`, `den_adj > 0`; M01/M02/M05 killed (re-run) | - |
| 2 | WF2 LUCK-MATERIAL iff 95% LOWER of lambda > 0.10 | CONFIRMED | L437; M03/M04 killed; reviewer R7 (point decides) killed | - |
| 3 | RS1 STABLE-MAP iff median ARI over 250 UMAP-differing pairs >= 0.80 | CONFIRMED | `rs1_pairs` u1<u2: 10 x 25 = 250; `>=` L577; M42-M44 killed | - |
| 4 | RS2 caption = STABLE (Jaccard med >= 0.75 over 24) AND >= 20/25 consensus AND BH q 0.05 over stable regions; none under UNSTABLE-MAP | CONFIRMED (code) / PARTLY (tests) | L586-617 as registered; reviewer R2 (caption without consensus) and R3 (BH q 0.10) SURVIVE | B1 |
| 5 | F-WM fires on rho's POINT >= 0.25 | CONFIRMED (code) / PARTLY (tests) | L496; reviewer R8 (F-WM on the upper bound) SURVIVES | B1 |
| 6 | O_adj luck model: c_i = 1/len(options) for MC sources, 0 otherwise; k_mc from TRAIN only, refit per replicate | CONFIRMED (code) / PARTLY (tests) | real corpus source is `MMLU_PRO` (11,641 items), fixture uses only `MMLU_PRO_LB`: reviewer R4 (drop `MMLU_PRO` from MC_SOURCES, i.e. c_i = 0, q = 1 on all MMLU items) SURVIVES; hook `wt` is zero on EVAL (v2_declared_cells L708-714) | B1 |
| 7 | R1: 471 ids / 427 texts by exact text, dropped first | CONFIRMED | own script: 21,606 rows, RES 6,482, twins 471 / 427; 427 twin items on the v2 side: TRAIN 265, EVAL 115, GATE 47 | - |
| 8 | W-R1b: the drop removes 0 scored EVAL items, so the R_AF 0.6201 / B 0.6049 identities on 5,907 stand | CONFIRMED | real dry-run: "twin items 0" on the scored EVAL set (all 115 EVAL-side twin items are unscored, n_q >= 2), TRAIN 0; map drops {EVAL 115, GATE 47, TRAIN 265} | - |
| 9 | Denominators 5,907 items / 5,404 components; map 20,108 x 512 | CONFIRMED | real dry-run lines (EVAL SET 5907 / 5404; MAP ROWS 20108: EVAL 6038, GATE 1986, TRAIN 12084) | - |
| 10 | No question text, no raw output in the release / outcome | CONFIRMED | export columns L1046-1084: item_id = "i:" + sha256 stem key (split_side.content_key, hex), question_id, benchmark, domain, side, x, y, region, correct__m Int8, n_correct, entropy, winner, caption_licensed; no `text` column; M64 + reviewer R5 (GPQA text in domain) killed | - |
| 11 | Unlicensed winner not released as a caption | REFUTED | `export` L1045: `winner = models[r["own"]]` for EVERY region, caption_licensed beside; under UNSTABLE-MAP every region still carries a "winner" | B2 |
| 12 | Zero calls | CONFIRMED | grep `requests|urllib|http|call_judge|openai|subprocess|ollama`: 1 hit, the docstring line 130 | - |
| 13 | Support arithmetic | CONFIRMED | (2.91-0.14)/3.92 = 0.7066pp; /0.195 = 0.0362; x2.8 = 0.1015. sqrt(0.1x0.9x1.1/5404) = 0.00428; /0.30 = 0.0143; x2.8 = 0.040. 1.2533x0.05/sqrt5 = 0.0280; x2.8 = 0.078. n_eff 5404/1.595 = 3388, 5404/1.10 = 4913. DEFF sources named (D-PR-1 measured; 1.10 planning; 2.0 DECLARED). SCOREABLE all three; script prints measured DEFF / SDs beside | - |
| 14 | Selftest 9/9; mutants 64/64, control survives | CONFIRMED | re-run in the scratch sandbox: 9/9; 64/64 KILLED, C00 SURVIVED | - |
| 15 | Pins of imports | CONFIRMED | union_af_route bf3f17db, v2_declared_cells f0f56805, union_cells_io 92a04543, cell_flips 998d39a7 (git hash-object; dry-run PIN lines agree) | - |

Reviewer mutants (each one in-memory edit; all 9 selftest cases run; scratch sandbox):
R1 undefined rho replicates -> -inf: KILLED (decisive WF1). R2 caption = BH-rejected without the consensus winner: SURVIVED
(decisive RS2). R3 BH at q 0.10: SURVIVED (decisive RS2). R4 `MMLU_PRO` removed from MC_SOURCES: SURVIVED (decisive WF1/WF2).
R5 GPQA text written into `domain`: KILLED (R4 rule). R6 consensus counts a None as a vote: KILLED. R7 WF2 decided by the point:
KILLED. R8 F-WM decided by the upper bound: SURVIVED (decisive falsifier).

## Defects and fixes

- **B1 (BLOCKER, test gap on deciding paths).** Add fixture coverage so R2, R3, R4, R8 are killed: (a) fixture corpus source
  `MMLU_PRO` (the real name; `MMLU_PRO_LB` is only the stratum label) for at least one region, and in `run()` refuse if the W-C
  MC count of `MMLU_PRO` is 0 while MMLU EVAL items are scored; (b) a STABLE region with a BH-rejected p but no 20/25 consensus
  (caption must stay off); (c) a stable-region p-value family where BH at 0.05 and at 0.10 differ; (d) a `branches` case with
  rho point < 0.25 <= upper bound (F-WM NOT FIRED while WF1 NOT-SHOWN). Add R2/R3/R4/R8 to MUTANTS.
- **B2 (BLOCKER, release content vs RS2).** The write-once release carries `winner` for every region. Fix: `winner` null unless
  `caption_licensed`; if the EVAL argmax is wanted, ship it as `eval_argmax_descriptive` and state in README "not a caption;
  only caption_licensed regions may be captioned". Add a mutant/selftest: under UNSTABLE-MAP every exported `winner` is null.
- D-3 LOW. README lists benchmark `MMLU_PRO_LB`; the exported `benchmark` value is the corpus source `MMLU_PRO`. Fix the README.
- D-4 LOW (registrar note, no code change). The registered "free-form BBH, c_i = 0" class is EMPTY in this corpus: all 5,757
  BBH items store a candidate list (e.g. object_counting 19, reasoning_about_colored_objects 18, geometric_shapes 11), so every
  BBH item gets c_i = 1/len(list) (harness log-likelihood choices). Dry-run W-C line: BBH MC 5757, GPQA 546, MMLU_PRO 11641,
  MUSR 756, MATH 0-class 1294, IFEVAL 0-class 541. Disclose in the outcome.
- D-5 LOW (registered design, disclose). RS2's challenger is chosen on the region's EVAL items and tested on the same items
  (in-sample selection); the 20/25 consensus is the only guard. State it beside the caption count.
- D-6 LOW. `item_id` is the sha256 stem key: no text, but anyone holding the GPQA text can confirm membership. Acceptable under
  R4 (ids allowed); state it in the README.
- CONDITION C1. The run command says "from the main checkout", where win_map.py does not exist yet (main d999e689). Merge the
  fixed branch first (check `merge-base --is-ancestor` against main), or run from the worktree with `--data-root <main>` (as I
  did for the dry-run). C2. busy.ps1 exit 1 before each of --dry-run and --run (both are pool readers; rule 7). C3. The fixed
  blob gets a delta READY (diff 8d7f172f..new tip; selftest, the 64 + R2/R3/R4/R8 mutants, pins).

## Commands (all read-only; zero calls)

```
git -C <wt> show --stat 8d7f172f ; git -C <wt> hash-object tools/analysis/{win_map,v2_declared_cells,union_af_route,union_cells_io,cell_flips}.py
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --selftest     # 9/9, rc 0
python tools/analysis/scratch_dir.py --run -- python tools/analysis/win_map.py --mutants      # 64/64 KILLED, C00 survived
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/wm_rev_mut.py           # R1..R8 (4 survive)
python E:/TaxoArena_tmp/wm_rev_twins.py   # corpus_questions mode=ro&immutable=1: twins 471/427; twin items TRAIN 265 EVAL 115 GATE 47
powershell -File E:/TaxoArena_tmp/busy.ps1 (exit 1) ; python tools/analysis/win_map.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
   # rc 0; POOL line first; gen/eval view sha256 EQUAL before/after; EVAL 5907/5404; twin items on scored EVAL 0; map 20108 x 512
sha256 multicorpus_cache_v1.db before/after own script: ad66e30a0eb4abd6 = ad66e30a0eb4abd6
```

## Run command (after B1/B2 fixed and the delta READY)

```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # must exit 1
python tools/analysis/win_map.py --dry-run               # from main after the merge (or --data-root <main> from the worktree)
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # must exit 1
python tools/analysis/win_map.py --run                   # ~30-60 min, ~3 GB; outcome + release write-once; back up to E:
```
