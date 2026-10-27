# DRAFTCHECK: BZ-AXIS-CONFIRM-FRESH draft amendment of 2026-10-26 (TaxoArena 65238f64)

Authority: D-2026-10-26-1 (a8990e4b; "yes to 1 and 3, build the variant both ways"). Reviewer: adversarial reviewer,
2026-10-26. Zero LLM calls. Nothing was run except read-only greps, arithmetic and one read-only load of the pinned V0
pickle (sha256 c2003c59...6660 = `meter_axis.AXIS_PINS["math"]`). Reviewed: `docs/judge_v2_program.md` section
"## Registrar's record 2026-10-26 (insertion only; zero calls; nothing run) — BZ-AXIS-CONFIRM-FRESH draft amended per
D-2026-10-26-1: ..." L25708-L25724 (_as_of 65238f64); `docs/agents/queue.json` and the five new results records at
65238f64; checked against DRAFTCHECK 95e69c9c, benchzoom master 8d8d824 (pinned files unchanged since 516c6ba) and
`E:/TaxoArena_tmp/review_flat-compare/phaseC_math.log` L20, L28-L31. No code under review, so no mutants.

## Verdict

**SOUND WITH EDITS.** The amendment only inserts lines, claims no registration, and transcribes D-2026-10-26-1
correctly: B decides, A is a secondary that moves no word. Every planning number reproduces to the digit from the
stated inputs. The new transport no longer assumes a constant DEFF. E2-E8 are disposed of. No BLOCKER and no HIGH.
Two MEDIUM edits are owed before the full registration:
- **D1.** The power plan and the floors are computed for a different SE from the one declared, and the floor argument
  reaches the author through Q2.
- **D2.** Rule A's N arm is not symmetric with V0_A and K_A. Author question 3 offers too few options, and the code
  owed for N_A is not listed.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; earlier sections and queue text kept | prog `--numstat` 18 / 0; `git diff a8990e4b 65238f64 -- prog \| grep -c '^-[^-]'` = 0. Queue: 256 -> 263 items, 0 removed, old order kept, 1 item changed (BZ-AXIS-CONFIRM-FRESH). Its `registration`, `notes`, `author_decision` and `blocker` all keep the old value as prefix; `depends_on` appended (+FRESH-RULES-SIM); `last_update` replaced. INDEX: only the count line changed (272 -> 277). Commit = 8 files (`--name-only \| wc -l`) | CONFIRMED | - |
