# READY review (pre-data): BZ-AXIS-CONFIRM-MMLU (draft blob 22cfd6a7, LF; commit 5f64b3b8)

Reviewer: adversarial reviewer, 2026-10-21, `_as_of ca7728d7`. Zero runs, zero LLM calls; no MMLU (original) result
opened. Read: the draft; author decisions 2026-10-21 D-1..D-3; benchzoom 450b86e (`examples/fetch_zoom_data.py` blob
f39c27d8, `src/benchzoom/sources.py` blob 67752ddc, both LF = working tree); BZ-METER-AXIS `outcome.json` (MMLU-Pro
L3a-L2 stats); the HELM bucket LISTING (run names only, no instances, no predictions).

## Verdict

**READY WITH EDITS, for the registration TEXT only.** This is not READY-1 (the draft defines READY-1 as registration +
code + synthetic gate + census + tree pins) and it authorises no HELM or tinyBenchmarks read. Edits E1-E8 go in as
`[D<n>]` brackets before the registration commit. Condition F1 (fetcher gate) must be fixed before ANY `helm` or
`tinylb` invocation: as committed, the gate opens on this file, on the draft, and on a file that says "NOT READY".

## Reviewer questions settled

- **Q3 deciding statistic: plain `G(L3a | L2)` decides (C-M1); the difficulty + length form stays secondary (C-M3).**
  A confirmation must test the statistic that was SUPPORTED (BZ-METER-AXIS decided on uncontrolled `L3a|L2`); making the
  controlled form deciding would be a criterion substitution (C-7). Difficulty is already in the backbone (LOMO Rasch
  b_ij plus the model-specific difficulty slope v_j, meter_registration Section 1). Wording edit E3 limits what a plain
  SUPPORTED may claim.
- **Q4 census thresholds: KEEP 99% coverage (>= 13,902 of 14,042 items) and <= 1% unmatched per model.** The run specs
  carry `max_eval_instances` 10000, 5 shots, 1 trial (v1.13 run-spec file, 4,503 runs, 79 models x 57 subjects), so a
  complete run covers each full subject test set; the thresholds only remove broken runs. **The newest-release dedup
  rule is kept but is VACUOUS on the real listing** (0 of 80 models appear in more than one release); what the listing
  DOES need is a prompt-variant rule (E5): 15 runs carry `additional_instructions=yifan` (claude-3-opus and
  claude-3-sonnet duplicate 5 subjects each in v1.0.0; google_gemini-pro has ONLY these 5 runs).
- Q1, Q2: answered by the author (D-3: "Keep MATH separate"; "17 coarse, 57 fine"); E1.

## Per-claim table (deciding claims)

| # | claim (draft) | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | HELM roster 81 models after dedup over v1.0-v1.13 | listing: 4,575 runs, 14 releases, 81 model names; excluding the 15 `additional_instructions` runs: **80 models, all 57 subjects, 0 in >1 release, 0 duplicate (model, release, subject)**; gemini-pro has 5 subjects only (yifan) and is dropped by any rule | PARTLY (80, not 81) | MEDIUM |
| 2 | code takes the newest release per model | `helm_latest_by_model` on the real listing RAISES `anthropic_claude-3-opus-20240229 / abstract_algebra: two runs in release v1.0.0`: the fetcher cannot run as committed | REFUTED (code) | HIGH (F2) |
| 3 | DEFF 1.13, n_eff 4,134 "POSTRUN claim 5" | outcome.json mmlu_pro L3a-L2: deff 1.125713, n_eff 4,134.27, se 0.0183072, se_cell_iid 0.0172547, mde80 0.0702997. Numbers CONFIRMED; the source is outcome.json (POSTRUN claim 5 does not print DEFF/n_eff); DEFF = (SE/SE_cell_iid)^2, i.e. within-item correlation ACROSS MODELS, not twin clusters (draft (a)-(b) attribute it to Kish 1.01) | PARTLY | LOW (E6) |
| 4 | SE 0.0167 = 0.0183 x sqrt(4,654/5,617); n_eff 4,971; stress 0.0371; MDE80 0.064 / 0.142 | 0.016658; 4,970.8; 0.037097; 0.06413 / 0.14246 | CONFIRMED | - |
| 5 | transport is conservative (no roster credit) | at constant ICC rho = (1.1257-1)/22 = 0.00571: DEFF at 80 models = 1.451, SE(80 models, 5,617 items) = 0.0102, MDE80 0.039 < 0.064: the transported SE is conservative even though DEFF GROWS with the roster | CONFIRMED | - |
| 6 | power: g=0 prints NOT SUPPORTED > 0.99; g=0.12 SUPPORTED ~0.88 | P(g_hat+2SE<0.10 given g=0) = 0.99997; P(g_hat>=0.10 given g=0.12) = 0.8845 | CONFIRMED | - |
| 7 | SCOREABLE; structural leg PASSES | MDE80 0.064 < bar 0.10; SUPPORTED reachable at infinite n iff g >= 0.10 (leaves cross subjects within a subcategory); the "engineering" subcategory (1 subject, 145 items < 160) cannot split, share printed | CONFIRMED | - |
| 8 | fetchers refuse without a READY file | `_registration_ok` = file exists AND the substring "READY" occurs. Executed: None -> False; a file reading `Verdict: NOT READY` -> **True**; BZ-AXIS-CONFIRM-MMLU_DRAFT.md -> **True**; BZ-MMLUPRO-MOREMODELS_DRAFT.md -> **True**. The test fixture for "not ready" lacks the word entirely (test_fetch_more.py L513), so the mutant table's "READY-word gate" kill is a presence check | REFUTED (vacuous gate) | BLOCKER for any fetch (F1) |
| 9 | no MMLU result opened so far | E: search (`find E:/benchzoom_cache E:/benchzoom_demo -maxdepth 4` for helm/tiny/lb.pickle, 6 hits): no helm_parts, no tinybench file, no lb.pickle. The 2026-10-09 probe `probe/helm/{inst,pis}.json` is 1,000 test instances with 10/9 references in 897 of them: MMLU-Pro (HELM capabilities), not original MMLU | CONFIRMED (absence by count) | LOW (disclose the probe) |
| 10 | seeds | split `default_rng([20261021, k])`, k = 0..56, and the Z bootstrap `[20261021, 9]` are the SAME stream for k = 9 | defect | LOW (E7) |

