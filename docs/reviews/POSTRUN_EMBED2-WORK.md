# POSTRUN review: EMBED2-WORK (V0 / K / N re-read on a second embedder, Ollama embeddinggemma; EXPLORATORY, WORK only)

Authority: D-2026-10-27-3 (TaxoArena c3aada22; "You can use the most relevent embedder available on ollama, ..."; the
main session's reading: EMBED2-WORK authorised, embeddinggemma chosen, new embedding files only). Reviewer: adversarial
reviewer, 2026-10-27. Zero LLM calls (the embedding model only: 50 distinct strings in 56 `/api/embed` requests:
50 single, 3 batch-16, 3 card-prompt); vault / reserved reads 0 in my own loads ([0, 0] on each corpus); at most 2
worker processes of mine at a time (plus an idle parent), BLAS 1.
Reviewed: benchzoom branch `embed2-work` (local only, 0 remotes), 35b2724..d17fde2, merge-base = master 35b2724 (master
tip unchanged). Tip LF blobs: plan `b5db60a2`, runner `881f9922`, test `de8634ee`; 0 CR bytes in all 3 files and
`git hash-object` = tip blob, so no CRLF rendering differs. Run blobs: embeds MATH `1e7b97a1`, MMLU-Pro `340c4952`
(dirty, in no commit), MMLU `25dc304d` (see D6); builds `b2c6a16b` / `78d678e5` / `e7049516`; parts and `--analyze`
`e7049516` (MATH launched from `25dc304d`, which differs by the EMB_PINS mmlu line only: `git diff ecf0bc8 291dc29`
= 1 line). Outputs `E:/benchzoom_demo/followups/embed2-work`: SHA256SUMS 10/10 OK, summary.txt sha256 ea79bb85...;
backup `E:/TaxoArena_backup_2026-10-27_embed2-work` SHA256SUMS_backup 30/30 OK (manifest sha256 15599be6...).

## Verdict

**OUTCOME CONFIRMED (exploratory). The pre-specified words stand as printed: R1 "V0 EMBEDDER-INVARIANT", "K
EMBEDDER-INVARIANT", "N NOT EMBEDDER-INVARIANT (moves on: MMLU (gemma lower))", "N512 EMBEDDER-INVARIANT"; R2 "ORDERING
NOT INVARIANT (moves: MATH V0 - K)". MERGEABLE (merge_ok): 3 new files, src untouched, plan insertion-only.**
- Every deciding number reproduces to the digit: own CR1 + MC statistics on the per-item arrays (max gap 2.8e-17 over
  42 statistics x 3 corpora); my own harness loop from `granularity_work` / `meter` primitives, on partitions and gemma
  rows I built myself, gives the per-item C1 arrays of V0, V0g, Kg0-4, Ng and both controls on all three corpora, and of
  N, N512, Ng512 on MATH and MMLU-Pro, with max |diff| 0.0 (MMLU N is the FLAT-COMPARE array, 0.0 npz-vs-npz).
- My own rebuild of the MATH gemma tree from the pinned npz gives the pickled V0g exactly (62 nodes, 34 leaves, same ids).
- The embedding files are what the plan says: my own re-embed of 50 random strings matches the npz rows to 7.7e-9
  (cosine 1.000000); the card prompt would give cosine 0.68-0.88, so the stored vectors are RAW.
- Conditions on USE, not on the merge: D1-D4 (what "invariant" licenses; two [P2] readings over-reach; power; one
  V0g build). An insertion-only [P3] bracket in docs/embed2-work.md carries them.

## Per-claim table (deciding claims)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 599f674 committed before any vector, tree or statistic | Committer = author dates; reflog 9 commits, no amend/reset. Plan 15:50:36; first gemma vector after runner 5f5a2f6 (16:08:21; MATH embed 16:08:33-16:20:52). Each pin before its build: MATH b13f351 16:24:39 < build start 16:24:47; MMLU-Pro 0d82af4 16:52:47 < 16:53:00; MMLU 291dc29 17:28:39 < 17:28:41. [P1] (16:24:39) precedes every build. Parts: MATH 17:11:26-17:33:53 (launched from ecf0bc8, 17:11:24), MMLU-Pro 17:35:56-17:46:46, MMLU 17:48:47-19:36:20 (after its build, 17:48:24), the runner of every later part (e7049516, 291dc29 17:28:39) committed before the first part ended (17:33:53); after it only 3493d49 (tests/ only) and d17fde2 (runner: one docstring hunk, the 1 removed line is the mutant-table placeholder; tests/ 1 assertion). Files written 15:30-16:08:30 outside test/mutant/selftest sandboxes: 1, another workflow's (guards-fresh-tau). Plan diff 599f674..d17fde2: 0 deleted lines | CONFIRMED | - |
| 2 | Embedder pinned, RAW protocol, same strings as qwen3, nothing truncated, new files only | Live `/api/tags` digest 85462619... = pin; Ollama 0.40.6. Gemma key sets = {sha256(name NUL text)} of the text side's strings on all 3 corpora (4,914 / 13,937 / 11,836 = qwen3 key counts; every item's qwen3 key in the qwen3 cache). Own re-embed (17 / 17 / 16 random distinct strings, single and batch-16): cosine min 1.000000, max abs diff 7.66e-9 / 7.21e-9 / 7.01e-9; with "task: clustering \| query: " cosine 0.68-0.88. Provenance: resumed False, n_embedded_now = distinct, truncated 0, fallback batches 0. qwen3 caches equal their pins (8b66bb23 / a1008263 / 38faef9c; mtimes 10-09 / 10-10 / 10-22); gemma npz = EMB_PINS; TaxoArena `embeddings_cache_embeddinggemma_latest.db` mtime 2026-09-29 | CONFIRMED | - |
| 3 | V0g 34 / 93 / 76 leaves, anchored, built on the pinned rows | Own walk of the pickled trees: leaf counts 34 / 93 / 76 (V0 36 / 100 / 80); depth-1 = V0's anchors; max 1 anchor per leaf; x_sha(own X512g from the npz by text key) = pickle x_sha256 on all 3; build config = V0's pickled config on all 34 fields (3/3); own rebuild of MATH V0g from the npz (`v5-orth.build_tree`, 361 s): 62 nodes / 34 leaves, leaf ids identical. MMLU / MMLU-Pro not rebuilt | CONFIRMED | - |
| 4 | Reproduction: V0 / KM / RND / N = FLAT-COMPARE, per item 0.0 on 14 arrays; MATH N512 = FRESH-RULES; cAMI = LABEL-ALIGN | npz-vs-npz: 14 common arrays per corpus, max \|diff\| 0.0, clusters equal (reference npz sha256 = FC_SHA, repro.npz f8c0e310...); MATH N512 vs FRESH-RULES 0.0. Own harness: V0 and both controls 0.0 (3 corpora); L3k, N512 0.0 (MATH, MMLU-Pro) | CONFIRMED | - |
| 5 | Gemma arms are what the plan says | Own partitions equal the part npz: V0g, Kg0-4 (flat-compare k-means on own X512g at V0g's per-anchor k), RNDg0-4: 12/12 equal on each corpus. Own field rows by text key; qwen3 text-side rows = meter WORK rows to 2.8e-17. Own harness per item, max \|diff\| 0.0: V0g, Kg0-4, Ng (3 corpora), Ng512 (MATH, MMLU-Pro). Not recomputed: MMLU N512 / Ng512 (same `make_fields` call, verified on the other two corpora and through MMLU Ng's rows) | CONFIRMED | - |
| 6 | C1 and paired tables of [P2] | Own stat code (CR1 written with reduceat, MC = SD of per-seed G / sqrt 5) on the part arrays: every value and SE of both tables and the cont brackets, max gap 2.8e-17 | CONFIRMED | - |
| 7 | R1: V0 / K / N512 INVARIANT; N NOT (MMLU, gemma lower) | Own rule code: 11 legs hold, MMLU N fails: D -0.0380, SE 0.0176 (n 8,425, 8,375 clusters, DEFF 1.003, n_eff 8,397, MDE80 0.0501), z -2.16. cont: z -2.15 (fails). V0-leaf SE 0.0221: z -1.72 (holds) | CONFIRMED (D5) | LOW |
| 8 | R2: NOT INVARIANT (moves: MATH V0 - K) | qwen3 -0.1652 (0.0358) z -4.61 beyond 3 SE; gemma -0.0363 (0.0279) z -1.30 within. Other cells same. Own direct test of the change (paired, MC included, not pre-specified): (V0-KM)q - (V0g-Kg)g = -0.1289, SE 0.0444, z -2.90; MATH V0-N +0.0093 (z +0.15); MMLU V0-K +0.0226 (z +1.04); MMLU V0-N -0.0405 (z -1.62) | CONFIRMED | - |
| 9 | Continuous tau^2 prints the same words | Own cont legs: same 5 words; golden point 752 / 741 / 748 of 875, 0 at the bound (from parts) | CONFIRMED | - |
| 10 | Support / power: DEFF 1.00-1.03, MDE80 0.047-0.159, flags | DEFF re-measured from the parts' own clusters (2,946 / 8,375 / 7,085 clusters, max size 2 / 2 / 3): 0.998-1.030 on every leg; n_eff 2,943-8,425. MDE80 0.0466-0.1587; UNDERPOWERED flags on exactly the 5 printed legs. But: every INVARIANT word contains an UNDERPOWERED leg; V0 MATH MDE80 0.1080 vs \|C1\| 0.1093 (ratio 0.99); realised MATH SEs 1.55x / 1.80x / 2.99x the planning SEs (V0 / K / N) | PARTLY | MED (D3) |
| 11 | Predictions PE1 HELD, PE2-PE4 FAILED, PE5 HELD, PE6 FAILED | Scored per plan §8 from the values. Spot check (descriptive): own pooled within-anchor cAMI (sklearn exact EMI) on own tree walks: MATH V0 0.0287, V0g 0.0251, agreement 0.4341; MMLU-Pro 0.3207 / 0.3369 / 0.5465, all = builder's at 4 decimals | CONFIRMED | - |
| 12 | Vault / reserved reads 0; zero LLM calls; no write to data of record | Parts: vault_reads 0, MMLU [0, 0], fallbacks 0. My loads: [0, 0] on all 3. In 15:34-19:41 the only files under E:/benchzoom_cache written by this test are the 3 new npz (the rest: BBH and MATH-train groundwork of other workflows). My runs: listing (path, size, mtime) of 2,578 files under benchzoom_cache, embed2-work, flat-compare, fresh-rules identical before and after (diff 0 lines); outputs 10/10 OK after | CONFIRMED | - |
| 13 | Selftest 9/9; mutants 86/86; suite 902 passed | Own sandboxed selftest (R0): 9 PASS / 0 FAIL by count. Branch tests: 5 passed, 1 deselected (slow = the selftest). Own mutants 6/8 killed; the 2 survivors are non-decisive for this run (D8). Builder's jsonl: last entry per id 87, 86 killed + control; X85's kill is the sandbox import check. Full suite not re-run (src diff 0 files) | CONFIRMED | LOW (D8) |
| 14 | [P2] readings (1)-(6) | (2), (4), (5), (6) correct. (1) "read the same predictive gain" and (3) "'the soft text field beats the tree' is not [embedder-dependent]" over-reach | PARTLY | MED (D1, D2) |

