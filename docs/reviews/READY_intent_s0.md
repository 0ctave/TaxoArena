# READY review: INTENT-TRANSFER-S0 build (branch intent-s0, tip 9b32cc4 on main 44ab46f)

Reviewer: adversarial-reviewer, 2026-09-30. Zero calls: no fetch, no embed, no Ollama post, no real run. Registration: prog
"## Registered 2026-09-29 (before any code or call) — INTENT-TRANSFER-S0: ..." L22092-L22134 (R-1..R-5); design
`docs/agents/plans/2026-09-29_intent_transfer_design.md` §2, §3, §5, §7.

## Verdict

- **MERGEABLE** (by path; three new files; main has moved 3 commits since 44ab46f, and those commits touch none of the 3 paths or
  the imported embedder_arms / split_side / data_v2/ro: count 0).
- **READY for fetch -> census now**, with C-5 (fetch as a dry run first).
- **Embedding (pilot included) READY only after the code changes C-2, C-3, C-6 land, or after the registrar declines them.** Any
  edit to `intent_transfer_s0.py` after the first `--embed --go` makes every `intent_emb_*.db` refuse: `intent_meta` pins the
  script's LF blob and `check_meta` compares it. So the code freezes before the pilot.
- **`--run` NOT READY until the registrar's pre-data bracket C-1 (the C1 interval) and C-4 (readings B2 / B3 / B7).**

## Pins (LF of record; the working tree is LF, 0 CR bytes in blob and in the worktree)

| path | blob (LF) | sha256-lf16 |
|---|---|---|
| tools/ingest/intent_ingest.py | 33f33f2159c9876c4b8cca1a8973a4656aa500cd | 4f20b299b13902ec |
| tools/analysis/intent_transfer_s0.py | 8386a99f84c96b493e3aa20954716cca9e6a55f7 | 192a49cff75789f0 |
| experiment_configs/intent_transfer_s0_pins.json | aa6fe805012279b6ba0babfa8a85e80014ae7721 | c95ab13cf393b91e |

## Per-claim table (deciding claims)

| # | claim | result | reviewer's number vs claimed | sev |
|---|---|---|---|---|
| 1 | CK-CLOSE-v1: side = side_of_hash(side_hash(stem_key)); exact norm-v1 duplicates share a side; a component with two gold labels is dropped | CONFIRMED | code L285-L304; unsalted key rule `norm-v1`/`ck-v1`; the manifest re-derives every side, key and drop and refuses a mismatch (II-TAMPER) | - |
| 2 | OOS forced to EVAL; an OOS component colliding with an in-scope row is dropped whole, so no OOS stem equals a TRAIN in-scope stem in CLINC | CONFIRMED | II-OOS / II-OOSCOLL; ingest mutants "OOS side not forced EVAL" and "only the OOS member dropped" KILLED | - |
| 3 | Fits are TRAIN-only (GATE for kappa and the C2 threshold); EVAL and OOS never fitted | CONFIRMED | every fit goes through fit_rows; the TF-IDF, C4 inventory and D2/D3/D6 centroids included; C4 variants whose stem equals any MASSIVE TRAIN stem are excluded | - |
| 4 | Embeds write only `intent_emb_<e>.db`; the shared caches are never written | CONFIRMED | check_emb_target refuses the names and paths of record; write_vectors gets `path` only; the shared caches' per-table hashes are taken before and after `--go` and a change REFUSES; the record caches are opened read-only for route parity only | - |
| 5 | Transport: keep-alive and bounded retry through embedder_arms; OLLAMA_HOST handled | PARTLY | EA.ollama_embed = one HTTP/1.1 connection plus 5 whole-batch retries (EA-CONN); the URL comes from EA.client_base(OLLAMA_HOST) (I-2) at import. The script never PRINTS the resolved URL (C-6) | LOW |
| 6 | C2 denominator = every CLINC OOS row, all hash sides (R-2) | CONFIRMED | `S_idx(EVAL, oos=True)` = every KEPT OOS row. oos_collision drops are excluded and counted, per design §5. Own mutant RV-1 (hash-side EVAL only) KILLED | - |
| 7 | R-1: nomic's fine line SCOREABLE iff measured SE <= 0.0071 and spread <= 0.020 | CONFIRMED | R1_SE = 0.020/2.8 = 0.00714; spread = max(qwen3, nomic), the bar's; boundary mutants KILLED | - |
| 8 | C1/C2/C3/C4 logic as registered (WORSE = D < -bar AND upper < 0; band() for C2/C4; C3 >= 2 of 3) | CONFIRMED | read line by line; builder's 58 mutants re-run: 58/58 KILLED; own RV-3 KILLED | - |
| 9 | D-c: "at the registered n the bias is about 20x smaller" | **REFUTED** | the bias scales with the number of contingency cells, ~K^2/n, not with n. Simulation with the script's own nmi/comp_weights at CLINC fine (K 150, n 6,750): bootstrap-mean minus D = +3.1 SE (diffuse errors; the point lies OUTSIDE its percentile CI), +0.3 SE (structured errors), -3.8 SE and +6.0 SE in mixed cases. MASSIVE/Banking fine: +1.7 SE diffuse, ~0 structured. Coarse K 10/18: <= 0.1 SE | HIGH |
| 10 | Support (d) C2: Hanley-McNeil SE 0.00573 x sqrt(1.05) = 0.0059 (registration; selftest asserts it) | PARTLY | the arithmetic reproduces (0.00573 / 0.00587) but the counts are SWAPPED: HM pairs (n_pos - 1) with Q1, and the positives are the 6,750 in-scope rows. HM in its own order gives 0.00352 (0.00361 with DEFF); a binormal simulation at A 0.90 (1,000 reps) gives SD 0.00438. The registered value is conservative; SCOREABLE holds in all three cases (MDE80 0.010-0.016 < 0.03) | LOW |
| 11 | Support (c)-(e) other arithmetic | CONFIRMED | n_eff 4,657 / 6,429 / 3,738; C2 1,286; C4 3,238; C4 SE 0.00527; SE_z 0.132 / 0.082 / 0.116; rho-MDE 0.35 / 0.23 / 0.31 | - |
| 12 | Tests | CONFIRMED | ingest selftest 21 PASSED, mutants 17/17; S0 selftest 114 PASSED, mutants 58/58. No file under src/ in the diff (count 0), so Gradle is not re-run. Root and worktree DB mtimes are unchanged across the runs | - |
| 13 | Tests pin the deciding intervals and seeds | **REFUTED (gaps)** | own mutants RV-2 (C1 bootstrap unpaired), RV-4 (C2 CI ignores the OOS resample), RV-5 (C3 decided at seed 4), RV-6 (C4 decided at seed 4): all 4 SURVIVED. The code is right by reading; nothing guards it | MEDIUM |

