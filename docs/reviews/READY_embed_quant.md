# READY_embed_quant — EMBED-QUANT writer + readout (branch embed-quant, tip 31b3c69c)

Reviewer: adversarial-reviewer, 2026-10-01. Zero judge calls, zero embeddings, no JVM. Registration: prog
"## Registered 2026-10-01 (before any code or call) — EMBED-QUANT: ..." L22738-L22760 (heading re-grepped at L22738 on main 96d6ca1e).

## Verdict

- **MERGEABLE by path** (3 added files, nothing else: `git diff main...embed-quant --name-status | wc -l` = 3, all `A`;
  `git merge-tree --write-tree main embed-quant` clean; merge-base 28b4032b = the registration commit; S0's
  `intent_transfer_s0.py` f662ceb1, `embedder_arms.py` 2073d131, `data_v2/ro.py` 1fdf7d75 identical on main and branch).
- **READY for the writer's `--embed --go`** (qwen3-embedding:8b-q8_0, 57,350 texts) and **then the readout `--run` after
  the registrar pins the Q8 file**, under conditions C-EQ-1..C-EQ-5.
- Pins (LF of record; working tree = LF for all three, `git hash-object` equal to `git rev-parse HEAD:<path>`, no CRLF rendering):
  `tools/analysis/embed_quant_writer.py` blob:1b2abdc8617f84f3cfd00c9778e3bbb94ae63d6f;
  `tools/analysis/embed_quant.py` blob:3930cf4bc5e77bebd38309c74cf4ecf8eeba74d0;
  `experiment_configs/embed_quant_pins.json` blob:e3b5bdd33e694886ab58d7903bbd3a9e18335dcd (`"q8": null`).

## Per-claim table (deciding claims)

