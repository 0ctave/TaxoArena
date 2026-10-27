# READY review: branch emb-target (8459398 EMB-TARGET-DIR, c7c2c63 RP06 N6-1)

Adversarial reviewer, 2026-09-29. Zero calls, no real embed, no Ollama contacted (stub Ollama on 127.0.0.1 only), nothing
written outside temp dirs and the scratchpad. Worktree `.claude/worktrees/emb-target`, tip c7c2c63 on main 1ba9a04
(main has since moved to 7eb4714: 11 files changed, 0 of them embedder_arms / cert_redraw_r512 / flat_mix_mmlu /
embedder_guard / pool_guard; a by-path merge is conflict-free on the reviewed files).

## VERDICT

| commit | MERGEABLE | READY for |
|---|---|---|
| 8459398 EMB-TARGET-DIR (embedder_arms --target-dir) | MERGEABLE | READY-WITH-CONDITIONS for `--embed-missing gemma_raw --expect-missing 3504 --target-dir experiment_results/embedder_cross --go` (C-ET-1, C-ET-2) and for `--embed-card gemma_card / nomic_card --target-dir experiment_results/embedder_cross --go` (C-ET-1, C-ET-2). NOT READY for any E0b / E1 READ (C-ET-3, C-ET-4, C-ET-5). |
| c7c2c63 RP06 N6-1 (cert_redraw_r512 VOID refuses) | MERGEABLE | READY (the delta READY that ruling N6-1 owes before any re-run of cert_redraw_r512) |

Conditions carried unchanged from READY_w0_delta3 (3da93fc) for the gemma --go: C8-4 LOW, Y8-H LOW (not re-derived).

## PINS (LF of record; working tree is CRLF)

