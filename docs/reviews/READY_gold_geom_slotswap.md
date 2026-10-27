# READY review: MMLU-GOLD-GEOMETRY (mmlu-gold-geom 6402ee6), INTENT-S0-SLOTSWAP-MECH (slotswap-mech db060d4), delta rp12-flat-pin (bd3c3be)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls. No --dry-run or --run on data. I did not open embeddings_cache.db or
multicorpus_cache_v1.db (RP12 constructions were running: java.exe PID 30652 seen by `tasklist`). Read-only reads I did make:
the raw leaderboard jsonl files (src census), the S0 intent DBs (`mode=ro&immutable=1`, the R-2 presence count), and
committed files. Registrations: prog "## Registered 2026-10-01 ... INTENT-S0-SLOTSWAP-MECH" L22301-L22330 and "...
MMLU-GOLD-GEOMETRY" L22332-L22357, `_as_of` b909414. Census bracket: prog L22242-L22250 (e7348f3). Ledger v321 is unchanged.

## Verdicts

| branch | merge | --dry-run | --run |
|---|---|---|---|
| mmlu-gold-geom 6402ee6 | MERGEABLE (1 new file, tools/analysis only) | READY on GC-1..GC-3 | READY after the dry-run meets GC-2, GG-D1 is discharged, and the registrar brackets GB1-GB4 (GC-4). It runs before G12 is read (B-A2, R-3) |
| slotswap-mech db060d4 | MERGEABLE (1 new file, tools/analysis only) | READY on SC-1, SC-2 | READY after the registrar brackets SB1-SB5 (SC-3) and reads the dry-run's tercile sizes (SC-4) |
| rp12-flat-pin bd3c3be | MERGEABLE (4 files, tools/analysis only; 0 of them changed on main since 87ee41e) | FLAT READY now. The pointer entry B0/mmlu_pro_lb is on main (4fad894) with snapshot_id 20261001_070346_Headless_Run_Auto_ge, which equals the pin. F-2 and F-4 of READY_rp12_pair_mc stand | READY after F-2 prints `[F-3] T2 census equals the pin` |

