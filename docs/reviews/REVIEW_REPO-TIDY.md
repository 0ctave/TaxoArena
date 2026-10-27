# REVIEW_REPO-TIDY: branch repo-tidy (tip 3d4e2843) against main (9b78ace1), plus the uncommitted C3/C4 drafts

Authority: D-2026-10-27-1 (64c37913) and D-2026-10-27-6 (9b78ace1, committed AFTER the branch base c98534d2). Zero LLM calls.
Reviewer: adversarial-reviewer, 2026-10-27. Worktree `Z:/FAC/TUBerlin/THESIS/TaxoArena_wt_tidy`. Ledger v430 unchanged.

## Verdict

| unit | state | verdict |
|---|---|---|
| C1 `5a7dedfc` (removes Dockerfile, mcp-server/ x3, scripts/plot_results.py) | committed | **MERGEABLE** |
| C2 `3d4e2843` (.github/workflows/ci.yml, compile-only, SHA-pinned) | committed | **MERGEABLE** (the first hosted run decides, S3) |
| C3 docs/README.md, 3 directory READMEs, 4 line-1 banners | uncommitted drafts | **MERGEABLE AFTER E5, E6** (MEDIUM); LOW items E8, E9, E11 can go in the same commit. Delta check only for the edited lines |
| C4 root README.md | uncommitted draft | **NOT MERGEABLE as drafted**: E1, E2 (HIGH), E3, E4 (MEDIUM). Delta review of the edited README needed before merge |

merge_ok: C1+C2 now (`git merge-tree --write-tree main repo-tidy` is clean; main moved only by +9 lines in
docs/agents/author_decisions/2026-10-27.md). C3 after E5/E6. C4 after E1-E4 and a delta review.

