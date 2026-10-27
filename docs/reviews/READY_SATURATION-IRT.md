# READY review: SATURATION-IRT (HF post 1), first full review

Reviewed: branch `worktree-wf_42805bc7-f2d-3` at tip `f2fbb6d5` (parent `d999e689` = main; `merge-base --is-ancestor` OK).
Blob: `tools/analysis/saturation_irt.py` blob:93116fec4231416bc3fcbfac21c22dc64a54ffed (git hash-object; the working tree is LF,
no CRLF bytes) / sha256-lf16:1001445c2bb4e739 / sha256-crlf16:ea0e16f03d806f23 (as the script prints it). The builder commit
changes exactly 1 file (`git diff --stat d999e689..f2fbb6d5` prints "1 file changed").
Registration: `docs/judge_v2_program.md` L25051-L25064 (+ R1-R6 at L25043-L25049), as of d999e689.

## VERDICT: NOT READY (BLOCKED by B1 only). After the B1 fix, a DELTA review (the diff, selftest, mutants, one real `--dry-run`) can return READY.

B1 stops the real `--dry-run` before it computes anything. I executed the dry-run read-only: busy.ps1 exit 1 first, and
multicorpus_cache_v1.db sha256 ad66e30a0eb4abd6 was the same before and after. Its last line is
`[SI] REFUSED: corpus_questions sources [... 'MMLU_PRO' ...] != the six registered [... 'MMLU_PRO_LB' ...]`.
Everything else on the deciding path is sound: the criteria, the twin rule, the data object, the Support arithmetic, the
release surface, zero calls, and the selftests and mutants.

## Per-claim table (deciding claims only)

| # | claim | reviewer's number / evidence | status | sev |
|---|---|---|---|---|
| 1 | R1: exact-text twins = 471 ids / 427 texts, refusal otherwise | 471 / 427 recomputed by my own script from corpus_questions + the paeec id file (GPQA 288, MMLU_PRO 179, BBH 2, MATH 2). Matches the audit's exact 471 / 427 (review 1df2cf1, row 1) | CONFIRMED | - |
| 2 | Remaining exact duplicates collapse to the lowest id | 589 dropped; 20,546 kept: MMLU_PRO 11,637, BBH 5,757, MATH 1,309, MUSR 756, GPQA 546, IFEVAL 541 ("about 21,000" registered). 13 collapse groups span MATH and MMLU_PRO (D6) | CONFIRMED | - |
| 3 | Items need all 18 cells; refusal above 1% incomplete | 0 of 20,546 incomplete. View rows 272,520 + 116,388 = 388,908 = 18 x 21,606; 0 duplicate (model, qid) rows; 0 response-source mismatches; no qid appears in both views | CONFIRMED | - |
| 4 | Roster 18 ACTIVE, Meta-Llama-3-70B-Instruct absent, pool row 5,642 / 6,153 | both views: 18 ACTIVE, Llama-70B not ACTIVE; pv2_1575de61bb20e977 = 5,642 / 6,153 | CONFIRMED | - |
| 5 | Source labels = the six registered | the DB says `MMLU_PRO`; the script's SOURCES says `MMLU_PRO_LB`. The real dry-run REFUSES (REFUSE.SOURCES). The fixture uses the same wrong label, so the selftest cannot see it | REFUTED | BLOCKER (B1) |
| 6 | SI1: KEEPS iff tau_LOMO >= 0.90, the POINT decides, printed "(descriptive-only by support)"; rule 8; F-SI = LOSES AND hi < 0.90 | code L612-L668 match the registration word for word; boundaries are killed by X01 / X03 / X04 | CONFIRMED | - |
| 7 | LOMO: m's own responses never choose m's items | st_lomo flips m's responses, refits the full model too (so the warm start changes), and m's set does not move. My Y1 (cold-start LOMO) SURVIVES, so the warm start from the 18-model fit leaks nothing on the e2e fixtures. The e2e oracle refits unpooled from a cold start and agrees to 5e-5 | CONFIRMED | - |
| 8 | SI2: NEFF_b = share of N_b with a^2 p(1-p) >= 0.10 at theta_top4 (2PL, that benchmark); ALL / NONE count 0; strict > | L752-L761, L620; X06 / X07 / X23-X25 and my Y2 are killed | CONFIRMED | - |
| 9 | Support: SE 0.0146, MDE80 0.041, n_eff 1,750, DEFF 1.2 transported from G13's 1.214; SI1 DESCRIPTIVE-ONLY | re-derived: Var(D) 3.68, SD 1.918, SE590 0.0251, x sqrt(1.2) 0.0275, x sqrt(590/2100) 0.0146, MDE 0.0408, n_eff 1,750. Realised data: k_total 2,056, Kish 1.0003 after the collapse (so DEFF is about 1.0) -> SE 0.0134, MDE 0.0376, n_eff 2,055. Predicted 0.93 is 0.03 from the bar, still inside the MDE: DESCRIPTIVE-ONLY holds | CONFIRMED | - |
| 10 | [R-b] k_b = round-half-up(0.10 x N_b) over all deduplicated items | matches the Support's "MMLU about 1,180, IFEVAL about 54": k = 1,164 / 576 / 131 / 76 / 55 / 54. My Y4 (floor) is killed | CONFIRMED | - |
| 11 | [R-d] identical-column pooling is exact | the objective is a w-weighted sum of per-item (ll + prior) terms. The e2e oracle (unpooled) agrees; X64 is killed | CONFIRMED | - |
| 12 | [R-a] MAP read as "posterior-mean a_i"; [R-e] seeds 20261009 / 20261010 | readings, not results. Acceptable; the registrar records them | ACCEPTED (reading) | LOW |
| 13 | Zero calls | no network, judge or .env import (whole-file grep: the 3 hits are all os.environ thread / data-root lines) | CONFIRMED | - |
| 14 | No GPQA text, no raw outputs in exports | `text[...]` is used only in r1_twins, collapse and stem_key (whole-file grep above the SELFTEST marker). The SELECTs read only model, legacy_qid, source, is_correct, is_correct_mathfix (never output_zlib, answer_text or pred). The figure JSONs hold ids, 0/1, parameters and model names; e2e asserts no GPQA text in any output | CONFIRMED | - |
| 15 | R2 extractors | IFEval is_correct = IMPORTED prompt_level_strict_acc (tools/analysis/data_v2/ingest.py L54; CHECKER-ANSWER-INGEST validated it); MATH uses the MATH-FIX overlay; X32 is killed | CONFIRMED | - |
| 16 | Selftest 14/14; mutants 70/70 killed, control survives | selftest 14/14 re-run (43 s, scratch sandbox). Mutants: see the mutant line below | CONFIRMED | - |
| 17 | P5 "holds by construction" | true: the 2PL nests Rasch at log a = 0, where the a-penalty is 0. So P5 is a VACUOUS prediction (D5) | CONFIRMED (vacuity) | LOW |

