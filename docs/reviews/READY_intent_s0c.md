# READY_intent_s0c: delta review of intent-s0c 9192a38 on 9699d7d (zero judge calls)

**Verdict: MERGEABLE. READY for `--embed --go` on qwen3, nomic and gemma.** After the embeds, `--run` stays gated on the registrar pinning the embedding DBs (unchanged from READY_intent_s0b 9fe96a6).
Condition C-1 (LOW, operator): each `--embed <e> --go` log must print `TRANSPORT parity bar <e>: min cos >= <bar>` with qwen3 0.9980 and nomic/gemma 0.9999 before any row is written. The --go call site has no test pinning the per-embedder default (RV-3 below).

Reviewed blob: `tools/analysis/intent_transfer_s0.py` LF `git hash-object` **c5346ce2** (the worktree rendering is the same: `--no-filters` also gives c5346ce2, so there is no CRLF variant). Prior blob 69e6f400 (READY_intent_s0b).

## Per-claim table (deciding claims)
| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | The diff is only the per-embedder bar plus its tests and mutants | CONFIRMED | 1 file (`--name-only \| wc -l` = 1), +49/-2: PARITY_BAR/PARITY_SOURCE constants; `route_parity(bar=None)` -> PARITY_BAR[e] with the source printed; 4 ST-PARITY checks; 5 mutants. No other logic touched | - |
| 2 | Bars: qwen3 0.998, nomic 0.9999, gemma 0.9999 | CONFIRMED | L173 `{"qwen3": 0.998, "nomic": 0.9999, "gemma": 0.9999}`. Both non-test callers (L563 --go, L1662 dry-run) take the default | - |
| 3 | 0.998 separates drift from a real route error (diagnosis 9699d7d) | CONFIRMED on the record | drift >= 0.99915 (the smallest drift) > 0.998 > 0.9846 (trailing space, the smallest route error). The rule is a min over 20 texts, so the trailing-space min 0.9846 fails. Margin above the bar is 0.00115 (drift); margin below it is 0.0134 (error) | - |
| 4 | --dry-run passes for all 3 on main + 9192a38 | CONFIRMED | main = 9699d7d, the parent of the tip, so main + 9192a38 = 9192a38. rc=0; qwen3 min **0.999196** (bar 0.9980) PASS, which is the digit-exact value of the 72851a1 refusal; nomic min 1.000000 PASS; gemma min 0.999995 PASS; "TRANSPORT PREFLIGHT PASSED (3 of 3 embedders)"; probe price total 67.9 min | - |
| 5 | The dry-run writes nothing | CONFIRMED | sha256 and mtime of the 3 record caches and intent_transfer_corpora_v1.db are unchanged before/after (diff empty); `ls intent_emb_*.db \| wc -l` = 0; embeddings_cache.db-wal 0 bytes, Sep 23 | - |
| 6 | Selftest and mutants | CONFIRMED | SELFTEST PASSED (133 checks = 129 + 4 new); MUTANTS 78 of 78 KILLED (73 + 5 new), the 5 new ones killed by ST-PARITY | - |

## Own mutants (3; delta < 150 lines)
- RV-1: qwen3 bar 0.998 -> 0.9985. KILLED (the ST-PARITY print check). Decisive.
- RV-2: `if not mn >= bar` -> `mn > bar` (equality at the bar). SURVIVED. This code predates the delta and cannot bind with 6-digit cosines. Not decisive.
- RV-3: the dry-run call site pins `bar=0.998` for every embedder. SURVIVED: the stub route returns cos 1.0, so no fixture separates the per-embedder bars at a call site; ST-PARITY exercises only `route_parity` directly. Not decisive for this blob: the live dry-run printed 0.9999 for nomic and gemma (claim 4), and L563 uses the same default. This is the source of C-1.

## Defects
- D-1 (LOW): no call-site test covers the per-embedder bar (RV-3). Fix: in ST-EMBED/ST-DRY, run `--dry-run` with `drift_fn(0.9992)` as the route and assert REFUSED at nomic. Not a merge blocker.
- Observation (not a defect): the qwen3 drift margin is thin (0.99915 vs 0.998). A future driver or GPU change could land between the two. A refusal would then be fail-closed, which is the right direction.

## Commands
```
git diff --stat 9699d7d 9192a38; git diff --name-only 9699d7d 9192a38 | wc -l          # 1 file, +49/-2
git show 9192a38:tools/analysis/intent_transfer_s0.py | git hash-object --stdin          # c5346ce2 (worktree LF = --no-filters)
python tools/analysis/intent_transfer_s0.py --selftest   (worktree)                      # PASSED (133 checks)
python tools/analysis/intent_transfer_s0.py --mutants    (worktree)                      # 78 of 78 KILLED
TAXOARENA_DATA_ROOT=<main root> python .claude/worktrees/intent-s0c/tools/analysis/intent_transfer_s0.py --dry-run   # rc=0, 3 of 3 PASS
sha256sum + stat -c %Y on the 4 DBs before/after | diff                                  # UNCHANGED
scratchpad rv.py: RV-1..3 applied one at a time, --selftest each                         # K / S / S
```
