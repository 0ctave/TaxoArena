# POSTRUN_rp12_r2: ARCH-V2-E-T-R2 (lane r2, G10/G11/G13/G14/G15) and EVAL-METRIC-DETERMINISM (five-leg run)

Adversarial-reviewer, 2026-10-01, zero calls, read-only. Registration: prog L22417-L22434 plus its brackets through
L22500 (`_as_of` 53a46849), and ARCH-V2-E-T L22028-L22060 (criteria and brackets carried over). Builds at M 2703f2c2.
EMD: registration L20311ff, outcome L22483-L22492. G12 and FLAT are NOT reviewed here (not yet read).
Data objects: snapshots.db of the pinned worktree, COPIED to scratch (sha256 9e5536e5... before = copy = after, mtime
unchanged, -wal 0 B), opened `mode=ro&immutable=1`; the side export REG_ARCHV2-SPLIT-2_2929bd46..._side.tsv (sha256 47e9048b...);
the B0 graft readouts; the RP03 views gen_view_REG.db / eval_view_REG.db (read-only files, `immutable=1`); the EMD
evidence dirs and the operator's staged copy (scratchpad/emd/run_emd_1, `sha256sum -c SHA256SUMS` 285 of 285 OK).

## VERDICT

ARCH-V2-E-T-R2: **G10 VALID (HELD), G11 VALID (HELD), G13 VALID (FAILED, genuine), G14 VALID (HELD), G15 VALID (HELD)**,
each under the wording conditions W-1..W-6 below. INC-C3: a procedural ORDER breach, **no effect on any artefact** (confirmed).
EVAL-METRIC-DETERMINISM: **VALID (DONE as recorded; MERGEABLE confirmed; merge 1f671215 src = the 4 FIX files)**, under W-7
and defect D-5. No BLOCKER.

## Per-claim table (deciding claims only)

| claim | record | mine | status | sev |
|---|---|---|---|---|
| G10 7 pairs byte-identical on A1-A5 (A4 as sets), A1/A2 N/A for graft | HELD | 7/7 pairs no diff; A4 set-equal AND multiset-equal 7/7; raw node-order differs in 266 of 439 nodes (ruling (A) was needed, hides nothing else); all dag lines equal (not only the last) | CONFIRMED | - |
| D-G-2 duplicate queryIds within a node | "disclosed in the outcome" | **0 of 439 nodes in B0, 0 of 439 in B0'**; g10_r2.txt does NOT print the required "set, multiplicity not compared" line (0 hits) | CONFIRMED count / wording OWED | LOW |
| G11 P_fl (6,139 / 5,628) | 0.8119 [0.8013, 0.8223] | 0.8119; replay of the registered draw [0.8013, 0.8223]; own seeds 7/11 [0.8009, 0.8218] / [0.8019, 0.8220] | CONFIRMED | - |
| G11 D_fd | +0.0937 [+0.0828, +0.1054] | +0.0937; replay [+0.0828, +0.1054]; P_descent 0.7182; discordance 0.1673 | CONFIRMED | - |
| G11 support | DEFF 1.124 / 1.291; MDE80 0.0148 / 0.0162 | replay SE 0.00529 / 0.00577 (same); n/G 1.0908; observed P_fl - 0.75 = 0.062 and D_fd 0.094 both >> MDE80: SCOREABLE stands | CONFIRMED | - |
| G13 D13 = P_fl - P(KC_0) | -0.0215 [-0.0301, -0.0125]; spread_KC 0.0112 | re-executed: KC_0..4 0.8334 0.8394 0.8340 0.8446 0.8413, spread 0.0112, D13 -0.0215 [-0.0301, -0.0125], SE 0.00452, DEFF 1.214, n_eff 5057.x (printed 5058, rounding) | CONFIRMED | - |
| G13 FAILED genuine (B-A3 expected UNDETERMINED) | FAILED | own spherical k-means (own init/seeds, 12 seeds): every P(KC) in [0.8353, 0.8448] > P_fl by >= 0.0235; registered implementation over 20 seeds: spread 0.0147 < 0.0215, KC_0 is the LOWEST of 20 (D13 the most conservative); discordant 204 vs 394 | CONFIRMED | - |
| G13 bundle is R2's | - | npz byte-equal to R1's bundle; explained: R2 B0 graft_flatleaf MAIN_union_routing_{queries,leaves,train_queries}.csv byte-equal to R1's (provenance only, not a readout); eval_fl == my R2 flatLeaf correctness 6,139/6,139; leaf_major = R2 leaves csv (133); labels = routing true_key 100% | CONFIRMED | - |
| G14 identity C1 | +2.67pp reproduced | +2.67pp (declared policy 52/52 cells = the frozen JSON) | CONFIRMED | - |
| G14 G_tree (full set, 5,907 / 5,404; TRAIN 11,841) | +2.62pp, two-stage [+1.43, +3.82] | point +2.62pp, M -0.05pp; best single Qwen2.5-72B; tree policy 52/52 = JSON; two-stage interval NOT re-derived (one-stage frozen-policy cluster SE 0.00532 gives lower +1.58pp; the two-stage 0.00610 is wider, as it should be) | CONFIRMED (point, counts); interval re-executed not re-derived | - |
| G15 drift per member | 0.0000pp x5, 0.0151pp mmlu_pro_lb | same; mmlu o1 total 7,231 vs 7,233 (4 counts moved), o2 0; shuffle seeds 1/2 in the manifests and EFFECTIVE (B0 vs o1 differ on A1-A5 for musr and mmlu) | CONFIRMED | - |
| INC-C3 "no effect" | ruled no effect | worktree graft TOMLs mtime 09:43:41 < start 09:44:02 (B0 flatleaf); LF sha 9873e036 / 3a7f7852 / 491cf857 = manifest config_sha256_lf = diagnostics/config.toml = the bytes parsed at 07:48:58Z (executed, 9/0/0); B0' graft parsed (executed, 07:56:46Z) BEFORE its launch; ConfigParsesTest walks experiment_configs/** incl. untracked | CONFIRMED | LOW (procedural) |
| EMD C1 0 of 6 | HELD | 0 of 6 (byte compare, evidence_R1/R2/R3) | CONFIRMED | - |
| EMD C3 0 of 24 | HELD | 21 files 0 differ under D9b's drops (file set + 2 pool tables from c3 log, not re-read: the DBs are not committed) | CONFIRMED (21 of 24 recomputed) | - |
| EMD C2 / P8 | HELD | staged XML: FIX golden 8/0/0; BASE 7 of 8 FAIL (tdcSampled FAILS; mainFixture passes); FIX failures = the two known | CONFIRMED (from temp copy only, D-5) | MEDIUM |
| EMD P6 / P7 | 0.467% / 1.89% | 0.00467 / 0.01890 | CONFIRMED | - |
| EMD merge scope | src = 3 metric files + test | `git diff --name-only 2f080e0 1f671215 -- src` = 4; 6569cd3..1f671215 src = 0; 1f671215..M src+gradle = 0; ancestor OK; verdict blob c45b1593 = 35bd6695:path | CONFIRMED | - |