Mutants, builder suite (re-run by me in the sandbox): 70 of 70 KILLED; X00 control SURVIVED; 0 not applied (whole-log grep: 71 KILLED-or-control lines, 0 other survivors). CONFIRMED.
Reviewer's mutants (sandbox; control X00 SURVIVED):
- Y1: LOMO cold start (no warm start from the 18-model fit). SURVIVED, as expected for an equivalence probe; decisive: it is the leakage probe.
- Y2: top 4 ranked by micro instead of macro. KILLED; decisive for SI2 / SAT4.
- Y3: NEFF uses `>` instead of `>=` at 0.10. SURVIVED; not decisive (the boundary has measure zero for continuous information).
- Y4: k_b by floor instead of half-up. KILLED; decisive for the SI1 subset.

## Defects (fix each)
- **B1 BLOCKER.** `SOURCES` / `MMLU` use `MMLU_PRO_LB`, but corpus_questions and both views use `MMLU_PRO`, so every real mode
  refuses at REFUSE.SOURCES. Fix: key the data on `MMLU_PRO`. If the registration's name is wanted in print, keep
  `MMLU_PRO_LB` only as a display alias. Move the fixture `_spec` to the real label, so the selftest exercises the label of record.
- **D2 MEDIUM (rule 7 / CPU lane; a condition, not code).** The pool read lasts seconds, but the job then runs about 2-2.5 h on the
  CPU, and busy.ps1's regex does not match `saturation_irt`, so peer workflows cannot see the run. Rule 7 also requires the CPU
  lane to pause during constructions. Fix: for the run window, the operator adds `saturation_irt` to the busy.ps1 pattern (or the
  orchestrator rules that this one-thread overlap is acceptable), and launches only when busy.ps1 exits 1.
- **D3 LOW.** The dry-run COST line prints "about 3.5-4.5 h"; the docstring and the builder say 2-2.5 h. Make them agree; the pilot
  re-times the run either way.
- **D4 LOW.** The items JSON carries `release="ids + parameters only (R4 / R5)"`, which misstates R5 (ids + 0/1 only). Relabel it
  "figure data, not a release; a release is ids + 0/1 (R5)".
- **D5 LOW (registrar).** P5 cannot fail (nesting). The registrar brackets it as non-informative, and its Brier credit is not counted.
- **D6 LOW.** 13 exact-text groups that span MATH and MMLU_PRO are collapsed across benchmarks to the lowest id. This is the
  registered rule; print the cross-source count beside the per-source drop counts.

## Delta re-review needs (after B1)
The diff touches only the source label and the fixture. Selftest 14/14; the mutant suite with 0 survivors; Y2 and Y4 above.
One real `--dry-run` must print R1 471 / 427, 589 collapsed, kept counts 11,637 / 5,757 / 1,309 / 756 / 546 / 541
(total 20,546), roster 18, pool row 5,642 / 6,153, and the multicorpus sha before = after.

## Commands (all read-only; DBs opened `mode=ro&immutable=1`; busy.ps1 exit 1 checked before every DB read)
```
git -C .claude/worktrees/wf_42805bc7-f2d-3 hash-object tools/analysis/saturation_irt.py   # 93116fec...
git -C .claude/worktrees/wf_42805bc7-f2d-3 diff --stat d999e689..HEAD                      # 1 file changed
python E:/TaxoArena_tmp/rev_satirt/r1.py          # twins 471/427, collapse 589, kept 20,546, complete 20,546, Kish, k_b
python -c "<views: rows, dup (model,qid), source mismatch, pool row>"   # 272,520 / 116,388, dup 0, mismatch 0, 5,642/6,153
python tools/analysis/saturation_irt.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # REFUSED: sources (B1)
sha256sum multicorpus_cache_v1.db  (before / after)   # ad66e30a0eb4abd6 both
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest   # 14 / 14
python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --mutants    # builder suite
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/rev_satirt/my_mut.py         # Y1-Y4
python -c "<Support arithmetic>"   # 0.0251 / 0.0275 / 0.0146 / 0.0408 / 1750; realised 2,056, 0.0134 / 0.0376
```

## Run command after the B1 fix is READY (operator; from main after the merge, or from the worktree with --data-root)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # must exit 1; add saturation_irt to its pattern for the window (D2)
python tools/analysis/saturation_irt.py --dry-run [--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena]
python tools/analysis/saturation_irt.py --pilot 3 [--data-root ...]
python tools/analysis/saturation_irt.py --run [--data-root ...]     # back up outputs to E:/TaxoArena_backup_<date>_saturation_irt
```
