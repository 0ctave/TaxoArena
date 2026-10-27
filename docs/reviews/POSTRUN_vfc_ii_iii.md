# POST-RUN review (2026-09-26, adversarial-reviewer): VFC-FIXES-2 delta checks (ii) and (iii), run under R2.6-b2 with harness v4

## 0. Verdict

**VALID. (ii) PASS, (iii) PASS. Reuse of `tools/analysis/vote_frame_cert.py` (blob:1a3d0bb5 / sha256-lf16:b45b75db7d98103e) by VOTE-FRAME-CERT, POSITION-INDEX-ALL and TIE-MECHANICS is LICENSED, subject to the registrar's record of this result (conditions in section 5).**

- **Certificate of record.** c731836 is NOT re-issued, and nothing here licenses re-issuing it. VFC_PIN_LF stays 72ceddfe919a982e. The certificate is re-issued only on a registration (C5). See section 5.
- **Zero calls.** I ran no leg, no selftest, no `--dry-run` and no construction.
- **What I did run:**
  - git objects;
  - sha256 and diff on text;
  - the harness's text-only scorers, on the operator's outputs and on my mutants of them;
  - two read-only label censuses (`mode=ro&immutable=1`) on 6 of the 62 caches. The sha256_16 of each was equal before, after and to the certificate.
