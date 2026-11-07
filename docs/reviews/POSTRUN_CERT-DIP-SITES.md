# POSTRUN review: CERT-DIP-SITES (lead #7; the split-dip rule under hierarchical BH at the sites of the two trees of record; exploratory)

Authority: D-2026-11-06-3 (`docs/agents/author_decisions/2026-11-06.md`), leads file `docs/agents/plans/2026-11-06_leads.md`
"### 7. CERT-DIP-SITES (rank 7)" (b42d58ef). Reviewer: adversarial reviewer, 2026-11-07. Zero LLM calls.
What I read: the run's saved outputs (`E:/TaxoArena_backup_2026-11-06_cert-dip-sites/{record,rerun,logs}`, equal to
`E:/TaxoArena_tmp/cert_dip_sites/`), the two site-null CSVs and `dag_snapshots.jsonl` last records (LF sha256 = CERT-RESOLUTION's
pins), and, for the data-object check only, the two trees' member rows: `snapshots.db` graphs and `embeddings_cache.db` member
vectors, `mode=ro&immutable=1`, -wal 0 bytes, no java / Gradle / other python running (process list), both DB sha256 / size /
mtime equal before and after my read and equal to the builder's `db_pre/` pins. Vault / RESERVED / sealed / EVAL rows read: 0
(BBH's sealed side untouched; the p2dca id file read as ids only, and none of its 3,445 ids is a `queries.id`, so no reserved
row matched). One process, BLAS 1. Scripts: scratchpad `.../7c10e5cb-.../scratchpad/{recompute,dataobj,own_mutants}.py`;
sandbox `E:/TaxoArena_tmp/cds_review_20261107/`. Nothing deleted.

Reviewed: TaxoArena branch `cert-dip-sites` (worktree `.claude/worktrees/cert-dip-sites`), 298b9cc9..b56d5008: 3 commits,
2 new files (`git diff --name-only main...cert-dip-sites | wc -l` = 2; `| grep -c '^src/'` = 0). Merge base = main = 298b9cc9
(fast-forward); b42c3300 is an ancestor. Each commit touches 1 path (`git show --name-only --format= <c> | wc -l`).
- Pins (LF of record; 0 CR bytes in the working file, so no separate CRLF rendering): runner `blob:6ae15e5d`
  (sha256-lf16:2589f379665dba05) = `d0408d27:` = tip; plan at the run `blob:34e80c3b` (sha256-lf16:e1832ad64e51e133) =
  `67c0a16a:` = the cache meta's plan pin; plan at the tip `blob:4649fc18` (sha256-lf16:811bb0381eb08d92), +26 / -0 vs 67c0a16a.
  Imported modules = main's blobs (cert_split_dip 1d46cd73, cert_resolution dbe9425d, embedder_guard 3fd9aea5, cert_planted
  028f05a2). Outputs: outcome sha256 2e9a962fc1be4ab4, sites CSV 6511fd0afdfa11cd, cache 354ad4d8da1d8ecb, SHA256SUMS.txt
  4111f3e3d82cde67; `sha256sum -c` 16 of 16 OK.
- Order: plan 67c0a16a 03:41:46 < runner file mtime 04:04 < runner commit 04:08:45 < probe 04:08:57 < dry-run (0 dip calls)
  04:09:38 < first dip output (cache) 04:12:06. No other cert_dip / CDS output exists under E:/TaxoArena_tmp or the backup
  (`find -iname '*cert_dip*' -o -iname '*cds*'`: 12 hits = the script 04:04, its pyc 04:00, the plan 04:19 and 9 output
  paths at 04:12 or later). A real-tree `--run` before 04:08:45 is impossible by code: `HEAD:<runner>` did not exist, so the
  blob compare of `clean_tree_check` refuses (fixture flags need a `.cds_fixture` data root).

## Verdict

