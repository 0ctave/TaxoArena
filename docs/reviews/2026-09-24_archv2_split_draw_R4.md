# R4 post-draw review — ARCH-V2-SPLIT-DRAW-1 (the real v2 split, b51eb71)

Adversarial reviewer, 2026-09-24. Zero calls. Read-only: every DB opened `mode=ro&immutable=1` after a sidecar check (no -wal / -journal / -shm in the REG directory). The five REG DBs have the same sha256 and the same `ls --full-time` listing before and after this review (`diff` of both listings is empty).

## VERDICT

**R4 MET. THE DRAW STANDS AS THE SPLIT OF RECORD.** A third implementation re-derives it with 0 differences in 21,384 of 21,384 rows. It is my own code, imports no repo module, and uses neither `split.compute` nor `gates.independent_draw`. It is compared field by field (item, component, stratum, side, corpora) against the committed TSV and against the sealed split DB.

All of the following are equal to the digit:
- five hashes of the side table: the TSV text, the TSV header, the sealed DB, the manifest and my re-derivation (table_sha `1b5f6395cac8f46f…`);
- the component table (21,374 rows, rank_hex included);
- the stratum table (52 rows);
- the three pool ids.

R3 is met in substance. The independent G2 is 0 on every intersection. The 4 input DBs are unchanged against the runlog.

**R1 is PARTLY evidenced.** The runlog's process list is one snapshot taken at launch. Nothing was appended during or after the build, and two other agents' commits landed inside the build window. "No other pool reader during the build" is therefore not shown by the record (D1, MEDIUM). The byte-identical inputs and the exact re-derivation mean no concurrent process changed the draw. No defect blocks use of the split.

## Identity (pin kinds named)

- Build commit b51eb71. The build started at HEAD beb8bc1 (transcript L2) and ended at HEAD ca3072d (manifest `git_head`; D2).
- Code pins in the manifest (`blob` = git blob of the LF rendering):
  - split.py blob:4f5b1d0b / sha256-lf16:62057a9ab1e67e23
  - gates.py blob:bc6c6e67 / sha256-lf16:bd1af326f5dccab9
  - build.py blob:6be9c529 / sha256-lf16:441ee69621ea0f6e
  - content_closure blob:1533cb5a
  - split_side blob:05224b5a
  - all equal to the READY 68d5e2c identities.
- `git ls-tree` gives the same 12 blobs at beb8bc1, ca3072d, b51eb71 and HEAD (`uniq -c` = 4 for each of the 12). `git status --porcelain` on those paths gives 0 lines.
- Manifest file sha256-bytes: 5fd9d2386ccf260b (MATCH the relay).
- REG DB sha256-bytes (`sha256sum`) equal the manifest:
  - corpus mmlu c8afeaa6
  - corpus union 21d79e8c
  - split 69c8dfa2
  - gen_view 690d06b8
  - eval_view 7c284b15
- The two corpus DBs are byte-identical to the ED3 DEV corpora, as the READY expects.
- Committed files: blob = `git hash-object` of the working tree for all 5. The TSV has 0 CR bytes, so the LF rendering is the only one. The TSV blob bytes (`git show b51eb71:… | sha256sum`) hash to c7f84f3f42f7f6bb, which equals the manifest's `side_export.sha256_bytes`.

## Per claim

