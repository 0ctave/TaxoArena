# READY review: TEMP-SPRAWL / scratch-dir-e (tip 26378771, base abde9a22), 2026-10-04, zero calls

**VERDICT: NOT MERGEABLE as-is; MERGEABLE after D-1 (one guard plus one selftest check in scratch_dir.py; delta review of
that file only) and C-1/C-2.** The import path (36 scripts, Gradle, Kotlin) is CONFIRMED. The `--purge-stale` CLI is not
safe: if its root is not a dedicated base, it deletes whatever it finds there.

Reviewed blobs (LF, `git rev-parse 26378771:<path>`): scratch_dir.py b3f9ab22 (working tree identical); build.gradle.kts
99390bb2 (worktree CRLF rendering 2002f2fb, autocrlf=true); TestTmp.kt ebc58ab6.

## Per-claim table (deciding claims)
| # | Claim | Result | My evidence | Sev |
|---|---|---|---|---|
| 1a | 36 scripts: logic unchanged except temp location | CONFIRMED | 39 changed line pairs (escalation_rc 2, flat_v2 3, 34x1). In all 39/39 the only change is `; import scratch_dir` appended to the `import tempfile` line (comments ignored). 0 lines added or removed, so no anchor moves. | - |
| 1b | none of the 36 is blob-pinned (a pinner would refuse) | CONFIRMED (code) | Old LF/CRLF blob[:8] and sha256[:8] (LF/CRLF) of all 36 grepped with `git grep` in tools/ src/ experiment_configs/ config/ build.gradle.kts at main and at the tip: 2 hits, neither is an assertion. v2_declared_cells.py L60 mentions router_clean_policy blob 2a726529 in its docstring only; there is no blob compare (grep of `blob` in that file). dataset_survey_table_w0_steward.csv cites supergpqa_stage0 35b11858 as a source. | - |
| 1c | provenance of pending runs | PARTLY | DATASET-SURVEY is in state `built`. READY_w0_delta2 L100 pins dataset_survey.py d83f3824, which the edit makes df460e6c, so a run from the merged tree would not match its READY pin. 14 more scripts are pinned in READY-only review files (list in the commands block). Every script that prints its own blob (fitset_intent, gemma_own_bar, gold_level_emb, oos_tree_cells, g11_reader, lcb_power_resim, ...) will print the new blob when rerun. | MEDIUM (C-1) |
| 2 | parity, original vs edited | CONFIRMED | Full-tree extracts of abde9a22 and 26378771 (minus experiment_results), the same 15 jobs on both sides. rc identical 15/15. Normalised stdout differs in 1 line only: card_protocol_writer's W-GO DISK GB, which now reads E: (275.8) instead of C: (116.4); expected. Selftests: dataset_survey 21, card_protocol_writer 88, union_af_route_ops 4/4, transport_check, escalation_rc 6/6, e1_split_draws 129, results_index, rp12_build_configs, topic_partition_t1b_null 78, judge_solved_split 63+18/18; h9_stability 6/7 on BOTH sides (no git or data in the extract). Mutants: dataset_survey 5/5, union_af_route_ops 11/11, transport_check 7/7, card_protocol_writer 37/37. Edited runs left 0 entries in the sub-base after each job. escalation_rc --mutants was cut off by my job's time limit; its killed child left py_50780_*, which `--purge-stale --root <sub-base>` removed (dead pid, removed 1, failed 0). | - |
| 3a | cleanup never deletes outside its base: links | CONFIRMED | Private base with a junction to OUTSIDE/keep.txt at the top level, inside a dead-pid py_ dir, and inside the live process dir. After purge_stale and cleanup(), OUTSIDE is intact. rmtree_robust(junction) returns False and deletes nothing (shutil.rmtree refuses links on Python 3.11.1). Symlinks cannot be created here without the privilege (winerror 1314); rmtree applies the same refusal. | - |
| 3b | cleanup never deletes outside its base: what "base" is | REFUTED | base() falls back to the SYSTEM TEMP when E: is absent or cannot be created (L90-L97). purge_stale(root=base()) then treats the whole system temp as the base. A dry run with the drive made absent: `removed 6313, kept (young) 1210` entries of C:\Users\octav\AppData\Local\Temp (other applications' files and the claude/ session dirs). The same happens with any `--root` or any TAXOARENA_TMP (for example `E:/`, where the outputs of record live): every non-pid entry older than --days goes. Nothing checks that the root is a dedicated scratch dir. | HIGH (D-1) |
| 4 | Gradle change merges cleanly with main | CONFIRMED; brief premise REFUTED | `git diff abde9a22 main -- build.gradle.kts` is 0 lines: main has NOT changed build.gradle.kts since the base. certPcK2 7, gemmaOwnBar 6 and certKnownPair 6 occurrences are already in the base. `git merge-tree --write-tree main 26378771` gives tree dd8daa69 with rc 0 and no conflicts. Its build.gradle.kts = 99390bb2 (the branch's), with all 3 tasks plus cleanTestTmp. main..merge = the same 45 files. No resolution needed. | - |
| 5 | wrapper works for a pinned script | CONFIRMED | `scratch_dir.py --run -- python tools/analysis/tie_mechanics.py --selftest` (pinned; blob 7f88d2ac unchanged on the tip): rc 0, 29 checks PASS. Run dir removed. E: base entries 17 before, 17 after. 0 new tiemech_* in C: temp. | - |
| 6 | Kotlin suite passes with the tmpdir on E: | UNDETERMINED | Not run: 4 java.exe were live (tasklist), so per the brief Gradle was not started. | C-2 |
| 7 | scratch_dir selftest + mutants M1-M11 | CONFIRMED (selftest) | `--selftest` rc 0, 9 checks C1-C9. Builder's M1-M11 taken as stated; my own mutants below. | - |

## Own mutants (scratch_dir.py; selftest must fail)
- OM1: `_install` reuses the inherited dir for ANY child, not only `--multiprocessing-fork` workers. SURVIVED. Not decisive: no check has a non-mp child inherit TAXOARENA_TMP_PROC; worst case is leftovers, never a deletion. (LOW, D-3)
- OM2: purge_stale treats every pid dir as alive. KILLED (C6).
- OM3: rmtree_robust without its `not islink` guard. SURVIVED. Not decisive: shutil.rmtree refuses links itself (3a). There is no link fixture. (LOW, D-3)
- OM4: cleanup() skips the process dir. KILLED (C3).

## Defects and fixes
- **D-1 (HIGH)**: purge_stale has no guard on what it purges.
  Fix: base() writes a marker `.taxoarena_scratch` into the dedicated base it creates, and never writes it on the system-temp fallback.
  purge_stale refuses (SystemExit, nothing deleted) when either holds:
  - the root lacks the marker;
  - the normcase'd root equals `_SYSTEM_TEMP`, a drive root, or the repo root.
  `--root` gets the same check. Add selftest checks:
  - purge on the fallback / system-temp root refuses;
  - purge on a dir without the marker refuses;
  - a marked base purges as now.
  Add mutants that drop each guard. Write the marker into the existing E:/TaxoArena_tmp once, in the same change.
- **C-1 (MEDIUM)**: provenance. The merge commit (or a one-line bracket in the DATASET-SURVEY record) states that these blobs are the same code apart from the import:
  - dataset_survey d83f3824 -> df460e6c;
  - supergpqa_stage0 35b11858 -> 61741d7f (cited in the steward CSV).
  The survey's operator then runs the new blob against that note. Otherwise revert those 2 edits and run them under `--run`. The full old -> new map of the 36 is in the commands block, for any later rerun of a script that prints its own blob.
- **C-2 (MEDIUM)**: before merge, with no java.exe live: `.\gradlew.bat test --offline` in the worktree (two known worktree failures allowed), then `.\gradlew.bat --stop`. Confirm afterwards that E:/TaxoArena_tmp/gradle/<worktree>_<hash> is gone (finalizer) and that no new ranking-service-test* / emb_explicit* / intent_emb_run* dirs appeared in C: temp (count before and after).
- **D-2 (LOW)**: E:/TaxoArena_tmp already holds other agents' hand-made files (ckd_*.py/txt, ckdmut_*, ckdst_*). `--purge-stale --days 1` deletes those after a day. Say so in the docstring, or exempt non-py_/run_ entries unless `--all` is given.
- **D-3 (LOW)**: selftest gaps OM1/OM3. Add a non-mp child that inherits the env and must get its own dir, and a junction fixture inside a purged dir with its target asserted intact. The broad legacy prefixes (`canary`, `k46`) can match foreign dirs; the dry run today matched only 2 intent_emb_run* dirs.

## Merge instructions
Once D-1 is fixed and delta-READY'd and C-1/C-2 are done, on main: `git merge --no-ff scratch-dir-e`. The trial merge has no
conflicts (main's build.gradle.kts = base). Commit by paths only. Never stage application.yml/.env/.gitignore.

## Commands (compact)
```
git diff abde9a22 26378771 -- <36> | (pairs check: code_b == code_a + '; import scratch_dir')  -> 39/39, 0 non-conforming
pins2/pins3.py: git grep -i -o -e <blob8|cblob8|sha8|csha8 x36> main -- tools src experiment_configs config build.gradle.kts  -> 2 hits (docstring, CSV)
  READY-only review pins: cert_redraw_r512 dataset_survey flat_generality gemma_own_bar jv2_rate_probe_selftest mix_lrt_site results_index
  rp12_build_configs supergpqa_stage0 topic_partition topic_partition_t1b_null transport_check union_af_route_ops (+agent_admission_pilot via results JSON)
par.py: git archive <rev> -- . ':!experiment_results' -> scratchpad/pb|pe; run --selftest/--mutants both sides; TAXOARENA_TMP=E:/TaxoArena_tmp/rv_review_sde (removed after)
safe.py: mklink /J fixtures; purge_stale(root=private); cleanup(); rmtree_robust(junction) -> OUTSIDE intact x3
python -c "...s.DEFAULT_BASE='Q:/TaxoArena_tmp'; s._BASE=None; s.purge_stale(dry_run=True)" -> under C:\...\Temp: removed 6313 (DRY-RUN)
git diff abde9a22 main -- build.gradle.kts | wc -l -> 0;  git merge-tree --write-tree main 26378771 -> dd8daa69 rc 0
scratch_dir.py --run -- python tools/analysis/tie_mechanics.py --selftest -> rc 0; before 17, after 17
old>new blobs: agent_admission_pilot 26caff21>4d56b4de; card_protocol_writer 2788d721>9c3e7084; cert_direction_stream a4be06c3>00557e5d;
 cert_pc_k2_known 15717e13>981097af; cert_redraw_r512 2c0982e9>0b3f05a8; dataset_survey d83f3824>df460e6c; e1_configs_check 92d22a43>070bd3fb;
 e1_split_draws 3318a16a>0414b8fa; embed_quant_writer 1b2abdc8>5654f753; escalation_rc a17f6821>8f99db7d; fitset_intent eaa29686>3359d815;
 flat_generality 0acfb540>d16f1042; flat_v2 ef7bca33>bbf1d506; g11_reader b86832e3>87ec8d40; g12_reader 1c8bf8bc>8a15dc2f;
 gemma_own_bar 3d92c811>d30be8ce; gold_level_emb 86765764>d21dc13d; h9_stability 0814869f>2a020d7b; intent_s0_slotswap_mech 78218155>fcbee659;
 judge_solved_split c1f36f79>16f35f8b; jv2_rate_probe_selftest 7c6fd9c9>765bfe7e; lcb_power_resim 8622ff95>efd4e0be; mix_lrt_site fbb480ca>e2d28a73;
 model_vintage_canary ee5215b9>a27766ee; online_stage2 6bbc40dd>eabf5f2b; oos_tree_cells 74a5cbf0>caaced4a; recipe_edge_audit 09369edb>292bf460;
 results_index 661a0eb6>20f2196b; router_clean_policy 2a726529>17f35f3b; rp12_build_configs d87c9337>fe0ffecc; split_exposure_sensitivity 145749ac>92f2dd12;
 supergpqa_stage0 35b11858>61741d7f; topic_partition 8721da09>9b893aed; topic_partition_t1b_null 956c6d02>30ec08e5; transport_check b9cb63eb>73915255;
 union_af_route_ops 5a020d29>157b4f6f
```