| # | claim | finding | mine vs claimed | sev |
|---|---|---|---|---|
| QB1 | two new scripts importing S0 + EA unchanged instead of a tag flag on embedder_arms.py and a --quant arm on embed_dim_slice.py | CONFIRMED admissible. Substantive reason, not convenience: `ITS.expected_meta` pins `embedder_arms_blob_lf` and `script_blob_lf` into every S0 embedding DB's intent_meta and `check_meta` compares them, so editing embedder_arms.py would make the pinned Q4 file (and nomic/gemma) fail S0's own readers; embed_dim_slice.py blob 068550b4 is pinned by its run. The registered substance is kept: vectors go through `EA.ollama_embed` + `EA.write_vectors` (the "paced writer"); the readout uses S0's Space / km_fit / nmi / comp_weights / kish exactly as embed_dim_slice.py does (Space(d) = first d coords then L2; embed_dim_slice loads 4096 and slices, EQ loads the first 1024 of the same bytes: identical rows). Form deviation: needs the registrar's insertion bracket before `--run` (C-EQ-1). | — | LOW |
| QB2 | route parity Q8-vs-Q8 (T3 repeatability, T4 resume) at 0.998; cos(Q8, Q4) printed, no bar | CONFIRMED admissible. A 0.998 bar on cos(Q8, Q4) would make the preflight decide the experiment's own question (EQ2/P3) and could refuse the instrument for the outcome under test; parity is defined only within one model. T1 refuses an unlisted tag and a Q8 digest equal to Q4's. Bracket with QB1 (C-EQ-1). | — | LOW |
| EQ1 | TOST per corpus at d_q* 1024; delta_c = Q4 seeds 0-4 max-min; SE_total = sqrt(SE_boot^2 + var_seed/20); EQUIVALENT open 90% interval; DIFFERENT = abs(D) > delta AND 95% excludes 0; 2-of-3 verdicts | CONFIRMED by reading `eq1`/`status`/`verdict` L274-L318 against the registration line by line; registered statistic, no substitution (C-7). Builder's 58 mutants cover sign, delta source, seed term, ddof, Z, open/closed, both DIFFERENT legs, 2-of-3 thresholds, paired stream. My OM1 (unpaired bootstrap) and OM4 (SE_boot = 0) KILLED. | — | — |
| SUP | Support (a)-(g) arithmetic | CONFIRMED, own script: seed term 0.00194 / 0.00057 / 0.00142; SE_total 0.00348 / 0.00148 / 0.00285 (= claimed); TOST MDE80 0.00866 / 0.00369 / 0.00708 vs claimed 0.00865 / 0.00368 / 0.00709 (last-digit rounding of SE_total); DIFFERENT MDE 0.01721 / 0.00542 / 0.01283 (=); n_eff 4,900 / 6,672 / 3,902 (=); margin at 0.003: 0.01128 SCOREABLE, 0.00117 DESCRIPTIVE-ONLY, 0.00743 SCOREABLE (thin, 0.00035 over). DEFF source named (S0 measured Kish). NON-VACUOUS: NOT-A-CONFOUND reachable on MASSIVE + Banking77 alone; the readout re-prints Kish, n_eff, SE_total and MDE per corpus from the run. | to the digit / ±1e-5 | — |
| ID | Q4 identity 0.76554 / 0.92810 / 0.84900, spreads 0.01428 / 0.00417 / 0.01043 | Constants CONFIRMED to 5 dp against EMBED-DIM-SLICE's committed `nmi_matrix.csv` (qwen3, 1024, EVAL, fine, seeds 0-4); `outcome.txt` blob b183890b and `selection.json` LF sha256 f1b508cf... (d_q* 1024) reproduced. Reproduction on the REAL Q4 file: UNDETERMINED by me (the real `--dry-run` REFUSED at heavy_check on two java.exe = idle Gradle daemons 37812 / 48560; I did not bypass the guard). The gate is fail-closed in `--run` (refuses, nothing written) and exercised in selftest with a planted mismatch -> C-EQ-2. | constants = | — |
| WR | keep-alive / retry / pacing / refusal reused; writes only its own DB; refuses a non-empty WAL | CONFIRMED in code: POST via `EA.ollama_embed`, writes via `EA.write_vectors`, `--pace-s/--tw-drain` set EA's globals (restored in finally); target = `intent_emb_qwen3_q8.db` only, `check_emb_target` refuses cache names and a non-empty -wal/-journal; exclusive create `xb`; shared caches per-table hashed before/after; S0 pins re-hashed after. Executed: a 100-byte -wal beside the target REFUSES with 0 posts, both for an absent file and a 40-row partial file. Gap: three of these guards are not killed by the writer's selftest (D1). | — | MEDIUM |
| MUT | builder: selftest 184 + 44; mutants 58/58 + 21/21 | selftest re-run: rc 0, 228 `ok` lines (= 184 + 44). Writer mutants re-run: 21 of 21 KILLED. Readout mutants re-run: 58 of 58 KILLED (0 SURVIVED by `grep -c`). | 228 = 228; 21 = 21; 58 = 58 | — |

## Own mutants (deciding paths; scratch harness, same exec-and-selftest scheme as `run_mutants`)

