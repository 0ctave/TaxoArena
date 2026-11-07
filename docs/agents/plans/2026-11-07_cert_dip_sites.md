# CERT-DIP-SITES: does the split-dip rule find modal structure at the real sites of the trees of record, under hierarchical BH over nested sites, and are Chemistry n00000006 and Engineering n00000015 among them? (EXPLORATORY; zero calls; CPU; rule-7 window)

STATUS: PLAN, committed BEFORE any statistic on tree members' vectors is computed and before the runner reads a member
vector. Not a registration and not a registered result: every number it produces is EXPLORATORY. Later edits are
insertion-only brackets `[P<n> <date>: ...]`.

Authority: author decision D-2026-11-06-3 (`docs/agents/author_decisions/2026-11-06.md`, b42c3300), the selection
verbatim: "Which zero-call leads should start now? None of them opens held-out data." = "SuperGPQA finer levels (#3)",
"Roster size (#6)", "Dip certificate (#7)", "Write-up angle (#2)"; meaning, as worded: "#7 CERT-DIP-SITES (in a window
with no other data readers) ... all zero calls". The lead: `docs/agents/plans/2026-11-06_leads.md` (b42d58ef) section
"### 7. CERT-DIP-SITES (rank 7)": "does the sample-splitting dip certificate, under hierarchical BH over nested sites,
certify real sites of the trees of record, and are Chemistry n00000006 and Engineering n00000015 among them?"; "R512
(bareq512_s42, id-disjoint only) and R256 (af_clean_s42, content-closed) counts are never joined (S4)". Zero LLM calls;
no judge; no embedding call; no held-out, vault, reserved or sealed item is read (tree members are construction rows);
no construction; nothing under `src/` changes (one new script `tools/analysis/cert_dip_sites.py`).

Standing words this plan does NOT move (CONTEXT section 5, [ADDED 2026-09-26 by MIX-LRT-SITE]): "The J site null of
record remains THE certificate"; "the certificate is geometric, not modal" is written only with its qualifier; "The DIP
half of L6 stays OPEN (unexplored)". Only the registrar can bracket any of these; this readout's words are new,
exploratory and named "MODAL (split-dip)", never "certified".

What the writer has seen before this plan (all of record, none new): CERT-SPLIT-DIP's registration and outcome (prog
L24958-L24972 and L25328-L25340: SD0 SIZE-OK 0 of 300, delta 0 0 of 15 (the unplanted single-category subsamples of math,
physics and economics at n 486 / 441), SD1 SENSITIVE 60 of 60 at delta 6, SD2 POS-OK 15 of 15 merged-category pairs,
F-SD 0 of 70); CERT-RESOLUTION (prog L20752-L20815, L20957ff; `experiment_results/cert_resolution/cert_resolution_sites.csv`
blob:6d83df50): the J hierarchical sets bareq512_s42 = {n00000006 Chemistry, n00000015 Engineering} (top family 14, 17
sites reached) and af_clean_s42 = 8 sites (n00000001, n00000005, n00000017, n00000018, n00000042, n00000045, n00000043,
n00000074), flat BH 0 / 70 and 12 / 69; MIX-LRT-SITE (the LR certifies every site, so it cannot discriminate); the
site-null CSVs' structural columns (depth, n, k, labels; bareq512_s42 depth-1 anchors n 314-907; af_clean_s42 root n 8,125
with children n 4,404 and 3,837); synthetic timings of `cert_split_dip.dip_site` on random Gaussian matrices (n 110 to
8,125; 0.04 to 13 s per site). No dip p of any tree site exists; none was computed.

## 1. Question

The J certificate of record is calibrated against the site's own moment-matched Gaussian and certifies separation, not
modes; the Gaussian-mixture LR / BIC half of L6 closed negative because the LR rejects every site. CERT-SPLIT-DIP built a
rule that tests bimodality on items NOT used to choose the axis, and showed on planted data that it keeps its size on
moment-matched and elongated unimodal clouds and finds planted 2-way shifts the J null misses; its consequence of record:
"a candidate supplementary certificate for data-driven 2-way sites, to be registered on G12's sites with multiplicity
control". Here the rule, unchanged, is applied to every site of the two trees of record, with CERT-RESOLUTION's
prefix-closed hierarchical BH. Q1: which sites of each tree are MODAL along their own split axis at per-family FDR q =
0.05? Q2: are bareq512_s42's two J-certified sites (Chemistry n00000006, Engineering n00000015) among them? Q3: how does
the MODAL set sit beside the J hierarchical set of the same tree (more, the same, fewer; overlap)?

## 2. Objects and hygiene