## Defects (none blocks the words or the merge)

- **D1 MEDIUM: "invariant" is written as equality.** [P2] reading (1) says the three readers "read the same predictive
  gain on the second embedder". No equivalence margin was pre-specified; the word means "no movement beyond 2 paired
  SE". 2-SE intervals as a share of the qwen3 gain: V0 MATH [-22%, +117%], MMLU [-80%, +91%]; K MATH [-59%, +3%], MMLU
  [-15%, +111%]; N512 MATH [-12%, +66%], MMLU [-64%, +6%]; MMLU-Pro legs span more than the whole gain. Fix ([P3]):
  "no movement detected at 2 paired SE (MDE80 0.05-0.16)".
- **D2 MEDIUM: reading (3) holds on MATH only.** The field's lead over the tree is unchanged on MATH (z -4.44 vs -4.39;
  change +0.0093, z +0.15). On MMLU it shrinks from -0.0629 (z -2.97) to -0.0224 (z -1.08; change -0.0405, z -1.62),
  and on MMLU-Pro from z -2.40 to -1.88. The R2 cell stays "same" only because the qwen3 MMLU z (-2.97) sits just inside
  the 3-SE line. Fix ([P3]): "'the soft text field beats the tree' is embedder-robust on MATH; on MMLU under gemma the lead
  is not established".
