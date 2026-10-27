# docs/reviews — what is here, and what stands in for it before 2026-09-17

This directory starts on 2026-09-17. Every post-run review from that date forward is a file here (`2026-09-DD_<subject>.md`), and every pre-run reviewer verdict is a `READY_<subject>.md`.

For any row adjudicated BEFORE 2026-09-17 there is no file here, and its absence is not a missing review. The check of record for those rows is one of five things, and each record in `docs/agents/results/<ID>.json` names which in its `review.file` field:

1. the Block 1 build-time adversarial check (the checker's number wins where it refutes the builder; programme "Block 1 record header"), 15 rows;
2. the independent checker's recomputation recorded inside the outcome bullet itself (the `check_*.py` scratch scripts named there), 4 rows;
3. a named successor test or instrument gate that re-read the number, 64 rows;
4. nothing — no independent re-reading exists; the record says exactly "no separate review file (pre-dates docs/reviews/)" and nothing more, 14 rows (BOARD-W, FORMAT, HYBRID, J1-R, J2-D, L1-V2, MC-BUILD, MC-FED, MC-ROOT, PAIR-NOREF, REF-CONF, SELECTIVE-ORDER, STACK, TEMP-0);
5. the ledger audit of 2026-09-14 or the adversarial review session `docs/review_session_2026-09-14.md` (ba12200), 20 rows.

Do not read "no review file" as "unreviewed": read the record's `review.file` sentence, which is the provenance of record. Counted 2026-09-23 over the 142 records then in `docs/agents/results/`: 24 cite a file here, 1 is not yet run, 117 fall into the five classes above.

[Written 2026-09-23 by the registrar as the class-4 pointer of docs/agents/results/INCONSISTENCIES.md (8eeddaf). Pointer only: no number here is new, and no record was changed to create it.]

[RECOUNTED 2026-09-23 by the registrar at HEAD e962327, the commit that writes this file (pointer only, zero calls, nothing above rewritten): docs/agents/results/ now holds 145 records, of which 27 cite a file in this directory and 1 (TOPIC-PARTITION-20NG-T1B-NULL) carries review null because it is registered and not yet run. The 117 and the five class sizes 15 / 4 / 64 / 14 / 20 are UNCHANGED and were re-verified record by record at this commit; the "142 records / 24 cite" counted above is the count as of e422daa, when the worksheet was written, and is left standing beside this one rather than rewritten.]
