# POST-RUN review: GEMMA-UNION-EXT (D-2026-10-08-4; RAW arm; engineering, no criterion; run 2026-10-09)

Reviewer: adversarial-reviewer, 2026-10-09. Zero judge calls and zero embedding calls by me. Every DB opened `mode=ro&immutable=1`;
busy.ps1 exit 1 before the read. Record: prog L25370 ("GEMMA UNION EXTENSION (D-2026-10-08-4; engineering, no criterion) ...").

## Verdict
**VALID (engineering build).** The new DB covers every distinct union text with a finite, unit-norm 768-d vector, and it is keyed
exactly as qwen3 keys the union. The base DB is unchanged.
Conditions G-1 and G-2 apply before any reader takes the DB. No criterion is decided here.

## Per-claim table
| # | claim (operator) | reviewer's number | result | sev |
|---|---|---|---|---|
| 1 | base sha 28f2e3a4... unchanged | sha256 28f2e3a41e77312f... (now) = provenance source_sha256 = backup | CONFIRMED | - |
| 2 | new DB sha 1360a7ed19604177 | 1360a7ed19604177... | CONFIRMED | - |
| 3 | 8,937 vectors written | new 20,690 rows minus base 11,753 = 8,937 added. The added set equals (distinct union texts minus base) exactly. All 11,753 base rows are present with byte-equal vectors | CONFIRMED | - |
| 4 | coverage 100% per source, 20,546 / 20,546 | 20,546 of 20,546 distinct corpus_questions.text (21,606 rows) carry a 3,072-byte vector | CONFIRMED | - |
| 5 | vectors sane | 0 non-finite; 8,937 distinct vectors (no degenerate repeats); norms 1.0000 for base and new alike (500 sampled each) | CONFIRMED | - |
| 6 | key = the union key readers use | all 20,546 union texts are present verbatim in qwen3 embeddings_cache.db `embeddings.query`, so the raw text is the shared key | CONFIRMED | - |
| 7 | model digest 85462619, route parity min cos 0.999995 over 20 texts | gemma_go.log shows digest EQUAL and parity min 0.999995 / median 1.000000 (bar 0.9999). Log read; not re-embedded (no Ollama call by me) | CONFIRMED (log) | - |
| 8 | Ollama capped at 12 threads | gemma_affinity.log: mask 0xFFF set on the ollama and ollama-app PIDs; within the ~22-thread cap (Amendment 27) | CONFIRMED (log) | - |
| 9 | backups | gemma_union_base 2/2 sums OK; gemma_union 7/7 sums OK (DB, provenance, driver, 4 logs) | CONFIRMED | - |
| 10 | "the record copies 7,624 missing; measured 8,937" | 8,937 by distinct text (BBH 5757, GPQA 546, IFEVAL 541, MUSR 756, MATH 1303, MMLU_PRO 34). L25370 states that 7,624 was copied from the brief and not re-derived | CONFIRMED discrepancy | LOW |

## Defects / conditions
- **G-1 (MEDIUM). The driver is unreviewed before its run and uncommitted.** It is gemma_union_ext.py,
  sha256 5ba08f3e4832f0e1..., which exists only in the backup and in E:/TaxoArena_tmp.
  I read it in full here. Its logic is sound: create the target exclusively; copy byte-for-byte with sha equality; INSERT OR IGNORE
  only the missing texts; refuse on the digest, on parity, or on a non-empty base -wal.
  Fix: commit the driver by path under tools/analysis/ so the DB's provenance resolves to a blob. The registrar records the blob in
  the provenance bracket.
- **G-2 (MEDIUM). The DB is staged, not live.** It sits at experiment_results/embedder_cross/gemma_union/ under the same basename the
  `--target-dir` readers expect. No reader points at it.
  Before any gemma reader is switched, two steps are needed: the EMBEDDER-PLUMBING gate (KNOWLEDGE §1: no non-qwen3 site null or
  FLAT read before RP08 merges), and a registrar's record naming this sha (1360a7ed...) as the gemma RAW object for the union.
  qwen3 stays of record.
- **L-1 (LOW).** The registrar brackets L25370: the missing count is 8,937 by distinct text; 7,624 is unexplained, and it was copied
  from the brief.
- **L-2 (LOW).** The base DB carries a 0-byte -wal and a -shm, both mtime 2026-10-09 02:13, which is before this op. Someone opened
  it non-immutable. Its sha is unchanged and the driver refuses only on a non-empty -wal.
  Fix: the data-steward identifies the opener; nothing is lost.

## Commands
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1    # rc=1
python - (inline, read-only): sha256 base/new; corpus_questions distinct texts; base vs new row sets and vector bytes;
         norms, finiteness, distinct vectors; union texts in embeddings_cache.db embeddings.query   # rows 1-6, 10
(cd E:/TaxoArena_backup_20261009_gemma_union_base && sha256sum -c SHA256SUMS.txt | grep -c ': OK')   # 2 of 2
(cd E:/TaxoArena_backup_20261009_gemma_union && sha256sum -c SHA256SUMS.txt | grep -c ': OK')        # 7 of 7
sha256sum E:/TaxoArena_tmp/op_20261009/gemma_union_ext.py   # 5ba08f3e... = provenance "driver"
```