| 2 | Span L25708-L25724, parent a8990e4b; amended section L25692-L25706 | Heading at L25708; file has 25,724 lines at 65238f64; `rev-parse 65238f64^` = a8990e4b (ancestor). The quote of the main session's reading is a verbatim substring of `author_decisions/2026-10-26.md` (745 chars, `in` True) | CONFIRMED | - |
| 3 | B deciding, A secondary, as D-2026-10-26-1 | Matches the main session's reading word for word. A "moves neither P's nor any F word". The reading still awaits the author's confirmation (Q1, relayed) | CONFIRMED | - |
| 4 | The rule is the same for every arm | B: V0' and K' partition old + fresh text; N' and N512' have neighbours in fresh training rows. Every arm reads responses only from fresh training rows. A: V0_A and K_A are partitions of the 4,914 old items' text, with offsets fitted on FRESH rows. N_A instead sums OLD WORK residuals (2,949 items, WORK parent, WORK-roster models only). So N_A is a transfer reader, not an old object read like the others (D2). The [E9] sentence "every arm, N included, is built on the old items (object vs object)" overstates this | B CONFIRMED; A PARTLY | MED |
| 5 | DRAFTCHECK E1-E9 fixed or deferred | E1 PARTLY (D1). E2: gloss withdrawn, Q2 reframed (fix applied) and relayed: CONFIRMED. E3: m = 4, F-RESID in the count, one-direction deciding, residual of interest 0.062 = half of 0.12405 (POSTRUN_FLAT-COMPARE row 3): CONFIRMED (+D6). E4: PF5-PF6 = -0.17, PF5-PF7 = -0.25, PF7+PF8-PF6 = +0.06; points at or beyond WORK: CONFIRMED. E5: rank of the depth-1 id = `enumerate(sorted(anchor))` in `kmeans_partition`: CONFIRMED. E6: re-measured LF 9bc8b35a76f508f9 / CRLF d7ae06f6a550aa21 (1,478 CR) and ed6359a6f3591152 / 6337577e7e3968bb (261 CR); `hash-object` da00fcda / 7067fe89: CONFIRMED. E7: all 7 queue items exist; meta v429 = ledger v429: CONFIRMED. E8: 1.82 labelled a stand-in; 6,609 reproduces (6,608.9): CONFIRMED. E9: PARTLY (row 4) | PARTLY | MED |
| 6 | n* under B: D_K 2,444, D_N 4,321, G(N\|L2+V0) 1,422, G(V0\|L2+N) 1,248, P 4,346 / 17,051; constant-DEFF D_K 3,257, D_N 5,118 | Own script from the stated inputs (SE_W, f from phaseC L28-L31 and L20, m_W 81.92, C(n) = 36(4,914+n)/4,914): 2,444 / 4,321 / 1,422 / 1,248 / 4,346 / 17,051; constant 3,257 / 5,118. All MDE80 rows and limiting D (3.07 / 4.87 / 2.29 / 3.04 / 4.77) agree. So do the floors (0.277 / 0.183 / 0.134 / 0.136 / 0.038) and the worked example (rho 0.01524, D 1.765, SE 0.0476, MDE 0.159). Every gap is 0, but only with the unrounded multipliers 3.3393 / 3.8416. At the printed 3.339 / 3.842 the D_N n* is 4,320 and P(SE_cell) is 17,055 (D8) | CONFIRMED (arithmetic) | LOW |
| 7 | The transport no longer assumes a constant DEFF; (g) floors | D(n) = 1 + (m(n)-1) rho with constant rho is a random-cells (cluster-sampling) model. Its floor sqrt(between-cell var / C) exists only for a cell-clustered SE. Neither declared SE has it: B's partition-level item resampling with rebuild, and A's cell-fixed item bootstrap with refit (row "A-vs-B"). Under those, heterogeneity across cells is fixed effect, not noise. The offset-noise part of the D2 mechanism gives a DEFF roughly constant in m. So "D_N / P(SE_cell) unreachable at ANY n" and "Rule A carries those floors" are UNDETERMINED for the declared SEs. The ICC n* is below the constant-DEFF n* for n < 7,375 | PARTLY | MED |
| 8 | Holm family and F-RESID coherent | Critical \|z\| 2.498 / 2.394 / 2.241 / 1.960 unchanged. A one-direction word on a two-sided p inside Holm keeps FWER. A DESCRIPTIVE-ONLY member that advances the step-down is valid. F-RESID is no longer vacuous (n* 1,248 against 0.062). It has no interest bar (D6) | CONFIRMED | LOW |
| 9 | No conflict with D-2026-10-21-1 / D-2026-10-20-4 / D-2026-10-20-5 | V0' is the full axis_v1-recipe tree. B reads no old response; vault TEXT is re-read as V0's construction read it, and the record counts "openings" as meter reads of vault responses (L25479). The ORDER condition meets "freeze before any fresh item is scored". The re-reading of L25499 is flagged. Missing: CONTEXT rule 1 (construction never sees EVAL) is not cited, and the record's WORDING line for transductive trees (L25487 Q2, L25518) is not carried (D5) | CONFIRMED | LOW |
| 10 | New queue items point at the right POSTRUN commits | 6e39fc98 / 81a99d9b / 71df6668 / 533002c3 / f73d7a83 each ADD `docs/reviews/POSTRUN_<id>.md` (`--name-status`, 5/5 'A'); all are ancestors of HEAD. Run blobs: `rev-parse` 8177915 -> 86bddccd, 516c6ba -> da00fcda, 983c34f -> 85fea703, 32d85f7 -> 634158a5, 1c9d097 -> 594683d0, 46b4155 -> 7fc4b73d. Merges 516c6ba / a19c608 / 6d04789 / 8d8d824 are on master. a19c608 also carries 63336fb (the post-review C1 fix), which the script field omits (D9) | CONFIRMED | LOW |
| 11 | Nothing claims a registration; ledger unchanged | The heading, STATE and queue `state` "drafted" all say so. FRESH-RULES-SIM and TAU-GRID are "not registered (exploratory)". The 5 records say "none (exploratory, not registered)" with ledger None. No BZ-AXIS-CONFIRM-FRESH record exists (count 0). The ledger is not in the commit (count 0) and stays at v429 | CONFIRMED | - |

