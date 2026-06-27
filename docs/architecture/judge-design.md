# **Architectural Paradigms for DAG-Driven, Domain-Specialized AI Agent Evaluators**

The evaluation of autonomous artificial intelligence agents has historically relied upon outcome-based metrics and static benchmarking datasets. However, as agentic systems increasingly deploy complex, multi-step analytical trajectories and utilize external tool-calling mechanisms, conventional evaluation paradigms have become critically insufficient. Assessing an agent solely on its final output creates a phenomenon recognized in recent literature as the "high-score illusion," wherein an agent may arrive at the correct answer through flawed logic, hallucinated tool use, or spurious correlations.1 To accurately evaluate advanced autonomous agents, the evaluation mechanisms themselves must evolve into specialized, trajectory-aware systems capable of parsing complex deductive steps.

The design of a domain-specific, hierarchical agent evaluation tool requires synthesizing several cutting-edge computational frameworks. By structuring domain knowledge as a Directed Acyclic Graph (DAG), extracting highly granular ground-truth logical traces from advanced datasets such as MMLU-Pro, and employing advanced meta-prompting to generate dynamic grading rubrics, it is possible to construct a highly reliable, automated evaluative architecture. This architecture evaluates competing agent traces through pairwise comparisons, ultimately feeding into a probabilistic ranking engine. The following comprehensive analysis details the theoretical frameworks, data extraction strategies, rubric generation protocols, and bias mitigation architectures necessary to engineer this sophisticated taxonomic evaluation system.

## **Theoretical Foundations of Hierarchical Taxonomic Graphs**

The deployment of general-purpose language models across highly technical or specialized domains often results in degraded evaluation quality. Generalist evaluators lack the nuanced understanding required to assess expert-level analytical progression in fields such as advanced mathematics, quantum physics, or clinical medicine. To resolve this limitation, the evaluation space must be decomposed into a hierarchical taxonomy, routing evaluation tasks to specialized agent judges calibrated for specific, highly granular subdomains.

### **Directed Acyclic Graphs for Subject Specialization**

Recent advancements in multi-agent systems rely heavily on structured graph topologies to manage task decomposition and information flow. The Subject-based Directed Acyclic Graph (S-DAG) framework provides a definitive blueprint for this architecture.3 In this paradigm, the entirety of human knowledge—or the specific bounds of a benchmarking dataset—is initially modeled as a fully connected graph. Specialized algorithms, such as Graph Neural Networks, are then utilized to infer interdependencies between subjects, pruning the structure into a functional DAG.4

Within the context of an agent evaluation tool, a DAG structures the domains hierarchically. Nodes represent specific knowledge domains, while directed edges represent the prerequisite or supportive relationships between these domains. For example, a node representing abstract algebra would receive directed edges from nodes representing basic arithmetic and set theory. This structure reflects a support-to-dominant relationship, ensuring that the analytical flow is sequenced according to logical dependencies.4

When an evaluation query is submitted, the system traverses the DAG using query embeddings. The semantic vector of the incoming query is matched against the localized embeddings of the graph's nodes, routing the evaluation task to the most appropriate, granular subdomain.4 This dynamic traversal ensures that the evaluation is not handled by a monolithic generalist, but rather by an instantiated expert judge possessing domain-specific policies. This topological approach is fundamental to creating systems that can scale across diverse knowledge bases without losing the precision required for expert-level adjudication.

### **Dependency-Driven Information Flow and the Endogeneity Paradox**

The structural scaffolding provided by a DAG allows for endogeneity in specialization—meaning the system provides minimal structural constraints through fixed routing order while enabling full role autonomy for the specialized node.7 Unlike centralized orchestrators that can become computational bottlenecks, decentralized DAG routing allows agents to specialize dynamically.8 This paradigm shifts the operational burden from a single coordinating model to a distributed network of highly tuned specialists.

When the taxonomic tool identifies a specific subdomain node, the corresponding agent judge inherits context not only from the node itself but from its ancestral lineage in the DAG.9 For instance, a query routed to a molecular biology node inherits foundational grading axioms from the parent general biology node. This hierarchical inheritance enforces cross-domain consistency and ensures that high-level logical constraints are preserved even as the evaluation criteria become hyper-specific.9

The literature highlights several frameworks that utilize topological structures for agent coordination, each offering unique advantages for specialized task execution.

| Topological Framework | Architectural Characteristics | Primary Advantages for Evaluative Systems |
| :---- | :---- | :---- |
| **S-DAG** | Utilizes Graph Neural Networks to infer subject-level dependencies and routes queries to domain-specific nodes based on localized embeddings. | Enables fine-grained subject matching and ensures that evaluation policies are grounded in the specific requirements of the queried domain.3 |
| **AgentNet** | A decentralized, retrieval-augmented framework that allows agents to autonomously evolve capabilities within a DAG-structured network. | Removes centralized bottlenecks, fostering high fault tolerance and allowing localized judges to refine their expertise autonomously.8 |
| **MASFactory** | Compiles natural-language intents into executable multi-agent workflows using pure DAG structures for pipeline-style collaboration. | Facilitates the seamless translation of high-level evaluation requirements into structured, node-specific execution paths.11 |
| **MemTree** | Explicitly models parent-child and containment relationships, allowing top-down navigation for abstract themes and bottom-up summarization. | Ensures that granular evaluation criteria maintain coherence with overarching domain principles through strict hierarchical inheritance.12 |

