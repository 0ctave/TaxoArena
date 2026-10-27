# POST-RUN review: CERT-RESOLUTION and RECORD-RECIPE-EDGE-AUDIT (2026-09-26, adversarial reviewer; zero calls, read-only)

## Verdict

**VALID, both outcomes; every printed number reproduces.** The scoring below stands as the scripts wrote it:
- CERT-RESOLUTION: C1 HELD, C2 and C3 as printed, P1-P5 HELD, F1 and F2 not fired.
- RECORD-RECIPE-EDGE-AUDIT: C1 HELD, P1-P4 HELD, F1 not fired.

How I checked:
- I recomputed everything with my own code from the pinned inputs, without importing the builder's scripts. The scripts are `review_certres/postrun.py` and `postrun_audit.py` in the session scratchpad. CP uses scipy `beta.ppf`, not the builder's bisection.
- The comparison against `cert_resolution_sites.csv` is field by field: k, p_site, cp_lo, cp_hi, cert, flat_bh, by, family_key, reached, hier_bh, the words (literal E1-E3 text plus the E4 and MC tags). Result: **0 mismatches on 265 of 265 rows**.
- The comparison against `recipe_edge_audit_sites.csv` covers birth, split_iter (stable-from), split_iter_first_equal, both late_born columns, bar_ratio, p95_ratio, cert and k. Result: **0 mismatches on 70 of 70 rows**.
- Inputs are unchanged. Outputs were written once and equal the run logs.

The READY's test gaps D1-D4 are therefore closed on the data of record:
- MC-MARGINAL against the granting cutoff: matches.
- E1, E2 and E3 membership: matches.
- P1 equality: True.
- bar_ratio and p95_ratio not swapped: matches.

What the talk may say is narrower than "the tree states which of its own splits are real". Section 4 gives the argument, section 3 the words of record.

## 1. Identity and integrity

