# READY review: rp08-embedder-plumbing (EMBEDDER-PLUMBING, plan RP08, EMB-01 a-c, D02) at 5172047 — 2026-09-27

## VERDICT: NOT READY (at 5172047). NOT MERGEABLE yet. After F1-F4 and the registrar's rulings a delta-READY is enough

Registration: docs/judge_v2_program.md L21754-L21772 (section "## Registered 2026-09-27 (before any code or call) — EMBEDDER-PLUMBING", registered at a357ef0).

What is wrong:
- **B1 (BLOCKER, a registrar item): A1 is unruled.** Item (d) says a reader REFUSES when neither the manifest nor -DembeddingModel names the model. The harness cannot reach a manifest: `run_manifest.json` has 43 keys and no snapshot id (the reviewer listed them for af_bareq512); the only link is headless_run.log. So as built, with no flag at all, the site null reads the DB of record and takes the canonical model as a DEFAULT (`resolveModel(null, ...)`, EmbedderReadGuard.kt L108-L123). That departs from (d)'s words. It is safe only because (c) catches a nomic tree run with no flags: its vmfMu is in nomic space, so the qwen3 vectors do not align with it. Only the registrar can accept this; the builder asked for the ruling. A2 (six arms refuse the flags where (a) says "the seven harness sites read it") and A3 (the discriminator counts 9 classes, not 1) also need recording.
- **H1 (HIGH): the multi-site gate is untested in both twins.** The registered guard takes "for every checked site ... the minimum cosine". Every synthetic tree has ONE split site: Python `synthetic()` gives the root only, and EmbedderReadGuardTest `tree()` returns `listOf(root)` (1 hit by grep). Four reviewer mutants SURVIVE the full embedder_guard selftest:
  - X1: the minimum becomes the maximum.
  - X2: only the first split site is checked.
  - X6: a tree with no split site is admitted, which is the vacuity class.
  - X8 (flat_mix_mmlu, full selftest): every site uses the root's region.

  The Kotlin twins of X1 and X2 (`minByOrNull` -> `maxByOrNull`; `sites.take(1)`) survive by construction, since there is one site. The proof legs of record cannot catch X1 or X2 either. In P-2 (ii) every site reads a wrong vector, so the max is low too. The min guard's job is the PARTLY-wrong read (a mixed or partially overwritten cache), and only a selftest can witness that.
- **M1 (MEDIUM): the P-2 (vi) command line is written two ways.**
  - embedder_guard.py docstring L34-L36 runs it with `--embedding-model nomic-embed-text:latest`. af_clean_s42's manifest names `qwen3-embedding:latest`, so that command refuses on the CONTRADICTION branch (`resolve_model`) before any cosine is read. No `[EMB-GUARD] vmfMu cosine ... budget 0.99` line is printed, which breaks the rule-11 line that (c) requires.
  - flat_mix_mmlu.py's bracket and the builder's report give the correct command: no model flag.
- **M2 (MEDIUM): the right-embedder margin is UNDETERMINED, and it decides C1.**
  - The guard compares the UNWEIGHTED mean over `regionQueryIds`, keyed by id.
  - The fitter's vmfMu is the WEIGHTED mean over `getRegionQueryWeights`, keyed by text (TaxonomyFitter.kt L204-L251). It is also held at the old value whenever the fresh fit is within 1 - cos <= 0.0025 of it (the early-out, L262-L266).
  - The registration's scratch readings (1.0000 / 0.9997 / 0.9984) are a sample of sites, not the minimum over 87 (af_bareq512) or 69 (af_clean_s42).
  - If any right-embedder site reads < 0.99, P-1 produces no CSV, C1 FAILS and F1 says "no merge". Nothing pre-states how that case is scored. The reviewer computed no real-data cosine: that number IS the P-2 (i) statistic.
