# DRAFTCHECK: BZ-AXIS-CONFIRM-FRESH draft amendment of 2026-10-27 per D-2026-10-27-5 (TaxoArena 31264855)

Authority: D-2026-10-27-5 (dcbac271; `docs/agents/author_decisions/2026-10-27.md` L24-L31). Reviewer: adversarial
reviewer, 2026-10-27. Zero LLM calls; nothing run except read-only git/grep and arithmetic. Reviewed:
`docs/judge_v2_program.md` section "## Registrar's record 2026-10-27 (insertion only; zero calls; nothing run) —
BZ-AXIS-CONFIRM-FRESH draft amended per D-2026-10-27-5 (A-D): ..." L25736-L25745 (_as_of 31264855) and queue item
BZ-AXIS-CONFIRM-FRESH at 31264855; checked against the sections L25708-L25724 / L25726-L25734, DRAFTCHECK a8004083,
DRAFTCHECK 95e69c9c, POSTRUN_TAU-GRID 6f16a31c, benchzoom master 35b2724 (blobs read with `git -C`, no worktree touched)
and the unmerged benchzoom plans `design-surface` 47d387e and `tau-cont-all` 3803853 (read with `git show`). No code
under review, so no mutants.

## Verdict

**SOUND WITH EDITS.** The commit is insertion-only and claims no registration. A-D transcribe the author's four
selections verbatim, and their meanings match the decisions file. The consequences of C are right: under N_A = N',
D_AB(N) and D_AB(N512) are 0 by construction; D2 is resolved; rule A reads no old response. The consequences of D are
right too: every planning number was derived under g2 and stays planning only. Every number reproduces to the digit.
No BLOCKER, no HIGH. One MEDIUM: blocker (2) names a source for n* that, by its own plan, prints no n*. Five LOW.

## Per-claim table (deciding claims)

