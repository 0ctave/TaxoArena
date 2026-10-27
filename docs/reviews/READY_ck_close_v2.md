# READY review: ARCH-V2-CK-CLOSE-V2 (CK-CLOSE-v2), gating the one-shot ARCH-V2-SPLIT-DRAW-2

Reviewer: adversarial-reviewer, 2026-09-24. Zero judge calls. Single process, read-only (`mode=ro&immutable=1`). DEV seeds only; the registered seed ARCHV2-SPLIT-2 was never drawn or passed to any code.

## [DELTA 2026-09-24, inserted after fc94b40] VERDICT: READY for the one-shot at 0414fb8's tools. D2, D3 and D7 are FIXED. One new MEDIUM (N1) and two LOW notes (N2, N3). C1 and C3 are amended as below; C2 and C4-C6 stand.

Scope: branch ck-close-v2, commits b506005, 3f0f9af and 0414fb8.

**Claims checked**

| # | claim | result | command | mine vs claimed |
|---|---|---|---|---|
| Δ1 | Only build.py and gates.py changed | CONFIRMED | `git diff --name-only e9ee12a 0414fb8`, counted with `wc -l`: 12 paths. 10 are manifests; the 2 tools are data_v2/build.py and data_v2/gates.py. | build.py blob:519c69d9 / sha256-lf16:589467d26b9cee2e. gates.py blob:28876ea9 / sha256-lf16:cf686b124cd7b36b. The working tree equals LF. These are the blobs at b506005 (build) and 3f0f9af (gates), so ED6 ran this code. passage_closure 003d5d4e, independent ba7fedf1, split a0ed6e06, common 462ffef3 and views 7a0f0ab3 are unchanged. |
| Δ2 | My mutants now die: 20 of 22 | CONFIRMED | mutate.py on a scratch copy of the 0414fb8 files, run under python and -O | 20 of 22 killed in both modes. M2, M2b, M3, M3c and M11 are now killed by G2 edge mismatches. The survivors are M6b and M16, both equivalent. The control passes. |
| Δ3 | Selftest: 182 checks under python and -O | CONFIRMED | `gates.py --selftest` on the scratch copy | rc 0, "ALL PASS (182 checks)" in both modes |
| Δ4 | D3: R1 fails closed (rc 3, a VOID manifest) | CONFIRMED | selftest lines SELFTEST-R1-D7 131-134. That selftest ran the build end to end with a live foreign python: rc 3, r1_void True, of_record "VOID (R1): ...". I also ran `r1_verdict` myself. | CLEAN when inputs are unchanged and no foreign process is seen. VOID on a changed input. VOID on a foreign pid. |
| Δ5 | D7: 523 / 228 / 89 against draw 1's committed export, read in its LF rendering | CONFIRMED | ED6_gates_r2.txt L37-L39 | {"EVAL": 228, "GATE": 89, "TRAIN": 523}, 0 absent; the export re-hashes to table_sha 1b5f6395.... This matches my row 1b. The first ED6 gate run (ED6_gates.txt, 36 lines) stopped inside D7 on the CRLF working-tree copy with no verdict; it is committed as evidence, and the rerun passes. |
| Δ6 | ED6 reproduces ED5's closure | CONFIRMED | ED6 transcript | Corpora sha256 c8afeaa6... and 21d79e8c... are byte-identical to ED5, so my third-implementation verification carries over unchanged. U 840 e3d291d0..., P 2,710 / O 62 / D 1, a4c613ed2d4957ad, 18,800 components. "[R1] verdict: CLEAN" in 14 samples. Gates ALL PASS. |

**Can a clean run be voided spuriously?** I executed each case with 0414fb8's `data_v2.build`:
- **Agent shells and git are not foreign.** The snapshot matches only `^(python|pythonw|java|javaw)\.exe$`. A sample taken while `git log` and `bash -c "sleep 5"` children were alive gave "0 FOREIGN" and a CLEAN verdict.
- **The launch chain is admitted.** The chain resolved from the OS parent map was bash.exe ×3, claude.exe, pwsh.exe, idea64.exe, jetbrains-toolbox.exe and explorer.exe. None of these is python or java.
- **The build starts no python or java child.** `grep subprocess|multiprocessing|sys.executable|Popen` over build, ingest, split, views, ro, common and the three closure modules finds only `git`, `powershell` and `ps`.
- **If the ancestor lookup fails,** only the build's own pid is admitted. The verdict is still CLEAN when the launch chain holds no python.
- **N1 (MEDIUM): a failed process sample voids the run.** If the CIM query fails or times out once, `process_snapshot` returns `["?", "sampling failed", ...]`. The pid `?` is not admitted, so the run is VOID ("FOREIGN process ? sampling failed", executed). One transient failure among about 14 samples would therefore burn the one-shot seed after the draw has been computed. A failed sample does leave the window unverified, so failing closed is defensible, and I accept it. Two fixes:
  - Label the reason as a sampling failure, not a FOREIGN process.
  - Operationally, see C2' below.