- **M3 (MEDIUM): two wiring points execute in no test.**
  - `fit_set` reading the configured cache: reviewer mutant X10 survives. `--dry-run` with the flags reaches it, and FLAT-GENERALITY will depend on it.
  - The guard call inside the siteNull arm: SeparationNullBySizeTest is excluded from `test` (build.gradle.kts), and no other test calls the arm. `grep siteNull` outside the harness gives 1 hit, a message string. P-2 (i) and (ii) and the P-1 discriminator's printed line cover this on real data later.

What is confirmed (details in the table below):
- The object: the branch is clean, 8 files changed, and it is an ancestor-descendant of 7676eab.
- Pins: 8 of 8 match the builder's blob / lf16 / crlf16.
- Every `File("embeddings_cache.db")` in the harness is gone: 7 before, 0 after.
- The builder's runs reproduce:
  - embedder_guard: selftest 29, mutants 16/16 killed, dry-run 1.0000 / -0.0154 with dims {768: 120}.
  - flat_mix_mmlu: selftest 88; the 75 old checks are identical to the reviewer's own run of main's c5cc7934; mutants 35/35 killed.
- The DB of record holds ONLY 4096-d vectors (39,631), so P-1 cannot refuse on the dimension check. This closes the builder's open item.
- P-2 (ii) is reachable: all 8,133 af_bareq512 ids resolve in the nomic DB (scratch copy), so a cosine is computed on all 87 sites.

Reviewer: adversarial-reviewer.
- Zero judge or Azure calls, no site null, no construction, no Ollama, no Gradle run by the reviewer (machine cap: THREAD-CAP is not proved).
- Python ran single-threaded (OMP / MKL / OPENBLAS = 1).
- Real-data reads were count and schema only, no statistic of any registered test:
  - embeddings_cache.db opened `mode=ro&immutable=1` (its -wal is 0 B): `SELECT id FROM queries` and `SELECT length(vector)/4, count(*) FROM embeddings GROUP BY 1`.
  - snapshots.db opened `mode=ro&immutable=1` (-wal 0 B): the graphs of 20260917_161817 (af_bareq512) and 20260917_201353 (af_clean_s42), for the site count, the vmfMu lengths and the id sets.
  - The nomic DB was read ONLY as a scratch copy, together with its -wal. The original's sha256 was the same before and after the copy (`sha256sum ... | diff`), and the original was never opened.
- Main's DB mtimes are unchanged: embeddings_cache.db 2026-09-23 14:33, snapshots.db 2026-09-23 04:34.
- Scratch: `scratchpad/rp08rev/` (rev_mutants.py, rev_mutants.log, eg_*.log, flat_*.log).

## Object
- Worktree `.claude/worktrees/w0-rp08-embedder-plumbing`, branch `w0-rp08-embedder-plumbing`, tip 517204771f85, parent 7676eab. `git merge-base --is-ancestor 7676eab 5172047` passes.
- `git status --short | wc -l` = 0 before and after every reviewer leg.
- `git diff --name-only 7676eab 5172047 | wc -l` = 8. That diff has 0 paths matching supergpqa, application.yml, .env, .gitignore or report/ (`grep -ci`).
- Main is now at 1adce88. `git diff 7676eab 1adce88 --name-only` has 0 hits on the 8 paths.
- Merge conflicts (`git merge-tree --write-tree`, exit 1 on both):
  - with w0-rp07-thread-cap: CONFLICT in build.gradle.kts (the siteNull forward block); SeparationNullBySizeTest.kt auto-merges.
  - with w0-rp05-flat-generality: CONFLICT in tools/analysis/flat_mix_mmlu.py. flat_generality.py on rp05 pins c5cc7934 in 4 places, so it fails closed until it is re-pinned.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | tip 5172047, parent 7676eab, clean tree, only these files | CONFIRMED | `git log -2`; `git status --short \| wc -l` = 0; `git diff --name-only \| wc -l` = 8 | 8 = 8 | - |