| # | Claim (registrar) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Insertion only; earlier sections and queue text kept | prog `--numstat` 11 / 0; `git diff dcbac271 31264855 -- prog \| grep -c '^-[^-]'` = 0 (10 non-blank lines added). Queue: 267 -> 267 items, same ids, 1 item changed (BZ-AXIS-CONFIRM-FRESH), key set unchanged; `registration`, `author_decision`, `blocker`, `notes` each keep the old value as a prefix (4/4 `startswith` True); only meta `last_update` / `head_at_update` replaced (convention). Commit = 2 files (`--name-only \| wc -l`) | CONFIRMED | - |
| 2 | Span L25736-L25745, parent dcbac271 | `git show 31264855:prog \| wc -l` = 25,745; last `^## ` at L25736 (verbatim heading); `rev-parse 31264855^` = dcbac271; dcbac271 is an ancestor of 31264855, and 31264855 = HEAD at review start | CONFIRMED | - |
| 3 | Author's selections quoted verbatim | 4/4 quoted labels are exact substrings of the decisions file. "What each option meant" is attributed to the main session, not the author | CONFIRMED | - |
| 4 | A: rule B decides P and every F word; A is secondary and moves no word | Matches the meaning (A) word for word; "P confirms the axis_v1 recipe (V0')" is carried unchanged from L25722 | CONFIRMED | - |
| 5 | B: the point against 3 meter-SE decides; SE_cell is printed beside; E2 closed; the Q2 clause is not carried | Matches the meaning (B). 3 / 1.80 = 1.6667, one-sided p = 0.04779 (printed 1.67 / 0.048). P n* = 2,949 x (3.84162 x 0.0316 / 0.10)^2 = 4,345.9 -> **4,346** (printed 4,346; the option said "about 4,300"). Dropping "has no n* at all ..." is a8004083 D1's own fix | CONFIRMED | - |
| 6 | C: N_A := N', N512_A := N512'; D_AB(N) = D_AB(N512) = 0 by construction; dropped; identity check | C1(N) = G(N \| C1 chain), parent L2 + diff + len, all rule-independent. With the same pool, parent, tau^2 and split, C1(N_A) is C1(N'), so the identity holds. The 3 superseded 2026-10-26 sentences are verbatim substrings of L25708-L25734 (3/3). The cross-pool reader is moot. Rule A now reads no old response, so there is no conflict with D-2026-10-20-4. The [E9] asymmetry is stated (a8004083 D2 fix 1). The identity-check guard is ill-specified (F4) | CONFIRMED (guard PARTLY) | LOW |
| 7 | D: every tau^2 by the cont rule of docs/tau-grid.md (2b1bb0e, blob 13a26e8a LF); bullet byte-identical at 35b2724 (blob 4ef4f65c); g2 beside | `rev-parse 2b1bb0e:docs/tau-grid.md` = 13a26e8a, `35b2724:` = 4ef4f65c; the 8-line cont bullet is equal in both (`==` True); 0 CR in both blobs; working tree 196 CR, `hash-object` = 4ef4f65c. The registrar's paraphrase matches the bullet and `select_cont` (tau-grid.py d89d8ea1 L305-L319). "Every reader's tau^2" is a reading of the option wording, not marked as one, and the code it needs is not listed (F2) | CONFIRMED (scope PARTLY) | LOW |
| 8 | Planning numbers under g2 stay owed; PF not revised; past records stay as recorded | The g2 provenance of every planning SE / n* is correct. -0.0004 = POSTRUN_TAU-GRID row 9, H cont - g2 MATH -0.000387. That shift covers tau_L2 only, so it gives the PF re-fix under all-reader cont no WORK basis (F3). "Every exploratory WORK record so far was fitted on g2" is false for TAU-GRID (F5) | PARTLY | LOW |
| 9 | Remaining blockers (1)-(6) complete | (1), (3), (4), (5), (6) are correct and complete against L25708-L25734, a8004083 and 95e69c9c. (2) "n* ... from FRESH-DESIGN-SURFACE" fails: that item's plan prints no n* (F1). The queue's `depends_on` lacks FRESH-DESIGN-SURFACE (F1) and TAU-CONT-ALL (F3) | PARTLY | MED |
| 10 | Nothing claims a registration; ledger unchanged | Heading and STATE say "NOT registered"; queue `state` = "drafted", `go` = "needed"; `ls docs/agents/results \| grep -c BZ-AXIS-CONFIRM-FRESH` = 0; INDEX mentions 0. The ledger is not in the commit (2 files); `test_ledger.html` was last touched at 70c61579, v430 | CONFIRMED | - |

## Defects (each with its fix; all at the registrar's next record, F1 before the full registration)

- **F1 (MEDIUM; blocker (2), section D "PLANNING NUMBERS", hand-back blocker 2).**
  - What is wrong: "n* and roster size from FRESH-DESIGN-SURFACE" and "Planning SEs and n* stay OWED from
    FRESH-DESIGN-SURFACE" name a source that will not deliver an n*.
    - Its plan (benchzoom `design-surface` 47d387e, `docs/design-surface.md` L132-L134) says: "No n* is printed: the
      effects shrink with n ..., so a fixed-distance n* is not licensed".
    - The record's own L25733 says "planning only, sets no n*", and the queue item says "sets no n* for
      BZ-AXIS-CONFIRM-FRESH".
    - As worded, the blocker either never closes or gets closed by an n* the item was barred from producing.
  - Fix, by insertion:
    - Reword (2): "the fresh n and roster size, chosen at the full registration (H1) from FRESH-DESIGN-SURFACE's SE
      surface under the cont rule (MDE80 at m*(n): 3.842 x SE for P, 3.339 x SE for F; the surface prints no n*),
      against the effect expected at the planned n with its basis stated; any fixed-distance n* printed beside it as
      planning only".
    - Bracket the queue blocker the same way.
    - Append FRESH-DESIGN-SURFACE to `depends_on`.
- **F2 (LOW; D scope and code owed).**
  - What is wrong:
    - "Every tau^2 ... (tau_L2 and every reader's tau^2, every arm under both rules)" is the registrar's reading of
      "the continuous tau^2 fit". It is the natural reading, and TAU-CONT-ALL's plan L56 and design-surface's L87 read
      it the same way, but it is not marked as a reading.
    - `meter` has no cont path. `select_cont` exists only in `examples/tau-grid.py`, and only tau_L2 was run through it.
    - C (ii) lists only the rule-A assignment functions as code owed.
  - Fix:
    - Mark "every tau^2" as the reading.
    - Add to code owed: the per-reader cont selection (`select_cont` on each reader's S-TAU criterion, with its f2
      branch asserted bit-for-bit against `meter.step` / `gw.reader`), with selftest, mutants and a READY.
    - Make the READY's "every tau^2 went through cont" a COUNT: selections through cont = selections made, per reader
      family. A presence check is not enough.
- **F3 (LOW; PF basis).**
  - What is wrong:
    - "The full registration fixes the predictions under the cont rule" has a WORK basis only for tau_L2 (PR4: H -0.0004,
      C1 -0.0002 on MATH).
    - PF1-PF4 and PF6-PF9 under all-reader cont have no WORK number until TAU-CONT-ALL runs.
  - Fix:
    - In (5), say the PFs are re-fixed under cont from TAU-CONT-ALL's POSTRUN, or on another stated basis.
    - If TAU-CONT-ALL is that basis, append it to `depends_on`. It still decides no word.
- **F4 (LOW; C (i) identity check).**
  - What is wrong:
    - "A non-zero value is a code defect and refuses" is vacuous if N_A is the same object as N'.
    - If N_A is recomputed, the check can refuse on rounding alone: two computations of the same criterion differed
      by -7e-12 .. +1.2e-10 nats (POSTRUN_TAU-GRID row 4).
  - Fix: declare one of two forms.
    - (a) N_A is aliased to N' and the check is printed as "aliased (identity by construction)".
    - (b) N_A is recomputed, and the check refuses at a stated per-item tolerance (e.g. max |diff| > 1e-9).
- **F5 (LOW; D "PAST RECORDS").** "Every exploratory WORK record so far was fitted on g2" is false for TAU-GRID: its cont
  arm fitted tau_L2 continuously, and its word is cont vs g2. Fix: add "except TAU-GRID's cont arm (tau_L2 only)".
- **F6 (LOW; pins, a condition for the READY, not the draft).**
  - What is wrong: D says "working tree CRLF" without giving the renderings.
  - Fix: pin the renderings at the full registration:
    - plan of record blob:13a26e8a = sha256-lf16:88161a2b043802f6;
    - master blob:4ef4f65c = sha256-lf16:5adbe370fabfcde4 / sha256-crlf16:a3f3e68e678d9b36 (working tree, 196 CR).
- **F7 (LOW, optional; B).** The author chose the looser bar knowingly (3 meter-SE = 1.67 cell-aware SE at WORK).
  Fix: bind every quotation of P's word to its cell-aware z and p, the way C-M1 is quoted beside its net.

Observation (not a defect; for BZ-GUARDS-FRESH-TAU's reviewer).
- Under N_A = N' no rule-A neighbour pool exists, so the fresh test no longer executes the code path that R7 guards
  (the pool parent in `part_split` / `part_boot`).
- R8 (A's build excludes the fresh ids) and C2 still bind. BZ-GUARDS-FRESH-TAU therefore still blocks the READY, as (4)
  says.
- benchzoom master is 35b2724; `guards-fresh-tau` f483194 is not merged.

## Commands / scripts (read-only; scratch `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad`)

```
git show 31264855 --numstat --format= ; git show 31264855 --name-only --format= | wc -l          # 6/6 queue, 11/0 prog; 2
git diff dcbac271 31264855 -- docs/judge_v2_program.md | grep -c '^-[^-]'                       # 0  (and '^+[^+]' 10)
git show 31264855:docs/judge_v2_program.md > prog.md; wc -l; grep -n '^## ' | tail -1           # 25745; L25736
git rev-parse 31264855^ ; git merge-base --is-ancestor dcbac271 31264855                         # dcbac271; ok
python -I qcheck.py   # q_old (dcbac271) vs q_new (31264855): 267/267, 1 changed, 4/4 prefix kept, meta 2 replaced
python -I quotes.py   # 4/4 selections verbatim; 6/6 old-section quotes verbatim; 3/1.80=1.6667 p 0.04779; n* 4345.9
git -C benchzoom rev-parse 2b1bb0e:docs/tau-grid.md 35b2724:docs/tau-grid.md 32c2e6e:examples/tau-grid.py  # 13a26e8a 4ef4f65c d89d8ea1
python -I -c "<cont bullet of tg_plan.md == tg_master.md>"                                        # 8 lines, True
git -C benchzoom cat-file -p 13a26e8a|tr -cd '\r'|wc -c ; ... 4ef4f65c ; tr -cd '\r' < docs/tau-grid.md | wc -c ; hash-object  # 0; 0; 196; 4ef4f65c
git -C benchzoom cat-file -p <blob> | sha256sum ; sha256sum docs/tau-grid.md                     # 88161a2b.. / 5adbe370.. / a3f3e68e..
git -C benchzoom show 35b2724:examples/tau-grid.py | sed -n 300,320p ; git grep -n golden 35b2724 -- src/   # select_cont; none in src/
git -C benchzoom show design-surface:docs/design-surface.md | sed -n 126,140p                     # "No n* is printed" (F1)
git -C benchzoom show tau-cont-all:docs/tau-cont-all.md | grep -n reader                         # every reader cont (F2/F3)
python -I -c "<queue item BZ-AXIS-CONFIRM-FRESH depends_on / state / go; FRESH-DESIGN-SURFACE notes>"   # no FDS, no TCA
ls docs/agents/results | grep -c BZ-AXIS-CONFIRM-FRESH ; grep -c ... INDEX.md ; git log -1 -- docs/test_ledger.html  # 0; 0; 70c61579
grep -n '^| 4 \|PR4' docs/reviews/POSTRUN_TAU-GRID.md                                             # row 4 (F4), row 9 (-0.000387)
```