## Defects (each with its fix; D1 and D2 before the full registration, the rest at the registrar's next record)

- **D1 (MEDIUM; Support (b)-(e), (g); author question 2).**
  - What is wrong:
    - (b) plans every contrast with the leaf-clustered factor f (D_K: the two-way form, seed KM0 only, called
      "DECLARED"). Yet the 10-26 section declares SE_cell under B to be the partition-level resampling and prints the
      clustered form "beside it, deciding nothing". The E1(b) mismatch (planning with an SE other than the declared
      one) therefore persists.
    - The floors in (g), and the Q2 line "has no n* at all if V0''s leaf count does not grow", hold only for a
      random-cells clustered SE (row 7).
  - Fix:
    - Label f as a proxy for an SE that has not been measured.
    - Condition every floor and every "unreachable at ANY n" on "a cell-clustered SE". State that neither declared
      resampling SE has a structural floor.
    - Strike "no n* at all" from Q2, or restate it as conditional on that SE.
    - Print the constant-DEFF n* beside every ICC n*: G(N|L2+V0) 1,965, G(V0|L2+N) 1,977, P(SE_cell) 14,140, beside
      the printed D_K 3,257 and D_N 5,118. Plan on the larger of the two until FRESH-RULES-SIM.
    - FRESH-RULES-SIM must report, per contrast:
      - the declared-to-clustered SE ratio;
      - the share of the DEFF that comes from offset noise (the cell-fixed refit bootstrap) versus cell heterogeneity;
      - V0''s leaf count at 3 or more build sizes. The two sizes the plan implies (old-only vs all 4,914) are too few.
- **D2 (MEDIUM; rule A's N arm, [E9], author question 3).**
  - What is wrong:
    - N_A's field values are OLD WORK residuals (WORK parent, WORK-roster models, a response matrix from another
      run). V0_A and K_A fit their offsets on FRESH rows. So under A, D_N and both G legs compare unlike quantities.
    - Q3 offers only "old WORK items or name another pool". The 2026-10-23 draft's own option is missing: N has no
      text-only object, so N_A = N' and the A-vs-B readout for N is 0 by construction.
    - `meter.step("field_txt")` takes neighbours only from `ctx.fit` rows of one Y matrix under one parent
      (`_field_sums`, `reader_sums`). A foreign WORK pool therefore needs new code: a combined matrix, mixed parents,
      and a rule for where S-TAU's inner folds select tau^2.
  - Fix:
    - Rewrite the E9 sentence to state the asymmetry.
    - Add option (ii), N_A = N', to Q3.
    - List the N_A / N512_A cross-pool reader under "code, selftest, mutants and a READY are owed", with its tau^2 rule.
    - State that every N-involving A contrast and its B counterpart are computed on the same WORK-roster model subset.
- **D3 (LOW; rule A V0 routing, READY condition).**
  - What is wrong:
    - V0 splits by the seed-free `axis_cut` (gates.py L509-L560): u* = unit(C1 - C0) of the Lloyd clusters, t > tau,
      a clip rule, then `order_swapped`.
    - u* is not stored. The pickle stores `cut_tau`, `cut_clipped` and `cut_fallback`, and 5 of the gated cuts are
      clipped. For those, the children's unit means do not give u*.
  - Fix:
    - Route by re-running `axis_cut(X512[node.rows], min_child=80)` at each node, applying tau and the child order.
    - The READY requires a count check: the 4,914 old items routed by the function land in their V0 leaves with
      0 mismatches.
    - K_A's nearest-centroid rule already reproduces the old labels (phaseC L19: own-centroid-nearest share 1.0000
      on all 5 seeds).
- **D4 (LOW; ORDER and pins).**
  - What is wrong: "sha256-lf16 of the tree pickle and of each label vector". These are binary files, and LF/CRLF does
    not apply to them.
  - Fix:
    - Pin them by full sha256 (the `AXIS_PINS` precedent).
    - Make the ORDER check a count: the response loader is guarded to 0 fresh-response reads until the pin commit,
      printed at load and at end like the vault guards [0]. A presence check of the pins is not enough.