- **D3 MEDIUM: no INVARIANT word is powered on all three corpora.** V0: MMLU and MMLU-Pro UNDERPOWERED, MATH at MDE80 /
  |C1| = 0.99; K and N512: MMLU-Pro UNDERPOWERED (K MMLU 0.89). The UNDERPOWERED bar is the reader's WHOLE gain, so the
  unflagged legs detect at 80% only losses of 44% (K MATH) to 99% (V0 MATH) of the reader's qwen3 gain. The planning SEs (V5-ORTH, a centring variant) were
  1.5-3.0x too small on MATH. Fix ([P3]): print the 2-SE intervals of D1 beside the words; name the backed legs: K
  and N512 on MATH and MMLU, V0 on MATH (borderline); MMLU-Pro backs nothing.
- **D4 MEDIUM: the V0g - V0 legs carry no build-variability term.** V0 and V0g are one seed-0 build each (MC 0.0000),
  as in POSTRUN_V5-ORTH D2. Part of the MATH +0.052 (z +1.38) or of the R2 move could be build noise. Fix: state it; if
  a V0g arm is ever used, build >= 3 recipe seeds per embedder and add their MC term.
- **D5 LOW: the one NOT word is fragile.** N MMLU z -2.16 is one of 12 legs (P(at least one leg fails | no embedder
  effect) about 0.43 if independent); it holds under the V0-leaf SE (z -1.72); Ng512 - N512 points the same way
  (z -1.64), with correlated legs; and N vs Ng changes the width too (4,096-d vs 768-d), while the width-matched
  N512 leg holds. Fix: print beside the word.
