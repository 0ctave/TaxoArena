# DRAFTCHECK: BZ-AXIS-CONFIRM-FRESH draft amendment of 2026-10-23 (TaxoArena f1060523)

Authority: D-2026-10-23-1 (17b9938b; "Go for 1 and 2"). Reviewer: adversarial reviewer, 2026-10-23. Zero LLM calls; nothing
run except read-only greps and arithmetic. Reviewed: `docs/judge_v2_program.md` section "## Registrar's record 2026-10-23
(insertion only; zero calls; nothing run) — BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-23-1: ..." L25692-L25706
(_as_of f1060523) and the queue item BZ-AXIS-CONFIRM-FRESH at f1060523, against benchzoom master 516c6ba
(`examples/flat-compare.py` blob:da00fcda, `docs/flat-compare.md` blob:7067fe89, `src/benchzoom/meter.py` blob:f31973af),
POSTRUN_FLAT-COMPARE (81a99d9b) and its scratch log `E:/TaxoArena_tmp/review_flat-compare/phaseC_math.log`. No code
under review, so no mutants.

## Verdict

**SOUND WITH EDITS.** The amendment adds only lines and is still a draft. Its configurations match 516c6ba exactly. The
Holm arithmetic is right, every copied WORK number matches the record, and the planning n* reproduce from the stated
inputs. Before the full registration, three edits are owed:
- **E1 (HIGH):** the power transport assumes the design effect stays constant as n grows, and it plans D_K with a
  different SE from the one the draft declares.
- **E2 (MEDIUM):** author question 2 needs reframing; the registrar's reading narrows POSTRUN D2.
- **E3 (MEDIUM):** G(V0|L2+N) is planned DESCRIPTIVE-ONLY, yet it is a Holm member and carries the falsifier F-RESID.

