# STEWARD: ck-v1 = CK-CLOSE-v1 stem_key, and the af_clean_s42 fit / held-out closure (FLAT-MIX-MMLU READY precondition)

Data-steward, 2026-09-26. Zero calls. Read-only: every DB opened `mode=ro&immutable=1` after checking that its `-wal` / `-journal`
is empty (embeddings_cache.db-wal, mmlu_pro_dataset_cache_v2.db-wal, snapshots.db-wal: 0 bytes each). snapshots_frozen.db not opened.
Registration: FLAT-MIX-MMLU, docs/judge_v2_program.md L20672-L20735 (commit 31d092e), "READY CHECK (the data-steward)" at L20679.
Checkout at HEAD af5871b.

## VERDICT: CONFIRMED (all three items), with one descriptive hazard below norm-v1

| # | claim | result |
|---|---|---|
| 1 | engine keyRule `ck-v1` = CK-CLOSE-v1 `split_side.stem_key` at norm-v1 | CONFIRMED: same normaliser, same fields, same separators and hash; 11,769 / 11,769 real texts give identical keys, 0 mismatches |
| 2 | 3,445 held-out questions vs the 8,125 fit texts, same stem_key | CONFIRMED: **0 / 3,445** (exact-text overlap also 0); held-out stem_key groups 3,445, all singletons, Kish mean size 1.0000 |
| 3 | the 171 closure moves were applied before the tree was built | CONFIRMED: the 171 rows (153 distinct texts) are in NONE of the tree's 8,125 fit texts; the snapshot's root region equals the post-closure train side exactly |

On item 3's wording: the closure moves rows **out of** the train side and **into** test as routing-only members
(MMLUDatasetFetcher.kt L874-L878). "Applied before the build" therefore means the moved rows are **absent** from the tree's train
side (its fit set), not present in it. That is what I checked, and it holds.

## 1. The engine key and the CK-CLOSE-v1 key

The spec: CK-CLOSE-v1 was adopted 2026-09-23 (docs/judge_v2_program.md L15013-L15025). Its key is "`split_side.stem_key` (norm-v1,
options-free; tools/analysis/split_side.py L80)". The four conditions are at L14324.

| | Python, CK-CLOSE-v1 key (tools/analysis/split_side.py, blob 05224b5a) | Kotlin, engine key (src/main/kotlin/taxonomy/dataset/SplitSide.kt, blob 4b099de1) |
|---|---|---|
| version tags | `NORMALISER_VERSION = "norm-v1"`, `KEY_RULE = "ck-v1"` (L31-L32) | `NORMALISER_VERSION = "norm-v1"`, `KEY_RULE = "ck-v1"` (L31-L32) |
| separators | `FIELD_SEP` U+001F, `OPTION_SEP` U+001E (L38-L39) | same (L38-L39) |
| whitespace | explicit class `WHITESPACE_CLASS` (L46) | the byte-identical string (L42) |
| norm | NFKC; ASCII-only A-Z to a-z; whitespace runs to one U+0020; strip U+0020 (L55-L60) | NFKC; ASCII-only A-Z to a-z; whitespace runs to one U+0020; trim U+0020 (L46-L52) |
| content key | sha256 hex of norm(stem) + US + concat(RS + norm(opt), options sorted by UTF-8 bytes) + US + contract_id (L67-L77) | the same payload, options sorted by UTF-8 byte order (L73-L78) |
| stem key | `content_key(text, [], "")` (L80-L83) | `contentKey(text, emptyList(), "")` (L81) |

Where the engine uses it: `MMLUDatasetFetcher.finishSplit` (L863-L902).
- It builds testKeys from `SplitSide.stemKey` over every test item. At the pin these are the 3,599 file ids, **sentinels
  included**, which is CK-CLOSE-v1 condition 1.
- It moves every train item whose stemKey is in testKeys (L871-L878) and logs `[SPLIT-CLOSURE]` (L882).
- It asserts side == tierA(...) for every item (L889-L898).
- The stamp printed in the build log comes from `SplitSide.stamp` (L115-L116).

Pinned at the build: af_clean_s42 was built at 190cb485 (build.out: "src/main is clean").
- `git rev-parse 190cb485:<path>` equals HEAD for SplitSide.kt (blob 4b099de1) and split_side.py (blob 05224b5a).
- Both last changed at 13f2142 (2026-09-16), and neither is modified in the working tree.
- The MMLUDatasetFetcher.kt diff between 190cb485 and HEAD (+99 lines) touches no split, closure or stemKey line.

The test ran on the real texts, not a 500-text sample.
- The texts: all **11,769** distinct texts in fit + held-out + the 3,599 test rows + the moved rows. They include 1,860 non-ASCII
  texts and 608 where norm-v1 differs from lower()+strip().
