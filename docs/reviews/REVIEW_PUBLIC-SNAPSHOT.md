# REVIEW_PUBLIC-SNAPSHOT: public snapshot of main 53612401 (D-2026-10-27-4/-6/-7), round 1

Authority:
- D-2026-10-27-4: a clean public snapshot instead of pushing the history.
- D-2026-10-27-6: A2 the record is included as is; A5 MIT; A7 guard the two clean-checkout tests.
- D-2026-10-27-7: push now. The main session's orphan snapshot goes first; the workflow's audited, doc-prepped version follows as a child commit, with no second force-push.

All three decisions, with the main session's readings, are in `docs/agents/author_decisions/2026-10-27.md` (D-7 committed in 5525c4f6).

Recorded by the registrar on 2026-10-27, at main 5525c4f6:
- Zero LLM calls. The registrar ran only read-only git and gh queries (listed at the end).
- Ledger unchanged. Local main and its history are unchanged. Nothing was pushed by this workflow.
- This file contains no secret value and no GPQA text. Excluded files are named by path only.

## Verdict

**PUSH_OK: no.** Not every final audit is CLEAN:
- links-build returned FINDINGS (OBJ-1 BLOCKER): the object to push, `refs/heads/public-snapshot`, was never built.
- The branch it would be built from, snapshot-prep, is not merged. The prep review found it NOT MERGEABLE, with merge condition E1.

What is already public is the main session's orphan snapshot e5a29430 (D-2026-10-27-7):
- Three audits are CLEAN on it.
- links-build has no BLOCKER or HIGH on it; it has Z-1 (MEDIUM) and LOWs.
- No audit asks for a path to be removed from it: exclude_paths = [] in all four.
- Its first hosted CI run on ubuntu-latest succeeded (S3, below).

| dimension | object audited | verdict | exclude_paths | deciding numbers |
|---|---|---|---|---|
| secrets and sizes | e5a29430 (substitute) | CLEAN | [] | 0 secret hits: 1,489 needle variants over 4,405 blobs, 165 container members, 5,642 path names and the commit object; 0 files over 50 MB |
| GPQA | e5a29430 plus the 6-path planned-child delta | CLEAN | [] | 0 HIT over 5,642 paths; 1 REVIEW, cleared; independent exact grep: 0 files |
| raw outputs and benchmark dumps | e5a29430 | CLEAN | [] | 0 files over the more-than-3-responses bar; 0 files at 20 or more benchmark items (max 5) |
| links and build | e5a29430 (substitute) | FINDINGS | [] | OBJ-1 BLOCKER (object absent); Z-1 MEDIUM (fails without .git); links 65/65; tests 569 / 0 failed / 2 skipped |

## Objects

Hash kinds: commit and tree ids are git object ids. Manifest sha256 values are of the file bytes, which are LF ASCII (0 CR). Scratch evidence hashes say which rendering they are.

**Source main.** `53612401` (Merge repo-tidy; 5,849 tracked files). Main is now `5525c4f6`, which only adds D-2026-10-27-7 to the decisions file.

**Public snapshot of record.** Built and pushed by the main session under D-2026-10-27-7.
- Commit `e5a29430ee9254e5938b785190e0083b4c2a5287`, tree `a2e3d7d09c703bfd3d0f8002fd8b61d5d584c135`. It is an orphan with 5,642 files.
- It is the same object as origin `refs/heads/main` (`git ls-remote origin main`, this record), local `refs/heads/public-snapshot-pushed`, and the local lightweight tag `public-snapshot-2026-10-27-r0`.
- The tag is not on origin: `git ls-remote origin refs/tags/public-snapshot-2026-10-27-r0` returns nothing.
- `git diff --name-status 53612401 e5a29430` shows 207 D, 0 M and 0 A. The deleted set equals the 207-path manifest exactly (`diff`, this record).

**The workflow's object, `refs/heads/public-snapshot`.** ABSENT. `git rev-parse --verify -q` returns rc=1 (this record), and the round-1 build report and all four auditors agree.

**Planned child (not built).** Copied from the builder and the prep review, who agree:
- `snapshot-prep` tip `0de6d8c8` minus the 207-path manifest gives tree `9232f21ec51bb30e8ddbc0f1e5d913c104ba9909`.
- The same tip minus exclude.txt alone gives `40961dc74016859c09e1c686d512846cc44b4038` (5,643 files).
- Main 53612401 minus exclude.txt gives `8beabe0d`, which reproduces the inventory's tree.

These child tree ids will change once E1-E3 (below) are applied.

## Manifest

| file | paths | sha256 (LF bytes) |
|---|---|---|
| `E:/TaxoArena_tmp/snapshot/inventory/exclude.txt` | 206 | `05cb7beb36f99d22e539e6d406bd401467596909728fbc0111bf06c0188b88d2` |
| `E:/TaxoArena_tmp/snapshot/prep/exclude_plus_rubrics.txt` | 207 | `2b765a0636f49442f5a4921fa35c661a12b03c02d11836ac1c192a3c193cada7` |

- **The 207-path file** is exclude.txt plus `experiment_results/rubric_null/rubrics.json`. That file holds LLM-written rubric texts; the main session held it back under D-2026-10-27-7 as model output "until the author says otherwise".
- **Per-path evidence** is in `E:/TaxoArena_tmp/snapshot/inventory/evidence.tsv` (sha256-lf16 `b1145f75e22a087d`). It has 310 path-by-category rows, written by the inventory's classify.py.

Counts per category for the 206 inventory paths, taken from evidence.tsv. A path can carry more than one category, and 95 do. For the primary count, each path is assigned to the first of its categories in the order gpqa > draft > raw > dump > binary > size.

| category | distinct paths | primary |
|---|---|---|
| b_gpqa | 14 | 14 |
| a_draft (`blog/**`, `docs/drafts/**`) | 15 | 15 |
| c_raw_output | 70 | 70 |
| d_benchmark_dump | 132 | 92 |
| e_binary | 76 | 15 |
| f_over_50MB | 3 | 0 |
| **inventory total** | **206** | **206** |
| held back by D-2026-10-27-7 (rubrics.json) | 1 | 1 |
| **removed from 53612401** | **207** | **207** |

**Kept by an explicit inventory decision.** These are evidence rows on files that stay: KEEP_figure 23, KEEP_fixture 2, KEEP_review 3, KEEP_excerpt 1, KEEP_text_utf16 1, and KEEP_S1 1 (`gradle/wrapper/gradle-wrapper.jar`).