Integrating these topological principles ensures that the AI Agent Judge taxonomic generation tool operates with maximum efficiency. By mapping incoming queries to specialized nodes, the system guarantees that the evaluating agent possesses the precise contextual background necessary to adjudicate complex analytical trajectories accurately.

## **Benchmark Extraction and Policy Induction**

To operationalize the specialized nodes within the DAG, each node requires domain-specific grading policies. These policies cannot be manually engineered at scale; they must be induced autonomously from high-quality benchmarking datasets. The MMLU-Pro dataset serves as an optimal substrate for this policy induction due to its rigorous structure, elimination of trivial questions, and emphasis on multi-step analytical processing.13

### **The Structural Architecture of Baseline Datasets**

The MMLU-Pro dataset expands upon previous massive multitask comprehension benchmarks to address model saturation and the plateauing of outcome-based evaluation.14 It encompasses over 12,000 rigorously curated questions spanning 14 broad domains, including biology, business, chemistry, computer science, economics, engineering, health, history, law, mathematics, philosophy, physics, and psychology.13 Crucially, the dataset provides highly granular sub-category metadata, perfectly mapping to the terminal nodes of a specialized DAG.15

Three architectural enhancements make this specific dataset uniquely suited for agent judge generation and policy induction. First, the dataset increases the answer choices from four to ten. This expansion reduces the probability of success through random guessing from twenty-five percent to exactly ten percent, drastically increasing the difficulty and ensuring that correct answers correlate strongly with correct analytical deductions.13 When generating policies, this widened option space provides a richer set of negative examples to train the evaluator on common failure modes.

Second, trivial and noisy questions present in older benchmarks have been systematically eliminated. During the dataset construction, questions that could be solved by smaller, less capable models via simple knowledge retrieval were filtered out, leaving problems that demand deliberate, complex deductive processing.14 Error analysis on top-performing models reveals that thirty-nine percent of errors on this dataset are due to flaws in the deductive process itself, rather than mere factual ignorance, highlighting its utility for training trajectory-aware judges.18

Third, the dataset demonstrates a high sensitivity to sequential logic traces. Unlike older benchmarks where direct answering often outperformed sequential processing, this advanced dataset shows that models utilizing step-by-step deduction achieve up to twenty percent higher performance, confirming that the dataset fundamentally measures procedural logic rather than rote memorization.13

### **Extracting Domain Axioms and Ground Truths**

To construct the judgment policy for a specific DAG node, the system must extract and analyze all questions associated with that node's corresponding source tag. The dataset schema provides several critical fields: the query, the ten potential answers, the ground-truth choice, and the highly detailed explanatory content field that outlines the optimal deductive path.15

The explanatory content field is of paramount importance for evaluating agent traces. It contains a step-by-step logical progression—ranging typically from one hundred and thirty to over one thousand characters—demonstrating exactly how a subject matter expert would arrive at the correct answer.15 For example, in an abstract algebra problem, the explanatory content explicitly details the theorems applied, the intermediate proofs, and the final deduction.15

By aggregating these explanatory traces across hundreds of queries within a single subdomain, the system can utilize a large language model to perform policy induction. The system analyzes the corpus of ground-truth trajectories and extracts the implicit domain axioms. For a mathematics node, the induced policy might prioritize strict adherence to order of operations and accurate theorem selection, whereas for a formal logic node, the policy might prioritize structural consistency and the avoidance of deductive fallacies. These extracted principles form the foundational instructions for the domain-specific agent judge.

| Dataset Component | Extraction Utility for Policy Induction | Operational Function in Evaluator Design |
| :---- | :---- | :---- |
| **Expanded Option Space** | Provides nine distinct incorrect vectors per query. | Utilized to map common domain-specific failure modes and train the judge to recognize hallucinated or flawed conclusions.13 |
| **Filtered Query Corpus** | Ensures all utilized queries require multi-step processing rather than simple retrieval. | Guarantees that the induced policy focuses on analytical depth rather than surface-level factual checking.17 |
| **Explanatory Content** | Delivers gold-standard, step-by-step deductions crafted by subject matter experts. | Serves as the absolute baseline for optimal trajectory mapping, allowing the judge to anchor its evaluations to verified expert logic.15 |
| **Granular Source Tags** | Categorizes data into highly specific sub-disciplines (e.g., college-level physics). | Enables the precise alignment of data clusters with the terminal nodes of the hierarchical DAG.15 |

The rigorous extraction of these components ensures that the resulting evaluation policy is not a generic set of guidelines, but a highly tuned, domain-specific regulatory framework. This process transforms a static benchmarking dataset into a dynamic training ground for specialized evaluative agents.

## **Advanced Meta-Prompting for Judge Generation**

Once the domain axioms are extracted from the dataset, they must be formalized into explicit grading instructions. Because the DAG may contain hundreds or thousands of granular subdomains, manually authoring these instructions is computationally and practically impossible. The system must employ automated meta-prompting protocols to generate highly discriminative evaluation criteria dynamically.

### **The Formal Mechanics of Meta-Prompting**

Meta-prompting represents a paradigm shift from traditional, content-centric prompt engineering to a structure-oriented approach. Rather than providing a model with specific instructions for a single task, meta-prompting provides the model with a structural framework detailing how to process an entire category of tasks.19 This approach shifts the focus from merely designing individual prompts to designing overarching systems for prompt creation and optimization.21

