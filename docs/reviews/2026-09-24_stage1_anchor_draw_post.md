# Post-run review: ARCH-V2-STAGE1-ANCHOR-DRAW (light, record run 1463759)

**VERDICT: CONFIRMED. The draw of record stands as recorded.** The 7 stage-1 anchors are business, history, math, other, philosophy, physics and psychology. I recomputed the counts, the digest, the seed, the groups and the draw with my own code from the sealed view and got the same result digit for digit. The only draw with the record master is 1463759. There are no BLOCKER, HIGH or MEDIUM defects. There are 2 LOW defects, both already noted by the registrar at L16086.

Adversarial reviewer, 2026-09-24. Zero judge calls, read-only, one process. The view was opened with `file:...?mode=ro&immutable=1`. No `-wal` or `-journal` file is present. The view's mtime (15:18, before the run) was unchanged after my read. The view file is read-only (r--r--r--).

Objects:
- Registration: `docs/judge_v2_program.md` L15985-L15994 (53eccb6).
- READY: 65a9173 (committed 17:48:42).
- Run: 1463759 (committed 17:51:09; output mtime 17:50).
- View: `data_v2/REG_ARCHV2-SPLIT-1_c03031568a0a9d827d834b075512b8e4dd095642/eval_view_REG.db`.
- Script: `scratchpad/s1.py` (session scratchpad, numpy 1.26.3).

## Per-claim table

