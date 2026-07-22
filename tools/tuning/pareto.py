# pareto.py
import csv
import os

def check_hard_gates(row, bridge_depths, gates_spec):
    # row is a dict of strings/floats representing a combined ledger row
    # bridge_depths is a list of integers representing bridge depths for this run_id
    
    reasons = []
    
    # 1. Acyclic
    if str(row.get("Acyclic", "")).lower() != "true":
        reasons.append("Acyclic is not true")
        
    # 2. DuplicateBridgeCount
    dup_bridges = int(row.get("DuplicateBridgeCount", 0))
    if dup_bridges != 0:
        reasons.append(f"DuplicateBridgeCount = {dup_bridges} > 0")
        
    # 3. OrphanCount
    orphans = int(row.get("OrphanCount", 0))
    if orphans != 0:
        reasons.append(f"OrphanCount = {orphans} > 0")
        
    # 4. MaxAssignmentCapRate
    cap_rate = float(row.get("MaxAssignmentCapRate", 0.0))
    le_val = gates_spec.get("gates", {}).get("hard", {}).get("MaxAssignmentCapRate_le", 0.20)
    if cap_rate > le_val:
        reasons.append(f"MaxAssignmentCapRate = {cap_rate:.4f} > {le_val}")
        
    # 5. has_depth2_sourceB
    if gates_spec.get("gates", {}).get("hard", {}).get("has_depth2_sourceB", False):
        # We need at least 1 Source-B bridge with depth >= 2
        # bridge_depths contains the depths of Source-B bridges
        has_depth_2 = any(d >= 2 for d in bridge_depths)
        if not has_depth_2:
            reasons.append("No Source-B bridge with depth >= 2")
            
    # 6. SmallLeafFraction
    small_leaf_frac = float(row.get("SmallLeafFraction", 0.0))
    le_val = gates_spec.get("gates", {}).get("hard", {}).get("SmallLeafFraction_le", 0.50)
    if small_leaf_frac > le_val:
        reasons.append(f"SmallLeafFraction = {small_leaf_frac:.4f} > {le_val}")
        
    # 7. SelectedNodeStarvedLeafFraction
    starved_frac = float(row.get("SelectedNodeStarvedLeafFraction", 0.0))
    le_val = gates_spec.get("gates", {}).get("hard", {}).get("SelectedNodeStarvedLeafFraction_le", 0.20)
    if starved_frac > le_val:
        reasons.append(f"SelectedNodeStarvedLeafFraction = {starved_frac:.4f} > {le_val}")
        
    # 8. SourceBPerAnchorMean
    sb_mean = float(row.get("SourceBPerAnchorMean", 0.0))
    le_val = gates_spec.get("gates", {}).get("hard", {}).get("SourceBPerAnchorMean_le", 3.0)
    if sb_mean > le_val:
        reasons.append(f"SourceBPerAnchorMean = {sb_mean:.4f} > {le_val}")
        
    return len(reasons) == 0, reasons

