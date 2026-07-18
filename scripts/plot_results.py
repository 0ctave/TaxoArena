#!/usr/bin/env python3
import os
import sys
import csv
import argparse

# Try importing matplotlib, handle failure gracefully
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib is not installed. Plots cannot be generated, but text summary will be printed.")
    print("To install: pip install matplotlib")

def setup_academic_plot_style():
    """Sets up a beautiful, publication-grade academic plotting style using standard matplotlib."""
    if not HAS_MATPLOTLIB:
        return
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "pdf.fonttype": 42
    })

def read_csv_data(filepath):
    """Reads CSV file and returns a list of dictionaries (keys are header columns)."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def plot_global_leaderboards(input_dir, output_dir, conditions):
    """
    Plots a comparison of global Bradley-Terry scores from leaf leaderboards
    across different experimental conditions.
    """
    all_rows = []
    for cond in conditions:
        filepath = os.path.join(input_dir, "validation", f"{cond}_leaf_leaderboard.csv")
        rows = read_csv_data(filepath)
        all_rows.extend(rows)
        
    if not all_rows:
        print("No leaderboard data found to summarize/plot.")
        return
        
    # Group by ModelId and LeafId
    leaf_models = {}
    for r in all_rows:
        leaf_id = r.get("LeafId", "unknown")
        model_id = r.get("ModelId", "unknown")
        score = float(r.get("BtScore", 0.0))
        
        leaf_models.setdefault(leaf_id, {})[model_id] = score
        
    print("\n--- Leaf Bradley-Terry Scores Summary ---")
    for leaf_id, models in leaf_models.items():
        print(f"Leaf/Domain: {leaf_id}")
        for model_id, score in models.items():
            print(f"  * {model_id}: {score:+.4f}")

    if not HAS_MATPLOTLIB:
        return

    # Plot Leaf-level BT Scores by Domain
    leaves = list(leaf_models.keys())
    if not leaves:
        return
        
    all_model_ids = set()
    for m in leaf_models.values():
        all_model_ids.update(m.keys())
    model_list = sorted(list(all_model_ids))
    
    x = range(len(leaves))
    width = 0.8 / len(model_list) if model_list else 0.4
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Custom color palette (cool tech tones)
    colors = ["#4A90E2", "#50E3C2", "#F5A623", "#D0021B", "#9B51E0"]
    
    for idx, model_id in enumerate(model_list):
        scores = []
        for leaf in leaves:
            scores.append(leaf_models[leaf].get(model_id, 0.0))
            
        offset = (idx - len(model_list)/2.0 + 0.5) * width
        ax.bar(
            [pos + offset for pos in x],
            scores,
            width,
            label=model_id,
            color=colors[idx % len(colors)]
        )
        
    ax.set_title("Leaf-Level Bradley-Terry Ranks across Domains")
    ax.set_xlabel("Taxonomy Leaf Node (Domain ID)")
    ax.set_ylabel("Bradley-Terry Score")
    ax.set_xticks(x)
    ax.set_xticklabels([l[:15] + "..." if len(l) > 15 else l for l in leaves], rotation=45, ha="right")
    ax.legend(title="Model")
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "leaf_leaderboard_comparison.pdf")
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved leaf leaderboard plot to {plot_path}")

def plot_condition_agreement_comparison(input_dir, output_dir, conditions):
    """
    Plots a comparison of overall judge-accuracy agreement rate and question coverage
    across different experimental conditions.
    """
    metrics_rows = []
    for cond in conditions:
        filepath = os.path.join(input_dir, "validation", f"{cond}_metrics.csv")
        rows = read_csv_data(filepath)
        metrics_rows.extend(rows)
        
    if not metrics_rows:
        print("No metrics data found to summarize/plot.")
        return
        
    print("\n--- Experimental Conditions Summary ---")
    for r in metrics_rows:
        print(f"Condition: {r.get('Condition')}")
        print(f"  * Total Queries:  {r.get('TotalQueries')}")
        print(f"  * Coverage Rate:  {float(r.get('CoverageRate', 0.0)):.2%}")
        print(f"  * Agreement Rate: {float(r.get('OverallJudgeAccuracyAgreement', 0.0)):.2%}")

    if not HAS_MATPLOTLIB:
        return

    cond_names = [r.get("Condition") for r in metrics_rows]
    agreements = [float(r.get("OverallJudgeAccuracyAgreement", 0.0)) for r in metrics_rows]
    coverages = [float(r.get("CoverageRate", 0.0)) for r in metrics_rows]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 1. Judge-Accuracy Agreement Rate
    axes[0].bar(cond_names, agreements, color="#2A9D8F", width=0.5)
    axes[0].set_title("Judge-Accuracy Agreement Rate")
    axes[0].set_ylabel("Agreement Rate")
    axes[0].set_ylim(0, 1.05)
    
    # 2. Coverage Rate
    axes[1].bar(cond_names, coverages, color="#F4A261", width=0.5)
    axes[1].set_title("Question Coverage Rate")
    axes[1].set_ylabel("Coverage Rate")
    axes[1].set_ylim(0, 1.05)
    
    plt.suptitle("Experimental Conditions Comparison Matrix", y=0.98)
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "conditions_agreement_coverage.pdf")
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved agreement/coverage comparison plot to {plot_path}")

def main():
    parser = argparse.ArgumentParser(description="TaxoArena Publication-Grade Plotting Companion")
    parser.add_argument("--input-dir", type=str, default="experiment_results",
                        help="Input directory containing exported CSV files (default: experiment_results)")
    parser.add_argument("--output-dir", type=str, default="plots",
                        help="Output directory to save generated plots (default: plots)")
    parser.add_argument("--conditions", nargs="+", default=["MAIN", "CANONICAL", "GENERIC_JUDGE", "RANDOM_SCHEDULER"],
                        help="Experimental conditions to process (default: all 4)")
                        
    args = parser.parse_args()
    
    setup_academic_plot_style()
    
    print(f"Processing results from: {args.input_dir}")
    plot_global_leaderboards(args.input_dir, args.output_dir, args.conditions)
    plot_condition_agreement_comparison(args.input_dir, args.output_dir, args.conditions)

if __name__ == "__main__":
    main()