| tree | recipe | snapshot | sites (CSV of record, pinned by CERT-RESOLUTION) | slice | split word |
|---|---|---|---|---|---|
| bareq512_s42 | R512 | 20260909_212117_Headless_Run_Auto_ge | `experiment_results/promoted/site_null_bareq512_s42.csv`, 70 | first 512 of 4,096, unit | id-disjoint only (pool p2dca21ab5f4ef3ae) |
| af_clean_s42 | R256 | 20260917_201353_Headless_Run_Auto_ge | `experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv`, 69 | first 256, unit | content-closed (KNOWLEDGE section 1; built on the clean split of p2dca21ab5f4ef3ae) |

- SITES: the rows of each CSV, read by `cert_resolution.read_sites` (reps 300, feasibility OK, integral q_site x reps),
  located and pinned by `cert_resolution.locate` with CERT-RESOLUTION's TREES pins (CSV and the last record of
  `dag_snapshots.jsonl`); `cert_resolution.identity_check` must pass (else REFUSE; a failed precondition).
- MEMBERS: regionQueryIds(site) over the snapshot graph read from `snapshots.db` (the DFS union of queryIds over childIds
  that SeparationNullBySizeTest.kt uses and MIX-LRT-SITE transcribed); |members| == the CSV's n at EVERY site, else REFUSE.
  `snapshots_frozen.db` is not opened. The snapshot graph's parentIds and childIds equal the jsonl's last record at every
  site, else REFUSE (the families of record are the jsonl's).
- VECTORS: `embeddings_cache.db` through `embedder_guard.read_vectors` (the record's SQL join on distilled_text,
  big-endian float32, first `slice` floats, L2-normalised); every member must have a vector and every raw vector must be
  4,096 floats, else REFUSE. Rows of a site in ascending member-id order.
- EMBEDDER IDENTITY: `embedder_guard.guard` (record arithmetic, unchanged) over the tested sites of each tree, model
  qwen3-embedding:latest: min cos(mean member vector, snapshot vmfMu) >= 0.99 else REFUSE; the min is printed.
- POOL: p2dca21ab5f4ef3ae printed FIRST, "printed, not used" (its id file hashed by `pool_guard.compute_pool_id`; the
  dataset DB is not opened: no held-out item is read; MIX-LRT-SITE's pattern). Members are construction rows (TRAIN side).
- DBs: opened only through `pool_guard.open_ro` (non-empty -wal / -journal REFUSED; mode=ro&immutable=1); a process-wide
  connect guard admits nothing else. The sha256 of both DB files is printed before and after `--run` and must be equal.
- RULE 7 (CONTEXT rule 7, W1-W5): `--dry-run` and `--run` print and enforce a probe first: W1 an exclusive-open probe of
  embeddings_cache.db, snapshots.db, snapshots_frozen.db and their -wal / -shm (every file FREE), W2 the process list with
  PIDs (any foreign java, Gradle worker, construction, or tools/analysis / tools/chains python other than this process and
  its own workers REFUSES; a `--selftest` process is admitted), W4 >= 12 GB free physical memory. At most 3 worker
  processes (BLAS single-threaded each); more REFUSES. The DB files are backed up to E: before the run of record.
- S4: the two trees are never joined: no sum, difference, ratio or ranking of a count or share across R512 and R256; each
  tree is read in its own block.

## 3. Arms (per tree, per site i, 0-based CSV row; t = 0 bareq512_s42, 1 af_clean_s42)

- OBS (the readout): the split-dip rule on the site's member rows.
- NULL (the size gate at the site's own geometry): M = 10 draws per site from the J site null's own generator
  (withinNodeCloud: mean + sum_c g_c c / sqrt(n), unit-renormalised) in its exact-in-distribution eigen form (MIX-LRT-SITE
  ruling A6: mean + Z diag(s) V^T / sqrt(n) with C = U diag(s) V^T the thin SVD of the site's centred rows, Z iid N(0, 1)),
  draw m from `numpy.random.default_rng([202611073, t, i, m])`, n rows each; the rule on each draw. NULL-TREE replicate m
  = every site's draw m.
- PLANT (power at the site's own geometry; descriptive): one fresh 2-way plant per site at delta 6 (CERT-SPLIT-DIP's
  delta_dec) with `cert_planted.direction` / `halves` / `plant_rows` unchanged: u = direction(202611071000 + 1000 t + i -
  U_SEED0, dim = slice), halves(ids, 202611072000 + 1000 t + i - H_SEED0); the rule on the planted rows.
- J (beside; no computation of record beyond a reproduction): the CSV's q_site -> p = (k + 1) / 301 -> CERT-RESOLUTION's
  hierarchical BH, which must reproduce the recorded J sets above exactly, else REFUSE.

## 4. Statistic

- THE RULE, imported unchanged (`cert_split_dip.dip_site`, blob:1d46cd73 asserted; diptest 0.11.0, 4 files, sha256
  302edebf89c97588... = CERT-SPLIT-DIP's cache meta, asserted): R = 20 halvings A / B (seed int(sha256(name)) mod 2^32 + r),
  spherical k-means k = 2 on A (k-means++, 10 restarts, <= 100 iterations), u = c1 - c2, B projected on u, Hartigan's dip
  (tabulated p), p_site = min(1, 2 x median of the 20 p). Site names: "CDS|<tree>|<node_id>|OBS", "...|N<m>", "...|P6".
- FLAT BH at q = 0.05 over the tree's m sites (`cert_resolution.bh_cutoff`, p as exact Fractions of the float);
  Benjamini-Yekutieli count beside (`cert_resolution.by_q`), DESCRIPTIVE.
- HIERARCHICAL (prefix-closed) BH at per-family q = 0.05: `cert_resolution.site_structure` + `hierarchical_bh` unchanged
  (families keyed by the nearest site ancestor along parentIds[0]; TOP = sites with no site ancestor: bareq512_s42's 14
  anchors, af_clean_s42's root alone; a site enters its family's BH only when all its site ancestors are rejected). The
  MODAL set D_T = its rejected set. No tree-wide FDR is claimed (per-family level only; nesting dependence not shown).

## 5. Gates (failed preconditions REFUSE before any p; G0 is an outcome word)

- Preconditions (REFUSE, no outcome): pins (CSV, jsonl, the three imported modules, diptest), identity_check, members ==
  n, graph == jsonl structure, vectors complete at 4,096, the embedder guard, the J reproduction, the DB sha256 unchanged,
  W1 / W2 / W4, workers <= 3, a clean tracked script for `--run` (its LF blob equal to HEAD's).
- G0 (SIZE at the tree's own geometry): SIZE-OK iff the tree's NULL draws are p_site <= 0.05 at a rate <= 0.10 with the
  95% Clopper-Pearson upper bound <= 0.15 (CERT-SPLIT-DIP's SD0 rule; denominator 10 x m = 700 / 690); else
  ANTI-CONSERVATIVE, and every word of that tree reads NOT EVALUABLE (every line still printed).

## 6. Word rule (per tree; exhaustive and exclusive; the POINT decides)

Site words (the only words of record for a named site): (M1) in D_T: "MODAL (split-dip) at per-family FDR q = 0.05
(hierarchical BH over nested sites, <tree>, <recipe>; EXPLORATORY)"; (M2) in the flat BH set only: "split-dip BH at q =
0.05 over the tree's m sites (nesting not respected; EXPLORATORY)"; (M3) p_site <= 0.05 only: "split-dip p <= 0.05
(per-site, uncorrected; EXPLORATORY)"; otherwise none. A site never reached by the hierarchical BH is printed UNTESTED
(not "unimodal"). No site is called "not modal", "unimodal" or "unreal".

- W1 (Q1): NOT EVALUABLE iff G0 fails; else SOME iff |D_T| >= 1; else NONE-POWERED iff PLANT certifies (p <= 0.05) at
  >= 0.5 of the tree's m sites; else NONE-UNDERPOWERED.
- W2 (Q2, bareq512_s42 only): NOT EVALUABLE iff G0 fails; else BOTH iff n00000006 and n00000015 are in D_T; ONE (the
  site named) iff exactly one; NEITHER iff none.
- W3 (Q3, within one tree): NOT EVALUABLE iff G0 fails; else MORE iff |D_T| > |J_T|, SAME iff equal, FEWER iff smaller;
  the overlap |D_T and J_T| of |J_T| and the D-only sites (in D_T, not in J_T) printed beside.
- Readings (as the lead worded its outcomes; EXPLORATORY): W2 BOTH -> "modal support for both J-certified sites of
  bareq512_s42 (a candidate stronger certificate sentence; the registrar's)"; W1 NONE-POWERED -> "no site of <tree> is
  modal along its split axis at per-family q = 0.05 although the rule finds a planted delta-6 shift at most of its sites:
  consistent with 'the certificate is geometric, not modal' (still a qualifier, never a closure)"; W3 MORE -> "the
  split-dip finds more modal sites than the J hierarchical set holds (the J set is resolution-limited at 300 reps; a
  different question, not a correction of the J null)".

## 7. Support

- (a) Denominators: per tree m = 70 (bareq512_s42) / 69 (af_clean_s42) sites; TOP family 14 / 1; W2 the 2 named sites;
  G0 10 x m = 700 / 690 null draws; PLANT m. Sites are NESTED (a site's members include its descendants'), not
  independent units.
- (b) DEFF: G0 1 BY CONSTRUCTION under the null (independently seeded draws); the draws of one site share its moments, so
  the realised one-way ICC over sites (10 draws each) and DEFF = 1 + 9 ICC are printed beside, never deciding. Across
  sites: BH's positive-dependence assumption is not shown; BY is printed as the sensitivity.
- (c) n_eff: G0 700 / 690 (at DEFF 1).
- (d) SE at the per-site level 0.05: sqrt(0.05 x 0.95 / 700) = 0.00824 (690: 0.00830); CP upper at 0 of 700 = 1 -
  0.025^(1/700) = 0.00526.
- (e) MDE80: 2.8 x 0.00824 = 0.0231 above 0.05 (690: 0.0232); the bar 0.10 lies 0.05 above 0.05, beyond the MDE: G0
  SCOREABLE as a classification. PLANT share SE at 0.75 over 70 sites 0.052 (descriptive).
- (f) VERDICT LINE: W1-W3 are deterministic set readouts on the computed p (the rule is seeded; no sampling beyond the
  members) and SCOREABLE as such; their between-site dependence is BH's assumption, not a sampling SE; G0 SCOREABLE.
- (g) STRUCTURAL: every word is reachable. The dip p is continuous and reaches 0, so unlike the J p (floor 1/301) no
  family is resolution-limited: bareq512_s42's first TOP threshold is 0.05 / 14 = 0.00357 (2 x median <= 0.00357), af's
  root alone faces 0.05. NONE is reachable if the 2-means axis of A projects B unimodally at every TOP site (CERT-SPLIT-DIP
  delta 0: 0 of 15 single-category subsamples at n 486 were certified). Under the global null with independent sites,
  P(any hierarchical rejection in a replicate) <= 0.05 (the TOP family's BH), so P(>= 3 of 10 replicates) <= 0.0115.

## 8. Predictions (the writer's, before any dip p on a tree member; words by Brier, counts HELD iff the point is in the band)

- P1 G0 SIZE-OK on each tree, 0.95; NULL rate 0.00 [0.00, 0.02] on each.
- P2 NULL-TREE: at most 1 of the 10 replicates of each tree has >= 1 hierarchical rejection.
- P3 W2 (bareq512_s42): BOTH 0.20, ONE 0.45, NEITHER 0.35.
- P4 |D| bareq512_s42 3 [0, 10]. P5 |D| af_clean_s42 12 [3, 30]. P6 af_clean_s42's root n00000001 in D, 0.90.
- P7 PLANT certified share: bareq512_s42 0.75 [0.50, 0.95]; af_clean_s42 0.80 [0.55, 0.97].
- P8 W3: bareq512_s42 MORE 0.40 / SAME 0.20 / FEWER 0.40; af_clean_s42 MORE 0.60 / SAME 0.10 / FEWER 0.30.
- P9 overlap: af_clean_s42's 8 J sites, >= 6 in D (HELD iff the count is in [6, 8]).

## 9. Falsifier

F-DIP fires on a tree iff G0 reads ANTI-CONSERVATIVE on it OR >= 3 of its 10 NULL-TREE replicates have >= 1 hierarchical
rejection. It overturns, for that tree, the reading "a MODAL site has modal structure along its split axis that its own
moment-matched Gaussian lacks": D_T would then hold the rule's false positives at the real geometry, and no M1-M3 word of
that tree may be quoted.

## 10. What this readout will not show

A certificate (the J site null stays THE certificate; nothing here is registered); a tree-wide FDR; k > 2 modes or which
2-way split the tree declared (the axis is the data's 2-means axis on half A, not the tree's partition); that an
unselected site lacks modes (only that this rule at this n did not find them); anything across R512 and R256; the frozen,
o0_clean_s42 or af_bareq512_s42 trees; other embedders; held-out data; anything about a judge, board or profile.

## 11. Runner, run of record, reproduction, outputs

`tools/analysis/cert_dip_sites.py`: `--selftest` (synthetic and fixture DBs in a sandbox; every gate, word, prediction
and falsifier branch executed through the real entry points with known answers), `--mutants` (spec in the docstring;
every mutant must be KILLED), `--probe` (W1 / W2 / W4 only), `--dry-run` (reads the pool: pins, members, guards, task
counts, estimate; computes NO dip p), `--run [--workers <= 3] [--pilot N]` (selftest gate; cache `<out>/cache.jsonl`
with meta pinned at first launch, refused on mismatch; resumable; an exception is never cached), `--analyze` (from a
complete cache only, write-once mode x: `CERT_DIP_SITES_OUTCOME.txt`, `cert_dip_sites_sites.csv`; a partial cache writes
`*_partial.txt`, a pilot `*_PILOT.txt`; opens no DB). The run of record from the committed runner at a clean tree, outputs
under E:/TaxoArena_tmp/cert_dip_sites/record; a second full run into .../rerun must be bit-equal (every cached p and the
outcome and sites files byte-identical; timing only in the logs). Outputs never committed: backup
E:/TaxoArena_backup_2026-11-06_cert-dip-sites (record/, rerun/, the pre-run DB copies) with SHA256SUMS.txt. The POSTRUN
review and the registrar's record follow (benchzoom pattern of D-2026-11-02-1).

[P1 2026-11-07 (the engine-coder; insertion only): BUILD AND RUN OF RECORD. Runner `tools/analysis/cert_dip_sites.py`
committed d0408d27 (LF blob 6ae15e5d, sha256-lf16:2589f379665dba05), built to this plan unchanged; selftest 66 checks
PASS; mutants 46 / 46 KILLED (table in the runner's docstring). Rule-7 window 2026-11-07 about 04:08-04:15 +0100 (the suite ran after it): W1
every pool file FREE (snapshots_frozen.db -wal / -shm ABSENT) before and after each run; W2 only ollama serve / app (idle,
not pool readers) and the runner itself; W4 19.1-19.5 GB free; no git write under src/. Backup first: embeddings_cache.db
sha256 b0e88d3a6e207bc0..., snapshots.db 431e19fa9bb42e92..., copied to the backup's db_pre/ and equal. `--dry-run`:
identity PASS on both trees; members == CSV n at all 70 / 69 sites; embedder guard ADMIT, vmfMu min cos 0.9976
(bareq512_s42, n00000050) and 0.9990 (af_clean_s42, n00000175), median 0.9997 / 0.9999 (the record's 0.99 budget; not
1.0, so the vectors read today are the tree's to that budget only); J sets reproduced (2 / 8); 1,668 tasks; 0 dip calls.
`--run --workers 3` from the clean worktree ([CLEAN] HEAD d0408d27): 1,668 tasks in 129 s, 0 failed, both DB sha256
EQUAL before and after. Second full run into rerun/: every cached row byte-equal (1,668 / 1,668; the cache files differ
only in line order, the workers' completion order), outcome and sites CSV byte-identical: REPRODUCED (bit-equal). Outcome
sha256 2e9a962fc1be4ab4..., sites CSV 6511fd0afdfa11cd..., record cache 354ad4d8da1d8ecb...; backup SHA256SUMS.txt sha256
4111f3e3d82cde67... (16 files, sha256sum -c 16 / 16 OK). TaxoArena suite in the worktree: 569 tests, 0 failed, 2 skipped
(MrlRoutingTest.testMrlConfigDefaults, TraceEnvelopeUnwrapTest blank trace).
WORDS (EXPLORATORY). bareq512_s42 (R512): G0 SIZE-OK (0 of 700); NULL-TREE 0 of 10; per-site p <= 0.05 2 of 70, flat BH
1, hierarchical: TOP family 14, D = {n00000015 Engineering, p 1.4e-05}; Chemistry n00000006 p 0.326 (TOP rank 5); 55 of
70 UNTESTED; PLANT 64 of 70. W1 SOME; W2 ONE (n00000015); W3 FEWER (1 vs 2; overlap 1 of 2); F-DIP NOT FIRED.
af_clean_s42 (R256): G0 SIZE-OK (0 of 690); NULL-TREE 0 of 10; per-site 3 of 69, flat BH 3; hierarchical: D = {n00000001
root, p 0.00021; n00000004, p 0}; the other J sites (n00000005 and below) p 1; 64 of 69 UNTESTED; PLANT 69 of 69. W1 SOME;
W3 FEWER (2 vs 8; overlap 1 of 8); F-DIP NOT FIRED. Every one of the 1,390 NULL draws read p_site = 1 (so the ICC and DEFF
print NA: no variation). Predictions: P1 HELD (both), P2 HELD (both), P3 ONE (Brier 0.465), P4 HELD (1 in [0, 10]), P5
FAILED (2 below [3, 30]), P6 yes (Brier 0.010), P7 HELD on bareq512_s42 (0.914), FAILED on af_clean_s42 (1.000 above
0.97), P8 FEWER on both (Brier 0.560 / 0.860), P9 FAILED (1 of 8). Not a reading of record; the POSTRUN review and the
registrar decide what, if anything, is bracketed.]