E4-E9 are LOW. Nothing in the amendment claims a registration.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; earlier lines untouched | Programme diff 17b9938b..f1060523: 0 removed lines, 15 non-blank lines added (16 with the blank). Commit touches 2 files (`--name-only \| wc -l` = 2). Queue: only BZ-AXIS-CONFIRM-FRESH and meta changed (0 other items). `registration`, `notes` and `author_decision` keep the old value as a prefix; `depends_on` is appended; `last_update` is replaced (expected) | CONFIRMED | - |
| 2 | Still a draft, NOT registered | Heading, STATE line, queue `state` "drafted" and `registration` "none (DRAFT)" all say so. No results JSON (`ls docs/agents/results \| grep -c` = 0). The only "registration" words point to the future full registration | CONFIRMED | - |
| 3 | K and N frozen = 516c6ba flat-compare.py | All 6 pinned blobs equal `git rev-parse 516c6ba:<path>`. Code: FLAT_SEED 20261025, KM_CODE 1, N_PART 5, KM_RESTARTS/ITERS 10/100, EMB_DIM 512 (`im.representation(X,"axis",512)`). k-means++ seeds on (1 - cos), not squared; best summed cosine kept; empty cluster re-seeded from a cluster of size >= 2. k_of = V0's distinct leaves per anchor over ALL items (MATH 9/3/4/6/4/7/3 = 36). L3k = `M.step("field_txt", lab.X, ..., "cv")`, KNN = 40, same category, cosine. C1 = G(arm \| L2 + diff + len) (harness `o_dl`). G(V0\|L2+N) and G(N\|L2+V0) are the L2-chain K2 legs | CONFIRMED (E5 wording) | LOW |
| 4 | Holm over the 4 at FWER 0.05: critical \|z\| 2.498 / 2.394 / 2.241 / 1.960; P one-sided p .00135; experiment-wise <= 0.00135 + 0.05 | 2.498 / 2.394 / 2.241 / 1.960; .00135; 0.05135 | CONFIRMED | - |
| 5 | F is coherent beside P's 3-SE rule | FWER arithmetic is coherent. The SE conventions are not (E2): at WORK's measured leaf factor 1.80, P's "3 meter-SE" equals 1.67 cell-aware SE (one-sided p 0.048), which is looser than F's most lenient Holm step (1.96). F also contains a planned-DESCRIPTIVE-ONLY member that carries a falsifier (E3) | PARTLY | MED |
| 6 | Predictions from POSTRUN_FLAT-COMPARE | Every WORK input matches [P2] / POSTRUN rows 3-7, 9 and 14: -0.1652 (0.0358); -0.2406 (0.054); +0.0067 (0.0102; upper 95% +0.027); +0.2450 (0.0459); +0.1093 (0.0316); +0.2745 (0.0462); +0.3499 (0.0596). The points are not mutually consistent and run against the stated selection direction (E4) | CONFIRMED (inputs); PARTLY (coherence) | LOW |
| 7 | Power plan: n* (cell-aware) D_K 3,015, D_N 6,563, G(N\|L2+V0) 4,742; G(V0\|L2+N) DESCRIPTIVE-ONLY; P 4,346 / 14,403 | From the stated inputs: 3,014.8 / 1,646.3; 4,741.5 / 1,431.4; 113,327.6 / 34,213.1; 4,345.9; 14,402.5. All agree after rounding up (113,327 is rounded down). D_N gives 6,563 only with the 3-dp SE 0.054; the unrounded 0.2406/4.44 = 0.05419 gives 6,609 (E8). The MDE80 tables agree to ±0.001, except D_N (0.566 / 0.400 / 0.329 / 0.253 at the unrounded SE). Substance: the transport is wrong for fixed cells and for the declared D_K SE (E1) | PARTLY | HIGH |
| 8 | Inductive rule is the same for every arm | V0 and K are symmetric under (A) and under (B) (same item set, k_a from V0/V0'). N has no frozen object under either rule (stated). Under (A), D_N therefore compares a frozen object with a reader built on fresh text (E9) | PARTLY | LOW |
| 9 | No conflict with D-2026-10-21-1 | D-2026-10-21-1: "full axis_v1 recipe tree as primary and the zoom curve as a reported secondary; V1b is not registered". Draft: V0 primary, P unchanged, zoom curve secondary on V0 only, K at V0's leaf count (not tuned), F never moves P. (A) and (B) both fit "recipe tree". D-2026-10-21-3 "Keep MATH separate" is respected. No unflagged conflict | CONFIRMED | - |
| 10 | Span L25692-L25706, parent 17b9938b | `grep -n '^## '` puts the heading at L25692; file is 25706 lines; `git rev-parse f1060523^` = 17b9938b; f1060523 is an ancestor of HEAD | CONFIRMED | - |

## Defects (each with its fix; E1-E3 before the full registration, the rest at the registrar's next record)

- **E1 (HIGH, Support (b)-(e), (g)).**
  - (a) Support (c)-(d) transports SE_cell(n) = SE_W x f x sqrt(2,949/n). That treats the cell DEFF f^2 as constant in
    n. Under rule (A) the cells are fixed (36 V0 leaves; 36 K cells per seed). A leaf-clustered SE then has a floor of
    about sqrt(between-cell variance / 36) and does not go to 0. BZ-GRANULARITY-WORK A4 shows the gain is
    heterogeneous across cells ("the gain sits in a handful of splits").
  - Bounding case: all of the excess DEFF is cell heterogeneity, the intra-leaf correlation is constant, f = 1.82.
    Floor MDE80 is 0.277 for D_N and 0.235 for G(N|L2+V0) (both > 0.22), and 0.186 for P under SE_cell (> 0.10). All
    three are then unreachable at ANY n; D_K's n* moves to 3,073. At the measured factor for G(N|L2+V0) (1.33, phaseC)
    the floor is 0.136, so that leg is reachable. D_N's factor was never measured.
  - So (g)'s "every F word is reachable at infinite budget" holds only for an SE that goes to 0 with n. That fails for
    a leaf-clustered SE under (A) whenever the cells are heterogeneous.
  - (b) The draft declares two-way V0-leaf x K-cell clustering for D_K but plans with the ONE-way factor 1.353 (3.41
    SE). phaseC measured the two-way SE (KM0 cells) at 0.0527 items; with the MC term that is 0.0535, f = 1.494, and
    n* = 3,676, not 3,015.
  - (c) "K cell" is undefined for a 5-seed mean, because each seed has different cells.
  - Fix:
    - Match SE_cell to the inductive rule. Under (A) the cells are fixed, so use an SE that conditions on them but
      refits the offsets (e.g. an item bootstrap with offsets refitted and cells held fixed). Under (B) use a
      partition-level bootstrap that rebuilds V0'/K' on resampled items.
    - Transport it with the cell count of that rule: fixed at 36 under (A), growing with n under (B).
    - Plan D_K with the SE actually declared, and define its K-cell term per seed (per-seed two-way variance averaged
      over seeds, plus MC).
    - Restate (g) conditional on the chosen SE.
    - Relay to the author with Q1 that, under (A) with leaf clustering, D_N and G(N|L2+V0) may be unscoreable at any n.

- **E2 (MEDIUM, author question 2 framing).**
  - The registrar's reading "keep P as drafted, since D2 conditions registrations built on M1, i.e. the F family"
    narrows D2. D2's mechanism (shared estimated cell offsets) applies to any partition reader, and D2 itself reports
    "C1(V0) itself is 1.9 SE (MATH) ... under leaf clustering" (phaseC: 0.0570 vs 0.0316, x1.80). The amended
    registration is itself built on M1.
  - Fix: reframe Q2 as a trade-off.
    - For keeping the meter SE: comparability with BZ-METER-AXIS and BZ-AXIS-CONFIRM-MMLU, which both decided under it.
    - Against: at the WORK leaf factor 1.80, "3 meter-SE" = 1.67 cell-aware SE (one-sided p 0.048), looser than every
      F step. Under rule (A) the P(SE_cell) n* may not exist at all (E1).
    - Drop the "i.e. the F family" gloss.

- **E3 (MEDIUM, coherence; registrar rules 5 and 8).**
  - G(V0|L2+N) is planned DESCRIPTIVE-ONLY "at any reachable n" and "decides nothing". It is still one of Holm's 4,
    and F-RESID "fires iff G(V0|L2+N) prints TREE ADDS BEYOND FIELD". A falsifier on a contrast that decides nothing is
    vacuous. The draft also leaves open whether a DESCRIPTIVE-ONLY member stays in Holm's m, or advances the step-down
    when it is rejected.
  - The cause: its Support is computed against the prediction (+0.01). For the falsifier, the relevant target is a
    residual of interest. At half of G(V0|L2) (0.062, the flat-compare §7 K2-B effect), MDE80 = 0.062 at n ≈ 2,948
    (SE_cell 0.0186); at the whole of G(V0|L2) (0.124) it is n ≈ 737.
  - Fix:
    - Power G(V0|L2+N) against a named residual of interest, and keep it deciding for the TREE ADDS BEYOND FIELD
      direction only.
    - PF3 stays range-only.
    - State that every planned member stays in m = 4 (conservative), and that a DESCRIPTIVE-ONLY-by-support member's
      rejection still advances the step-down. Alternatively, fix m at the number of deciding contrasts before data.
      Either way, write it at the full registration.
- **E4 (LOW, predictions).**
  - PF5 - PF6 = -0.15 but PF1 = -0.16, and PF5 - PF7 = -0.23 but PF2 = -0.22.
  - "fresh D_K and D_N are expected no larger than on WORK" (signed, since WORK favours V0), yet both points (-0.16,
    -0.22) sit above WORK (-0.1652, -0.2406).
  - Fix: make the points mutually consistent and on the stated side of WORK, or drop the direction sentence.
- **E5 (LOW, frozen config wording).** In `default_rng([20261025, 1, a, s])`, a is the RANK of the anchor in sorted
  depth-1 node-id order (`kmeans_partition`; plan §2), not the anchor. Under (B), V0' can number its anchors differently.
  Fix: write "a = rank of the anchor's depth-1 node id", as in plan §2.
- **E6 (LOW, registrar rule 10).** The benchzoom master working tree is CRLF for the two pinned docs/runner files
  (1,478 and 261 CR bytes). Fix: print beside the LF pins `examples/flat-compare.py` sha256-lf16:9bc8b35a76f508f9 /
  sha256-crlf16:d7ae06f6a550aa21, and `docs/flat-compare.md` sha256-lf16:ed6359a6f3591152 /
  sha256-crlf16:6337577e7e3968bb.
- **E7 (LOW, registrar rule 11).** `depends_on` names BZ-TREE-VARIANTS-WORK and FLAT-COMPARE, and neither is a queue
  item (membership check: both False). The hand-back says this only for FLAT-COMPARE. meta.ledger_version is still v428
  although the ledger is v429 (stale from 10-22; this commit edited meta.last_update and left it). Fix: create the two
  records/items, or point `depends_on` at the review files; set meta.ledger_version to v429.
- **E8 (LOW, planning inputs).** "1.82 ... the largest measured" was not measured; it comes from the rounded "1.9 SE".
  The measured factor for C1(V0) is 1.80, and D_N's factor was never measured. Its n* uses the 3-dp SE (6,563; unrounded
  6,609). The measured G-leg factors are 1.33 / 1.49 (n* for G(N|L2+V0) 2,536 at 1.33). Fix: cite phaseC's measured
  factors and label 1.82 as a rounded conservative stand-in.