- Python keys: `split_side.stem_key`.
- Kotlin keys: `taxonomy.dataset.SplitSide.INSTANCE.stemKey`, called from a Java harness on the compiled class
  build/classes/kotlin/main/taxonomy/dataset/SplitSide.class (sha256 7344ff4c...). The class was compiled 2026-09-19, after the last
  source change on 09-16.
  - Disclosed harness deviation: kotlin-stdlib 2.2.20 was on the classpath, while the project compiles against 2.1.10. The stdlib is
    backward-compatible for the calls used.
- Result: `kotlin keys 11769 mismatches vs python 0 keyRule=ck-v1 norm=norm-v1`.
- The line-level comparison is exact. The two key files differ only in line endings: the Python dump used CRLF.

Discriminator: Python mutants of norm show that the comparison can fail. Mismatches against the Kotlin keys:

| mutant | mismatches |
|---|---|
| no NFKC | 89 |
| full `str.lower()` instead of the ASCII fold | 30 |
| no whitespace collapse | 766 |
| no case fold | 11,726 |
| raw text | 11,731 |
| Python `str.split()` whitespace | 0 (it coincides on this corpus; the explicit class is what the spec pins) |

The unmutated `split_side.norm` gives 0.

## 2. Held-out vs fit set, on the real sets

Sources, as the FLAT-MIX-MMLU instrument defines them (flat_mix_mmlu.py on gmm-tests at 772e059):
- **Fit set.** Snapshot 20260917_201353_Headless_Run_Auto_ge in snapshots.db. `regionQueryIds(rootId)` gives 8,125 ids, all of which
  resolve through embeddings_cache.db `queries.distilled_text`, giving **8,125 distinct texts**.
- **Held-out.** The 3,445 judgeable ids of experiment_configs/reserved_pool_frozen_p2dca.json (3,599 ids; 154 sentinels), mapped by
  eval id to `eval_question_link.question_text`. This gives **3,445 distinct texts**, as anchor_free_readout.corpus defines them.

Independent reconstruction of the engine split, following loadFromDb and formatData:
- Read the mmlu_pro rows LEFT JOIN eval_question_link on `mmlu_pro_row_id` (the link table, not a text join). The id is question_id,
  or -1000000 - rowid when there is no link.
- 12,000 rows split into **8,401 train / 3,599 test**.
- stem_key closure moves **171**, leaving **8,230 train**.
- Those 8,230 rows carry **8,125 distinct texts**, and the set is **identical** to the snapshot fit set (0 / 0 set difference).

This matches build.out L28 and L30-L32 exactly: 8401 / 3599; `[SPLIT-CLOSURE] 171`; `8230 train (843 gate) / 3770 test`;
`keyRule=ck-v1`.

Counts. Denominator: the 3,445 judgeable held-out questions of p2dca21ab5f4ef3ae.
- Held-out whose stem_key equals a fit text's stem_key: **0 / 3,445**.
- Exact text overlap: **0**.
- Keyed on the judgeable ids' mmlu_pro-row texts instead of the link texts: the stems agree 3,445 / 3,445 and the fit overlap is 0.
- Fit texts whose key is in the full 3,599-row test key set (the set the closure keyed on, sentinels included): **0 / 8,125**.
- Within-held-out stem_key twin groups: **3,445 groups, max size 1, Kish mean size 1.0000**. The DEFF bracket from twins is [1, 1], so
  n_eff = 3,445 for C1's cluster unit. This confirms the registrar's B3 / B7 ruling (L20693).

### Near-duplicates below norm-v1 (DESCRIPTIVE ONLY; CK-CLOSE-v1 by definition does not catch these)

Method:
- Vectors come from embeddings_cache.db `embeddings`: qwen3-embedding, 4,096 d, big-endian float32, keyed by text. They were found
  for 8,125 / 8,125 fit and 3,445 / 3,445 held-out texts.
- Each vector is unit-normalised at the full 4,096 d, and also at the 256-d prefix slice the arms use.
- Exact brute-force cosine matrix, 3,445 x 8,125, single-threaded (BLAS threads = 1), 4 s wall. No MinHash and no sampling.

| slice | threshold | cross pairs | held-out with >= 1 fit partner | distinct fit partners |
|---|---|---|---|---|
| 4096 | cos >= 0.99 | 19 | 19 / 3,445 | 19 |
| 4096 | cos >= 0.98 | 39 | **37 / 3,445 (1.07%)** | 36 |
| 4096 | cos >= 0.95 | 94 | 80 / 3,445 | 77 |
| 256 | cos >= 0.99 | 24 | 24 / 3,445 | 24 |
| 256 | cos >= 0.98 | 48 | **45 / 3,445 (1.31%)** | 44 |
| 256 | cos >= 0.95 | 110 | 94 / 3,445 | 91 |

