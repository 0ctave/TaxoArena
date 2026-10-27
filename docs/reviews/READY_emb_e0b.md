# READY review: branch emb-e0b, tip f693b29 (EMBEDDER-CROSS-FLAT E0b reader, tools/analysis/embedder_cross_flat.py)

Adversarial reviewer, 2026-09-29. Zero calls, no real-data mode: no pool read, no DB of record opened, no Ollama contacted
(every probe on the script's own synthetic stubs, TAXOARENA_DATA_ROOT = an empty scratch dir; `ls -A` of it = 0 afterwards).
Full first review of one new file (+1010 lines, 1 file: `git diff --name-only f667d6b..f693b29 | wc -l` = 1). Branch base
380e965; main is now 2332d29 (f3d9c9f + one run commit touching only experiment_results/, 8 paths, no tools/ file).

## VERDICT

| object | verdict |
|---|---|
| f693b29 (embedder_cross_flat.py) | MERGEABLE (by path, one file; the only other diff vs main is main's own READY_emb_target2.md, which the branch never touched) |
| `--run --part cpu` | NOT READY until C-E0B-1 (D2 bracket) and C-E0B-3 (spread tests) are discharged AND the registrar fills the nomic_raw pin (carried: the 4th write, READY_emb_target2 E0b-3). Then READY-WITH-CONDITIONS (C-E0B-2, -4..-7). |
| `--run --part embed` | as part cpu, plus C-E0B-4 (Ollama preflight in the dry-run) and all 4 arm pins filled (gemma_card is an INCIDENT at 2332d29: W2 not complete). |

The code is correct on every deciding path I read and the builder's 25 mutants are real kills; what is not READY is the
instrument's definition (D2) and three test gaps on the deciding spread / M2-denominator legs.

## PINS (LF of record; `git rev-parse <c>:<f>` = `git hash-object`)

| file | blob | sha256-lf16 | sha256-crlf16 | note |
|---|---|---|---|---|
| tools/analysis/embedder_cross_flat.py | 3a7147c50fe23899080e0397a08f7cf40ab45874 | 62db36b4efaace71 | d6a6da920783f290 | = commit message; worktree = blob |
| tools/analysis/embedder_arms.py (IMPORT_PINS) | c8940349ea410eef0bb69c30ecea81a0e4208820 | 1c432baba8779fd3 | (READY_emb_target2) | = f3d9c9f = 2332d29 = main working file (CRLF, normalises to the pin) |
| tools/analysis/flat_mix_mmlu.py (IMPORT_PINS) | 555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2 | b80cec50c2eef49d | (READY_emb_target2) | = f3d9c9f = 2332d29 = main working file |
| experiment_configs/embedder_cross_arm_pins.json | b475ec2a74bc5c52813d2d4ad54833233fe70055 | | | main = worktree = f3d9c9f; all 4 sha256 null |

Hygiene: `git diff --name-only f667d6b..f693b29 | grep -cE "application.yml|\.env|\.gitignore|experiment_results/"` = 0.
Worktree `git status --porcelain | wc -l` = 0 before and after my runs.

## PER-CLAIM TABLE (deciding claims)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | IMPORT_PINS equal main f3d9c9f | c8940349 / 1c432bab and 555ae3ac / b80cec50 at f3d9c9f, at 2332d29 and on main's CRLF working files via the script's own `pins_of` | CONFIRMED | - |
| 2 | Registered constants | SE 0.00663 / 0.357e-3, MDE80 0.0186 / 1.00e-3, spread 0.0305, DEFF 1.0, k (14, 82), seeds 0-4, 256-d, fit/held-out/keyed 8,125 / 3,445 / 10,925, read set 11,687 (3,504 bracket), P1 / P2 / P5 / P6 values: all equal L21705-L21730 and L21837 | CONFIRMED | - |
| 3 | Support reproduces | 2.8 x 0.00663 = 0.018564 -> 0.0186; 2.8 x 0.357e-3 = 0.9996e-3 -> 1.00e-3; DEFF 1.0 sourced (FLAT-MIX-MMLU B7, measured; FLAT C1 CI width 0.0264 / 3.92 = 0.00673 ~ 0.00663); n_eff 3,445. The script re-measures DEFF (Kish m-bar) and n_eff at the run but prints the REGISTERED SE / MDE, not the realised SE of each deciding contrast (C-E0B-6) | CONFIRMED (registration); PARTLY (post-run print) | LOW |
| 4 | Criterion = registered WORSE (FLAT L1 form, strict, CI upper < 0; spread over qwen3's V seeds) | `worse` = `FM.loss` (`diff < -spr and hi < 0`); spread = `FM.spread` over `mq[("V",k,s)]`, s in 0-4; F1 = >= 2 of (nomic_raw, gemma_raw, mxbai NOT RUN = not WORSE) on M2 at ks[0] = 14; cards never counted. By inspection + builder mutants 1-9 KILLED | CONFIRMED | - |
| 5 | Selftest non-vacuous | 44 checks, rc 0 (12.6 s). Deciding paths executed end to end on stub arms through the real open_arm_reader, registrar pin, flat_mix connect guard, write-once; known answers (qwen3 stub M1 1.0 all seeds, spread 0; gemma = qwen3 -> diff exactly 0) | CONFIRMED | - |
| 6 | Builder mutants 25/25 KILLED | reproduced 25/25, `grep -c SURVIVED` = 0. Two are killed by a crash, not by the check they name: "coverage guard skipped" (KeyError -> printed root WinError 267 at temp cleanup) and "write-once off" (the mode-x backstop). Both fail closed on real data | CONFIRMED (2 by backstop) | LOW |
| 7 | Null pins refuse before any fit | own probe on the COMMITTED pin file (main, blob b475ec2a) with stub arms: part cpu and part embed, --run and --dry-run: all REFUSE "[EMB-ARMS] ... no sha256 for arm nomic_raw yet (ruling 19, PINS OWED)"; fit_space calls 0; outcome dir absent. BUT the refusal comes after the pool line and the full qwen3 DB-of-record read ("ARM qwen3_raw" printed first) | CONFIRMED (before any fit); not before any read (C-E0B-5) | LOW |
| 8 | Every non-qwen3 read through open_arm_reader; qwen3 in place with no flag | load_arm: qwen3 asserts open_arm_reader(...) is None; others only via it; builder bypass mutant KILLED by the flat_mix gate; own OM4 (all arms open nomic_raw) KILLED; globals / connect restored (st_refuse) | CONFIRMED | - |
| 9 | Fit on the 8,125 only; no held-out in any fit; TF-IDF fit-only | hygiene refuses on exact text or stem_key overlap (mutant KILLED); Xfit from W.fit; TF-IDF fit_transform(fit) (mutant KILLED) | CONFIRMED | - |
| 10 | D2 is admissible without a bracket | FLAT-MIX-MMLU's registered M1 (L20689) takes the cell majority from "the readout's train set, 'train 8324 distinct texts'"; E0b takes it from the 8,125 fit texts. A registered-definition change (see D-table) | REFUTED | HIGH (for --run) |
| 11 | Registered verdict line (f) printed | printed VERBATIM, but its premise ("the record's spread 0.0305") is the spread D2 says is never used; the per-line WORSE outputs carry no SCOREABLE / DESCRIPTIVE-ONLY tag | PARTLY | MEDIUM |
| 12 | Spread leg and M2 denominator are tested | own OM1 (spread over K seeds), OM2 (spread over V seeds 1-4), OM8 (M2 on keyed texts in the fit only) all SURVIVED the full selftest; m2_block's n is never asserted = 10,925 (every synthetic keyed text is a fit text) | REFUTED (test gap on deciding legs) | MEDIUM |

## BUILDER DECLARATIONS

| D | ruling |
|---|---|
| D1 seed-0 vs seed-0 | ADMISSIBLE specification of an under-determined term ("M(V_S) - M(V_qwen3)"); fixed in code pre-data, mean and K0 printed descriptive. Registrar records it. |
| D2 M1 majority from the 8,125 | A REGISTERED-DEFINITION CHANGE, not an admissible silent read. The registration scores "M1 purity" and imports FLAT's realised SE and spread; FLAT's M1 is defined on the 8,324 train texts. It is FORCED by the data-steward's read set (arithmetic from recorded counts, not a data read: 8,324 - 8,125 = 199 non-fit train texts; 11,687 - 11,570 = 117 keyed texts outside fit and held-out; 11,769 - 11,687 = 82 corpus texts outside the read set, 16 of them missing from gemma), so FLAT's M1 is infeasible for the card arms and gemma_raw without embedding more texts. Pre-data, so admissible AS A BRACKET: the registrar records M1' (majority from the 8,125) as the E0b statistic, or the author/registrar extends the read set by the 82. Not a C-7 promotion because D2 is declared; the outcome must name it (C-E0B-1). |
| D3 TF-IDF parameters | ADMISSIBLE (unregistered parameters of a registered floor arm); fit-only shown by mutant. Record. |
| D4 floor readout | ADMISSIBLE, DESCRIPTIVE. |
| D5 truncation proxy ceil(chars/4) | ADMISSIBLE only as a printed PROXY (the registration asks for a count of stems over the context); CONTEXT_TOKENS unsourced. LOW. |
| D6 digest from /api/tags at the run | Does NOT meet "tag digest pinned" in substance: provenance.json records no digest (`write_provenance` keys), so the printed digest is today's tag, not the one that produced the vectors; the sha256 file pin is the vectors' identity. Registrar brackets the reading, or the run-operator records the digest at each --go (C-E0B-7). LOW. |
| D7 prediction scoring | ADMISSIBLE (priors; inclusive intervals, own unit tests). |

## OWN MUTANTS (8, full selftest each; `e0b/own_mut.py`)

- OM1 spread over qwen3's K seeds instead of V -> SURVIVED. DECISIVE (the spread leg decides WORSE and F1).
- OM2 spread over V seeds 1-4 only -> SURVIVED. DECISIVE (same leg).
- OM3 M1 CI ignores twin groups (arange) -> SURVIVED. Not decisive if the held-out groups are singletons (registered DEFF 1.0; the run prints Kish m-bar).
- OM4 every non-qwen3 arm opens the nomic_raw copy -> KILLED (E0-EMBED).
- OM5 mxbai (NOT RUN) counted WORSE -> KILLED (E0-SCORE).
- OM6 criterion on the mean-over-seeds diff -> KILLED (E0-CONTRAST).
- OM7 arm_read_guard skipped for gemma arms only -> SURVIVED. Not decisive (one uniform call site; the KeyError backstop covers coverage, not the native-dim leg).
- OM8 M2 computed on keyed texts in the fit only -> SURVIVED. DECISIVE in kind (F1's metric, silent denominator change); not reachable by the committed code path.

## DEFECTS / CONDITIONS

- C-E0B-1 (HIGH, before --run): the registrar brackets D2 pre-data (M1' = majority from the 8,125; FLAT's 0.0305 and 0.00663 are
  carried as NOMINAL, the measured spread and CI decide), or the read set is extended by the 82 texts per arm. The outcome and
  CSV label the column "M1' (D2)", never bare "M1 purity". Optional bridge: qwen3's M1 under both sources printed side by side.
- C-E0B-2 (MEDIUM): print, per WORSE line, its support status against the MEASURED bar max(MDE, spread_qwen3) and re-derive the (f)
  labels from it beside the verbatim registered (f); the registered (f) premise 0.0305 is not this instrument's spread.
- C-E0B-3 (MEDIUM, before --run): kill OM1 / OM2 / OM8: in st_contrast make qwen3's seed 0 the unique extreme and K values
  differ from V; in `_synth` put held-out and non-fit texts in the keyed set; assert `m2["n"] == len(W.keyed[4])` (and print it).
  Re-pin the script after the change; delta READY (small).
- C-E0B-4 (MEDIUM, part embed): the dry-run REFUSES unless /api/tags lists qwen3-embedding:latest (today it prints UNAVAILABLE and
  passes); the floor posts after every fit and before write_once, so an Ollama fault (cf. W2's ephemeral-port incident,
  2332d29) loses the whole run. Consider running the floor BEFORE the fits.
- C-E0B-5 (LOW): check every arm pin of the part (registrar_pin on the expected DIR file) right after the pool line, before
  real_world and the qwen3 read, so a null pin costs no pool-reader window.
- C-E0B-6 (LOW): print the realised SE (twin-bootstrap SD of the paired diff; M2 boot SD) and MDE80 = 2.8 x SE beside each
  deciding diff, next to the registered values (check 8).
- C-E0B-7 (LOW): D6 digest reading bracketed, or digest recorded at each --go.
- CARRIED from READY_emb_target2 §E0b: item 3 (nomic_raw DIR copy, the 4th write) owed; item 4's C-ET2-3 test (PM1) NOT carried
  (flat_mix unchanged and pinned; exposure nil: E0b holds one token at a time and restores it, st_refuse asserts None) - LOW,
  stays open on flat_mix; items 1, 2, 5, 6 MET (claims 7-9, 3).
- NOTE: part embed re-fits nomic_raw; P1 is scored in part cpu and F1 in part embed on separate fits of the same data
  (deterministic single-threaded; a disagreement between the two nomic_raw lines would be a defect to report, not to pick from).

## COMMANDS (compact)

```
git diff --name-only f667d6b..f693b29 | wc -l                          # 1
git rev-parse f693b29:tools/analysis/embedder_cross_flat.py; git hash-object <wt file>      # 3a7147c5 both
git show f693b29:<f> | sha256sum | cut -c1-16 ; ... | sed 's/$/\r/' | sha256sum             # 62db36b4efaace71 / d6a6da920783f290
git rev-parse f3d9c9f:<f> f693b29:<f> HEAD:<f>   (embedder_arms, flat_mix, pin json)      # equal
python: pins_of-equivalent on main's and the worktree's working files                     # c8940349/1c432bab, 555ae3ac/b80cec50
cd .claude/worktrees/emb-e0b; export TAXOARENA_DATA_ROOT=<scratch>/nodata
python tools/analysis/embedder_cross_flat.py --selftest                 # SELFTEST PASSED: 44 checks, rc 0
python tools/analysis/embedder_cross_flat.py --mutants                  # 25 of 25 KILLED; grep -c SURVIVED = 0
python <scratch>/e0b/own_mut.py                                          # OM1-OM8 as listed
python <scratch>/e0b/nullpin.py   (stub arms, EA.ARM_PINS_FILE = main's committed pin json) # REFUSED x4, fit_space calls 0
sed -n 20689p docs/judge_v2_program.md                                   # FLAT M1: "train 8324 distinct texts"
grep -n 'def write_provenance' -A25 tools/analysis/embedder_arms.py      # no digest key
```
