# READY review: SPLIT-EXPOSURE-SENSITIVITY at 4934a28 (adversarial reviewer, 2026-09-23, zero calls, read-only)

**VERDICT: NOT READY.** One BLOCKER (D1): on the real data, the route (A) child crashes after the headline is parsed on every consumer whose original closes a connection. RUBRIC-512-SS, RUBRIC-512-R and LADDER therefore fail C0 as UNDETERMINED (BY VALIDITY), which covers **5 of 13 cells** (b-E28, b-E70, c-E28, c-E70, e-LADDER). A run at 4934a28 would score P6 FAILED, and the cause would be the instrument, not the data. One HIGH (D2): READY hazards (a)-(d) appear nowhere in the instrument. Everything else I checked holds. With a scratch one-line fix, the three consumers reproduce their headlines to the digit.

Registration: docs/judge_v2_program.md L14701-L14756 (46889ea). Evidence: L14829-L14841 (af15402). Rulings: L14867-L14881 (a4d736a). Record: docs/agents/results/SPLIT-EXPOSURE-SENSITIVITY.json.

## Identity (pins with their kinds; LF rendering is the rendering of record; working tree LF for both new files, so no CRLF pin)
- tools/analysis/split_exposure_sensitivity.py: blob:4bb615547d6f65722a6ce2ad3691da514b3a9ab2 / sha256-lf16:ab53335b154db3ae (`git hash-object`; `git show 4934a28:<path> | sha256sum`). Matches the brief.
- tools/analysis/split_exposure_child.py: blob:177ed5367be7eb466f8ff79ec9ffe37b08dde5c2 / sha256-lf16:0a322a3d77a525ad. Matches the brief.
- Imported unedited: cert_under_filter.py blob:f7d59019c3d65128687df46aebdcb798b43c3062 / sha256-lf16:0db2026f17b559a1 (working tree CRLF, sha256-crlf16:b144a7d4377acfd3). pool_guard.py blob:6521b51ac0fce04063563f9e6dcf42554ad86591.
- Route (A) originals, A1 pins (blob kind; each identical in main and in the worktree): rubric_512.py 81ae1d39, rubric_512_ss.py f401668c, rubric_512_r.py 70b10af1, leaf_powered.py ca46cee9, rubric_ladder.py d94831fc, stack_judge.py 6acfc319, j6_rubrics.py a898515f.
- `git diff --stat 751cf57 4934a28 -- tools/analysis` shows only the two new files (+2491), so they are mergeable by path.
- Evidence sets (sha256-lf, full hash truncated to 16): E28 525aad9a16e61066 (28), E70 0dfea2fcdf8af2bb (70), E14 2b758ed2d955d409 (14), E74 1ca79db5764ba80d (74). The relations check out: E28 is a subset of E70; E74 = E70 u E14; E70 n E14 = 10.

## Rule 7 and hygiene of this review
- The window was 19:11-19:40. The only other processes were an idle Gradle daemon (up since 11:35, no worker) and another agent's CERT-DIRECTION-STREAM `--selftest` mutation runs (synthetic, admitted). CERT-DIRECTION-STREAM itself was not running, and there was no construction and no site null.
- Dry-run: `python tools/analysis/split_exposure_sensitivity.py --dry-run --workers 1`, from main (the worktree lacks mmlu_pro_dataset_cache_v2.db, snapshots.db and leaf_powered.db). It ran through temporary untracked copies of the two 4934a28 files. It took 28 m 43 s and ended rc=0 with "DRY-RUN COMPLETE".
- The copies were removed afterwards (by the coordinator, who confirmed them byte-identical to the 4934a28 blobs). `git status --short tools/` prints nothing. No python process of mine is alive (checked with a Win32_Process listing).
- Inputs: my own fingerprint script covered size, mtime_ns and sha256_16 of all 15 input DBs, plus every -wal/-journal/-shm in the three DB directories. The before and after snapshots are IDENTICAL (`diff` empty, 33 lines each). The -wal files beside mmlu_pro_dataset_cache_v2.db, snapshots.db and ratings_x12.db are 0 bytes; stack_v2_promptv2_x12all.db has no sidecar. The instrument's own checks agree: "route (A) files opened by the consumer children: 15; unchanged: yes", and inputs before/after are unchanged.
- snapshots_frozen.db and twenty_newsgroups_cache_v1.db were not opened. The glob only stat'ed their sidecars.

