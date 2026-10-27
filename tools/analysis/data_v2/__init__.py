"""TaxoArena ARCH-v2 data layer (E-D): ingestion (M1), the split (M2), the physical views (M3), the verdict schema (R6/R7).

Import with tools/analysis on sys.path:  from data_v2 import open_generation, open_eval
The stage-gated openers are the only entry points a v2 stage uses to read corpus text:
  open_generation(stage)  stages construct / label / induce / policy_fit      -> gen_view.db  (TRAIN + GATE text only)
  open_eval(stage)        stages judge / arena / route                          -> eval_view.db (EVAL text)
Each refuses every other stage (views.py). The only sqlite3.connect in this package is in ro.py (lint_connect.py).
"""
from .views import open_generation, open_eval, GENERATION_STAGES, EVAL_STAGES  # noqa: F401