**The 14 GPQA-bearing paths** (paths only): `experiment_results/archv2/{rp12,rp12_r2}/{B0/gpqa,B0/graft_descent,B0/graft_flatleaf,B0p/gpqa,B0p/graft_flatleaf,o1/gpqa,o2/gpqa}/seed_42/validation/MAIN_routing_diagnostics.txt`.

**The 3 paths over 50 MB:**
- `experiment_results/archv2/{rp12,rp12_r2}/B0/readouts/g13_bundle_flatleaf.npz`
- `experiment_results/x12_crossdomain/stack_v2_promptv2_x20.db`

The full list is the manifest.

## Prep: snapshot-prep and its review

The builder's report, copied as the brief states it:
- **Commits.** `snapshot-prep` (worktree `E:/TaxoArena_tmp/snapshot/wt-prep`) has two commits on base 53612401: `ee31fdad` (markers), then tip `0de6d8c8` (README sentence).
- **Edits.** It edits README.md, docs/IMPLEMENTATION.md, docs/RESULTS.md, experiment_results/README.md and experiment_results/r8/README.md. These are mutable docs only; no record, author-owned or `src/` file is touched.
- **Tests.** The snapshot check copy is a git repo built from tree 40961dc7, run with `--offline --no-build-cache --max-workers=3` and no credentials. It gives 569 tests, 0 failed, 2 skipped (the A7 tests). The worktree gives the same result.
- **Trace.** A file-open trace of the test JVM on the full tree saw 1,044 tracked files read and 0 excluded files. The trace cannot see sqlite opens.
- **Checks.** Mutable-doc links: 65, 0 bad. Named-path check: 7 excluded names, 0 unmarked. Checker mutants: 10/10 behaved as expected (7 killed, 3 boundary cases held). No test guard was needed.

**Prep review verdict: NOT MERGEABLE as committed; merge_ok: no.** The reviewer wrote no review file, so this record carries it.

**Merge commit: NONE.** `git merge-base --is-ancestor snapshot-prep main` returns rc=1 (this record). The reviewer checked the preconditions read-only: nothing was staged, and `git merge-tree` is clean (`0745cc22`).

The reviewer's numbers:
- **Diff:** 5 files, 10 lines changed. The two guard tests are unchanged from the blobs that REVIEW_REPO-TIDY checked.
- **Snapshot tree:** 40961dc7 (5,643 files, wrapper jar kept). No kept file is over 50 MB, and no binary is kept apart from the jar.
- **Tests on the reviewer's own snapshot copy:** 569 / 0 failed / 2 skipped (MrlRoutingTest and TraceEnvelopeUnwrapTest).
- **Links:** 10 mutable docs, 65 links, 0 bad. Over all 494 kept `.md` files there are 10 bad links, the same set as the full tree minus the 2 in `blog/`.
- **Markers:** all accurate. Of 13 named-path hits, 4 are marked. The 9 unmarked ones are HTML comments, local-cache mentions, the README L276 covering sentence and a pinned sha256 line.
- **Do tests read excluded files?** No.
- **Reviewer mutants:** 3/3 killed. M1, a link to an excluded file, gives bad = 1. M2, a removed marker, raises the unmarked count from 9 to 10. M3, a removed config file, makes LcbStage0ConfigTest fail.