- **CERT-DIP-SITES: OUTCOME CONFIRMED (EXPLORATORY; construction rows of each tree; each tree in its own block, never
  joined), with qualifiers Q1 (MEDIUM) and Q2-Q5 (LOW).** Every deciding number reproduces to the digit from the saved
  cache with my own BH / hierarchical-BH code (no import of the runner or cert_resolution): p_site = min(1, 2 x median) at
  1,668 / 1,668 rows, both J sets, both MODAL sets, G0, NULL-TREE, PLANT, W1-W3, F-DIP and every P line and Brier. My own
  read of the members reproduces the OBS rows bit for bit (row hash = cache `ysha` at 70 / 70 and 69 / 69 sites) and the
  pinned rule on my rows gives the cached p (to the 6 printed digits) at the 7 deciding sites.
- **One hand-back sentence is not licensed as worded:** "Chemistry n00000006 is not modal" (and "Chemistry n00000006 not" in
  the b56d5008 subject). Plan section 6: "No site is called 'not modal', 'unimodal' or 'unreal'" (Q1).
- **MERGEABLE: YES** (fast-forward, 2 new files, 0 `src/`, so `execution_graph` owes nothing). Q1-Q5 go into the registrar's
  record or an insertion-only [P2] of the plan; no rerun. D1-D2 are LOW code defects for any reuse of the runner. No
  BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table (deciding claims; bareq512_s42 = R512, id-disjoint only; af_clean_s42 = R256, content-closed)

| # | claim | mine | verdict | sev |
|---|---|---|---|---|
| C1 | bareq G0 SIZE-OK, 0 of 700 null draws p <= 0.05 | 0 of 700; CP upper 0.00526; all 700 null p_site = 1.0 | CONFIRMED (Q2) | - |
| C2 | bareq D = {n00000015 Engineering}, p 1.4e-05 | D = {n00000015}, p 1.41519e-05; TOP family 14, bar 0.05/14 = 0.00357; 15 reached, 55 UNTESTED | CONFIRMED | - |
| C3 | W2 ONE (n00000015); Chemistry p 0.326 | p 0.3261790, TOP rank 5 of 14, reached, not rejected -> ONE (n00000015) | CONFIRMED; "not modal" REFUTED as worded | MEDIUM (Q1) |
| C4 | bareq W3 FEWER (1 vs 2), overlap 1 | J (own hier BH on CSV q_site) = {n00000006, n00000015}; FEWER; overlap 1 of 2 | CONFIRMED | - |
| C5 | bareq PLANT 64 of 70 | 64 of 70 (0.9143); outside D 63 of 69 | CONFIRMED | - |
| C6 | af G0 SIZE-OK, 0 of 690 | 0 of 690; CP upper 0.00533; all 690 null p_site = 1.0 | CONFIRMED (Q2) | - |
| C7 | af D = {root n00000001, n00000004} | p 0.000207610, 0.0; reached 5 (n00000001, -04, -05, -46, -47), 64 UNTESTED; flat BH 3 (+ n00000085, UNTESTED) | CONFIRMED | - |
| C8 | af W3 FEWER (2 vs 8); only the root in both | J = the 8 of record; FEWER; overlap 1 of 8; n00000005 tested p 1.0; the other 6 J sites UNTESTED | CONFIRMED (Q3) | LOW |
| C9 | af PLANT 69 of 69 | 69 of 69 | CONFIRMED | - |
| C10 | F-DIP NOT FIRED on both (0 of 10 replicates) | replicates [0 x 10] on each tree | CONFIRMED (Q2) | - |
| C11 | P1, P2, P4 HELD; P5, P9 FAILED; P7 HELD / FAILED; P3 ONE Brier 0.465 | same; P3 0.4650, P6 yes 0.0100, P8 FEWER 0.5600 / 0.8600 | CONFIRMED | - |
| C12 | REPRODUCED (bit-equal) | rerun meta == record meta; 1,668 rows equal as a set (files differ in order only); outcome and sites CSV `cmp` equal | CONFIRMED | - |
| C13 | DB sha256 equal before / after | builder logs EQUAL; my pins after my read b0e88d3a6e207bc0 / 431e19fa9bb42e92 = db_pre | CONFIRMED | - |
| C14 | selftest 66 PASS; mutants 46 / 46 | re-run: 66 PASS; 46 / 46 KILLED (0 SURVIVED; X29 by KeyError); own: 2 of 6 killed, 4 survive, none decisive | CONFIRMED (D2) | LOW |
| C15 | Gradle 569 tests, 0 failed, 2 skipped | test-results XML: 569, 0 failures, 0 errors, 2 skipped (the two named) | CONFIRMED | - |
| C16 | members = construction rows; no held-out / reserved read | own DFS: members == CSV n at 70 / 70, 69 / 69; vectors 8,278 / 8,125 found at 4,096; id overlap with p2dca not checkable (Q5) | CONFIRMED on the record's split words + code path | LOW (Q5) |
| C17 | plan before every statistic | order above; plan edit insertion only (0 removed lines); cache plan pin = 67c0a16a's blob | CONFIRMED | - |

