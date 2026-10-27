# READY review: RP06 CERT-REDRAW-R512 at 73e5a04 (adversarial reviewer, 2026-09-27, zero calls, no real-data statistic)

## VERDICT

**CERT-REDRAW-R512: NOT READY. No `--run` is licensed.**

**Merge: MERGEABLE by pathspec (`tools/analysis/cert_redraw_r512.py` only), as a tool.** It is a new file. `--run` refuses while `OPEN_RULINGS` is non-empty, and the base is byte-identical. Merging after the patch in R-1..R-4 is preferred, so that main never carries a blob that will not run.

Why NOT READY:
- **B1 BLOCKER. The registration has two open gaps and no ruling on either.** `grep -c "CERT-REDRAW" docs/judge_v2_program.md` = 2, counted over the whole file: the registrar's index line L21535 and the registration L21680. There is no bracket on O1 or O2.
  - Ruling them means a code patch (`P4_READING`, `OPEN_RULINGS = {}`), and the patch is a new blob. This READY cannot pin the blob that will run.
- **H1 HIGH. A mutant that changes the outcome survives the selftest.** X3 computes R2's p as k/300 in place of (k+1)/301 in `analyze()` L290, and the selftest does not kill it.
  - Under X3, every tested site with k = 0 rejects whatever its alpha, so structurally unreachable sites (Engineering) would be printed "also FWER 0.05".
  - That flips P4 and the R3 "beside" words. No check exercises a k = 0 site with n/N < 0.0664 through `analyze()`.
- **H2 HIGH. The R3 words of record for Engineering are decided by structure, not by the data, and the printed words hide this.** Engineering has n/N = 0.0600 / 0.0607 / 0.0613 on s42 / s137 / s2048, below the reach bar 0.0664 on every tree. So R2 cannot reject it at 300 reps.
  - The beside words would then print `not FWER 0.05`, which reads as a data outcome.
  - The registration's (g) requires "UNREACHABLE at 300 reps by construction (printed per site)". The R3 line must say that.

## PROCEDURE TO READY (in order)
1. **Registrar, pre-data bracket (insertion only)** on L21680-L21703:
   - **O1:** fringe-site identity is NOT COMPUTED. No readout among R1-R3, C1, C2, P1-P4 and F1 consumes it, and the member sets exist only in snapshots.db (a DB, contrary to HYGIENE). I confirmed that dag_snapshots.jsonl nodes carry only integer `directQueries` / `residualQueries` / `subtreeQueries`, with no member lists.
   - **O2:** a reading for P4. Recommended: (A) "at least one of {Chemistry, Engineering} rejected". That is the literal sense of "rejects a non-empty subset of X".
   - With the O2 bracket, **disclose** that Engineering is R2-unreachable on s42. P4 is therefore equivalent to "R2 on s42 rejects Chemistry" under (A); under (B) it is "Chemistry rejected and no other site rejected".
   - **Ratify the wording renderings:**
     - R3 "..." expanded literally ("... on bareq512_s42 not on either R512 re-draw"). A "but" is optional; that is the registrar's call.
     - "not FWER 0.05" becomes "not FWER 0.05 (UNREACHABLE at 300 reps, n/N < 0.0664)" for an unreachable site (H2).
     - "parent site" means the nearest site ancestor (inert: 0 multi-parent sites on all three trees).
     - The run prints the M-1 line below.
2. **Builder patch R-1..R-4** (worktree w0-rp06-cert-redraw):
   - R-1: set `P4_READING` to the ruled value and `OPEN_RULINGS = {}`.
   - R-2: add the H2 words and a check (st6) that an unreachable exhibit prints the UNREACHABLE form.
   - R-3: add selftest checks that kill X3, X5 and X11. If cheap, also add X1: a depth-3 site under a rejected grandparent and an unrejected parent is never tested.
   - R-4: add the M-1 print line.
   - Then re-run `--selftest` (all green, 18 + the new mutants killed) and `--dry-run`, and commit by path with the ancestry check.