| check | command / script | result |
|---|---|---|
| merged blobs | `git rev-parse f708c12:tools/analysis/{cert_resolution,recipe_edge_audit}.py` | dbe9425dc406edcd41661a6df4e00d33b44299b6 and 09369edb4db47be2d85924fee35f1055ea31990e (= the READY's pins); `git diff --name-only 7375a97 f708c12` = these 2 paths; `merge-base --is-ancestor 7375a97 HEAD` succeeds |
| the script that ran = the pinned one | the outcome header lines | cert_resolution.py blob:dbe9425d / sha256-lf16:3e3fb1b91aa3d361; recipe_edge_audit.py blob:09369edb / sha256-lf16:2a73dedca0eb9749 |
| inputs unchanged | postrun.py asserts the LF sha256-16 of all 8 CERT-RESOLUTION inputs; postrun_audit.py of all 5 audit inputs | all equal the registered pins (L20768-L20776, L20827-L20829) |
| write-once | `grep -c 'else "x"'` = 1 in each script (open mode "x"); output mtimes 03:43:06.68 and 03:43:07.84; no earlier file exists | one write each. The files are UNTRACKED and not gitignored (`git check-ignore` rc 1), so the registrar must commit them with the outcome |
| outputs = run logs | outcome bytes are contained in `cert_resolution_run.log` / `recipe_edge_audit_run.log`; each log has exactly 26 extra bytes (the leading "pool: none (no DB opened)" line printed by main) | equal |
| output pins (sha256 of the LF files as written; 0 CR bytes) | `sha256sum` | cert_resolution_outcome.txt b5867a34ca96cfe9 (95 lines); cert_resolution_sites.csv a151392aa1785b9e (266 lines = header + 265); recipe_edge_audit_outcome.txt c574f5923ee0f23a (56); recipe_edge_audit_sites.csv 662dcc5e1e121c2d (71 = header + 70) |

## 2. Per-claim table (claimed = printed by the run; got = my recompute)

| claim | got | claimed | status |
|---|---|---|---|
| bareq512_s42 (R512) hierarchical BH | 2: n00000006 Chemistry, n00000015 Engineering; both k = 0; top family 14; r* = 2; cutoff 0.007143; margin 0.00382 > 1/301, so NOT MC-MARGINAL; 3 families run (sizes 14, 2, 1) | 2; same ids; no MC | CONFIRMED |
| bareq512_s42 flat BH / BY | 0 / 0 (only 3 sites at k = 0; 5 needed) | 0/70, 0 | CONFIRMED |
| af_clean_s42 (R256) flat / BY / hierarchical | 12 (cutoff 12 x 0.05 / 69 = 0.008696) / 0 / 8; top family = root; 9 families run | 12 / 0 / 8 | CONFIRMED |
| o0_clean_s42 (R256) flat / BY / hierarchical | 4 (cutoff 0.003333, all 4 at k = 0) / 0 / 4 (Chemistry, Math k = 2, Engineering, Biology) | 4 / 0 / 4 | CONFIRMED |
| frozen (R256) flat / BY / hierarchical | 0 / 0 / 2 (Chemistry, Biology; k = 0; margin 0.00382, not MC) | 0 / 0 / 2 | CONFIRMED |
| MC-MARGINAL (A4) | 2 sites: af_clean n00000124 (E2, flat cutoff) and o0 n00000143 (E2, flat cutoff 0.003333 vs p 0.003322). No E1 site is MC-MARGINAL on any tree | same 2 | CONFIRMED |
| E-lists | bareq512 E1 2 / E2 0 / E3 8; af_clean 8 / 4 / 2; o0 4 / 1 / 6; frozen 2 / 0 / 4 | same | CONFIRMED |
| D1 (CP contains 0.05, among cert_site_p95 sites) | bareq512 4 of 10; af_clean 1 of 14; o0 4 of 11; frozen 2 of 6 | same | CONFIRMED |
| D1 cross-tab | o0 has 1 site that is cert_site_p95 true with k > 14: n00000026 (q_site 0.0500, k 15, CP [0.028, 0.081]). The quantile certificate and the exceedance count disagree at the boundary. It carries E3 + E4 words, as it should | printed | CONFIRMED (note) |
| P1 (reproduction) | 0/70, 12/69, 0/66, equality True. F2 does not fire | HELD | CONFIRMED |
| P2 (o0 flat, unseen) | 4, inside [0, 5]; the point 0 missed | HELD | CONFIRMED |
| P3 hierarchical sizes | 2 / 8 / 4 / 2 against [1,6] / [6,14] / [1,6] / [1,4] | all HELD | CONFIRMED |
| P4, C1, F1 | C1 HELD (2 > 0); F1 does not fire | same | CONFIRMED |
| P5 | 4 of 10 resolution-limited, inside [3, 7] | HELD | CONFIRMED |
| Audit births at iteration >= 9 | n00000523 and n00000524 at 9 (parent n00000191); n00000693 and n00000694 at 13 (parent n00000154) | same | CONFIRMED |
| Audit late-born (stable-from) | 2 of 70: n00000191 "Macroeconomic Policy and Aggregate Dynamics" (split 9, q_site 0.62, not certified) and n00000154 "Electromagnetic Field and Charge Interaction Analysis" (split 13, q_site 0.54, not certified). First-equal gives the same 2; the readings disagree on 0 of 70 | same | CONFIRMED |
| Audit C1 / P1 | 0 of 10 certified sites late-born | HELD | CONFIRMED |
| Audit D1 bar ratio (descriptive) | certified: min 2.3726 (n00000054); < 1.05: 0; < 1.10: 0. All 70: min 1.2256 | same | CONFIRMED |
| Audit P2 / P3 / P4 | 2 in [2, 4]; 0 bar-edge; 2.3726 in [2.0, 3.2] | HELD | CONFIRMED |

## 3. The words of record the talk may use (E1-E4, verbatim; per tree; never across recipes)

**R512, bareq512_s42 (the tree of record).**
- E1, the talk's certified R512 exhibits: **Chemistry (n00000006)** and **Engineering (n00000015)**, each "certified at per-family FDR q = 0.05 (hierarchical BH over nested sites, 300 reps, bareq512_s42, R512)". Neither carries MC-MARGINAL or "resolution-limited".
  - What is certified is the SPLIT AT the site: Chemistry into its 3 children, Engineering into its 2. It is not the anchor category, which is given, not discovered.
- E3, the other 8 per-site certified sites: "passes its own site-null p95 (per-site, uncorrected, 300 reps)". Four of them (Law, History, n00000127, n00000078) add "; resolution-limited at 300 reps".
  - They may NEVER be called "certified" alone or with an error rate.
- The count of record 10/70 stays the per-site, uncorrected count.

**R256 (read side by side, descriptively; frozen is on another pool, p8a29d8f3ff75aa55).**
- af_clean_s42:
  - E1 (8): the root split and n00000005, n00000017, n00000018, n00000042, n00000043, n00000045, n00000074.
  - E2 (4): n00000086, n00000111, n00000113, n00000124 (the last MC-MARGINAL), with the literal E2 words.
  - **D5, disclosure:** these 4 E2 sites belong to the 12-site flat set whose count was SEEN POST HOC (the brief's 12/69; C2-af_clean_s42 is POST-HOC-SEEN). Wherever they are named, the POST-HOC-SEEN status of the flat count must be stated beside the E2 words.
- o0_clean_s42 (unseen):
  - E1 (4): Chemistry, Math, Engineering, Biology.
  - E2 (1): n00000143, MC-MARGINAL.
  - E3 (6).
- frozen:
  - E1 (2): Chemistry, Biology.
  - E3 (4): Math, Business, Engineering, n00000160.

**Prohibition.** No sentence may set bareq512_s42's 2 against the R256 trees' 8 / 4 / 2, nor its 0 flat against their 12 / 4 / 0. The recipes differ in dimension (512 vs 256) and bar (0.0145 vs 0.025), and the outcome prints the prohibition. Forbidden examples:
- "Engineering is certified on R512 but not on frozen";
- "R256 certifies more".

## 4. What this shows, and does not show, for "the tree states which of its own splits are real"

**Shows:**
1. The tree of record can attach a STATED ERROR RATE to a nonempty set of its splits. The registered falsifier F1 did not fire. The set is 2 of 70 (Chemistry, Engineering), at per-family FDR 0.05, prefix-closed, 300 reps.
   - Both rest on k = 0 (no null replicate reached the observed separation).
   - The set is not one exceedance from collapse. If both had k = 1, both would still be rejected (2/301 = 0.00664 <= 2 x 0.05 / 14 = 0.00714). One site at k = 2 would reduce it to 1.
2. The splits below them were TESTED and are not certified. Chemistry's and Engineering's child sites entered their families (m_f 2 and 1) with k = 186, 299 and 300. So the certified structure stops at the first emergent level under those two anchors: it is not deep.
3. The certified-per-site set does not come from the unsettled part of the loop. Both post-quiescence splits (iterations 9 and 13) are uncertified (q_site 0.62 and 0.54). The certified sites sit 2.37x to 6.19x above the construction bar. That readout is descriptive, and near-vacuous by construction (registered structural note).

**Does not show:**
1. That the tree states which of its splits are real IN GENERAL. 53 of 70 bareq512 sites were never tested, because the 12 anchor splits above them were not rejected. Five of the 8 E3 sites are in that group, including n00000020 at k = 0 (under Physics, k = 68).
   - Under this prefix-closed procedure, strong per-site evidence below an unrejected anchor cannot be certified.
   - That is the registered design, not evidence that those splits are unreal. They are UNTESTED at a stated error rate, not "not real".
2. A tree-wide FDR of 0.05. Only the per-family level is controlled, and BH's positive-dependence assumption over nested sites is not shown.
   - Under arbitrary dependence (BY, flat) NOTHING survives on any of the four trees (0 / 0 / 0 / 0). This sensitivity belongs beside the E1 words whenever an error rate is quoted.
3. Anything at more than 300 reps. Holm is unreachable at this resolution, and flat BH needs 5 of 70 sites at k = 0 while bareq512 has 3. More reps (CERT-FAMILYWISE-REPS) is the author's window.
4. That the tree of record is a fixed point. Part 1 stands: CERTIFIED false, a GED-quiescence stop. C1 HELD on the audit does not change that. The k-edge half remains UNDETERMINED BY INSTRUMENT.
5. That a certified split is modal (MIX-LRT-SITE), capability-relevant (CAP-GATE-POSTHOC), or matters for routing, boards or profiles.
6. Any R256-vs-R512 statement (section 3).

## 5. Defects and notes

- **N1 (LOW, records).** The four output files are untracked and not ignored; the registrar commits them with the outcome, pinned as in section 1. `git status --short experiment_results/cert_resolution experiment_results/recipe_edge_audit` shows `??` for both dirs.
- **N2 (note, not a defect).** o0_clean_s42 n00000026 is cert_site_p95 true with q_site 0.0500 (k = 15): the quantile certificate and the exceedance count split at the boundary. Its words (E3 + E4) are correct.
- **N3 (carried).** The READY's D1-D4 remain selftest follow-ups for any future edit of these scripts. On this run they are closed by recomputation. D7 (the R256 redraw jsonl files untracked and not archived) is still open for the data-steward.
- **N4 (reviewer process, carried from the READY).** My one `taskkill //IM python.exe` during the READY session may have killed a foreign python process. This review used PID-scoped handling only; a foreign python.exe (PID 48568) was running throughout and was not touched.

Scratch (session scratchpad `review_certres/`): `postrun.py`, `postrun_audit.py`, plus the READY-stage `indep.py` and `tree_struct.py`.
