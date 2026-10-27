# Delta review: k46-repost2 @ 30f86150 (C-K7 of READY_paid_prereqs 89b50493) and e1-configs @ 3724f221

Reviewer: adversarial-reviewer, 2026-10-01. Base: main b3dd18ab (registrar brackets of record; C-K5 met there). Delta review of
`git diff 3679bae4 30f86150` (3 files, counted: `git diff --name-only 3679bae4 30f86150 | wc -l` = 3) and of
`git diff 96d6ca1e 3724f221` (3 added files). Code untouched by the delta is CONFIRMED in 89b50493 and not re-derived.
Zero calls, nothing posted; dry-runs only (fake .env, host *.invalid).

## Verdict

| branch @ tip | MERGE | dry-run | --go |
|---|---|---|---|
| k46-repost2 30f86150 | **MERGEABLE** by path (3 files; main moved 3679bae4..b3dd18ab in 0 of them) | **READY** (all three legs; freeze-canary) | RP21 v2 leg (`--leg canary`): **READY** (gate file `READY_k46_repost.md`, this commit). RP20 + ONE: **READY after RP21's C1-v2 is read**, under C-K8 |
| e1-configs 3724f221 | **MERGEABLE** by path (3 added files) | n/a (configs + check tool; zero JVM) | E1 itself stays gated by E1-ROUTE C1-C5 HELD (unchanged) |

C-K1..C-K4 and C-K6 of 89b50493 are discharged in code and killed by the selftest; C-K5 at b3dd18ab; C-K7 by this file and the
gate file. One new condition C-K8 (MEDIUM): the C-K6 order gate admits a VOID canary read.

## Pins (LF of record = `git rev-parse <tip>:<path>`, `git cat-file blob | sha256sum`; worktree renderings beside)

| file | blob (LF) | sha256-lf16 | worktree |
|---|---|---|---|
| tools/analysis/k46_repost.py | 8c5ce9db5f7cf39577264e222450a3e1f599eae6 | **dd8152585fd7f0d7** | sha256-crlf16 06eccdf43ed00ddb |
| tools/analysis/k46_repost_selftest.py | 67b71629473a29c05266cc19d8fc8380048bee2e | eb67285c68bd8869 | sha256-crlf16 b435ccf1412ab1b8 |
| experiment_results/archv2/g17_canary/g17_v2_canary_set.json | baf35d6ea8f8b2c0916fc21581a37c3370e7d970 | dc7a5f7ca6d33380 | LF (same) |
| experiment_configs/e1_route/E1_nomic_raw_af_clean_s42.toml | edace9f9534d0ca4272852baf9c55c91304d63aa | 3e1373b366977f71 | sha256-crlf16 83a1e2afba50bbd7 |
| experiment_configs/e1_route/E1_nomic_card_af_clean_s42.toml | 67bcdc2b1ad134c9b029eb1f9fb618764a836937 | bd5200efd17d821c | sha256-crlf16 42d4b2519e1bb622 |
| tools/analysis/e1_configs_check.py | 92d22a4376f5f60891d94464a81095c1ee5e04f2 | a3b9c6b9b37b4df8 | LF (same) |

The set file's own `script_sha16_lf` = dd8152585fd7f0d7 = the tip blob (drawn by the final script). E1 blobs = the registrar's
4cb99c65 (blob:edace9f9 / blob:67bcdc2b).