## Per-claim table
| # | Builder claim | Verdict | Command / evidence | Got vs claimed | Sev |
|---|---|---|---|---|---|
| 1 | Selftest passes under python and -O, 52/52 branches | CONFIRMED | `--selftest` and `python -O ... --selftest` | rc 0 both; "52 of 52 required"; 18 s each | - |
| 2 | 15/15 mutants killed | PARTLY | ses_build/mutants2.out | 15/15 killed, but RA4 ("consumers in one process") dies on the A4 credential check (the parent env holds AZURE_AI_API_KEY in the selftest), not on the A5 pid check | LOW |
| 3 | Negative controls: writer, missing-table CREATE, socket, wrong pin, -wal | CONFIRMED | selftest "NEGATIVE CONTROL writer/create/socket", A1, [SIDECAR] | all refuse | - |
| 4 | 7 consumers' recorded outcome texts replay to the headline | CONFIRMED as stated; VACUOUS as a witness | selftest_route_static parses tracked text files | The same 3 consumers whose texts "replay" fail C0 by EXECUTION (D1). A text replay is a presence check on a pattern | see D1 |
| 5 | All 13 cells built; C0 through the redirect | **REFUTED on real data** | dry.out; scratchpad trace_child.py | C0 PASS 8/13; UNDETERMINED (BY VALIDITY) 5/13, `ProgrammingError: Cannot operate on a closed database` at split_exposure_child.py L347 | BLOCKER |
| 6 | Headline captured from the original's own stdout, exactly one line per pattern | CONFIRMED | adversarial original printing two header lines | refused "[A6] ... matched 2 lines" | - |
| 7 | Removal applied to an in-memory copy of the input; n drops by exactly the removed matches | CONFIRMED | fidelity.py (builder path) vs indep.py (my own SQL) | see Removal fidelity | - |
| 8 | Zero calls enforced (A4) | PARTLY | adv_route.py | see note 8 below the table | MEDIUM |
| 9 | No write can land (A3) | PARTLY | adv_route.py | see note 9 below the table | MEDIUM |
| 10 | A1 pins checked at launch and in the child | PARTLY | parent L285-L298, child L433-L438 | Only the 7 top-level originals are pinned. The imported graph (rejudge_grok, rubric_value_contrast, rubric_p8, rubric_512, rejudge_reasoning, rejudge_reference, judge_free_tests, prompt_v2, pool_guard, rubric_ladder via j6) is neither pinned nor printed. C0 is the only witness against drift | MEDIUM |

**Note 8 (A4, zero calls).**
- urllib is refused and counted: 1 attempt. The original swallowed the exception, and the cell is still UNDETERMINED.
- A raw `_socket.socket().connect` BYPASSES the guard: the listener accepted.
- Stripping credentials does nothing for this project, because every key is read from ROOT/.env by load_env() (rejudge_grok L215, rubric_p8 L30, rejudge_reasoning L63, rejudge_reference L36, rubric_value_contrast L86).
- A name such as GOOGLE_APPLICATION_CREDENTIALS passes is_secret.
- So the printed "credentials left 0" certifies nothing; the socket guard is the only control.
- Across the real module graph, `_socket` / subprocess / os.system occur 0 times outside pool_guard's selftest (grep -c over 15 files).