| # | claim | result | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | Per-anchor EVAL item counts, pool pv2_6f78aece2bf9a612, `corpus_version = 'mmlu-pro-v2'` | CONFIRMED | `side s JOIN item i ON i.item_id = s.item_id WHERE s.side='EVAL' AND i.corpus_version='mmlu-pro-v2' GROUP BY lower(trim(stratum_domain))` | 14 anchors, sum 3,749, which equals the pool row's n_items (3,745 components). Every stratum_source is MMLU_PRO. chemistry 425, physics 422, math 405, engineering 391, law 292, other 282, economics 257, psychology 245, business 238, health 206, biology 191, philosophy 153, computer science 125, history 117. Equal to the file's `counts` (dict equality True). There are no ties at any group boundary. The EVAL side holds 6,419 items. The 2,670 of them not in mmlu-pro-v2 belong to mc6 (3,749 + 2,670 = 6,419), so the item_id join mixes no corpus. |
| 2a | Seed = sha256(master\|"stage1-anchors")[:8] big-endian | CONFIRMED | `int.from_bytes(sha256("ARCHV2-STAGE1-ANCHORS-1:229687736d52902c3741e48ebc83be62efed488c\|stage1-anchors")[:8], "big")` | 10949444882593111949 = file = log |
| 2b | Groups: 7 consecutive pairs, descending by count, ties by name | CONFIRMED | own sort `(-count, name)`, pairs [0:2], [2:4], ... | [chemistry, physics] [math, engineering] [law, other] [economics, psychology] [business, health] [biology, philosophy] [computer science, history] = file `groups` |
| 2c | The draw, one per group | CONFIRMED | own `np.random.Generator(np.random.PCG64(seed))`, then `integers(0,2)` per group in group order. Cross-checked with a fresh generator and `choice(2)`. | picks physics, math, other, psychology, business, philosophy, history. Sorted: business, history, math, other, philosophy, physics, psychology = file `anchors` (both methods) |
| 3a | Counts digest 309490882deebbdb... | CONFIRMED | sha256 over `name\tcount\n` sorted by name | 309490882deebbdb12260f910bc6df81ebd811ec004479d478e33d379a6349bc (full match) |
| 3b | File sha 08cdff0e... | CONFIRMED | `sha256sum` of the working tree file and of `git show 1463759:<path>` | both 08cdff0e314dce5520bca8316e3a74a94845c64850fe8956c99b6d875ffb6140. `git hash-object` (LF) gives blob:b62d67c2f11d095437316736802f8c3a0f4974d4, the pin the registrar printed at L16086. The working tree is identical (the two sha256 values match), so no CRLF rendering is needed. |
| 3c | Streams digest 6164226e... | CONFIRMED | sha256 of `stage1-anchors\t10949444882593111949\tnumpy.PCG64\n` | 6164226ede640ea61136d1d576be2ff9e030ac7dcfc975bc1426b6fce752ea23 = file |
| 3d | eval_view sha256-bytes 7c284b15... | CONFIRMED | sha256 over the view's bytes | 7c284b15c45aa381654b5d175549fbac49269e0f4eed00c24e26990220650fb1 = file = log |
| 3e | Code the run used = 62e2688 | CONFIRMED | `git hash-object` on the run's export `scratchpad/s1draw/...` against `git rev-parse 62e2688:<path>` | runner da2754d3 = 62e2688, stage1.py 480bc77b, common.py a3346c6a, design.py 4959cb52, streams.py 30c23f97. All equal the JSON's `code` pins and 62e2688. The log prints the old `st.summary()` line, which the later uncommitted edit in the builder worktree replaces, so the dirty worktree runner did NOT produce this log. |
| 4a | No other commit carries or uses the record master | CONFIRMED | `git log --all -S'ARCHV2-STAGE1-ANCHORS-1:229687736d'` | 3 commits: 53eccb6 (registration), 62e2688 (constant in `stage1.py` L28 and in the runner's docstring; `git grep` on 62e2688), 1463759 (the run). `git log --all -- experiment_results/archv2/stage1_anchor_draw` gives 1463759 only. |
| 4b | No other output from the record master | CONFIRMED | `grep -rl` over `experiment_results` in the main tree and all worktrees (excluding .git and *.db) | 2 files, both in `experiment_results/archv2/stage1_anchor_draw/` (the count is by `wc -l`). The directory holds exactly 2 files (`ls \| wc -l` = 2), both tracked, none modified. `experiment_configs/` has 0 entries matching stage1 (`grep -ic`). Files newer than the READY under `experiment_results/archv2` and the worktrees: only these 2, plus an unrelated INDUCE-RUBRIC audit file. Session transcripts: 1 "STAGE1-ANCHOR-DRAW: RECORD DRAW" line in total, 0 "DRY-RUN" headers of this tool, and 0 other write-once sha lines. |
| 4c | Order: READY before run | CONFIRMED | `git log --format='%h %ci'` | 65a9173 17:48:42 < output mtime 17:50 < 1463759 17:51:09 |

## Defects

- D1, LOW (already noted at L16086 and by READY 65a9173): the run log's streams line names a `.streams.tsv` that was never written. The stream has 1 entry, and its seed and digest are printed in full and sit in the JSON, so nothing is lost. The fix is uncommitted in the builder worktree (`agent-a43fa24264b556ea7`, runner blob 5acf01bc). It must never be read as the code of record (the record is da2754d3).
- D2, LOW: the runner script itself (`archv2_stage1_anchor_draw.py`) is not among the JSON's 4 `code` pins, which cover only the libraries. It is pinned indirectly by the log line `archv2_pilot lf16 8d391ed8d8089270` and by the export's blob, which matches 62e2688. Fix: the next record tool should pin its entry point in the output.
- Note, not a defect: the registration says the digest is "pinned by the dry-run". I found no transcript of a pre-run dry-run of this tool. This does not matter for identity: a dry-run and the record compute the same counts from the same immutable, sha-pinned view, and the digest reproduces exactly (row 3a).

## Verdict

**CONFIRMED.** Stage-1 anchors of record: business, history, math, other, philosophy, physics, psychology (drawn: physics g1, math g2, other g3, psychology g4, business g5, philosophy g6, history g7). Seed 10949444882593111949. Counts digest 309490882deebbdb12260f910bc6df81ebd811ec004479d478e33d379a6349bc. File sha256 08cdff0e314dce5520bca8316e3a74a94845c64850fe8956c99b6d875ffb6140 (blob:b62d67c2...). One draw with the record master, never redrawn.