In advanced theoretical models, meta-prompting is formalized using mathematical category mappings. The space of all problem types represents one category, and the space of all structured prompts represents another. Meta-prompting acts as a functor that maps a task category to a specific prompt template, ensuring that the composition of sub-tasks logically maps to the composition of sub-prompts.22 This functorial property guarantees that if a complex evaluation task can be broken down into discrete sub-components, the meta-prompt can automatically generate modular instructions for each component.22

In practice, this means an overarching conductor model analyzes the taxonomy of the DAG and generates optimized, node-specific system prompts for each agent judge.21 By feeding the extracted benchmark queries and optimal explanatory traces into a meta-prompting engine, the system acts as an automated prompt engineer. It analyzes the specific failure modes common to the subdomain and iteratively refines the prompt template to instruct the agent judge on exactly what to penalize and what to reward.20

### **Role Engineering and Managerial Structures**

The efficacy of the generated judge relies heavily on the specificity of its assigned role. Studies have demonstrated that providing long, structured prompts dramatically improves an agent's ability to follow complex instructions without deviation.24 This technique, often referred to as the managerial approach, involves generating prompts that read more like detailed specification documents than simple queries.24

The meta-prompting engine utilizes the extracted domain axioms to construct these managerial documents for each DAG node. Rather than simply instructing the node to "evaluate the accuracy of the response," the generated prompt defines the specific pedagogical or analytical standards of that domain. For a node dedicated to software engineering, the meta-prompt might generate instructions requiring the judge to verify cyclomatic complexity, memory management, and adherence to specific design patterns. This level of hyper-specificity turns a general language model into a specialized problem-solver by pre-loading it with domain expertise and strict guardrails before it even begins the evaluation process.24

Furthermore, these prompts can be optimized continuously using evaluation loops. Automated frameworks utilize the outcomes of previous evaluations to refine the system prompt iteratively. If an agent judge consistently fails to penalize a specific type of logical fallacy within a subdomain, the meta-prompting engine analyzes the failure and automatically generates an updated prompt rule to close the evaluative gap.25 This recursive optimization ensures that the agent judges become increasingly precise over time.

## **Automated Grading Criteria Synthesis and Reward Modeling**

While meta-prompts establish the overarching behavior and persona of the judge, the specific grading criteria establish the quantitative scale. Transitioning from implicit quality definitions to explicit, multidimensional criteria is essential for reducing variance and mitigating subjective biases.26 The creation of rigorous, automated grading frameworks is central to deploying scalable evaluative architectures.

### **Contrastive Synthesis of Evaluation Criteria**

The generation of highly discriminative grading criteria cannot rely solely on examining optimal answers. The Contrastive Rubric Generation methodology is highly effective for synthesizing robust evaluation scales.27 This process derives explicit constraints and implicit quality standards by directly contrasting preferred responses—such as the gold-standard traces extracted from the benchmark—against rejected or flawed responses.27

By analyzing the precise deviations between an optimal trajectory and a flawed trajectory, the contrastive algorithm isolates the critical junctures where logic typically fails within a specific domain. The system then automatically drafts grading criteria that specifically target these identified vulnerabilities. This ensures that the resulting evaluation scale is not merely a generic assessment of fluency, but a highly targeted diagnostic tool designed to uncover domain-specific analytical errors. The generated criteria are subsequently filtered via preference-label consistency, utilizing rejection sampling techniques to eliminate any ambiguous or noisy grading parameters.27

### **Context-Aware Reward Modeling Protocols**

To further enhance the reliability of the generated grading criteria, the system must integrate principles from Context-Aware Reward Modeling (CARMO). In standard automated evaluation, static grading scales often lead to systemic exploitation, where an agent learns to optimize for superficial features—such as generating excessively long lists or mimicking authoritative terminology—to achieve high scores without producing substantively accurate content.29

CARMO mitigates this vulnerability by generating dynamic, context-relevant criteria tailored specifically to the individual user query prior to scoring.29 Instead of applying a universal grading scale to every query within a subdomain, the node's agent judge dynamically adjusts its evaluation parameters based on the specific constraints of the incoming problem. If a query requires the derivation of a mathematical proof, the dynamic criteria instantly assign higher weights to sequential validity and formulaic accuracy, actively suppressing the weight of narrative prose. This context-aware generation guarantees that the agent judge is strictly anchored to the genuine requirements of the specific query, systematically neutralizing superficial optimization strategies.29

| Criteria Synthesis Architecture | Operational Mechanism | Impact on Evaluation Quality |
| :---- | :---- | :---- |
| **Contrastive Generation** | Derives parameters by analyzing the differences between optimal and flawed analytical trajectories. | Ensures grading scales target specific, recurring errors within a domain, highly increasing discriminative power.27 |
| **Context-Aware Adaptation** | Dynamically adjusts evaluation weights based on the specific parameters of the incoming query. | Prevents superficial exploitation by ensuring the evaluation focuses strictly on query-relevant analytical processes.29 |
| **Retrieval-Augmented Criteria** | Retrieves domain knowledge from related, previously evaluated queries to enrich current grading scales. | Improves interpretability and ensures that grading parameters remain consistent with historical domain standards.32 |
| **Coarse-to-Fine Generation** | Hierarchically structures criteria from broad principles down to granular, specific execution checks. | Provides highly detailed supervision for the evaluator, ensuring no aspect of the analytical trajectory is overlooked.33 |

### **Boundary Optimization and Iterative Refinement**