- **D6 LOW: embed provenance names end-of-run code.** `code_rec()` runs when the record is written (30-35 min after
  launch): mmlu_pro.json names blob 340c4952 (dirty tree, in no commit) and mmlu.json 25dc304d, not the launch blobs the
  docstring names. `git diff 5f5a2f6 291dc29` changes only EMB_PINS, a `check_recipe` extraction (same refusal), one
  `draw_sizes` info line and selftest lines, so the embed path is identical; own re-embed confirms the vectors. Fix:
  capture `code_rec()` at launch.
- **D7 LOW: process cap.** About 17:28:41-17:33:22 (MMLU build + MATH harness, 2 workers) and 17:36:41-17:45:38 (MMLU
  build + MMLU-Pro harness, 2 workers; times = part json mtime less load, harness and alignment seconds) ran 3 busy CPU
  processes, and the Ollama GPU embeds ran beside CPU builds and the MATH part
  (KNOWLEDGE §2: one heavy process at a time; [P1] discloses the embed/build overlap only). Results unaffected (own
  reproduction 0.0). Fix: none now; serialise next time.
- **D8 LOW: two guards are not pinned by the selftest.** Own R2 (card prompt prepended to every request) SURVIVES: E1
  never checks the strings the transport receives, so the RAW protocol is guarded only by my live re-embed (row 2), not
  by code. Own R7 (Z80 0.8416 -> 1.2816) SURVIVES: the MDE80 constant is not asserted (the printed MDE80s use 0.8416; I
  recomputed them). X85 is killed by the sandbox copy's import check, not by an assertion on the resumable skip. Fix:
  assert in E1 that the fake transport received exactly the cache strings; assert Z80 against plan §7; test the skip
  with a stub loader.

## What it licenses / does not

- **Licenses (exploratory, WORK rows, selection; RAW-protocol embeddinggemma; one V0g build):** on MATH and MMLU, at 2
  paired SE, no cross-embedder movement is detected for matched k-means (K) and the width-matched kNN reader (N512); on
  MATH none for the axis tree (V0). The full-width kNN reader N reads 0.038 lower on MMLU under gemma (z -2.16, fragile:
  D5). On MATH the kNN field beats the tree by more than 4 SE under both embedders; the k-means lead over the tree on
  MATH shrinks from 4.6 to 1.3 SE (change z -2.90, post hoc). The gemma tree's leaves are a different object (cAMI with
  V0 0.43-0.56; same-k k-means across embedders 0.52-0.65; two qwen3 k-means seeds 0.78-0.85).
