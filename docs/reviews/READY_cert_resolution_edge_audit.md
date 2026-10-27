# READY review: CERT-RESOLUTION and RECORD-RECIPE-EDGE-AUDIT (2026-09-26, adversarial reviewer; zero calls)

## Verdict

**READY, both instruments. MERGEABLE by path, 2 files only:**
- `tools/analysis/cert_resolution.py`
- `tools/analysis/recipe_edge_audit.py`

Both come from branch `cert-resolution`, tip add344f532c8da6432d328df367b3a54a9c13ed0.

Every registered criterion, prediction, output column and exhibit word reproduces in the code:
- CERT-RESOLUTION: programme L20752-L20815 (6402b0a).
- RECORD-RECIPE-EDGE-AUDIT: programme L20817-L20844 (6402b0a).
- Rulings A1-A4, A6 and the two minors: L20921-L20955 (23f9f00).
- RC1 and RC2 are present on the pinned blobs.

I recomputed flat BH, BY, the hierarchical BH, top-family size, the Clopper-Pearson (CP) interval and the E1-E4 / MC-MARGINAL words with my own code. I ran them on 1,600 synthetic k-vectors over the four REAL parent maps and got **0 mismatches** against the builder's code. CP agrees with scipy to 2.7e-14 on every k in 0..300.

Each hierarchical leg is reachable at 300 reps on the real family sizes. The top family has 14 sites on bareq512_s42, o0_clean_s42 and frozen, and 1 site (the root) on af_clean_s42. Every other family has at most 4 sites. Audit C1 is non-vacuous.

Four of my 8 mutants SURVIVE both selftests (D1-D4 below, MEDIUM or LOW). In each case I showed by execution that the pinned code is correct. What is missing is a selftest assertion, not correct behaviour. Because the blobs are pinned, a regression cannot enter before the run. The post-run review must recompute the four quantities concerned (section 5).

**Process disclosure (mine):** during this review I ran `taskkill //F //IM python.exe` once, to stop my own runaway fixture script.
- That command kills EVERY python.exe on the machine, not only mine.
- `tasklist` about 4 minutes earlier showed no python process.
- I cannot prove that no foreign process was running at that moment. Any builder whose python job died around 03:3x local time on 2026-09-26 should re-run it.
- After that I killed only by PID.

## 1. Identity (hash kinds named; the LF rendering is of record)

| object | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| tools/analysis/cert_resolution.py @ add344f | blob:dbe9425dc406edcd41661a6df4e00d33b44299b6 | 3e3fb1b91aa3d361 | b0982ba75521b7d4 |
| tools/analysis/recipe_edge_audit.py @ add344f | blob:09369edb4db47be2d85924fee35f1055ea31990e | 2a73dedca0eb9749 | d21a7696e46c3b77 |

- The worktree files are LF, so their sha256 equals the lf16.
- The main checkout has core.autocrlf=true, so after the merge its working files will be CRLF and must read sha256 = the crlf16 above.
- Commands:
  - `git hash-object <f>` = `git rev-parse add344f:<f>`
  - a python sha256 over the bytes with CRLF normalised to LF, then re-expanded to CRLF
- Branch scope, proved by count: `git diff --name-only 6402b0a add344f | wc -l` = 2 (the two scripts). `git diff --stat f31937c add344f` gives +68/-26 in the same 2 files.
- Main at 23f9f00 tracks neither path (`git ls-files ... | wc -l` = 0), and `git diff --name-only 6402b0a HEAD -- tools/ | wc -l` = 0.

## 2. Per-claim table

