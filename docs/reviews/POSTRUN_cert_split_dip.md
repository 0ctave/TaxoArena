# POSTRUN review: CERT-SPLIT-DIP (+ SI-NULL-TRIAD joint launch), operator run of 2026-10-08

Reviewer: adversarial-reviewer, 2026-10-08, main 160bc01a. Prior review: READY_cert_split_dip.md (READY, C1-C4).
Zero calls. Read-only: the two snapshots.db files opened `mode=ro&immutable=1`; no other DB opened; nothing written
outside this file.

## Verdict

- **CERT-SPLIT-DIP: NO OUTCOME. The run is VALID as a FAILED PRECONDITION and is not an outcome.** The `--dry-run`
  refused at G12/P2, and nothing after it ran: no `--run` and no `--analyze`. The output dir holds only
  `run_operator.log` (1 file, counted by `ls | wc -l`). No word of record exists, and none may be written.
- **SI-NULL-TRIAD: NO OUTCOME** (it never ran). It is still NOT READY (B1), as the READY review and the registrar (c5f23e7a) recorded.
- **The operator's diagnosis is half REFUTED.** The snapshot is NOT missing from the data of record. It is in
  `.claude/worktrees/rp12-r2-run/snapshots.db` (exact-id count 1). Its buildStamp equals the pointer entry
  `B0/mmlu_pro_lb` and passes all three check_stamp keys, and 60 of 60 G12 site ids are nodes of it. The operator's
  probe of that DB returned `[]` because it searched column names containing "snapshot", but the table is `snapshots`
  and the key column is `id`. That is a false absence.
- **The root cause is a READY-gate defect (D1).** The reviewed run command (READY L44-L52) has no `--data-root`. The
  tool defaults to the repo root. Every prior cert_* run that reads snapshot 20261001_094311 used the rp12-r2-run
  data root: POSTRUN_cert_pc_k2_known L4, POSTRUN_cert_pc_size L3, prog L23640. The READY review exercised G12 only
  on a fixture snapshots.db that it seeded with G12's node ids (`--selftest-io`). It never ran `--dry-run` on the
  real data root, so the deciding refusal path stayed unread.

## Per-claim table (deciding claims only)

| # | Claim (operator) | Status | My number vs claimed | Sev |
|---|---|---|---|---|
| 1 | Refused at step 4 (dry-run), nothing ran, zero calls, no outcome or HELD files | CONFIRMED | log: `[G12] REFUSED: P2 ...`, `dry-run exit=1`. Output dir has 1 file (the log). No HELD_not_of_record/ | - |
| 2 | Script blob 1d46cd73 = READY pin | CONFIRMED | `git hash-object` 1d46cd733e87 (LF; 0 CR bytes, so the CRLF rendering is the same). Same blob at 397ebd77. The c5f23e7a by-path merge touches the file (count 2). 397ebd77 is NOT an ancestor of main (by-path merge, blob-equal) | LOW |
| 3 | The 4 pins print OK, D0 max abs diff 1.34e-08, 6993 TRAIN rows | CONFIRMED (from the log) | as claimed. The check read main's embeddings_cache.db. Under a rp12-r2-run data root it must re-print | - |
| 4 | Snapshot 20261001_094311 is not in main's snapshots.db | CONFIRMED | main: 216 rows, exact 0, LIKE '20261001_0943%' 0 | - |
| 5 | "A probe also failed to find it in rp12-r2-run/snapshots.db" | **REFUTED** | rp12-r2-run: 234 rows, exact 1. Stamp == pointer: True. poolId / enginePoolSha256Lf / namespacesLoaded all OK. 135 nodes, root depth 0. G12 sites in it: 60/60 | HIGH |
| 6 | Support arithmetic: SE 0.0685, MDE80 0.192 (DEFF 1.5, n_eff 40); SIZE SE 0.0126, MDE 0.035 | CONFIRMED | sqrt(.1875/40)=0.068465, x2.8=0.191703; sqrt(.0475/300)=0.012583, x2.8=0.035233. These are the registration's pre-run figures only: no run, so no realised DEFF | - |
| 7 | busy.ps1 exit 1 before the dry-run | CONFIRMED (log line `busy exit=1`) | - | - |
| 8 | Backup E:/TaxoArena_backup_20261008_cert_split_dip_refused | CONFIRMED | SHA256SUMS: 1 line, db854741924b6099.... `sha256sum` and `cmp` against the run copy are equal | - |
| 9 | READY C4 (category-level dependence) and C3 (seed overlap) disclosures | UNDETERMINED (not reached) | owed at the post-run of an actual `--run`. They do not lapse | - |