## Edits required in the registration (insertion brackets)

- **E1** Replace Q1/Q2 with the author's D-2026-10-21-3 answers verbatim (17 subcategories = L1, 57 subjects = L2, entry
  at L1; MATH BZ-AXIS-CONFIRM-FRESH stays drafted and separate).
- **E2** Q3 settled: C-M1 plain `G(L3a|L2)` deciding; C-M3 secondary, as drafted.
- **E3** Claim wording: a C-M1 SUPPORTED licenses "the axis leaves add a gain of interest over the 57 subjects under
  the meter's backbone (item difficulty and per-model difficulty slope)"; "beyond difficulty AND length" may be written
  only if C-M3 also prints SUPPORTED (secondary), and C-M3 is printed beside C-M1 in every quotation.
- **E4** Roster: "80 models" (not 81) expected after the rules; the census still freezes the list.
- **E5** HELM run rule, in order: (i) scenario mmlu, method multiple_choice_joint, eval_split test; (ii) **the run name
  carries no field beyond subject, method, model, eval_split, groups** (drops the 15 `additional_instructions=yifan`
  runs; the unmodified prompt only); (iii) newest release per model (a guard; vacuous on today's listing, say so);
  (iv) `num_train_trials` == 1 in run_spec.json, else REFUSE (exact_match must be binary for the meter; the mean over
  trials in `helm_run_frame` would yield fractions); (v) coverage >= 13,902 items and <= 1% unmatched; (vi) join by
  (subject, normalised question + choices) with the count of DUPLICATE keys within a subject printed; a duplicated key
  is joined by within-subject order and its text equality checked, else both items leave the scored set (count
  pinned before READY-1).
- **E6** Support (a)-(b): DEFF 1.1257 source = `E:/benchzoom_demo/meter_axis_v1/outcome.json`
  `datasets/mmlu_pro/stats/all_models/L3a-L2/deff`; it is the cross-model within-item correlation, expected to GROW
  with the roster (about 1.45 at 80 models under constant ICC), the SE transport stays conservative (row 5). [A1]
  re-measures it on WORK; the post-run prints DEFF, n_eff and MDE80 beside C-M1.
- **E7** Seeds: Z bootstrap `[20261021, 109]` (or split seeds `[20261021, 0, k]`), so no stream is shared.
- **E8** Hygiene: disclose the 2026-10-09 HELM capabilities probe (MMLU-Pro instances and per-instance stats on E:,
  not original MMLU); name the READY-1 file path the fetcher gate must require (F1).

## Code conditions (before READY-1; benchzoom, not edits to the registration)

- **F1 (BLOCKER for any fetch)** `_registration_ok`: require the exact path `docs/reviews/READY1_BZ-AXIS-CONFIRM-MMLU.md`
  (or whatever READY-1 is named in E8), tracked in TaxoArena git (`git ls-files --error-unmatch`), whose verdict line
  matches `^VERDICT: READY-1$` exactly; "NOT READY", "READY WITH EDITS" and the drafts must be refused; add a test with
  a "NOT READY" fixture. Until then no agent runs `fetch_zoom_data.py helm|tinylb`.
- **F2 (HIGH)** `helm_mmlu_runs`/`helm_latest_by_model` implement E5 (ii) and (iv); a census mode (`--list-only`
  plus instances.json and run_spec.json, no predictions) that runs WITHOUT the gate, since the draft's census must be
  committed before READY-1 and the current `--list-only` sits behind the gate (circular).

## Commands (all read-only)

```
git -C benchzoom rev-parse 450b86e:<f>; git hash-object <f>   # LF blobs, wt = HEAD (autocrlf true)
python -I scratchpad/gate.py notready.md   # None False | NOT READY True | both drafts True
python -I scratchpad/helmls.py             # helm_mmlu_runs(_GcsFiles()) listing only -> 4,575 runs, 81 names; latest_by_model raises
python -I scratchpad/helm2.py              # yifan dups 20 rows / 2 models; 80 complete models; 0 in >1 release (sha256 7c120b96 listing csv)
python -I scratchpad/rs.py                 # v1.13 runspecs: 4,503 runs, 79 models x 57, max_eval 10000, 5-shot, 1 trial
python -I scratchpad/oc.py                 # outcome.json mmlu_pro L3a-L2 deff/n_eff/se/se_cell_iid/mde80
python -I -c "<Support arithmetic>"        # SE 0.016658, n_eff 4970.8, stress 0.037097, MDE 0.06413/0.14246, ICC transport
python -I scratchpad/inst.py               # probe inst.json: 1,000 test items, references 10/9/4 -> MMLU-Pro
```
Own mutants: none (no deciding code exists; registration precedes code). The F1 execution check stands in for one.