| # | claim | command / script | got vs claimed | status | sev |
|---|---|---|---|---|---|
| 1 | Selftests green on the READY blobs | `python tools/analysis/cert_resolution.py --selftest`; same for the audit (OMP_NUM_THREADS=1); logs in scratchpad `review_certres/{cr,ra}_selftest.log` | CR 11/0, 20/20 mutants killed; audit 8/0, 15/15 killed. Byte-identical to the builder's `*_add344f.log` apart from their 4-line header and exit-code footer | CONFIRMED | - |
| 2 | Dry-runs compute 0 statistics, write nothing, and print the pins | `--dry-run` on both (logs `review_certres/{cr,ra}_dry.log`); `ls experiment_results/{cert_resolution,recipe_edge_audit}` in the worktree and main | both end "0 statistics evaluated on real rows"; both output dirs absent in both checkouts; logs equal the builder's | CONFIRMED | - |
| 3 | Input pins = registration (4 CSVs, 4 jsonl, metrics, proposals, build.out) | own python over the main-checkout files (git blob of the LF bytes, lf16, crlf16) | all 11 equal the registered blob / lf16 / crlf16 prefixes. The scripts gate on the FULL LF sha256, and st0 asserts prefix = registration | CONFIRMED | - |
| 4 | k = round(q_site x 300); p = (k+1)/301; assert reps 300, feasibility OK, off-integer <= 0.016 | code L236-L246; st4; dry-run "PASS on all rows" on 265 rows | as registered. The CSV's child-count k is used only by identity (A1). RC1 header line is present and asserted in st8 | CONFIRMED | - |
| 5 | CP exact two-sided 95% | own loop k = 0..300 against scipy 1.14.1 `beta.ppf` | max abs diff 2.70e-14. k=0 upper 0.012221 = 1-0.025^(1/300). k=7 0.0475, k=8 0.0519 | CONFIRMED | - |
| 6 | Flat BH step-up q = 0.05, per tree; BY with c(m) | independent `bh()` in `review_certres/indep.py` (sort, largest r with p_(r) <= rq/m) | 1,600 fixtures, 0 set mismatches (1,236 non-empty) | CONFIRMED | - |
| 7 | Hierarchical BH: family = nearest site ancestor along parentIds[0]; TOP = no site ancestor; a family runs only after its key is rejected; prefix-closed | independent recursive implementation over the REAL last-record parent maps with synthetic k | 0 mismatches over 1,600 fixtures (1,176 non-empty hierarchical sets); top-family size agrees on every fixture. A3 (multi-parent) is inert: 0 multi-parent sites on all four trees (dry-run) | CONFIRMED | - |
| 8 | MC-MARGINAL as ruled in A4: cutoff r* x q / m of the granting procedure (family for E1, flat for E2), strictly less than 1/301 below | independent `words()` in indep.py compared on every site of every fixture | 0 mismatches; 4,183 MC tags exercised. Equality ties (<= vs <) are impossible at these m (301 = 7 x 43; shown by divisibility), so the strictness never binds on real data | CONFIRMED | - |
| 9 | E1-E4 words literal; E2 literal (minor ruling); E4 = CP contains 0.05; E3 excludes the flat and hierarchical sets | st7 plus my execution on the real bareq512 map (6 deep k=0 sites: flat 6, hier 0, E2 6, E3 64, E3 ∩ flat = 0) | as registered | CONFIRMED (no test guard for E3: D2) | - |
| 10 | Reachability printout = the registration's arithmetic | dry-run text; st6; own check `ceil(m/15.05)` = `ceil(20m/301)` = 5/5/4/5 | min p 0.003322; Holm impossible at m >= 16; flat BH needs 5/5/4/5 sites at k = 0; a family of <= 15 can reject one k = 0 site; kmax 7 | CONFIRMED | - |
| 11 | Support arithmetic (rule 8) | own: SE sqrt(0.05 x 0.95 / 300); MDE 2.80 SE; binom.cdf(7, 300, p) | SE 0.012583 (reg. 0.01258). MDE 0.035233 (reg. 0.0352). P(k<=7 \| p=0.0185) = 0.805 >= 0.8; at p=0.019 it is 0.786. DEFF 1 is declared by construction (independent parametric null reps), with no transported DEFF. C1/C2/C3 are deterministic set readouts: SCOREABLE; margins DESCRIPTIVE-ONLY. The Support section is non-vacuous | CONFIRMED | - |
| 12 | R256 never compared with R512 | read render_outcome L554-L685 | per-tree blocks only; no cross-tree difference, ratio or rank; the header prints the prohibition | CONFIRMED | - |
| 13 | Parent-map identity (script check: id, isLeaf, depth, non-bridge child count) | dry-run; plus mine beyond the script: each tree's last jsonl record against `snapshots.db` `graph` of the CSV's snapshot_id, opened `mode=ro&immutable=1` (WAL 0 bytes; sha256-16 of snapshots.db 390c313e5a40e0a7 and mtime 2026-09-23 04:34:26.59 unchanged after) | the script's check PASSES on 70/69/60/66. Mine: node-id sets equal (158/151/145/154) and parentIds and childIds identical for every node on all four trees | CONFIRMED | - |
| 14 | "Only the last jsonl record" | `review_certres/tree_struct.py`: records, iteration sequence, id reuse | contiguous records 1..18 / 1..14 / 1..15 / 1..10; 0 ids reused; last record = saved snapshot (row 13). The rule does NOT bite on the pinned files. It would bite on an appended or resumed jsonl, or a post-loop edit before the save. The full-sha pin fixes the content; iteration and node count are also asserted for bareq512_s42 (18/158) and frozen (10/154), but not for af_clean_s42 / o0_clean_s42 (D6) | CONFIRMED | LOW |
| 15 | The evidence-archive fallback cannot admit a wrong file | code `locate` (both scripts); archive `grep -v SHA256SUMS SHA256SUMS \| sha256sum -c -` = 11/11 OK (SHA256SUMS has 12 lines and lists itself, as noted); dry-run with `--data-root <worktree>` only | a candidate is admitted ONLY if its full LF sha256 equals the pin; the checkout is tried before the archive; mismatches print WARN and are skipped. Executed: the bareq512 jsonl, metrics, proposals and build.out load from the archive with the pinned hashes; af_clean's jsonl (no archive copy) REFUSES. A wrong file needs a SHA-256 collision | CONFIRMED | - |
| 16 | Audit bar = 0.0145 at build a900da09, with no size-dependent substitute | `git grep proposalSeparationBar\|barFor a900da09 -- src/main`; `git show a900da09:.../AdaptiveBar.kt`, `TaxonomySplitter.kt` L147-L167, L285-L294; build.out L15; `grep -c ADAPTIVE-BAR build.out` = 0; config.toml L43 | every gate (splitter min-pair L294, residual viability L98, marginalEps fallback L167, merger L951/L1016) reads `barFor()`. That returns the global bar when `adaptiveBars` is empty. build.out L15 has `adaptiveBarFile=null`, `marginalEps=null`, `proposalSeparationBar=0.0145`; the splitter comment reads "One flat bar for every proposal, regardless of node size". **The READY records the effective bar = 0.0145**, as the registration requires | CONFIRMED | - |
| 17 | Late-born = STABLE-FROM (A6); first-equal descriptive; no refusal; disagreements printed | code `audit` L328-L352, `render_outcome`; st1; own mutant | index 1 (stable-from) decides; `first_equal_decides` is KILLED; the disagreement list prints whether empty or not; columns split_iter_first_equal / late_born_first_equal are added | CONFIRMED | - |
| 18 | Audit preconditions: 18 records, 158/87 = metrics, first quiet 8, 70 sites, 10 certified, proposals header | dry-run; mine: record vs iteration_metrics node and leaf counts for all 18 iterations | 0 of 18 mismatches (nodes 42, 85, 134, 148, 150, 152, 154, 154, 156 x4, 158 x6) | CONFIRMED | - |
| 19 | Audit C1 reachable (non-vacuous) | mine, a boolean only (no cert status, no q_site read): does any CSV site's non-bridge child set change at iteration >= 9? | True, so at least one of the 70 sites is late-born. Whether it is certified decides C1; both outcomes are possible | CONFIRMED | - |
| 20 | CERT-RESOLUTION C1 reachable at 300 reps | family sizes from the dry-run parent maps (tree_struct.py); no q_site read | bareq512_s42 m_top = 14 (all depth-1 anchors); the other families are at most 2. One anchor at k = 0 is enough (1/301 = 0.003322 <= 0.05/14 = 0.003571). C1 can come out either way. Structural corollary, not a defect: a top-family rejection at r* = 1 has margin 0.000249 < 1/301, so it is necessarily MC-MARGINAL. Same for o0_clean_s42 and frozen (m_top 14; families <= 4). af_clean_s42's top family is the root alone (reject iff its k <= 14) | CONFIRMED | - |
| 21 | Leakage: the brief's 0/70, 12/69, 0/66 are not re-derived as "confirmation" | `grep -n -i "confirm\|replicat\|reproduc"` = 2 lines only, P1 "(reproduction, not a test)" (L638) and F2 (L684); C2 lines carry " POST-HOC-SEEN" for the three seen trees | the flat counts appear only as C2 (tagged), P1 (a reproduction) and F2 (an instrument check), as registered. E2 exhibit words carry no POST-HOC tag (D5) | CONFIRMED | LOW |
| 22 | No DB opened; no writes outside write-once outputs | `grep -c -E "sqlite3\|\.connect\("` = 0 in both scripts; every `open(..., "w")` is under a selftest tempdir or in `run` with mode "x" | as claimed; "pool: none (no DB opened)" is printed first | CONFIRMED | - |
| 23 | scipy dependency | `python -c "import scipy..."` in the main checkout's python | scipy 1.14.1, numpy 1.26.3, Python 3.11.1 | CONFIRMED | - |