- tools/analysis/embedder_arms.py: blob:05214b039165153a261dfd9f9083723d2cfe0361 / sha256-lf16:7ac7592c93c6c140 /
  sha256-crlf16:a997b4839cdd3143 (`git hash-object` = `git rev-parse c7c2c63:...`; = the commit message's pins).
- tools/analysis/cert_redraw_r512.py: blob:2c0982e9ee6864938986c17333bcd783c00c4c3a / sha256-lf16:b5c50d5622286c55 /
  sha256-crlf16:c73e143b333772f1 (= the commit message's pins).
- `git diff --name-only 1ba9a04..c7c2c63 | wc -l` = 2 (the two .py files; no Kotlin, no yml/.env/.gitignore). Kotlin
  untouched, so `gradlew test` was not re-run (the builder's 470 / 2 allowed failures stands as reported, not re-derived).

## PER-CLAIM TABLE (deciding claims only)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | The source is never written (raw and card) | Source opened only via pool_guard.open_ro (immutable=1), `_sha` and copyfile's read; writes go to `staged[1]`. Selftest EA-TARGET asserts source sha + 25 rows unchanged. My WAL-mode fixture (the real gemma DB is WAL: header bytes 18/19 = 2/2): source sha unchanged, root holds only the source (no -wal/-shm), DIR holds only copy + provenance, provenance sha256_after == file. Real caches: size/mtime/sha256 (gemma 3e9ce577..., nomic 53d1540a...) identical before/after all my runs. | CONFIRMED | - |
| 2 | Selftest 74 checks, mutants 51/51 killed | 74 ok, rc 0; 51 KILLED / 0 SURVIVED (counted by grep -c) | CONFIRMED | - |
| 3 | Absent-flag inertness, with an execution discriminator | `--inertness` rc 0: 20 records, 4 file shas, 7 stub requests identical; leg A new-code calls {}; leg B check_target_flag 11, run_embed 10, resolve_target 10, target_dir None each. Discriminator is real (wrappers installed in the exec'd namespace the code resolves through). Non-vacuity by my own mutants R3 (None-path drops one missing text: NOT INERT, records/files/requests all differ) and R4 (None-path configure_arm model=None: NOT INERT, records differ). Scope limit: the proof covers stubbed pool guard / needed_texts; the real DATA_ROOT read path is unchanged code. | CONFIRMED | - |
| 4 | "EMBEDDER-CROSS-FLAT's reader on the copy and only it" | The check exists (configure_arm_copy + pin_copy_connect; EA-TREADER under the real flat_mix connect guard; my R7, pin on the source path, KILLED). BUT no EMBEDDER-CROSS-FLAT reader exists: `git grep -l "configure_arm\|embedder_arms" c7c2c63 -- *.py *.kt *.kts *.sh` = 1 file (embedder_arms.py itself); results/EMBEDDER-CROSS-FLAT.json script = "NOT BUILT". The only built non-qwen3 read paths bypass the provenance check: flat_mix_mmlu `--dry-run/--identity-check --embedding-cache-file <any path>` (configure_embedding admits the basename, no provenance, no path pin) and the Kotlin siteNull `-DembeddingCacheFile`. bootRun (E1 construction) forwards no cache-file property at all (`git grep -c 'systemProperty("embeddingCacheFile"' build.gradle.kts` = 1, the siteNull task): an E1 N-card build cannot read a DIR card file. | PARTLY (enforced in a library function no read path calls) | HIGH for E0b/E1; none for the writer |
| 5 | Provenance = the ruling-19 pin | configure_arm_copy checks the file against the WRITER's own sha256_after; ruling 19 requires a REGISTRAR bracket pin and a read that refuses on mismatch (PINS OWED). Self-certification, not the pin. | PARTLY | MEDIUM |
| 6 | "Existing copy overwritten" caught only after the overwrite | The code refuses an existing copy/provenance BEFORE any post or copy (target_paths, via resolve_target at the top of embed_missing / embed_card). What the builder admits is a test-ordering fact: with the check off, the copy is overwritten and the kill comes from provenance mode x (my R1, with mode x also off: KILLED by the second-run assertion, again post hoc). The real gap is a race: my scenario plants a file at DIR/<basename> during route parity (after the check, before stage_copy): the run returns 2, the planted file is silently overwritten, provenance written. On the card path, write_vectors would INSERT into a planted file and the reader would then admit it (sha256_after self-consistent). | REFUTED as "only after"; race CONFIRMED | MEDIUM |
| 7 | --expect-missing 3504 | Not recomputed (a zero-call dry run is the operator's step and a pool reader under rule 7). The tool is count-checked fail-closed: `--expect-missing 5` on 2 missing REFUSES with DIR empty and 0 posts (EA-TARGET). The 3,504 is the data-steward's bracket (prog L21837, L21901) and the 532dd1d dry run. | UNDETERMINED by me; guarded by the tool | - |
| 8 | c7c2c63: a VOID s42 leg REFUSES before any output | Selftest 11 checks 0 failed; mutants 20 run / 20 killed (ic_void_soft KILLED by st5c, st6). run(): VOID refusal at the line before render and `os.makedirs`. Own: CR-M2 (refusal only after makedirs, render's refusal off) KILLED by st5c (out dir created); CR-M1 (run()'s raise dropped, log line kept) SURVIVED: EQUIVALENT (render raises before makedirs; same log, same refusal, no path). crL_P1_ge_not_eq "SURVIVED (not reachable here)" is pre-existing upstream, unchanged. | CONFIRMED | - |

## OWN MUTANTS (7)

- R1 target_paths lexists off + provenance mode "w" -> KILLED (EA-TARGET second run: "copy unchanged" assertion, post hoc). decisive for claim 6.
- R6 stage_copy's source-after-copy sha replaced by the before sha -> SURVIVED; not decisive (write_provenance re-hashes the source after the write).
- R7 reader path pin installed on the SOURCE path -> KILLED (EA-TREADER). decisive for claim 4 (function level).
- R3 None-path embed_missing drops one missing text -> NOT INERT. decisive for claim 3.
- R4 None-path configure_arm model=None -> NOT INERT. decisive for claim 3.
- CR-M1 run() VOID raise dropped -> SURVIVED, equivalent (render refuses first). not decisive.
- CR-M2 VOID refusal after os.makedirs, render refusal off -> KILLED (st5c). decisive for claim 8.

## DEFECTS / CONDITIONS

- C-ET-1 (MEDIUM; before the --go runs, or the operator's written acceptance of the race): close the check-to-copy race.
  Fix: in stage_copy create the copy exclusively (`with open(source,"rb") as s, open(copy,"xb") as d: shutil.copyfileobj(s,d)`),
  and on the card path create the NEW file with `open(path,"xb").close()` right after resolve_target's check under --go
  (or refuse in write_vectors when `existed` under --target-dir); add a selftest that plants the file during parity and
  asserts REFUSED with the planted bytes intact and 0 further posts. Operator workaround if not fixed: one pre-embedder
  process at a time, DIR listed before and after (copy absent before; exactly copy + provenance after).
- C-ET-2 (LOW; record hygiene): `git check-ignore -v` shows `<basename>.db.provenance.json` IGNORED by .gitignore:124
  `*.db.*`, while the copy `.db` is UN-ignored by .gitignore:145 `!experiment_results/**/*.db` (a 38 MB+ untracked DB a
  broad `git add` would sweep). The provenance is not a committed record: the registrar must bracket source sha256,
  sha256_after and vectors_written from the run's printed lines (ruling 19); never commit the .db. .gitignore is
  author-owned: no change proposed here.
- C-ET-3 (HIGH; before any E0b-EMBED read): the E0b reader must be built to configure every non-qwen3 arm through
  `embedder_arms.configure_arm(FM, arm, DATA_ROOT, target_dir=DIR)` and must refuse flat_mix's `--embedding-cache-file`
  path for these arms; its READY must show, by execution, that a read of the DIR copy without the provenance check
  (flat_mix `--embedding-cache-file experiment_results/embedder_cross/<basename>`) is refused or unreachable.
- C-ET-4 (MEDIUM; ruling 19, PINS OWED): the E0b reader must also compare the copy's sha256 with the REGISTRAR's bracket
  pin (not only the writer's provenance) and refuse on mismatch.
- C-ET-5 (HIGH for E1 N-card only): no JVM read path for a DIR card file (bootRun forwards no cache-file property;
  EmbeddingCache.cacheFileFor names repo-root files by tag). E1 N-raw (nomic, root file, no embed) is unaffected by this
  branch; E1 N-card through a --target-dir file needs a registered plumbing change and its own inertness proof.
- NOTE: the selftests' raw source is created in rollback mode; the real gemma source is WAL. My WAL fixture (claim 1)
  covers it; a WAL-mode source in EA-TARGET would make that a standing check (LOW, optional).

## COMMANDS (compact)

```
cd .claude/worktrees/emb-target; export TAXOARENA_DATA_ROOT=<scratch>/nodata
python tools/analysis/embedder_arms.py --selftest     # SELFTEST PASSED: 74 checks, rc 0
python tools/analysis/embedder_arms.py --inertness    # INERT ... leg B executed the new code, rc 0
python tools/analysis/embedder_arms.py --mutants      # MUTANTS: 51 of 51 KILLED; grep -c SURVIVED = 0
python tools/analysis/cert_redraw_r512.py --selftest  # SELFTEST: 11 checks, 0 failed; MUTANTS: 20 run, 20 killed
python <scratch>/own_mut.py R1|R6|R7|R3|R4            # exec'd mutants of embedder_arms (selftest subsets / inertness())
python <scratch>/cr_mut.py                            # CR-M0 control, CR-M1, CR-M2 via run_selftest on exec'd source
python <scratch>/race.py      # "RACE: run returned 2 | planted file survived: False | provenance exists: True"
python <scratch>/walsrc.py    # WAL source: DIR = copy + provenance only; root = source only; source unchanged; 27 rows
git hash-object tools/analysis/{embedder_arms,cert_redraw_r512}.py; git show c7c2c63:<f> | sha256sum (| sed 's/$/\r/' for crlf16)
git grep -l "configure_arm\|embedder_arms" c7c2c63 -- '*.py' '*.kt' '*.kts' '*.sh' | wc -l   # 1
git grep -c 'systemProperty("embeddingCacheFile"' c7c2c63 -- build.gradle.kts               # 1 (siteNull)
git diff --name-only 1ba9a04..main | grep -c -E "embedder_arms|cert_redraw_r512|flat_mix_mmlu|embedder_guard|pool_guard"  # 0
stat/sha256sum of the three repo-root caches before and after: diff empty (UNCHANGED)
git check-ignore -v experiment_results/embedder_cross/<basename>.db{,.provenance.json}
```