Pins (blob, LF of record unless noted; all = HEAD = M for the readers): g10_compare e5fa7e34, g11_reader b86832e3,
g13_comparator 61d83ec7, h9_stability 0814869f, v2_declared_cells c5b90278, rp12_pairing 35214b3f. Outcomes as committed:
g11_outcome 8559e937, g13_outcome ff8fa439, G14 outcome 92e57c8a (0 CR); g10_r2.txt fd6fe0ae (38 CR: the CRLF bytes are
what was committed, no LF rendering exists in git); g15_mmlu_pro_lb.txt da210905 (4 CR).

## Wording conditions (for the registrar's outcome section)

- **W-1 (G11, B-A1, MEDIUM).** Every P_fl / D_fd sentence carries "surface-sensitive, untested on capability text"; neither
  g11_outcome.txt nor g13_outcome.txt carries it (0 hits each). AND: P_fl 0.8119 is a union-mix figure carried by BBH (n 1,718,
  0.973) and MUSR (229, 1.000); per source (descriptive) MMLU_PRO_LB 0.745 (n 3,478), GPQA 0.673, MATH 0.621. Write "filing
  precision on the union EVAL mix"; never "the tree files above 75%" per corpus. Robustness (descriptive): under the engine's
  anchor-path column `domain_ok` instead of the reviewed modal `leaf_dominant` rule, P_fl 0.8042 [0.7941, 0.8146], D_fd +0.0946
  [+0.0836, +0.1057]: HELD either way.
- **W-2 (G13, MEDIUM).** FAILED is genuine, not an artefact of seeds (table). Words: "class-conditional spherical k-means at
  matched per-class prototypes (which reads the TRAIN labels) files EVAL better than the label-free tree's flatLeaf, D13 -2.15pp
  [-3.01, -1.25], beyond the comparator's seed spread 1.12pp". It is a filing-precision statement only; F-TAX L-2 is scored at
  F-TAX. B-A3's "UNDETERMINED likelier" did not happen; P4 is scored as registered (D13 and spread_KC inside their bands).
- **W-3 (G10, LOW).** Print "A4 per-node membership as SETS (multiplicity not compared): 0 of 439 nodes carry a duplicate
  queryId in B0, 0 of 439 in B0'; multiset comparison also equal, 7 of 7" (D-G-2 ruling). Words of record: "byte-identical on
  the declared set (A4 membership as sets) for 7 B0/B0' pairs at 12 threads from one commit"; never "deterministic". The
  graft_descent build (G11's descent arm) has no B0' pair: G10 does not cover it (as registered, 7 pairs).
- **W-4 (G15, MEDIUM).** The depth-1 anchors ARE the declared domains (labels = the declared classes; IFEVAL has ONE anchor, so
  its drift is 0 by construction). G15 therefore measures only cross-anchor re-filing (MMLU-Pro o1: 4 counts of 7,233), not
  structure; the 0.6pp bar is far from anything an anchored build can move. Write "anchor mass shares are order-stable (max
  0.0151pp over 6 members x 2 arms)"; within-anchor structure is the printed mu-match only (MMLU-Pro o1 73/74 at cos 0.95,
  70/74 at 0.99; o1 132 nodes / 73 leaves vs 135 / 74). P6: the drift value 0.0151pp lies BELOW its 80% band [0.10, 0.70] -> that
  clause FAILED (low); "G15 HELD 0.80" HELD; mu-match >= 95% at 0.95 on both arms HELD (73/74 = 98.6% the minimum).