- **D5 (LOW; conflict check).**
  - What is wrong: CONTEXT rule 1 is not cited, and the transductive WORDING line is not carried.
  - Fix:
    - Cite CONTEXT rule 1 together with the benchzoom precedent: BZ-METER-AXIS Q2 and BZ-AXIS-CONFIRM-MMLU WORDING,
      transductive on text, with no response leak.
    - Bind P and every F word to "fresh responses held out from the meter; leaves built on all items' text, fresh
      items' text included". Never "clean", "content-closed" or "held-out tree".
- **D6 (LOW; F-RESID).** It fires on any detected positive G(V0'|L2+N'), even one far below the 0.062 residual of
  interest, at a large fresh n. Fix: add an interest condition (e.g. fire only if the point is >= 0.062 / 2; otherwise
  print "DETECTED, BELOW INTEREST"), as the meter line does ("NOT SUPPORTED by interest only").
- **D7 (LOW; A-vs-B readout).** The SE of D_AB(X) cannot be assembled from two different resampling schemes. Fix:
  declare one joint item resampling. In each replicate, rebuild B's partitions and refit A's offsets on the same
  resample. Alternatively, print the paired content-cluster SE only.
- **D8 (LOW; wording).** The n* use z 3.3393 / 3.8416 unrounded, while the text prints 3.339 / 3.842. The D_K "DECLARED
  two-way" SE is from seed KM0 only. Fix: say both.
- **D9 (LOW; record).** The REREAD-STEPS queue item and results record give its script as "8610a5d..6d6eb11, merged
  a19c608", but the merge also carries 63336fb (the [P5] / docstring fix per POSTRUN C1). Fix: name 63336fb.
- **Incidental (tool hygiene, outside scope).** `python tools/analysis/results_index.py --help` ignores the flag and
  rewrites `docs/agents/results/INDEX.md`. I triggered this by accident. The output was byte-identical: `git status
  --short` on the file was empty afterwards. Fix: make the script refuse unknown flags.

## Commands / scripts (read-only; scratch `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/dc1026`)

```
git show 65238f64 --numstat --format= ; git show 65238f64 --name-only --format= | wc -l        # 18 0 prog; 8 files
git diff a8990e4b 65238f64 -- docs/judge_v2_program.md | grep -c '^-[^-]'                     # 0
git show 65238f64:docs/judge_v2_program.md | grep -n '^## ' | tail -2 ; ... | wc -l           # L25708; 25724
python -I <queue diff q_old.json q_new.json>        # +7 items, 0 removed, 1 changed, prefixes kept, order kept
python -I <quote check vs author_decisions/2026-10-26.md>                                      # 745 chars, verbatim
python -I power.py                    # Holm z 2.4977; n* / MDE80 / D_inf / floors / worked example (row 6)
python -I -c "<constant-DEFF n* at z 3.3393 / 3.8416>"   # 3,256.9 / 5,117.8 / 1,964.2 / 1,976.5 / 14,140.0; crossover n 7,375
sed -n '1,32p' E:/TaxoArena_tmp/review_flat-compare/phaseC_math.log                         # f inputs L28-L31, MC 0.0092 L20
for c in 6e39fc98 81a99d9b 71df6668 533002c3 f73d7a83; do git show $c --name-status --format= | grep POSTRUN_; done   # 5 x A
git -C Z:/FAC/TUBerlin/benchzoom rev-parse <c>:<path> ; git diff --stat 516c6ba 8d8d824 -- src/ examples/flat-compare.py docs/flat-compare.md   # blobs; empty
tr -cd '\r' < <file> | wc -c ; sha256sum ; git show HEAD:<file> | sha256sum                   # E6 renderings
.venv/Scripts/python.exe -c "<load math_axis_seed0.pkl: 66 nodes, 36 leaves, 22 internal split, 5 clipped, 0 fallback; 422.6 s>"
sed -n 184,300p src/benchzoom/meter.py ; sed -n 440,560p src/benchzoom/gates.py               # field_txt pool; axis_cut (D2, D3)
grep -o 'v4[0-9][0-9]' docs/test_ledger.html | sort | uniq -c                                  # v429
```
