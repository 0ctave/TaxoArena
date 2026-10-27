# READY review: HIER-FAIR-BACKOFF + BACKOFF-ROBUST (hier_fair_backoff.py), TREE-CUT-GRANULARITY + NESTING (tree_cut_granularity.py)

Reviewer: adversarial-reviewer, 2026-10-08. Zero calls. Reviewed against the registrations at prog L24974-L25027
(`_as_of` e83b59d5; headings "## Registered 2026-10-08 (before any code or call) — HIER-FAIR-BACKOFF / BACKOFF-ROBUST /
TREE-CUT-GRANULARITY / NESTING"). Branch `worktree-wf_fa0ebf63-18c-3`, tip db44a46a (parent e83b59d5, an ancestor of main HEAD
d999e689; the delta adds exactly 2 files, 3,573 lines, per `git diff --stat e83b59d5 db44a46a`).

## VERDICT: READY (both tools), with conditions C1-C3

Pinned blobs (LF, `git hash-object` = `git rev-parse db44a46a:<path>`; the working tree carries the same LF blob):
- `tools/analysis/hier_fair_backoff.py` blob:6d3e86b5dc04e5dfcd73e5844218983f898ca653 (sha256-lf16 83e642947d8bd5b4, sha256-crlf16 45aa6e327deb2f1d, the builder's; the blob was recomputed here)
- `tools/analysis/tree_cut_granularity.py` blob:c80c3c1023ab62193483c1a4387000b532620640 (the TCG dry-run printed lf16 b1c3d18d2f489423 / crlf16 58527d545ea77b5f)
- Imported instruments (tree_backoff, union_route_common, e1_split_draws, flat_mix_mmlu, resp_profile_info, construction_arms,
  stability_vs_kmeans, free_tests_f4_f7, g13_breakdown): the blobs on the branch equal main HEAD's. The comparison loop printed no DIFF line for any of the 9 files.

## Per-claim table (deciding claims only)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | HFB selftest 8/8 | CONFIRMED | 8/8, 19.0 s (sandboxed) | - |
| 2 | HFB mutants 51/51, control survives | CONFIRMED | 51/51, X00 SURVIVED | - |
| 3 | TCG selftest 12/12 | CONFIRMED | 12/12, 13.6 s | - |
| 4 | TCG mutants 61/61, control survives | CONFIRMED | 61/61, X00 SURVIVED | - |
| 5 | HB1/HB2/R1 words, clause order, closed PARITY margin, 95%/90% percentiles, two-stage (components then seeds) bootstrap, DEFF = Var(two-stage)/Var(component-only), n_eff = components/DEFF | CONFIRMED by reading `hb1_word`/`hb2_word`/`r1_word`/`cv_boot`/`interval` against L24980-L24981, L24995 | - | - |
| 6 | Folds = sha256(component + "HIER-FAIR-BACKOFF-FOLDS-1") mod 10; held-out fold out of every fit; tau* = first GATE maximiser over the ascending grid (ties to smaller) | CONFIRMED (`fold_of`, `cv_predict` w = fold != f); own R1 (salt -> FOLDS-2) KILLED | - | - |
| 7 | Shape-matched BC_s reproduces AF-U per-level counts | CONFIRMED ON REAL DATA (my dry-run): AF-U [6,10,21,31,53,63,38,6]; BC0-BC4 equal, 123 centroids each, 0 degenerate, 0 empty | = pilot's counts | - |
| 8 | TRAIN-CV denominator 11,841 / 10,781 (D5 risk of [HFB-CV-DENOM]) | PARTLY: structural proxy, no key read: 11,841 items / 10,781 components, 311 cross-source (= pilot's 311); GATE routing-row items on the TRAIN side 0. Key-completeness is checked only at --run | 11,841/10,781/311 vs 11,841/10,781/311 | LOW |
| 9 | No EVAL before the HB1/HB2/R1 words are fixed | CONFIRMED: `train_cv` runs in `read_views`' `between` hook after the TRAIN key, before `open_tw("eval")`, the marker and the EVAL unseal (union_route_common L196-L227) | - | - |
| 10 | TC1/TC/NV1/NV rules, rule 8, depths d >= 2 with 4 <= L_d < L_max, the bar = max(0.0083 registered, spread_KM) | CONFIRMED by reading `tc1_word`, `tc_word`, `nv1_word`, `nv_word`, `used_depths`, `summarize` against L25008, L25022 | - | - |
| 11 | TCG held-out never enters a centroid; categories in the scorer only | CONFIRMED: KM/BKM fit on Xf only; own T2 (KM fit on Xh) KILLED; real hygiene: fit texts not TRAIN 0, held-out in fit 0, shared stem_key 0 on all 3 trees + af_clean_s42 | - | - |
| 12 | TCG real objects | CONFIRMED (my dry-run): pools p5fb86f1/p6d15d91/p69d2762 + p2dca pass; leaves 80/87/72; fit 8,171/8,247/8,269; held-out 3,598/3,522/3,500; graph16 equal to the pins; [EMB-GUARD] own ADMIT, permuted REFUSE on each tree; TC depths 6/6/5; NESTING cells d2 9/7/9 and d3 18/15/18 against fine counts 80/87/72 | = registered | - |
| 13 | BKM nesting identity holds by construction | CONFIRMED by reading: `fit_bisecting` seeds split j by `seed*1000003 + j`, so the L_d run is a prefix of the L_max run; the labels are the bisection labels, not a nearest-centroid re-filing | - | - |
| 14 | Support arithmetic (HFB, BACKOFF-ROBUST, TCG, NESTING) | CONFIRMED; see the script below. HFB: SE 0.1954 / 0.2199, DEFF 1.610 / 1.561, n_eff 6,696 / 6,911, MDE80 0.546 / 0.616, TOST need 0.485. BR: TAU200 SE 0.1467, MDE80 0.412; NO-XSRC SE 0.198, MDE80 0.554. TCG: SE 0.00296, MDE80 0.0083. NV: SD 0.0447, SE 0.0200, MDE80 0.056. DEFF source: the pilot's component-only SEs, read here from results.json /subsets/ALL: D_acc se 0.154 and D_gain se 0.176 | to the digit | - |
| 15 | Pilot files cited by the registrations | CONFIRMED: the sha256 prefixes of test3 results.json 866284ca1bb5cf98, verify.json 97e9815d9f5677e4, granularity_free 2fc8ba3a99b8dc54 and nesting cb5a74cf0d870081 all match | - | - |
| 16 | Zero calls; dry-runs write nothing | PARTLY: no outcome dir was created, and no file under the main checkout changed during both dry-runs (`find -newer`: 1 file). That 1 file is `mmlu_pro_dataset_cache_v2.db-shm`: a WAL DB was opened `mode=ro` without `immutable=1`. The .db file is unchanged (mtime 2026-10-03) and the -wal file is 0 bytes | - | LOW |
| 17 | The registered constants are pinned by the selftest | PARTLY: HFB yes (own R1 fold salt and R3 parity 0.0065 were KILLED). TCG no: own T1 (mde80 0.0083 -> 0.0090) and T3 (v90_bar 0.10 -> 0.12) SURVIVED. Reading the committed blob, its values are correct: mde80 0.0083, v90_bar 0.10, maj 0.90, l_min 4, B 1000, boot_seed 20261008, seeds 0-4, n_init 10, nest_depths (2, 3) | - | MEDIUM |

Own mutants (6; all on deciding paths):
R1 fold salt FOLDS-1 -> FOLDS-2 | KILLED | decisive.
R2 BC split seed fixed at 0 for every s | KILLED | decisive (the seeds would collapse).
R3 PARITY margin 0.0060 -> 0.0065 | KILLED | decisive.
T1 TC bar MDE80 0.0083 -> 0.0090 | SURVIVED | decisive (can move TC1) -> C1.
T2 KM fitted on the held-out | KILLED | decisive (leakage).
T3 NV1 bar 0.10 -> 0.12 | SURVIVED | decisive (can move NV1) -> C1.

## Defects / conditions

- **C1 (MEDIUM; does not block the pinned blob).** The TCG selftest does not pin the registered constants, so T1 and T3 survive. The pinned blob carries the right values (row 17). Fix (engine-coder, before any later edit of the tool): in the selftest, assert `REG` against the registered literals (mde80 0.0083, v90_bar 0.10, maj 0.90, l_min 4, B 1000, boot_seed 20261008, seeds (0..4), n_init 10, nest_depths (2, 3)). The operator must run blob c80c3c10 exactly: compare the `[SCRIPT]` line of the dry-run and of the run with the pin.
- **C2 (LOW).** The deciding TRAIN-CV denominator is confirmed only structurally (row 8). If `--run` refuses with [HFB-CV-DENOM], that is a failed precondition reached before the eval view opens and before any statistic. Do not re-pin; return the refusal to the registrar.
- **C3 (LOW; registrar).** Three descriptive deviations must be recorded with the outcome: D1 (the AF-U per-benchmark re-print is NOT DONE; the tool prints "DESCRIPTIVE NOT DONE"); D2 (R2_int reads the MMLU-Pro key of record: keyed_questions, 46 models, 10,925 key-complete questions); D4 (KWF = the per-source K_s cells of record, [SC], tau 0). No criterion reads any of them.
- **D-shm (LOW).** Row 16. The touch comes from the imported, pinned readers (`pool_guard.open_ro` / `free_tests_f4_f7`, `mode=ro`), not from the new code. It is not a write to the record. Fix later: open with `immutable=1`.
- NOTED, not a defect: AF-U and BC_s both use the held-out fold's TRAIN vectors (geometry only, no correctness) in cell construction, which is symmetric across the arms. HFB's "[HFB-SHAPE]" check is satisfied by construction (BC_s copies AF-U's topology), so it is an identity check, not a finding. The bootstrap holds tau* fixed per fold (printed in WORDS).

## Rule 7 / runtime

Both tools are POOL READERS. Run them one at a time, never inside a construction or site null, with busy.ps1 run first (exit 1 = free; it was free at 15:17). The dry-runs took 14.8 s (HFB) and 20.5 s (TCG). Expected `--run` time on one thread: HFB about 10-30 min, TCG about 15-25 min (135 KM fits x 10 restarts + 135 BKM + 4 3PL). Each `--run` writes its outcome once only, under the main checkout. Never commit the outcome; back it up to E: with SHA256SUMS.

## Commands (compact)

```
cd .claude/worktrees/wf_fa0ebf63-18c-3
python tools/analysis/scratch_dir.py --run -- python tools/analysis/hier_fair_backoff.py --selftest     # 8/8
python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_cut_granularity.py --selftest  # 12/12
python tools/analysis/scratch_dir.py --run -- python tools/analysis/{hier_fair_backoff,tree_cut_granularity}.py --mutants  # 51/51, 61/61
WHICH=hfb|tcg python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/rv_own/own_mut.py   # own R1-R3, T1-T3 (sets MUTANTS, calls run_mutants)
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # exit 1
touch E:/TaxoArena_tmp/rv_own/marker_before
python tools/analysis/hier_fair_backoff.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena            # rc 0
TAXOARENA_DATA_ROOT=Z:/FAC/TUBerlin/THESIS/TaxoArena python tools/analysis/tree_cut_granularity.py --dry-run  # rc 0
python E:/TaxoArena_tmp/rv_own/cv_count.py   # no key: structural 11841, cv-set 11841, components 10781, cross-source 311, GATE on TRAIN 0
find <main> -path ./.git -prune -o -path ./.claude -prune -o -type f -newer marker_before -print | wc -l   # 1 (the -shm)
python - (Support arithmetic: interval widths / 3.92, (SE/SE_c)^2, 10781/DEFF, 2.8 SE, (1.645+0.842) x 0.195, range/2.326/sqrt 5)
git diff --stat e83b59d5 db44a46a; git rev-parse {HEAD,db44a46a}:tools/analysis/<9 imports>   # 2 files; equal
```
Logs: E:/TaxoArena_tmp/rv_{hfb,tcg}_{selftest,mut}.log, E:/TaxoArena_tmp/rv_own/{hfb,tcg,hfb_dry,tcg_dry}.log.