| 2 | 8 pins (blob / lf16 / crlf16) | CONFIRMED | python over `git cat-file -p HEAD:<f>` (LF) plus a CRLF re-rendering | 8/8 exact. BUT "the working tree is CRLF" holds for 4 of 8 files; the 4 new files are LF in the working tree | LOW (L2) |
| 3 | 7 hard-coded cache paths replaced | CONFIRMED | `grep -c 'File("embeddings_cache.db")'`: 7 at 7676eab, 0 at tip; `unguardedEmbDb(`: 7 lines = definition + 6 calls | 7 -> 0 | - |
| 4 | the six unguarded arms refuse either flag | CONFIRMED (code + unit test) | SeparationNullBySizeTest.kt L1326-L1335; EmbedderReadGuardTest L214-L229 (reflection) | - | registrar A2 |
| 5 | siteNull: resolve, print [EMB-CACHE], run guard before heap guard and any replicate | CONFIRMED by inspection; NOT EXECUTED by any test | diff hunk at L1687-L1724; SeparationNullBySizeTest excluded from `test` (build.gradle.kts) | - | MEDIUM (M3) |
| 6 | "[EMB-GUARD] not run" on both skip paths | CONFIRMED (code) | L1693, L1697 (sit before each Assumption) | - | - |
| 7 | (b) only "", "qwen3-embedding", "qwen3-embedding:latest" route to the DB of record; non-qwen3 names unchanged | CONFIRMED | EmbeddingCache.kt companion; EmbeddingCacheRoutingTest XML 3/3 pass; no qwen3 variant tag anywhere in config/ or experiment_configs/ (grep) | inert on every configured path | LOW (L3: two tags against "the exact canonical tag"; L4: the `dbFile` wiring is not tested, only the companion) |
| 8 | (c) every accepted split site, unweighted mean, budget 0.99 | PARTLY | code correct; X1/X2/X6/X8 survive (below) | the multi-site gate is untested | HIGH (H1) |
| 9 | dimension check: native dim, unknown model, mixed lengths, vmfMu width | CONFIRMED | selftest EG-DIM; builder mutants killed; DB of record `length(vector)/4` = {4096: 39631} | P-1 cannot refuse on dims | - |
| 10 | embedder_guard selftest 29 / mutants 16 of 16 / dry-run | CONFIRMED | re-run: `--selftest` rc 0 "29 checks"; `--mutants` "16 of 16 KILLED"; `--dry-run` min 1.0000 ADMIT / min -0.0154 REFUSE, dims {768: 120} != {4096} | exact | - |
| 11 | flat selftest 88, 75 old checks line-for-line equal to main | CONFIRMED | re-run at tip: 88; main's c5cc7934 run by the reviewer (`TAXOARENA_DATA_ROOT`=scratch): 75; `diff` of the 75 `ok` lines = empty | exact | - |
| 12 | flat mutants 35 of 35 | CONFIRMED | re-run: "MUTANTS: 35 of 35 KILLED" | exact | - |
| 13 | 13 new Kotlin tests pass | CONFIRMED from artefact (not re-run: machine cap) | build/test-results XML: EmbedderReadGuardTest tests=10 f=0 e=0 s=0; EmbeddingCacheRoutingTest tests=3 f=0 e=0 s=0 | 13/13 | - |
| 14 | full suite 464 / 2 allowed failures | PARTLY (log only; the XML dir was overwritten by the targeted run) | gradle_test_full.log: the two failures are MrlRoutingTest.testMrlConfigDefaults and TraceEnvelopeUnwrap blank-trace; `@Test` count 482 -> 495 (+13, `git grep -c`) | consistent | LOW (L5: that run executed `processTestAot`, the uncapped JavaExec fork of RP07 H1, before THREAD-CAP was proved) |
| 15 | discriminator: 9 EmbedderReadGuard*.class files; the harness class references the guard; 0 on main | CONFIRMED | `ls \| grep ^EmbedderReadGuard \| grep -vc Test` = 9; `grep -c EmbedderReadGuard SeparationNullBySizeTest.class` = 10; `git grep EmbedderReadGuard 7676eab -- src` = 0 files | 9 / present / 0 | registrar A3 |
| 16 | flags forwarded only when set (JVM properties unchanged when absent) | CONFIRMED | build.gradle.kts diff: two `?.let` lines | - | - |
| 17 | FLAT: --run / --analyze refuse the flags | CONFIRMED | FT-EMBGUARD checks; builder mutant "embedding flags admitted with --run" killed | - | - |
| 18 | FLAT default path is inert (no flags) | CONFIRMED with qualification | af_clean_s42 manifest embedding_model = qwen3-embedding:latest (read); a guard now runs in `header()` on every mode. Reads and prints only, but it is a NEW REFUSAL PATH on the recorded instrument (M2) | - | MEDIUM (M2) |
| 19 | P-2 (vi) command line | REFUTED in one of two places | embedder_guard.py L34-L36 carries `--embedding-model nomic-embed-text:latest`, which gives a contradiction refusal with no cosine | - | MEDIUM (M1) |
| 20 | "Not checked: non-4096 vectors in the DB of record" | CHECKED by the reviewer | immutable read, `GROUP BY length(vector)/4` -> [(4096, 39631)] | none | - |
| 21 | registration support: C1 87 sites | CONFIRMED | snapshots.db graph 20260917_161817: 179 nodes, 87 split sites, vmfMu lengths {512}, 8,133 ids | 87 = 87 | - |
| 22 | P-2 (ii) reachable (cosines computed, not NaN) | CONFIRMED | nomic DB scratch copy: 8,299 queries, all joinable, 11,769 vectors all 768-d; af_bareq512 ids in it: 8,133 / 8,133 | reachable | - |
| 23 | P-2 (vi) reachable | CONFIRMED | af_clean_s42 (20260917_201353): 69 sites, vmfMu {256}, 8,125 ids, 5,706 in the nomic DB; the refusal fires on dims {768} != {4096} and on the cosine over partial coverage | reachable | LOW (L6: partial coverage is admitted silently when the vectors are right-dimensioned; the admit path prints found/n only for the 3 worst sites) |
| 24 | no DB of record opened or written by the builder | CONSISTENT | main mtimes above; the worktree's *.db files are 4-77 KB test artefacts from 06:09 | - | - |

