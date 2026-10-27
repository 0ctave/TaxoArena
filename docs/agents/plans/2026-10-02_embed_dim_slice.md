# EMBED-DIM-SLICE: registration draft (research-lead, 2026-10-01 for 2026-10-02). Zero calls; design only

This is a plan file. It is not a record file, and nothing here is registered until the registrar commits it.
The author's priority, relayed by the coordinator, is "run the dimension test first". This draft is standalone; the
other three drafts go in `docs/agents/plans/2026-10-02_next_registrations.md`. CARD-PROTOCOL (draft 3 there) reads
its slices from this test's GATE selection.

Verified by the research-lead at HEAD 47c72bb5 (zero calls; the commands are named):
- `intent_emb_qwen3.db` stores 4096-d vectors: 16,384 bytes per vector, 57,350 rows, meta `native_dim 4096`, protocol RAW,
  model digest 64b93349. `intent_emb_gemma.db` stores 768-d vectors: 3,072 bytes per vector. Both were opened `mode=ro&immutable=1`.
- `ollama show`: qwen3-embedding:latest is 7.6B, Q4_K_M, embedding length 4096. embeddinggemma:latest is 307.58M,
  BF16, embedding length 768. `ollama list` shows no non-Q4 qwen3-embedding tag locally.
- S0's fine numbers come from `experiment_results/intent_transfer_s0/s0_run.log` L32-L63; SLOTSWAP M3 comes from its results JSON.
- Ledger and programme grep for EMBED-DIM: 0 hits.

## Registration text (for the registrar)

**Heading.** `## Registered <date> (before any code or call) — EMBED-DIM-SLICE: on S0's pinned intent corpora and embeddings, is S0's "gemma beats qwen3 at the fine level" (C1a, 2 of 3 corpora; SLOTSWAP M3) an artefact of the 256-d slice, which keeps 6% of qwen3's 4096 dims and 33% of gemma's 768? (zero calls; zero new embeddings; no build)`

**Question and kind.**
- Kind: zero-call CPU reader.
- Every cross-embedder comparison in S0, SLOTSWAP and E0b used slice 256 renormalised.
- The D1 sweep found 512 best for qwen3, measured on tree certification on MMLU-Pro.
- The test asks whether gemma's fine edge survives when each embedder is read at its own best slice, chosen on GATE.
- Two confounds are NOT controlled here and are disclosed in every outcome line:
  - quantisation: qwen3 Q4_K_M against gemma BF16;
  - prompt protocol: RAW on both sides.
- CARD-PROTOCOL tests the protocol. No test of quantisation is registered (see Out of scope).

**Prior results touched (none revised).**
- INTENT-TRANSFER-S0: C1a's gemma rows. Fine D(gemma) at 256 is MASSIVE +0.03340 BETTER, CLINC -0.00691 NEITHER, Banking77 +0.05628 BETTER.
- D2 H (qwen3 / gemma): MASSIVE 0.40 / 0.88; CLINC 0.14 / 0.29.
- INTENT-S0-SLOTSWAP-MECH M3: S is 0.7598 for qwen3 and 0.8262 for gemma, a difference of +0.0664 [+0.0515, +0.0820] at seed 0. The seed spread is 0.0335.
- EMBEDDER-CROSS-FLAT E0b: "gemma better" is forbidden there.
- D1 sweep: 512 wins for qwen3 trees.
- The author's D3 of 2026-10-01: keep qwen3; gemma is a registered secondary arm.
- Closed lines (CONTEXT §5): none touched. There is no judge, rubric, sub-anchor row, frontier, order, temperature or GMM LR.

**Hygiene.**
- Inputs are read only, opened `mode=ro&immutable=1`. The sha256 of each file is checked before the run and again after it:
  - `intent_transfer_corpora_v1.db` 487e0093...;
  - `intent_emb_qwen3.db` 9e100e04...;
  - `intent_emb_gemma.db` b187b82f... (the S0 pins).