**Note 9 (A3, no write can land).**
- A second connection, and `connect(DB, factory=Subclass)`: refused, no write.
- `sqlite3.dbapi2.connect(DB)` and direct `sqlite3.Connection` subclass construction BYPASS the redirect. The write LANDS on the file (a table was created) and is only detected afterwards by the fingerprint (cell UNDETERMINED).
- A write with `open(path, "w")` goes undetected, and the cell scored.
- In the real module graph, `dbapi2|sqlite3.Connection|_sqlite3|apsw` occurs 0 times (grep -c, 15 files), and there is no `open(..., "w"/"a")` in the 7 originals or their helpers.

## Per-cell C0 table from the real-data dry-run (my independent recomputation beside it)
My recomputation is scratchpad ses_ready/indep.py and indep_ladder.py: my own SQL, every DB opened `mode=ro&immutable=1`, no original imported.

| cell | C0 at 4934a28 | recorded | my recomputation | connection log (opens) | A4 attempts | k (matches / exposed q) |
|---|---|---|---|---|---|---|
| a-E28 RUBRIC-512 | PASS +1.8, 42:25, p 0.0498, n 946 | same | n 946, 42:25, +1.797pp | bareq512_s42 1, rubric_contrast 1, mmlu_pro 1 | 0 | 7 / 7 |
| a-E70 RUBRIC-512 | PASS | same | same | same | 0 | 20 / 19 |
| b-E28 RUBRIC-512-SS | **UNDETERMINED (BY VALIDITY)**, D1 | +1.0, 35:26, p 0.31 | n 946, 35:26, +0.951pp | bareq512_s42, generic_ss, ratings_x12, rejudge_grok, rubric_contrast, mmlu_pro (1 each) | 0 | (7 / 7) |
| b-E70 RUBRIC-512-SS | **UNDETERMINED (BY VALIDITY)**, D1 | same | same | same | 0 | (20 / 19) |
| c-E28 RUBRIC-512-R | **UNDETERMINED (BY VALIDITY)**, D1 | 0.842 = 0.842, 24:24, 946 | n 946, 24:24 | grok_reasoning_cell, _generic, ratings_x12, rejudge_grok, mmlu_pro (1 each) | 0 | (7 / 7) |
| c-E70 RUBRIC-512-R | **UNDETERMINED (BY VALIDITY)**, D1 | same | same | same | 0 | (20 / 19) |
| d-E28 LEAF-POWERED | PASS -0.3, 9:7, n 786 | same | n 786, 9:7, -0.2545pp | leaf_powered 1, rubric_ladder 1, mmlu_pro 1, snapshots 1 | 0 | 8 / 4 |
| d-E70 LEAF-POWERED | PASS | same | same | same | 0 | 22 / 13 |
| e-LADDER | **UNDETERMINED (BY VALIDITY)**, D1 | 35:38 on 967, p 0.68 | n 967, 35:38; 14 anchors, 0 questions with two anchors | ratings_x12 2, rubric_contrast 1, rubric_ladder 1, mmlu_pro 1 | 0 | (2 / 2) |
| e-STACK (v1) | PASS acc 0.843, n 944 | 0.843 on 944 | 796/944 = 0.84322 | stack_v2 2, rejudge_mistral_reference_grok_reasoning 1, mmlu_pro 2 | 0 | 3 / 3 |
| e-STACKv2 | PASS acc 0.865, n 944 | 0.865 on 944 | 817/944 = 0.86547 | stack_v2_promptv2 2, rejudge_mistral_ref 1, mmlu_pro 2 | 0 | 3 / 3 |
| e-J6 | PASS -1.8, 23:40, p 0.043, n 944 | same | n 944, 23:40, -1.801pp | generic_ss 1, rubric_j6 1, mmlu_pro 1 | 0 | 3 / 3 |
| f-CERT | PASS W_F 17, W_R 24.15, Delta_W -7.15, [-14.22, -0.08], 13 anchors, 752 edges, SE 3.606, HELD (406 s) | same | equivalence to CERT is established by the CERT-DIRECTION-STREAM READY 751cf57; not re-run | cert's log: 4 connects, stack cache exactly once, all immutable | n/a (in-process) | 201 / 69 of 74 (= evidence 69 / 201) |