- **Writes.** Nothing was written to the repo except this file. My scratch is `<scratchpad>\pr_vfc\`.

`<S>` = `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\vfc_ii_iii\`.

## 1. Identity of what ran (hash kinds named; LF is of record)

| object | expected (source) | got (my command) | verdict |
|---|---|---|---|
| harness `<S>/H/rerun_vf4.py` | sha256-lf16:818cfa3b66ba8b3a, blob:8db1d2e7 (registrar, programme L20441) | `sha256sum`: 818cfa3b66ba8b3abe32194ce66f4246fa4c608e541cd475c52220e405b9f959. `git show ea68f47:experiment_results/vfc_fixes_2/harness/rerun_vf4.py \| cmp -` identical; same against HEAD b0c231c. CR 0 | CONFIRMED |
| archive `<S>/T` | LF `git archive f76a93b tools/analysis src/main/kotlin experiment_configs` | My own fresh archive of f76a93b, then `diff -r`: 1 line, "Only in <S>/T/tools/analysis: __pycache__". 630 archive files match byte for byte. The 7 extra .pyc files date from 00:07-00:09, i.e. from the E3 selftests; the legs set `dont_write_bytecode` | CONFIRMED |
| vote_frame_cert.py in T | sha256-lf16:b45b75db7d98103e (ruling 93cc7de) | b45b75db7d98103ef3ac...baca1, CR 0 | CONFIRMED |
| position_index_all.py in T | sha256-lf16:9c78d485f37f442a | 9c78d485f37f442a907b..., CR 0 | CONFIRMED |
| tie_mechanics.py in T | sha256-lf16:d6a1a0409a0fc06e | d6a1a0409a0fc06e3b13..., CR 0 | CONFIRMED |
| legs ran those bytes | each leg's `[BUILD]` x3 | leg_{vfc,pia,tm}.txt L1-L3: "as archived = LF = expected", CR bytes 0, for all 3 files in all 3 legs | CONFIRMED |
| main carries the reused bytes | HEAD = f76a93b for the instrument | `git rev-parse HEAD:` / `f76a93b:` / `git hash-object` on the worktree: 1a3d0bb5 for vote_frame_cert.py; bcbaf609 for pia; 7f88d2ac for tm. `git diff --name-only f76a93b HEAD -- <15-module closure> \| wc -l` = 0 | CONFIRMED |
| prep | rc 0, pins OK, 0 CR, 0c = 1 line | step1_prep.txt: [0a] OK x3; CR 0; [0c] "rc 0, 1 line(s): ['tools/analysis/vote_frame_cert.py']"; "[PREP] extracted 689 members". The transcript does not print rc. The "extracted" line comes after every gate (rerun_vf4.py L219-L230), and the next statement is `sys.exit(0)` | CONFIRMED (rc inferred from the code path, not printed) |

## 2. Per-claim table

| # | claim | verdict | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | E3 vfc 472/0 under python, transcript sha ad6aa8d0... | CONFIRMED | `grep -c '^ *\[PASS\]'` / `'^ *\[FAIL\]'` on e3_vfc_py.txt; `sha256sum` | PASS 472, FAIL 0, Traceback 0; L474 "SELFTEST PASS: 472 checks, 0 failed"; sha256 ad6aa8d0ef5b5073ae4ba748bc14b083cb9e271f03028c50d17a8ef7daf80888 |
| 2 | E3 vfc 472/0 under -O | CONFIRMED | same, on e3_vfc_O.txt | 472 / 0. `diff` against the python transcript: 2 lines differ (L375, L446), both only in the mkdtemp directory name |
| 3 | E3 pia 55/0 + 1 INFO | CONFIRMED | same, plus `grep -n '\[INFO\]'` | 55 / 0. One `[INFO]` line (L46). Total line "55 checks, 0 failed; 1 INFO line(s)". L47 names the imported reader as b45b75db7d98103e, which ties this transcript to the b2 bytes by content |
| 4 | E3 tm 29/0 | CONFIRMED | same | 29 / 0 |
| 5 | the leg's [E3] sha equals the step-3 sha | CONFIRMED | leg_vfc.txt L4 and L7 vs `sha256sum e3_vfc_py.txt` | ad6aa8d0...0888 = ad6aa8d0...0888 (62199 bytes). The archive hashes (e3_archive_sha.txt, 00:07) and the transcripts (00:08-00:09) come from the same step; T is unchanged since (row "archive" above) |
| 6 | legs rc 0 | CONFIRMED | window.log: "[LEG] vfc rc 0 wall 9 s", "pia rc 0 wall 5 s", "tm rc 0 wall 15 s". Each transcript ends at its last statement (`[C-ii-3] after ... -> unchanged`). `grep -c REFUSED` = 0 in all three | as claimed |
| 7 | the window waited for the probe and emd_selftest; clear at 00:33:58 | CONFIRMED | window.log: NOT CLEAR from 00:23:08 to 00:33:27 (emd_selftest PIDs 48000 and 61692; jv2_rate_probe --pilot 56100, --run 55924, --analyze 62544); "[W] CLEAR 2026-09-26T00:33:58"; W1 FREE; W4 26.82-27.05 GB | as claimed. HEAD was b0c231c at every [W5] (before each leg and at close). No commit fell inside 00:33:58-00:34:28, and b0c231c (00:33:55) precedes the window |
| 8 | [PRE]/[POST] 62/62 unchanged | CONFIRMED | leg_vfc L6 / L411 | "[PRE] 62 of 62 ...", "[POST] 62 of 62 caches unchanged". Both record and new JSON carry 62 caches, 62 distinct paths. My spot check on 6 caches: sha256_16 now = the certificate's |
| 9 | the audit hook refused nothing | CONFIRMED as far as the transcripts can show it | `grep -c 'REFUSED'` = 0 / 0 / 0; `grep -ci audit` gives 1 hit in leg_vfc, which is an H3 evidence line, not a refusal. C-ii-3 "-> unchanged" in all 3 legs; the four outputs of record have raw sha16 06876dac / c68a655a / 5c7b12cb / 1a8d802e, equal to my `sha256sum` now; `git status --short` on them = 0 lines | limit: the hook raises RuntimeError, so an instrument that swallowed a refusal would leave no line. The byte checks [POST] and C-ii-3 cover the objects that matter |
| 10 | score-vfc rc 0, 17 expected, 0 findings | CONFIRMED | my own re-run of `rerun_vf4.py score-vfc` (pinned copy, same args): rc 0; output identical to score_vfc.txt after `--strip-trailing-cr`. My own `diff --strip-trailing-cr rec new`: see section 3 | 17 / 0 / rc 0 |
| 11 | L1 exact | CONFIRMED | `diff` hunk 1c1 | new L1 = "... LF bytes b45b75db7d98103e (of the CRLF rendering b45b75db7d98103e) ===". 3b44739e is absent. JSON `script_sha256_16_lf` = `_crlf` = b45b75db7d98103e |
| 12 | the six secondaries move to R6 on contestant-name labels, not '' | CONFIRMED | section 4 | n of m exact; labels are the contestants; 0 '' |
| 13 | F1: the C3 _backup cache UNCERTIFIABLE -> CERTIFIED-CONTESTANT as expected | CONFIRMED | my own JSON comparison (all 62 caches, every unit, every count key) | the only cache move and the only unit move is `_backup/newcomer_placement_steps_2026-09-19_complete.db` UNCERTIFIABLE(RX) -> CERTIFIED-CONTESTANT, with order-1 387/387, order-2 380 contestant and unresolvable 767 -> 0, as R2.6 L154-L157 expects. No other count key moved in any unit |
| 14 | score-pia rc 0, L2 exact | CONFIRMED | my re-run: rc 0, identical output. `diff --strip-trailing-cr`: exactly 1 hunk, 2c2. Python equality against the ruling's string: True | L2 moves from 8939144e5ce87636 / 6f6694eac5a176f8 to 9c78d485f37f442a / 9c78d485f37f442a. L3 did not move ([CERT] entered 50, excluded 12). leg_pia L227 has [WITNESS] "7 times, 4 by content" = the ruling's 4 content resolutions. `[FRAME] REFUSED` count 0 |
| 15 | score-tm rc 0: exactly L14; [POOL] did not move | CONFIRMED | my re-run: rc 0, identical output. `diff --strip-trailing-cr`: exactly 1 hunk, 14c14. Equality against TM_L14_NEW: True | L1 "[POOL] p2dca21ab5f4ef3ae (pool of record; pool_guard.assert_pool_of_record passed)" is identical in record and new, so the UNDETERMINED pool-guard risk did not occur. `[FRAME] REFUSED` count 0 |
| D1 | HEAD moved 1b749ed -> b0c231c; the 4 record paths are byte-identical | CONFIRMED | `git diff --name-only 1b749ed b0c231c \| wc -l` = 10; `grep -vc '^experiment_results/'` = 0 (all under experiment_results/jv2_rate_probe/ plus day_calls_2026-09-26.json). `git rev-parse 1b749ed:<p>` = `b0c231c:<p>` for all four (8db4403f / 5ec19826 / bb1578ca / a2df609d). `git show b0c231c:<p> \| cmp - <S>/rec_*`: all 4 EQ. None of the 10 files is among the 62 caches (`grep -cFxf` = 0) | DEVIATION ACCEPTED: no effect on any object read |
| D2 | W1-W5 were run by the operator's probe, not the harness | ACCEPTED, with a note | w_probe.ps1 and window.sh. The probe is stricter than rule 7: it refuses ANY python/java process, selftests included | NOTE (LOW, PR-3): "[W3] admitted PIDs: none" is a constant `echo`, printed only after CLEAR. It is correct here because CLEAR requires 0 foreign python/java, but it is not a computed list |
| D3 | pia/tm outputs are CRLF, records are LF; --strip-trailing-cr gives only the expected lines | CONFIRMED | `tr -cd '\r' \| wc -c`: new outputs 402 / 221 / 61 CR (every line); records 0. Plain `diff` on tm: 122 changed lines (61 x 2, CR only). `--strip-trailing-cr`: pia 1 hunk (L2), tm 1 hunk (L14), vfc the 17 of section 3. The scorer reads with universal newlines (`open(...).read()` in text mode) | as claimed |

## 3. (ii): every expected diff of R2.6-b2, checked by my own `diff --strip-trailing-cr <S>/rec_vote_frame_cert.txt <S>/ii/vote_frame_cert.txt`

Record 404 lines; new 402 lines. The C3 block goes from 4 lines to 3, and L403 is removed.

| # | record line | expected (93cc7de §3 / f387d58 R2.6) | got | verdict |
|---|---|---|---|---|
| 1 | L1 | exact b45b75db / b45b75db string | exact | MET |
| 2 | L4 | "62 SQLite files scanned" | 184 -> 62 | MET |
| 3 | L154-L157 (C3) | CERTIFIED-CONTESTANT, order-1 387/387, order-2 380 contestant, unresolvable 0 | `154,157c154,156`: exactly that; the "767 stored labels ... no name profile" note line is gone | MET |
| 4-9 | L176 / L180 / L184 / L188 / L245 / L275 | "UNCERTIFIABLE (R6), secondary, n resolved of m informative", with 111/1024, 187/1048, 182/993, 140/972, 29/279, 36/288 | exactly those six n / m | MET |
| 10-11 | L345 / L350 | H3 gains the transitive-scan sentence | The only change on each line is ONE inserted list element: "local imports scanned transitively at the run-time pin ... (D-C' (f)): rejudge_grok.py@fb8fb5bd2f1a, rubric_value_contrast.py@70370357d100" (L350 adds bias_audit.py@d76b1db5880f). The common prefix is 418 / 414 characters, and the tail after the insertion is identical | MET |
| 12 | L388 | "0 other scanned files" | 122 -> 0 | MET |
| 13 | L389 | classes 54 / 5 / 0 / 0 / 1 / 2 | 54 / 5 / 0 / 0 / 1 / 2 | MET |
| 14 | L400 | "P4 HELD: 1 UNCERTIFIABLE among the 60" | exact prefix | MET |
| 15 | L402 | six reasons, "(6) ... 0" | "(6) stored labels unresolvable (a name-profile gap: instrument knowledge, not frame) 0" | MET |
| 16 | L403 | removed | the "P4 reason OUTSIDE the five" line is absent: 0 occurrences in new | MET |
| 17 | L404 | "P4 is carried by: ['E-COMB, combiner not verified']" | exact | MET |

- **Nothing else moved.** `diff` shows no other hunk: 0 E1-E4 lines and 0 P1-P5 lines other than L400. L3 ("selftest (E3), executed in-process ... PASS") is unmoved and, per the ruling, is not evidence.
- **Classes.** The record's `Counter` of classes is {POS 54, CONT 4, UNCERT 2, NDO 2}; the new one is {POS 54, CONT 5, UNCERT 1, NDO 2}.
- **The one UNCERTIFIABLE left** is x12_crossdomain/rubric_contrast.db verdicts, R2 (pin timing). This is the record's own adjudication at L14618 ("1 after removing the RX artefact"). No verdict of record moves.

## 4. The six secondaries: n of m, and labels (JSON, and the caches themselves)

My JSON comparison of all 62 caches: exactly 6 secondary class moves, each CERTIFIED-POSITIONAL -> UNCERTIFIABLE, uncert_reason R6, resolved_klass CERTIFIED-POSITIONAL. The unresolvable totals are unchanged from the record (the F1 ungated counter adds 0 rows here).

| cache | n resolved | m informative | n + unresolvable = m | unresolvable_values (sum) | read-only census of `winner` (mode=ro&immutable=1) |
|---|---|---|---|---|---|
| causal_length/grok-reasoning | 111 | 1024 | 111 + 913 | gemini-3.1-pro_5-shots 371, iask_pro 276, arx_0314 178, gpt-4o-2024-08-06 88 (913) | the same four names at the same counts, TIE 164, '' 0 |
| causal_length/mistral | 187 | 1048 | 187 + 861 | 324 / 249 / 182 / 106 (861) | same, TIE 216 |
| causal_length/mistral_refgrok | 182 | 993 | 182 + 811 | 286 / 254 / 172 / 99 (811) | same, TIE 200 |
| causal_length/mistral_refgrok_v2 | 140 | 972 | 140 + 832 | 285 / 259 / 180 / 108 (832) | same, TIE 179 |
| x12_crossdomain/arxiask | 29 | 279 | 29 + 250 | iask_pro 126, arx_0314 124 (250) | iask_pro 126, arx_0314 124, TIE 49; `winner=''` 0 |
| x12_crossdomain/oracle | 36 | 288 | 36 + 252 | arx_0314 133, iask_pro 119 (252) | arx_0314 133, iask_pro 119, TIE 49; `winner=''` 0 |

- **The labels are contestant names.**
  - Every non-TIE stored `winner` is one of the pair's contestants: the same names appear in the units' contradict_contestant keys (e.g. '1026|gpt-4o-2024-08-06|iask_pro|original').
  - The counts equal unresolvable_values to the unit.
  - '' occurs 0 times.
- **P4 routing.** The P4 routing condition (all-'' labels) does not arise. By R-P4-2 (2a340dd) these are ordinary R6 findings, which R2.6 lists as expected.
- **What R6 means here.** The resolved tallies are DESCRIPTIVE, downgrade only. The primaries stay CERTIFIED-POSITIONAL, so no consumer's entered set is affected.
  - position_index_all.plan() selects by c["klass"] and u["klass"], not by the secondary (position_index_all.py L206-L222).
- **Cache integrity.** sha256_16 of the 6 caches, before and after my reads, equals the certificate: b2e2fb02 / c2e995ae / aa1b6f5f / 4b3c97aa / 157589b4 / eba8a8ac.

## 5. What (ii)/(iii) license, and what remains

**Licensed.** Reuse of vote_frame_cert.py blob:1a3d0bb5 / sha256-lf16:b45b75db7d98103e by VOTE-FRAME-CERT, POSITION-INDEX-ALL and TIE-MECHANICS. This is the condition of L17300 ("Reuse waits on VFC-FIXES-2's READY plus the section-5 delta check") and L17321 ("REUSE ... STILL WAITS on VFC-FIXES-2's delta READY showing (i), (ii) and (iii)"):
- (i) was shown by f387d58;
- (ii) and (iii) are shown here, on the bytes that main carries today (closure diff f76a93b..HEAD = 0).
- Pins of the consumers: position_index_all.py blob:bcbaf609 / sha256-lf16:9c78d485f37f442a; tie_mechanics.py blob:7f88d2ac / sha256-lf16:d6a1a0409a0fc06e.

**Not licensed by this result:**
- a new certificate;
- any change to VFC_PIN_LF;
- any re-reading of a class of record;
- reuse of any bytes other than those pinned above: any edit to the 15-module closure voids this;
- V-C5 (dynamic imports), which stays in force.

**Conditions:**
- **C1 (registrar).** Record this post-run by insertion: VFC-FIXES-2 (ii)/(iii) VALID; P3 MET with the four E3 transcript sha256 (py ad6aa8d0..., O 7de8842c..., pia e20271bd..., tm 0ce4cbcd...). Then close the queue item VFC-FIXES-2-DELTA-II-III.
- **C2 (RP-5).** Keep branch `worktree-agent-ad89ebf95e36802f5` until C1 is committed.
  - It is now (tip a9d8d7df), and it is the only ref containing 930ccc7 and a9d8d7d (`git branch -a --contains` prints only it).
  - After C1 it may go. f76a93b is an ancestor of HEAD (rc 0) and carries the reused blob.
  - The evidence of part (i) still cites 930ccc7. Either tag it before removing the worktree, or accept that part (i)'s build becomes unreachable.
- **C3 (certificate of record c731836): NO RE-ISSUE NEEDED. The registrar inserts a bracket instead.**
  - The ruling (93cc7de §5, standing) fixes c731836 and VFC_PIN_LF 72ceddfe as of record, and says "no new certificate". A re-issue needs its own registration (C5). It would also move the writer pin that position_index_all.load_cert checks, so the pia pin would move too.
  - No verdict moves:
    - E1-E4 and P1, P2, P3, P5 are unchanged;
    - P4 prints 1, which is the record's own "1 after removing the RX artefact" (L14618). P4 stays "HELD, PARTLY": it rests on ONE pin-timing exclusion (rubric_contrast R2), 0 under the registered definition.
  - The bracket, on the VOTE-FRAME-CERT outcome, states that under the fixed instrument b45b75db:
    - the _backup copy reads CERTIFIED-CONTESTANT, not UNCERTIFIABLE (RX);
    - the six E-COMB secondaries read UNCERTIFIABLE (R6), descriptive only, with the n of m of section 4;
    - reason (6) is 0 and the OTHER line is retired.
  - Consumers are unaffected: the _backup copy is excluded by prefix (position_index_all.py L177), and plan() reads primary classes only. That last point is READ from source, not executed against a re-issued certificate.
- **C4 (evidence).** See section 7.

## 6. Defects

| id | severity | defect | evidence | fix |
|---|---|---|---|---|
| PR-1 | LOW (scorer vacuity; did not bite) | score-vfc judges an expected diff only where one occurs, L1 excepted (L1 is positional). An expected change that FAILS to happen is not a finding | my mutant m2: the new L389 set back to the record's "CONTESTANT 4 ... UNCERTIFIABLE 2" gives rc 0 (pr_vfc/mut_vfc_m2.out). Discharged for THIS run by count: the operator's and my scorer runs list 17 expected entries, and my own diff shows all 17 hunks | in any later use of the harness, require that every expected record line id appear among the paired diffs (a count check, 17), as H1/H2 already do positionally for L1 / L2 / L14 |
| PR-2 | LOW (readout blind spot; did not bite) | The F1 READOUT compares cache and unit classes and unresolvable counts, not secondary class. The six R6 moves therefore do not appear in it, and the text scorer checks only the "n resolved of m" prefix. An all-'' label set on a secondary would pass both | my mutant m4 (the arxiask labels set to '') gives rc 0 (pr_vfc/mut_vfc_m4.out). Discharged here by my JSON and DB census (section 4: 0 '') | add the secondary klass and unresolvable_values to the F1 readout, and make '' in any unresolvable_values a FINDING (R-P4-3 already makes it an F5 finding) |
| PR-3 | LOW (procedural) | The W3 line is a constant echo, and leg rc / wall come from the operator's wrapper, not from the harness | window.sh | none needed for this run (CLEAR requires 0 foreign python/java). Future windows should print the admitted-PID list computed from the probe |
| PR-4 | INFO | The vfc leg took 9 s of wall time, against the ruling's UNMEASURED 5-15 min estimate | window.log | none. [PRE]/[POST] hash all 62 caches, so the speed is not evidence of a skipped read. Record 9 / 5 / 15 s as the measured costs |

Mutant controls on the real outputs (the scorer is not vacuous where it matters):
- a secondary n changed 111 -> 112: rc 3;
- a trailing token on an unrelated vfc line: rc 3;
- the same on an unrelated pia line: rc 3;
- the tm [POOL] line's pool id changed: rc 3;
- score-vfc with `--expect-lf 211112d41eed0b77`: rc 2, refused by name (RV4-1).

## 7. Evidence to archive (C4)

`<S>` is temporary and is NOT yet on the evidence disk: `find .../evidence_2026-09-25 -name e3_vfc_py.txt | wc -l` = 0. Copy all of `<S>` (13 MB) to `Z:\FAC\TUBerlin\THESIS\TaxoArena_data\evidence_2026-09-25\vfc_ii_iii\`, then verify by sha256.

The 25 files outside T are REQUIRED. The prefix shown is sha256[:16] of the file bytes as they sit on disk:

| file | sha256[:16] |
|---|---|
| step1_prep.txt | 7053058588e88398 |
| e3_archive_sha.txt | 4ae38b5cf691e637 |
| e3_vfc_py.txt | ad6aa8d0ef5b5073 |
| e3_vfc_O.txt | 7de8842ca2f12b46 |
| e3_pia_py.txt | e20271bd5bba66be |
| e3_tm_py.txt | 0ce4cbcdff45fbf3 |
| rec_vote_frame_cert.txt | 5e3af71cfd97e759 |
| rec_vote_frame_cert.json | 48e5f5a3d4dd02d0 |
| rec_position_index_all_outcome.txt | 1c4370b23474cf3c |
| rec_tie_mechanics_outcome.txt | 2b28ee178c466477 |
| window.log | f76854c4a678d3a2 |
| window.sh | bca53d6858d64484 |
| w_probe.ps1 | 312a4148cc179b77 |
| leg_vfc.txt | e55245b55bde2968 |
| leg_pia.txt | c90d007f794179e8 |
| leg_tm.txt | fda1941043d4de02 |
| ii/vote_frame_cert.txt | 677af84fa1a9e6b5 |
| ii/vote_frame_cert.json | 4a2b56c7188a901b |
| ii/steward_62.txt | be5c1f9188f7b2f8 |
| iii_pia/position_index_all_outcome.txt | 149cb95b57b5c030 |
| iii_tm/tie_mechanics_outcome.txt | 9491cca19e1b5269 |
| score_vfc.txt | fb37aa1f8d5a6bd3 |
| score_pia.txt | 5dd2e226b299c962 |
| score_tm.txt | da745b3a70494dbf |
| H/rerun_vf4.py | 818cfa3b66ba8b3a |

- The four rec_* sha equal the sha256-lf16 of the records of reference in READY f387d58 R2.1.
- **T/** can be regenerated from f76a93b (my `diff -r` differs only in `__pycache__`). Archiving it too is cheap and preserves the exact executed tree.
- **My scratch** `<scratchpad>\pr_vfc\` (Tdiff.txt, my_score_*.txt, mut_*.out, paths62.txt, b0c_files.txt) is optional supporting evidence.

## 8. What this review does not show

- It does not show that an instrument never swallowed an audit refusal. The transcripts show none, and the byte checks show nothing of record changed.
- It does not show how consumers behave when fed a RE-ISSUED certificate. (iii) ran, as ruled, against the certificate of record.
- It does not re-execute the selftests or the legs. The counts are recounted from the transcripts, which are pinned by sha above.
- It does not close V-C5 or VFC-FIXES-2 D1 / D2.