Support (re-derived): G0 SE 0.00824 / 0.00830, CP upper at 0 events 0.00526 / 0.00533, MDE80 0.0231 / 0.0232, PLANT SE 0.0518,
P(>= 3 of 10 | 0.05) 0.0115: all reproduce the plan's section 7. Post-run DEFF: 0 events, so the ICC is undefined (NA, as
printed); at the worst case DEFF = 10 (every draw of a site identical) n_eff = 70 / 69 and the CP upper at 0 events is 0.0513 /
0.0521 <= 0.15, so G0 SIZE-OK holds at any DEFF. W1-W3 are set readouts with no sampling SE; their only internal randomness
is the halving seed (descriptive spot check, 3 alternate site names through the pinned `dip_site` on my rows): Engineering
1.08e-05..1.42e-05 (bar 0.00357), Chemistry 0.33..0.55, Health n00000009 0.012..0.074 (rank-2 bar 0.00714), af root
0.00021..0.0019 (bar 0.05), n00000004 0 x 4, n00000005 1 x 4, n00000085 0 x 4: no deciding membership moves. Distinct rows =
distinct texts = n at all 7 sites, so p = 0 at n00000004 / n00000085 is not a duplicate point-mass artefact.

## Qualifiers and defects (each with its fix)

- **Q1 MEDIUM (wording).** "Chemistry n00000006 is not modal" (hand-back) and "Chemistry n00000006 not" (b56d5008 subject)
  break plan section 6. Fix: the registrar writes "Chemistry n00000006: no split-dip word (reached in the TOP family of 14,
  p_site 0.326, rank 5; EXPLORATORY)" and Engineering's word verbatim: "MODAL (split-dip) at per-family FDR q = 0.05
  (hierarchical BH over nested sites, bareq512_s42, R512; EXPLORATORY)", with "id-disjoint only". No count or site word goes
  without its M1-M3 text; "UNTESTED" is never "not modal".
- **Q2 LOW (uninformative gate, disclosed).** 700 / 700 and 690 / 690 null draws read p_site = 1.0 (minimum 1.0), so G0 and
  F-DIP certify only that the rule never fires on each site's moment-matched Gaussian. Size against non-Gaussian unimodal
  shapes rests on the dip's own calibration (uniform least favourable), not on G0. Fix: the record carries "the size gate is
  Gaussian-only and was never near its bar (0 events)" beside every MODAL word.
- **Q3 LOW (af W3 / P9).** "overlap 1 of 8" must read "1 of 8; n00000005 tested p_site 1; 6 J sites UNTESTED (prefix
  closure)". Their descriptive p_site is 1.0 at all 6, so FEWER is not a gating artefact; the sentence still needs it.
- **Q4 LOW (S4).** The plan's [P1] (line 212) and the hand-back write "1,390 NULL draws": 700 + 690, a count joined across
  R512 and R256. Fix: an insertion bracket "700 of 700 (bareq512_s42); 690 of 690 (af_clean_s42)".
- **Q5 LOW (data object).** An id check of members against p2dca cannot be done: 0 of its 3,445 ids is a `queries.id`
  (different id spaces), so "members & pool = 0" would be vacuous and is not claimed. "No reserved item read" rests on
  KNOWLEDGE section 1 (bareq512_s42 id-disjoint only, content twins disclosed; af_clean_s42 content-closed) and on the code
  path (the connect guard admits only `embeddings_cache.db` / `snapshots.db` at `mode=ro&immutable=1`; the dataset DB is never
  opened; the pool id file is hashed only). Fix: word it so; do not cite an id intersection.