Own mutants (run against ST-STATS + ST-E2E + ST-VERDICT on the builder's fixture; control RV-0 identity SURVIVED as it should):
RV-1 C2 OOS = hash-EVAL only: KILLED, decisive. RV-2 C1 bootstrap unpaired: SURVIVED, decisive. RV-3 WORSE on lower < 0: KILLED,
decisive. RV-4 C2 CI with no OOS weights: SURVIVED, decisive. RV-5 C3 seed 4: SURVIVED, decisive. RV-6 C4 seed 4: SURVIVED,
decisive.

## D-c ruling (the C1 interval)

The percentile interval is not a valid 95% interval for D at K 150. The bias under resampling can be several SE, in EITHER
direction (it favours the partition with the more diffuse contingency, not the higher NMI). The point estimate D carries about the
same plug-in bias, and at K 150 that bias (0.005-0.010) is on the scale of the 0.0112 bar and of the predicted -0.020.

The point clause D < -max(2.8 SE, spread) protects against a manufactured WORSE while |b| is small against the bar. The interval
clause, however, can block a true WORSE (toward-zero bias; this spuriously fires F1) or become vacuous (away-from-zero bias).

The interval of record needs a pre-data bracket (C-1). A bias note alone is not enough on the fine lines. BCa is unnecessary: the
basic (reverse-percentile) interval [2D - q97.5, 2D - q2.5], with the bias-corrected point D - b printed beside, removes the
first-order shift at no cost.

## Defects and conditions (each with its fix)

- **C-1 HIGH (registrar, pre-data, before `--run`).** Bracket C1's interval. Either (a) decide on the basic interval, with D - b
  printed beside; or (b) keep the percentile and print b/SE on each line, so that a fine line with |b| > 0.5 SE prints
  BIAS-FLAGGED and is DESCRIPTIVE-ONLY. Recommended: (a). Correct D-c's "20x smaller" in the record.
- **C-2 MEDIUM (code, before the first `--embed --go`).** Implement C-1's choice. c1_level already holds `draws`, so this is a
  two-line change plus a printed b/SE, with a selftest that the basic interval contains D.
- **C-3 MEDIUM (code, before the first `--embed --go`).** Add assertions that kill RV-2, RV-4, RV-5 and RV-6:
  - recompute one C1 CI and the C2 CI independently at small B, with paired, stratified weights;
  - recompute the C3 cell table and the C4 same-cell vector at seed 0.
- **C-4 MEDIUM (registrar, pre-data).** Confirm or bracket three readings:
  - B2: the criterion text reads per family, but the FAIL OBSERVABLE "fewer than 2 corpora with a WORSE fine family" reads per
    corpus. The two differ when nomic is WORSE on one corpus and gemma on another. Pick one.
  - B3: seed 0 for C2 and C4 (the registration names a seed only for C3).
  - B7: every swappable slot is swapped (versus one slot). This moves C4's S.
  - B1, B4, B5, B6 and B8 are sound.
- **C-5 LOW (operator).** Run `intent_ingest.py --fetch --dry-run` first. It downloads, prints the shas and the census, and
  writes no DB. Plain `--fetch` also writes the write-once DB. Pin the raw files, then ingest, then run `--manifest`.
- **C-6 LOW (code).** Print `EA.OLLAMA_URL` (resolved from OLLAMA_HOST) in `--dry-run` and in every `--go` header. The operator
  sets OLLAMA_HOST explicitly.
- **C-7 LOW (code or registrar).** In `hanley_mcneil`, order the arguments as (A, n_pos, n_neg) and correct the selftest's 0.0059,
  or have the registrar bracket Support (d) as "counts swapped; conservative". Either way, the bootstrap decides.
- **C-8 LOW.** Other small points:
  - `--run` does not compare the ingest DB's provenance shas with pins["raw"]. The registrar should check this when pinning, or a
    one-line check should be added.
  - The docstring says "Kind: readout"; the outcome header says zero-call (R-5).
  - `annot_text_mismatch` is counted, not excluded. The pilot should show 0; otherwise exclude those rows.
  - The selftest reads `docs/agents/queue.json` relative to the cwd, so it must run from the repo root.

## What the first fetch must show (untested URLs; every parser fails closed)

1. Five HTTP 200 responses:
   - `amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz`
   - `raw.githubusercontent.com/clinc/oos-eval/master/data/{data_oos_plus.json,domains.json}`
   - `raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/{train,test}.csv`

   A 404 on `domains.json` is the likeliest failure; it stops with an unhandled HTTPError and no DB is written.
2. MASSIVE: exactly one member ending `/data/en-US.jsonl`; 16,521 rows (11,514 train / 2,033 dev / 2,974 test); 18 / 60 labels;
   ids unique.
3. CLINC: 15,000 / 3,000 / 4,500 in-scope and 250 / 100 / 1,000 OOS. The OOS split is UNVERIFIED on the card, so print it.
   `domains.json`: 10 domains covering exactly the 150 intents, with no intent in two domains.
4. Banking77: header `text,category`; 10,003 / 3,080 rows; 77 categories.
5. Census: EVAL within 5% of 4,890 / 6,750 / 1,350 (OOS, all kept) / 3,925; the drop counts by reason; labels below the minima;
   cross-corpus stem collisions. Otherwise a registrar bracket is needed before any read.

## Commands (all read-only or temp-dir; run from the worktree at 9b32cc4)

```
git rev-parse 9b32cc4:<path>; git show 9b32cc4:<path> | sha256sum | cut -c1-16; ... | tr -cd '\r' | wc -c   # pins, CR = 0
git diff --name-only 44ab46f..9b32cc4 | wc -l   -> 3 ; ... | grep -c '^src/' -> 0 ; ... | grep -Ec 'application.yml|\.env|\.gitignore' -> 0
git diff --name-only 44ab46f..main | grep -Ec 'intent_|embedder_arms|split_side|data_v2/ro' -> 0
python tools/ingest/intent_ingest.py --selftest  -> 21 PASSED ; --mutants -> 17 of 17 KILLED
python tools/analysis/intent_transfer_s0.py --selftest -> 114 PASSED ; --mutants -> 58 of 58 KILLED
scratchpad rv/own_mut.py (RV-0..RV-6 via the script's own exec-mutant pattern, fixture from build_fixture)
scratchpad rv/dc_sim.py (M.nmi + M.comp_weights; K/n = 150/6750, 60/4890, 77/3925, 10/6750, 18/4890; B 300-400)
Hanley-McNeil both orders + binormal SD (1,000 reps, n_pos 6,750, n_neg 1,350, A 0.90)
ls -l --time-style=full-iso on the root and worktree DBs before and after: unchanged
```
