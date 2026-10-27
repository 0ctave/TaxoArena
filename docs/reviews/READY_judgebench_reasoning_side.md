# DELTA-2 READY 2026-09-25: JUDGEBENCH-REASONING-SIDE, 85a2d9f (on 20a6462)

Reviewer: adversarial-reviewer. Zero calls, read-only, nothing posted; no --go, no pilot, no analysis on real caches. This section is inserted above the earlier ones; nothing below it is changed.

Only tools/analysis/judgebench_side.py changed: `git diff --name-only 20a6462 85a2d9f` lists 1 path.

## VERDICT (delta-2)

**READY for posting at 350, 250 and 150.** At 150, C1 and P3 are DESCRIPTIVE-ONLY by design (D2).

Posting still awaits:
- the author's size choice, recorded by the registrar;
- the post-pilot merge (procedure in the first review; the runner is now blob e8faa08b);
- the launch conditions below.

D11 is closed: every fix was verified by running it. No finding at or above MEDIUM remains in the code.

## Per-fix table

| item | result | command / evidence | got |
|---|---|---|---|
| D11 (a) sentinels | FIXED, CONFIRMED | re-ran my probe: `JBSIDE_SELFTEST_MUTANT=size_gate_open python tools/analysis/judgebench_side.py --selftest-one` | `[FAIL] --analyze --go is REFUSED by its gate (SENTINEL: main() reached the real analyze)`, and the same for pilot_report. The real functions no longer execute; before this commit they reached ROOT ("...judgebench_side_G_v1.db not found"). |
| D11 (b) refuse_mutant_on_root | FIXED, CONFIRMED | the first statement of analyze() (L1319) and pilot_report() (L1295); the selftest probe with MUTANT = "probe" | Both refuse with "JBSIDE_SELFTEST_MUTANT='probe' ... repo root". The probe's out_dir and ledger_dir are temporary, so even a broken guard writes nothing real. |
| D11 (c) mutant both_gate_open | KILLED | battery | "SENTINEL: main() reached the real arm_main" (FAIL lines) |
| My mutant S: sentinels installed, never restored (`G_.update(real_eps)` -> `pass`) | DETECTED (crash, rc 1) | copy in scratch, `--selftest-one` | `RuntimeError: SENTINEL: main() reached the real analyze` at the D11 (b) probe. Stale sentinels fail SAFE (they raise, never execute). The battery's kill rule (rc != 0 AND a "[FAIL]" line) would call a crash-only mutant SURVIVED, which is conservative (D14, INFO). |
| My mutant R: refuse_mutant_on_root disabled (`if False:`) | KILLED | copy in scratch | 2 FAIL lines ("--analyze / --pilot-report with a mutant set refuses the repo root") |
| My mutant C: the CEILING row without `day=` (now in record_ceiling) | KILLED (was surviving) | copy in scratch | 3 FAIL lines, including "the 0-call CEILING row sits on the LAUNCH day's ledger (READY D12)" |
| D13 rollover exit | FIXED, CONFIRMED | selftest check + code (`_after_launch` L1173-L1179: the rollover branch comes before the pilot-guard refusal) | exit 6, "STOPPED AT DATE ROLLOVER ... relaunch the same command to resume" |
| No selftest path reaches arm_main / both_main / analyze / pilot_report on ROOT | CONFIRMED | every call in selftest() listed by grep | The e2e analyze / pilot_report calls use a temporary root. The only `main(argv)` calls are in section 14, under sentinels. The D11 (b) probe calls analyze / pilot_report on ROOT deliberately, and refuse_mutant_on_root stops it first (mutant R proves it is killed). The mutant-battery children run the same code. The --emit-anchor child opens no DB and posts nothing. |
| Selftest | CONFIRMED | `python [-O] tools/analysis/judgebench_side.py --selftest` | 92 `[ok]` (85 checks + 7 mutant lines), 0 FAIL, rc 0, in both modes; 7 of 7 KILLED |
| Ingest | CONFIRMED | python and -O | 0 failures |
| lint 0 | UNDETERMINED | pyflakes and ruff are not installed | — |
| Dry-run anchors | CONFIRMED | `--arm both --size N --dry-run` at 85a2d9f for N = 350/250/150; 13 keys per size diffed against the e5cac52 transcripts | 0 differing lines at every size; BODY-DIFF OK |
| No real state touched | CONFIRMED | day_calls sha256 before and after all runs; `ls` | ledgers unchanged; no judgebench_side_*_v1.db at the root; experiment_results/judgebench_side/ holds only ingest_manifest.json |

## Remaining LOW / INFO (none blocks)

- D4(b): both_gate is a mistake-guard that can be spoofed deliberately. Launch only with `--arm both`.
- D7: C0(e)'s 1,540 label at every size (the arm caps bind at 770 / 550 / 330).
- D9: accepted_tests_ledger has no lock across different tests (pre-existing).
- D14: crash-only mutants read SURVIVED in the battery.
- lint: unverified here.

## FINAL PINS for the registrar

