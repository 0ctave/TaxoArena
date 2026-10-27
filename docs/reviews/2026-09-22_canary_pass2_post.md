# Post-run review 2026-09-22: CANARY-BASELINE pass 2

adversarial-reviewer (agent abd6f74a7e8c16d08), zero calls; both caches opened mode=ro&immutable=1; scratch `canary_review/recompute.py`. Nothing written under docs/, tools/ or experiment_results/ by the reviewer; the two insertions it prescribed were applied by the orchestrator (4178a7c).

## Per-claim table

| # | claim | verdict | got vs claimed | how |
|---|---|---|---|---|
| 1 | pass-1 cache untouched: sha 5142795bdc8c5a8e..., run_meta resumed ["2026-09-16 01:44:41"], no relaunch key | CONFIRMED | sha identical; 12 run_meta keys; 24 columns | sha256sum; run_meta dump |
| 2 | pass-2 cache: 300 rows / 300 distinct, 26 columns, provider1/provider2 | CONFIRMED | all verdict cells non-null on 300 rows; 0 empty raw responses | recompute |
| 3 | pass-2 run_meta: judge, STACK-v2, 8192, temperature omitted, set 50af669ac6997f9f, pool p2dca, script sha in the READY's set | CONFIRMED | script_sha256_16 976207e2bb8934c3; started 10:53:59; resumed ["10:54:44"] | run_meta |
| 4 | script of record: blob 7d9a4e2e7bd11ef662ec813c99f19a2ff1561875, LF d62dc048ba6e9cf9, CRLF 976207e2bb8934c3, ea9fbc7 | CONFIRMED | | git |
| 5 | fingerprint {'azure:grok-4-1-fast-non-reasoning': 600}; finish {'stop': 600}; invalid 0 | CONFIRMED | ctok max 457/468 (cap 8192); pass 1: 600 stop, 0 invalid | recompute |
| 6 | pilot = first 12 ids, inside the 300, no re-post; log counts 12 + 288 | CONFIRMED | earliest 12 rows = set[:12] = {332, 803, 1166, 1303, 1678, 2299, 3520, 4653, 5313, 6206, 6716, 7713}; pass 1 used the same 12 | recompute + logs |
| 7 | set integrity | CONFIRMED | 300 ids == pass1 == pass2; 0 static-field mismatches; 279 q, 61 pairs; frontier 137 / keytie 13 / cross 150 | recompute |
| 8 | inputs of record untouched | CONFIRMED | grok-reasoning.db 536e3f463ced750b (mtime 09-10); rubric_ladder.db 09-08; canary_set.json 09-15 | find -newermt |
| 9 | FLOOR convention B: contested 13/150 = 0.087 [0.041, 0.140] SE 0.0247 DEFF 1.16; cross 13/150 = 0.087 [0.046, 0.135] SE 0.0230 DEFF 1.00; all 26/300 = 0.087 [0.056, 0.122] SE 0.0170 DEFF 1.09 | CONFIRMED to the digit | own clustered bootstrap (seed 42, 2000) reproduces; independent numpy bootstrap (seed 7, 4000): [0.041, 0.138] / [0.045, 0.133] / [0.056, 0.120] (MC noise only); unrounded 0.086667 on all three | recompute |
| 10 | convention A = B; 0 pairs dropped | CONFIRMED | 0 INVALID and 0 finish=length in either pass | recompute |
| 11 | agreement 0.913; decisive-only disagreement 0.000 (n=102/113/215); per-order raw vote disagreement 0.110/0.087/0.098 | CONFIRMED | ALL 26 disagreements are TIE<->decisive (16 TIE->decisive, 10 decisive->TIE), 0 direct reversals; 23 further matches change a raw order vote but keep the verdict; 0 byte-identical raw responses between passes | recompute |
| 12 | ALARM thresholds: n=300 0.138; n~1,000 0.115 | CONFIRMED | 0.086667 + 3 x 0.0170 = 0.1376; 0.086667 + 3 x sqrt(p(1-p)/1000) x sqrt(1.09) = 0.1146; n = 900: 0.116; per half at n=150: contested 0.161, cross 0.156 (descriptive) | recompute |
| 13 | Rule (ii): F_c <= 0.114 both conventions | CONFIRMED -> NO ALARM | DECOMP 17/299 = 0.0569 verified (decomp_outcome.txt L10); 0.057 + 3 x sqrt(0.057 x 0.943/150) = 0.1138 | recompute |
| 14 | Rule (i) band reading | CONFIRMED as printed | 0.087 OUTSIDE [0.040, 0.060] inclusive (13/150 = 0.086667); cross = contested -> "does not hold"; both DESCRIPTIVE; the contested CI contains the band and DECOMP's 0.057 | outcome L30 |
| 15 | "ALARM STATE:" line present | REFUTED at 5b709bd (absent; the script has no such print) -> INSERTED flush-left at 4178a7c | grep |
| 16 | pass-1 descriptives of record unchanged (rule (v)) | CONFIRMED | byte-identical lines between 7076615 and HEAD; recomputed 42/150, 29/150, 50/65, 53/65; 33/150, 26/150, 72/78, 74/78; 75/300, 55/300, 122/143, 127/143 | git diff; recompute |
| 17 | what --analyze changed beyond the pass-2 sections | CONFIRMED, three items | header sha and cache name; two pass-1-era lines deleted ("FLOOR: pass 2 not judged yet...", "Prediction on record..."); the pass-1 fingerprint line added. The file of record for pass 1 is 7076615 (0ba096f is the programme record) | git diff |
| 18 | pass-2 key-decidable accuracy reproduces pass 1 within noise | CONFIRMED | all n=143: 0.874 / 0.899 (vs 0.853 / 0.888); paired 0:3, exact McNemar p = 0.25; the 3 gains are a pass-1 TIE becoming the key's side | recompute |
| 19 | tie rates per pass | CONFIRMED | 75/300 = 0.250 -> 69/300 = 0.230; paired 16:10, p = 0.327; flip 55 -> 48 | recompute |
| 20 | outcome commit hygiene | CONFIRMED | 5b709bd one file; pass DBs untracked (un-ignored by .gitignore:145); logs ignored | git |