3. **Re-review of the delta** (this reviewer or another). It pins the new blob with its LF and CRLF renderings, re-runs my mutants X1-X12, and checks the bracket text against `P4_READING`. The verdict becomes READY only then.
4. **Data steward** (condition before the run, MEDIUM D3): archive the untracked dimsweep2 s137 / s2048 `dag_snapshots.jsonl`, with a SHA256SUMS line, next to the s42 evidence copy. The pins make a missing file REFUSE rather than corrupt, but the run is not reproducible without them.
5. **Merge by path into main:** `git checkout w0-rp06-cert-redraw -- tools/analysis/cert_redraw_r512.py`, then `git commit -- tools/analysis/cert_redraw_r512.py`, then `git merge-base --is-ancestor <prev HEAD> HEAD`.
6. **Run from the MAIN checkout**, single-threaded (`OMP/MKL/OPENBLAS_NUM_THREADS=1`), one process: `python tools/analysis/cert_redraw_r512.py --run`.
   - It writes once to `experiment_results/cert_redraw_r512/`. The outputs go under the checkout that holds the script, so do not run from the worktree.
   - Then the post-run review. It carries the registration's STANDING condition for CERT-RES-SELFTEST-GAPS: recompute MC-MARGINAL and the E-lists in the sites CSV `words` column independently, because crL and raG stay open in the base.

## PER-CLAIM TABLE