- k values in parentheses were measured by my code and by the scratch-fixed child. All other k are from the dry-run and agree with my code. Import-time opens are "none" for every consumer.
- Probe count equals headline n for every PASS consumer, and for the scratch-fixed SS / R / LADDER (946 / 946 / 967).
- LADDER anchor ambiguity: none.
- Every qid of every consumer lies in p2dca's judgeable ids (0 outside). All consumers join by eval question_id (LADDER through match_history.eval_question_id).
- **The scratch fix confirms D1 is the only blocker for these cells.** I made a local copy of the child in which writes() skips connections the original closed (scratchpad fixchild/, not in any tree). With it, C0 reproduces SS 35:26, p 0.3057, n 946; R 0.842/0.842, 24:24, n 946; LADDER 967, 35:38, p 0.6800, (a) FAIL, (b) FAIL. A4 attempts are 0 for all three.

## Removal fidelity (my own code against the builder's child on one real removal set; n, b, c exact)
| cell / set | child: full -> reduced | mine: reduced | n drop = k |
|---|---|---|---|
| RUBRIC-512 x E70 | 946 42:25 -> 926 41:25 (T 8/463) | 926 41:25 | 20 = 20 |
| LEAF-POWERED x E70 | 786 9:7 -> 764 9:7 | 764 (7 leaf-only, 9 anchor-only) | 22 = 22 |
| STACK-v2 x E14 | 817/944 -> 815/941 | 815/941 | 3 = 3 |
| J6 x E14 | 944 23:40 -> 941 23:40 | 941 23:40 | 3 = 3 |
| RUBRIC-512-SS x E70 (fixed child) | -> 926 34:26 | 926 34:26 | 20 |
| RUBRIC-512-R x E70 (fixed child) | -> 926 24:24 | 926 24:24 | 20 |
| LADDER x E14 (fixed child) | -> 965 35:38 | 965 35:38 | 2 |

- The witness also holds off the exposed set. A random 5-question removal drops n by 6 / 11 / 7 / 5, equal to those questions' scored matches.
- The parent enforces the witness as a count check (mapper: `st["n"] == st0["n"] - sum(mcount)`).

## The null
- Anchor-matched on whole questions; the counts are exposed scored QUESTIONS per anchor, as registered; k in matches is printed but not matched.
- Seeds Random(14701 + j), j = 1..13 in registry order (a-E28 14702 ... f-CERT 14714), printed in the dry-run.
- R = 1,000 for cells and 200 for CERT. check_draws reports "none holds an exposed question" for every cell.
- **Reproduced:** my own draw for RUBRIC-512 x E70 at Random(14703) equals the builder's first 3 draws, and the universes are equal (scratchpad draws.py). No null quantile was computed, so no outcome was seen before the run.
- The observed shift is never in its own null (batch[0] held apart; `need(len(null) == R)`; mutants M2a and M2b killed).
- The flag is two-sided and strictly outside the central 95% (numpy linear; equality does not flag; M3a-c killed). k = 0 gives UNDETERMINED (BY SUPPORT) with no null drawn.
- Directions follow r7 (leak_sign -1 for RUBRIC-512/-SS/-R, LEAF-POWERED, STACK, STACK-v2; +1 for LADDER and CERT; 0 for J6, which is UNDEFINED, two-sided and DESCRIPTIVE-ONLY).
- A CERT flag is printed only (FALS.DESCRIPTIVE_FLAG; r8).

## Support (rule 8, re-derived)
- **Planning SEs reproduce to the digit from DEFF 1.2 and n**, formula sqrt(DEFF k v / ((n - k)(n - 1))):
  - RUBRIC-512 0.087 / 0.135pp; -SS 0.084 / 0.129; -R 0.074 / 0.115; LEAF-POWERED 0.049 / 0.080; LADDER 0.062; STACK 0.085; STACK-v2 0.080; J6 0.060.
  - MDE = 2.80 x SE matches every registered value. CERT n_eff 752 / 1.636 = 459.7; MDE 4.65.
  - The DEFF sources are stated (POSITION-INDEX-ALL pilot 1.2; 605675c measured 1.636).