Pins (all LF; each worktree's rendering equals the commit blob, so there is no CRLF variant):
- mmlu_gold_geometry.py blob:5ab1c87846e56cdd29da72f557e97ccb00645260.
- intent_s0_slotswap_mech.py blob:7821815544e47679f611204d9bbd02a039bd46d4.
- flat_v2.py 61d35abd; rp12_pairing.py d6b75fc2; g11_reader.py ddf9a22b; g12_site_null.py 115e6d9b.
- intent_transfer_s0.py on main = blob f662ceb1 (the imported, asserted blob). It and its dependencies are unchanged 9b218b8..main (count 0).

## Per-claim table (deciding claims)

| # | claim | result | evidence (mine vs claimed) | sev |
|---|---|---|---|---|
| G1 | selftest 54/54 | CONFIRMED | rerun: 54 passed, rc 0 | - |
| G2 | mutants 37/37 killed, not vacuous | CONFIRMED | rerun: 37/37, all killed by an assertion, no crash kills. Exact values are asserted (join 1006/1/1, assignment digest, text digest, p95). My mutants: GG-M1 GB1 index prepended (seed 2102) KILLED; GG-M2 little-endian decode KILLED (crash in linkage); GG-M3 ambiguous EVAL key counted as src SURVIVED (a disclosure count only; GG-D2) | LOW |
| G3 | join by the options key, never by text | CONFIRMED | okey = json.dumps of the stripped options. DB side: extract_options. The "join by text" mutant is killed by the nesting refusal. Raw census (3 files, 12,032 docs each, the files agree): 91 src, 14 categories, 0 src under 2 or more categories, 11,869 keys, 1 ambiguous key. This equals the steward's 91 / 14. Per category: law 3, psychology 3 (min), physics 11 (max) | - |
| G4 | 6,992 TRAIN items is the member | CONFIRMED (definition) / UNDETERMINED (value) | The script counts distinct `i:`+stem_key over MMLU_PRO rows tagged mc6, side TRAIN, after blanks. This is the [ITEM-CENSUS] definition: rows 7228 -> 6993 texts -> 6992 items. The script prints the same rows -> texts -> items chain and REFUSES on != 6992. The value is first seen at the dry-run | - |
| G5 | the 13 EVAL items with no src are excluded | PARTLY | No EVAL vector or label enters any fit: member() never adds EVAL to `tr`, and the EVAL/GATE mutants are killed. The printed count, though, is over the MMLU_PRO_LB member's EVAL items on the all-corpora side export, not over pv2_41's 3,492. The docstring's "13 of 3,492" names another denominator. The count also reads the options of EVAL rows ("reads no EVAL row" holds for vectors and labels only) | LOW (GG-D2) |
| G6 | the 1,000-permutation null matches | CONFIRMED | Fixture: my own sklearn recomputation at seed 2105 gives p95 0.027453 = the builder's 0.0275. The script asserts d2's p95 equals a replica (guard mutation-killed). Real gold map (raw composition, labels sorted by src; ARI does not change if categories are renamed): p95 **0.0264**, null mean -0.0005, SD 0.0155 at seed 2105 (0.0264 at 2102, so GB1's seed does not matter) | - |
| G7 | Support (b)-(f) | CONFIRMED, conservative | The transported SD was 0.018; I measured 0.0155. MDE80 = 2.485 x 0.0155 = **0.0384** (registered 0.045). The bar is about 0.026 (assumed about 0.03). Still SCOREABLE: prediction 0.30, lower 80% bound 0.12 | - |
| G8 | cannot run beside a construction | CONFIRMED | heavy_check (java.exe) runs in both --dry-run and --run before any DB open (2 mutants killed). The sidecar check refuses a non-empty -wal. All tables of embeddings_cache and corpus_questions are hashed before and after the run; a change REFUSES, which catches a build that starts mid-run, because builds rewrite queries. Gap: no ollama check (GG-D5) | LOW |
| G9 | the vector is the representation G12's tree saw | UNDETERMINED | The script keys vectors by corpus_questions.text (the min-qid row). The B0 construction keys by queries.distilled_text (READY_rp12_pair_mc #8: 6,993 distinct distilled texts). The counts agree; identity is not shown | MEDIUM (GG-D1) |
| S1 | selftest 84/84 | CONFIRMED | rerun: 84 passed, rc 0 | - |
| S2 | mutants 40/40 killed, not vacuous | CONFIRMED | rerun: 40/40, all killed by an assertion. E2E D_Q / D_T equal an independent recomputation (own k-means, regex shares, own mid-rank groups). My mutants: SS-M1 margin from gemma origins KILLED; SS-M2 D_T against the middle tercile KILLED; SS-M3 D_T CI draws unweighted KILLED | - |
| S3 | all 3,222 variants present (R-2) | CONFIRMED | Read-only count with S0's own text_set: 3,222 / 3,222 in each of intent_emb_qwen3 / nomic / gemma; all 57,350 texts present in each; 3,207 components. Note: 3,215 distinct variant texts, so 7 texts are shared across origins (descriptive) | - |
| S4 | reproduces S 0.75978 | UNDETERMINED (by design) | Not run (it needs the k-means; one heavy process, beside a construction). --run REFUSES unless S is within 5e-6, n = 3,222 and components = 3,207 (the record S is 2448/3222 = 0.7597765; tolerance admits that count only). The 3 mutants on this guard are killed | - |
| S5 | criteria as registered | CONFIRMED | M1 HELD iff lower >= 0.10, FAILED iff upper < 0.10. M2 HELD iff lower > 0, FAILED iff upper <= 0. The interval decides (point mutants killed). Margin = top1 - top2 of the EVAL origin vs c4's seed-0 Cm0. flip = 1 - same0. One component weight stream; M3 is paired | - |
| S6 | Support (d)-(e) | CONFIRMED | M1 sqrt(0.33/640) x 1.00464 = 0.0228, MDE 0.0639. M2 sqrt(0.42/1070) x 1.00464 = 0.0199, MDE 0.0557. M3 sqrt(0.25/3192) = 0.00885, MDE 0.0248. DEFF 1.0093 = Kish sum m^2 / sum m, which equals 15 pairs in 3,207 components (S0 outcome L33). R-1 re-computes the SE at the realised sizes at --run | - |
| S7 | cannot run beside a construction | CONFIRMED | heavy_check in both modes (mutants killed). sha256 of the 4 DBs before and after; strict pins at --run | - |
| F1 | D-1 exclusion line names G11 / G13 only; g11 re-pinned | CONFIRMED | PAIRING_PIN d6b75fc2 = `git hash-object` rp12_pairing.py at bd3c3be. My FM-2 reverted the pin to 5fc484de: the g11 selftest REFUSES | - |
| F2 | D-2 mixed depths; RD killed | CONFIRMED | My RD (`!= [1]` -> `1 not in`): g12 selftest 8/9, killed | - |
| F3 | F-3 census pinned 74 / 6993 / 20261001_070346 | CONFIRMED | Equals READY_rp12_pair_mc #8 and the pointer entry on main. check_census refuses each field alone. --run and --analyze call it before FM.fit_set | - |
| F4 | selftests 13/4/7/9/6 | CONFIRMED | rerun: flat_v2 13/13, rp12_pairing 4/4, g11 7/7, g12 9/9, g13 6/6 | - |
| F5 | the census check in --run / --analyze measures the census | PARTLY | My FM-1 (census_of returns the pin itself, line count kept) SURVIVED 13/13. census_of runs in no selftest; the dry-run path computes it independently through t2_census | LOW (FP-D1) |

Disclosed read (gold-geom builder): one schema/count query on multicorpus_cache_v1.db with `mode=ro&immutable=1` during an RP12
build. RULING: a procedural breach of rule 7's letter (a reader of a construction's input DB inside the build window). It has no
evidential consequence. immutable=1 takes no lock and writes no sidecar: the -wal is 0 bytes (mtime Sep 15) and the -shm mtime
is Sep 23, so neither was touched today. No B0/B0p output can depend on it, so nothing is rebuilt. LOW. The outcome's hygiene
line records it; builders do not open DBs of record during a build window.

## Conditions

- GC-1 / SC-1 (rule 7): --dry-run and --run start only when no java.exe runs and no construction, site null or Ollama embedding
  is in flight (W1-W5; one heavy process). Both scripts refuse on java.exe; the operator checks the rest.
- GC-2 / SC-2: run from the main checkout after the merge. In a worktree, ROOT / OUT_DIR point at the worktree, and the DBs
  and raw files are not there.
- GC-2: the gold dry-run must print TRAIN items 6,992, labels 91 in 14 with min >= 10 per label, and all kept texts with a
  4096-d vector. Any other value is a refusal or a STOP; nothing is imputed.
- GC-3 (GG-D1): before --run, the operator runs one read-only count in the same rule-7 window. It counts how many of the kept
  representative texts equal a queries.distilled_text of the B0 MMLU_PRO_LB snapshot's root ids. If it is short of all kept
  items: STOP to the registrar (which text decides is the registrar's).
- GC-4 / SC-3: the registrar brackets GB1-GB4 and SB1-SB5 before any --run. My readings: GB1 acceptable (the seed is
  immaterial, p95 0.0264 at both seeds). SB1 is R-1's rule, but an empty tercile reads UNDETERMINED for structural reasons.
  SB2 (variant-side share) is a free choice that must be fixed pre-data.
- SC-4: the registrar reads the dry-run's realised swap-share tercile sizes before --run. They are data, not the outcome.
- POST-RUN check (gold): with all 91 labels kept, d2's p95 must equal **0.0264** (seed 2105). A different value means the label
  set differs from the raw census.
- FLAT: F-2 and F-4 unchanged. B0p/o1 builds are running now, so the F-2 dry-run waits.

## Defects (each with a fix)

- GG-D1 MEDIUM: the vector input is not shown to be the construction's (G9). Fix: GC-3, or a dry-run line in a reviewed delta.
- GG-D2 LOW: the EVAL-without-src count has another denominator than "13 of 3,492", and GG-M3 survives (no ambiguous EVAL key in
  the fixture). Fix: print "of N MMLU_PRO_LB EVAL items on the 5a3e756 export"; add one ambiguous EVAL key to the fixture.
- GG-D3 LOW: the TRAIN-ONLY audit cannot fail, because corpus_of labels every kept item TRAIN. The real guard is member()'s side
  filter, which is mutation-killed. Fix: take the side from the export in corpus_of, or reword the audit line.
- GG-D4 LOW (info): the registered null ARI(gold, perm(gold)) keeps the gold sizes, not the cut's. It binds as registered (S0 D2
  verbatim). Fix: none before the run; DOES NOT SHOW may name it.
- GG-D5 / SS-D3 LOW: heavy_check sees java.exe only. Fix: add ollama.exe, or leave it to the operator's W1-W5 (GC-1).
- SS-D1 LOW: the dry-run prints the M1 SE at the nominal [644]*5 under the words "realised quintile sizes". Fix: say "nominal".
- SS-D2 LOW: support_lines names kish(comp) = 1.0093 both "Kish mean cluster size" and DEFF; the registration's 1.0047 is the
  plain mean. Fix: wording.
- FP-D1 LOW: census_of runs in no selftest (FM-1 survives). Fix: one case that patches FM.load_snapshot_graph with a fixture
  graph and asserts census_of == t2_census.

## Commands

```
git rev-parse 6402ee6:tools/analysis/mmlu_gold_geometry.py; git -C .claude/worktrees/mmlu-gold-geom hash-object tools/analysis/mmlu_gold_geometry.py   # 5ab1c878 x2
git rev-parse db060d4:tools/analysis/intent_s0_slotswap_mech.py; git -C .claude/worktrees/slotswap-mech hash-object ...                                # 78218155 x2
git diff --name-only <merge-base>..<tip> | grep -vc '^tools/analysis/'      # 0 for all three branches
git diff --name-only 87ee41e..main -- tools/analysis/{flat_v2,rp12_pairing,g11_reader,g12_site_null,g13_comparator}.py | wc -l   # 0
git diff --name-only 9b218b8..main -- tools/analysis/intent_transfer_s0.py intent_ingest.py split_side.py v2_engine_pool.py data_v2/ embedder_arms.py | wc -l  # 0
python tools/analysis/mmlu_gold_geometry.py --selftest | --mutants          # 54 passed; 37 of 37 KILLED
python tools/analysis/intent_s0_slotswap_mech.py --selftest | --mutants    # 84 passed; 40 of 40 KILLED
python tools/analysis/{flat_v2,rp12_pairing,g11_reader,g12_site_null,g13_comparator}.py --selftest   # 13/13 4/4 7/7 9/9 6/6
scratchpad/ggrev/own_mut.py (GG-M1..3, SS-M1..3: exec of the edited source, selftest on the builder's fixtures)
scratchpad/ggrev/mut.py (FM-1 census_of -> pin, line count kept: 13/13 SURVIVED; FM-2 g11 pin revert: REFUSED; RD: 8/9 KILLED; no-op control 13/13)
raw census: first 3 sorted samples_leaderboard_mmlu_pro_*.jsonl -> 12,032 docs each, agree; 91 src / 14 cats / 0 nesting breaks / 1 ambiguous key
null: sklearn ARI(gold, rng.permutation(gold)), default_rng(2105), 1,000 reps -> fixture p95 0.027453; real map p95 0.0264, SD 0.0155
R-2: ITS.load_corpora + ITS.text_set on intent_transfer_corpora_v1.db; ITS.present_texts per intent_emb_*.db -> 3222/3222 x3; 57350/57350 x3
side export LF sha256 47e9048bb09a6910a2d511cf3c3f4d8ba734ef44ca78c87f7a60a9fc99cc4764 (= SIDE_SHA_LF = pointer stamp sideExportSha256Lf)
pointer: experiment_configs/rp12/objects_of_record.json entries['B0/mmlu_pro_lb'].snapshot_id = 20261001_070346_Headless_Run_Auto_ge (4fad894 on main)
ls -la multicorpus_cache_v1.db* embeddings_cache.db*   # -wal 0 bytes; no sidecar touched today (directory listing only, no open)
```