- **D1 LOW (vacuous clean check).** `clean_tree_check` runs `git -C tools/analysis status --porcelain -- tools/analysis/
  cert_dip_sites.py docs/agents/plans/...`; the pathspecs resolve under `tools/analysis/tools/analysis/...`, so porcelain is
  always '' (shown: the same form on a modified file in main prints 0 lines, from the top 1 line). The script stays guarded by
  the HEAD-vs-working blob compare; the PLAN is not guarded at all. No consequence on the record (the cache's plan pin
  34e80c3b = 67c0a16a). The selftest never executes this function (OM6 survives). Same class as BBH-RESERVED-CONFIRM C1.
  Fix: `git -C <toplevel>` or `:/`-prefixed pathspecs, and a selftest on a temp repo with a dirty plan.
- **D2 LOW (selftest gaps, own mutants).** OM1 (G0 count strict), OM2 (W2 from the flat set) and OM5 (raw-dimension check
  off) survive; none is decisive on the record (below). The builder's X29 is killed by a KeyError, not by an assertion. Fix:
  one ST8 scenario with a null p exactly 0.05, one where the flat set and D differ at a named site, one fixture with a
  2,048-float vector.
- Disclosed by the builder and agreed, LOW: embedder identity to the 0.99 budget only (min 0.9976 / 0.9990); two early mutant
  passes at 3 copies x (selftest + 2 ST7 workers) exceeded the 3-worker cap (synthetic data only).

## Own mutants (copies in `E:/TaxoArena_tmp/cds_review_20261107/mut`, `--selftest` must fail; CDS_SRC_DIR = the worktree)

- OM1 G0 count strict (`x <= ALPHA` -> `x < ALPHA`): SURVIVED; not decisive (every null p on the record is 1.0).
- OM2 W2 read from the flat BH set instead of D: SURVIVED; not decisive (bareq512_s42 flat = D = {n00000015}).
- OM3 NULL-TREE replicate positive only at >= 2 rejections: KILLED (ST8 repl3).
- OM4 NULL-TREE replicates all read draw 0: KILLED (ST8 repl3).
- OM5 raw-dimension precondition off (`if set(dims) != {RAW_DIM}` -> `if False`): SURVIVED; not decisive (raw dims {4096} at
  8,278 / 8,125 vectors, logged; my own read asserts 4,096 floats at every row).
- OM6 `clean_tree_check` always CLEAN: SURVIVED (the function is never executed by the selftest; D1); not decisive (blob
  compare CLEAN at the run; plan pin = 67c0a16a).

## Commands (all read-only; outputs in the scratchpad / sandbox)

```
git -C <wt> log --format='%h %ad %s' --date=iso main..HEAD; git diff 67c0a16a b56d5008 -- <plan> | grep -c '^-[^-]'   # 0
git diff --name-only main...cert-dip-sites | wc -l   # 2;  | grep -c '^src/'  # 0;  git merge-base --is-ancestor main / b42c3300
git rev-parse 67c0a16a:<plan> d0408d27:<plan>; git hash-object <runner>; sha256sum <runner>; grep -c $'\r' <runner>   # 0
python -I scratchpad/recompute.py     # cache -> p_site, own flat / BY / hierarchical BH, J from CSV q_site, G0, NULL-TREE, PLANT, W, P, Brier
python scratchpad/dataobj.py          # own DFS members, own vector read (ro, immutable), ysha 139/139, duplicates, alt-name p, p2dca ids in queries 0
sha256sum embeddings_cache.db snapshots.db; stat -c '%s %Y'   # equal before / after my read and to db_pre/SHA256SUMS.txt
cd E:/TaxoArena_backup_2026-11-06_cert-dip-sites && sha256sum -c SHA256SUMS.txt | grep -c ': OK'   # 16; cmp record/* rerun/*
git -C docs/drafts status --porcelain -- docs/drafts/2026-10-06_talk_script.md | wc -l   # 0 (vacuous form); from the top: 1
python tools/analysis/cert_dip_sites.py --selftest   # 66 PASS;  --mutants > E:/TaxoArena_tmp/cds_review_20261107/builder_mutants_rerun.log
python scratchpad/own_mutants.py      # OM1-OM6
python: test-results XML count   # 569 / 0 / 0 / 2 skipped
```