## Per-claim table (deciding claims only)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | diff main...repo-tidy touches nothing author-owned and no insertion-only record | 6 paths (1 M, 5 D). Diff over report, config, .gitignore, .env, docs/agents, docs/reviews, programme, ledger, registrations: 0 committed and 0 uncommitted | CONFIRMED | - |
| 2 | the removed paths have zero remaining references | rg -i `dockerfile\|mcp.server\|plot.results\|my_mcp` over the main checkout: 23,771 text files, tracked + untracked + ignored, report/ included, 0 rg errors. Only the plan's false positives turn up: build.gradle.kts L674, pot_runner.py L6/L34/L35/L168 (its own embedded string), and archive PR_HISTORY #61 (untracked, names a Gradle dependency). benchzoom: 15,120 files, hits only in .venv third-party packages. Memory: 44 files, 0 hits. All 181 local branch tips (`git grep`): the same false positives only | CONFIRMED | - |
| 3 | build and default suite pass in the worktree | `.\gradlew.bat compileKotlin compileTestKotlin test --offline --max-workers=6`: **569 tests, 2 failed**. Both failures are the known environmental ones (MrlRoutingTest.testMrlConfigDefaults L51; TraceEnvelopeUnwrapTest blank-trace L124). compile was UP-TO-DATE (src is unchanged by the delta); test executed | CONFIRMED (with the 2 known failures) | - |
| 4 | the CI job compiles from a sparse clean clone | own stand-in: depth-1 `--sparse` clone of repo-tidy, cone `src gradle`, empty GRADLE_USER_HOME and empty `-Dmaven.repo.local`. **BUILD SUCCESSFUL in 5m13s**, 4 tasks executed (fresh compile), m2 holds 0 entries afterwards | CONFIRMED (Windows proxy) | - |
| 5 | action pins and inputs | ls-remote: checkout v7.0.1 = 3d3c42e5; setup-java v6.1.0 = b843ebf9; gradle/actions v6.4.0^{} = 3f5f9ada (annotated tag b9bee63 peeled). At the pinned SHAs all three run on node24, setup-gradle has the `cache-provider` input, and the wrapper jar sha256 91a23940...8b1e60 is listed in wrapper-checksums.json (7 hits). gradlew is i/lf, mode 100755. YAML parses; actionlint is not installed | CONFIRMED | - |
| 6 | relative markdown links in new or changed files resolve | 64 links checked across the 9 files, 0 bad; every target is tracked or is one of the 3 new READMEs | CONFIRMED | - |
| 7 | banners preserve line numbers | each is a pure suffix appended to line 1; line counts stay 113/112/1617/38; `git diff --numstat` gives 1 1 each. The records' line citations (IMPLEMENTATION L36-L38, L103) are unaffected | CONFIRMED | - |
| 8 | docs/README.md keeps the cited sha256 lines at L81-L82 | identical bytes at L81-L82 on main and in the draft. Cited by review 2026-09-20 L65 and L120. No other record cites a TaxoArena README by line: the reviews' "README Lnn" hits are benchzoom's README | CONFIRMED | - |
| 9 | README numbers match their ledger rows and JSONs | 85 checked strings (numbers and key phrases) across 11 rows; all present in the row or its results JSON, with context spot-checked (C1_G, C3_K12/K37 "13 categories", U1/U2/U3b/F-AK 0.0002, RWS 183 vs 123, ROUTER-REGRET +0.000/-0.002 +-0.007 over 3,130, CS1 denominator, C2_R, HX1 -0.0473 / 15.0, F6 -1.534e-3 [-2.230, -0.826], CERT 53 of 70). `run.calls` is 0 in all 10 JSONs | CONFIRMED | - |
| 10 | programme spans _as_of 70c61579 | 70c61579 is an ancestor of main. Central question and SQ1-SQ5 are verbatim at L21446-L21447. L21449 rule, L21486, L21500 "the judged half of SQ2 is OPEN", L21453 (6) and L25108 all present | CONFIRMED | - |
| 11 | plan 3a(6) / B2: the README makes no replication claim | README L270 "Clean-clone replication of the frozen construction was verified on 2026-08-02" | REFUTED | MED |
| 12 | texts follow the author's decisions | D-2026-10-27-6 A1 (drafted r8 paragraph), A5 (MIT) and defaults A6 / A8 are not applied (the drafts predate 9b78ace1) | REFUTED | HIGH |
| 13 | split words (S3) | docs/README L64 "the frozen tree's held-out split" has no CK-CLOSE check | PARTLY | MED |
| 14 | no secrets, GPQA text or raw outputs in new text | none found by grep (keys/tokens, question text, the blog, benchzoom, HF, BZ-). .env.example has empty values only. Local absolute E:/ paths appear in 2 source comments (E8) | CONFIRMED (E8 LOW) | LOW |
| 15 | replication inputs intact; no writes | report/: 0 references to any changed path. Worktree `status --porcelain --ignored`: tracked and untracked identical before and after (only an ignored -shm/-wal leftover vanished). Main-checkout *.db: mtimes and sizes unchanged (22 files) | CONFIRMED | - |

Support / DEFF: not applicable (no test, no registration; the plan says so in its header).

## Defects and fixes