Specialized domains often require boundary-focused optimization to handle highly nuanced edge cases. Frameworks detailed in recent literature demonstrate the efficacy of refining automated grading scales through iterative reflection and human-in-the-loop validation.34

In boundary-focused optimization, the generation system identifies boundary pairs—two analytical trajectories that are semantically and structurally similar but diverge on a critical, subtle deductive step.35 The system formulates highly discriminative rationales explaining exactly why one trajectory satisfies the quality threshold while the other fails. By encoding these boundary rationales into the agent judge's context window, the judge becomes highly adept at distinguishing between genuinely exceptional deduction and fundamentally flawed logic masquerading as competence.34

Furthermore, comprehensive frameworks like Autorubric provide production infrastructure for these processes, supporting binary, ordinal, and nominal criteria with configurable weights.36 Such frameworks implement reliability metrics drawn from psychometrics, including distribution-level tests and correlation coefficients, to continuously monitor and validate the consistency of the generated evaluation criteria.36 This rigorous mathematical validation ensures that the automated judge behaves indistinguishably from a calibrated human expert.

## **Trajectory-Aware Pairwise Evaluation Methodologies**

With the taxonomic DAG populated by specialized agent judges armed with dynamically generated grading criteria, the system is prepared to evaluate incoming AI agent traces. However, the methodology by which these traces are evaluated dictates the ultimate validity of the ranking engine. Assessing complex, multi-step agent workflows requires abandoning single-turn outcome verification in favor of comprehensive, pairwise trajectory analysis.

### **Deconstructing the High-Score Illusion**

Traditional automated evaluations rely heavily on simplistic metrics that assess whether the final generated token matches a predefined ground-truth answer. In complex, multi-step environments, this creates the aforementioned high-score illusion.1 An agent might stumble upon the correct final output through a sequence of logical fallacies, or through sheer coincidence in a vast search space.2

To evaluate the true capability of an agent, the judge must assess the entire problem-solving sequence. The TRACE (Trajectory-Aware Comprehensive Evaluation) framework establishes the standard for this methodology.1 Rather than comparing the final output to a ground truth, this framework conducts a multi-faceted analysis of the intermediate steps, the evidence retrieved from the environment, and the deductive transitions made between states.39

The evaluation of these sequential traces operates across four fundamental dimensions, ensuring a holistic assessment of the agent's capabilities 41:

| Evaluation Dimension | Description and Analytical Focus |
| :---- | :---- |
| **Factuality** | Assesses whether the information retrieved, referenced, or generated within intermediate steps aligns strictly with established domain knowledge and the provided context. |
| **Validity** | Evaluates the soundness of the transitions between execution steps. Ensures that conclusions directly and logically follow from the preceding premises without relying on inferential leaps. |
| **Coherence** | Measures the structural flow of the trajectory. Penalizes contradictory statements, looping behaviors, or sudden, unexplained shifts in strategic direction. |
| **Utility** | Determines whether the intermediate actions actively contribute to solving the overarching query, heavily penalizing unnecessary tool calls or redundant computational sequences. |

By utilizing the optimal explanatory content extracted from the benchmark dataset as the structural baseline for these dimensions, the agent judge can map the evaluated agent's trajectory against an idealized path. The judge is instructed to heavily penalize deviations in validity or utility, even if the agent manages to output the correct final string. This ensures that the ranking engine rewards genuine analytical competence rather than stochastic success.

### **The Mathematical Superiority of Pairwise Comparisons**

To establish a probabilistic ranking system, the agent judge must quantify the relative quality of two competing trajectories. State-of-the-art research unequivocally demonstrates that pairwise comparative assessment is vastly superior to pointwise scoring, wherein an output is graded in isolation on a numerical scale.43

Pointwise scoring suffers from severe calibration degradation. Large language models struggle to maintain absolute consistency across arbitrary numerical scales, frequently exhibiting a tendency to cluster scores artificially around the median.45 This central tendency bias effectively destroys the discriminative power of the evaluation, rendering the resulting rankings statistically meaningless. In sharp contrast, pairwise comparison forces a direct, binary decision—or a definitive tie—between two discrete options. This relative evaluation aligns significantly closer with verified human preferences and exhibits substantially higher positional and logical consistency across repeated trials.43

In a pairwise trajectory preference task, the specialized agent judge receives the original query, the dynamically generated criteria, and the full execution sequences of both candidate agents simultaneously.48 The judge must analyze the trajectories step-by-step, cross-referencing the logical validity of each agent's approach, before outputting a definitive preference verdict accompanied by a detailed justification rationale.

To translate these pairwise judgments into a robust ranking architecture, the system relies on probabilistic mathematics, specifically the Bradley-Terry model.49 This model quantifies the relative quality of the agents based on the win-loss ratios derived from the continuous pairwise comparisons. Through maximum likelihood estimation, the system calculates and updates the coefficients for each agent, allowing for the continuous, dynamic updating of the leaderboard as new agents and novel traces are evaluated against the taxonomic baseline.49

### **Integrating Pointwise Analysis within Pairwise Frameworks**

While pairwise comparison is the mathematically optimal framework for determining ultimate preference, the simultaneous presentation of two complex traces can occasionally cause the judge to over-index on superficial differences—such as formatting or length—rather than their fundamental architectural merits. To optimize the evaluation, researchers have introduced hybrid protocols that integrate pointwise analysis strictly as a precursor to the pairwise decision.51