- **N2 (LOW): any foreign python or java voids.** That includes a peer's `--selftest`, which rule 7 W1-W5 would admit while the pool is FREE, and any java.exe, for example a Gradle or Kotlin daemon started by the IDE. For a one-shot, this is the right strictness: the orchestrator must announce the window so that no agent runs python or java during it.
- **N3 (LOW): pid reuse can wrongly admit.** A dead ancestor's pid reused by a new python process would be admitted. This errs toward a false CLEAN, is unlikely within a 3-minute window, and the post-draw review checks the samples. Documented only.

**C1, amended.** The draw runs from 0414fb8's tools/, or from a merge whose blobs equal these exactly (blob / sha256-lf16):

| file | blob | sha256-lf16 |
|---|---|---|
| build.py | 519c69d9 | 589467d26b9cee2e |
| gates.py | 28876ea9 | cf686b124cd7b36b |
| passage_closure.py | 003d5d4e | 2d36985c91133d30 |
| split.py | a0ed6e06 | 395848223cf4741e |
| independent.py | ba7fedf1 | 0a1d49c80f3baff3 |
| common.py | 462ffef3 | 4cc46c38670db854 |
| views.py | 7a0f0ab3 | 98bad1d49aeebf3f |
| content_closure.py | 1533cb5a | - |
| split_side.py | 05224b5a | - |

The transcript must print "dirty paths: none", and the seed/registration pair must be exactly as registered. The e9ee12a pins in the original C1 are SUPERSEDED for the draw. They remain the code of ED5.

**C2', added to C2.** Immediately before launch:
- announce a window with no other python or java process (N2);
- run one `ProcessLog` sample (or a DEV build) to prove that the CIM query answers (N1);
- keep at least 12 GB of RAM free (rule 7).

**C3, amended.** C3 stands, plus:
- the exit status is 0;
- the transcript shows "[R1] verdict: CLEAN";
- the manifest has `r1_void` false;
- G2 passes D7 with 523 / 228 / 89 and 0 absent.

A run that exits 3 is VOID, and a re-draw needs a new registered seed and a stated reason.

## VERDICT: READY, subject to conditions C1-C6. No BLOCKER. Three MEDIUM and five LOW defects, none of which changes the closure on the ED5 corpora.

My own third implementation of U, P, O and D, written from the registration text (docs/judge_v2_program.md L16101-L16130), reproduces the sealed ED5 closure exactly:
- the U set and its digest;
- the P and O edge sets and the D group;
- the 15-19-token band;
- the component partition and its ids;
- the DEV draw's side for all 20,544 items.

The closure is free of any seed. Its edge-set sha matches the builder's under six hash seeds across the two implementations. The ingest is byte-deterministic (ED4 and ED5 are byte-identical). So the one-shot draw's closure is fixed ahead of time, provided the draw sees the same inputs (conditions C2 and C3).

## Identity (at e9ee12a; LF rendering of record; the working tree equals LF for every file, so there is no CRLF difference)

| file | blob | sha256-lf16 |
|---|---|---|
| tools/analysis/passage_closure.py (new) | 003d5d4ef28bd6f5ed9b5020b669e206d995d92e | 2d36985c91133d30 |
| tools/analysis/data_v2/split.py | a0ed6e061a91541112768614ec967fb47983dd27 | 395848223cf4741e |
| tools/analysis/data_v2/independent.py (new) | ba7fedf1aab9a2c3a22d7e35d9bc1bae3a50b3e4 | 0a1d49c80f3baff3 |
| tools/analysis/data_v2/gates.py | 166b444f48bd309dc40678a9e49e8929d572196d | d77594a459f34398 |
| tools/analysis/data_v2/build.py | 6b318c56cb716a01e07c0b4c6de07ccc68b2bd43 | 72f2187d1fa65ae0 |
| tools/analysis/data_v2/common.py | 462ffef3b839624685cfea7b8abd3181d7b5a8c7 | 4cc46c38670db854 |
| tools/analysis/data_v2/views.py | 7a0f0ab31a09e02fcc54db6b8ce26d99284b1603 | 98bad1d49aeebf3f |
| tools/analysis/content_closure.py (unchanged) | 1533cb5a56c8e001ddc65d3e2ec0cc4b56aa87e3 | - |
| tools/analysis/split_side.py (unchanged) | 05224b5a4b76e74353bc3931ec69f0b14f0e340b | - |