## Defects, ranked
1. MEDIUM (record completeness): no machine-readable "ALARM STATE:" line in the outcome; consumers (placement_steps.py:142) require it at column 0. INSERTED at 4178a7c: `ALARM STATE: NO ALARM` after the ALARM line.
2. MEDIUM (fragility): `--analyze` opens the outcome in mode "w" (L464): a re-run wipes the inserted lines and re-prints the stale MDE literal. `--analyze` is forbidden on this file until an engine-coder adds the ALARM STATE line, the convention-A line and a measured-SE MDE line to the script (zero calls, re-pin the LF sha) before epoch 2.
3. LOW (rule (iv)): convention-A floor not in the file. INSERTED at 4178a7c beside the "all" floor.
4. LOW (stale literal): "(a single pass pair of 300 has MDE ~2.7pp ...)" is registration text at DECOMP's 0.057, binomial. At the measured floor: 1.96 x SE = 3.3pp at n = 300 (DEFF 1.09), 1.8pp at n ~ 1,000; the 3-SE one-sided alarm at n = 300 fires only at 0.138, a +5.1pp drift; FRAMEWORK L141's "power ~0.59 against a 3pp drift" is lower at 0.087. Bracketed in the file at 4178a7c; the script should print from the measured SE.
5. LOW (denominator wording): "n~1,000 (three epochs pooled)": three epochs x 300 = 900; threshold 0.116 at n = 900 vs 0.115 at n = 1,000.
6. LOW (comparator caveat): DECOMP's 17/299 is a per-call, single-order disagreement (ARENA-13 arm A, hours apart); the canary's F_c is the combined dual-order verdict. Like-for-like: per-order raw vote disagreement, contested 33/300 = 0.110 (1.9x DECOMP), cross 26/300 = 0.087, all 59/600 = 0.098; unclustered z ~ 2.3 vs DECOMP (different population, reference and gap: not a drift test). The record must not write "consistent with DECOMP's 0.057" without this caveat.
7. LOW (stale artefact): canary_baseline_outcome_partial.txt (pilot readout, DEFF nan) is untracked-not-ignored; never commit.
8. LOW (informational): the MODEL-VINTAGE precheck commit 50d1d23 landed at 10:54:06 while the pilot was posting (first pass-2 row 10:54:09); no concurrent pool read observed (52 s apart).