Under these advanced protocols, the agent judge is first instructed to perform an atomic, isolated critique of the first trace, evaluating it strictly against the multidimensional criteria. It then performs an entirely isolated critique of the second trace. Only after generating these independent, highly granular rationales is the judge permitted to execute the comparative pairwise judgment. This operational sequencing forces the judge to ground its final decision in the substantive, step-by-step analysis generated during the isolated phase, drastically reducing the likelihood of superficial or aesthetically driven decision-making.37

## **Mitigating Systemic Vulnerabilities in Automated Evaluators**

The deployment of automated evaluation architectures introduces significant systemic vulnerabilities. Advanced models exhibit documented, highly predictable biases when acting in an evaluative capacity. If left unmitigated, these biases compromise the integrity of the pairwise comparisons, leading to a contaminated and statistically invalid ranking engine. The taxonomic evaluation tool must implement robust architectural defenses against these failure modes at every level of the DAG.

### **Combating Presentation and Positional Biases**

Automated judges are highly susceptible to presentation biases that mimic human cognitive flaws, fundamentally skewing the evaluation of complex trajectories:

The most pervasive of these is verbosity bias. Evaluator models consistently demonstrate a strong preference for longer responses, improperly conflating word count and structural complexity with thoroughness and quality.45 Under this bias, a concise, perfectly accurate analytical trace will frequently lose to a sprawling, repetitive sequence filled with irrelevant filler data. To mitigate this, the dynamically generated grading criteria must explicitly enforce length penalties and reward brevity. The meta-prompt must instruct the judge to assess information density and penalize traces that violate the utility dimension by including unnecessary computational steps or redundant narrative prose.37

Equally problematic is positional bias. When presented with two options simultaneously, the judge often exhibits a systemic, mathematically quantifiable preference for either the first or the second option, entirely independent of the actual content.45 To neutralize this vulnerability, the system must implement automated position-consistency checking, commonly referred to as option shuffling. Every pairwise comparison must be executed twice, with the order of the traces reversed during the second pass. If the judge selects the first trace during the initial pass, but switches its preference to the newly positioned trace during the swap, the system registers an unresolvable tie or flags the evaluation for deeper scrutiny, preventing arbitrary positional preferences from influencing the ranking engine.37

Furthermore, judges frequently succumb to authority or bandwagon biases. They inherently reward outputs that contain fabricated citations, a highly confident tone, or claims of majority consensus, mistaking the superficial appearance of rigor for actual factual correctness.52 Mitigation requires the evaluation to be heavily anchored to the verified reference material extracted from the baseline dataset. Additionally, external bias detection modules can be deployed. These plug-in modules independently review the judge's generated rationale, detecting instances where the judge rewarded tone over substance and forcing a self-correction loop before the final verdict is logged.54 Research indicates that deploying such detectors can improve evaluation accuracy by nearly twenty percent while significantly enhancing positional consistency.54

### **Addressing Preference Leakage and Model Relatedness**

A significantly more insidious vulnerability in automated evaluation is preference leakage, often referred to as self-enhancement bias. When an automated judge evaluates an output generated by an agent that utilizes the same underlying algorithmic architecture or belongs to the same model family, it exhibits a systemic, disproportionate preference for that output.53 The judge implicitly recognizes and favors its own latent linguistic patterns, phrasing styles, and structural organizations.

Because the taxonomic generation tool will inevitably utilize specific foundation models to instantiate its nodes, it runs the severe risk of unfairly elevating competing agents that share that foundation model, destroying the neutrality of the ranking system.55 This contamination is pervasive and exceptionally difficult to detect using standard validation metrics.55

To mitigate preference leakage, the architecture must enforce absolute cryptographic anonymity, stripping all identifying metadata, distinct formatting markers, and system tags from the agent traces prior to evaluation.53 Furthermore, utilizing an ensemble approach—where a panel of judges utilizing entirely distinct, heterogeneous foundation models cast independent votes to reach a consensus—can mathematically dilute the impact of preference leakage from any single model family.53

### **Preventing Rubric-Induced Preference Drift**

As the system relies on the continuous, automated generation and optimization of grading criteria, it is highly susceptible to Rubric-Induced Preference Drift (RIPD). This phenomenon occurs when natural, seemingly harmless edits to the criteria during the meta-prompting phase subtly shift the judge's preferences away from the true domain objective.57 Over time, these slight deviations compound exponentially, causing the judge to internalize a skewed evaluation policy that entirely misaligns with human expert judgment, sometimes reducing target-domain accuracy by nearly thirty percent.57

| Systemic Vulnerability | Primary Manifestation | Architectural Defense Mechanism |
| :---- | :---- | :---- |
| **Verbosity Bias** | Disproportionately rewarding lengthy, redundant traces over concise, accurate deductions. | Explicitly coding information density requirements and length penalties into the dynamically generated criteria.37 |
| **Positional Bias** | Systemic preference for the first or second option in a pairwise assessment regardless of content. | Implementing mandatory position-consistency checking via automated option shuffling across all evaluation passes.37 |
| **Preference Leakage** | Favoring agent traces generated by models sharing the evaluator's underlying architecture. | Enforcing absolute trace anonymity and deploying multi-model ensemble voting panels to dilute specific algorithmic preferences.53 |
| **Rubric-Induced Drift** | Gradual misalignment of grading criteria due to unmonitored, automated prompt optimizations. | Executing continuous regression testing against immutable, expert-verified baseline traces to reject misaligned criteria updates.57 |

