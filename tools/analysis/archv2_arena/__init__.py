"""archv2_arena - ARCH-V2 E-A: the arena simulator (gate G22) and the zero-call v1/v2 replay (gate G23).

Engineering item ARCH-V2-E-A (docs/agents/queue.json; author decisions docs/judge_v2_program.md L15070-L15084; budget
study record L15098-L15123; synthesis docs/agents/results/evidence/ARCH-V2_SYNTHESIS_2026-09-23.md section 4 G22 / G23,
R11, R12; budget memo docs/agents/results/evidence/ARCH-V2_BUDGET_STUDY_2026-09-23.md section 5). ZERO judge calls.

NOTHING HERE IS REGISTERED. G22 and G23 each need their own registration (criteria, Support section) before a readout
is of record; the thresholds coded here are the synthesis's and the memo's WORDS, carried as parameters and printed as
"provisional (synthesis section 4 / memo section 5)", never as a registered bar. The CLIs therefore write only to an
explicit --out path, write-once, and every output's first line says UNREGISTERED.

[REGISTERED 2026-09-24 at d6129cf (ARCH-V2-G22 and ARCH-V2-G23, docs/judge_v2_program.md L15208-L15265), inserted by
the engine-coder; the text above is kept and read with this bracket: the bars are registered and printed as such, a
record run uses the registered masters (ARCHV2-G22-REC-1 / ARCHV2-G23-REC-1) and R = 1,000, other runs print DEV RUN.]

Modules
  streams.py        every random stream named, seeded from a master string by sha256, logged (the D-1 lesson)
  ro.py             the connection discipline: every DB through pool_guard.open_ro (the -wal / -journal refusal, then
                    mode=ro&immutable=1); snapshots_frozen.db and any 20NG DB refused by name; a global connect guard
  bt.py             batched numpy Bradley-Terry MM (the prior of record, 0.5), question-clustered bootstrap tensors,
                    a Newton BT with a per-match offset (length-adjusted fits)
  cert.py           the certificate: the functions of record imported from systematic_budget (craw / cbud / nll / fit /
                    mcnemar_edge), their vectorised twins (asserted equal by the selftest), LOAO, delta-deviance,
                    the binned gate, Holm, multi-stream c~ with MC-UNRESOLVED, Clopper-Pearson / Poisson / Wilson
  verdict_model.py  the per-order verdict model fitted on a judged board (key, position, length, anchor x model bias)
                    and its simulator (fixed / random / retest modes)
  data.py           read-only loaders for the caches of record and the key; the v1-exact edge builder and the fast one
  design.py         design specifications (D0, D4, D1-stage1, D1-full, D2), supply, schedules under the filter
"""