## Defects (each with a fix)

- **D1 (HIGH, READY gate; returns to the registrar/reviewer).** The reviewed run command omits the data root of record.
  Fix: amend the run command to `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/rp12-r2-run` on all
  three modes (dry-run, run, analyze), matching POSTRUN_cert_pc_k2_known / cert_pc_size. The dry-run must then
  re-print, from that root, the 4 pins, the D0 diff (tolerance 1e-6) and the 6993 IDENTITY count, because the
  embeddings cache moves with the root. The G12 line must print `blob 21f110af OK; snapshot 20261001_094311...`. The
  G12_sites.csv blob is 21f110af in both main and rp12-r2-run, so the CSV does not depend on the root. This is an
  operational flag, not a code change: no delta code review is needed. The registrar records the ruling as a bracket.
- **D2 (MEDIUM, operator evidence).** The absence in rp12-r2-run was asserted from a column-name probe (check 10).
  Fix: prove an absence with `SELECT count(*) FROM snapshots WHERE id=?` and report the count.
- **D3 (LOW, READY gate).** The READY review's commands list has no real-root `--dry-run`. Its `--selftest-io` fixture
  seeds G12's node ids, so the fixture can never fail P2. Fix: a READY for any tool that resolves a snapshot through
  a pointer prints the real-root `--dry-run` G12 line before the verdict.
- **D4 (LOW, my own process; disclosed).** busy.ps1 printed exit 1 at the end of my wait loop. A peer process
  (PID 30092, a synthetic `benchzoom` numpy script that opens no TaxoArena DB) matched the guard before my few-second
  `mode=ro&immutable=1` read of the two snapshots.db files. My re-check after the read printed busy=0. No construction
  or site null was running (java: none). The read wrote nothing, and it cannot affect a peer.
- C1 stands for the eventual run: there is no `--dip-only` path, so SI_NULL_TRIAD_* goes to `HELD_not_of_record/`
  before the backup.

## Commands (all read-only)

```
cat experiment_results/cert_split_dip/run_operator.log; ls experiment_results/cert_split_dip | wc -l       # refusal; 1 file
sha256sum + cmp run_operator.log vs E:/TaxoArena_backup_20261008_cert_split_dip_refused/; cat SHA256SUMS.txt
git hash-object tools/analysis/cert_split_dip.py; grep -c $'\r' ...; git show 397ebd77:<path> | git hash-object --stdin  # 1d46cd73 x2; 0
git merge-base --is-ancestor 397ebd77 HEAD   # rc 1 (by-path merge c5f23e7a, blob-equal)
python -c (objects_of_record.json entries['B0/mmlu_pro_lb'])      # snapshot_id 20261001_094311_Headless_Run_Auto_ge + stamp
sed -n 224,233p tools/analysis/cert_positive_control.py; sed -n 101,121p tools/analysis/g12_site_null.py   # member/snapshot_row/check_stamp
python - : for db in {main, rp12-r2-run}/snapshots.db (file:...?mode=ro&immutable=1):
   count(*) snapshots; count(*) where id=SID; LIKE '20261001_0943%'; stamp==pointer; want keys; G12 ids in nodes
   -> main 216/0/0; rp12-r2-run 234/1/1, True, True, 135 nodes, root depth 0, 60/60
git hash-object {main,rp12-r2-run}/experiment_results/archv2/rp12_r2/g12/G12_sites.csv       # 21f110af both
python -c "sqrt(.1875/40), *2.8, sqrt(.0475/300), *2.8"          # 0.068465 0.191703 0.012583 0.035233
grep -n 'data.root|rp12-r2-run' docs/reviews/POSTRUN_cert_pc_k2_known.md POSTRUN_cert_pc_size.md; prog L23640
```