| # | claim | verdict | command / script | got vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Third implementation reproduces the split | CONFIRMED | `scratchpad/r4_third.py` (own code, no repo import) | 0 of 21,384 rows differ vs TSV; 0 vs sealed DB; 0 only-left or only-right; items E/G/T 6,419 / 2,143 / 12,822; components 6,415 / 2,142 / 12,817; 52 strata; 10 merged components (20 items); 34 multi-stratum. All as claimed | — |
| 1a | component and stratum tables | CONFIRMED | same | component: 0 of 21,374 differ (n_items, stratum, rank_hex, side). Stratum: 52 rows equal | — |
| 1b | pool ids | CONFIRMED | same | pv2_ffa5eea85c29112c 6,415 / 6,419; pv2_4cce62591eb5a2cb 6,187 / 6,187; pv2_6f78aece2bf9a612 3,745 / 3,749. All equal the DB | — |
| 1c | the comparison is not vacuous | CONFIRMED | same, [ctl] lines | a different seed changes 2,000 of 2,000 ranks. Half-up differs from floor in 5 strata (n = 185, 146, 105, 295, 152 → EVAL 56, 44, 32, 89, 46). The tie-break acts on 2 real components (this covers READY E7 on real data) | — |
| 2 | TSV table_sha = sealed DB side table | CONFIRMED | r4_third.py [sha] | text / header / DB / manifest / mine all 1b5f6395cac8f46f…; header split_sha256 = the split file's sha256 69c8dfa2; column header = DB columns; rows in item order | — |
| 3 | R3: ratios = C4 (0.30 / 0.10 / 0.60) | CONFIRMED in substance | split meta: `eval_ratio` '0.3', `gate_ratio` '0.1'. My draw uses exact integers `(3n+5)//10` and `(n+5)//10`, capped, with TRAIN as the remainder, and reproduces every row | realised items 0.3002 / 0.1002 / 0.5996; components 0.3001 / 0.1002 / 0.5997 | D4 LOW |
| 4a | R1: dirty paths none | CONFIRMED, with a scope caveat | transcript L2; build.py L92 | the check covers `tools/analysis/data_v2` only. content_closure and split_side are covered by `code_pins` (blob of the working tree at manifest time = the pin) | D3 LOW |
| 4b | R1: pins match | CONFIRMED | ls-tree at 4 commits | 12 of 12 | — |
| 4c | R1: no other pool reader during the build | UNDETERMINED from the record | runlog mtime 15:15:42.98 = launch (`ls --full-time`); the runlog's last line is the tasklist; there is no AFTER section (`grep -c -i after` = 0 matches outside process names); the snapshot has 0 python.exe / java.exe (`grep -c python` = 1, the "earlier waits" line) | pre-launch only. 613da05 (15:16:44) and ca3072d (15:17:12) were committed inside the 168 s build window | D1 MEDIUM |
| 5 | Independent G2 = 0 | CONFIRMED | `scratchpad/r4_g2.py AD` (ed3_indep.py part A retargeted; keys through main's content_closure blob:1533cb5a; no data_v2 code) | all 0: EVAL stems vs gen stems, gen item keys, gen item ids, content keys (rows, variants, responses, references), sentinel stems (228 EVAL items with no ACTIVE response), components, 4 alias namespaces, ACTIVE qid families, and 4,619 EVAL-stem shingles in gen reference.raw. Salted set re-derived equal (6,419). gen keys 14,965 / eval keys 6,419, as gates.txt says | — |
| 5a | legacy references | CONFIRMED | r4_g2.py D | 3,632 = EVAL 1,073 (v0 1,014 + v1 59) + gen 2,559 (2,418 + 141); 0 variant mismatches; 0 gt mismatches | — |
| 6 | 4 input DBs unchanged | CONFIRMED | `sha256sum` of the 4 inputs, diffed against runlog L5-L8: empty diff | 4 of 4 identical. The -wal files beside the two caches are 0 bytes and predate the draw (09-23, 09-15) | — |
| 7 | R5: no read of the side table before the manifest commit | UNDETERMINED beyond R2 | mtimes: TSV 15:18:11, manifest 15:18:39, gates 15:19:45, commit 15:20:00 | the only recorded reads are the build's own verify and the R2 gates; no record excludes others | — |

## Defects

- **D1 MEDIUM: the R1 "no other pool reader" evidence is one pre-launch snapshot.**
  - The runlog was written once, at 15:15:42, and nothing was appended.
  - There is no process sampling during the 168 s build, and no AFTER input hash in the runlog (the AFTER leg exists only as gates G1 "unchanged since the build" and this review).
  - Other agents were active: two commits landed mid-build.
  - Consequence: nil for the split's substance, since the inputs are byte-identical and the draw re-derives exactly. It is an evidence gap for rule 7.
  - Fix:
    - A registrar bracket on the draw's record: "R1 no-reader evidence = pre-launch snapshot only".
    - For future one-shot draws and constructions, the runlog samples the process list during the run and appends the input hashes and the process list AFTER the run.
- **D2 LOW-MEDIUM: the manifest `git_head` (ca3072d) is the end-of-build HEAD, not the HEAD the build ran from (beb8bc1).**
  - build.py L92 reads HEAD at the start; L114 reads it again at the end.
  - HEAD moved mid-build (ca3072d changes only canary_baseline.py and accepted_tests_ledger.py). All 12 pinned blobs are identical across both HEADs, so there is no code effect.
  - Fix:
    - Read HEAD once and write that value to both places, or record `git_head_start` / `git_head_end` and flag it when they differ.
    - A registrar bracket naming beb8bc1 as the launch HEAD.
- **D3 LOW: the "dirty paths" check covers `tools/analysis/data_v2` only.**
  - content_closure.py and split_side.py are imported but not scoped. `code_pins` covers them after the fact.
  - Fix: add both paths to the porcelain call.
- **D4 LOW (ruling on the missing train_ratio): IMMATERIAL.**
  - TRAIN is defined by the rule as the per-stratum remainder `n - n_eval - n_gate`. It has no parameter of its own, so no value of a train_ratio key could disagree with the draw.
  - The C4 record (0.30 / 0.10 / 0.60) is met because 0.60 = 1 - 0.30 - 0.10 per stratum, up to rounding. It is witnessed by an exact-rational re-derivation that matches every row.
  - A real residual: the manifest's `eval_ratio` / `gate_ratio` are the code constants `DEFAULT_*` (build.py L116), not the values passed to `build_split`. They are equal here only because build.py passes none. The split DB's meta is the authoritative value.
  - Fix (optional): write the passed values into the manifest, and add `train_ratio: "remainder"` to the meta.
- **D5 INFO: legacy qids of the quarantined model cross the split.**
  - 3,154 MMLU-Pro legacy qids appear on both sides, only through quarantined Meta-Llama-3-70B rows. The ACTIVE-row count is 0.
  - 477 gen-view references share a legacy qid with an EVAL-side quarantined response. The ACTIVE count is 0.
  - This is by design: those rows are id-shifted, and every content intersection is 0. The hazard is for consumers: any E-J or E-A join on `legacy_qid` that admits quarantined rows would cross sides.
  - Fix: E-J / E-A loaders join by item_id / variant_id only.
- **D6 INFO: a rule ambiguity that does not bite on this data.**
  - The docstring words the vote fallback per ITEM; ed3_indep.py applies it per COMPONENT.
  - On this data the two readings disagree on 0 of 21,374 components.

## Reproduce

Scratchpad (session): `r4_third.py` → `r4_third.out`; `r4_g2.py AD` → `r4_g2.out`; before-state `r4_before_sha.txt` and `r4_before_ls.txt`. The DEFF figures in the transcript (Kish 1.9079 / 1.9094, "rho = 1 upper bound") were not re-measured here. The draw registers no deciding statistic, so there is no Support section to check.
