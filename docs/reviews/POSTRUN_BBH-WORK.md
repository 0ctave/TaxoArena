# POSTRUN review: BBH fetch, census and sealed split + BBH-WORK (exploratory WORK readouts, 3/5/7 recovery)

Authority: D-2026-10-27-4 (TaxoArena d463cdb0, `docs/agents/author_decisions/2026-10-27.md`, with the main session's
reading, item (2)). Reviewer: adversarial reviewer, 2026-10-28. Zero LLM calls (4 + 4 embedding calls to the local
Ollama embedder, row 13). RESERVED responses read by me: 0 (every score read filtered on WORK ids; the raw re-extraction
skipped RESERVED rows before any response field). At most 2 heavy processes, BLAS 1.
Reviewed: benchzoom branch `bbh` (local), 35b2724..ee1e508: 10 new files, 0 deleted lines, 0 files under `src/` or
`docs/execution_graph.md`; `git merge-tree --write-tree master ee1e508` clean against master 6ab459b.
- Pins at ee1e508 (LF blobs, `git hash-object` = `git rev-parse HEAD:<path>`): runner `blob:dd80ddcc`, plan
  `blob:33dc3326` (sha256-lf16:4b73f0f9bb17512b; the working copy is MIXED EOL, 83 CRLF lines in [P2], sha256
  8cb2461d973852e9: L4), census doc `blob:f56f10c8`, bbh_census `blob:66b65aad`, bbh_fetch `blob:19db843e`, tests
  `blob:41f90592` / `blob:9dc6b598`; split lists `blob:d32499f7` / `blob:54f39303` (sha256-lf16 3d4d644a7ac34d22 /
  9ef05cc2cfe34c91, `cmp`-identical to `E:/benchzoom_demo/bbh/split`). Run of record: runner `blob:82628180` (a77e058),
  parts and analyze `dirty ""`; recovery runner `blob:febac9da` (90c42f3).
- Outputs: `sha256sum -c` bbh-work 14/14, census_r2 8/8, split 3/3, work_accuracy 3/3; backups: bbh-work 23/23,
  SHA256SUMS sha256 55009518 (bbh-work) and 3ad86bc9 (bbh, 1,060 lines) as claimed. After all my runs: 14/14 again,
  and 0 files newer than my start under the outputs, the census dirs, the parts dir and the npz (`find -newermt | wc -l`).

## Verdict