- **W-5 (G14, LOW).** Decided on the reader's two-stage normal form [+1.43, +3.82] (the RP03 form the identity check
  reproduces); the registration's default percentile [+1.27, +3.64] agrees; name the form. M -0.05pp stays DESCRIPTIVE-ONLY.
- **W-6 (INC-C3, LOW).** "C-3 was discharged after, not before, the two B0 graft launches (the first C-3 run was FROM-CACHE);
  the parsed bytes are the stamped bytes; no artefact is affected." Also disclose the transient W1-W5 breach at 09:56:48 (two
  of the operator's own Gradle JVMs; zero at the 09:57:13 launch).
- **W-7 (EMD).** Words as registered (f): "byte-identical over 3 replicate AG_NEWS smoke builds" for the two files; P7 FAILED
  on its margin (1.89% > 1.0%), disclosed. R2's G10 (7 MMLU-scale pairs byte-identical on A3 incl. TotalDasguptaCost) is
  consistent with C1 but is R2's evidence, not EMD's; never "deterministic".

## Defects

- D-1 LOW: g13_comparator prints "Kish mean cluster size 1.3043"; 1.3043 is Sum m^2 / Sum m (the registered Kish mean is
  1.0908, which g11_reader prints correctly). Fix: relabel in the next delta of g13_comparator (FM.kish_mbar's name).
- D-2 LOW: g10_compare has no duplicate counter (membership_as_sets collapses duplicates silently); the D-G-2 count had to be
  computed here. Fix: print the count in --g10 (W-3 covers this outcome).
- D-3 LOW: g10_r2.txt and the g15 logs are committed with CRLF lines (38 / 4 CR); pin them as `blob:` of the committed bytes and
  say so; future logs written LF.
- D-4 LOW: the G11 HELD rests on the reviewed P1 rule (modal TRAIN-majority `leaf_dominant`), not the engine's `domain_ok`
  (anchor at depth 2); both HELD here, but the outcome should name the rule (W-1).
- D-5 MEDIUM: 130 of the 285 files hashed in run_emd_1/SHA256SUMS are NOT in the repo (xml_base.xml and xml_fix/*.xml are
  ignored by `.gitignore` `*.xml`; logs and DBs uncommitted); C2 / P8 evidence lives only in a temp scratchpad. Fix: copy
  run_emd_1 staged files to the E: backup and record the path (or `git add -f` the XML/logs by path; `.gitignore` is the author's).

## Own checks used as mutants (deciding paths)

- K1 my G10 comparator on B0 vs o1 (musr, mmlu_pro_lb): DIFFERS on A1-A5 (killed: the comparator is not vacuous). decisive.
- K2 G11 filing column swapped (modal leaf_dominant -> engine domain_ok): P_fl 0.8119 -> 0.8042, verdict HELD both (survived: the verdict is robust to the rule; not decisive). My multi-class set = the outcome's 14 EVAL keys (count 14, kept 6,139 / 5,628).
- K3 G13 verdict under a 20-seed spread (0.0147): still FAILED (|D13| 0.0215 > 0.0147). decisive for "genuine".

## Commands (scripts in the session scratchpad; all read-only)

```
cp .claude/worktrees/rp12-r2-run/snapshots.db $S/   # sha256 before/copy/after 9e5536e5..., -wal 0 B
python $S/g10_mine.py $S/snapshots.db               # A1-A5 own compare, raw/multiset/set A4, duplicate count
python $S/g10_mut.py  $S/snapshots.db               # K1 (B0 vs o1)
python $S/g11_mine.py                               # engine domain_ok rule (robustness)
python $S/g11b.py                                   # modal leaf_dominant rule + replay of draw seed 20260929
python $S/g13_mine.py 12                            # independent spherical k-means, 12 seeds
python - (g13_comparator.compute pieces on the R2 bundle; seeds 0-4 and 0-19)
python $S/g14_mine.py                               # TRAIN fit, policies vs frozen JSON, EVAL points, counts
python - (h9 drift from dag_snapshots last lines, B0p vs o1/o2/B0)
python - (EMD evidence: C1, C3 under D9b drops, P6/P7); sha256sum -c SHA256SUMS in $S/emd/run_emd_1 (285 OK)
git diff --name-only 2f080e0 1f671215 -- src | wc -l   # 4
git check-ignore -v .../xml_base.xml                   # .gitignore:17 *.xml
```
