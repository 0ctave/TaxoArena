# READY review — INTENT-S0-CARD-PROTOCOL (branch card-proto, tip b3b1a9ad)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls; no embedding posted; one readout `--dry-run` on the pinned S0 DBs
(read-only; one `/api/tags` GET for the digests). Against: `## Registered 2026-10-01 (before any code or call) — INTENT-S0-CARD-PROTOCOL: ...`,
prog L22655-L22680 _as_of 46954215 (no bracket inside the span at HEAD 2b6591bb: `grep -n CARD-PROTOCOL` after L22680 hits only
EMBED-QUANT's text).

Reviewed blobs (`git hash-object`, LF; worktree files hold 0 CR bytes, so LF = working tree; = HEAD tree entries):
| file | blob (LF, of record) | sha256-lf16 |
|---|---|---|
| tools/analysis/card_protocol_writer.py | blob:2788d7214df86dd8aabdb67d9b1b373ba3ec49fe | 55d93334997fc685 |
| tools/analysis/card_protocol.py | blob:cdcc1dbb4ece15b150988f43913e757432e90e77 | a41f1c2c2693c320 |
| experiment_configs/card_protocol_prompts.json | blob:5b54f82e52b8f8586f9a2a805bdf0d48903ddde2 | 19c3d1f888ba3a99 (= writer's PROMPTS_FILE_SHA) |
| experiment_configs/card_protocol_pins.json | blob:732097b4e8c4429bb7b3e77db66dd07742792592 | b292be4514a98d25 (all three pins null) |
Imported unchanged: intent_transfer_s0.py blob:f662ceb1 (asserted), embedder_arms.py 2073d131, data_v2/ro.py, split_side.py
(`git diff 3de208c7 main --` on the four: empty). Outcome path of record: `experiment_results/card_protocol/outcome.txt` (write-once `x`).

## Verdict

**MERGEABLE** (4 files, all added: `git diff --name-only main...card-proto | wc -l` = 4; `git merge-tree --write-tree main card-proto`
clean; no application.yml/.env/.gitignore).
**READY for the writer passes** (qwen3 card, gemma card, serial; nomic NOT run, orchestrator's ruling), from main after the merge,
under C-CP-1, C-CP-2. **READY for the readout `--run`** after both CARD files are COMPLETE and pinned, under C-CP-3..C-CP-5.

## Deciding claims

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Prompt strings = registration, byte for byte | CONFIRMED | JSON values == registered literals (python equality); qwen3 90 B, 1 LF, ends `\nQuery:` (no space), sha256 e92a9484; gemma `task: clustering \| query: ` 11ab9b67; nomic `clustering: ` 1885ff31. Against the published cards: Qwen3-Embedding-8B README L127 `f'Instruct: {task_description}\nQuery:{query}'`; ai.google.dev EmbeddingGemma model card `task: clustering \| query: {content}` (HF README gated 401); nomic-embed-text-v1.5 README `'clustering: the quick brown fox'`. Double entry (file pin + constants) and the qwen3 card-form check refuse a drift (W-T0, W-CONST) | — |
| 2 | Writer follows the EMBED-QUANT pattern; WAL and hash tests | CONFIRMED | Same skeleton as embed_quant_writer.py (load_inputs/after_check/preflight T1-T4/timed_probe/_state/dry_run/embed, `xb` create, EA.write_vectors with a CARD Arm, layer_norm False). READY_embed_quant D1 (OM5-OM7) and D3 closed: W-WAL (1-byte -wal / -journal beside an ABSENT target refused, 0 posts, both --go and --dry-run; 100-byte -wal beside a partial file refused; 0-byte admitted), W-HASH (shared-cache change and a byte appended to S0's RAW / ingest DB during the pass refused), T4 on a 1-19-row file (my OM7 KILLED) | — |
| 3 | CP1 computed as registered | CONFIRMED | `cp1`: D = gemma CARD@768 - qwen3 CARD@1024 seed means; bar = max(2.8 SE, max(CARD spreads)); S0 `c1_status` (BETTER iff D > bar AND lo > 0); BASIC CI, B 2,000 (ITS.BOOT_B), component weights shared by all arms (paired); `verdict` nb>=2 REOPEN / nw>=2 KEEP-STRONG / else KEEP (total). My OM1, OM8 KILLED | — |
| 4 | CP2 computed as registered | CONFIRMED | `cp2`: D-bar = mean over corpora of qwen3 (CARD - RAW); joint draw = per-index mean of three independent per-corpus streams ("resampled independently per corpus"); bar_pool = max(2.8 SE(D-bar), mean_c max(spread CARD, spread RAW)); HELD / HURTS / NOT SHOWN with BASIC bounds. My OM5 KILLED | — |
| 5 | IDENTITY reproduces EMBED-DIM-SLICE at qwen3@1024 / gemma@768 | CONFIRMED (real dry-run) | Dry-run printed means 0.76554/0.92810/0.84900 and 0.79883/0.92566/0.89286, spreads 0.01428/0.00417/0.01043 and 0.01277/0.00968/0.01216, D* +0.03329/-0.00244/+0.04386, BASIC [+0.02961,+0.03998]/[-0.00560,-0.00048]/[+0.04108,+0.04990]: all equal to the targets. My own recomputation of means/spreads/D* from nmi_matrix.csv (blob 1056bad9) agrees to the 5th digit; the CIs equal outcome.txt (blob b183890b) L22-L24. So CP1's stream is DS1's | — |
| 6 | Data object and Support | CONFIRMED | Dry-run census: EVAL 4,946 in 4,923 / 6,672 in 6,672 / 3,908 in 3,905; Kish 1.0093 / 1.0000 / 1.0015 (source: S0 measured; re-measured here); n_eff 4,900 / 6,672 / 3,902. SE(D-bar) = sqrt(1.633e-5)/3 = 0.001347; MDE80 0.0081/0.0038/0.0069, CP2 0.0038; planning bar_pool 0.01613; (f) lines reproduce (Banking77 0.0207 > 0.0069; CLINC 0.0156 > 0.0038; MASSIVE -0.0146 inside; CP2 0.0039 > 0.0038, thin). Non-vacuous; in-run bars decide | — |
| 7 | TRAIN-only; no write to inputs | CONFIRMED | Dry-run: 31 fits audited, 31 TRAIN, 0 GATE, 0 EVAL, 0 OOS. sha256 of ingest / qwen3 / gemma RAW DBs and mtime+size of embeddings_cache.db(-wal/-shm) and every intent_*.db identical before/after (`diff pre.sha post.sha`); no CARD file created | — |
| 8 | CW3: tag digest = S0's RAW file digest | CONFIRMED (real) | /api/tags: qwen3-embedding:latest 64b93349…, embeddinggemma:latest 85462619…, nomic-embed-text:latest 0a109f42… = `model_digest` in intent_meta of intent_emb_{qwen3,gemma,nomic}.db (immutable read). T1 will pass today; a re-pull refuses | — |
| 9 | Selftest 292; mutants 37/37 + 71/71 | CONFIRMED | My runs: readout 204 + writer 88 = 292 ok, rc 0; writer `--mutants` 37 of 37 KILLED(assert); readout `--mutants` 71 of 71 KILLED(assert), rc 0 | — |
| 10 | Own mutants (8) | 7 KILLED, 1 SURVIVED (non-decisive) | OM4 survives: no test plants a RAW file without a stored digest (D2) | LOW |

## Builder's readings

| id | Reading | Ruling |
|---|---|---|
| CB1 | two new scripts, S0 + EA imported unchanged (not "a card writer on embedder_arms.py") | ADMISSIBLE (READY_embed_quant QB1 reason: EA/S0 blobs are pinned in S0's DBs' intent_meta). Registrar brackets the form (C-CP-3) |
| CB2 / CW2 | route parity (S0's bars) on the RAW route; T3/T4 on the CARD route; cos(CARD, RAW) printed, no bar | ADMISSIBLE (QB2's reason: a bar on cos(CARD, RAW) would decide the treatment) |
| CW1 | no transform on any card arm | ADMISSIBLE for qwen3/gemma (their cards prepend a prompt only). For nomic the v1.5 card layer-norms before a Matryoshka slice; moot this pass (nomic not run); bracket if nomic is ever run |
| CW3 | T1 digest = S0's RAW file digest | ADMISSIBLE, stricter than registered; verified on real tags (claim 8) |
| CB3 | DS1's stream, paired; CP2 joint per-draw mean | CONFIRMED (claims 4, 5) |
| CB4 | SE = SD ddof 1; MDE80 2.8 SE; BASIC decides, percentile beside | CONFIRMED (Support (e)) |
| CB5 | CP3 percentile CI on DS3's stream, BASIC beside | ADMISSIBLE (descriptive; DS3 EB4 precedent) |
| CB6 | CP4 nomic @256 | MOOT this pass (NOT READ) |
| CB7 | dry-run reads RAW EVAL only | CONFIRMED (EVAL values already of record; CARD files absent) |
| CB8 | closed 80% intervals; KEEP-STRONG inside the KEEP event | ADMISSIBLE ("KEEP 0.75 (KEEP-STRONG 0.10)"; 0.75 + 0.25 = 1) |
| CB9 | no shifted-points bracket; points scored as registered | NOT ADMISSIBLE as a reading: the registration orders the bracket (D1, C-CP-1) |

## Defects

- **D1 MEDIUM (registered pre-data bracket missing; CB9).** The registration: "if [EMBED-DIM-SLICE's] outcome moves P3 by more than
  0.01 on any corpus, the registrar brackets the shifted CP1 points pre-data". DS1 moved MASSIVE +0.02200 -> +0.03329 (+0.01129 > 0.01);
  CLINC +0.00956 and Banking77 -0.00114 do not trigger. Fix: the registrar inserts the bracket BEFORE the first writer `--go`. The
  registered prior (CP1 = P3 - 0.012, which gives +0.010 / -0.024 / +0.033 from P3) suggests MASSIVE +0.021 [+0.001, +0.041]; the numbers
  are the registrar's. The criterion and the (f) word are unchanged (+0.021 is inside the planning bar 0.0246 and 0.0070 beyond DS1's
  in-run bar 0.01428 < MDE80 0.0076: DESCRIPTIVE-ONLY either way). The outcome prints the registered point; the post-run record scores
  CP1-P MASSIVE against the bracket (no code change needed).
- **D2 LOW (test gap, writer T1).** OM4 (`if dr and dg != dr`) survives: no fixture lacks a stored RAW digest. Not decisive: all
  three real RAW files carry a digest (claim 8), so the code as written refuses correctly. Fix (optional): one W-REFUSE case with
  `model_digest` deleted from the fixture's RAW meta.
- **D3 LOW (stale registered sentence).** READING AGAINST D3, REOPEN-on-both branch, prints "complete except E1 and quantisation
  (EMBED-QUANT, an option)" verbatim; EMBED-QUANT has run (NOT-A-CONFOUND; tag narrowed to "quantisation: Q4_K_M ~ Q8_0 (EMBED-QUANT);
  above Q8_0 untested", W-EQ-1). Fix: registrar bracket pre-data on the registration's line; the outcome keeps the registered words and
  the post-run record carries the bracket.
- **D4 LOW (nomic).** CP4's nomic rows are registered but not run (orchestrator's ruling). Code prints "CP4 nomic: NOT READ --
  ... not pinned" (`load_inputs` reads nomic only when `pins["nomic_card"]` is set at --run; builder mutant killed). Fix: the
  registrar records the ruling so the NOT READ line has its cause of record; nomic_card stays null in the pins file.
- **D5 LOW (order).** At `--run` the IDENTITY is checked after the CARD EVAL reads (it refuses before any write). Acceptable because the
  dry-run proves it first on the same pinned RAW files; C-CP-4 binds the dry-run before `--run`.

## Conditions

- **C-CP-1** (before the first writer `--go`): D1 bracket inserted by the registrar (pre-data).
- **C-CP-2** (writer passes): from main after the merge (writer_blob_lf in the CARD meta = blob:2788d721; the readout refuses another);
  `--dry-run --embedder <e>` first (T0-T4 and the 500-text probe; READY requires T1-T4 PASS printed); one Ollama pass at a time, no
  construction, no other Ollama pass (any S1 build serial); qwen3 and gemma one at a time, either order; nomic NOT run.
- **C-CP-3** (before `--run`): registrar pins both COMPLETE files (sha256-bytes from the final `[EMB-ARMS] wrote ... sha256 after` line)
  in card_protocol_pins.json by insertion, and brackets CB1/CB2/CW1-CW3, D3 and D4.
- **C-CP-4** (before `--run`): readout `--dry-run` on main prints IDENTITY REPRODUCED and both CARD files 57,350 of 57,350.
- **C-CP-5**: `--run` from blob:cdcc1dbb only; post-run review recomputes CP1 per corpus and CP2 from nmi_card.csv + the BASIC CIs.

## Commands (all read-only; S = scratchpad)

```
git -C <wt> hash-object <4 files>; git show HEAD:<f> | sha256sum; tr -cd '\r' < <f> | wc -c      # pins table; 0 CR
python: json.load(prompts)[e] == registered literal (True x3); sha256 e92a9484 / 11ab9b67 / 1885ff31
curl huggingface.co/{Qwen/Qwen3-Embedding-8B,nomic-ai/nomic-embed-text-v1.5}/raw/main/README.md; ai.google.dev/.../embeddinggemma/model_card
python tools/analysis/card_protocol.py --selftest            # 204 + 88 ok, rc 0 (1m54s)
python tools/analysis/card_protocol_writer.py --mutants      # 37 of 37 KILLED(assert)
python tools/analysis/card_protocol.py --mutants             # 71 of 71 KILLED(assert), rc 0
python S/om/own_mut.py w|r                                   # OM1-OM8 (in-memory exec, builder's selftest sections)
  OM1 CP1 gemma CARD - qwen3 RAW           KILLED  decisive
  OM2 boot stream 11 x corpus index        KILLED  decisive (identity CI refuses)
  OM3 identity mean/spread qwen3 only      KILLED  decisive
  OM4 writer T1 admits a missing RAW digest SURVIVED not decisive (D2)
  OM5 CP2 HELD on the percentile bound     KILLED  decisive
  OM6 --run identity without the CI        KILLED  decisive
  OM7 writer T4 checks 1 stored row        KILLED  not decisive
  OM8 CP1 bar ignores gemma's spread       KILLED  decisive
sha256sum intent_transfer_corpora_v1.db intent_emb_{qwen3,gemma}.db; stat embeddings_cache.db* intent_*.db*  > pre.sha / post.sha; diff: IDENTICAL
TAXOARENA_DATA_ROOT=<main> python tools/analysis/card_protocol.py --dry-run   # rc 0; IDENTITY equal to target; census; 31 TRAIN fits; nothing written
python: nmi_matrix.csv EVAL fine seeds 0-4 -> means/spreads/D* (claim 5)
curl 127.0.0.1:11434/api/tags; sqlite3 file:intent_emb_<e>.db?mode=ro&immutable=1 intent_meta model_digest   # claim 8
git diff --name-only main...card-proto | wc -l  -> 4;  git merge-tree --write-tree main card-proto -> clean
```