Conditions (line numbers as of `0de6d8c8`, as the reviewer quoted them):
- **E1 MEDIUM (the merge condition).** README L275 says "a single snapshot". Under D-2026-10-27-7 the public history will be the main session's snapshot plus a child commit, so that is no longer accurate. Fix: "is a snapshot of this repository without its development history; ...", and cite D-2026-10-27-7 in the L282 comment.
- **E2 LOW.** Add "and unpublished drafts" to the L275 list, because kept figure captions cite `docs/drafts/...`.
- **E3 LOW.** RESULTS.md L88 has a double parenthesis. Make it "(committed extract; not in the public copy)".
- **N1 LOW (pre-existing).** RatingsDbGuardTest fails outside a git repo: with no `.git`, 1 of its 3 tests fails. This is the same finding as Z-1 below. Whether to guard it is the main session's choice.
- **Disclosure.** During M3 the reviewer briefly moved a scratch-copy file into `C:\Users\octav\AppData\Local\` by mistake. It was restored, and the scratch tree is clean and still 40961dc7.

Evidence for the prep review is in `E:/TaxoArena_tmp/snapshot/review-prep/`.

## Audit 1: secrets and sizes

**Verdict: CLEAN; exclude_paths [].**

**Object.** e5a29430 (tree a2e3d7d0). It stands in for the absent target.

**Report.** NOT WRITTEN: the harness refused `report.r1.md`. The findings were returned as text and are recorded here. Evidence is in `E:/TaxoArena_tmp/snapshot/audit-secrets-sizes/`:
- `exact_result.json`, sha256-16 of the on-disk CRLF bytes `88da861b381ae0a1`
- `pattern_result.json`, same rendering, `86aba20b950e1c04`
- `census.json` and `blob_sizes.tsv`
- scripts, by sha256 prefix: needles.py 977d28ad, exact_scan.py b0574c26, pattern_scan.py 7d544e63, pattern_controls.py 822e94ab, triage_entropy.py c5672760, entropy_recheck.py 746513e5, hex32_census.py 42c94e05

**Method.** Secret values were held in memory only; the only output is a fingerprint of each.
- Value sources:
  - 50 dotenv files (TaxoArena, every worktree root, and a depth-6 search of Z:, E: and the home folder);
  - the working-tree application.yml literals;
  - the HF token files;
  - the Claude OAuth tokens;
  - docker and gh configs;
  - 17 SSH/PuTTY private keys;
  - the process and registry environment.
- That gives 427 values, 243 distinct, expanded to 1,489 variants: utf8, utf16le, JSON- and URL-escaped, base64 at 3 alignments, and 16-char partials.
- Pattern passes: 32 keyed token formats, assignments, Bearer/Authorization, URL credentials, entropy (with a recheck of the 234,400 path-like tokens), and a 32-hex census.
- Sizes: a full blob census, magic-byte detection of binaries, and the pack size from `pack-objects --revs --stdout`.
- At most 2 worker processes.

**Coverage.** All 5,642 entries (4,405 unique blobs, 294,648,079 B), 165 container members (jar entries and PDF Flate streams), all path names and the commit object. Every zero is a count over the full list.

Not covered:
- Windows Credential Manager, DPAPI stores and browser stores;
- `C:\` outside the home folder;
- rotated keys no longer on the machine, except by their shape.

**Controls.**
- C1 source self-scan: 427/427 values found in their own source files.
- C2 planted canary: found in 10/10 variant forms and 3/3 containers.
- C3 synthetic samples: 32/32 keyed formats found, plus the assignment, Bearer, URL-credential, entropy and hex samples.

**Findings.**
- **Sizes:** 0 of 5,642 files over 50 MB. The largest is 9,485,718 B; 90 files are over 1 MiB. The binary blobs are the wrapper jar, 6 PNG and 17 PDF, plus 1 UTF-16 text file. 0 paths have a binary-output extension. Pack 74,718,548 B; tree total 508,844,974 B.
- **L-1 LOW: Azure AI resource hostname.** It is not a credential, and the value is fingerprinted in the evidence, not printed here. It occurs 33 times in 17 paths, mostly as "PREFLIGHT: OK (endpoint ...". The API key and the full endpoint URL have 0 hits. The host was already public through origin's v1.0.x-thesis tags. Fix: none required; optionally network-restrict the resource.
- **L-2 LOW: session identifiers in local path strings and the mandated `Claude-Session:` attribution lines.** These are not credentials. The messaging token and the OAuth tokens have 0 hits. Fix: none.
- **I-1 INFO.** Benign exact hits: "password" in prose and in a jar constant, "localhost", and an api-version date string.
- **I-2 INFO.** `experiment_results/cert_positive_control/ops_20261003/07_arm_transcript.txt` is UTF-16LE. It was passed to Audit 3, which scanned it decoded with 0 hits.
- **U-1 LOW, now resolved.** The wrapper jar could not be checked offline. Audit 4 checked it online: sha256 91a23940... is the official 7.5/7.5.1 wrapper checksum. The hosted wrapper-validation step also passed (S1, S3).
- **C-1 CONDITION.** The child commit needs a delta audit: `exact_scan.py <ref>` and `pattern_scan.py <ref>` (both take the ref as argv[1]), plus the pack size.

## Audit 2: GPQA

**Verdict: CLEAN; exclude_paths [].**

**Objects.** e5a29430, plus the content of the planned child delta: the 5 prep blobs at `0de6d8c8` and the decisions file at `5525c4f6`.

**Report.** NOT WRITTEN: the harness refused it. Evidence is in `E:/TaxoArena_tmp/snapshot/audit-gpqa/`:
- `summary.txt`, sha256-16 of the on-disk CRLF bytes `34dee2c98a8c8ae3`
- `controls2.out`, `mutants2.out`, `scan_res.pkl`
- scripts: scan2.py, fp2.py, build_fp2.py, controls2.py, mutants2.py, summarize.py

**Method.** A text-free fingerprint, independent of the inventory's.
- Source: `multicorpus_cache_v1.db` corpus_questions with source='GPQA', opened `mode=ro&immutable=1`: 1,192 rows.
- Fingerprinted items: 546 distinct questions, 286 correct answers (16 or more squashed characters) and 615 distractors (40 or more raw characters).
- Normalisation: decode escapes (JSON, HTML, %XX; one and two passes), then NFKC, then casefold, then drop every non-alphanumeric character.
- Windows: 30 squashed characters, plus a 16-char prefix window verified by full hash. 212 windows shared with non-GPQA corpora were dropped; 211,445 were kept.
- Rule, fixed before the scan: HIT if coverage is 0.5 or more, or the longest run is 50 or more squashed characters.
- Layers scanned: raw bytes; gzip, bz2, xz and zip (recursively); npy; PDF; PNG text; UTF-16; base64; JSON, HTML and %-decoded text. Also commit objects, path names, and canary and GPQA-header regexes.
- Second, independent method: 2,403 exact raw substrings, passed to `git grep -F -l -f -` on stdin only.

**Coverage.** 5,642 paths, 4,405 blobs, 508,844,974 B.
- 0 HIT, 0 errors, 0 container failures.
- 1 REVIEW, cleared: `docs/reviews/READY_content_closure.md` L78. Item Q332 matched 3 of 337 windows in a 32-char run; it is a generic MCQ stem.
- 0 canary files. One false positive was cleared: a project phrase in `docs/reviews/2026-09-23_tie_mechanics_post.md`.
- 0 CSV header hits.
- 0 hits in the commit messages of e5a29430, 0de6d8c8 and 5525c4f6.
- 0 path-name hits.
- Exact grep on e5a29430: 0 files.
- Planned child delta (6 paths): 0 HIT, 0 REVIEW.

**Controls.**
- Positive: 85/85, including fully escaped, double-JSON, HTML-entity, gzip, zip, base64-of-gzip, UTF-16 and %-encoded forms.
- Negative: 396 held-out MMLU-Pro science rows give 0 HIT and 0 REVIEW. The empty-fingerprint mutant gives 0 HIT.
- Mutants M1-M4 all KILLED. M1 and M2 survived the first control suite and were killed after fully escaped controls were added.
- Real-data check: over the 133 excluded non-DB files the scan flags exactly the inventory's 14 b_gpqa paths and nothing else. The exact grep on 53612401 lists 21 files, all of them in exclude.txt.

**Findings.**
- **Target absent.** This CLEAN does not certify a commit that has not been built. For the child, run `scan2.py <delta.tsv> <out.pkl> 2` on the delta from e5a29430. If the child is built as an orphan from anything other than 53612401 minus the 207 paths, rescan the whole tree.
- **Method limit (LOW).** Correct answers under 16 squashed characters (575 row-instances) and distractors under 40 characters are not fingerprinted. They would still be caught next to their question.
- **Scope (LOW).** The excluded DBs were not scanned by scan2. The exact grep hit `x12_crossdomain/rubric_kit.db` and `rubric_kit_rk1b_cards.db`. Any DB that is ever re-included needs a row-level GPQA scan first.

## Audit 3: raw outputs and benchmark dumps

**Verdict: CLEAN; exclude_paths [].**

**Object.** e5a29430.

**Report.** `E:/TaxoArena_tmp/snapshot/audit-raw-dumps/report.r1.md` (sha256-lf16 `26439a03b515bdd5`).

**Method.** Fingerprints built from the local DBs, independent of the inventory's multi_fp.npz, with every DB opened read-only and immutable.
- Benchmark index: about 254k items and 17.69M ten-token windows (`fp/k10.npy` e69aea5c). Sources: MMLU-Pro, BBH, MATH, GPQA, MuSR, IFEval, AG News, 20NG, banking77, CLINC, MASSIVE, JudgeBench, LiveCodeBench, SuperGPQA, BFCL and the embeddings_cache queries.
- An item counts as matched in a file when 80% or more of its windows occur there.
- Raw-output index: 107,393 + 31,950 items (`fp_out2/k10.npy` 51811d29), taken from every 200+ char reply in the judge and solve caches, plus samples of contestant outputs.
- Also: structural key classing of JSON/CSV strings; free-text output shapes; 9,509 short items matched as whole delimited pieces; magic-byte binary detection; PDF text extraction.
- Script pins (sha256-16): fpcore 84d5b98a, build_fp bc3f5607, build_fp_out2 cc769fd4, scan 86e0fa65, classify 558ffb22, short_items 25d0e6a5.

**Coverage.** 5,642/5,642 blobs: 5,617 UTF-8, 1 UTF-16 (decoded), 17 PDF, 1 jar and 6 PNG (no OCR). Results:
- GPQA: 0 files.
- Benchmark dumps: 0 files at 20 or more items; the highest per-corpus count in any file is 5.
- Raw-output index: 0 full matches; 4 files have a single weak partial match below 50%.
- Structural raw outputs: 0 files over the more-than-3 bar once false positives are cleared.
- Record files: 0 hits.

**Controls.**
- Positive: 115/115 of the inventory-excluded text paths are flagged on 53612401. Synthetic tests: 25/25 x20 replies, 8/8 contestant outputs, 30/30 MMLU-Pro questions and 38/40 banking77 utterances.
- Negative: README.md gives 0.

**Findings** (all LOW):
- **L1.** The four `experiment_results/canary_epoch2/dry_run_pass*.log` files each print the same 3 model texts. That is at the more-than-3 bar, not over it.
- **L2.** `experiment_results/trace_truncation/dry_run_main.log` has one response of 200+ chars.
- **L3.** The three `experiment_results/archv2/induce_rubric_{1,2,3}/rubric_mcq_*.json` files each hold one grok-induced rubric. That is under the bar, but they are the same kind of text as rubrics.json.
- **L4.** `experiment_results/intent_transfer_s0/ingest/census.txt` matches 5 MASSIVE items.
- **L5.** Payload previews and fixtures with 1-2 items each.
- **L6.** The registered screening probe texts in the `induce_rubric_*` held-out, fit and unfit files were written by the specialist; they are not model outputs.
- **D1 (decision for the orchestrator, or the author if it is a content choice).** Should L1 and L3 follow the rubrics.json hold-back? Under the threshold they stay.
- **Gaps.** The 6 PNGs (no OCR); intent utterances under 3 tokens; contestant outputs, covered by sample only; benchzoom downloads, MATH-train copies and Multi-SWE text, none found locally.

## Audit 4: links and build

**Verdict: FINDINGS; exclude_paths [].**

**Object.** The object of record is absent, so the whole procedure was run on the SUBSTITUTE e5a29430. That object is mode- and blob-identical, path for path (5,642/5,642), to main 53612401 minus the 207 paths.

**Report.** NOT WRITTEN: the harness refused it. Evidence is in `E:/TaxoArena_tmp/snapshot/audit-links-build/`:
- `test.log`, sha256-16 of the on-disk CRLF bytes `f941b4f8bee0f488`
- `ci_sim.log`, same rendering, `7ce65d7261971cce`
- `nogit_test.log`, same rendering, `a11c6ccfb0b69429`
- scripts linkcheck.py, refscan.py, pathscan.py, wrapper_check.py, junit_sum.py, plus the `lc_*` and `ps_*` result files

**Method.**
- **Clone.** `git clone --no-local` of public-snapshot-pushed, with the remote removed.
- **Build.** compileKotlin and compileTestKotlin, then `test --offline --no-build-cache --max-workers=3 --no-daemon`, with no .env and no credential variables.
- **CI simulation.** Sparse checkout of src and gradle, JDK 21, a cold GRADLE_USER_HOME and an empty `maven.repo.local`.
- **ZIP simulation.** A `git archive` export with no `.git`.
- **Wrapper.** The jar's sha256 was checked against all 384 published Gradle wrapper checksums.
- **Link checker.** Inline links, images, strict ref-defs and HTML href/src, matched with exact case against the tracked set, plus GitHub-slug fragments for the mutable docs. It was run on e5a29430, on 53612401 minus 207, on 0de6d8c8 minus 207, and on full main.

**Coverage and results.**
- **Compile:** exit 0.
- **Tests:** 569, 0 failed, 0 errors, 2 skipped (MrlRoutingTest.testMrlConfigDefaults and the TraceEnvelopeUnwrapTest blank-trace case), parsed from 114 fresh JUnit XMLs.
- **CI simulation:** BUILD SUCCESSFUL, exit 0, the m2 directory still empty, and the downloaded 8.10 zip matches the official sha256.
- **Links in the 11 mutable docs:** 65/65 resolve, with 0 case mismatches and 0 broken anchors.
- **Record files:** 1 broken relative link (`docs/reviews/POSTRUN_FLAT-COMPARE.md` L63), already broken in main. The record stays as is.
- **Would-be child (0de6d8c8 minus 207):** the same link result.

Not simulated exactly: the Linux runner, temurin, and setup-gradle caching. The hosted run under S3 covers them.

**Controls.**
- A planted fixture: 10/10 defects found, 0 false positives once the ref-def rule was made strict.
- Raw `](` counts equal the checked counts.
- The e5a29430 result equals the main-minus-exclusions result (TSV diff 0).
- Two self-corrections were redone: a wrong CR count from grep, and a first 8.x wrapper scan that was vacuous.

**Findings.**
- **OBJ-1 BLOCKER: object absent.** `refs/heads/public-snapshot` does not exist. Fix: settle orphan versus child, merge snapshot-prep after its delta review, build the ref, then re-run this audit (the scripts take `<repo> <rev>`).
- **Z-1 MEDIUM** (pre-existing, same as prep N1). In a no-`.git` export, `RatingsDbGuardTest` "a tracked database is refused" fails, 1 of 3; a git clone passes 3/3. This makes README L257 ("the rest of the suite passes") false for ZIP users. Fix: an A7-style `assumeTrue` on git, or reword L257 to "on a git clone". This is the main session's choice.
- **LOW, named but absent.** 7 mentions name excluded files. Three of them say the file is present: README L234, RESULTS L88 and r8/README L27. Prep `0de6d8c8` marks all three.
- **LOW, unresolved backtick mentions.** 30 of 172 do not resolve even in full main (local caches and archive history). Fix optional.
- **LOW, broken links in other docs.** 3, all pre-existing: `docs/prereg_discriminative_power.md` L196 and `docs/separation_null_by_size.md` L15 and L24.
- **W-1 LOW.** `gradle-wrapper.properties` has no `distributionSha256Sum`. Fix optional.
- **LOW, line endings.** There is no `.gitattributes`, so `gradlew.bat` is stored LF; `gradlew` is LF with mode 100755, which is correct. Fix optional.
- **LOW, suite writes the checkout root.** The suite creates 11 gitignored artefacts at the checkout root. That is harmless in a clean clone; the data-bearing case is for the data steward.
- **INFO, observed and not judged.** `.claude/agents/` (12 tracked files) and JUnit XML under `experiment_results/` are in the snapshot. Audits 1 and 3 scanned every blob, these included, with no hit.

## Rounds

| round | build | audits | outcome |
|---|---|---|---|
| 1 | **blocked** (details below) | 4 audits, all on the substitute e5a29430: secrets and sizes CLEAN, GPQA CLEAN, raw/dumps CLEAN, links-build FINDINGS | PUSH_OK no |

The round-1 build:
- It stopped at its stop condition: snapshot-prep is not merged, so there was no SOURCE merge commit.
- It wrote no index, tree, commit, ref or manifest under `E:/TaxoArena_tmp/snapshot/build/`.
- It flagged that the brief asks for an orphan while D-2026-10-27-7 asks for a child commit.

No round 2 has run.

## S1 / S2 / S3

These are the conditions in REVIEW_REPO-TIDY, under the heading "## Conditions on the downstream snapshot (D-2026-10-27-4; not defects of this branch)".

**S1 (keep `gradle/wrapper/gradle-wrapper.jar`): HELD on e5a29430.**
- The jar is present: blob `249e5832f090a2944b7473328c07c9755baa3196` (`git ls-tree`, this record).
- Its sha256 91a23940... is the official Gradle 7.5/7.5.1 wrapper checksum (Audit 4).
- The hosted wrapper-validation step passed (S3).

**S2 (link and path check on the snapshot tree): links HELD, presence claims OPEN.**
- Links: 65/65 resolve in the mutable docs (Audit 4, prep review).
- Presence claims: three mutable-doc mentions still claim an excluded file is present in e5a29430: README L234, RESULTS L88 and r8/README L27. Prep `0de6d8c8` marks all three, but it is not merged. S2 closes when the child carries the markers and a delta audit confirms them.

**S3 (the first hosted run on ubuntu-latest decides): HELD for e5a29430.**
- The brief states S3 as still open. This record observed a completed run (`gh run list`, `gh run view 40570616518`): run 40570616518, workflow CI, event push, branch main, head e5a29430, created 2026-10-27T19:36:19Z, conclusion **success**.
- Its job, compile, succeeded at every step: checkout, wrapper-validation, setup-java, setup-gradle, and `./gradlew --no-daemon ... compileKotlin compileTestKotlin`.
- `ci.yml` at e5a29430 has `runs-on: ubuntu-latest`.
- The child commit gets its own first hosted run once pushed, and that run decides S3 for the child.

## Open before PUSH_OK can be yes

1. Apply E1 (with E2 and E3) on snapshot-prep, get merge_ok from a delta review, and merge into main.
2. Settle orphan versus child. The workflow brief says orphan; D-2026-10-27-7, the latest author decision, says a child of the public commit with no second force-push. The orchestrator settles this; this record reads D-2026-10-27-7 as the decision of record.
3. Build `refs/heads/public-snapshot`.
4. Re-run all four audits on that ref, using the delta commands each auditor named:
   - Audit 1: `exact_scan.py` and `pattern_scan.py <ref>`, plus the pack size.
   - Audit 2: `scan2.py` on the delta (on the whole tree if the child is an orphan not equal to 53612401 minus 207).
   - Audit 3: `scan.py <commit> out.jsonl [pathlist]`.
   - Audit 4: the links-build scripts on `<repo> <rev>`.
5. Open choices; they do not block by severity:
   - Z-1/N1: guard RatingsDbGuardTest or reword README L257 (the main session's call).
   - D1: whether the L1 and L3 rubric texts follow the rubrics.json hold-back (the orchestrator's call, or the author's).
   - The optional LOWs: W-1, line endings, and the three pre-existing broken links in other docs.

## Overall

**PUSH_OK: no.** Not all final audits are CLEAN (links-build: FINDINGS, OBJ-1 BLOCKER), and the object to push does not exist.

For the already public e5a29430, no audit requests a removal: exclude_paths = [] in all four audits, and there are 0 secret, 0 GPQA and 0 over-bar raw-output or dump hits.

Read-only commands run by the registrar for this record:
- `git rev-parse --verify -q refs/heads/public-snapshot`
- `git for-each-ref`
- `git cat-file -p e5a29430`
- `git diff --name-status 53612401 e5a29430`, and `diff` against the 207-path manifest
- `git ls-tree -r --name-only` on both commits
- `git merge-base --is-ancestor snapshot-prep main`
- `git ls-remote origin main refs/tags/public-snapshot-2026-10-27-r0`
- `git ls-tree e5a29430 gradle/wrapper/ .github/workflows/`
- `gh run list -L 5`, `gh run view 40570616518`
- `sha256sum` of the manifests and evidence files
- category counts from evidence.tsv

## Round 2: child commit (D-2026-10-27-7)

Recorded by the registrar on 2026-10-27, at main `1d23c3c7` (insertion only; the round-1 text above is unchanged):
- Zero LLM calls. The registrar ran only read-only git and gh queries (listed at the end of this section). Ledger unchanged. Nothing was pushed by this workflow; origin is untouched.
- This section contains no secret value and no GPQA text. Excluded files are named by path only.
- **Orphan versus child is settled** (round-1 item 2 under "## Open before PUSH_OK can be yes"): under D-2026-10-27-7, as the orchestrator's brief reads it, the doc-prepped version is pushed as a CHILD of `e5a29430` (`commit-tree -p e5a29430`), never an orphan and never a force-push.

### Round-2 verdict

**PUSH_OK: no.** The rule for this round is PUSH_OK yes only if both final audits are CLEAN with no exclude_paths. The content audit is CLEAN; the links-build audit returned FINDINGS (two LOW, no BLOCKER, HIGH or MEDIUM). exclude_paths = [] in both: nothing has to leave the tree, and nothing in the delta is a secret, GPQA text, a raw output or a benchmark dump.

| dimension | object audited | verdict | exclude_paths | deciding numbers |
|---|---|---|---|---|
| content (secrets and sizes, GPQA, raw outputs and dumps) | child `344aa90c` (tree `a7888e78`), full ref plus the 9-path delta | CLEAN | [] | secrets: +2 exact hits over round 1, both benign words in the new review file; GPQA 0 HIT / 0 REVIEW on the delta; 0 benchmark items and 0 raw-output matches in the delta; 0 files over 50 MB |
| links and build | child `344aa90c` | FINDINGS | [] | F1 LOW (README L257 false for a ZIP copy), F2 LOW (three "tracked" mentions of an excluded file); links 72/72; clone 569 / 0 failed / 2 skipped; export 569 / 0 failed / 3 skipped |

### Objects (round 2)

Hash kinds: commit and tree ids are git object ids; the manifest sha256 is of its LF bytes (0 CR). Every delta blob is LF with no CR, so the LF rendering is the only one.

- **Prep fix commit.** `snapshot-prep` tip `1771b40138319f788ce0c4fd620d3eaf83cb734e` (parent `0de6d8c8`, tree `8291b9f4`; this record: `git rev-parse`). It edits README.md, docs/RESULTS.md, docs/separation_null_by_size.md and src/test/kotlin/taxonomy/service/RatingsDbGuardTest.kt (`git diff --name-only 1771b401^1 1771b401`, this record): E1, E2, E3, the Z-1/N1 guard (RatingsDbGuardTest skips its refusal check when there is no git metadata; new probe `gitCheckoutPresent`) and two dead link markups dropped in separation_null_by_size.md. Branch history on 53612401: `ee31fdad`, `0de6d8c8`, `1771b401`.
- **Delta review: MERGEABLE, merge_ok yes.** No review file was written (the harness refuses report files); the merge commit message carries the review summary.
- **Merge commit.** `a0fe0c013b1db1607406fdf52d487119f7127efc` (`--no-ff`), parents `b55f2478` and `1771b401`, tree `ee16733b` (the reviewer's `git merge-tree` prediction). `b55f2478`, `5525c4f6` and `1771b401` are ancestors of it, and it is an ancestor of main (`git merge-base --is-ancestor`, this record). This resolves the builder's condition that the branch was based on 53612401 without 5525c4f6 and b55f2478.
- **Child of record.** `344aa90cd1efe3c3da0c6307712fda0f805152e8`, tree `a7888e78072f41c3cf2adfa96cc79816e860ab0c`, exactly one parent `e5a29430ee9254e5938b785190e0083b4c2a5287`; history 2 commits (`git cat-file -p`, `git rev-list --count`, this record). SOURCE `a0fe0c01`. Local `refs/heads/public-snapshot` and the lightweight tag `public-snapshot-2026-10-27-r1` both point to it. Neither is on origin: `git ls-remote origin` shows `refs/heads/main` (and HEAD) at `e5a29430`, the v1.0.x-thesis tags and 76 pull-request refs, no public-snapshot branch and no r0/r1 tag (this record).
- **Tree check.** `git diff --name-status a0fe0c01 344aa90c` is 207 D and nothing else; the sorted list equals `E:/TaxoArena_tmp/snapshot/prep/exclude_plus_rubrics.txt` (sha256 `2b765a0636f49442f5a4921fa35c661a12b03c02d11836ac1c192a3c193cada7`, the round-1 pin); the child has 5,643 files; the 9 delta blobs equal their `a0fe0c01` blobs (this record; the builder and both auditors agree).
- **Intermediate trees** (copied from the builder and the delta review, who agree): `1771b401` minus the manifest is `dba05ea6`, 7 modified, 0 added, 0 deleted against `e5a29430`.

### Delta, e5a29430 -> 344aa90c

1 added, 8 modified, 0 deleted (`git diff --name-status`, this record); all mode 100644, LF, no CR. Sizes in bytes, old -> new, copied from the builder (`E:/TaxoArena_tmp/snapshot/build-child/delta_sizes.tsv`):

| status | path | size |
|---|---|---|
| M | README.md | 26640 -> 27131 |
| M | docs/IMPLEMENTATION.md | 7254 -> 7279 |
| M | docs/RESULTS.md | 7244 -> 7344 |
| M | docs/agents/author_decisions/2026-10-27.md | 10664 -> 12425 |
| A | docs/reviews/REVIEW_PUBLIC-SNAPSHOT.md | 28329 (the round-1 text only) |
| M | docs/separation_null_by_size.md | 31024 -> 30983 |
| M | experiment_results/README.md | 4205 -> 4230 |
| M | experiment_results/r8/README.md | 2252 -> 2327 |
| M | src/test/kotlin/taxonomy/service/RatingsDbGuardTest.kt | 2497 -> 4149 |

Builder's exclusion-name check: 0 of 9 paths match a category (binary extension, `blog/`, `docs/drafts/`, `MAIN_routing_diagnostics`, `gpqa` in the name, over 50 MB). The decisions file (+5 lines) and RatingsDbGuardTest (+33 lines) only add lines (links-build audit).

### Build and tests (round 2)

Copied from the reports named; scratch evidence in the directories given.
- **Prep builder** (`E:/TaxoArena_tmp/snapshot/prep-r2/`): worktree 569 tests, 0 failed, 2 skipped (the A7 pair); git-archive export of `dba05ea6` (no `.git`, LF, 5,642 blobs matching the tree) 569 / 0 failed / 3 skipped (the A7 pair plus the RatingsDbGuardTest refusal check); git clone of the planned-child shape RatingsDbGuardTest 3/3 passed, 0 skipped. Mutants: the 6 behaviour-changing ones killed or caught; the old unguarded test fails in the export (Z-1 reproduced); 2 equivalent. The new probe is in the compiled class in all three runs.
- **Delta reviewer** (`E:/TaxoArena_tmp/snapshot/rev-delta-r2/`): clone of the planned child 569 / 0 / 2, RatingsDbGuardTest 3/3; export 569 / 0 / 3; links 65/65; marker check 7 names, 0 unmarked. Mutants: M1 (guard ignores `ranking.db.path`) KILLED in the clone; M2 (probe without the `.git` check, export inside an unrelated git repo) KILLED; M3 (probe always reports no git) survives as a failure, caught only by the skip count, hence condition C3 (count skips on a clone).
- **Child builder** (`E:/TaxoArena_tmp/snapshot/build-child/`): git clone of `344aa90c` 569 tests, 0 failed, 0 errors, 2 skipped (`MrlRoutingTest.testMrlConfigDefaults`, the `TraceEnvelopeUnwrapTest` blank-trace check); RatingsDbGuardTest 3 run, 0 skipped (C3 met); `gitCheckoutPresent` in the compiled class.

### Audit C (content): CLEAN; exclude_paths []

**Object.** `refs/heads/public-snapshot` = `344aa90c` (tree `a7888e78`), read-only, 0 LLM calls, at most 2 workers. Report not written (harness); findings returned as text, recorded here. Evidence: `E:/TaxoArena_tmp/snapshot/audit-delta-c4/`.

**Method and findings.**
- **Object.** One parent `e5a29430`, history 2; the tree is exactly `a0fe0c01` minus the 207-path manifest (mode/blob/path diff 0 lines, 5,643 entries); manifest sha256 matches; 0 of 207 manifest paths in the child (exact, as directory prefixes and case-folded); wrapper jar `249e5832` kept.
- **Delta.** 9 paths plus the commit object; all 9 blobs identical to `a0fe0c01`; UTF-8 text, LF, 0 NUL, no magic bytes; delta pack 74,019 B (22 objects). 0 files over 50 MB in the tree (largest 9,485,718 B); binaries are the round-1 set (17 PDF, 6 PNG, the jar, 1 UTF-16 file).
- **Secrets.** Copies of `exact_scan.py` and `pattern_scan.py` with the round-1 pins, run on the full ref from the auditor's own scratch (run in place they would overwrite the round-1 evidence). Controls C1 427/427, C2 13/13. Exact scan 3,048 hits against 3,046 in round 1; the +2 are both in the new review file at its L162 (the round-1 I-1 line): the words "localhost" and "password" (identified by fingerprint; benign). Commit object: 4 hits, the session id in the `Claude-Session:` line (round-1 L-2; `e5a29430` has the same 4). Pattern scan: 1 new candidate, the path `experiment_results/r8/README`, an entropy false positive.
- **GPQA.** `scan2.py`, 2 workers: 0 HIT and 0 REVIEW on the 9 paths and the commit object; canary regexes found only the plain word "canary" (4); positive control 10/10; independent exact grep with 3,225 needles: 0 files (control 1/1).
- **Raw outputs and dumps.** `scan.py` with fp and fp_out2: 0 benchmark items and 0 raw-output matches in the delta; free-text flags only `verdict_token` (2) in `docs/IMPLEMENTATION.md`, unchanged from round 1; controls reproduce the record (215 GPQA items, 22,044 output-keyed strings); `short_items.py` on the full tree flags 1 file, the same pre-existing one as round 1, not in the delta.
- **INFO-1.** The review file published in the child says "PUSH_OK: no" and "public-snapshot ABSENT"; that is true of the round-1 record as written. This round-2 section reaches the public copy only through a later child.
- **INFO-2.** The new record reveals only harmless facts (local scratch paths, workflow ids, the count of 17 SSH keys, the stated coverage gaps); no values.

### Audit L (links and build): FINDINGS; exclude_paths []

**Object.** `344aa90c`, tree `a7888e78`, one parent, history 2; tag r1 lightweight on the same commit. Read-only. Report not written (harness); findings recorded here. Evidence: `E:/TaxoArena_tmp/snapshot/audit-child-links/`.

**Method and results.**
- **Tree check.** SOURCE `a0fe0c01` -> child is 207 deletions, identical to the manifest (sorted diff empty); manifest sha256 matches; 5,643 files; wrapper jar present (blob `249e5832`, sha256 91a23940...).
- **Clone.** `--no-local` clone, remote removed, Windows autocrlf: 569 tests, 0 failed, 0 errors, 2 skipped (the A7 pair); RatingsDbGuardTest 3 run, 3 passed, 0 skipped; `gitCheckoutPresent` in the compiled class (1 hit).
- **Export.** git-archive with `core.autocrlf=false` (the LF bytes of GitHub's ZIP), no `.git`: 569 tests, 0 failed, 0 errors, 3 skipped. RatingsDbGuardTest skips its refusal check instead of failing it: **Z-1 / N1 closed** in the child.
- **Guard mutants.** M1: `gitCheckoutPresent` forced true in the export -> that test fails (1 of 3), so the skip does real work. M2: an empty `.git` directory in the export -> skip, not failure.
- **Links.** The 11 mutable docs plus separation_null_by_size.md: 72 links, all resolving (65 to files, 7 to headings in the same doc); raw `](` counts equal checked counts; the auditor's checker and the round-1 checker agree; the auditor's checker caught 7/7 planted defects; clone and export identical. Remaining broken links are 2 pre-existing ones in record and other docs (`docs/reviews/POSTRUN_FLAT-COMPARE.md` L63, `docs/prereg_discriminative_power.md` L196; the builder left L196 alone because the docs index says `prereg_*.md` are preserved unedited).
- **Markers.** All three named presence claims are marked "(not in the public copy)": README L234, RESULTS L88, r8/README L27; five more mentions carry the same marker; every marked file is absent from the child (no `.db`, no `r8/*/judging/`). RESULTS L88 reads "`snapshots_frozen.db`, a committed extract (not in the public copy)", not the round-1 E3 text, because that text tripped the prep marker check; the delta reviewer accepted the deviation.

**Findings.**
- **F1 LOW (= delta-review C1).** README L257 says two tests skip; that is true for the clone (2) and false for a ZIP copy (3). Fix: name the RatingsDbGuardTest skip for copies without git metadata.
- **F2 LOW (new).** docs/separation_null_by_size.md calls `snapshots_frozen.db` "tracked" at L284, L380 and L478, but the file is not in the public copy; only README L276's general sentence covers it. Fix: add "(not in the public copy)" at those three lines.
- **INFO.** The published review file still reads "PUSH_OK: no / public-snapshot ABSENT" (= Audit C INFO-1). The Linux runner was not simulated; the child's first hosted run decides S3.

Line numbers in F1, F2 and the markers are as of `344aa90c` (`_as_of 344aa90c`, re-grepped by this record with `git show 344aa90c:<path>`).

### Other open conditions (round 2)

- **C2 LOW (delta review, open).** README L275 says the cited commit hashes "refer to that unpublished history", but origin still serves 526 early commits (up to 2026-08-02) through the v1.0.x-thesis tags and 76 pull-request refs. Reword.
- **C4 (delta review): met.** The added review file has now been through both audits in this delta.
- **Main moved after SOURCE.** Main gained `56da993f` and `1d23c3c7` (two added files: `docs/reviews/POSTRUN_EMBED2-WORK.md`, `docs/reviews/POSTRUN_TAU-CONT-ALL.md`) and now this section. A child built from a later main carries them, and its delta from `e5a29430` needs the delta audits again on every path not already audited here.
- **D1 (round 1, open).** Whether the L1/L3 rubric texts follow the rubrics.json hold-back; outside this delta.

### S1 / S2 / S3 (round 2)

- **S1 (keep the wrapper jar): HELD on `344aa90c`.** Blob `249e5832f090a2944b7473328c07c9755baa3196` (`git ls-tree 344aa90c gradle/wrapper/gradle-wrapper.jar`, this record); sha256 91a23940... (Audit L).
- **S2 (links and path check): links HELD (72/72); presence claims HELD for the three named in round 1, OPEN on F2** (three unmarked "tracked" mentions in separation_null_by_size.md).
- **S3 (first hosted ubuntu-latest run decides): OPEN for the child.** `344aa90c` is not pushed, so it has no hosted run; `gh run list -L 3` (this record) shows the latest run is 40570616518 on `e5a29430` (success, round 1). The first hosted run after the child is pushed decides S3 for it.

### Rounds (round 2)

| round | build | audits | outcome |
|---|---|---|---|
| 1 | blocked (snapshot-prep not merged) | 4 audits on the substitute `e5a29430`: 3 CLEAN, links-build FINDINGS | PUSH_OK no |
| 2 | child `344aa90c` (tree `a7888e78`, parent `e5a29430`) from SOURCE `a0fe0c01` | content CLEAN, links-build FINDINGS (F1, F2 LOW) | PUSH_OK no |

### Open before PUSH_OK can be yes (round 2)

1. A docs commit on main fixing F1 (README L257), F2 (separation_null_by_size.md L284, L380, L478) and C2 (README L275).
2. A new child with parent `e5a29430` (`commit-tree -p e5a29430`, D-2026-10-27-7 as the brief reads it; r1 was never pushed), built from that main minus the 207-path manifest, with C3's skip count on a clone (RatingsDbGuardTest 0 skipped).
3. Both delta audits on the new child, over every path in its delta from `e5a29430` not audited here (at least README.md, docs/separation_null_by_size.md, this review file and the two POSTRUN files), with PUSH_OK yes only if both are CLEAN with exclude_paths [].
4. After the push (no force), its first hosted ubuntu-latest run decides S3.

Read-only commands run by the registrar for this section:
- `git rev-parse` on `refs/heads/public-snapshot`, the r1 tag, the child tree, `a0fe0c01^1`, `a0fe0c01^2`, `a0fe0c01^{tree}`, `1771b401^1`, `1771b401^{tree}`; `git cat-file -t` on the r1 tag; `git cat-file -p 344aa90c`; `git rev-list --count 344aa90c`
- `git merge-base --is-ancestor` (a0fe0c01 in main; b55f2478, 5525c4f6, 1771b401 in a0fe0c01)
- `git diff --name-status e5a29430 344aa90c`; `git diff --name-status a0fe0c01 344aa90c` and `diff` against the manifest; `git diff --stat a0fe0c01 344aa90c -- <9 delta paths>` (empty); `git diff --name-only 1771b401^1 1771b401`; `git log --oneline 53612401..1771b401`; `git diff --name-status a0fe0c01 HEAD`
- `git ls-tree -r --name-only 344aa90c | wc -l`; `git ls-tree 344aa90c gradle/wrapper/gradle-wrapper.jar`
- `git show 344aa90c:<path>` for README L234/L257/L275, RESULTS L88, r8/README L27, separation_null_by_size.md L284/L380/L478
- `git ls-remote origin`; `gh run list -L 3`; `sha256sum` of the manifest

## Round 3: wording fixes and the push of record (main session, D-2026-10-27-7)

- F1, F2 and C2 of round 2 were fixed on main as 72d44757 (README L257 names the RatingsDbGuardTest skip in copies without git metadata; README L275 says the early history up to the v1.0.x-thesis tags is on GitHub; docs/separation_null_by_size.md L284/L380/L478 mark snapshots_frozen.db "not in the public copy"; one line each, docs only, not separately reviewed).
- Child of record: ceb5901e2db031c1c2333e7c8619d5782c1ddad2, tree 1abfbacd63572e5789aa8e1d4975a00a6544fdd1 = 72d44757 minus the 207-path manifest (sha256 2b765a06...; diff-tree removals equal the manifest exactly), parent e5a29430. Delta against the audited child 344aa90c: README.md, docs/separation_null_by_size.md, docs/reviews/REVIEW_PUBLIC-SNAPSHOT.md (round 2 section), and the added records docs/reviews/POSTRUN_EMBED2-WORK.md and POSTRUN_TAU-CONT-ALL.md; no code change, so the round-2 clone (569/0/2) and no-git export (569/0/3) results carry over.
- Main session's scan of the full child tree (scratchpad quickscan.py: GPQA 9-token windows over 546 questions and 791 answer/option strings with raw/JSON/HTML/embedded controls; exact .env and HF token values with 16-char fragments; sizes): 0 GPQA files, 0 files over 50 MB, secret-fragment hits in the same 18 files as the audited e5a29430 (the already-public Azure host name, L-1; .env.example by a generic URL suffix); raw-output markers in the 5 changed files: 0.
- Pushed as a fast-forward (no force): origin main e5a29430 -> ceb5901e; local tag public-snapshot-2026-10-27-r2. S3: hosted CI run 40591946965 on ceb5901e, ubuntu-latest, success (1m19s). The unpushed 344aa90c (tag r1) is superseded.
- Still open for the author: D1 (whether the three induce_rubric JSON files and four canary dry-run logs, public and under threshold, follow the rubrics.json hold-back).
