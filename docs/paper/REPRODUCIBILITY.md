# Reproducibility Artifact Checklist

> Required for submission to ACL/EMNLP/NeurIPS/ICLR venues.
> Most venues require artifacts to be available at submission time.
> Updated June 2026.

---

## 1. Code & Build

| Item | Status | Notes |
|------|--------|-------|
| Source code public | ✅ | `github.com/0ctave/TaxoArena` |
| Deterministic build | ✅ | JDK Temurin 21, Kotlin version pinned in `build.gradle.kts` |
| Pinned random seeds | ✅ | Every stochastic phase (vMF init, k-means++ restarts, OpenSkill scheduling) uses documented seeds |
| `.db` cache excluded from git | ✅ | `*.db` in `.gitignore` (PR #65 / M3) |
| `downloadDataset` Gradle task | 📋 | Needed so reviewers can reproduce the MMLU-Pro cache without a pre-built `.db` file |
| Startup dimension validation | ✅ | `check(actualDim == expectedDim)` in `TaxonomyEngine.adaptTaxonomy` (M3) |

---

## 2. Dataset

| Item | Status | Notes |
|------|--------|-------|
| MMLU-Pro 14-domain split policy documented | 📋 | Add HuggingFace-style dataset card: query count per domain, split policy, reserved-vs-full-set boundary |
| Dataset checksum in README / appendix | 📋 | SHA-256 of the downloaded MMLU-Pro snapshot used in all reported runs |
| Reserved test split held out | ✅ | `reservedOnly = true` enforced in experiment config |
| Full-dataset numbers reported | 📋 | Paper needs both `reservedOnly=true` and `reservedOnly=false` numbers |
| Per-domain query counts | 📋 | Currently global counts only; add per-domain table to paper appendix |

---

## 3. Model Cards

| Item | Status | Notes |
|------|--------|-------|
| Embedding model card | 📋 | `Qwen/Qwen3-Embedding-8B`, version, `{128,256,512,1024}` MRL prefix set |
| LLM judge model card | 📋 | Model name(s), version, temperature, system prompt template (hash of prompt) |
| Labelling model card | 📋 | `config.llm.labelingModel`, same details |

---

## 4. DAG Snapshots

| Item | Status | Notes |
|------|--------|-------|
| Released DAG snapshots | 📋 | One `.dot` + `taxonomy_visualization.json` per benchmark config, versioned by run hash |
| Re-scoring without re-generating | 📋 | Eval-results ZIP schema must be documented; `ModelEvalLoader` currently accepts an undocumented format |
| Snapshot naming convention | 📋 | Include: `{model}_{dataset}_{numIter}_{minSize}_{epsilon}_{seed}` |

---

## 5. Experiment Config Reproducibility

Every reported number must be traceable to a config. The recommended approach:

```yaml
# Canonical experiment config block (include in paper appendix)
taxoadapt:
  execution:
    numIterations: 25
    minClusterSize: 25
    maxDepth: 5
    enableLabeling: false
    enableLiveLabeling: false
  formalism:
    separationEpsilon: 0.01
    assignmentCosineGap: 0.15
    deltaAssign: 1.0
  llm:
    labelingModel: "ministral-3:14b"
    judgeModel: "mistral-small:latest"
```

Add a `--export-config` CLI flag that dumps the resolved config as JSON to stdout
before the run starts. This makes the config part of the run artifact.

---

## 6. Publication Venue Requirements

| Venue | Specific requirement |
|-------|--------------------|
| ACL / EMNLP | Reproducibility checklist form + anonymous artifact submission |
| NeurIPS | Code + data URL in submission; camera-ready requires OpenReview artifact |
| ICLR | Reproducibility statement in paper body |
| ECIR / SIGIR | IR evaluation: TREC-style run file format preferred |

The TaxoArena eval results (per-query routing decisions + scores) should be exportable
in a standard run-file format for IR venues.