| file | blob (LF, rendering of record) | sha256-lf16 | sha256-crlf16 (main's working tree, autocrlf) |
|---|---|---|---|
| tools/analysis/judgebench_side.py @85a2d9f | blob:e8faa08b7d2c7837e22c9fe2b4d8f900dd5caa61 | ed9aac5877e741cf | 3a34350bb02c0c1c |
| tools/ingest/judgebench_ingest.py | blob:a2b0878fe75a00720095cebd72a8bf791a7d0a83 | eeb4286b619ab6bc | 2a28f3f0b5d26075 |
| experiment_results/judgebench_side/ingest_manifest.json | blob:87c59f86394a4cb44ec4ed56c8564d5a12264bb4 | b00cb01492e301dd | 392a59d961aa379f |
| tools/analysis/accepted_tests_ledger.py (3-WAY MERGE of main a4a1d7ee + the JB hunk; never path-restored) | blob:fabb66a8b3d73a3c31053170145c3be7b8e54975 | e5f942de85da83d5 | 9875b083df114b29 |

Other pins:
- **Corpus DB** judgebench_corpus_v1.db:
  - file sha256 a2ca40b8d4b06126c8b61f6d1f2c2c5a2cd65ad844b542599dedf79efcf2f498;
  - pairs table eee0193c4abf8f0003d319a9e7a04f3ba5a641d6498b4ea75d1832d9ab9b2064 (620 rows);
  - meta table 41f2bf1d86e6e3e5b2208d8d23f01b428c9386a4450606e84fb36d44461db0cf (15 rows).
- **SYSTEM** 3760f9882264b9705154057c550a0bec1c05de56edb820283756b61c063981da.
- **Payload anchor**, pair 58d81545-6e2e-5388-b1b7-05ec20157459, order 1: G 742b02ecf235180805e921651dac2030c795e5d70a26b3549dffd8b4f2f7793d / S1 b536f9fd1eca82157f8d0b3929f6b85ccc9efe9fff725f3069d39cf8813bfdf9.
- **Schedule set**, 350 / 250 / 150: b9e4a23bc5710d2e840c0841e0ed97636c77580a8949dceb4d3ec9c6786654cc / c8765672d9de90c8ba1b3248b8b298ae5115894487c802295e25d3dcf12cf1b8 / dbc0ea2837e94534ce48fbe3d01ae24cccbee84b8865727607c31f804cb24849.
- **Pilot set** 2bee205c6d63ac75fdc901a5b33c04ec19c8c43564f22a8c9134c6b084fe66c7.
- **Payload sets**, G / S1:
  - 350: 832e54a9c9a32a4541e49c6d93433735c0992406d5e443edf5227b1c02efa1a0 / 1806a6bee90883bdaf67d632810d0ad285fc8ec2af0f3dc9fbe8258cbfb7707b;
  - 250: a3b2c955264eaf709f1351a511f2195ea79045dd2985fe217e70128b04f8f327 / 54987d1c89e3d0118831faa6bd1222b7052b40b1f266199ff7ed50d551c833b5;
  - 150: 0848879ea96d9af169acdc11695035937e52e29d8ef90027367e507a7954ab0d / 4f4df2bfc6a6759bb377fcafb761657a70f8fe9647e492a55bc4718cf9cb7449.
- **rr.payload_body source** 907366e47c3f5ce98b2a6e0d59284ba35bc586b59fb7699916c3280bdda554d9.

## Launch conditions (binding)

1. The author's size is recorded by the registrar (350 / 250 / 150; at 150, C1 and P3 are descriptive-only).
2. Merge after the ARCH-V2-PILOT-K46 run of record, per the first review's procedure, with the runner at blob e8faa08b and the ledger module by 3-way merge (fabb66a8). Then:
   - re-run on main, under python and -O: induce_run_3_selftest, both JB selftests (expect 92 ok / 7 of 7 killed; 15 ok);
   - rebuild the corpus DB on main and check a2ca40b8 / eee0193c;
   - run the dry-run on main at the chosen size and check it prints the anchors above.
3. Post on a fresh day, after the pilot's last post, with no K46 row that day.
4. Launch only with `--arm both`. A rollover exit 6 is resumed by relaunching the same command.
5. Registrar brackets before the pilot: the P4b Shapley formula; the P9b measured base rate; D5 (the corpus DB is an EXCLUDED input).
6. Back up the corpus DB and both caches to the E: manifest after the run.

---

# DELTA READY 2026-09-25: JUDGEBENCH-REASONING-SIDE fixes, 59f51f5 + 20a6462 (on e5cac52)

Reviewer: adversarial-reviewer. Zero judge calls, read-only. No --go, no pilot, no analysis on real caches. This section is inserted above the first review; nothing below it is changed.

Only tools/analysis/judgebench_side.py changed: `git diff --name-only e5cac52 20a6462 | wc -l` = 1.

## VERDICT (delta)

**NOT READY for posting at 350, 250 or 150, because of one new defect, D11 (HIGH).**

- D1, D2, D3 and D6 are fixed and verified by execution. D4(b) is accepted as a mistake-guard.
- D11: the new selftest section 14 calls the real `main()`. The mutant battery then runs, in its size_gate_open child, the REAL `analyze()` and `pilot_report()` on the real repo root. Today they refuse only because the real caches do not exist yet. Once the caches exist, a routine `--selftest` would write judgebench_side_outcome.txt, the write-once outcome of record, from a mutant process. Also, the base selftest's `--arm G --go` case is kept away from the real posting path (arm_main: real ledger rows, load_env, posts) only by `both_gate`, so a later edit that breaks the gate turns the selftest into a real launch.
- The fix must land BEFORE the pilot: `cache_meta` pins `script_blob`, so any code change after the first cache row refuses every relaunch.

With D11 fixed, the selftests re-run under python and -O, and the dry-run shas unchanged, the build is **READY at 350 and 250, and at 150 (now correctly DESCRIPTIVE-ONLY for C1)**. Posting still awaits:
- the author's size choice, recorded by the registrar;
- the post-pilot merge (procedure below, with the new blob).

## Per-fix table

| item | result | command / evidence | got |
|---|---|---|---|
| D1 midnight | FIXED, CONFIRMED | My own scenario (scratch; post_jobs with a fake call, **4 workers**, the date flips after the 7th completed post; then reconcile and a relaunch on the new day) | Launch 1: rolled_over True, 10 posts (7 completed + 3 in flight, all journaled AND ledgered on 2026-10-01). Reconcile clean. Launch 2: 30 posts on 2026-10-02. Journal {10-01: 10, 10-02: 30} = ledger {10-01: 10, 10-02: 30} = 40 posts = PostCounter 40. No spurious row, no refusal. |
| D1, my mutants (copies in scratch, `--selftest-one`) | 2 of 3 KILLED; the survivor is harmless | A: finish_launch appends with no `day=`. B: the rollover check removed (`if False:`). C: the 0-call CEILING row appended with no `day=` | A KILLED (2 FAIL: "ledger {'2026-09-25': 3}" vs journal 01-05; "ledgers 11 vs journal 8"). B KILLED (3 FAIL). C SURVIVES, but that row carries 0 calls, so no count, equality or cap moves (LOW, D12). |
| D1, the builder's mutant day_rollover_unguarded | KILLED | battery | 2 FAIL lines |
| D2 at 150 | FIXED, CONFIRMED | selftest section (a synthetic +55pp gain at N 150) + code read, render L678-L689 and L744-L748 | C1.DESCRIPTIVE_ONLY and P3.NOT_SCORED are hit; no C1 verdict and no P3 HELD/FAILED; F1 still scored ("JOINED RECORD: C1 DESCRIPTIVE-ONLY (N 150) / F1 ..."). |
| D3 MDE labels | FIXED, CONFIRMED | selftest string checks + code | C1 8.4 / 10.0 / 12.9pp by size. Interaction: 17.5pp registered at 350; at other sizes the registration's formula, labelled planning. |
| D6 | FIXED, CONFIRMED | selftest: `--analyze --go` and `--pilot-report --go` refused ("--go is only for a posting launch") | ok |
| D4(b) both_gate | ACCEPTED as a MISTAKE-GUARD, not a security boundary (LOW) | A 3-line wrapper that sets `JBSIDE_BOTH_PARENT=str(os.getpid())` and spawns a child calling `both_gate("S1", True, True)` | The child is ADMITTED. With a wrong pid it is refused. From a shell, `$env:JBSIDE_BOTH_PARENT=$PID` before `python ... --arm S1 --go --from-both` also passes. Spoofing takes a hidden flag plus a hand-set env var, so it cannot happen by accident; that is the goal of D4(b). Keep the launch condition "only `--arm both`". |
| D7 | stays LOW | code | The per-arm caps are enforced three times (journal trigger `arm_cap`, PostCounter cap, atl (i)): ceil(2.2N) = 770 / 550 / 330 per arm, so a size-250 run cannot pass 1,100 whatever C0(e)'s 1,540 label says. The label is cosmetic. Fix at leisure. |
| Dry-run shas unchanged | CONFIRMED | `--arm both --size N --dry-run` for N = 350/250/150 at 20a6462; 13 anchor keys per size (SYSTEM, anchors, schedule / pilot / payload sets, payload_body source, BODY-DIFF) extracted and diffed against the e5cac52 transcripts | diff = 0 lines at every size; BODY-DIFF OK. |
| Selftest 80 checks + 6 mutants, python and -O | CONFIRMED | `--selftest` at 20a6462 | 86 `[ok]` (80 + 6 mutant lines), 0 FAIL, rc 0, in both modes; 6 of 6 KILLED. |
| Ingest 15/15 | CONFIRMED | unchanged file; re-run | 0 failures |
| lint 0 | UNDETERMINED | pyflakes and ruff are not installed | — |
| No real state touched by the selftests | CONFIRMED today | day_calls sha before and after = 8b96846e...; no judgebench_side_*_v1.db at the root; experiment_results/judgebench_side/ still holds only ingest_manifest.json | — |

## New defects

**D11 (HIGH): the selftest reaches real outputs of record through `main()`.**
- *Evidence:* `JBSIDE_SELFTEST_MUTANT=size_gate_open python tools/analysis/judgebench_side.py --selftest-one` prints `[FAIL] --analyze --go is REFUSED ([JBSIDE] Z:\...\agent-a908...\judgebench_side_G_v1.db not found)`, and the same for `--pilot-report`. So the child passed the size gate and ran the real `analyze()` / `pilot_report()` against ROOT, stopped only by the missing caches.
- *Risk after the run:*
  - analyze() writes the write-once outcome of record from a mutant child, outside the launch sequence;
  - the real `--analyze` then refuses;
  - with incomplete caches it writes the _partial file instead.
- *Latent path to real posts:* the base selftest calls `main(["--arm", "G", "--size", "350", "--go"])`, and only `both_gate` stands between that and the real arm_main posting path. No mutant disables both_gate.
- *Fix:*
  - (a) in section 14, replace `arm_main`, `both_main`, `analyze` and `pilot_report` with a sentinel that raises before calling `main(argv)`, and restore them in `finally`, so a gate failure fails the check instead of executing;
  - (b) make `analyze()` and `pilot_report()` refuse when `MUTANT` is set and `root == ROOT`;
  - (c) add a mutant `both_gate_open`, which must be KILLED by (a);
  - then re-run the selftest under python and -O and re-check the dry-run shas.

**D12 (LOW):** my mutant C (the 0-call CEILING row without `day=`) survives. It is harmless, since no count moves. A one-line check that the CEILING row sits on the launch day would kill it.

**D13 (LOW):** a pilot launch that rolls over returns 3 with "PILOT GUARD INCOMPLETE: the run is refused on this cache" rather than 6. A relaunch of `--pilot` still resumes correctly, so only the message misleads.

## Final pins (provisional: D11's fix will change the runner's blob)

| file | blob (LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/judgebench_side.py @20a6462 | blob:6d46274307eb3e56d4585b7ae7188c15027d29b4 | 832b1fe468e03a93 | 06a239a4931ce53c |
| tools/ingest/judgebench_ingest.py (unchanged) | blob:a2b0878fe75a00720095cebd72a8bf791a7d0a83 | eeb4286b619ab6bc | 2a28f3f0b5d26075 |
| experiment_results/judgebench_side/ingest_manifest.json (unchanged) | blob:87c59f86394a4cb44ec4ed56c8564d5a12264bb4 | b00cb01492e301dd | 392a59d961aa379f |
| tools/analysis/accepted_tests_ledger.py, 3-way merged | blob:fabb66a8b3d73a3c31053170145c3be7b8e54975 | e5f942de85da83d5 | 9875b083df114b29 |

All dry-run anchors in the first review's table stand unchanged: SYSTEM 3760f988..., anchors 742b02ec / b536f9fd, schedule / pilot / payload sets. So do the corpus DB pins (a2ca40b8 / eee0193c / 41f2bf1d). The merge procedure below stands, with the runner taken from the D11-fixed commit.

---

# READY review: JUDGEBENCH-REASONING-SIDE, build e5cac52

Reviewer: adversarial-reviewer, 2026-09-25. Zero judge calls. Read-only on every DB of record. No --go, no pilot, no analysis on real caches.
Registration: docs/judge_v2_program.md L17330-L17533 (6134573), posting gate L17502.
Build: e5cac52 (parent 6134573), branch worktree-agent-a908ab11f8ceee064, not merged. Main is at 31420e9 during this review.

## VERDICT

**NOT READY for posting as built.**

- **D1 (HIGH) blocks every size.** If a launch crosses local midnight, the ledger gets a spurious row that double-counts its posts. The next launch then refuses, and C0(e) fails for good because the day ledger is append-only. I proved this by running it (below).
- **D2 (HIGH) blocks size 150 only.** At N=150 the runner scores C1 and P3, although the registration makes C1 DESCRIPTIVE-ONLY at 150.

Once D1 is fixed, and its selftest check is re-run under python and -O and passes a delta review of those hunks only, the build is **READY at 350 and 250**. That READY is still subject to:
- the author's size choice, recorded by the registrar;
- the post-pilot merge described below.

Size 150 also needs D2 fixed, or a registrar ruling.

Everything else the builder claimed reproduces to the digit.

## Per-claim table

| # | claim | result | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | Source pins = HF revision 57dd5e0b | CONFIRMED | independent `curl` of both files from `.../resolve/57dd5e0b.../data/*.jsonl` into scratch; `sha256sum`; HF API revision endpoint | gpt 1,960,188 B d5106306...6042; claude 920,039 B 3b705045...0a62; API sha 57dd5e0b..., lastModified 2024-10-09T18:10:45Z, license mit. All equal. |
| 2 | Registered counts | CONFIRMED | own parse of the downloaded JSONL (scratch v1.py) | GPT 350 rows, 350 unique questions; K154 R98 M56 C42; A>B 193 / B>A 157; gpt-4o-2024-05-13 x350; longer-correct 161/350 = 0.460 (K .442, R .418, M .518, C .548); 0 length ties; Claude 270 / 269 unique; shared questions 91 (K43 R33 M11 C4). All equal. |
| 3 | Corpus DB = the sources; side labels | CONFIRMED | all 620 DB rows compared field by field against the raw lines (split, source, category, question, both responses, label, model, row sha256, original_id, len_A/len_B, side_v2) | 0 mismatches of 620. Side (own split_side.stem_key lookup in the committed side TSV, 20,544 rows): GPT K EVAL 44 / GATE 18 / TRAIN 92; Claude 41/13/100; all non-knowledge NOT_IN_SPLIT. Equal. |
| 4 | DB byte-deterministic, sha a2ca40b8 | CONFIRMED | ran `build()` from my own download into scratch | file sha256 a2ca40b8d4b0...f498; pairs table eee0193c...2064 (620); meta 41f2bf1d...b0cf (15). Byte-identical to the worktree DB. |
| 5 | Owed (i), knowledge: 151/154 hit MMLU-Pro | CONFIRMED | own 8-token shingling (\w+ casefold, k=8) over mmlu_pro question + options, immutable ro | mmlu-pro-v2 125,673 texts: K151 M2 C2. mc6:MMLU_PRO 126,024: K151 M2 C2 (same 4 non-K pair ids). |
| 6 | Owed (i): a few math/coding shingles | CONFIRMED | same | mc6:MATH 1,324 texts: M5 C1 K3, the same 6 non-K pair ids as the manifest. BBH / GPQA / IFEVAL / MUSR: 0. |
| 7 | Owed (i): 0 hits on INDUCE-1/2 | CONFIRMED (+1) | same, on the rubric texts (sha verified ef9c9e87 / ace41ede) | 0 / 0. I also ran INDUCE-3's rubric of record (9e0a4022, which did not exist at build time): 0 hits. |
| 8 | Owed (ii): the 44 EVAL items are all in pv2_41dbd3dbcd399df0 | PARTLY | manifest; sealed view not re-opened by me; eval_view_REG.db sha256 re-hashed e35b7518...e369 = the manifest | 44 EVAL in_pool / 0 GATE-or-TRAIN in pool. Note D10: membership is keyed by "i:"+stem_key, the same key as the side export. It is a consistency check between two artefacts of one split, not an independent test. |
| 9 | Owed (iii): OPTIONS map, 45 judgeable p2dca, 38 board-of-record | CONFIRMED | own okey over eval_results (Llama-3-70B excluded); pool_guard.eval_ids (3,445); DISTINCT qid of x12all where invalid=0 | x12all qids = 2,811 (9,142 rows); x20's 2,646 qids are a subset (checked), so x12all is the board's judged set. GPT: keyed 154, p2dca 45 (EVAL-side 14), board 38 (EVAL-side 13). Claude: 154 / 37 / 31. Equal. |
| 10 | DBs of record unchanged by the owed pass | CONFIRMED | `sha256sum` now vs the manifest's `reads` | mmlu_pro_dataset_cache_v2 4f65414f... (mtime 09-19); multicorpus_cache_v1 ad66e30a... (09-13); x12all eb0bec27... (09-10); eval_view e35b7518... All equal; -wal 0 bytes. |
| 11 | Runner selftest: 68 checks + 5 mutants, python and -O | CONFIRMED | `python [-O] tools/analysis/judgebench_side.py --selftest` in the worktree | 73 `[ok]` lines, 0 `[FAIL]` (counted by grep -c), rc 0, in both modes; each mutant KILLED by a named check. |
| 12 | Ingest selftest 15/15 | CONFIRMED | `python [-O] tools/ingest/judgebench_ingest.py --selftest` | 15 ok, 0 FAIL, rc 0, in both modes. |
| 13 | "lint 0" | UNDETERMINED | pyflakes and ruff are not installed | The selftest's static lint (sqlite3.connect only in open_ro / open_cache_rw) passes, as part of #11. |
| 14 | SYSTEM sha 3760f988; GENERIC slot in the system turn; swap imported | CONFIRMED | own build from MAIN's modules: prompt_v2 template, REF->NOREF by pair_noref's constants, rvc slot texts, SCHEMA_INSTRUCTION | 3760f9882264b9705154057c550a0bec1c05de56edb820283756b61c063981da, 2,015 chars. GENERIC_SYSTEM 3a5e223c.../130 chars and GENERIC_RUBRIC 67f843eb.../81 chars are both present; "reference" absent; no "$"; REF sentence appears once in the template; stack_norubric's slot texts = rvc's. Runner uses `pnr.noref_system_template()` (L301), and noref_swap_check refuses retyped lines. |
| 15 | Per-size schedule and payload set shas | CONFIRMED | own sort by sha256("JUDGEBENCH-REASONING-SIDE\|"+pid), own quotas, own json.dumps bodies; and the builder's `--arm both --size N --dry-run` for N = 350/250/150 | all 11 values below are equal. |
| 16 | The two bodies differ only in "model" | CONFIRMED | own bodies; dry-run [BODY-DIFF] OK at all three sizes; mutants s1_temperature / s1_max_tokens KILLED | no "temperature"; max_tokens 8192. |
| 17 | Size gate and refusals | CONFIRMED | 7 non-posting invocations (no --go was run) | no --size, size 300, run or pilot without --go, --dry-run --go, and --analyze without --size are all refused with the stated message. |
| 18 | Accounting: the urlopen wrapper really counts | CONFIRMED | rejudge_reasoning.py L127 calls `urllib.request.urlopen(req, ...)` by attribute at call time, so PostCounter.install (L940-L942) intercepts every attempt, retries included | The wrapper is not bypassed. |
| 19 | Accounting: per-arm journal = ledger | REFUTED at midnight (D1) | scratch simulation of reconcile() / check_equal() with the builder's functions | journal 5, ledger 10 after the next launch's reconcile, then "ledger AHEAD ... refused". |
| 20 | Runner writes nothing to any pool or cache of record | CONFIRMED | code read + audit hook + dry-run [LINT] | The arm process may open only the corpus DB (ro, immutable) and its own cache (root, gitignored); any other sqlite3.connect raises (L105-L112) and is recorded for C0(g). It also writes the day ledger (by design), the lock file, and write-once outcome files. vote_frame_cert's root scan (L755) does not classify the JB tables as dual-order candidates (no ORDER_KEY_COLS column; response_A/B do not match RAW_PAIR_RE), so its census is not perturbed. |
| 21 | Support section (DEFF and its source, n_eff, SE, MDE) | CONFIRMED, NON-VACUOUS | own arithmetic | Unique question strings measured at 350, so DEFF 1.00 is structural and n_eff = 350. SE = sqrt((0.33-0.0121)/350) = 0.03014, MDE = 2.80 x 0.03014 = 8.44pp. At 250: 0.03566, 9.98pp. At 150: 0.04604, 12.89pp, which is >= +12, so DESCRIPTIVE-ONLY. The runner re-measures DEFF (Kish), d, SE and MDE beside C1 (render L651-L655). |

Dry-run anchors of record (in LF; they do not depend on CRLF, because script_blob and payload_body source are read LF-normalised):

| item | value |
|---|---|
| SYSTEM | sha256 3760f9882264b9705154057c550a0bec1c05de56edb820283756b61c063981da (2,015 chars) |
| payload anchor, pair 58d81545-6e2e-5388-b1b7-05ec20157459, order 1 | G 742b02ecf235180805e921651dac2030c795e5d70a26b3549dffd8b4f2f7793d / S1 b536f9fd1eca82157f8d0b3929f6b85ccc9efe9fff725f3069d39cf8813bfdf9 |
| schedule set 350 / 250 / 150 | b9e4a23bc5710d2e840c0841e0ed97636c77580a8949dceb4d3ec9c6786654cc / c8765672d9de90c8ba1b3248b8b298ae5115894487c802295e25d3dcf12cf1b8 / dbc0ea2837e94534ce48fbe3d01ae24cccbee84b8865727607c31f804cb24849 |
| pilot set (identical at every size) | 2bee205c6d63ac75fdc901a5b33c04ec19c8c43564f22a8c9134c6b084fe66c7 (3 per category) |
| payload set 350, G / S1 | 832e54a9c9a32a4541e49c6d93433735c0992406d5e443edf5227b1c02efa1a0 / 1806a6bee90883bdaf67d632810d0ad285fc8ec2af0f3dc9fbe8258cbfb7707b |
| payload set 250, G / S1 | a3b2c955264eaf709f1351a511f2195ea79045dd2985fe217e70128b04f8f327 / 54987d1c89e3d0118831faa6bd1222b7052b40b1f266199ff7ed50d551c833b5 |
| payload set 150, G / S1 | 0848879ea96d9af169acdc11695035937e52e29d8ef90027367e507a7954ab0d / 4f4df2bfc6a6759bb377fcafb761657a70f8fe9647e492a55bc4718cf9cb7449 |
| rr.payload_body source | sha256 907366e47c3f5ce98b2a6e0d59284ba35bc586b59fb7699916c3280bdda554d9 |

## Pins for the registrar

Hash kinds are as rule 8 names them. The worktree files are LF. After a `git checkout e5cac52 -- <path>` on main (core.autocrlf = true), the working tree will be CRLF, so the CRLF value is given beside each.

| file | blob (LF) | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/judgebench_side.py | blob:5e8f68eb484fa02f957019c0898eb050f1b47fca | 5f783bb76a23e0fc | 6caada2ac19410a0 |
| tools/ingest/judgebench_ingest.py | blob:a2b0878fe75a00720095cebd72a8bf791a7d0a83 | eeb4286b619ab6bc | 2a28f3f0b5d26075 |
| experiment_results/judgebench_side/ingest_manifest.json | blob:87c59f86394a4cb44ec4ed56c8564d5a12264bb4 | b00cb01492e301dd (full b00cb01492e301ddeb4908007c580d4e28659ae2902e9569de2bf561335107a1) | 392a59d961aa379f |
| tools/analysis/accepted_tests_ledger.py, branch | blob:1d945bb1896ec8cce6abe2ac2dd8533feb818118 | 03884b78f3cab8dc | (not to be merged by path) |
| tools/analysis/accepted_tests_ledger.py, 3-WAY MERGED (main a4a1d7ee + JB hunk) | blob:fabb66a8b3d73a3c31053170145c3be7b8e54975 | e5f942de85da83d5 | 9875b083df114b29 |

Other pins:
- **Corpus DB** judgebench_corpus_v1.db (SQLite 3.39.4):
  - file sha256 a2ca40b8d4b06126c8b61f6d1f2c2c5a2cd65ad844b542599dedf79efcf2f498;
  - pairs table_sha256 eee0193c4abf8f0003d319a9e7a04f3ba5a641d6498b4ea75d1832d9ab9b2064, 620 rows. This is the value the runner checks (CORPUS_PAIRS_TABLE_SHA, L157);
  - meta table_sha256 41f2bf1d86e6e3e5b2208d8d23f01b428c9386a4450606e84fb36d44461db0cf, 15 rows.
- **Dependencies unchanged 6134573..main**, proved by count: `git diff --name-only 6134573 main -- rejudge_reasoning rejudge_grok pair_noref rubric_value_contrast prompt_v2 stack_norubric split_side pool_guard boundary_disagreement | wc -l` = 0. The side TSV blob 716b3b84 is identical on main and at e5cac52. judge_v2/induction.py did change on main (147e6874), but `_tokens` is textually unchanged (L400-L401), so the ingest selftest's tokenizer check still holds.

## Merge procedure (deviation 7)

1. **Order.** Merge after the pilot K46 run of record has closed, as the orchestrator plans, and after D1 is fixed on the branch. Do not path-restore accepted_tests_ledger.py: the branch blob 1d945bb1 lacks `CEILINGS["ARCH-V2-INDUCE-RUBRIC-3"] = 6`, which main added at 0b512e3.
2. **The three new files, by path from the fixed branch commit:** `git checkout <fixed> -- tools/analysis/judgebench_side.py tools/ingest/judgebench_ingest.py experiment_results/judgebench_side/ingest_manifest.json`.
3. **The ledger module, 3-way:**
   ```
   git show 6134573:tools/analysis/accepted_tests_ledger.py > base
   git show main:tools/analysis/accepted_tests_ledger.py > ours
   git show <fixed>:tools/analysis/accepted_tests_ledger.py > theirs
   git merge-file -p ours base theirs > merged
   ```
   Then write the result to the path. I ran this in scratch:
   - rc 0, no conflict;
   - the diff against main is the JB line only (+ 2 blank lines);
   - CEILINGS = {INDUCE-1 6, INDUCE-2 6, INDUCE-3 6, CANARY 1260, JB 1540, TRACE 2184};
   - result blob:fabb66a8b3d73a3c31053170145c3be7b8e54975 / sha256-lf16:e5f942de85da83d5 / sha256-crlf16:9875b083df114b29.
   
   Verify with `git hash-object` after staging (the LF blob must be fabb66a8).
4. **Commit** with `git commit -- <the 4 paths>` only.
5. **Re-run on main:**
   - `python tools/analysis/judge_v2/induce_run_3_selftest.py` under python and -O. It asserts `atl.CEILINGS.get(TEST) == 6` and calls atl.guard on a temp ledger, so the extra key changes no expected number; confirm by the run;
   - `judgebench_side.py --selftest` and `judgebench_ingest.py --selftest` under python and -O. Expect 73 ok / 15 ok, 0 FAIL, all mutants KILLED.
6. **Corpus DB on main** (deviation 1):
   - `--fetch --raw-dir <scratch>`, then `--build`;
   - the file sha256 must be a2ca40b8... and pairs eee0193c... (the runner refuses otherwise);
   - copying the worktree DB instead is byte-equivalent, but the rebuild is the independent check.
7. **Dry-run on main** at the author's size. It must print the anchors in the table above.

**Does the CEILINGS entry change the pilot's accounting?** NO.
- tools/analysis/archv2_pilot/accounting.py uses only atl._rows, ledger_files, ledger_calls, day_ledger_path, MATCH_RULE and append. It uses neither CEILINGS nor atl.guard (grep of the file).
- pilot.py pins no atl blob. The pilot READY's "atl blob 4e9db106 (unchanged)" was a statement made at review time, not a runtime check, and atl has already moved to a4a1d7ee on main.

The entry does change atl.guard's combined statement (iii) for CANARY / TRACE / INDUCE-* by JB's posted calls. It adds 0 until JB posts. The current combined value is 4,060 + 3,434 = 7,494 before JB's 1,400 planned.

So nothing forces the merge to wait for the pilot. Waiting is harmless and conservative. JB may not post until the pilot has finished posting, whatever the merge date (D4).

## Rulings on the deviations

1. **The DB rebuilt on main by the operator, with its sha checked.** ACCEPTED. The build is byte-deterministic (claim 4). The gate is the pairs table sha, which the runner checks, plus the file sha for the manifest.
2. **The size-150 quotas are the builder's derivation.** ACCEPTED as a derivation. K66/R42/M24/C18 is exactly x3/7 of 154/98/56/42, the same rule as 300 (x6/7) and 250 (x5/7), and the draw keeps the registered order. But see D2: 150 is DESCRIPTIVE-ONLY for C1.
3. **P4b pinned as a Shapley decisiveness split.** ACCEPTED.
   - Decisiveness part = (sS-sG)(dG+dS)/2 and discrimination part = (dS-dG)(sG+sS)/2. These sum to the conv-A gain exactly; I checked the algebra, and the selftest checks it to 1e-12.
   - Here "decisiveness" is the COMMITTED share (1 - tie - INVALID). The registration's gloss is "1 - tie rate". The two coincide only when there are 0 INVALID pairs. The committed share is the choice that makes accA = share x disc exact.
   - The registrar should bracket the formula before the pilot. It is pinned in the docstring (L69-L74) and the code (L565-L566).
4. **Stop-truncations counted UNPARSED but still voted via the regex fallback.** ACCEPTED. The registration's parse is parse_judge, including its fallback. Its UNPARSED class includes stop-truncation, for the guards. Conv A's wrong list (TIE / INVALID / NON_TERMINATED / content_filter) does not include stop-truncation. The runner prints the stop-truncation count beside each arm. I verified that strict_verdict mirrors parse_judge's JSON path branch for branch (L388-L400 against rejudge_grok L168-L190).
5. **P9b scored against the measured base rate.** ACCEPTED. At 350 the measured rate is 161/350 = 0.460 exactly, with 0 length ties, so it equals the registered value. At 250 and 150 the measured subset rate is the proper analogue, and the registered 0.460 is printed beside it.
6. **The accounting design.** ACCEPTED except for D1:
   - the 0-call ceiling row;
   - per-arm journal = ledger at the start and end of every launch;
   - the urlopen wrapper (effective, claim 18);
   - the refusal on any day with a K46 row;
   - the invocation-cap trigger, and the HTTP cap ceil(2.2N) per arm.
   
   The K46 refusal protects in one direction only (D4).
7. **Ledger clash.** See the merge procedure.
8. **The early read-only schema read of mmlu_pro_dataset_cache_v2.db.** ACCEPTED as disclosed (LOW). It was a read outside the one-pass W1-W5 protocol, and its compliance cannot be verified after the fact. The DB is provably unwritten: sha 4f65414f... equals the value the owed pass recorded, the mtime is 2026-09-19, and the -wal is 0 bytes.
9. **Selftests not re-run.** Resolved: I re-ran them (claims 11-12), plus the dry-runs at three sizes. They must be re-run on main after the merge (step 5).

**Also checked:**
- The no-reference swap is imported: CONFIRMED (claim 14).
- GENERIC_SYSTEM + GENERIC_RUBRIC 67f843eb are in the system turn: CONFIRMED.

**EVAL items (the 44 EVAL; 14 of them in p2dca's judgeable set, 13 on the board of record; 38 board-of-record questions in the GPT split overall).** Judging them breaks no reserved-pool rule:
- Rule 1 forbids construction, labelling, induction and fitting over EVAL; judging is what EVAL is for.
- The responses are gpt-4o-2024-05-13's, not a contestant's. The recipe has no reference. No verdict enters any board.
- The runner writes nothing to any pool, view or cache of record (claim 20).
- One gap in the record (D5): the corpus DB itself carries key-bearing copies (label = the MMLU-Pro key) of all 44 EVAL items. Registration HYGIENE (c) excludes "both side DBs"; the ingest's docstring and the DB's meta already extend the exclusion to the corpus DB.

## Defects

**D1 (HIGH): a midnight-crossing launch corrupts the day ledger and voids C0(e).**
- *Mechanism:*
  - arm_main fixes `day` once at the launch start (L1022). Every journal row carries that day (L1043).
  - The launch's ledger row is appended in `finally` with no `day=` (L1087), so it lands on the END date.
  - The next launch's reconcile() compares per day (L877-L884). It first appends a "reconciled after crash" row for the start day (a double count) and then refuses on the end day ("ledger AHEAD").
  - The ledger is append-only, so analyze's C0(e) `led == tot` then fails, and the test is UNDETERMINED BY VALIDITY after the spend.
- *Proved by execution* (scratch, the builder's functions, temp ledger):
  - a journal of 5 posts dated 2026-10-01, with the finally row on 2026-10-02: end-of-launch check_equal = 5 (passes);
  - the next launch: `created day_calls_2026-10-01.json ... reconciled after crash: 5`, then `[JBSIDE] the ledger of 2026-10-02 carries 5 posts of arm S1 but its journal 0 ... refused`;
  - ledger total 10 against journal 5.
- *Also:* posts after midnight bypass the next day's K46-row check and day-cap check.
- *Likelihood:* S1 is 60-175 min per the registration, and any RAISED transport error needs a relaunch.
- *Fix:*
  - in `one()` (L1032), before the invocation insert, `if time.strftime("%Y-%m-%d") != day: stop.set(); raise PostCapReached("day rolled over; relaunch")`, so no post of a launch falls outside its launch day;
  - pass `day=day` to the finally `atl.append` (L1087) and to the CEILING row (L1024);
  - add a selftest check that simulates a rollover (0 posts after it; ledger = journal per day);
  - re-run the selftests under python and -O;
  - delta review of these hunks.

**D2 (HIGH, size 150 only): C1 and P3 are scored at N=150, where the registration makes C1 DESCRIPTIVE-ONLY.**
- *Where:* SUPPORT L17447 and the registrar's (f). render (L657-L680, L712-L713) has no size branch, so it would print "C1: REASONING BETTER" and score P3.
- *Fix:* at size 150, print C1's point, p and interval under a registered branch "C1.DESCRIPTIVE_ONLY (N 150)"; mark P3 NOT SCORED; F1 stays scored and descriptive. Or the registrar rules otherwise before the author is asked.

**D3 (LOW): fixed labels.** render prints "MDE 17.5pp ... at N 350" (L683) and "registered planning MDE 8.4pp at N 350" (L653) at every size. *Fix:* print the size's registered values (8.4 / 10.0 / 12.9pp for C1; 17.5pp only at 350).

**D4 (MEDIUM, operational): the one-directional day rule and single-arm runs.**
- (a) The K46-row refusal protects JB from launching on a pilot day, but not the pilot from launching later on a JB day: accounting.py knows nothing of JB. *Condition:* JB posts only after the pilot's run of record has finished posting.
- (b) `--arm S1 --go` alone checks only its own pilot guard (L1015-L1017). The other arm's pilot PASS is checked only in both_main (L1138-L1148). *Condition:* launch the pilot and the run only with `--arm both`.

**D5 (MEDIUM, record):** HYGIENE (c)'s exclusion names "both side DBs". The corpus DB holds the same key-bearing copies (44 GPT-split EVAL items, 41 Claude). *Fix:* a registrar bracket extending the EXCLUDED-input rule to judgebench_corpus_v1.db, as the ingest docstring (L32-L33) and the DB meta already state.

**D6 (LOW):** `--analyze --size N --go` ignores --go silently (main L1678-L1680; size_gate is called with go=False). Refuse it, as the dry-run does.

**D7 (LOW):** C0(e) compares against 1,540 at every size (L1254). The arm caps (550 / 330) bind first, so the effect is nil. Print the size's ceiling ceil(1.1 x 4N).

**D8 (LOW, disclosure):** INDUCE-3's rubric of record (9e0a4022) postdates the build and is not in the owed list. My 8-token check: 0 hits.

**D9 (LOW, pre-existing, not this build's):** atl.append has no cross-test lock. JB's LedgerLock covers only its own two arms. Another test appending on the same day could lose a row. Mitigated by the separate-day rule for K46; note for any other test that posts the same day.

**D10 (INFO):** Owed (ii) is keyed by "i:"+stem_key against the view's items, the same key as the side export. It is a consistency check (44/44, 0 disagreements), not independent evidence.

## Structural leg (the registrar's (g))

CONFIRMED.
- C1 is reachable at 350 and 250 (MDE 8.4 / 10.0pp, below the predicted +12pp; no ceiling binds).
- The population is finite (350), so no budget helps the DESCRIPTIVE-ONLY interaction.
- A C0(d) termination failure in S1 is the named structural hazard. It is read UNDETERMINED BY VALIDITY, never as a falsification. The runner's render branch C1.UNDETERMINED_BY_VALIDITY / F1.NOT_EVALUATED is executed by the selftest.

## Launch conditions once D1 is fixed

1. The author's size is recorded by the registrar, and the READY applies to 350 or 250. 150 needs D2 fixed or a ruling.
2. Merge per the procedure, after the pilot, with the re-runs in step 5.
3. Posting day: a fresh day, after the pilot's last post (D4a), with no K46 row that day.
4. Launch with `--arm both` only (D4b).
5. The dry-run on main prints the anchors above.
6. Registrar brackets: the P4b formula (ruling 3); the P9b base-rate reading (ruling 5); D5.
7. Back up the corpus DB and both caches to the E: manifest after the run, as registered.
