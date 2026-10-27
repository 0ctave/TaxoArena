# Post-run review — MODEL-VINTAGE-CANARY instrument step 0b, the stamp run (9fa2545)

Adversarial reviewer, 2026-09-22, zero calls. Objects: `experiment_results/x12_crossdomain/model_vintage_v0_harness.json` (18,621 B, sha256 97f85a093e042f9f172f6fbd8f25635d737e5285843bc8bdd3ecd801e349c0e1) and `.txt` (10,913 B, sha256 93c8a4826253bc93f8f7c8c1d94727adc46eca04c0ca1e2629731e91fcac5f02), both mtime 12:27:00.626, 0 CR bytes, committed 9fa2545 (2 files, 872 insertions, nothing else). Script at run time: 53fda56, LF sha 599d6e07aaf478f2a6e2232208544b9b4521bd4a99db5be1d27c967f712e4e78 (in both headers; working tree still == HEAD). Reference numbers: the reviewer's own recomputation of the READY (dbae0a4; scratchpad indep_canary.py / indep_full.out: own regexes, own SQL, `mode=ro&immutable=1`).

## Per-claim

| claim | verdict | got vs claimed | how |
|---|---|---|---|
| sidecar validates | CONFIRMED | `validate_sidecar(json.load(...)) == []` | `python -c` import of the script, read-only |
| meta | CONFIRMED | script_sha_lf 599d6e07...4e78; extract_v1_sha b9782bef338e4815; variant_shas tier1-blank-v1 cbed6f92deece096 / three-tier-v1 b9782bef338e4815 / three-tier-G-v1 14f7b3bce20bcdfd; set_hash 50af669ac6997f9f; pool_id p2dca21ab5f4ef3ae; judge_calls 0; x12_matches_verified 300; mode run; date 2026-09-22 12:27:00; fulltable_seconds 334.0; families 5 / 2 / 5 verbatim | own compare |
| canary 3 x 12 table (agree counts and rates) | CONFIRMED | 36 / 36 cells equal to the reviewer's counts (exact integers, rates to 1e-12) | own compare |
| full-table 3 x 12 column (agree counts, rates, rows) | CONFIRMED | 36 / 36 cells and the 12 row counts equal (12032 x 9, arx 12005, gemini 12020, iask 11939; arx 11907 / 11924 / 11924) | own compare |
| the stamp rows (harness_id, variant, n, agree, Wilson) | CONFIRMED | 12 / 12: harness_id = FAMILY_ASSIGNMENT for every model, refused False x 12; n 279 x 11 + 278; eleven at 279/279 (278/278), arx_0314 277/279 = 0.9928 [0.9742, 0.9980] (own Wilson to 5e-5) | own compare |
| residual qids | CONFIRMED | arx_0314 [(4941, B, I, t3), (7433, B, H, t3)]; [] for the other eleven | own compare |
| criteria | CONFIRMED | A1 HELD; C1H HELD (12 of 12); A2_count 0, A2_refused []; A3 arx_0314 2, others 0; premise_overturned False; contradictions = exactly ["gemini-3.1-pro_5-shots: CONTRADICTION-TIE (...)"]; rule_check AGREES x 10, arx_0314 AGREES-BY-EXCEPTION (canary_tied all three, fulltable_tied [three-tier, three-tier-G]), gemini CONTRADICTION-TIE; FULLTABLE-AGREES x 12 | own compare |
| P-A1 / P-A2 / P-A3 HELD; P-A4 not scorable | CONFIRMED | .txt L86-L89 | grep |
| .txt = the dry-run text | CONFIRMED | the reviewer's 12:03 dry-run output and the committed .txt are identical modulo the header timestamp (diff empty) | diff |
| DB stat pins unchanged | CONFIRMED | mmlu_pro_dataset_cache_v2.db 974917632 B 2026-09-19 16:30:10.106974800; -wal 0 B 2026-09-19 16:58:06.750922000; ratings_x12.db 11550720 B 2026-09-06 02:42:21.060766200; canary_set.json 71465 B 2026-09-15 19:48:12.947628500; model_vintage_extractor_check.txt 6181 B sha a3b9439d...48b2; -shm mtime 12:21:17 = the run's pool_guard open (READY defect 1; 12:27:00 - 334 s - seconds), not a write | stat |
| commit footprint | CONFIRMED | 9fa2545 touches the two sidecar files only | `git show --stat` |
| READY condition 3 (brackets before the run) | CONFIRMED | 2b88766 12:16:23 inserted brackets 1-3 at L9711 / L9718 / L9719 (programme diff 0 deleted lines) before the run's 12:21 start; 9fa2545 cites them | git log / diff |
| rule-7 window | CONFIRMED as stated | the operator's message records a worktree gradle test run waited out before launch; the run is a pool reader and the DB pins are unchanged | commit message; stat |

