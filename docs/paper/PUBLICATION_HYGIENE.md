# Publication Hygiene

> Non-experimental paper tasks. Must be complete before submission.
> Covers citations, licensing, ethics, and limitations section.
> Updated June 2026.

---

## 1. Complete Citation Pass

Every adopted method needs a DOI or arXiv link in the bibliography. Below is the
complete list with verified identifiers.

### Statistical foundations

| Method | Reference | DOI / URL |
|--------|-----------|----------|
| vMF MLE | Banerjee et al. 2005, JMLR 6 | `10.5555/1046920.1088394` |
| Bias correction | Hornik & Grün 2014, JSS 58:10 | `10.18637/jss.v058.i10` |
| Small-N vMF simulation | Marrelec & Giron 2024, Commun. Stat. 53:1 | `10.1080/03610918.2021.2011923` |
| vMF impossibility | Jabbar et al. 2026 | (preprint — check arXiv at submission) |
| OAS covariance | Chen, Wiesel, Eldar & Hero 2010, IEEE TSP | `10.1109/TSP.2010.2053029` |
| Ledoit–Wolf robustness | Ledoit & Wolf 2025, JMVA | (check final DOI) |

### Dimensionality & embedding

| Method | Reference | DOI / URL |
|--------|-----------|----------|
| MRL | Kusupati et al. 2022, NeurIPS | `10.5220/0008643100002068431-2192` |
| Qwen3-Embedding | Model card | `huggingface.co/Qwen/Qwen3-Embedding` |
| vMF–cosine equivalence | Banerjee et al. 2005 | same as above |

### Hierarchy & split criterion

| Method | Reference | DOI / URL |
|--------|-----------|----------|
| Dasgupta cost | Dasgupta 2016, STOC | `10.1145/2897518.2897527` |
| BIC for vMF | Gopal & Yang 2014, ICML | `proceedings.mlr.press/v32/gopal14` |
| Roy & Pokutta HC bounds | Roy & Pokutta 2017 | `10.48550/arXiv.1611.02182` |

### Ranking

| Method | Reference | DOI / URL |
|--------|-----------|----------|
| Weng–Lin / OpenSkill | Weng & Lin 2011, JMLR 12 | `10.5555/1953048.1953057` |
| OpenSkill library | Kovalchuk et al. 2024 | `arXiv:2401.05451` |
| LLM ranking survey | JuStRank 2025, ACL | (check proceedings) |

### Evaluation metrics

| Metric | Reference | DOI / URL |
|--------|-----------|----------|
| Overlapping NMI | Lancichinetti, Fortunato & Kértesz 2009, NJP 11 | `10.1088/1367-2630/11/3/033015` |
| LFK overlapping communities | Lancichinetti & Fortunato 2009, PRE 80 | `10.1103/PhysRevE.80.056117` |
| DAG HC evaluation | Monath et al. 2021, AISTATS, PMLR 130 | `10.48550/arXiv.2105.04024` |
| H-P / H-R / H-F | Kosmopoulos et al. 2014, IRJ 18 | `10.1007/s10791-013-9224-2` |
| Hierarchical classification survey | Silla & Freitas 2011, DMKD | `10.1007/s10618-010-0175-9` |
| Tree balance survey | Fischer et al. 2021/2023 | `arXiv:2109.12281` |
| Universal tree balance | Lemant et al. 2022, Syst. Biol. 71 | `10.1093/sysbio/syac027` |
| Routing calibration (ECE) | Guo et al. 2017, ICML | `proceedings.mlr.press/v70/guo17a` |
| HTC metrics study | Plaud et al. 2024, CoNLL | (check proceedings) |
| WLP related work | Zhong & Ghosh 2005 | (check DOI) |
| Dendrogram Purity | Heller & Ghahramani 2005 | `10.5555/2976248.2976312` |

---

## 2. License Audit

| Asset | License | Action |
|-------|---------|--------|
| TaxoArena source | Apache-2.0 | ✅ confirmed |
| MMLU-Pro dataset | MIT | ✅ covers research use |
| LLM judge outputs (included in artifacts) | Depends on model license | Check: if using GPT-4 / Claude, outputs may not be redistributable; if using Mistral/Qwen (Apache-2.0), redistribution is fine |
| Qwen3-Embedding model | Apache-2.0 | ✅ covers research use |
| OpenSkill library | MIT | ✅ |

**Action:** Add a `LICENSE-THIRD-PARTY.md` file listing all bundled/generated assets
and their licenses.

---

## 3. Ethics & Data-Use Statement

Include in paper (1 paragraph, typical venue requirement):

> We use the MMLU-Pro dataset (MIT license) for evaluation only. No new human
> annotations were collected. LLM judge comparisons use [model names] for automated
> pairwise evaluation; judge outputs are included in released artifacts under
> [license]. The taxonomy construction does not involve personal data.

For venues with an ethics checklist (NeurIPS, FAccT), also address:
- **Potential misuse:** taxonomy-based routing could be used to selectively suppress
  certain query types; mitigated by publishing the full algorithm and DAG snapshots.
- **Biases:** MMLU-Pro domain distribution is English-centric academic; generalisation
  to other corpora is not claimed.

---

## 4. Limitations Section

Required by most venues. Include all of the following:

### Mathematical

- **H-F1 requires per-query true-leaf GT.** The current implementation reports `0.0`
  until GT plumbing is complete (see `EMPIRICAL_PLAN.md`). Results in the paper will
  use the wired version.
- **Hornik–Grün bias correction is asymptotic.** Not exact for small `d`; exact
  unbiased estimation of `κ` is provably impossible (Jabbar et al. 2026).
- **OAS assumes Gaussian samples.** Unit-sphere embeddings are directional data;
  the Gaussian approximation holds for moderate `κ` but is acknowledged as an
  approximation.
- **Cross-link detection is purely geometric** (majority-vote cosine score). No
  semantic validation of cross-links is performed.

### Empirical

- **Single embedding model.** All experiments use Qwen3-Embedding-8B. Contamination
  ratio (~16.8%) appears invariant across algorithm params, suggesting an
  embedding-geometry bottleneck. Generalisation to other models is untested.
- **English-only, academic domain.** MMLU-Pro is entirely English academic content;
  TaxoArena's performance on other corpora (multilingual, domain-specific, etc.)
  is not evaluated.
- **Weng–Lin independence assumption.** Cross-linked nodes share queries, creating
  partial non-independence in the OpenSkill model. Effect on ranking accuracy is
  unquantified.
- **Softmax temperature `τ=0.5` is a fixed hyperparameter.** ECE calibration of
  routing probabilities is pending (see `EMPIRICAL_PLAN.md`).

---

## 5. Renames and Formal Definitions Needed in Paper

| Current name | Required change | Location |
|--------------|-----------------|----------|
| `ACR` | Rename to **Exact-Match Ancestor Rate (EMAR)** | Code, TUI, paper §6 |
| `Equilibrium Index` | Supplement with **Normalised Sackin Index** or rename | Code, paper |
| `WLP` | Add formal definition with formula to paper §6 | Paper only |
| `Contamination Ratio` | Add formal definition (denominator, threshold) | Paper only |