- **FETCH / CENSUS / SPLIT: CONFIRMED.** **MIXED-2: ACCEPTED** (row 3).
- **BBH-WORK: OUTCOME CONFIRMED (exploratory, with qualifiers).** Words after review, unchanged: R1 **C1(V0) NOT SHOWN
  AT 3 SE**; K1 **KILLED**; K2 **KILLED on BBH** (quote only with C1's qualifier); V0 vs random **NOT DISTINGUISHABLE
  FROM SIZE ALONE (UNDERPOWERED)**; recovery V0m and Km **DOES NOT RECOVER SUB-VARIANTS** (read only as C3 says).
- **MERGEABLE (merge_ok yes).** No BLOCKER. Conditions C1 (HIGH), C2, C3 (MEDIUM); L1-L5 (LOW).

## Per-claim table (deciding claims; x 1e-3 nats per cell; WORK rows; denominators named)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Parts = the raw leaderboard samples | 3 KEPT models drawn by `default_rng(20261028).choice(342, 3)`: Yi-1.5-6B-Chat, Yarn-Mistral-7b-128k, gemma-1.1-2b-it. Own reader at the part's recorded commit: latest file 24/24 equal to part.json; 0 newer BBH sample files on the Hub; item columns (text, n_choices, doc_hash) 5,761/5,761 equal; WORK scores 3,457/3,457 equal to the stored `acc_norm` AND to my own recomputation (argmax loglik / len(choice without delimiter) == gold), each model; RESERVED rows: 2,304 skipped before any response field; 58-65 MB per model downloaded and deleted (dir count 0) | CONFIRMED | - |
| 2 | Census r2: 348 / 345 / 342 KEPT; 5,761 items, 24 subtasks; 4 dup texts on 8 items; ND-1 385 groups, 924 items, max 8 | Own code from the 345 parts' item columns: 342 KEPT, EXCLUDED zephyr-orpo (cov 0.9564), Phi-3-small x2 (0.8382, 23 subtasks), MISSING Qwen2-57B / dbrx / Mixtral-8x22B-Instruct; status = models.csv for all 348; 5,761 items in 24; 4 / 8; own ND-1 (norm-v1, loose key, multiset 5-gram J >= 0.95): 622 pairs, 385 / 924 / max 8, SAME partition as census `group` | CONFIRMED | - |
| 3 | MIXED-2 amendment (after census r1, before the split, no score read) | Off-majority cells 251, all in zephyr-orpo; with it excluded the 342 KEPT parts disagree on 0 items, so MIXED-2 = "exclude the odd part, then MIXED-1". Census r1 16:52, amendment 663b631 17:01:40, r2 17:02:05: no response value enters. Restores object_counting (250 items) dropped by one run with 18 instead of 19 choices | ACCEPTED | - |
| 4 | Split sealed and committed before any statistic beyond counts | Own SPLIT-1 from census groups = committed lists; 0 groups straddle; pins PENDING at 663b631, set at 458b786 (17:03:49); accuracy.json 17:03:59; split.json 544806b5 | CONFIRMED | - |
| 5 | WORK acc_norm mean 0.475 (sd 0.105, 0.297-0.738), chance 0.289, 18 NC-1 | Own read (WORK filter): 342 models, mean 0.4753, sd 0.1051, min 0.2968, median 0.4673, max 0.7382; chance 0.2885; NC-1 18 | CONFIRMED | - |
| 6 | RESERVED responses read 0 | Code: the only `score` reader is `SplitGuard.read_scores` (bbh_census.py:674; every other read_parquet names ITEM_COLUMNS); parts json reserved_reads 0 / 0, values 442,496 = 3,457 x 128 (both); guard mutants G1, G2 killed. Limit: pyarrow decodes a row group before its filter (byte level); no RESERVED value reaches any statistic | CONFIRMED | - |
| 7 | Plan aec5385 before every statistic on responses; words by its rules | Times: plan 18:13:33; merged build 18:26 and recovery 18:30 at 90c42f3; [P1] 19:19:58; parts 19:20-22:07 and analyze 22:08 at a77e058. Files older than the plan under the outputs and the builder's tmp: main build, embed record, their 2 logs, src copies (`find ! -newermt`), no response output. Plan aec5385..ee1e508: 0 deleted lines. Runner a77e058..ee1e508: hunks in docstring, fixture_world, selftest only. Disclosed exceptions stand (main V0 leaf counts before the plan; one task's tau_L2 before [P1]) | CONFIRMED | - |
| 8 | Deciding numbers | Own SE code on the parts npz (cluster-robust, G/(G-1), MC over 5 seeds), own clusters (cos >= 0.98 on own unit rows UNION census groups: 2,662, max 35, same partition as the npz). Each G / SE / V0-leaf SE / MDE80 / n_eff equals the json to 4 dp: C1(V0) +0.0845 (0.0722), C1(K) +0.0719 (0.0621), C1(random) +0.0118 (0.0385), C1(N) +2.4758 (0.3901), V0-K +0.0126 (0.0528), V0-random +0.0727 (0.0775), G(N\|L2+V0) +2.3142 (0.3885), G(V0\|L2+N) -0.0269 (0.0316). Own harness from library primitives (own fold loop over `gw.group_folds` / `gw.l2_contexts` / `gw.reader` / `meter.step("field_txt")` / `gw.item_pi`, own roster and WORK read; the runner not imported), main world g2, 25 tasks: 16 per-item arrays (V0, KM0-4, RND0-4 on C1; V0, N on L2; V0\|L2+N; N\|L2+V0; N\|C1) equal the record at max\|diff\| 0; tau_L2 0.04 x 23, 0.08 x 2 as recorded | CONFIRMED | - |
| 9 | Words | R1 z 1.17 < 3; K1 0.0126 <= 0.0528; K2 arm A 5.96 SE, arm B -0.0269 <= 0; random 0.94 SE, MDE80 2.8416 x 0.0775 = 0.2204 > 0.0845 | CONFIRMED | - |
| 10 | "DEFF 11.5 because BBH items are templated" | n_eff = n / DEFF and MDE80 reproduce (301, 0.2775). DEFF itself is not re-measurable: the cell differences are not saved (L1). From the cache's own clusters the content-cluster factor is (SE_cluster / SE_item-iid)^2 = 1.20 for C1(V0), 1.06-1.37 across the contrasts, so about 9.6 of the 11.5 is within-item correlation of the 128 models' cells. MATH had DEFF 1.05 with the same definition (FLAT-COMPARE) | PARTLY (attribution REFUTED) | MEDIUM |
| 11 | K2 KILLED on BBH | Word right under the plan's SE. geometric_shapes, disambiguation_qa, boolean_expressions carry 83% of N's summed C1 gain (both V0-unsplit in the first two). Clustered by subtask z 1.74, by V0 leaf 1.87; the other 21 subtasks: G(N\|L2+V0) +0.286 (0.316), 0.91 SE | PARTLY (fragile) | HIGH |
| 12 | Recovery: variant hidden from the tree; DOES NOT RECOVER | Build call: groups = `anchors_of(task, "merged")` (20; equal to the pickle's anchors); the task column is passed only as text names (`label_tree`, after `bisect`); `anchor_check` REFUSES a subtask-grouped tree against the merged anchors (run on the record objects). Own sklearn AMI: -0.0024 / -0.0024 (ARI -0.0022 / -0.0021; WORK -0.0010 / -0.0024); own null p95 0.0035 / 0.0035 (record 0.0035 / 0.0039: seed-dependent, not deciding). V0m = Km for 5/5 seeds; each of the 5 leaves = one scenario (keyword share 1.00), crossed with 3/5/7 (41-61 per cell). Meter: VAR +1.5309 (0.2938), V0m +0.0172 (0.0616) reproduce | CONFIRMED | - |
| 13 | Embedding provenance | npz sha256 0e9ef33a; keys = sha256("ollama:qwen3-embedding:8b-q8_0" NUL text) present for all 5,761 items (5,757 distinct). 4 seeded texts re-embedded: `qwen3-embedding:8b-q8_0` (digest 9704fd987c12) cos 1.000000 x 4; `qwen3-embedding:latest` 0.988-0.990 (discriminator). embed.json's `code` names a dirty copy (disclosed) | CONFIRMED | - |
| 14 | [P1] roster | Own draw `default_rng([20261027, 9])` = both parts' 128 models; 6 of 18 NC-1 inside | CONFIRMED | - |
| 15 | Tests, selftest, mutants | `pytest tests/test_bbh.py tests/test_bbh_work.py` 25 passed (TMP in E:); selftest on a copy 9 PASS / 0 FAIL; full suite not re-run (named). Own mutants below: 8 of 9 killed | CONFIRMED | - |

Own mutants (sandbox copies `E:/TaxoArena_tmp/rv_bbh_mut_20261028/<id>`, TMP/TEMP/TMPDIR/BZ_SANDBOX redirected; killed =
rc != 0 or a `^SELFTEST .*: FAIL$` line; R0 control: rc 0, 9 PASS):
- R1 folds not grouped by content cluster: killed (S3). Decisive (twin leakage into the kNN field).
- R2 random arm = V0's own cells: killed (S3). Decisive (V0 vs random word).
- R3 K2 arm A reads C1(N): killed (S9). Decisive (K2 word).
- R4 cluster cos 0.98 -> 0.90: killed (IndexError crash, not an assertion). Decisive (SE clusters).
- R5 merged tree grouped by the hidden subtask: SURVIVED (the selftest never runs `build_world`); the real path refuses
  it (`anchor_check`, row 12) and the record pickle was checked directly. Not decisive on the run (L2).
- R6 V0-leaf SE computed on content clusters: killed (S5). Not decisive (descriptive SE; C1 reads it).
- R7 recovery null cAMI divided by Hbar: killed (S6). Not decisive on the run (cAMI < 0 either way).
- G1 guard parquet filter removed; G2 returned RESERVED values not counted (builder C17 / C18, regression): killed
  (test_guard_reads_work_only_and_counts). Decisive (the seal).

## What it licenses / does not

- **Licenses** (exploratory description of BBH as a fourth benchmark; WORK rows, 3,457 items x the seeded 128 models):
  the BBH data object (census, sealed split, per-model WORK accuracy); on BBH the axis tree's C1 is not shown at 3 SE,
  k-means reaches it (K1 KILLED) and it is not distinguishable from size-matched random cells (underpowered: realised
  MDE80 0.2775 vs the planned 0.112); the text-kNN reader's gain +2.48 (0.39), concentrated in 3 templated subtasks; at
  the axis rule's resolution (5 leaves per merged anchor) V0m and Km split on scenario templates, not on 3/5/7.
- **Does NOT license:** any RESERVED, vault, registered or confirmatory statement; "a partition is not needed on BBH"
  without C1's qualifier; "the embedding cannot see the 3/5/7 count" (C3); "the tree finds no structure in BBH" (a NOT
  SHOWN at MDE80 0.28); any statement about the full 342-model roster (L5); attributing BBH's DEFF to templated items
  (C2); replacing V0 anywhere; pooling BBH with MATH / MMLU / MMLU-Pro words.