## Defects

None new. The three LOW items of the READY stand as recorded (pool_guard `mode=ro` without `immutable=1` moves the -shm; [RESOLVED 2026-09-23 by the registrar: POOL-GUARD-IMMUTABLE MERGED at d30c19e (pool_guard.py blob:6521b51ac0fce04063563f9e6dcf42554ad86591 / sha256-lf16:8ca50c0fba9b8ce3 / sha256-crlf16:5c528e083c4120d2); open_ro now opens mode=ro&immutable=1 and moves no -shm or -wal (reviews d72c790 claim 1d, cc0ccc9 R3); docs/judge_v2_program.md L14591-L14599.] selftest check 10's 11925 vs the real 11924; the sidecar's `meta.assignment_rule` carries the superseded "ONE stated exception" wording, corrected by brackets 1-2 at L9718-L9719).

## Sentence of record (ledger row covering steps 0 + 0b)

"Leaderboard pred columns are harness artefacts; under one extractor 5 of 12 reproduce at >= 0.99, under each model's own harness extractor 12 of 12; the stamp of record is model_vintage_v0_harness.json."

Numbers behind it: step 0 (model_vintage_extractor_check.txt, 50d1d23) extract-v1 alone: 5 of 12 at >= 0.99 (arx_0314 0.9928; deepseek, gemini, gpt-4o, iask_pro 1.0000; the seven others 0.8674-0.9785), C1 as registered FAILED, registrar's >= 10 of 12 FAILED. Step 0b (model_vintage_v0_harness.json, 9fa2545): each model under its fixed family's variant: 11 at 1.0000 and arx_0314 277/279 = 0.9928 [0.9742, 0.9980]; A1 HELD, C1-H HELD 12 of 12, A2 0, A3 arx_0314 2 (q4941 B/I, q7433 B/H); families H-tier1-blank x 5 / H-constantG x 2 / H-threetier x 5; one rule-wording contradiction recorded (gemini, CONTRADICTION-TIE: an uninformative all-1.0000 canary tie; membership unchanged; full table 0.9980 / 1.0000 / 0.9986 identifies three-tier), arx_0314 AGREES-BY-EXCEPTION with a three-way tie; full-table column agrees with every membership.

Chips: `C1 FAILED (one extractor, 5 of 12)` · `C1-H HELD (own harness, 12 of 12)` · `A1 HELD` · `A2 0 REFUSED` · `A3 arx_0314 2 residual` · `P-A1 P-A2 P-A3 HELD` · `1 CONTRADICTION-TIE (gemini, wording; membership unchanged)` · `0 calls` · `sidecar write-once 9fa2545`.

Does not show: any model drift (no v1 exists); F_gen, F_cache, a_m, the alarm (C2-H, C3-H, C4 need the author's generation pass); a fourth extractor (no regex added to extract-v1); any change to pred, is_correct or a verdict; that a family's variant is the submitter's actual code (a behavioural signature reproduced at 1.0000, not a provenance); gemini's fallback behaviour from the canary (only the full table shows it); the frontier order.