To prevent this drift, the system must continuously calibrate its generated criteria against a static, immutable baseline. The expert-verified explanatory content extracted from the foundational benchmark serves as this unyielding anchor. During the criteria generation phase, the system must perform periodic regression testing, ensuring that the newly updated criteria still correctly rank the gold-standard baseline trace above known, sophisticated distractors.57 If a criteria update causes the judge to fail this baseline test, the update is immediately rejected, preserving the integrity of the domain-specific policy.

## **Synthesis of the End-to-End Evaluation Architecture**

To fulfill the complex requirements of generating a highly specialized, reliable evaluation tool, the state-of-the-art research dictates a highly structured, sequential operational flow. This flow integrates topological routing, rigorous data extraction, dynamic criteria generation, and trajectory-aware evaluation into a single, cohesive architecture.

The process begins with Taxonomic Initialization. The system ingests the foundational dataset, mapping its diverse domains and granular sub-categorizations into a hierarchical Directed Acyclic Graph. Nodes are established for every distinct knowledge domain, and relationship edges are mapped to ensure logical inheritance.3 This creates the physical topology upon which the evaluators will reside.

Following initialization, the system executes Policy Extraction. For a given node, the system aggregates the associated benchmark queries, the expanded answer choices, and the crucial expert-verified explanatory traces.13 An analytical model parses this corpus to induce the implicit rules, axioms, and logical constraints governing that specific subdomain, transitioning the raw data into foundational behavioral guidelines.59

These guidelines are then subjected to Dynamic Criteria Generation. Utilizing advanced meta-prompting frameworks and contrastive generation techniques, the system abstracts the extracted axioms into an explicit, multi-dimensional grading scale.20 This scale is contextually adjusted per query to prevent superficial exploitation and is continuously optimized using boundary exemplars and regression testing to prevent drift.31

With the nodes fully operational, the system enters the Agent Evaluation Execution phase. When tasked with comparing two AI agent traces, the system utilizes query embeddings to route the task through the DAG to the appropriate specialized judge.4 The judge utilizes a hybrid evaluation protocol, first independently analyzing the factuality, validity, coherence, and utility of each trace in isolation.38

Finally, the system finalizes the process through Pairwise Judgment and Probabilistic Integration. The judge executes a direct pairwise comparison of the two traces, heavily fortified by automated position swapping and strict length penalties.43 The judge outputs a definitive preference accompanied by a structured rationale. This binary result is fed into the probabilistic mathematical engine, which recalculates the maximum likelihood estimation coefficients, seamlessly updating the agents' global rankings within the specific domain.49

This architectural synthesis represents the absolute frontier of automated evaluation methodologies. By abandoning monolithic, generalist evaluators in favor of a topologically routed network of specialized judges, the system ensures that evaluation policies are inherently tied to the rigorous, multi-step demands of specific domains. Leveraging high-fidelity foundational datasets allows for the automated synthesis of highly discriminative criteria. When coupled with strict pairwise evaluation protocols that assess the entirety of an agent's analytical trajectory—and fortified by aggressive mitigation techniques against systemic biases—the resulting architecture produces a probabilistic ranking engine of unprecedented accuracy, transparency, and alignment with expert human judgment.

#### **Sources des citations**