def check_soft_gates(row, gates_spec):
    reasons = []
    
    # 1. AvgMatchCount band
    avg_match = float(row.get("AvgMatchCount", 0.0))
    band = gates_spec.get("gates", {}).get("soft", {}).get("AvgMatchCount_band", [1.0, 4.0])
    if not (band[0] <= avg_match <= band[1]):
        reasons.append(f"AvgMatchCount = {avg_match:.4f} outside band {band}")
        
    # 2. Top1Accuracy_ge
    top1 = float(row.get("Top1Accuracy", 0.0))
    if top1 <= 1.0:
        top1 = top1 * 100.0
    ge_val = gates_spec.get("gates", {}).get("soft", {}).get("Top1Accuracy_ge", 0.74)
    threshold = ge_val if ge_val > 1.0 else ge_val * 100.0
    if top1 < threshold:
        reasons.append(f"Top1Accuracy = {top1:.2f}% < {threshold}%")
        
    # 3. RoutingECE_le
    ece = float(row.get("RoutingECE", 0.0))
    le_val = gates_spec.get("gates", {}).get("soft", {}).get("RoutingECE_le", 0.15)
    if ece > le_val:
        reasons.append(f"RoutingECE = {ece:.4f} > {le_val}")
        
    # 4. BorderlineRate band
    soft_gates = gates_spec.get("gates", {}).get("soft", {})
    if "BorderlineRate_band" in soft_gates:
        borderline = float(row.get("BorderlineRate", 0.0))
        band = soft_gates["BorderlineRate_band"]
        if not (band[0] <= borderline <= band[1]):
            reasons.append(f"BorderlineRate = {borderline:.4f} outside band {band}")
        
    # 5. CrossAnchorMigrationRate band
    migration = float(row.get("CrossAnchorMigrationRate", 0.0))
    band = gates_spec.get("gates", {}).get("soft", {}).get("CrossAnchorMigrationRate_band", [0.10, 0.30])
    if not (band[0] <= migration <= band[1]):
        reasons.append(f"CrossAnchorMigrationRate = {migration:.4f} outside band {band}")
        
    # 6. CanonicalAdaptedJaccard band
    jaccard = float(row.get("CanonicalAdaptedJaccard", 0.0))
    band = gates_spec.get("gates", {}).get("soft", {}).get("CanonicalAdaptedJaccard_band", [0.0, 1.0])
    if not (band[0] <= jaccard <= band[1]):
        reasons.append(f"CanonicalAdaptedJaccard = {jaccard:.4f} outside band {band}")
        
    return len(reasons) == 0, reasons

def dominates(candidate1, candidate2):
    # Candidate 1 dominates Candidate 2 if it's better or equal in all objectives
    # and strictly better in at least one.
    # Objectives:
    # Maximize: WeightedLeafPurity, DendrogramPurity, SphericalSilhouette, DeltaRhoTotal, CanonicalAdaptedJaccard
    # Minimize: TotalDasguptaCost, RoutingECE, BrierScore, NoMatchRate, SmallLeafFraction, KappaShrinkageMean, SelectedNodeStarvedLeafFraction
    
    obj_max = ["WeightedLeafPurity", "DendrogramPurity", "SphericalSilhouette", "DeltaRhoTotal", "CanonicalAdaptedJaccard"]
    obj_min = ["TotalDasguptaCost", "RoutingECE", "BrierScore", "NoMatchRate", "SmallLeafFraction", "KappaShrinkageMean", "SelectedNodeStarvedLeafFraction"]
    
    better_or_equal = True
    strictly_better = False
    
    for metric in obj_max:
        v1 = float(candidate1.get(metric, 0.0))
        v2 = float(candidate2.get(metric, 0.0))
        if v1 < v2:
            better_or_equal = False
            break
        if v1 > v2:
            strictly_better = True
            
    if not better_or_equal:
        return False
        
    for metric in obj_min:
        v1 = float(candidate1.get(metric, 0.0))
        v2 = float(candidate2.get(metric, 0.0))
        if v1 > v2:
            better_or_equal = False
            break
        if v1 < v2:
            strictly_better = True
            
    return better_or_equal and strictly_better

def compute_pareto_front(candidates):
    # candidates is a list of row dicts
    pareto_set = []
    for c in candidates:
        is_dominated = False
        for other in candidates:
            if c["run_id"] == other["run_id"]:
                continue
            if dominates(other, c):
                is_dominated = True
                break
        if not is_dominated:
            pareto_set.append(c)
    return pareto_set

def compute_dominance_counts(candidates):
    # For each candidate, count how many other candidates it dominates.
    counts = {}
    for c in candidates:
        dom_count = 0
        for other in candidates:
            if c["run_id"] == other["run_id"]:
                continue
            if dominates(c, other):
                dom_count += 1
        counts[c["run_id"]] = dom_count
    return counts
