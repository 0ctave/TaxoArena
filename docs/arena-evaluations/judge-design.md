# LLM Pairwise Judge Design & Rubric Synthesis

This document details the design of the **domain-specialized LLM judges** in **TaxoArena**. It explains the superiority of pairwise comparative assessment over pointwise grading, the structure of trajectory evaluations, and the automated contrastive synthesis of grading rubrics.

---

## 1. Pointwise vs. Pairwise Evaluation

In automated LLM evaluation, two primary methodologies exist:
1.  **Pointwise Evaluation**: A single model trajectory is graded in isolation (e.g., scoring from $1$ to $10$).
2.  **Pairwise Comparative Evaluation**: A judge model is shown two competing trajectories (Model A and Model B) for the same query and must choose a winner (or declare a tie).

### Calibration Degradation in Pointwise Scoring
Pointwise scoring suffers from **calibration degradation**. Large Language Models struggle to maintain a consistent absolute numerical scale across different domains and over time. They exhibit a strong **central tendency bias** (artificial clustering of scores around the median, e.g., 7 or 8) and **leniency bias** (hesitancy to assign low scores). This lack of variance degrades the statistical power of the evaluation, making ranking leaderboards unstable.

### Pairwise Comparison
Pairwise evaluation forces a relative choice. Since LLM judges are much better at comparing two options than assigning absolute scores, this approach maps closely to human preferences and demonstrates high positional and logical consistency. Order bias (preferring Model A simply because it was shown first) is mitigated by evaluating each pair twice with positions flipped ($A$ vs $B$ and $B$ vs $A$) and requiring agreement for a win.

---

## 2. Trajectory-Aware Evaluation vs. Outcome Verification

Evaluating autonomous agents based solely on their final answers creates a **high-score illusion**. An agent might arrive at the correct final token through flawed logic, tool hallucination, or accidental correlation.

TaxoArena implements a **trajectory-aware evaluation** paradigm. The judge evaluates the entire problem-solving sequence across four dimensions:

| Dimension | Analytical Focus |
| :--- | :--- |
| **Factuality** | Do intermediate assertions align with domain knowledge and context? |
| **Validity** | Are the logical transitions sound? Does each step flow from the previous? |
| **Coherence** | Is the trajectory free from self-contradictions and infinite loops? |
| **Utility** | Do intermediate tool calls directly contribute to solving the query? |

### Anchoring to Explanatory Ground-Truth Traces
To guide this evaluation, TaxoArena extracts the `explanatory_content` field from the MMLU-Pro benchmark. This field contains a step-by-step logical trace (typically $130 \dots 1000+$ characters) written by a subject matter expert. The judge model uses this expert trace as an absolute baseline, comparing the candidate agents' execution steps against this gold-standard reasoning path rather than just validating the final choice.

---

## 3. Automated Rubric & Prompt Synthesis

Because the taxonomy DAG contains dozens of granular subdomains, manual authoring of grading rubrics is impossible. TaxoArena automates prompt and rubric generation through **Meta-Prompting**.

### Contrastive Rubric Generation
To compile the grading rules for a leaf node $N$, the system contrasts preferred trajectories (gold-standard traces) with rejected trajectories (known incorrect model answers from the dataset). The conductor LLM identifies the critical junctures where reasoning typically fails in that specific subdomain and compiles these into a set of explicit rules.

### Context-Aware Reward Modeling (CARMO)
Rather than using a generic rubric for all queries within a domain, the judge dynamically adjusts its grading weights per query before scoring:
*   If a query demands a mathematical derivation, the judge dynamically shifts weight to step-by-step formulaic correctness.
*   If a query is conceptual, the judge shifts weight to argument consistency and terminology precision.

### Prompt Template Structure
The generated system prompt for a specialized judge at node $N$ follows a structured blueprint:

```markdown
You are a domain-specialized academic judge in [Domain Label].
Your task is to adjudicate a pairwise contest between two AI agents solving a query in this domain.

[ induced domain axioms: e.g., "In Abstract Algebra, enforce strict group property proofs..." ]

EVALUATION BASELINE (Expert Trace):
[ ground truth explanation ]

CANDIDATE TRAJECTORIES:
Agent 1: [ trajectory 1 ]
Agent 2: [ trajectory 2 ]

Grading Rubric:
1. Deductive Validity (0-3 pts)
2. Tool Use Precision (0-2 pts)
3. Step Coherence (0-2 pts)

Output your step-by-step comparison, assign a final verdict (Winner: Agent 1 / Agent 2 / TIE), and state your confidence score [0.0 - 1.0].
```

---

## 🔗 Related Code References
*   [TaxonomyBenchmarkService](../../src/main/kotlin/taxonomy/service/TaxonomyBenchmarkService.kt): Handles matchmaking execution, runs pairwise comparisons, and parses judge outputs.
*   [TaxoPrompts](../../src/main/kotlin/taxonomy/prompts/TaxoPrompts.kt): Contains the template builders for judge prompt synthesis.