## 3. Reviewer mutants (copies under scratchpad `review_certres/mut/`, each run with `--selftest`)

| mutant | change | result |
|---|---|---|
| crC_family_key_immediate_parent | family key = parentIds[0] even when it is not a site | KILLED (st3, st8) |
| crD_k_floor_not_round | `k = int(x)` instead of `round` | KILLED (st8) |
| raH_birth_last_record | birth = last record containing the id | KILLED (st1, st1b) |
| raI_P2_counts_certified_only | P2 counts only certified late-born sites | KILLED (st5) |
| crB_mc_uses_flat_cutoff_for_E1 | MC-MARGINAL measured against the flat cutoff for an E1 site that is also flat-rejected (violates A4) | **SURVIVED** (D1) |
| crK_E3_includes_flat | the E3 list also takes flat-rejected sites | **SURVIVED** (D2) |
| crL_P1_ge_not_eq | P1 scored with `>=` instead of `==` | **SURVIVED** (D3) |
| raG_bar_ratio_swapped | bar_ratio and p95_ratio swapped in `audit` | **SURVIVED** (D4) |

For each survivor, the PINNED code is correct by execution:
- crB: row 8 (indep.py, 0 mismatches on MC tags).
- crK: row 9 (E3 ∩ flat = 0).
- crL: synthetic render with bareq512 flat = 1 gives "P1 FAILED" and "F2 FIRES".
- raG: `audit()` on a fixture with observed_sep 0.029 and p95 0.020 gives bar_ratio 2 and p95_ratio 29/20.