- OM1 readout, unpaired bootstrap (Q4 arm gets reversed weights): KILLED (Q-E2E oracle SE_total) — decisive.
- OM2 readout, EVAL-row parity check between arms removed: SURVIVED — not decisive (`load_slice` already refuses a missing vector, so the rows cannot differ); LOW, no fix required.
- OM3 readout, CLINC OOS rows admitted into EVAL: KILLED (crash in Q-E2E) — decisive.
- OM4 readout, SE_boot = 0: KILLED (Q-E2E) — decisive.
- OM5 writer, `ITS.check_emb_target(path)` removed from `embed()`: SURVIVED; executed under the mutant, an absent target with a non-empty -wal is NOT refused (108 posts; sqlite's own open discards the bogus -wal before `EA._check_target` looks), the partial-file case still refuses via `RO.open_ro`. Decisive for the WAL claim -> D1.
- OM6 writer, shared-cache before/after compare disabled: SURVIVED -> D1.
- OM7 writer, S0 `after_check` removed from `embed()`: SURVIVED -> D1.

## Defects

- **D1 MEDIUM (writer selftest coverage).** OM5/OM6/OM7 survive: the non-empty-WAL refusal on a new target, the shared-cache
  hash compare and the S0 after-check exist and run, but no writer check plants the condition. Fix: add three W-REFUSE checks
  (a 1-byte `intent_emb_qwen3_q8.db-wal` with no file -> refused, 0 posts; a planted change to a fixture shared cache inside a
  stub `embed_fn` -> refused; a byte appended to the fixture Q4 file inside `embed_fn` -> refused) and the three mutants.
  Not blocking this run: the code paths are correct (WAL refusal executed above), the run writes no shared object.
- **D2 LOW (EVAL reads).** The readout `--dry-run` reads Q4 EVAL (seeds 0-4) once more than "EVAL read once per arm"; it reproduces
  values already of record and reads no Q8 EVAL (builder mutant "dry-run reads Q8 EVAL" killed). The registrar's bracket should
  say so with QB1/QB2.
- **D3 LOW (T4 floor).** T4 resume parity runs only when >= 20 rows are stored; a `--limit` pilot below 20 rows resumes unchecked.
  Operator: use `--limit` >= 20 (or none).

## Conditions

- **C-EQ-1** the registrar brackets QB1-QB6 (and D2) by insertion before `--run`; mergeable and the writer's `--go` do not wait for it.
- **C-EQ-2** order: readout `--dry-run` FIRST (Q8 file absent is handled) and it must print `IDENTITY ... ` with all six values equal
  before the writer's `--go`, so a non-reproducing Q4 stops before the Ollama pass; `--run` re-checks it fail-closed.
- **C-EQ-3** window: no java.exe (both scripts refuse on ANY java.exe, including the two idle Gradle daemons now running: the owner
  stops them, nobody kills by image name), Ollama serving only this pass (serial with INTENT-S0-CARD-PROTOCOL; not beside RP13), the
  writer `--dry-run` (T1-T4 + 500-text price) passes before `--go`; disk line printed (Q8 DB about 0.94 GB on Z:; the pull on C:).
- **C-EQ-4** after `COMPLETE`, the registrar fills `"q8"` in `embed_quant_pins.json` from the writer's last sha256 line by insertion;
  `--run` refuses a null or different pin.
- **C-EQ-5** post-run: the reviewer re-measures DEFF from the EVAL components, recomputes D_q / SE_total / the three statuses from
  `nmi_q.csv` and the bootstrap, and prints n_eff and the MDE beside each status.

## Sidecars (READY_e1_route2 C-E1R-1)

The repo root now carries 14 sidecar files (7 `-wal` all 0 B, 7 `-shm` 32 KB; `ls -la *.db-wal *.db-shm`), not 6. Three pairs sit beside
this run's read-only shared caches (`embeddings_cache.db`, `..._nomic-embed-text_latest.db`, `..._embeddinggemma_latest.db`); the
writer opens them through `RO.open_ro`, which refuses only a NON-EMPTY -wal/-journal, so a 0-B -wal is admitted and the immutable read
is exact. `intent_emb_qwen3.db` and `intent_transfer_corpora_v1.db` have no sidecars. They do **not** matter for this run as long as
every -wal stays 0 B; if one grows, the writer refuses (fail-closed). Moving them stays C-E1R-1's business, not a precondition here.

## Commands

```
git diff main...embed-quant --name-status | wc -l        # 3 (all A); git merge-tree --write-tree main embed-quant -> clean
git hash-object <3 paths> vs git rev-parse HEAD:<path>    # equal (LF; no CRLF rendering)
python tools/analysis/embed_quant.py --selftest           # rc 0; grep -c '^  ok' = 228 (184 + 44)
python tools/analysis/embed_quant_writer.py --mutants     # 21 of 21 KILLED
python tools/analysis/embed_quant.py --mutants            # 58 of 58 KILLED; grep -c SURVIVED = 0
python scratch/eqrev/own_mut.py, own_mut2.py              # OM1-OM7 + WAL execution (results above)
TAXOARENA_DATA_ROOT=<main> python tools/analysis/embed_quant.py --dry-run   # REFUSED at heavy_check (2 java.exe); nothing read
python -c "<nmi_matrix.csv qwen3 1024 EVAL fine seeds 0-4 mean / max-min>"  # 0.76554 0.01428 / 0.92810 0.00417 / 0.84900 0.01043
python -c "<sha256 of selection.json LF>"                 # f1b508cf...; d_q* 1024
python - <<Support (d)-(f)>>                              # table SUP above
sha256sum intent_emb_qwen3.db                             # 9e100e04fc91b137... = S0 pin
```