## Defects and conditions

- **C1 (HIGH; record condition): K2 KILLED on BBH is carried by three subtasks.** Quote it as "K2 KILLED on BBH
  (content-cluster SE, the plan's; arm A is 1.74 SE clustered by subtask and 1.87 by V0 leaf; geometric_shapes,
  disambiguation_qa and boolean_expressions carry 83% of N's gain; on the other 21 subtasks G(N|L2+V0) +0.29 (0.32))".
  The hand-back's NUMBERS OF RECORD print the word without this. Fix: registrar brackets [P2] reading (2) and any
  ledger chip; a BBH follow-up that reads K2 clusters by subtask and is DESCRIPTIVE-ONLY at 24 clusters.
- **C2 (MEDIUM): the DEFF attribution is wrong.** Content clusters inflate the variance by 1.06-1.37 only; the rest of
  DEFF 11-15 is within-item correlation of the 128 models' cells, absent on MATH (DEFF 1.05). Fix: bracket [P2]
  "DEFF 11-15 from templated items" and the hand-back's "because BBH items are templated" to "within-item (cross-model)
  correlation; content-cluster factor 1.06-1.37 (POSTRUN_BBH-WORK row 10)". Any BBH power plan uses the realised SE,
  not FLAT-COMPARE's MATH scaling.
- **C3 (MEDIUM): DOES NOT RECOVER is about the split order, not the embedding.** On the same 512-d rows a 5-fold
  logistic probe classifies 3/5/7 at accuracy 1.000 in both merged anchors (chance 0.333); k-means at k = 15 gives AMI
  0.574 (k = 3: -0.002). The plan's section 6 already says a DOES NOT "is informative only about the axis rule's split
  choices". Fix: bracket [P2] reading (3) "invisible to both text partitions" with "at V0m's 5-leaf resolution; the
  count is linearly present in the embedding (probe 1.000)".
- **L1 (LOW): DEFF is not re-measurable from the files of record.** The parts keep per-item G only, not the cell
  differences. Fix (future runners): save the per-item cell-iid variance term or the seed-averaged cell differences.
- **L2 (LOW): selftest gap on the build path.** R5 survives; the hidden-label property rests on `anchor_check` and on
  this review's check of the merged pickle. Fix: a fixture call of `build_world("merged")` asserting depth-1 = 20.
- **L3 (LOW): RESERVED text is read.** Embedding, trees, ND-1 and the census read all 5,761 texts (V0's convention); the
  response seal is intact. A future RESERVED registration must state whether trees built on all items' text are
  admissible (transductive text use).
- **L4 (LOW): plan working copy has mixed EOL** (83 CRLF lines in [P2]). The LF blob 33dc3326 is of record. No action
  beyond naming both renderings.
- **L5 (LOW): roster.** Every harness number is for the seeded 128 of 342 (6 of 18 NC-1). A full-342 re-run (about 18 h
  on 2 workers) is the author's, optional.

## Commands (scripts in `E:/TaxoArena_tmp/rv_bbh_review_20261028/`; read-only on every record file)

```
# hygiene (in Z:/FAC/TUBerlin/benchzoom_wt_bbh)
git log --format='%h %ci %s' 35b2724..ee1e508; git diff --name-only 35b2724..ee1e508 | wc -l          # 10
git diff --name-only 35b2724..ee1e508 -- src docs/execution_graph.md | wc -l                           # 0
git diff aec5385 ee1e508 -- docs/bbh-work.md | grep '^-' | grep -v '^---' | wc -l                       # 0
git diff -U0 a77e058 ee1e508 -- examples/bbh-work.py | grep '^@@'; git merge-tree --write-tree master ee1e508
for f in <10 files>; do git hash-object $f; git rev-parse HEAD:$f; done; tr -cd '\r' < docs/bbh-work.md | wc -c   # 83
find E:/benchzoom_demo/followups/bbh-work E:/TaxoArena_tmp/bbh-work -path '*/mut*' -prune -o -type f ! -newermt '2026-10-27 18:13:33' -print
sha256sum -c SHA256SUMS   # in bbh-work 14/14, census_r2 8/8, split 3/3, work_accuracy 3/3, backup bbh-work 23/23
# data object and numbers (own code; venv python -I)
python rv_raw.py "01-ai/Yi-1.5-6B-Chat,NousResearch/Yarn-Mistral-7b-128k,google/gemma-1.1-2b-it" E:/TaxoArena_tmp/review_bbh_raw_20261028
python rv_census.py; python rv_numbers.py; python rv_recovery.py; python rv_probe.py; python rv_guardcheck.py
python rv_embed.py        # local Ollama embedder only; keep_alive 0
python rv_harness.py      # own harness from library primitives, main world g2, 25 tasks, 2 workers
# tests and mutants
PYTHONPATH=src python -m pytest tests/test_bbh.py tests/test_bbh_work.py -q -p no:cacheprovider   # 25 passed
python rv_mut.py          # R0-R7, G1-G2
```