The median held-out-to-fit max cosine is 0.668 at 4096 d and 0.707 at 256 d.

Character check of the 37 held-out questions at 4096 cos >= 0.98, using the difflib ratio on the norm-v1 texts of the best partner:
- 32 at >= 0.95, 3 in 0.90-0.95, 2 in 0.80-0.90.
- Most are the same question differing by punctuation, spacing, a unit glyph or one word. Examples: "298K" vs "298 K"; "annular
  spacebetween" vs "annular space between"; a dropped pair of parentheses in a formula.
- At least one pair is a different question with the same frame and a different answer: "Balls are identical besides of their
  colors" vs "Balls are distinct even with the same color".

So 37 (4096) / 45 (256) is an upper-bound description of near-copy leakage, not a count of copies.

## 3. The 171 closure moves precede the build

Build-log order, experiment_results/anchorfree/redraw/af_clean_s42.build.out:

| line | log entry |
|---|---|
| L30 | `20:12:33.461 [SPLIT-CLOSURE] 171 ...` |
| L31 | `20:12:33.705 [SPLIT-SIDE] 8230 train (843 gate) / 3770 test ... keyRule=ck-v1` |
| L32 | `closedByContent=171` |
| L71 | `20:12:33.960 [ANCHOR-FREE] 8125 train queries placed at the root` |
| L1907 | `[TRAIN-ONLY] after construction: 0 EVAL texts among the tree's members` |
| L1913 | `[TRAIN-ONLY] saveSnapshot: 0 EVAL texts ... (3445 pool texts checked)` |
| L1914 | snapshot 20260917_201353_Headless_Run_Auto_ge saved |

The data:
- The 171 moved rows (153 distinct texts; 94 carry sentinel ids) have **0** texts and **0** stem_keys in the snapshot's 8,125 fit
  texts.
- The post-closure train side (8,230 rows, 8,125 texts) equals the fit set exactly.
- Without the closure, the root would have held 8,125 + 153 = 8,278 texts. That is the member count of bareq512_s42, which was built
  before the closure existed (L14306), and it corroborates the result.
- Partners of the moved rows: 96 are sentinel-only test rows, 73 judgeable-only, 2 both. So condition 1 (sentinels in the key set)
  did work here: 96 moves would have been missed without it (the review's "96 GEN rows").
- The snapshot's `reserved_queries` column lists 3,599 ids, equal to the pool file.

## Hazards the analysis must carry

1. **Near-duplicates below norm-v1 are now MEASURED, descriptively.**
   - 37 / 3,445 held-out questions (4096 d; 45 at the 256 slice) have a fit text at cos >= 0.98. Most are punctuation or spacing
     variants of the same question.
   - The registration's "near-duplicate leakage below norm-v1 ... not measured" (L20679, L20733) stays correct as a statement about
     CK-CLOSE-v1.
   - Any use of "held-out" should carry the qualifier "content-closed at norm-v1; about 1.1% of held-out questions have an embedding
     near-copy (cos >= 0.98) in the fit set".
   - It affects M4 (held-out log-likelihood) and M1 for every arm alike, so it should not favour an arm, but it is not zero.
   - The embedding store's text key is not options-aware.
2. **Evidence is untracked.** af_clean_s42.build.out (git blob-hash 111c9d61...) is not in git. The READY cites its lines, so the file
   should be tracked or its hash pinned. I did not touch it.
3. **A log count is unreconciled.** build.out L1907 says "3644 keys checked". I count 3,563 distinct stem_keys over the 3,599 test
   rows (3,575 distinct texts). The verdict does not depend on it (0 fit texts share any test key). It is named here because I did
   not reproduce it.
4. **The fit texts are read through embeddings_cache.db `queries` ids.** Every construction rewrites that table (the steward's memory
   note). Today all 8,125 snapshot ids resolve, and they resolve to exactly the post-closure train texts. The instrument's 8,125
   assertion is the guard against later drift.

## Reproduction

The scratch scripts are in the session scratchpad `ckv1/` and are not committed:
- `steward_ckv1.py`: split reconstruction, snapshot fit set, key counts, dump.
- `KtKeys.java`: Kotlin keys through the compiled SplitSide.
- `discrim.py`: the mutants, and the check that reserved_queries equals the pool file.
- `neardup.py`: the cosines.

Their printed outputs are quoted above verbatim. There is no DB write anywhere.