## 4. Defects

- **D1 (MEDIUM, test gap).** No selftest reaches `analyze_tree`'s choice of cutoff for the MC-MARGINAL words (L484); st7 tests `words_for` with a given threshold only.
  - Fix: an st8-style fixture with a site rejected in both the family (m_f 2) and the flat set, at different cutoffs, asserting the E1 word with and without MC.
- **D2 (LOW-MEDIUM, test gap).** No selftest asserts the E-lists that `analyze_tree` builds (L505-L508).
  - Fix: assert e1, e2 and e3 on the st8 fixture (E3 must exclude flat-rejected sites).
- **D3 (LOW-MEDIUM, test gap).** P1 scoring is covered only by an all-reproduce scenario and an all-differ scenario in st9, so `>=` survives.
  - Fix: add a scenario with bareq512 flat 1 or af_clean 13 expecting P1 FAILED and F2 FIRES.
- **D4 (MEDIUM, test gap).** st3 tests `ratio()`, but no selftest asserts that `audit` assigns observed_sep / 0.0145 to bar_ratio and observed_sep / p95 to p95_ratio. P3 and P4 are scored from bar_ratio.
  - Fix: assert both on st1b's fixture (site A: 0.0152 / 0.0145 = 152/145 and 0.0152 / 0.012).
- **D5 (LOW).** E2 words for the three POST-HOC-SEEN trees carry no post-hoc tag in the exhibit lists (only the C2 criterion lines do). The minor ruling fixes E2 as literal, so no change is required. The outcome record should say that the af_clean_s42 E2 list is the post-hoc-seen set.
- **D6 (LOW).** CERT-RESOLUTION asserts the last-record iteration and node count only for bareq512_s42 and frozen (last_iter None for the two R256 redraws). They are covered by the full-sha pin and the identity check, and I verified them against snapshots.db (row 13).
  - Fix if ever re-pinned: add 14/151 and 15/145.
- **D7 (LOW, durability).** The af_clean_s42 and o0_clean_s42 dag_snapshots.jsonl files are untracked, and the evidence archive has no copy of them. If they are lost, the run REFUSES (fail-closed).
  - Recommendation (data-steward): archive them with SHA256SUMS beside the bareq512 set.