## Sentence of record
"CANARY-BASELINE pass 2 (2026-09-22 10:53:59-11:01:01, 600 calls, provider1/provider2 azure:grok-4-1-fast-non-reasoning x 600, finish stop x 600, 0 INVALID; script blob 7d9a4e2e7bd11ef662ec813c99f19a2ff1561875, run_meta sha 976207e2bb8934c3 = CRLF rendering of LF d62dc048ba6e9cf9; pass 1 2026-09-16, no fingerprint recorded): the set's own retest floor on the frozen 300 matches (50af669ac6997f9f, 279 questions, 61 pairs) is 26/300 = 0.087 [0.056, 0.122], SE 0.0170, DEFF 1.09 (question-clustered bootstrap); contested 13/150 = 0.087 [0.041, 0.140] SE 0.0247 DEFF 1.16; cross-tier 13/150 = 0.087 [0.046, 0.135] SE 0.0230 DEFF 1.00; convention A = convention B on every line (0 INVALID or non-terminated in either pass, 0 pairs dropped). Every one of the 26 disagreements is a TIE against a decisive verdict (16 TIE -> decisive, 10 decisive -> TIE); the 215 matches decisive in both passes never reverse. ALARM STATE: NO ALARM (contested floor 0.087 <= 0.114 under both conventions, rule (ii)); the next epoch reads floor + 3 SE = 0.138 at n = 300 and 0.115 at n ~ 1,000 pooled (0.116 at n = 900; contested 0.161 and cross 0.156 at n = 150 beside them, descriptive). Prediction 'floor 4-6% on the contested half': OUTSIDE at the printed 0.087 (unrounded 13/150 = 0.086667; the interval contains the band and DECOMP's 0.057); 'cross-tier lower than contested': does not hold (0.087 vs 0.087); both descriptive by rule (i). Criterion (measured floor and agreement with interval): READ. Key-decidable accuracy pass 1 -> pass 2 on n = 143: 0.853 -> 0.874 ties-wrong, 0.888 -> 0.899 ties-half (paired 0:3, p = 0.25); tie rate 0.250 -> 0.230 (16:10, p = 0.33)."

## Chips
FLOOR 0.087 [0.056, 0.122] (26/300, DEFF 1.09) | CONTESTED 0.087 = CROSS 0.087 | CONV A = CONV B (0 INVALID) | ALARM STATE: NO ALARM | THRESHOLD 0.138 @300 / 0.115 @~1,000 | PREDICTION 4-6% OUTSIDE (descriptive; CI covers the band) | CROSS < CONTESTED DOES NOT HOLD (descriptive) | ALL 26 DISAGREEMENTS AT THE TIE BOUNDARY, 0 REVERSALS | KEY-DECIDABLE 0.853 -> 0.874 (0:3, p = 0.25) | FINGERPRINT PASS 2 ONLY (600 x azure:grok-4-1-fast-non-reasoning) | CRITERION READ

## What pass 2 does not show
One retest pair, ~6 days apart, on one requested deployment: a floor, not a drift test. Pass 1 carries no fingerprint; pass 2's is the echoed model name (no system_fingerprint), so a silent redeploy under the same name is invisible. The floor is not shown equal to DECOMP's 0.057 (like-for-like per-call contested 0.110; different population). n = 150 per stratum cannot separate contested from cross (13/150 each) nor the 4-6% band from 0.087. The retest noise is entirely at the TIE boundary (26/26); nothing about reversals of decisive verdicts beyond 0 of 215 observed. No accuracy or tie-rate drift (0:3, 16:10 within noise). MDE / power figures in the file and FRAMEWORK L141 are stated at 0.057; at 0.087 the one-epoch alarm needs +5.1pp. Amendment 4's re-use key is verifiable from pass 2 onward only.

## Verdict
Numbers CONFIRMED to the digit; the outcome file is complete after 4178a7c (ALARM STATE + convention A + MDE bracket); READ / NO ALARM; ledger row patchable with the chips above.
