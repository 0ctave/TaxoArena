# Eval-results ZIP / JSON schema

Precomputed model evaluations are ingested by `ModelEvalLoader` from TIGER-AI-Lab
MMLU-Pro eval-result files. A source may be a `.zip` (containing one or more inner
`.json` files), a single `.json`, or a directory of per-category `.json` files. Each
JSON file is a **top-level array**, with **one object per question**.

## Field reference

Each array element is parsed into `RawEvalItem`. Unknown keys are ignored.

| Field          | Type            | Required | Semantics |
|----------------|-----------------|----------|-----------|
| `question_id`  | int             | yes      | Canonical upstream MMLU-Pro question id. Items with `question_id < 0` are skipped. Forms the primary key `(question_id, model_name)` in `eval_results`. |
| `question`     | string          | yes      | The question text. Blank questions are skipped. Denormalized into `eval_results.question_text` and used to cross-reference `mmlu_pro.question` and the embeddings cache. |
| `options`      | array of string | yes      | The A–J answer choices, in order. |
| `answer`       | string          | yes      | Ground-truth answer **letter**, e.g. `"A"`. |
| `answer_index` | int             | no       | 0-based index of the correct option. Informational; correctness is computed from `pred == answer`. |
| `category`     | string          | yes      | MMLU-Pro category, e.g. `"math"`, `"physics"`. Used for per-category benchmark stats. |
| `pred`         | string or null  | no       | The model's extracted answer letter, e.g. `"A"`. `null` means extraction failed. `is_correct` is set to `pred != null && pred == answer`. |
| `model_outputs`| string          | no*      | The full chain-of-thought reasoning trace. |
| `cot_content`  | string or null  | no*      | Legacy fallback for the trace. Used only when `model_outputs` is blank. |

\* At least one of `model_outputs` / `cot_content` should be present; the loader stores
`model_outputs.ifBlank { cot_content ?: "" }` as the trace.

## Model-name → path convention

The model name is taken from the explicit argument to
`ModelEvalLoader.loadFromZip(zipPath, modelName)` /
`loadFromDirectory(dirPath, modelName)`. When loading via `loadFromPath(path)` without an
explicit name, it is derived from the filename, which follows the convention:

```
model_outputs_<MODEL>_<N>shots.zip
```

e.g. `model_outputs_GPT-4o_5shots.zip` → model name `GPT-4o`.

## Reserved-pool file

`syncReservedPool` reads `reserved_test_queries.json`, a JSON object mapping
**category → list of reserved question texts**:

```json
{
  "math":    ["math q1: 2+2?", "math q2: derivative of x^2?"],
  "physics": ["physics q5: unit of force?", "physics q6: speed of light?"]
}
```

The texts are resolved back to `question_id`s via the `eval_question_link` table and the
matching rows in `eval_results` are flagged `is_reserved = 1`. Benchmarks default to the
reserved pool only (`BenchmarkRequest.reservedOnly = true`).

## Minimal example

A single inner `.json` file (the ZIP simply contains one or more of these):

```json
[
  {
    "question_id": 1,
    "question": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "answer": "B",
    "answer_index": 1,
    "category": "math",
    "pred": "B",
    "model_outputs": "2 + 2 = 4, which is option B. Final answer: B"
  },
  {
    "question_id": 2,
    "question": "What is the SI unit of force?",
    "options": ["joule", "newton", "watt", "pascal"],
    "answer": "B",
    "answer_index": 1,
    "category": "physics",
    "pred": "A",
    "cot_content": "Force is measured in newtons... answer: A"
  }
]
```