1. TRACE: Trajectory-Aware Comprehensive Evaluation for Deep Research Agents \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2602.21230v1](https://arxiv.org/html/2602.21230v1)
2. \[2604.11996\] Filtered Reasoning Score: Evaluating Reasoning Quality on a Model's Most-Confident Traces \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/abs/2604.11996](https://arxiv.org/abs/2604.11996)
3. S-DAG: A Subject-Based Directed Acyclic Graph for Multi-Agent Heterogeneous Reasoning, consulté le mai 5, 2026, [https://arxiv.org/html/2511.06727v1](https://arxiv.org/html/2511.06727v1)
4. S-DAG: A Subject-Based Directed Acyclic Graph for Multi-Agent Heterogeneous Reasoning, consulté le mai 5, 2026, [https://ojs.aaai.org/index.php/AAAI/article/view/40180/44141](https://ojs.aaai.org/index.php/AAAI/article/view/40180/44141)
5. S-DAG: A Subject-Based Directed Acyclic Graph for Multi-Agent Heterogeneous Reasoning, consulté le mai 5, 2026, [https://www.alphaxiv.org/overview/2511.06727v1](https://www.alphaxiv.org/overview/2511.06727v1)
6. AI Agent Routing: Tutorial & Best Practices, consulté le mai 5, 2026, [https://www.patronus.ai/ai-agent-development/ai-agent-routing](https://www.patronus.ai/ai-agent-development/ai-agent-routing)
7. Drop the Hierarchy and Roles: How Self-Organizing LLM Agents Outperform Designed Structures \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2603.28990v1](https://arxiv.org/html/2603.28990v1)
8. AgentNet: Decentralized Evolutionary Coordination for LLM-based Multi-Agent Systems, consulté le mai 5, 2026, [https://neurips.cc/virtual/2025/poster/115584](https://neurips.cc/virtual/2025/poster/115584)
9. MagicAgent: Towards Generalized Agent Planning \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2602.19000v2](https://arxiv.org/html/2602.19000v2)
10. Ontology-Driven Multi-Agent System for Cross-Domain Art Translation \- MDPI, consulté le mai 5, 2026, [https://www.mdpi.com/1999-5903/17/11/517](https://www.mdpi.com/1999-5903/17/11/517)
11. MASFactory: A Graph-centric Framework for Orchestrating LLM-Based Multi-Agent Systems with Vibe Graphing \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2603.06007v1](https://arxiv.org/html/2603.06007v1)
12. Graph-based Agent Memory: Taxonomy, Techniques, and Applications \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2602.05665v1](https://arxiv.org/html/2602.05665v1)
13. MMLU-Pro Leaderboard \- a Hugging Face Space by TIGER-Lab, consulté le mai 5, 2026, [https://huggingface.co/spaces/TIGER-Lab/MMLU-Pro](https://huggingface.co/spaces/TIGER-Lab/MMLU-Pro)
14. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2406.01574v4](https://arxiv.org/html/2406.01574v4)
15. TIGER-Lab/MMLU-Pro · Datasets at Hugging Face, consulté le mai 5, 2026, [https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro)
16. MMLU-Pro Explained: The Advanced AI Benchmark for LLMs \- IntuitionLabs, consulté le mai 5, 2026, [https://intuitionlabs.ai/pdfs/mmlu-pro-explained-the-advanced-ai-benchmark-for-llms.pdf](https://intuitionlabs.ai/pdfs/mmlu-pro-explained-the-advanced-ai-benchmark-for-llms.pdf)
17. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2406.01574v3](https://arxiv.org/html/2406.01574v3)
18. MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2406.01574v6](https://arxiv.org/html/2406.01574v6)
19. What is Meta Prompting? \- IBM, consulté le mai 5, 2026, [https://www.ibm.com/think/topics/meta-prompting](https://www.ibm.com/think/topics/meta-prompting)
20. Meta Prompting: Use LLMs to Optimize Prompts for AI Apps & Agents \- Comet, consulté le mai 5, 2026, [https://www.comet.com/site/blog/meta-prompting/](https://www.comet.com/site/blog/meta-prompting/)
21. What Is Meta Prompting? Definition & Simple Guide \- Truefoundry, consulté le mai 5, 2026, [https://www.truefoundry.com/glossary/meta-prompting](https://www.truefoundry.com/glossary/meta-prompting)
22. Meta Prompting Guide: Automated LLM Prompt Engineering | IntuitionLabs, consulté le mai 5, 2026, [https://intuitionlabs.ai/articles/meta-prompting-automated-llm-prompt-engineering](https://intuitionlabs.ai/articles/meta-prompting-automated-llm-prompt-engineering)
23. Automatic system prompt generation from a task \+ data : r/LLMDevs \- Reddit, consulté le mai 5, 2026, [https://www.reddit.com/r/LLMDevs/comments/1lxz803/automatic\_system\_prompt\_generation\_from\_a\_task/](https://www.reddit.com/r/LLMDevs/comments/1lxz803/automatic_system_prompt_generation_from_a_task/)
24. How Meta-Prompting and Role Engineering Are Unlocking the Next Generation of AI Agents, consulté le mai 5, 2026, [https://rediminds.com/future-edge/how-meta-prompting-and-role-engineering-are-unlocking-the-next-generation-of-ai-agents/](https://rediminds.com/future-edge/how-meta-prompting-and-role-engineering-are-unlocking-the-next-generation-of-ai-agents/)
25. Arize: System Prompt Learning for Coding Agents Using LLM-as-Judge Evaluation \- ZenML, consulté le mai 5, 2026, [https://www.zenml.io/llmops-database/system-prompt-learning-for-coding-agents-using-llm-as-judge-evaluation](https://www.zenml.io/llmops-database/system-prompt-learning-for-coding-agents-using-llm-as-judge-evaluation)
26. RubricBench: Aligning Model-Generated Rubrics with Human Standards \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2603.01562v1](https://arxiv.org/html/2603.01562v1)
27. OpenRubrics: Towards Scalable Synthetic Rubric Generation for Reward Modeling and LLM Alignment \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2510.07743v2](https://arxiv.org/html/2510.07743v2)
28. Rubric-Based Evaluations & LLM-as-a-Judge — Methodologies, Biases, and Empirical Validation in Domain-Specific Contexts. | by Adnan Masood, PhD. | Apr, 2026 | Medium, consulté le mai 5, 2026, [https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80](https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80)
29. CARMO: Dynamic Criteria Generation for Context Aware Reward Modelling \- ACL Anthology, consulté le mai 5, 2026, [https://aclanthology.org/2025.findings-acl.114.pdf](https://aclanthology.org/2025.findings-acl.114.pdf)
30. \[Paper Note\] CARMO: Dynamic Criteria Generation for Context-Aware Reward Modelling, Taneesh Gupta+, ACL'25 Findings, 2024.10 · Issue \#4509 · AkihikoWatanabe/paper\_notes \- GitHub, consulté le mai 5, 2026, [https://github.com/AkihikoWatanabe/paper\_notes/issues/4509](https://github.com/AkihikoWatanabe/paper_notes/issues/4509)
31. arXiv:2410.21545v2 \[cs.CL\] 17 Feb 2025, consulté le mai 5, 2026, [https://arxiv.org/pdf/2410.21545](https://arxiv.org/pdf/2410.21545)
32. RubricRAG: Towards Interpretable and Reliable LLM Evaluation via Domain Knowledge Retrieval for Rubric Generation \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2603.20882v1](https://arxiv.org/html/2603.20882v1)
33. RubricHub: A Comprehensive and Highly Discriminative Rubric Dataset via Automated Coarse-to-Fine Generation \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2601.08430v1](https://arxiv.org/html/2601.08430v1)
34. LLM-Based Automated Grading with Human-in-the-Loop \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2504.05239v3](https://arxiv.org/html/2504.05239v3)
35. Optimizing In-Context Demonstrations For Llm-Based Automated Grading \- Stanford SCALE Initiative, consulté le mai 5, 2026, [https://scale.stanford.edu/ai/repository/optimizing-context-demonstrations-llm-based-automated-grading](https://scale.stanford.edu/ai/repository/optimizing-context-demonstrations-llm-based-automated-grading)
36. Autorubric: A Unified Framework For Rubric-Based Llm Evaluation \- Stanford SCALE Initiative, consulté le mai 5, 2026, [https://scale.stanford.edu/ai/repository/autorubric-unified-framework-rubric-based-llm-evaluation](https://scale.stanford.edu/ai/repository/autorubric-unified-framework-rubric-based-llm-evaluation)
37. Autorubric: A Unified Framework for Rubric-Based LLM Evaluation \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2603.00077v1](https://arxiv.org/html/2603.00077v1)
38. Evaluating Step-by-step Reasoning Traces: A Survey \- ACL Anthology, consulté le mai 5, 2026, [https://aclanthology.org/2025.findings-emnlp.94.pdf](https://aclanthology.org/2025.findings-emnlp.94.pdf)
39. Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents, consulté le mai 5, 2026, [https://openreview.net/forum?id=chLlLbI7de](https://openreview.net/forum?id=chLlLbI7de)
40. \[2510.02837\] Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/abs/2510.02837](https://arxiv.org/abs/2510.02837)
41. Evaluating Step-by-step Reasoning Traces: A Survey \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2502.12289v2](https://arxiv.org/html/2502.12289v2)
42. Evaluating Step-by-step Reasoning Traces: A Survey \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2502.12289v1](https://arxiv.org/html/2502.12289v1)
43. A Survey on LLM-as-a-Judge \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2411.15594v3](https://arxiv.org/html/2411.15594v3)
44. A Survey on LLM-as-a-Judge \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2411.15594v4](https://arxiv.org/html/2411.15594v4)
45. LLM-as-a-Judge: How to Build Reliable, Scalable Evaluation for LLM Apps and Agents, consulté le mai 5, 2026, [https://www.comet.com/site/blog/llm-as-a-judge/](https://www.comet.com/site/blog/llm-as-a-judge/)
46. A Survey on LLM-as-a-Judge \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2411.15594v6](https://arxiv.org/html/2411.15594v6)
47. A Survey on LLM-as-a-Judge \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2411.15594v1](https://arxiv.org/html/2411.15594v1)
48. Aligning Agents via Planning: A Benchmark for Trajectory-Level Reward ModelingCode and data will be released after corporate approval. \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2604.08178v1](https://arxiv.org/html/2604.08178v1)
49. BrowserArena: Evaluating LLM Agents on Real-World Web Navigation Tasks \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2510.02418v2](https://arxiv.org/html/2510.02418v2)
50. From Replication to Redesign: Exploring Pairwise Comparisons for LLM-Based Peer Review \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2506.11343v1](https://arxiv.org/html/2506.11343v1)
51. The Comparative Trap: Pairwise Comparisons Amplifies Biased Preferences of LLM Evaluators \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2406.12319v4](https://arxiv.org/html/2406.12319v4)
52. Domain-Specific LLM Evaluation: Why Generic Rubrics Fall Short \- Galileo AI, consulté le mai 5, 2026, [https://galileo.ai/blog/domain-specific-llm-evaluation-expert-annotations](https://galileo.ai/blog/domain-specific-llm-evaluation-expert-annotations)
53. Exploring LLM-as-a-Judge \- Weights & Biases \- Wandb, consulté le mai 5, 2026, [https://wandb.ai/site/articles/exploring-llm-as-a-judge/](https://wandb.ai/site/articles/exploring-llm-as-a-judge/)
54. NeurIPS Poster Any Large Language Model Can Be a Reliable Judge: Debiasing with a Reasoning-based Bias Detector, consulté le mai 5, 2026, [https://neurips.cc/virtual/2025/poster/115702](https://neurips.cc/virtual/2025/poster/115702)
55. LLM-as-a-judge, consulté le mai 5, 2026, [https://llm-as-a-judge.github.io/](https://llm-as-a-judge.github.io/)
56. When AIs Judge AIs: The Rise of Agent-as-a-Judge Evaluation for LLMs \- arXiv, consulté le mai 5, 2026, [https://arxiv.org/html/2508.02994v1](https://arxiv.org/html/2508.02994v1)
57. Daily Papers \- Hugging Face, consulté le mai 5, 2026, [https://huggingface.co/papers?q=rubric](https://huggingface.co/papers?q=rubric)
58. Demystifying evals for AI agents \- Anthropic, consulté le mai 5, 2026, [https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
59. Evaluating Large Language Models' Abilities to Process and Understand Technical Policy Reports | RAND, consulté le mai 5, 2026, [https://www.rand.org/pubs/research\_reports/RRA4269-1.html](https://www.rand.org/pubs/research_reports/RRA4269-1.html)
60. A Comprehensive Evaluation of Inductive Reasoning Capabilities and Problem Solving in Large Language Models \- ACL Anthology, consulté le mai 5, 2026, [https://aclanthology.org/2024.findings-eacl.22.pdf](https://aclanthology.org/2024.findings-eacl.22.pdf)