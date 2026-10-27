# Shortlist from three literature passes, 2026-10-04 (orchestrator)

Sources:
- docs/literature/2026-10-04_response_structure.md (a8fb1be4)
- docs/literature/2026-10-04_embedding_structure_tests.md (ea418fcb)
- docs/literature/2026-10-04_hierarchy_evaluation.md

All proposals are zero-call. Selection rule: highest thesis value per cost; prefer tests that settle an open question in memo v3.

| # | Test | Question it settles | SQ | Source |
|---|---|---|---|---|
| 1 | SI-NULL-TRIAD | Plain vs background-covariance (Huang 2015) vs Gao-type null on CERT-PLANTED's planted grid: is any null sensitive to 2-way structure? | SQ3 (k=2 open) | hierarchy |
| 2 | SITE-SUPPORT | Do certified sites recur across the 4 re-draw trees more than uncertified ones (transfer support, Lemoine 2018)? A label-free check of the certificate. | SQ3 | hierarchy |
| 3 | TREE-LIKE | Is the embedding space hierarchical at all (Gromov delta, ultrametricity, cophenetic fit) against the site null, with a planted-hierarchy control? | SQ3 | embedding |
| 4 | SCALE-AGREE | Do embedders agree at coarse k and diverge at fine k, label-free, scaled against the q4-vs-q8 copy? | SQ5 | embedding |
| 5 | RESP-PROFILE-INFO | Do source-conditioned cells predict the winning model after a Rasch residual, beyond random within-source cells? | SQ1/SQ3 | response |
| 6 | CELL-DIFFICULTY | Are cells difficulty strata; do the 7 CELL-FLIPS cells survive a 3PL fit (evidence of more than one ability dimension)? | SQ1 | response |
| 7 | CELL-STRATA-EVAL | Does cell-stratified item sampling estimate a held-out model's accuracy more cheaply than random, source-only or IRT anchors? | SQ4 (price, undetermined) | response |
| + | HIER-F | Pre-data addendum to GRANULARITY-GT: hierarchical F, taxonomic P/R, ancestor-F1, level-wise Fowlkes–Mallows | SQ3 | hierarchy |

Deferred (lower value per cost or dominated): GEO-SPECTRUM, MODAL-SPLIT, PS-SITE, TEXT-RESP-ALIGN.
Declined, as the reviewers advised: MDL / Bayesian evidence (the closed MIX-LRT-SITE family), tree edit distance, data thinning, and any "cluster on TRAIN, file EVAL, then test" certificate (anti-conservative per Gao et al.).
Disclosure for 5–7: an exploratory, read-only look at the union DB (TRAIN+EVAL; no cell or label quantity) was taken during the response-structure pass.