- **D8 (LOW, cosmetic, already recorded).** SHA256SUMS lists itself; exclude that line before `sha256sum -c`.

None of D1-D8 changes a number the run writes. D1-D4 are selftest follow-ups (a CERT-RESOLUTION-SELFTEST-GAPS item). They do not block, because the blobs are pinned and the post-run review recomputes these quantities (section 5).

## 5. Merge and run procedure (main checkout Z:\FAC\TUBerlin\THESIS\TaxoArena)

1. Preconditions:
   - `git ls-files tools/analysis/cert_resolution.py tools/analysis/recipe_edge_audit.py | wc -l` = 0.
   - `git diff --cached --name-only | wc -l` = 0, or only paths you own.
   - `git merge-base --is-ancestor 6402b0a HEAD` succeeds.
   - `experiment_results/cert_resolution/` and `experiment_results/recipe_edge_audit/` do not exist.
   - No foreign heavy process (the author's cap: one python process, OMP_NUM_THREADS=1).
2. `git checkout add344f532c8da6432d328df367b3a54a9c13ed0 -- tools/analysis/cert_resolution.py tools/analysis/recipe_edge_audit.py`
3. `git commit -m "<msg>" -- tools/analysis/cert_resolution.py tools/analysis/recipe_edge_audit.py` (pathspec only).
4. Verify the merge:
   - `git rev-parse HEAD:tools/analysis/cert_resolution.py` = dbe9425dc406edcd41661a6df4e00d33b44299b6.
   - `git rev-parse HEAD:tools/analysis/recipe_edge_audit.py` = 09369edb4db47be2d85924fee35f1055ea31990e.
   - `git diff --name-only HEAD~1 HEAD | wc -l` = 2.
   - `git merge-base --is-ancestor <pre-merge HEAD> HEAD` succeeds.
   - Working files (CRLF) have sha256 prefix b0982ba75521b7d4 / d21a7696e46c3b77.
   - The scripts' own identity line prints blob:dbe9425d / sha256-lf16:3e3fb1b91aa3d361 and blob:09369edb / sha256-lf16:2a73dedca0eb9749.
5. From the main checkout, with `OMP_NUM_THREADS=1`:
   - `python tools/analysis/cert_resolution.py --dry-run` must end "0 statistics evaluated on real rows". The data root is main; the bareq512 jsonl comes from main or the archive. Every pin must print equal to section 2 row 3.
   - `python tools/analysis/recipe_edge_audit.py --dry-run` must also end "0 statistics evaluated on real rows".
6. Run (the in-process selftests take about 15 s each and must be green, or the script refuses):
   - `python tools/analysis/cert_resolution.py --run`
   - `python tools/analysis/recipe_edge_audit.py --run`
7. Outcome paths (write-once, mode "x"):
   - `experiment_results/cert_resolution/cert_resolution_outcome.txt`
   - `experiment_results/cert_resolution/cert_resolution_sites.csv` (265 rows + header; leading `tree` column)
   - `experiment_results/recipe_edge_audit/recipe_edge_audit_outcome.txt`
   - `experiment_results/recipe_edge_audit/recipe_edge_audit_sites.csv` (70 rows + header)
8. The post-run review must recompute from the output CSVs, independently:
   - the flat, BY and hierarchical sets with m_f per family (D1-D3);
   - MC-MARGINAL against the granting cutoff (D1);
   - E1 / E2 / E3 membership (D2);
   - the P1 equality (D3);
   - bar_ratio = observed_sep / 0.0145 and p95_ratio from the site-null CSV (D4);
   - late-born by stable-from from the 18 records.
   It must also state that the E1 lists of the three R256 trees are never set against the R512 list.

## 6. Scratch evidence (session scratchpad `review_certres/`)

- `cr_selftest.log`, `ra_selftest.log`, `cr_dry.log`, `ra_dry.log`
- `indep.py`: the independent BH / BY / hierarchical / CP / words recompute
- `tree_struct.py`: family sizes, records, id reuse
- `mut/*.py` and `mut/*.log`: the 8 reviewer mutants

The worktree was left clean at add344f. I removed the two `__pycache__/*.pyc` files my imports created (gitignored), and `git status --short | wc -l` = 0.
