# Terminal User Interface (TUI) Dashboard & Visualization

This document details the layout, panel organization, hotkey navigation, and taxonomy visualization components of the **TaxoArena** Terminal User Interface (TUI).

---

## 1. TUI Panel Architecture

The TaxoArena TUI is built using Kotlin and a text-based console interface library. It provides a real-time, responsive control dashboard divided into several distinct panels:

```
┌────────────────────────────────────────────────────────────────────────┐
│  TaxoArena Dashboard v1.0   |   Status: RUNNING BENCHMARK   | Snap: A  │
├───────────────────────────────┬────────────────────────────────────────┤
│  DAG TREE VIEW                │  LEADERBOARD PANEL (Selected Node)     │
│  ├─ Root                      │  Selected: Quantum Mechanics           │
│  │  ├─ Physics (q=234)        │  1. GPT-4o        | score:  2.13 (±0.2)│
│  │  │  ├─ Quantum (q=45)      │  2. Claude 3.5    | score:  1.98 (±0.2)│
│  │  │  └─ Relat. (q=50)       │  3. Gemini 1.5    | score: -0.15 (±0.3)│
│  │  └─ Math (q=120)           │  4. Llama 3       | score: -3.96 (±0.4)│
├───────────────────────────────┴────────────────────────────────────────┤
│  LIVE LOGS PANEL                                                       │
│  15:02:11 [Fitter] Starting level-by-level parallel vMF/NiW fitting... │
│  15:02:13 [Scheduler] Bootstrap pass: 12 matches scheduled             │
├────────────────────────────────────────────────────────────────────────┤
│  [ENTER] Select  [TAB] Switch Pane  [L] Expand  [R] Judge  [S] Snapshot│
└────────────────────────────────────────────────────────────────────────┘
```

### Main Panels
1.  **Header Status Panel**: Displays global runtime state (e.g., "Idle", "Running Pipeline", "Evaluating Benchmark"), current iteration number, and the active SQLite snapshot database.
2.  **DAG Tree View (Left Pane)**: Visualizes the hierarchical structure of the self-organizing Directed Acyclic Graph. It shows:
    *   Node labels and depths.
    *   Query counts at each leaf node (or parent residuals).
    *   Node state indicators (whether vMF fitting or NiW regularization is complete).
3.  **Leaderboard Panel (Right Pane)**: Displays the local Bradley-Terry model leaderboard for the selected node. It renders:
    *   Ranked list of evaluated models.
    *   Fitted log-strength scores ($\beta$).
    *   Standard error intervals ($\pm SE$) indicating estimation uncertainty.
4.  **Live Logs Panel (Bottom Pane)**: Displays scrolling, colored system logs in real time. It is driven by [LogsPanel](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/tui/features/startup/LoadingPanel.kt) to monitor background fitting, routing, and matchmaking threads.

---

## 2. Interactive Navigation Controls & Hotkeys

Navigation is governed by keyboard events mapped to specific pipeline operations:

| Hotkey | Action | Operation |
| :--- | :--- | :--- |
| **`Tab`** | Switch Focus | Toggles selection focus between the DAG Tree View and the Leaderboard Panel. |
| **`Enter`** | Select Node | Focuses on a specific node, loading its query corpus and local leaderboard. |
| **`L`** | Expand / Collapse | Expands or collapses the children of the selected node in the Tree View. |
| **`R`** | Trigger Adjudication | Manually triggers the LLM-judge pairwise comparisons for the selected domain leaf. |
| **`S`** | Persist Snapshot | Freezes the current DAG state and saves it to `snapshots.db`. |
| **`Arrow Keys`** | Navigate Tree | Scroll up and down through the visible node list. |

---

## 3. Taxonomy Snapshot Visualization

To view the generated taxonomy in standard graph layouts, TaxoArena provides visualization utilities:

*   **Kotlin Exporter**: [TaxonomyVisualizer](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyVisualizer.kt) sweeps the in-memory DAG and exports its structure in Graphviz DOT format.
*   **Python Renderer**: The script [visualize_taxonomy.py](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/visualize_taxonomy.py) parses the `.dot` file. It color-codes nodes by depth, sizes nodes relative to their query count, and draws tree child edges as solid lines and cross-link parent edges as dashed lines.
*   **Command Line Execution**:
    ```powershell
    python visualize_taxonomy.py --input taxonomy_initial.dot --output taxonomy.png
    ```

This visualization pipeline allows researchers to inspect the self-organizing knowledge boundaries.

---

## 🔗 Related Code References
*   [LoadingPanel](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/tui/features/startup/LoadingPanel.kt): TUI view components.
*   [TaxonomyVisualizer](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyVisualizer.kt): Generates Graphviz DOT representation of GraphNodes.
*   [visualize_taxonomy.py](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/visualize_taxonomy.py): Python post-processing and rendering script.