Commands:
- `git hash-object` on each file.
- `git show e9ee12a:<p> | sha256sum`, compared with `sha256sum < <p>`.
- `git diff --stat 7cf6284 e9ee12a -- tools/analysis/split_side.py tools/analysis/content_closure.py` prints nothing.
- `git diff --stat a72e8a4 e9ee12a -- tools` prints nothing: e9ee12a adds only manifests, so the ED5 build ran this exact code.

The DEV manifest `data_v2/manifests/DEV_DEV-20260924-ED5.json` has sha256 1fc85eb79af0836f2951704331c8729aad978ed03a99468cb2c62916bb8387eb, as claimed.

## Per-claim table

Every script is in the session scratchpad `C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\ckv2\`:
- `load.py`: read-only loader of the two ED5 corpora.
- `third.py`: the third implementation.
- `cmp.py`, `variants.py`, `either.py`, `mixed.py`, `deg.py`, `deg2.py`, `kish.py`, `u840.py`, `devsim.py`, `witness.py`, `det.py`.
- `mutate.py`: runs mutants on a scratch copy `mt/`; the worktree is untouched.

**Data object.** The ED5 corpora:
- corpus_v2_mmlu_pro_v2.db, sha256 c8afeaa6...;
- corpus_v2_union_mc6.db, sha256 21d79e8c...;
- 21,384 items before U;
- split_v2_DEV_DEV-20260924-ED5.db, sha256 427ec001....

All three DBs were re-hashed after the review and are unchanged. The mtimes are unchanged. `git status` of the worktree is empty.

| # | claim | result | command / script | mine vs claimed |
|---|---|---|---|---|
| 1 | U excludes 840 items, digest e3d291d0..., universe 20,544 | CONFIRMED | third.py; cmp.py (compared with the `excluded_u` table) | 840 / e3d291d0042cf044... / 20,544, the same set. Every excluded item has no source_row, no ACTIVE response and at least 1 quarantined vote. |
| 1b | U is exactly the author's 840 (TRAIN 523 / EVAL 228 / GATE 89 on the superseded split) | CONFIRMED (a check the build does not make) | u840.py against the side table of split_v2_REG_ARCHV2-SPLIT-1 (immutable) | 840 of 840 present, by side 523 / 228 / 89. 0 universe items are missing from the old split. |
| 2 | Edges P 2,710, O 62, D 1; band P 2,773 / O 59 | CONFIRMED | third.py; cmp.py (compared with the `closure_edge` table) | P, O and D are equal as sets (symmetric difference 0 / 0 / 0). Band 2,773 / 59. |
| 3 | 18,800 components, largest 14 (BBH) | CONFIRMED | third.py; cmp.py | 18,800 / 14. Component id differs for 0 of 20,544 items (the id is `c:` + the smallest stem_key). |
| 4 | Before U, the build reproduces the DEV-SIM (18,938) | CONFIRMED | kish.py (my pre-U closure) | P 3,303, O 694, D 695 groups, 18,938 components. |
| 5 | EVAL share 0.3006 | CONFIRMED | cmp.py (my own draw rule, seed DEV-20260924-ED5) | 6,175 / 20,544 = 0.3006. 0 of 20,544 sides differ from the sealed side table. |
| 6 | Kish: MMLU-Pro 1.078, BBH 1.735, MuSR 2.413 | CONFIRMED (numbers) | kish.py | 1.078 (3,507 items / 3,400 components), 1.735, 2.413 |
| 6b | "The difference between MMLU-Pro 1.078 and the DEV-SIM's 1.185 is one of units" | **REFUTED** | kish.py, deg.py | The difference is U, not a unit. With my implementation's own units (EVAL items per component), before U, over 20 DEV seeds: median **1.186** (range 1.157-1.206), which matches 1.185. After U: median 1.072 (1.053-1.088). Cause: 704 of the 840 excluded items are `\textdegree` response variants whose D edge (695 groups before U) pairs them with active twins. After U, D has 1 group. BBH and MuSR are unchanged by U: medians 1.712 and 2.445 against 1.80 and 2.44. See D1. |
| 7 | K2: the edge-set sha a4c613ed... is the same under two hash seeds | CONFIRMED | `PYTHONHASHSEED={1,987654} python gates.py --edge-sha <ED5 corpora>` (builder code); det.py (my code) under PYTHONHASHSEED 3 and 777 | a4c613ed2d4957ad all 4 times. My implementation, serialised the builder's way, gives the same sha. The component-map sha16 446e79bd6b814b41 is identical under both seeds. |
| 8 | No seed or clock enters the closure | CONFIRMED | Read split.py L576-L581: `load_corpora(corpus_paths, out)` has no seed argument, and `apply_closure_v2` runs inside it before `compute(data, seed)`. My implementation takes no seed. | Structural and by execution (row 7) |
| 9 | Selftest: 169 checks pass under python and -O | CONFIRMED | `python tools/analysis/data_v2/gates.py --selftest` on the scratch copy, both modes (mutate.py CONTROL) | rc 0; "ALL PASS (169 checks)" in both modes |
| 10 | Mutants: all killed | PARTLY | mutate.py: 22 reviewer mutants on top of the builder's 9. The passage_closure pin is updated to the mutant's blob, so no kill is the vacuous pin refusal. | 15 killed and 7 survived. Of the 7: M6b is equivalent by construction; M2 and M2b have no effect on real data; M16 is equivalent on both the fixture and ED5; 3 (M3, M3c, M11) change the real-data output (164,351, 14 and 1 edge; see D2). Table below. |
| 11 | The gates' independent implementation matches U, P / O, D and the sides (0 of 20,544) | CONFIRMED, and a third implementation agrees | cmp.py | see rows 1-5 |
| 12 | independent.py is independent | PARTLY | A verbatim-line intersection script: shared lines longer than 25 characters are 1 with passage_closure, 3 with split and 2 with gates (imports, `for k, cid in enumerate(cids)`, `if cv == "mc6-2026-09-11":`, a union-find line). An AST gate forbids importing split, passage_closure or common.pc. | Independent in CODE. NOT independent in INTERPRETATION: the same author made the same choices on every open point (pair rule, df per channel, the item's own modal stratum and its tie rule). My third implementation made those choices from the spec text and the data leaves only one of them open (the pair rule, deviation 1). |
| 13 | R1: 13 of 13 process samples are clean | CONFIRMED (count), PARTLY (the guard) | `grep -c '^\[R1\].*: 0 python/java process(es) besides'` on the ED5 transcript gives 13, the same as the total count of samples. I executed `build.ProcessLog` with a foreign `python -c sleep` alive: it reported "1 python/java process(es) besides this build" at launch, during and after. | Detection works by execution. The guard is RECORD-ONLY: a foreign process, or an input marked CHANGED, prints a line and the build still exits 0 (D3). |
| 14 | The registered seed was never drawn | CONFIRMED | `find . -name "split_v2_REG*" -o -name "*ARCHV2-SPLIT-2*"` finds only the REG_ARCHV2-SPLIT-1 DB. `git log --all -S "ARCHV2-SPLIT-2:2929bd46"` lists 3 commits: 7cf6284 (registration), 7fc8b97 (pin) and d3ab777 (record). | REGISTERED_DRAWS L75 holds exactly "ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2", and `git rev-parse 2929bd4` gives that full sha. |
| 15 | Support section | N/A is ACCEPTED | Registration: "an ENGINEERING registration: Support N/A, the deciding observables are equalities and counts" | Correct: no estimate decides K1-K5. The Kish figures are upper bounds at rho = 1 and must not be cited as the source of a DEFF for any downstream Support section. |

### Mutants (reviewer's, python and -O; mutants.txt)

| mutant | fixture selftest | effect on the ED5 data (third.py with the same mutation) |
|---|---|---|
| M1 N off-by-one: join needs 21 or more tokens | KILLED (G2 edges) | P -78, O -7 |
| M1b edge at 19 tokens | KILLED | - |
| M2 / M2b df counted over variants, not items | **SURVIVED** | 0 edges change: equivalent on real data |
| M3 BBH mask over the whole BBH source, not the task | **SURVIVED** | **P 167,061 (symmetric difference 164,351), 16,999 components** |
| M3b BBH mask `>= 5%` | KILLED | - |
| M3c global mask `df >= R` | **SURVIVED** | P symmetric difference 14, O 2 |
| M4 U also drops response-only items that have an ACTIVE response | KILLED (the K1 assertion) | - |
| M4b U keeps quarantined-only items | KILLED | - |
| M5 D applied to options | KILLED | 250 D groups, 13,968 components |
| M6 component id = the largest stem_key | KILLED (G2 sides) | - |
| M6b union-find root = the larger element | SURVIVED | equivalent (the id is min(stem_key) whatever the root) |
| M7 pair rule "either" | KILLED | P +23 (deviation 1) |
| M8 diagonal ignored | KILLED | - |
| M9 D without its second regex | KILLED | - |
| M10 D off | KILLED | - |
| M11 no casefold | **SURVIVED** | P symmetric difference 1 |
| M12 O reads the stems | KILLED | - |
| M13 edges not joined into the union-find | KILLED (K4 crossing check: not vacuous) | - |
| M14 O not joined | KILLED (K4) | - |
| M15 BBH never recognised | KILLED | - |
| M16 families from before U kept | SURVIVED | equivalent: the excluded items carry no family (0 declared, and quarantined responses give no qid edge) |

## Rulings on the five deviations

1. **Pair rule "both": ACCEPTED, to be recorded before the draw.** The spec's own words ("every 8-shingle UNMASKED", with the mask defined per item) read naturally as "unmasked for each item of the pair".
   - The rule is output-relevant only for BBH pairs across tasks. On ED5, 0 BBH x non-BBH pairs share any 8-shingle (mixed.py), so the BBH/non-BBH framing of the deviation is empty on the data.
   - Against "either" (either.py): +23 P edges (16 tracking_shuffled_objects and 7 logical_deduction sibling-task pairs), 0 O edges, 18,789 components against 18,800.
   - "both" reproduces the registration's own DEV-SIM before U (18,938). "either" would give 18,927, because U removes no BBH item and the BBH shares are identical before and after U. So the registration's numbers were made under "both".
2. **DRAW-1 in RETIRED_DRAWS and refused: ACCEPTED.** This implements "ARCHV2-SPLIT-1 is NEVER reused". Draw 1 stays re-derivable at b51eb71 with the v1 code, and under v2 code it would be a different split under the same name. The selftest D1 executes the refusal both by entry and by seed.
3. **K3 D reading (D joins \textdegree with °; P joins ° with U+FFFD): ACCEPTED.** The registered formula for d() governs, and it cannot map U+FFFD. The reading is also empty on the data:
   - U+FFFD occurs in **0** variant stems, 0 option lists and 0 source_row texts or options of either corpus. It also occurs in 0 rows of `eval_results.question_text` and `mmlu_pro.question` in the source cache (deg2.py; SQL `instr(...,char(65533))`).
   - All 704 `\textdegree` stems are variants from quarantined responses (origin = response), and all are excluded by U.
   - In the universe, D joins exactly 1 pair: "298 °K" against "298°K", a whitespace case (deg.py).
   - The "U+FFFD twins" in the data-steward's evidence (L16094) do not exist in these corpora. The record should say so by insertion.
4. **The edge-set sha is not comparable with bd5e56db: ACCEPTED.**
   - K2 is met on the build's own serialisation (row 7).
   - bd5e56db2ec18a0e was not reproduced by any of 240 combinations: before/after U × {P, PO, POD, PO + D-all-pairs, PD} × prefix stripped or not × 12 serialisations (witness.py).
   - The registration's counts reproduce instead: 18,938 components; 121 option-only edges that are degree twins. Two counts differ slightly: 52 shared option menus against 50, and an MMLU-Pro 15-19 band of 178 against 181 (D6).
5. **Pool rows via merge_pool: ACCEPTED.**
   - The pool table changes schema: `n_items` becomes `n_items_by_scope` (JSON). Views copy the DDL.
   - `git grep "FROM pool"` on main finds no reader outside data_v2. The downstream re-pin must read the new column.
   - The "one id naming two component counts" refusal cannot be reached, because the id is the hash of the component list. It is a tautological guard, and harmless.

## Defects

- **D1 MEDIUM: the explanation of the Kish difference is wrong.** 1.078 against 1.185 comes from U, not from units (row 6b).
  - Fix: a record correction by insertion.
  - Add Kish before U to the "BEFORE U, reproduced here" line of `v2_report`, so that K5 prints like against like.
- **D2 MEDIUM: the K3 fixture is blind to 4 mutants.**
  - The fixture has one BBH task, so "the task's 5%, not R" tests "not R" only. Stratum against source is not tested: M3 survives, and on real data it would add 164,351 edges.
  - There is no unmasked case at df = R = 6 (M3c survives), no upper-case variant (M11) and no item with 2 variants (M2).
  - On a real build, G2 (independent.py) catches M3, M3c and M11, but G2 runs AFTER the one-shot draw has happened. C2 and C3 cover the draw.
  - Fix, for any later edit of passage_closure: add a second BBH task, a df-6 unmasked run, a case pair and a two-variant item to the fixture.
- **D3 MEDIUM: R1 only warns.** `build.py` prints "[R1] AN INPUT CHANGED DURING THE BUILD: the build is void", still writes the manifest and exits 0. A foreign process in a sample prints and never refuses.
  - For a one-shot, a detection after the fact voids the draw anyway, so the fix is operational (C2 and C3).
  - Recommended code fix: a non-zero exit on CHANGED, and a manifest flag set on any foreign process.
- **D4 LOW: a record defect.** The registrar's line from d3ab777 (the "FIVE BUILDER DEVIATIONS" paragraph) contains a literal TAB: `D joins <TAB>extdegree <-> °`. `od -c` shows `\t e x t d e g r e e`; a backslash escape was eaten.
  - Fix: an insertion bracket restoring "\textdegree".
- **D5 LOW: the builder's mutant harness is not committed.** In its transcript, the "hash() used for shingle identity" mutant is "KILLED rc 1 no failing line". That is a kill by crash, which cannot be verified.
- **D6 LOW: small unexplained DEV-SIM differences.** O-only menus: 52 here against 50. MMLU-Pro 15-19 band: 178 here against 181. The steward's scan is uncommitted. These are not criteria; disclose them.
- **D7 LOW: K1's assertion is tautological.** It applies the same predicate that defines U, in both implementations. The check that is not tautological is row 1b (the superseded split: 523 / 228 / 89 = the registration).
  - Fix: add row 1b to G2, by count.
- **D8 NOTE:** the K4 "0 edges crossing sides" check holds by construction but is NOT vacuous: M13 and M14 are killed by it.

## Conditions for the one-shot ARCH-V2-SPLIT-DRAW-2

- **C1 Code.** Run from e9ee12a's tools/ (byte-identical to a72e8a4 and ED5), or from a merge whose blobs equal the identity table above. The transcript must print "dirty paths: none". The registered pair must be exactly `--seed "ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2" --registration ARCH-V2-SPLIT-DRAW-2`.
- **C2 Pre-launch inputs, by command, before the draw.** `sha256sum` must equal the ED5 R1 BEFORE values:

  | input | sha256 |
  |---|---|
  | mmlu_pro_dataset_cache_v2.db | 4f65414f7625a1e7... |
  | multicorpus_cache_v1.db | ad66e30a0eb4abd6... |
  | experiment_results/judge_solve/grok-reasoning.db | 536e3f463ced750b... |
  | experiment_results/judge_solve/grok-reasoning-v1.db | e6e5b783db6c3c2a... |

  I re-verified the first two at the end of this review. If any value differs, do NOT launch: run a new DEV build and re-review the closure.
  Rule 7 (W1-W5 and the process list) holds for the launch, and no other python or java process is alive.
- **C3 Post-run acceptance (otherwise the draw is VOID, and a re-draw needs a new registered seed).** The transcript must show all of the following:
  - corpus sha256 c8afeaa6... and 21d79e8c...;
  - U 840, digest e3d291d0042cf044...;
  - edges P 2,710 / O 62 / D 1, band 2,773 / 59;
  - edge-set sha16 a4c613ed2d4957ad;
  - 18,800 components;
  - every [R1] sample "0 python/java process(es) besides", and all 4 inputs UNCHANGED;
  - gates ALL PASS, with G2 at 0 differ.
  All but the draw itself is fixed by this review, independently of the seed.
- **C4 Record the rulings first.** The registrar records rulings 1-5 by insertion BEFORE the draw, with the pair-rule sensitivity (+23 P edges, 11 components, all BBH sibling-task pairs) and the correction to the U+FFFD evidence (0 occurrences). The D1 and D4 corrections go in the same insertion.
- **C5 R4.** The post-draw review re-derives U, P, O, D, the components and the sides with a third implementation (the scratchpad `third.py` + `cmp.py` does this in about a minute, pointed at the REG DBs) and re-hashes the side TSV row by row. R5 applies: no read of the side table before the manifest is committed.
- **C6** The registered seed appears in no dry-run, DEV build or selftest before the draw.