- **E1 HIGH (C4).** The History slot (README L211-L215) still holds option (c). D-2026-10-27-6 A1 chose the rev2 L270 paragraph with
  its [CORRECTED 2026-09-27] fix ("its CELL rubrics"). Fix: put that paragraph in verbatim, fix applied, and nothing else reworded
  ("this thesis" included: the words are the author's). Keep L21449 as the source comment.
- **E2 HIGH (C4).** README L295-L298 say "There is no licence file". A5 is MIT. Fix: add a root `LICENSE` with the MIT text and
  the author's name as copyright holder. Change the section to "MIT (see LICENSE); the thesis text in report/ is all rights
  reserved" (the wording of D-2026-10-27-6 A5).
- **E3 MEDIUM (C4).** README L270 makes a replication claim, which plan 3a(6) and the B2 check forbid. It also misleads: the 2026-08-02
  replication needed the two local caches, which are not in git, and it is r8-era. Fix: delete L270. docs/README section 9 keeps
  the dated, scoped statement.
- **E4 MEDIUM (C4).** A6 default is the plan's neutral line, but README L227 shows only "the thesis sources (LaTeX), author-owned"; the
  caveat is in a comment. Fix: make the row read "the thesis sources (LaTeX), the author's. Its 'certified fixed point' sentences
  hold for the frozen artefact 20260727_042523 only, not for the tree of record bareq512_s42 (prog L20860(e)). Rewriting it is
  the author's alone (prog L21453)".
- **E5 MEDIUM (C3).** A8 default: early-campaign docs carry the [P-FAM] history label in the docs index. docs/README section 7 has none.
  Fix: label section 7 (heading or rows) "[P-FAM] history (docs/reviews/RULING_w0_p2dca_family.md)", without quoting a number.
- **E6 MEDIUM (C3).** docs/README L64: replace "the frozen tree's held-out split" with "the frozen tree's reserved split
  (p8a29d8f3ff75aa55)" (incident doc L5).
- **E7 LOW (C4).** README L200 says "the judged stage stopped at its 26-model roster". The record says LCB-STAGE0 F1 FIRED (STOP) at
  that roster and recipe, and the judged stage is not registered on LCB (CONTEXT section 5 L53). Fix that clause to match.
- **E8 LOW (C3/C4).** Two source comments cite local scratch files: README L261 (E:/.../builder/logs/worktree_test.log) and
  experiment_results/README L17 (E:/.../steward_inv/inventory.tsv). Both are public files, and the sources cannot be checked from
  the repository. Fix: cite this review (claim 3) or the record, or drop.
- **E9 LOW (C3).** The docs/README L3 comment says A2 is undecided, but D-2026-10-27-6 decided it (the record goes in as is; docs/drafts stays
  out). Fix: update the comment. Whether docs/registrations/*_DRAFT.md (BZ-* only) are listed falls under A9 (default: no).
- **E10 LOW (timing).** README L254 and the ci.yml L2 comment describe the state before A7. When the A7 test guard merges (its own
  review), update both.
- **E11 LOW (C3).** experiment_configs/README gives "3,492 EVAL items" and "6,153". The pin files' `counts.eval` say 3,586 and 6,466. The record
  numbers are key-complete counts (V2-DECLARED-CELLS "leg M key-complete of 3,492"). Fix: write "3,492 key-complete EVAL items"
  (same for 6,153, per KNOWLEDGE section 1), or name the pin count beside it.
- **E12 LOW (C2, no action).** `filter: blob:none` is redundant: checkout sets it itself when sparse-checkout is given
  (git-source-provider.ts L182-L185). It is harmless.

## Conditions on the downstream snapshot (D-2026-10-27-4; not defects of this branch)

- S1: keep `gradle/wrapper/gradle-wrapper.jar`. A binary-exclusion rule "and similar" must not sweep up `.jar`: ./gradlew and
  wrapper-validation both need it.
- S2: the Layout table and indexes name files the snapshot drops (snapshots_frozen.db, judge_solve/grok-reasoning.db, the cache
  DBs in docs/README section 9). Re-run the link and path check (claim 6) on the snapshot tree.
- S3: C2 is shown only by a Windows proxy. The first hosted run on ubuntu-latest decides.

## Mutants (evidence tools; no deciding code path in the delta beyond CI, which the stand-in executed)

| id | change | result | decisive |
|---|---|---|---|
| M1 | link checker: README link tools/README.md -> tools/READMEX.md | killed (1 bad) | yes (claim 6) |
| M2 | link checker: link to the ignored `.env` instead of `.env.example` | killed (1 bad; untracked target) | yes (claim 6) |
| M3 | number check: CS1 0.9447 -> 0.9448 | killed (absent from CELL-STRATA-EVAL.json) | yes (claim 9) |

## Pins of the reviewed objects (blob = `git hash-object`, LF rendering as committed; core.autocrlf=true; the 4 bannered files are CRLF in the worktree, so their CRLF renderings differ)

- ci.yml at 3d4e2843: blob:ee084e5b94678740c19b9cf913380621f8e5ca74 (sha256-lf16:37f29bc0908d9898; 0 CR, LF in the worktree too).
- C3 drafts: docs/README.md 2268a8bd37c9; experiment_results/README.md 8d196432d264; experiment_configs/README.md c95a6e024a44;
  tools/README.md fc1acfd9a016; docs/IMPLEMENTATION.md 9f00c2bbaf0d; docs/RESULTS.md ef4581d9b791; docs/test_catalogue.md
  0f6ac3fc9c68; experiment_results/r8/README.md 7e59ccc18872. C4 draft: README.md 146fb22fffbe.
- C3 acceptance: `git rev-parse <C3>:<path>` equals the blob above for each file not touched by E5/E6/E8/E9/E11. The edited
  files get a delta check of the changed lines only.

## Commands (compact)

```
git diff --name-status main...repo-tidy ; git diff --name-only [main...repo-tidy] -- report config .gitignore .env docs/agents docs/reviews docs/judge_v2_program.md docs/test_ledger*.html docs/registrations | wc -l   # 0 / 0
rg -i --no-ignore --hidden -g '!.git' -g '!.claude/worktrees/**' -g '!*.db' -c -e dockerfile -e 'mcp.server' -e 'plot.results' -e my_mcp .   # main checkout; same over benchzoom and memory
git for-each-ref refs/heads | while read r; do git grep -l -i -e dockerfile -e mcp-server -e mcp_server -e plot_results "$r"; done | sort | uniq -c   # 181 tips
powershell: .\gradlew.bat compileKotlin compileTestKotlin test --offline --max-workers=6   # "569 tests completed, 2 failed"
git clone --depth 1 --sparse --branch repo-tidy file:///.../TaxoArena repo; git sparse-checkout set --cone src gradle; GRADLE_USER_HOME=<empty> gradlew.bat --no-daemon --max-workers=6 -Dmaven.repo.local=<empty> compileKotlin compileTestKotlin   # E:/TaxoArena_tmp/tidy/review/ci/ci_standin.log
git ls-remote https://github.com/{actions/checkout,actions/setup-java,gradle/actions} refs/tags/<tag> refs/tags/<tag>^{} ; curl raw action.yml / git-source-provider.ts / wrapper-checksums.json at the pinned SHAs
python links.py (64 links, 0 bad) ; python claims.py main (ledger rows by <td class="id">, html-unescaped, plus results JSON) ; python banner check (suffix-append, line counts)
git status --porcelain --ignored | sort  (before/after diff) ; ls --time-style=full-iso TaxoArena/*.db (before/after diff)
git merge-tree --write-tree main repo-tidy   # clean
```

## Delta review 2026-10-27: repo-tidy 3d4e2843..57b1d2b7 (C3 5c3b2bdf, C4 ea110342, A7 c1d975f0, C3 follow-up 57b1d2b7) against main adbad427

Insertion only; the sections above are unchanged. Zero LLM calls. Delta = 13 files, +608/-105. The C3/C4 drafts' blobs
(above) were never written to the object store (`git cat-file -t 2268a8bd37c9` etc.: not valid objects), so the edited
files were re-checked whole, not as a line diff. Unedited C3 files: tools/README.md and the 4 bannered files equal the
reviewed draft pins at every one of the 4 commits (`git rev-parse <c>:<path>`).

### Verdict

| unit | verdict |
|---|---|
| C3 5c3b2bdf + 57b1d2b7 | **MERGEABLE** (E5, E6, E8, E9, E11 applied) |
| C4 ea110342 (+ README L257 in c1d975f0) | **MERGEABLE** (E1-E4, E7, E8 applied; E10 applied with A7) |
| A7 c1d975f0 | **MERGEABLE** (both tests skip without local data and run with it; clean clone 0 failed) |

merge_ok: yes, the whole branch (C1-C4 + A7). `git merge-tree --write-tree main repo-tidy` is clean (tree a936324a); main moved only by
this file since the first review. No blocker. N1-N2 are LOW and are not merge conditions. Downstream conditions S1-S3 (above) still apply to the snapshot.

### Per-claim table (delta)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| D-1 | E1: History = rev2 L270 verbatim with only "its anchor rubrics" -> "its cell rubrics" | script: README L214 == the rev2 L270 quote with that one replace (exact string equality, True); the only prose line between `## History` and `## Layout`; source comment keeps L21449 | CONFIRMED | - |
| D-2 | E2: LICENSE is standard MIT; README licence excludes report/ | LICENSE == choosealicense.com `_licenses/mit.txt` body with [year]=2026, [fullname]=0ctave (byte-equal after the fill); README L304-L307 "MIT ... The exception is the thesis text in `report/`, which is all rights reserved" | CONFIRMED | (N1 LOW) |
| D-3 | E3: no replication claim remains | whole-README grep replicat/reproduc/determinis: L88 "a sensitivity, not a replication", L214 (the author's paragraph), 2 comment lines; no claim. docs/README section 9 keeps the dated 2026-08-02 statement (as E3 allowed) | CONFIRMED | - |
| D-4 | E4: report/ row is the plan's neutral line | README L230 = plan 3a item 4 wording (the author's; "certified fixed point" true of 20260727_042523 only, prog L20860(e); rewrite the author's alone, L21453), visible text | CONFIRMED | - |
| D-5 | E5 / E6 | docs/README L60 heading "7. Campaign history: [P-FAM] history (RULING_w0_p2dca_family.md)", no number; L64 "reserved split (p8a29d8f3ff75aa55)" | CONFIRMED | - |
| D-6 | E7: LCB clause | README L202 matches CONTEXT section 5 L53 [ADDED 2026-09-25] (F1 FIRED (STOP) at the 26-model roster and tree recipe; judged stage not registered on LCB; closes nothing elsewhere; power unverified) | CONFIRMED | - |
| D-7 | E8: local paths gone | `[A-Za-z]:/` in the whole of README, docs/README and the 3 directory READMEs: 0 each; in the 641 added lines of main...repo-tidy: 0 (secret patterns also 0) | CONFIRMED | - |
| D-8 | E9 (+ A9 default) | docs/README L3 comment records A2 as decided; docs/registrations/*_DRAFT.md (2 files) unlisted | CONFIRMED | - |
| D-9 | E10 | README L257 (skipped, not failed, without the local data) and ci.yml L2 (the sparse checkout lacks tracked files) | CONFIRMED | - |
| D-10 | E11 | experiment_configs/README L20-L21 and README L63 give the record's counts 3,492 / 6,153 (prog L16198) with the pin `counts.eval` beside them: 3586 / 6466 (read from both engine_pool_*.json). prog L21881: key-complete 3,351 / 3,350 of 3,492, so E11's first option ("3,492 key-complete") was WRONG and the builder was right to take the second | CONFIRMED | - |
| D-11 | no BZ / benchzoom / blog / HF mention | `\bBZ[-_]`, `benchzoom`, `\bblog`, `hugging ?face`, `\bHF\b` (-i): 0 of 641 added lines; whole README 0 | CONFIRMED | - |
| D-12 | banners keep line counts | 4 files: line-1 suffix only, lines 2..n byte-equal to main, 113/112/1617/38, numstat 1 1 each; docs/README L81-L82 byte-equal to main | CONFIRMED | - |
| D-13 | relative links resolve | own checker over the 9 added/modified .md files: 65 links, 0 bad (targets tracked at the tip, file or directory) | CONFIRMED | - |
| D-14 | README numbers still match the record (spot check: the draft cannot be diffed) | 136 numeric tokens in "Where the record stands", each found in its bullet's ledger row (html-unescaped) or results JSON: 0 absent | CONFIRMED | - |
| D-15 | A7 without local data: skip, not fail, not silent pass | own clone (`--no-local`; committed application.yml without the key; no data DB; `--no-build-cache`; 10/10 tasks executed): **569 tests, 0 failures, 0 errors, 2 skipped** (JUnit XML: exactly MrlRoutingTest.testMrlConfigDefaults and the blank-trace test). Trace test alone with no DB file: SKIPPED (mutant D1 turns it into a silent pass) | CONFIRMED | - |
| D-16 | A7 with local data: the checks still run | key set by env `TAXOADAPT_FORMALISM_PROPOSALSEPARATIONBAR` (independent of the builder's SPRING_APPLICATION_JSON): 0.02 passed, 0.03 FAILED "expected <0.02> but was <0.03>". Fixture DB on the engine's stub schema: pass -> passed; recovered (deepseek traced) -> FAILED; new blank model -> FAILED; 0 rows -> SKIPPED | CONFIRMED | - |
| D-17 | guard code (read) | Mrl: skip keyed on the PRESENCE of `taxoadapt.formalism.proposal-separation-bar`, not on its value; the judge/labeling asserts run before it on every checkout. Trace: `evalRowCount()` checks the file exists before opening it with `open_mode=1` (read-only, never creates it), returns null if the table is missing; the query and both assertions after the assumption are unchanged | CONFIRMED | - |
| D-18 | nothing author-owned or insertion-only touched | `git diff --name-status main...repo-tidy` = 18 paths (wc -l); the same diff restricted to report, config, .gitignore, .env, docs/agents, docs/reviews, programme, ledger, docs/registrations, plan: 0 | CONFIRMED | - |
| D-19 | commit hygiene | 4 commits touching 8/2/4/1 files, each with the attribution trailer; 3d4e2843 is an ancestor of the tip | CONFIRMED | - |

Support / DEFF: not applicable (no test, no registration).

### Defects

- **N1 LOW (C4, the author's option).** LICENSE L3 names the copyright holder by the git handle "0ctave", and D-2026-10-27-6 A5 names no holder. If the author
  wants a legal name, change that one line. The report/ exception lives only in the README, as A5 says, so a reader of LICENSE alone sees no exception. No action unless the author asks.
- **N2 LOW (pre-existing; disclosed by the builder; not a merge condition).** TraceEnvelopeUnwrapTest's two sibling DB tests (`no ingested trace
  carries a reason_code field`, `no ingested trace is a raw JSON envelope`) `?: return` when the file is absent and pass on the empty stub. On a clean
  checkout they are 2 PASSED that checked nothing, and README L257's "the rest of the suite passes" counts them. Fix (own commit, delta check): put
  `assumeTrue((evalRowCount() ?: 0L) > 0L, ...)` first in both. The clean-checkout skip count becomes 4 and README L257 changes to match.
- Correction to E11 above (insertion): its first option ("3,492 key-complete EVAL items") was wrong. 3,492 is the item count; key-complete is 3,351 / 3,350 (prog L21881).
- Harness note (not a defect): in a run that includes MrlRoutingTest, the Spring context recreates the empty stub DB before the trace test runs. The "file
  absent" state is therefore reachable only when the trace test runs alone: D1 survived the combined run and was killed in a trace-only run.

### Mutants (sandbox clone E:/TaxoArena_tmp/tidy/review-delta/repo only; restored; matrix Mrl (no key, 0.02, 0.03) / Trace (empty, pass, recovered); original = SKIPPED, passed, FAILED for both)

| id | change | result | decisive |
|---|---|---|---|
| MA1-MA4 (builder's, re-run) | Mrl guard true / inverted / false / old key separation-epsilon | killed 4/4 (MA1, MA4: no key -> FAILED "was <0.04>"; MA2: no key FAILED and 0.02 SKIPPED; MA3: 0.02 SKIPPED) | yes |
| MB1-MB4 (builder's, re-run) | Trace guard true / rows >= 0 / false / table-name typo | killed 4/4 (MB1, MB2: empty -> FAILED; MB3, MB4: pass -> SKIPPED) | yes |
| D1 | Trace guard `rows != null && rows > 0L` -> `rows != 0L` (null passes) | killed in the trace-only run with no file (orig SKIPPED, D1 passed); survived the combined run (see the harness note) | yes (skip, not silent pass) |
| D3 | link checker: docs/README `(reviews/RULING...)` -> `(review/RULING...)` | killed (1 bad) | yes (D-13) |
| D4 | number check: 0.9447 -> 0.9448; +0.14 -> +0.15 | killed (1 absent each) | yes (D-14) |

### Pins of the delta (blob = `git hash-object`, LF as committed; lf16 = sha256-lf16 of `git show 57b1d2b7:<path>`; crlf16 = the worktree's CRLF rendering)

README.md blob:f2b775a557a177dd29ec9b979be1024cfae9134c lf16:84957541b20c0381 · LICENSE blob:1b0e8e0d20744a070cc081cdfff828f81840e4bf lf16:606ff9212bd7c733 ·
docs/README.md blob:5ce5b6bde4676edd55f709875e6abb31e40241a3 lf16:79a7ce9e64a2bba4 · experiment_results/README.md blob:71e957eedfdfa1642d6adba575b7b026a920c034 lf16:18ff9dd47d842254 ·
experiment_configs/README.md blob:4f6cb847cd2d27d7fb067526c6133904381aeac7 lf16:f51340b0bd389098 · tools/README.md blob:fc1acfd9a016bdd5f67474c94482c99e1c8cf520 lf16:68e82f4733ef9fae ·
ci.yml blob:5b2336c90936c20de5b9c33ac7a4ef721a8164fe lf16:4b7a8aa176c4d117 (these 7 are LF in the worktree too) ·
MrlRoutingTest.kt blob:8200fdca143af24c800c7d51f6bee5fab2fafbe4 lf16:d847580681aa7e83 crlf16:8a441267ea267482 ·
TraceEnvelopeUnwrapTest.kt blob:964aec17e3220078b33c096312f2de5a617cbe5f lf16:fd6daad861ffadcb crlf16:d502f57fe8e866e5 ·
banners (= the draft pins above): IMPLEMENTATION 9f00c2bbaf0d lf16:5e7367cd6a88cd1c crlf16:333039288c8f4429; RESULTS ef4581d9b791 lf16:b11bdac02e567a4f
crlf16:d7b2b172327a73e8; test_catalogue 0f6ac3fc9c68 lf16:c5f8cb6f7c3f627d crlf16:402db49e474fa0b2; r8/README 7e59ccc18872 lf16:a486dfedd136cd6c crlf16:52711aee45606d12.

### Commands (compact)

```
git diff --stat 3d4e2843..57b1d2b7 ; git diff --name-status main...repo-tidy | wc -l   # 13 files / 18 paths
git diff --name-only main...repo-tidy -- report config .gitignore .env docs/agents docs/reviews docs/judge_v2_program.md 'docs/test_ledger*.html' docs/registrations docs/plan_2026-09-15.md | wc -l   # 0
for c in 5c3b2bdf ea110342 c1d975f0 57b1d2b7: git rev-parse $c:<path> vs the draft pins ; git cat-file -t 2268a8bd37c9   # not an object
python e1.py (rev2 L270 quote .replace('its anchor rubrics','its cell rubrics') == README History line) ; curl choosealicense mit.txt, fill, compare
python links.py repo-tidy [mutant]  # 65 / 0 bad ; python nums.py repo-tidy [MUT=a|b]  # 136 tokens / 0 absent ; python ban.py  # suffix-only, counts, L81-L82
git diff main...repo-tidy -U0 | grep '^+' | grep -v '^+++' | grep -c -i -E '\bBZ[-_]|benchzoom|\bblog|hugging ?face|\bHF\b'   # 0 (641 added lines)
git clone --no-local --branch repo-tidy file:///Z:/.../TaxoArena E:/TaxoArena_tmp/tidy/review-delta/repo ; gradlew.bat --no-build-cache --max-workers=4 --offline compileKotlin compileTestKotlin test   # 569 / 0 F / 0 E / 2 skipped (XML)
python -I E:/TaxoArena_tmp/tidy/review-delta/mut.py orig D1 MA1 ... MB4   # E:/TaxoArena_tmp/tidy/review-delta/mutants.txt, mutants_traceonly.txt
git merge-tree --write-tree main repo-tidy   # clean, a936324a
```