- **Does not license:** equality or equivalence of any reader across embedders (D1); "V0's gain is embedder-robust"
  (D3); anything on MMLU-Pro; "the field beats the tree" beyond MATH under gemma (D2); "N is embedder-dependent" as a
  finding (D5); the card-prompt protocol, other embedders, or other widths; fresh items; any vault, reserved or
  registered number; replacing V0, its embedder or any deciding estimator of BZ-AXIS-CONFIRM-FRESH (the author's).

## Own mutants (copies under E:/TaxoArena_tmp/rev_embed2work/mut_<stamp>/<id>, TMP / TEMP / BZ_SANDBOX redirected; runner `--selftest`)

| id | change | result | decisive |
|---|---|---|---|
| R0 | control | passes (9 PASS) | - |
| R1 | deciding paired SE clustered by V0 leaf instead of content cluster | killed (S3, S4, S6, S8) | yes |
| R2 | card task prompt prepended to every embed request | SURVIVED | no for this run (row 2 proves RAW); D8 |
| R3 | R2 qwen3 3-SE status judged with the gemma SE | killed (S6) | yes |
| R4 | Kg streams shifted (s + 1) | killed (S2) | no (any seed set valid; plan fixes the streams) |
| R5 | R1 word ignores the MMLU-Pro legs | killed (S6) | yes |
| R6 | UNDERPOWERED against the gemma arm's C1 | killed (S6) | no (flag) |
| R7 | Z80 0.8416 -> 1.2816 | SURVIVED | no (MDE80 printout; D8) |
| R8 | paired difference sign flipped (B - A) | killed (S3, S4, S5, S6, S8) | yes |

## Commands (scripts in the session scratchpad; every data read read-only; venv Z:/FAC/TUBerlin/benchzoom/.venv)

```
git log --format='%h %ad %cd' --date=iso-strict master..embed2-work ; git reflog --date=iso embed2-work
git diff --name-only master...embed2-work | wc -l                  # 3 ; -- src | wc -l  -> 0
git diff 599f674 d17fde2 -- docs/embed2-work.md | grep -c '^-[^-]'  # 0
git diff 291dc29 d17fde2 -- examples/embed2-work.py | grep '^@@'     # one hunk at L39 (docstring)
git diff 5f5a2f6 291dc29 -- examples/embed2-work.py                  # pins, check_recipe extraction, draw_sizes, selftest
for f in plan runner test; do tr -cd '\r' < $f | wc -c; git hash-object $f; git rev-parse d17fde2:$f; done
curl localhost:11434/api/tags | digest ; sha256sum E:/benchzoom_cache/emb/*.npz
python verify_embed.py      # key sets, qwen3 coverage, 50 re-embeds (single, batch 16, card prompt)
python recompute_stats.py   # own CR1 + MC, all arms / legs / cells, words, V0-leaf and cont re-reads, FC / FR npz 0.0
python extra.py             # R2 change between embedders, paired with MC
python rev_harness.py {mmlu_pro,math} 2 all ; rev_harness.py mmlu 2 Ng   # own partitions, gemma rows, g2 harness -> 0.0
python cfg.py ; python rebuild.py math                                   # configs 34/34 equal; MATH V0g rebuilt identical
python rev_cami.py          # sklearn pooled cAMI spot check (MATH, MMLU-Pro)
python rev_mut.py           # R0-R8 (E:/TaxoArena_tmp/rev_embed2work/mut_20261027_221842)
pytest tests/test_embed2_work.py (sandboxed basetemp)                   # 5 passed, 1 deselected
find <data of record> -printf '%p %s %T@' before / after my runs | diff  # 0 lines (2,578 files)
find ... -newermt '2026-10-27 15:30' ! -newermt '16:08:30'   # 697 = 210 pytest + 486 sandbox/mutant copies + 1 other workflow
sha256sum -c SHA256SUMS (10/10) ; sha256sum -c SHA256SUMS_backup (30/30)
```