- No new embedding and no Ollama process. No pool of record and no `embeddings_cache.db` is read.
- Slicing takes the first d coordinates and then L2-renormalises (S0's rule). Both models are MRL-trained according to their cards.
- Split and roles are S0's CK-CLOSE-v1 hash sides:
  - k-means is fitted on TRAIN;
  - the slice is SELECTED on GATE;
  - EVAL is read once, after the selection file is written and its sha256 printed (the R3 pattern).
- Slot variants are S0's EVAL-side variants, already embedded.
- The CPU lane is single-threaded (BLAS 1), one heavy process at a time, and it pauses during a construction.

**Instrument.**
- `tools/analysis/embed_dim_slice.py`, TO BE BUILT. It imports S0's functions verbatim (`intent_transfer_s0.py` blob:f662ceb1): spherical k-means (k-means++, n_init 1, max_iter 300, seeds 0-4, TRAIN fit, nearest-centroid filing), NMI (arithmetic), the BASIC component bootstrap (B 2,000, partitions fixed), D2's H, and SLOTSWAP's S.
- Arms: qwen3 at d in {256, 512, 1024, 4096}; gemma at d in {256, 768}.
- The outcome is write-once at `experiment_results/embed_dim_slice/outcome.txt`, with CSVs beside it.
- IDENTITY PRECONDITION (refuses on failure; no readout is written):
  - qwen3@256 and gemma@256 reproduce S0's fine D to the printed 5 dp: +0.03340 / -0.00691 / +0.05628;
  - S at seed 0 reproduces 0.7598 / 0.8262.

**Selection rule (GATE; fixed now).**
- For each embedder, d* = the slice maximising mean-over-seeds fine NMI on GATE (GATE items filed to TRAIN centroids), averaged over the 3 corpora. This gives ONE slice per embedder.
- Ties within 0.001 go to the smaller d.
- The selection is written and hashed before EVAL is opened. Per-corpus GATE maxima are printed but never used.

**Readouts and criteria.**
- **DS1 (deciding; the D3 readout; POINT and INTERVAL, one conjunctive clause each way, S0's C1 rule verbatim).** Per corpus:
  - D* = mean_s NMI_EVAL(gemma, d_g*) - mean_s NMI_EVAL(qwen3, d_q*), at K_f (60 / 150 / 77).
  - BETTER iff D* > bar (point) AND the BASIC CI lies above 0. WORSE symmetrically. NEITHER otherwise.
  - bar = max(MDE80, max(spread_qwen3(d_q*), spread_gemma(d_g*))). The spreads are measured IN-RUN, as max - min over seeds 0-4 of that arm's EVAL NMI. The transported values below are planning only.
  - VERDICT:
    - **REOPEN-CANDIDATE** iff gemma is BETTER on >= 2 of 3 corpora;
    - **KEEP** iff gemma is BETTER on <= 1;
    - **KEEP-STRONG** iff qwen3 is BETTER, i.e. gemma WORSE, on >= 2 of 3 (a sub-case of KEEP).
  - There is no UNDETERMINED: the 2-of-3 classification is total.
- **DS2 (DESCRIPTIVE-ONLY; Support (f)):** qwen3's slice curve, NMI(qwen3, d) - NMI(qwen3, 256), for d in {512, 1024, 4096}, per corpus, with CIs; also gemma 768 - 256.
- **DS3 (DESCRIPTIVE-ONLY; Support (f)):** S(gemma, d_g*) - S(qwen3, d_q*) on MASSIVE at K 60, as a mean over seeds 0-4, with a component-bootstrap CI; the full 6-arm S table beside it.
- **DS4 (DESCRIPTIVE-ONLY):** H per arm on MASSIVE and CLINC (Banking77 has no coarse level), each with its item-bootstrap interval and its size-matched random p95.
- Printed, never deciding: the full 6-arm x 3-corpus fine-NMI matrix; coarse NMI per arm; GATE NMI per arm.

**Reading table (fixed now; the author owns D3).**
- **KEEP:**
  - Words: "at each embedder's GATE-selected slice, gemma's fine-level edge over qwen3 is not shown on >= 2 of 3 intent corpora (RAW protocol; qwen3 Q4_K_M vs gemma BF16)".
  - This supports D3 as decided (qwen3 of record, gemma secondary).
  - It does NOT say that the slice explains the S0 edge when MASSIVE reads NEITHER inside its bar (Support (f)).
- **KEEP-STRONG:** in addition, "qwen3 is better at the fine level at its selected slice on >= 2 of 3".
- **REOPEN-CANDIDATE:**
  - Words: "gemma's fine edge survives the slice confound on >= 2 of 3 corpora".
  - D3's revisit conditions stay the author's (checkpoint B: CARD-PROTOCOL CP1 HELD AND F-E1 not fired). This test alone never changes the embedder of record, and quantisation stays uncontrolled.
- In every branch, d_q* is reported against the tree slice of record (512). If d_q* != 512, that fact is RELAYED to the tree specialist and changes nothing of record (the D1 sweep measured certification, not NMI).

**Support.**
- (a) Deciding denominators:
  - EVAL fine: MASSIVE 4,946 items in 4,923 components; CLINC in-scope 6,672 in 6,672; Banking77 3,908 in 3,905 (S0 census, s0_run.log L23-L26).
  - GATE for the selection: counts printed by the dry-run.
  - DS3: 3,222 variants in 3,207 components.
- (b) DEFF and source: Kish 1.0093 / 1.0000 / 1.0015, measured in S0 on the same components. DS3 1.0093 (SLOTSWAP).
- (c) n_eff: 4,900 / 6,672 / 3,902; DS3 3,192.
- (d) SE:
  - The paired fine-NMI difference has no closed form. S0's component bootstrap measured SE(D) at 256 for gemma - qwen3 of 0.00289 / 0.00137 / 0.00247 (s0_run.log L41, L37, L33). This is transported to DS1 (same items and pairing; only the slices differ) and re-measured in-run.
  - DS3: SE 0.0078, from SLOTSWAP M3's CI half-width 0.0153 / 1.96.
- (e) MDE80 = 2.8 x SE: 0.0081 / 0.0038 / 0.0069; DS3 0.022.
  - Planning bars, the larger of S0's measured seed spreads at 256 (qwen3 0.02463 / 0.00942 / 0.01434; gemma 0.01757 / 0.00229 / 0.01400): **0.0246 / 0.0094 / 0.0143**. The bar of record is the in-run spread (K3's rule: one source, stated once).
- (f) VERDICT LINES at the predictions (P3):
  - Banking77 SCOREABLE: +0.045 is 0.031 beyond its bar, more than its MDE of 0.0069.
  - CLINC is DESCRIPTIVE-ONLY at the point: -0.012 is 0.0026 beyond -0.0094, less than its MDE of 0.0038. It is SCOREABLE only if the true D <= -0.013.
  - MASSIVE DESCRIPTIVE-ONLY: +0.022 lies inside its 0.0246 bar.
  - So the 2-of-3 verdict is SCOREABLE as a classification: both KEEP and REOPEN are observable at n. But the corpus most likely to decide it sits inside its own bar. That is why KEEP's words are "not shown", never "explained by the slice".
  - DS2: at a predicted +0.010 against bars of 0.009-0.025, DESCRIPTIVE-ONLY (the curve is the deliverable).
  - DS3: +0.055 is 0.0215 beyond its 0.0335 bar, less than its MDE of 0.022, so DESCRIPTIVE-ONLY.
  - DS4: DESCRIPTIVE-ONLY. H rests on 60 / 150 labels; MMLU-GOLD's item-bootstrap SE was 0.029.
- (g) STRUCTURAL LEG:
  - DS1 is reachable at infinite budget only where the true absolute D* exceeds the in-run seed spread, which does not shrink with n. Inside the spread a corpus reads NEITHER at any budget, and KEEP is then the verdict by construction on that corpus (stated now).
  - The GATE selection is always computable.

**Predictions (80% intervals; priors named).**
- P1 selection: d_q* in {1024, 4096} 0.55, = 512 0.30, = 256 0.15; d_g* = 768 0.75.
  - Priors: the D1 sweep (512 for trees); MRL truncation is lossy below the native width.
- P2 (DS2) qwen3 NMI(d_q*) - NMI(256): +0.010 [0.000, +0.025] on each corpus.
- P3 (DS1) D*: MASSIVE +0.022 [+0.005, +0.040]; CLINC -0.012 [-0.025, +0.002]; Banking77 +0.045 [+0.030, +0.060].
  - Prior: S0's D at 256, minus P2's qwen3 gain, plus a gemma 768 gain of about +0.003.
- P4 verdict: KEEP 0.55 (KEEP-STRONG 0.05), REOPEN-CANDIDATE 0.45.
- P5 (DS3): +0.055 [+0.030, +0.080] (SLOTSWAP M3 +0.066, minus a qwen3 gain).
- P6 (DS4, at the point): gemma H > qwen3 H on MASSIVE at every qwen3 slice 0.85; qwen3 H non-decreasing in d on both corpora 0.50.

**Falsifier.** F-DS fires iff DS1 reads REOPEN-CANDIDATE.
- It overturns this registration's working hypothesis that S0's gemma > qwen3 at the fine level is a slice artefact.
- The descriptive "gemma beats qwen3" rows of S0 C1a and SLOTSWAP M3 then survive the dimension confound, on RAW prompts and with mismatched quantisation.
- No recorded number is revised.

**Out of scope, disclosed.**
- Quantisation. A non-Q4 qwen3-embedding (Q8_0 / F16, about 8-15 GB) needs a download and a 57,350-text re-embed, which is one heavy Ollama process. That would be its own registration (EMBED-QUANT). Whether to pull the weights is the machine lane's call; disk space is the author's.
- Prompt protocol: CARD-PROTOCOL, at this test's d*.
- MMLU-Pro: E0b's slices are not re-read here.

**Cost.**
- 0 calls, 0 cce, 0 embeddings.
- CPU: an estimate, unsourced, of 1-2 h single-threaded. It is dominated by 15 k-means fits at 4096-d (CLINC TRAIN about 13.5k x K 150). The dry-run times one 4096-d fit and prints the full price.
- Memory: about 0.94 GB for the qwen3 matrix (float32).
- Agent time:
  - engine-coder about 2-3 h (one script that imports S0's functions, with a --dry-run that prints the pins, the denominators and the timing);
  - reviewer READY plus a post-run review;
  - registrar.

## Plan of delegation (briefs; each "report in the KNOWLEDGE §0 format"; pins per KNOWLEDGE §1)

1. **registrar.** Commit the registration text above verbatim. Queue item EMBED-DIM-SLICE, lane CPU, 0 calls. Acceptance: the rule-9 re-grep and the closed-lines check. Already verified: the S0 pins, the DB dims, the quantisations, and 0 ledger hits.
2. **engine-coder** (worktree emb-dim-slice, from main). Build tools/analysis/embed_dim_slice.py. It imports S0's functions (no copies), and its --dry-run prints the sha256 of the 3 DBs, the GATE / EVAL counts, one timed 4096-d fit and the identity check. Acceptance: the identity precondition passes in the dry-run, and the selection file is written before any EVAL read (shown by execution). Hand to the reviewer.
3. **adversarial-reviewer.** READY on the script at zero calls. It checks the GATE-before-EVAL order by execution, the in-run bar, the identity digits, and that no fit reads EVAL. Output docs/reviews/READY_embed_dim_slice.md.
4. **run-operator.** Dry-run, then --run, in a no-construction window (CPU lane).
5. **adversarial-reviewer.** Post-run, on DS1's three D* values and bars, and on the verdict. Then the **registrar** records the outcome, the ledger row and the queue. Then the synthesis is written here.

## Synthesis (after the outcome; frame fixed now)

- If KEEP: the S0 / SLOTSWAP gemma edge is not shown at fair slices. D3 stands on more than incumbency. CARD-PROTOCOL then tests the protocol at d*.
- If REOPEN-CANDIDATE: the edge survives the slice. The author's D3 revisit waits on CP1 and E1, and quantisation is the remaining named confound.

**What this result does NOT show (fixed now, before data):**
- Anything about quantisation (Q4_K_M vs BF16, uncontrolled) or prompts (RAW).
- Anything about MMLU-Pro or capability text. Intent corpora only.
- Embedder parity: there is no TOST, and NEITHER is never parity.
- That the slice "explains" the S0 edge, when the deciding corpus reads NEITHER inside its seed-spread bar.
- That d_q* is the right slice for trees (D1 measured certification; this test measures fine NMI against gold).
- Any change to the embedder of record. D3 is the author's.

## Decisions that are the author's
- D3 (the embedder of record) after this test, CARD-PROTOCOL and E1.
- Pulling a non-Q4 qwen3 tag (disk and machine lane), if EMBED-QUANT is wanted.