- At the measured k, every registered support word is unchanged:
  - LEAF-POWERED k 8 / 22 against planning 6 / 16: MDE 0.16 / 0.27pp, below Delta* 2.0.
  - STACK and STACK-v2 k 3: MDE 0.21 / 0.19pp.
- BOUND at the measured k: BOUNDED for -SS x E28 (0.75 < 1.0), -R x E28 (0.75), LEAF-POWERED x E28 (1.03 < 2.0), STACK (0.27 < 0.4), STACK-v2 (0.28 < 2.6) and LADDER (0.21 < 2.0).
- LEAF-POWERED x E70 is reachable (bound 2.89pp at k 22, against the registration's "by 0.08pp only").
- The measured null SD, DEFF, n_eff and MDE are printed by the run (r10) for the post-run review.

## Runtime and memory (dry-run, --workers 1; another agent's mutation selftests ran concurrently)
- CERT: C0 took 406 s. Replicates took **418.0 s each**, against the registered 5.3 min (318 s). 201 x 418 s = 23.3 CPU-hours, about **2.9 h wall at 8 workers** (about 3.0 h with C0), not 2.3 h. The parent peaked at 162 MB; each worker holds D (6.3 MB pickled), so plan about 0.2-0.3 GB per worker.
- Route cells (start-up, then seconds per removal run):

  | cell | start-up | per removal run | child peak RAM | CPU for 1,001 runs |
  |---|---|---|---|---|
  | RUBRIC-512 | 1.3 s | 0.1 s | 223 MB | about 2 min |
  | -SS | 1.4 s | 0.1 s | 250 MB | about 2 min |
  | -R | 1.4 s | 0.1 s | 290 MB | about 2 min |
  | LEAF-POWERED | 2.0 s | 0.1 s | 213 MB | about 2 min |
  | **LADDER** | 2.7 s | **2.3 s** (its 2,000-replicate bootstrap is inside analyze()) | 81 MB | about 38 min |
  | **STACK** | 3.3 s | 0.5 s | **869 MB** | about 9 min |
  | **STACK-v2** | 3.4 s | 0.6 s | **867 MB** | about 10 min |
  | J6 | 1.3 s | 0.1 s | 278 MB | about 2 min |

- The 12 route cells total about 1.25 CPU-hours, about **10-12 min wall at 8 workers**. Peak RAM there is about 8 x 0.87 = 7 GB (the STACK chunks).
- **Projection for the whole run: about 3.1-3.3 h at 8 workers. Price a rule-7 window of 3.5 h with 12 GB free.** The registration's "minutes" holds for cells (a)-(e) only.
- **Sharing a window with CERT-DIRECTION-STREAM** (2.34-2.49 h at 8 workers):
  - The machine is a Ryzen 9 7900X3D, 12 physical / 24 logical cores, 64 GB (34 GB free).
  - 16 CPU-bound workers exceed the 12 physical cores. RAM fits (about 9 GB together).
  - Expect both to slow by about 1.3-1.6x, so about 4-5 h for both. Neither run is resumable.
  - W1-W5 refuse "any other tools/analysis process", so sharing needs an explicit admission of both PIDs.
  - Recommended: two back-to-back windows (3.5 h + 2.5 h), or one window at 6 + 6 workers with both PIDs admitted.

## Hazards (a)-(d) (evidence L14829-L14841)
- `grep -ciE 'Random\(556\)|REPRODUCTION|internal-node|JUDGE-LEAK|options key|hazard'` returns 0 in both scripts (whole-file count). None is printed in the dry-run or the outcome. D2.
- (a) E14 is a reproduction of the 150-per-anchor cap draw (rubric_ladder SEED_CORPUS 556), not a logged corpus. It touches LADDER k 2, STACK / STACK-v2 / J6 k 3, and E74.
- (b) E74 contains all of E70.
- (c) E28 relies on the 17 / 17 [JUDGE-LEAK] witness.
- (d) is met in substance (eval question_id throughout; 0 qids outside the pool) but is unstated.

## Checks that pass without checking
1. The static C0 "replay" of recorded outcome TEXT passes for SS, R and LADDER while EXECUTION fails (D1). The synthetic original never closes a connection and imports none of the real helpers.
2. "judge credentials left in the child's environment 0" is printed for every consumer, but the keys live in ROOT/.env and are never in the environment. The number is vacuous; the socket guard is the real control.
3. The dry-run exits rc=0 and prints "DRY-RUN COMPLETE" with 5 cells UNDETERMINED (BY VALIDITY). There is no summary count of C0 failures, and main_dry hits `C0.CERT_PASS` for every non-CERT cell.
4. A removal-run CellInvalid is printed by cell_lines as "C0: the recorded headline does NOT reproduce", and P6 lists it under "C0 failed".
5. RA4 is killed by the credential check, not by the A5 pid check.
6. The redirect drops connect keyword arguments (factory, isolation_level, detect_types) silently. This is harmless for the 7 originals (C0 witness) but undocumented.

## Defects
- **D1 BLOCKER.** Location: split_exposure_child.py L346-L347. `Redirect.writes()` reads `total_changes` of every proxied connection, including those the original closed (rubric_value_contrast.matches_for, gt_correct).
  - Effect: `ProgrammingError`, and 5 of 13 cells are UNDETERMINED (BY VALIDITY). P6 would read FAILED.
  - Fix: override `ROConn.close()` to record `total_changes` before closing, and have writes() use the recorded value. Do not swallow the error.
  - Add a synthetic original that closes a connection mid-analysis and imports a helper that opens and closes its own.
  - Re-run `--dry-run`; require C0 PASS on 13 / 13 with A4 = 0.
- **D2 HIGH.** Hazards (a)-(d) are not carried. Print them in the header of `--dry-run` and of the outcome, and beside the affected cells: (a) on e-LADDER / e-STACK / e-STACKv2 / e-J6 / f-CERT; (b) on f-CERT; (c) on the four E28 cells; (d) with the measured "0 qids outside the pool; joined by eval question_id" line per consumer.
- **D3 MEDIUM.** A3 is detection-after-the-fact for bypass paths (dbapi2, Connection construction, open() writes), while the printed text claims "no write can land".
  - Fix: state it accurately. Preferably also patch `sqlite3.dbapi2.connect` and `sqlite3.Connection.__init__` in the child.
- **D4 MEDIUM.** A4's credential strip is vacuous for .env-sourced keys, and `_socket` bypasses the guard.
  - Fix: state that the socket guard is the enforcing control. Preferably add `sys.addaudithook` in the child, refusing socket.connect, subprocess.Popen and os.system events.
- **D5 MEDIUM.** A1 does not cover the imported module graph.
  - Fix: print and pin blob + sha256-lf16 of every tools/analysis module loaded in each child (`sys.modules` at the end of the job), and check them at launch.
- **D6 LOW.** The mislabels in checks 3-6 above.
- **D7 LOW.** Runtime is priced at 2.3 h and measures about 3.1-3.3 h at 8 workers. The window must be 3.5 h.

## Conditions for READY
1. D1 fixed. A re-run dry-run shows C0 PASS 13 / 13 through the redirect, reproducing the table above to the digit, with the connection log per consumer and A4 = 0.
2. D2 fixed.
3. D3-D5 fixed, or stated as documented limitations in the docstring with the registrar's acceptance.
4. New pins (blob / sha256-lf16) re-reviewed.
5. The window is priced at 3.5 h with 12 GB free, and not shared with CERT-DIRECTION-STREAM unless both PIDs are admitted.

Scratch (session scratchpad ses_ready/): selftest.out, selftest_O.out, adv_route.py, dry.out, fp_before.txt, fp_after.txt, fp.py, indep.py, indep_ladder.py, fidelity.py, draws.py, trace_child.py, c0_fixed.py, time_fixed.py, fixchild/.