## Reviewer mutants (scratchpad/rp08rev/rev_mutants.py; each mutant runs the FULL selftest, `only=None`)

| id | file | mutation | result |
|---|---|---|---|
| X1 | embedder_guard.py | `worst = min(...)` -> `max(...)` | **SURVIVED** |
| X2 | embedder_guard.py | `split_sites(...)` -> `[:1]` (first site only) | **SURVIVED** |
| X3 | embedder_guard.py | site mean from one member vector | KILLED (min cos 0.6572) |
| X4 | embedder_guard.py | model contradiction compared by prefix before ':' | SURVIVED (no impact: an unknown variant then fails the NATIVE_DIM lookup) |
| X5 | embedder_guard.py | a site admitted with 1 of n vectors | KILLED |
| X6 | embedder_guard.py | `if not sites:` check removed (zero-site tree admitted) | **SURVIVED** |
| X7 | embedder_guard.py | the undefined-cosine check removed | SURVIVED (largely equivalent: the no-vmfMu and no-vector reasons still fire) |
| X8 | flat_mix_mmlu.py | guard region = the root region for every site | **SURVIVED** |
| X9 | flat_mix_mmlu.py | guard opens the DB of record, not the configured cache | KILLED, but for the WRONG reason (the worktree's test-artefact embeddings_cache.db-wal is non-empty) |
| X10 | flat_mix_mmlu.py | `fit_set` opens the DB of record | **SURVIVED** |
| X11 | flat_mix_mmlu.py | `EMB_CACHE_SET` never set | SURVIVED (inert today: the FLAT T always has a manifest) |
| X1-K / X2-K | EmbedderReadGuard.kt | `minByOrNull` -> `maxByOrNull`; `sites.take(1)` | SURVIVE by construction (every test tree is `listOf(root)`); not executed (no Gradle run by the reviewer) |
| X8-K | SeparationNullBySizeTest.kt | delete the `EmbedderReadGuard.run` block in siteNull | SURVIVES the unit suite (the harness is excluded from `test`); caught only by P-2 (ii) / the P-1 printed line |

## Defects and fixes
- **B1** Registrar rules A1 (no flag -> DB of record + canonical model, with the protection resting on (c)), A2 (six arms refuse the flags), A3 (discriminator = 9 guard classes plus the printed line), and L3 (two canonical tags).
- **F1 (H1)** Add a two-site synthetic tree to BOTH twins:
  - one site with a wrong vmfMu (or a member set drawn from a second cluster). The guard must REFUSE, print that site's cosine as the minimum, and name it.
  - a zero-split-site tree, which must REFUSE "no site to check".

  X1, X2, X6 and X8, and their Kotlin twins, must be KILLED; add them to MUTANTS.
- **F2 (M1)** Fix the embedder_guard.py docstring: the (vi) refusal leg takes NO `--embedding-model`. Optionally, compute and print the cosine before a contradiction refusal as well.
- **F3 (M3)** Add a selftest that `fit_set` opens the configured cache (X10 killed).
- **F4 (M2)** Before the window, the registrar pre-states the score when the RIGHT embedder is refused: C2 (i) FAILED and C1 FAILED, F1 fires, and the budget or the weighting is changed only by a new registration. P-2 (i) runs FIRST in the window (below).
- LOW, fix at will:
  - L1: the Kotlin and Python printed dims differ, `{4096=120}` against `{4096: 120}`, although the docstring claims identical lines.
  - L4: test that `EmbeddingCache.dbFile` uses `cacheFileFor`.
  - L6: print found/n for every site on ADMIT.

## Merge and run procedure (after F1-F4 and a delta-READY)
1. Merge ORDER: RP07 THREAD-CAP first, once READY and proved. Resolve the build.gradle.kts siteNull hunk by keeping BOTH sets of property forwards. Then merge rp08 by explicit path with `git merge-base --is-ancestor` checked. Re-run on the merged tree: embedder_guard `--selftest` / `--mutants`, flat_mix_mmlu `--selftest` / `--mutants`, and the targeted Kotlin tests (EmbedderReadGuardTest, EmbeddingCacheRoutingTest). rp05 re-pins flat_mix_mmlu.py and wires `FM.configure_embedding` / `FM.embedding_guard_flat(graph=..., manifest_path=...)` per tree.
2. The window (a W-window, after THREAD-CAP is proved):
   - Beforehand: a backup, and no construction running.
   - The steward's WAL checkpoint of `embeddings_cache_nomic-embed-text_latest.db` (-wal 4,647,392 B) and the gemma DB, with the sha before and after recorded (RP02).
   - Record the sha and mtime of every DB before and after each leg.
3. The legs, in this order:
   1. P-2 (i): siteNull on af_bareq512_s42 with GUARD-22-RENAME-PROOF's recorded command line plus `-PjvmThreads=12`, no new flag. Expect `[EMB-GUARD] ... min >= 0.99 ... ADMIT` over 87 sites.
   2. P-2 (ii): the same command plus `-DembeddingCacheFile=<absolute nomic DB> -DembeddingModel=qwen3-embedding:latest`. Expect a REFUSE before any replicate, with every site's cosine printed (P3: all < 0.2).
   3. P-1: the P-2 (i) run's CSV is compared with sha256 aec4b517...a665 (`cmp`). The discriminator is 9 guard classes and the `[EMB-GUARD]` line in that run's stdout.
   4. P-2 (vi): `flat_mix_mmlu.py --dry-run --embedding-cache-file <nomic DB>` with NO `--embedding-model`: REFUSE, cosine printed. Then `flat_mix_mmlu.py --dry-run` with no flags: ADMIT.
4. SuperGPQA: not touched by this build (0 paths); no seal is involved.