- **E9 (LOW, symmetry).** Under (A), V0 and K are frozen objects while N reads fresh training text, so D_N and the G legs
  compare an object with a recipe. Only (B) gives recipe-vs-recipe for every F contrast. Fix: one sentence in the
  inductive-rule paragraph, relayed with Q1.

## Commands / scripts (read-only; scratch `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad`)

```
git show f1060523 --numstat                                   # 16 0 programme; 8 6 queue
git diff 17b9938b f1060523 -- docs/judge_v2_program.md | grep -c '^-[^-]'   # 0
git show f1060523 --name-only --format= | wc -l              # 2
python -I -c "<queue diff: old value prefix of new; other items changed 0; depends_on membership>"   # BZ-TREE-VARIANTS-WORK False, FLAT-COMPARE False
git -C Z:/FAC/TUBerlin/benchzoom rev-parse 516c6ba:<path>     # da00fcda / 7067fe89 / f31973af / 7afb0a8a / 7fc4b73d / d45d4166
git -C .../benchzoom show 516c6ba:examples/flat-compare.py > fc.py; sed -n 140,335p fc.py; sed -n 368,422p fc.py; sed -n 945,992p fc.py
sed -n 15,35p;170,200p;245,300p src/benchzoom/meter.py       # KNN = 40, same category, nearest_cos, S-TAU "cv"
tr -cd '\r' < <file> | wc -c ; sha256sum                       # CRLF renderings (E6)
python -I power.py                                            # Holm z, MDE80 tables, n* (stated inputs), fixed-36 bound, F-RESID n
grep -n 'SE sensitivity' E:/TaxoArena_tmp/review_flat-compare/phaseC_math.log   # leaf factors 1.80 / 1.37 / 1.33 / 1.49; 2-way D_km 0.0527
sed -n 1,30p docs/agents/author_decisions/2026-10-21.md ; cat docs/agents/author_decisions/2026-10-23.md
```