## Per-claim table (deciding claims only)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | C-K1 interval form NORMAL | CONFIRMED | PRECONDITIONS interval_form = "normal"; K13 asserts it on real_cfg(); headers cite L22762-L22784 / L22786-L22810 (D9 closed) | - |
| 2 | C-K2 ONE go = count of the verbatim quotation in the Amendment 34 BODY, heading excluded | CONFIRMED | go_one_check on the worktree plan AND on b3dd18ab's plan: body 1, heading 1 (not counted) -> VERIFIED; my OK2 (gate removed), OK11 (heading counted), OK12 (n >= 1) KILLED; builder go_presence_only KILLED (K2 two in body, K3 heading only, K4 other string) | - |
| 3 | 4K-RULE line printed by every rp20 / one launch and dry-run | CONFIRMED by execution | dry-runs print `RP20 3692 + ONE 1636 = 5328 matches > 4000 ... Amendment 34 -> VERIFIED`; 2 x 1,846 + 2 x 818 = 5,328 | - |
| 4 | C-K3 OK4 / OK5 / OK8 killed | CONFIRMED | my OK4, OK5, OK8 re-applied to the tip: KILLED (were SURVIVED decisive at fb1430d8); builder both_unusable_same / census_off / c1v2_conv_b KILLED | - |
| 5 | C-K6 refusal (no canary outcome; FAILED) on rp20 AND one | CONFIRMED | K6/K7; my OK9 (FAILED admitted) and OK10 (gate on rp20 only) KILLED; the gate sits before the READY gate, posting launches only | - |
| 6 | C-K6 admits only a READ C1-v2 | **PARTLY** | an outcome of record whose line is `C1-v2: UNDETERMINED BY VALIDITY` (caches complete, C0 failed) is ADMITTED: my probe on order_gate -> ADMITTED. A void canary is not "read" (89b50493 C-K6) | MEDIUM (C-K8) |
| 7 | C-K4 canary set: 300 matches, set hash 10e027fe, order sha 4fa3bc0e, reproducible from the store | CONFIRMED independently | own sqlite (immutable) re-draw: frame 2,661; alloc NONE/health 940->106, NONE/math 903->102, ONE/health 392->44, ONE/math 426->48; set hash 10e027fe046e2a07, order 4fa3bc0e23ce2025, ids equal in order, 300 components, klass/anchor/component equal row by row, TIE 58 = 58; `--freeze-canary --dry-run` and `--leg canary --pass v2-1 --dry-run` print REPRODUCED by the draw | - |
| 8 | NOT BUILT line (per-contestant agreement with the reference side) | CONFIRMED | printed in the ONE readout (I1b); R5 bracket b3dd18ab | - |
| 9 | transport preflight binding on all three legs (C-K7) | CONFIRMED | transport_check (b) on `--leg canary --pass v2-1`, `--leg rp20`, `--leg one` dry-runs @30f86150: PASS x3 ((a) PASS, 8 posting refs, 1 load_env) | - |
| 10 | identity gate / store untouched | CONFIRMED | IDENTITY GATE PASS on every dry-run; store sha256 44724d25aa8653b4... before = after (dry-runs and my re-draw) | - |
| 11 | dry-run counts / ceilings / schedule shas | CONFIRMED | canary 300 m / 600 calls per pass (1,200 registered, ceiling 1,260); rp20 3,692 / 7,384 / 7,750, schedule sha 5b9df7eeed023160 (= R4); one 1,636 / 3,272 / 3,440, 1577f3a11b6e84dc (= R4) | - |
| 12 | selftest / mutants | CONFIRMED | selftest 84 OK python and -O (70 before); `--mutants` KILLED 21 of 21 | - |
| 13 | Support (delta does not touch it) | CONFIRMED (cited 89b50493 #15) | C1-v2 re-derived: sqrt(0.1 x 0.9 / 300) x sqrt(1.169) = 0.01732 x 1.0812 = 0.01873; MDE80 0.0524 vs bar 0.15 (SCOREABLE) [CORRECTED 2026-10-01 by G17-CANARY (registrar; D4 of docs/reviews/POSTRUN_rp21_v2.md, cb40d39e): wrong word for a HELD: HELD is DESCRIPTIVE-ONLY at the prediction (distance 0.05 < MDE80 0.0524); FAILED is SCOREABLE (registration Support (f))] | - |
| 14 | E1 configs = af_clean_s42.toml + outputDir only | CONFIRMED | `diff` of each blob against main's experiment_configs/anchorfree/redraw/af_clean_s42.toml: 15 comment lines + ONE changed line (L44 outputDir); e1_configs_check.py: OK x2, launcher admits both; base / launcher / embedder_arms unchanged 96d6ca1e..main (count 0); experiment_results/e1_route/E1_nomic_* absent (count 0) | - |
| 15 | e1_configs_check selftest 11/11, mutants 7/7 | CONFIRMED / PARTLY | selftest 11/11 python and -O; own mutants: E3 (expected value not compared) KILLED; E1 (launcher's outputDir not compared) SURVIVED, E2 (OUT_PREFIX not required) SURVIVED, both not decisive ((b) pins the value of each committed config; the launcher refuses protected dirs itself) | LOW (D-E1) |

## Own mutants (scratch copy `git archive 30f86150`; one at a time; selftest rc)

OK1 errored pilot jobs dropped from the guard: SURVIVED, not decisive (D4 of 89b50493 stands) | OK2 ONE go gate removed: KILLED, decisive |
OK3 hard cap `>`: KILLED | OK4 both-unusable not a difference: KILLED, decisive | OK5 kd census unchecked: KILLED, decisive |
OK6 transport refusal swallowed: KILLED | OK7 window from now: SURVIVED, not decisive | OK8 canary C1-v2 on `!=`: KILLED, decisive |
OK9 order gate admits FAILED: KILLED, decisive | OK10 order gate on rp20 only: KILLED, decisive | OK11 go counted with the heading: KILLED |
OK12 go presence (n >= 1): KILLED, decisive.
E1 / E2 / E3 (e1_configs_check): SURVIVED / SURVIVED / KILLED (above).

## Conditions

- **C-K8 (MEDIUM; RP20 and ONE --go).** Before any rp20 / one posting launch the run-operator reads the `C1-v2:` line of
  `experiment_results/archv2/k46_repost/g17_v2_canary_outcome.txt` in the checkout that posts: it must be `HELD` or `UNDETERMINED`.
  `UNDETERMINED BY VALIDITY` (a void canary) means C1-v2 is NOT read: RP20 does not post until the research-lead rules in the
  record (re-run the canary, or relax C-K6). The code admits it today (claim 6); a code fix belongs to any later delta.
- **C-K9.** RP21 posts from the same checkout RP20 later posts from (the order gate reads `cfg.out_dir` of the running checkout;
  a canary outcome written in a worktree is invisible to a main launch and refuses, the safe side).
- C-E3-3 / C-K6 stand: RP20 not on pass 5's day; RP20 after RP21's C1-v2. The 89b50493 conditions not named here are discharged.

## Defects

- **D-K1 MEDIUM** (k46) order_gate admits `UNDETERMINED BY VALIDITY`. Fix: `if w not in ("HELD", "UNDETERMINED"): refuse`, plus a
  selftest case with a VALIDITY stub. Carried by C-K8 until then.
- **D-K2 LOW** (k46) OK1 / OK7 survive (as at fb1430d8; D4 of 89b50493): errored pilot jobs and the v2-2 window are not
  discriminated by the selftest. Not decisive (--run refuses an uncached pilot job; the window check reads the persisted start).
- **D-E1 LOW** (e1) e1_configs_check survives E1 / E2: a selftest case where the launcher reads a different outputDir and one
  where the outputDir lies outside experiment_results/e1_route/ (with a matching `want`). Not decisive for the two committed files.

## Commands (zero-call; S = session scratchpad/rp2; TAXOARENA_DATA_ROOT = main; K46_REPOST_ENV_ROOT = fake .env)

```
git diff --name-only 3679bae4 30f86150 | wc -l ; git diff --name-only 3679bae4 b3dd18ab | grep -c -E "k46_repost|g17_canary"   (3 ; 0)
git rev-parse 30f86150:<path> ; git cat-file blob <blob> | sha256sum ; sha256sum <worktree path>
python tools/analysis/k46_repost.py --selftest ; python -O ... --selftest ; --mutants                      (k46-repost2 worktree)
python S/om2.py S/k          (OK1-OK12 on git archive 30f86150)
python S/repro.py            (own immutable read of pilot_k46_verdicts_run2.db; independent re-draw vs the committed set file)
python tools/analysis/k46_repost.py --freeze-canary --dry-run | --leg canary --pass v2-1 --dry-run | --leg rp20 --dry-run | --leg one --dry-run
python tools/analysis/transport_check.py --script tools/analysis/k46_repost.py --rev 30f86150 --env-var K46_REPOST_ENV_ROOT \
   --dry-run-cmd "python Z:/.../k46-repost2/tools/analysis/k46_repost.py --leg <canary --pass v2-1|rp20|one> --dry-run"   -> PASS x3
python -c "... K.go_one_check(cfg) on the worktree plan and on git show b3dd18ab:docs/plan_2026-09-15.md ..."
python -c "... K.order_gate on a temp out_dir with C1-v2: UNDETERMINED BY VALIDITY -> ADMITTED; FAILED (...) -> REFUSED"
sha256sum pilot_k46_verdicts_run2.db before/after (44724d25... equal) ; git status --short | wc -l (0, both worktrees)
diff <(git show main:experiment_configs/anchorfree/redraw/af_clean_s42.toml) <(git show 3724f221:<E1 config>)   (1 line + header)
python tools/analysis/e1_configs_check.py ; --selftest ; python -O ... --selftest ; own E1-E3 on git archive 3724f221
```