| # | Builder claim | Verdict | Command / script | Mine vs claimed | Sev |
|---|---|---|---|---|---|
| 1 | Tip 73e5a04, parent 4f5e03d, ancestry ok, tree clean, 1 file | CONFIRMED | `git merge-base --is-ancestor 4f5e03d 73e5a04`; `git diff 4f5e03d HEAD --name-only \| wc -l` = 1; `git status --porcelain \| wc -l` = 0 | same | - |
| 2 | New script pins blob:56762cf4 / sha256-lf16:452aed5bc0e8a563 / sha256-crlf16:bb5c33e01016c244, LF working file | CONFIRMED | `git hash-object` = 56762cf485a8...; python sha256 of the LF / CRLF renderings; 0 CR bytes in the working file | same | - |
| 3 | Base cert_resolution.py unchanged: blob:dbe9425d / sha256-lf16:3e3fb1b91aa3d361 / sha256-crlf16:b0982ba75521b7d4 | CONFIRMED | `git rev-parse HEAD:` and `73e5a04:tools/analysis/cert_resolution.py`, plus `git hash-object` on main's and the worktree's working files: all dbe9425dc406... (the worktree working file is CRLF, and the LF pin matches) | same | - |
| 4 | The script refuses every mode on a wrong base | CONFIRMED | st0, and the builder's mutant no_base_pin KILLED (my re-run) | same | - |
| 5 | Selftest 8 checks / 0 failed; 18 of 18 own mutants killed | CONFIRMED | `python tools/analysis/cert_redraw_r512.py --selftest`, single-threaded, 60.7 s, exit 0 (log scratchpad/rv_rp06_selftest.log) | 8/0, 18/18 | - |
| 6 | Upstream crB and crK KILLED as source copies | CONFIRMED | same run: both KILLED by `gap_checks` on a mutated base copy | same | - |
| 7 | crL cannot matter here; raG not imported | CONFIRMED (scope) | `grep -n "render_outcome\|recipe_edge"` over the whole new file: 3 hits, all inside string literals, so no call. The registration's "crL, raG run first" is therefore met only by its STANDING alternative, which binds the post-run review (procedure step 6) | - | LOW |
| 8 | Dry-run: pins match; m 70 / 67 / 71; snapshots as registered; last records 18/158, 10/152, 13/160; identity PASS; 0 multi-parent sites | CONFIRMED | my independent script rv_rp06/indep.py (no base import; reads bytes, the CSV `n` and the jsonl structure; no q_site): sha256-lf of the CSVs ea0cb198... / 8bd6c8de... / a88d75ed..., dags 0bf29bbc... / 8da4e1ef... / ab36d2fc...; m, snapshot, iteration and nodes identical; multi-parent 0 | same, to the digit | - |
| 9 | Exhibits keep ids: Engineering n00000015, Chemistry n00000006, depth 1, on all trees | CONFIRMED | indep.py label lookup; no duplicate labels on any tree | same | - |
| 10 | Structural leg (g): N 8547 / 8547 / 8566; top family 14; reachable 7 / 7 / 6 | CONFIRMED | indep.py, with the exact integer test 20N <= 301n; top family = depth-1 sites on all three trees | same, including Biology on s42 at 0.06646, just above 0.066445 | - |
| 11 | Engineering unreachable by R2 on every tree; Chemistry reachable | CONFIRMED | indep.py: Engineering n 513 / 519 / 525 against a needed n >= 568 / 568 / 570; Chemistry 905 / 919 / 921 | same | feeds H2 |
| 12 | `--run` exits 2 with REFUSED open rulings and writes nothing | CONFIRMED | `--run` gives exit 2 with that message; `ls experiment_results/cert_redraw_r512` = no such dir in both checkouts | same | - |
| 13 | Support (d) SE 0.01258, (e) MDE 0.0352, DEFF 1 by construction | CONFIRMED | sqrt(0.05 x 0.95 / 300) = sqrt(0.000158333) = 0.012583; 2.80 x 0.012583 = 0.035232. DEFF source: independent MC reps per site (declared by construction, not measured; acceptable for DESCRIPTIVE-ONLY) | same | - |
| 14 | O1 is not needed by any readout | CONFIRMED | read R1-R3, C1, C2, P1-P4 and F1 at L21689-L21703: every one reads anchors by label or whole-tree sets; the jsonl has no member lists (node keys printed) | - | ruling owed (B1) |
| 15 | O2: two readings can disagree | CONFIRMED | a set with {Chemistry, other} gives A HELD and B FAILED (the builder's st6 scenarios 3 / 4 execute this) | - | ruling owed (B1) |
| 16 | Selftest pins the R2 / readout wiring | PARTLY | rv_rp06/mut.py: 12 reviewer mutants, each built as a source copy with the byte-identical base beside it, then `selftest()` called: **7 KILLED, 5 SURVIVED** (X1, X3, X5, X7, X11) | builder: 18/18 | H1 / D4 / D5 |
| 17 | R2 is a hierarchical ("top-down") FWER | PARTLY (vacuous at 300 reps) | the max n/N of any depth >= 2 site is 0.0622 (s42 n00000020) / 0.0593 / 0.0586, all below 0.0664. At 300 reps R2 is exactly a weighted Bonferroni over the 14 top-family sites; the parent gate never matters | - | M-1 MEDIUM |

## REVIEWER MUTANTS (rv_rp06/mut.py; log rv_rp06/mut.log)

| mutant | change | result | real-data impact |
|---|---|---|---|
| X1 | gate on "any site ancestor rejected" in place of "parent rejected" | SURVIVED | inert at 300 reps (no deep site reachable, #17); live under CERT-SEQ-REPS |
| X2 | alpha = q n_s / n_parent | KILLED (st2) | - |
| X3 | R2 p = k/300 | **SURVIVED** | **decisive:** a k = 0 unreachable site rejects, flipping P4 / R3 (H1) |
| X4 | R3 beside reads hier in place of R2 | KILLED (st6) | - |
| X5 | sites CSV `fwer_rejected` from the tested set | SURVIVED | wrong write-once CSV column (D4) |
| X6 | gate on tested in place of rejected | KILLED (st2) | - |
| X7 | dry-run reach line N over all sites | SURVIVED | display only; the dry-run figures were verified independently (#10) |
| X8 | instrument-check mismatch accepted | KILLED (st5, st6) | - |
| X9 | C1 / C2 labels swapped | KILLED (st6) | - |
| X10 | P3 sizes from the flat set | KILLED (st6) | - |
| X11 | sites CSV `alpha_s` = 0.05 | SURVIVED | wrong write-once CSV column (D5) |
| X12 | P4 (A) counts any rejection | KILLED (st6) | - |

## DEFECTS
- **B1 BLOCKER.** O1 and O2 are unruled, so no runnable blob exists. Fix: procedure steps 1-3.
- **H1 HIGH.** X3 survives. Fix: in st4 or st5, put a top site with k = 0 and n/N < 0.0664 through `analyze()` and assert it is tested and not rejected; also put the reachable twin through and assert it is rejected.
- **H2 HIGH.** Engineering's R2 status is structural, but it prints as the data word "not FWER 0.05". Fix: the R3 beside line and the outcome print "UNREACHABLE at 300 reps (n/N x.xxxx < 0.0664)" for any exhibit outside `fw["reachable"]`; add a selftest branch for it; the registrar ratifies the words. P4's prior (0.55) was set without this; disclose it in the O2 bracket.
- **M-1 MEDIUM (vacuity).** At 300 reps R2 cannot reach any site below the top family, so the "top-down" word overstates the procedure. Fix: print "R2 at 300 reps reduces to weighted Bonferroni over the <m_top> top-family sites (no deeper site reachable)", computed per tree from `fw["reachable"]` against the depth or top set.
- **M-2 MEDIUM (registered weights, forward).** The CSV `n` (= the jsonl `subtreeQueries`, 0 mismatches over the 208 sites) is **not nested**: child-site sums exceed the parent's n at 15 / 15 / 19 parents (for example s42 Physics 873 against children 532 + 352 = 884). Meinshausen's bound is 0.05 x (max antichain weight) / N = 0.05060 / 0.05063 / 0.05068 (rv_rp06/anti.py). This is inert here, since only the top family is reachable (top weights sum to exactly 1). It binds CERT-SEQ-REPS (RP50): renormalise the child weights per parent, or word the bound, before more reps are registered.
- **D3 MEDIUM (durability).** All three parent maps are untracked in main (`git ls-files` count 0 of 3; `git status --porcelain --ignored` shows `??`). s42 has an evidence copy under TaxoArena_data; s137 and s2048 have none. Fix: the steward archives them with SHA256SUMS before the run.
- **D4 / D5 MEDIUM.** The sites CSV's `fwer_rejected` and `alpha_s` columns are unpinned by any check (X5, X11). Fix: in st5, assert the row values for the fixture (C6 and E9 rejected, alpha 0.016667, L1 false).
- **M-3 MEDIUM (soft guard; kept at MEDIUM because the check is new).** INSTRUMENT CHECK MISMATCH only warns and then prints C1 / C2 / R3 / P / F1. Fix: make R3, C1, C2, P1-P4 and F1 VOID on a mismatch, or refuse, with the registrar's assent.
- **L-1 LOW.** The deviation in form (a new file importing the base, rather than an edited base) is accepted: it is the "new blob" the registration asks for, and it keeps the base's four trees byte-inert.
- **L-2 LOW.** The printed (g) rewords the registration's "a top-family BH rejection needs k = 0 when m >= 8" as "a rank-1 BH rejection ...". The builder's form is the correct one (at r* >= 2 a k = 1 site can be rejected in a family of 14), so the registrar should note it.
- **L-3 LOW.** The R3 "neither" string is grammatically bare. That is the registrar's call.

## HYGIENE / CAP
- **No DB opened.** The new file has no sqlite import (grep over the whole file), and neither does the base. My reads were the three site-null CSVs (column `n` and structure only; I read no q_site or k value) and the three dag jsonl files.
- **No real-data statistic** was computed by me or printed by the dry-run: the builder's STAT_CALLS guard stayed at 0.
- **Machine cap:** single-threaded python only, one process at a time, BLAS threads 1, no JVM, no construction, no judge or Azure call.
- SuperGPQA is not touched (N/A to this instrument).

## PINS OF RECORD (LF rendering; CRLF beside, as the worktree base file is CRLF)
- `tools/analysis/cert_redraw_r512.py` @ 73e5a04: blob:56762cf485a820a66038b32a8bff75e9a56b5d91 / sha256-lf16:452aed5bc0e8a563 / sha256-crlf16:bb5c33e01016c244. This blob is NOT the run blob (B1).
- `tools/analysis/cert_resolution.py`: blob:dbe9425dc406edcd41661a6df4e00d33b44299b6 / sha256-lf16:3e3fb1b91aa3d361 / sha256-crlf16:b0982ba75521b7d4.
- Inputs (sha256-lf16):
  - site_null_bareq512_s42.csv ea0cb19865f63036; s137 8bd6c8de94a6de28; s2048 a88d75edc5be5d5b.
  - dags: s42 0bf29bbc8c9b10b2; s137 8da4e1ef92f72de1; s2048 ab36d2fcc255a35a.

Scripts and logs: C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/rv_rp06/ (indep.py, anti.py, nest.py, mut.py, mut.log) and ../rv_rp06_selftest.log.
