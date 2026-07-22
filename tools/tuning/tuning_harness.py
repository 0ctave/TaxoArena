# tuning_harness.py
import sys
import os
import argparse
import json
import subprocess
import csv
import hashlib
import shutil

from orthogonal_arrays import map_levels_to_values, verify_orthogonality
from pareto import check_hard_gates, check_soft_gates, compute_pareto_front, compute_dominance_counts

def parse_toml(content):
    data = {}
    current_section = None
    for line in content.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            continue
            
        if "=" in line:
            parts = line.split("=", 1)
            key = parts[0].strip()
            val_str = parts[1].strip()
            
            # Parse value
            if val_str.lower() == "true":
                val = True
            elif val_str.lower() == "false":
                val = False
            elif val_str.startswith("[") and val_str.endswith("]"):
                items = val_str[1:-1].split(",")
                val = []
                for item in items:
                    item = item.strip()
                    if not item:
                        continue
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        val.append(item[1:-1])
                    elif "." in item:
                        val.append(float(item))
                    else:
                        try:
                            val.append(int(item))
                        except ValueError:
                            val.append(item)
            elif (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
                val = val_str[1:-1]
            elif "." in val_str:
                val = float(val_str)
            else:
                try:
                    val = int(val_str)
                except ValueError:
                    val = val_str
            
            if current_section:
                sec_parts = current_section.split(".")
                d = data
                for part in sec_parts:
                    d = d.setdefault(part, {})
                d[key] = val
            else:
                data[key] = val
    return data

def compute_config_sha256(factors):
    normalized = json.dumps(factors, sort_keys=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def modify_toml(base_toml_text, overrides):
    lines = base_toml_text.splitlines()
    keys_to_set = set(overrides.keys())
    new_lines = []
    for line in lines:
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            new_lines.append(line)
            continue
        if "=" in trimmed:
            parts = trimmed.split("=", 1)
            key = parts[0].strip()
            if key in keys_to_set:
                val = overrides[key]
                if isinstance(val, bool):
                    val_str = str(val).lower()
                elif isinstance(val, str):
                    val_str = f'"{val}"'
                else:
                    val_str = str(val)
                new_lines.append(f"{key} = {val_str}")
                keys_to_set.remove(key)
                continue
        new_lines.append(line)
        
    for key in sorted(list(keys_to_set)):
        val = overrides[key]
        if isinstance(val, bool):
            val_str = str(val).lower()
        elif isinstance(val, str):
            val_str = f'"{val}"'
        else:
            val_str = str(val)
        new_lines.append(f"{key} = {val_str}")
        
    return "\n".join(new_lines) + "\n"

def load_manifest(manifest_path):
    if not os.path.exists(manifest_path):
        return []
    runs = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    return runs

def save_manifest(manifest_path, runs):
    with open(manifest_path, "w", encoding="utf-8") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")

def cmd_generate(args):
    if not os.path.exists(args.spec):
        print(f"Error: Spec file not found: {args.spec}")
        sys.exit(1)
        
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = parse_toml(f.read())
        
    runs_dir = spec.get("output", {}).get("runs_dir", "tuning/runs")
    manifest_path = os.path.join(runs_dir, "manifest.jsonl")
    os.makedirs(runs_dir, exist_ok=True)
    
    existing_runs = load_manifest(manifest_path)
    runs_by_id = {r["run_id"]: r for r in existing_runs}
    
    generated_runs = []
    
    if args.stage == "screen":
        factors_spec = spec.get("factors", {})
        l9_configs = map_levels_to_values(factors_spec)
        seed = spec.get("screening", {}).get("seed", 42)
        
        for i, factors in enumerate(l9_configs):
            run_id = f"L9_{i+1:03d}_seed{seed}"
            config_sha = compute_config_sha256(factors)
            
            run_row = {
                "run_id": run_id,
                "stage": "screen",
                "seed": seed,
                "config_path": os.path.join(runs_dir, run_id, "config.toml").replace("\\", "/"),
                "output_dir": os.path.join(runs_dir, run_id, "output").replace("\\", "/"),
                "factors": factors,
                "config_sha256": config_sha,
                "status": "pending"
            }
            generated_runs.append(run_row)
            
    elif args.stage == "validate":
        finalists_seeds = spec.get("finalists", {}).get("seeds", [137, 2048])
        
        finalist_shas = []
        if args.finalists:
            finalist_shas = [sha.strip() for sha in args.finalists.split(",")]
        else:
            finalists_csv_path = "tuning/finalists.csv"
            if not os.path.exists(finalists_csv_path):
                print(f"Error: No finalists specified, and {finalists_csv_path} does not exist. Run 'select' subcommand first.")
                sys.exit(1)
            with open(finalists_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                seen = set()
                for row in reader:
                    sha = row["config_sha256"]
                    if sha not in seen:
                        seen.add(sha)
                        finalist_shas.append(sha)
                        if len(finalist_shas) >= 3:
                            break
                            
        if not finalist_shas:
            print("Error: No finalists found to validate.")
            sys.exit(1)
            
        print(f"Validating finalists with SHAs: {finalist_shas}")
        
        sha_to_factors = {}
        for r in existing_runs:
            if r["config_sha256"] in finalist_shas:
                sha_to_factors[r["config_sha256"]] = r["factors"]
                
        for sha in finalist_shas:
            if sha not in sha_to_factors:
                ledger_path = spec.get("output", {}).get("combined_ledger", "tuning/combined_ledger.csv")
                if os.path.exists(ledger_path):
                    with open(ledger_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row["config_sha256"] == sha:
                                factors = {}
                                for f_key in spec.get("factors", {}).keys():
                                    if f_key in row:
                                        val_str = str(row[f_key])
                                        factors[f_key] = float(val_str) if "." in val_str else int(val_str)
                                sha_to_factors[sha] = factors
                                break
                                
        for sha in finalist_shas:
            if sha not in sha_to_factors:
                print(f"Error: Could not find factor values for finalist config {sha}")
                sys.exit(1)
                
        for sha in finalist_shas:
            factors = sha_to_factors[sha]
            short_sha = sha[:8]
            for seed in finalists_seeds:
                run_id = f"val_{short_sha}_seed{seed}"
                run_row = {
                    "run_id": run_id,
                    "stage": "validate",
                    "seed": seed,
                    "config_path": os.path.join(runs_dir, run_id, "config.toml").replace("\\", "/"),
                    "output_dir": os.path.join(runs_dir, run_id, "output").replace("\\", "/"),
                    "factors": factors,
                    "config_sha256": sha,
                    "status": "pending"
                }
                generated_runs.append(run_row)
                
    base_config_path = spec.get("base", {}).get("config", "experiment_configs/dagmax_feature_on.toml")
    if not os.path.exists(base_config_path):
        print(f"Error: Base config file not found: {base_config_path}")
        sys.exit(1)
        
    with open(base_config_path, "r", encoding="utf-8") as f:
        base_toml_text = f.read()
        
    for r in generated_runs:
        run_id = r["run_id"]
        config_path = r["config_path"]
        output_dir = r["output_dir"]
        factors = r["factors"]
        seed = r["seed"]
        
        overrides = {
            "outputDir": output_dir.replace("\\", "/"),
            "seed": seed,
            "runBaselines": r.get("stage") == "validate",
            "runTrickle": True,
            "runBenchmark": False,
            "runPipeline": True,
            "numIterations": 35,
            "enableFinalMetrics": False
        }
        for k, v in factors.items():
            if k == "splitThreshold":
                overrides["separationEpsilon"] = v
            else:
                overrides[k] = v
                
        toml_text = modify_toml(base_toml_text, overrides)
        
        if args.dry_run:
            print(f"\n[DRY RUN] Would write config for {run_id} to {config_path}:")
            print(f"Overrides: {overrides}")
        else:
            run_config_dir = os.path.dirname(config_path)
            os.makedirs(run_config_dir, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(toml_text)
            
            if run_id in runs_by_id:
                if runs_by_id[run_id]["config_sha256"] == r["config_sha256"] and not getattr(args, "clean", False):
                    r["status"] = runs_by_id[run_id]["status"]
                runs_by_id[run_id] = r
            else:
                runs_by_id[run_id] = r
                
            if getattr(args, "clean", False) and os.path.exists(output_dir):
                import shutil
                print(f"Wiping output directory for {run_id}: {output_dir}")
                try:
                    shutil.rmtree(output_dir)
                except Exception as e:
                    print(f"Warning: Failed to clean {output_dir}: {e}")
                
    if not args.dry_run:
        new_manifest_list = sorted(list(runs_by_id.values()), key=lambda x: x["run_id"])
        save_manifest(manifest_path, new_manifest_list)
        print(f"Manifest written with {len(new_manifest_list)} runs at {manifest_path}")

def cmd_run(args):
    if not os.path.exists(args.spec):
        print(f"Error: Spec file not found: {args.spec}")
        sys.exit(1)
        
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = parse_toml(f.read())
        
    runs_dir = spec.get("output", {}).get("runs_dir", "tuning/runs")
    manifest_path = os.path.join(runs_dir, "manifest.jsonl")
    
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found: {manifest_path}. Run 'generate' subcommand first.")
        sys.exit(1)
        
    runs = load_manifest(manifest_path)
    
    gradle_cmd = spec.get("base", {}).get("gradle_cmd", "gradlew.bat bootRun")
    gradle_args = gradle_cmd.split()
    
    only_runs = [r.strip() for r in args.only.split(",")] if args.only else []
    
    executed_count = 0
    limit = args.limit if args.limit else len(runs)
    
    for r in runs:
        run_id = r["run_id"]
        if args.stage and r.get("stage") != args.stage:
            continue
        if only_runs and run_id not in only_runs:
            continue
            
        config_path = r["config_path"]
        output_dir = r["output_dir"]
        seed = r["seed"]
        
        ledger_file = os.path.join(output_dir, "tuning_ledger.csv")
        validity_file = os.path.join(output_dir, f"seed_{seed}", "validation", "MAIN_graph_validity.csv")
        bridge_file = os.path.join(output_dir, f"seed_{seed}", "validation", "MAIN_bridge_quality.csv")
        
        run_exists = os.path.exists(ledger_file) and os.path.exists(validity_file) and os.path.exists(bridge_file)
        
        if r["status"] == "success" and run_exists:
            print(f"Skipping completed run: {run_id}")
            continue
            
        if executed_count >= limit:
            print(f"Reached execution limit of {limit} runs. Stopping.")
            break
            
        print(f"\n=== Executing run: {run_id} ===")
        print(f"Config: {config_path}")
        
        r["status"] = "running"
        save_manifest(manifest_path, runs)
        
        run_dir = os.path.dirname(config_path)
        log_file_path = os.path.join(run_dir, "run.log")
        
        config_rel_path = os.path.relpath(config_path).replace("\\", "/")
        cmd = list(gradle_args)
        cmd.append(f'--args=--config {config_rel_path}')
        
        print(f"Running command: {' '.join(cmd)}")
        
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            try:
                result = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT, text=True)
                success = (result.returncode == 0) and os.path.exists(ledger_file) and os.path.exists(validity_file)
                if success:
                    r["status"] = "success"
                    print(f"Run {run_id} completed successfully.")
                else:
                    r["status"] = "failed"
                    print(f"Run {run_id} failed. See log: {log_file_path}")
            except Exception as e:
                r["status"] = "failed"
                print(f"Run {run_id} encountered execution error: {e}")
                log_file.write(f"\nExecution error: {e}\n")
                
        save_manifest(manifest_path, runs)
        executed_count += 1

def cmd_collect(args):
    if not os.path.exists(args.spec):
        print(f"Error: Spec file not found: {args.spec}")
        sys.exit(1)
        
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = parse_toml(f.read())
        
    runs_dir = spec.get("output", {}).get("runs_dir", "tuning/runs")
    manifest_path = os.path.join(runs_dir, "manifest.jsonl")
    
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file not found: {manifest_path}")
        sys.exit(1)
        
    runs = load_manifest(manifest_path)
    
    combined_ledger_path = spec.get("output", {}).get("combined_ledger", "tuning/combined_ledger.csv")
    combined_bridges_path = "tuning/combined_bridges.csv"
    
    ledger_rows = []
    bridge_rows = []
    
    factor_keys = list(spec.get("factors", {}).keys())
    extra_cols = ["run_id", "config_path", "output_dir", "config_sha256", "stage", "seed"] + factor_keys
                  
    for r in runs:
        run_id = r["run_id"]
        output_dir = r["output_dir"]
        seed = r["seed"]
        
        ledger_path = os.path.join(output_dir, "tuning_ledger.csv")
        if not os.path.exists(ledger_path):
            continue
            
        with open(ledger_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Condition") != "MAIN":
                    continue
                row["run_id"] = run_id
                row["config_path"] = r["config_path"]
                row["output_dir"] = output_dir
                row["config_sha256"] = r["config_sha256"]
                row["stage"] = r["stage"]
                row["seed"] = seed
                for f_k in factor_keys:
                    row[f_k] = r.get("factors", {}).get(f_k, "")
                
                ledger_rows.append(row)
                
        bridge_path = os.path.join(output_dir, f"seed_{seed}", "validation", "MAIN_bridge_quality.csv")
        if os.path.exists(bridge_path):
            with open(bridge_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                for brow in reader:
                    if brow and brow[0].startswith("bridge_"):
                        bridge_rows.append({
                            "run_id": run_id,
                            "BridgeId": brow[0],
                            "BridgeType": brow[1],
                            "Depth": brow[2],
                            "Coverage": brow[3],
                            "CrossDomainLabelMix": brow[4] if len(brow) > 4 else "",
                            "TopRepresentativeQueries": brow[5] if len(brow) > 5 else ""
                        })
                        
    if ledger_rows:
        os.makedirs(os.path.dirname(combined_ledger_path), exist_ok=True)
        fieldnames = extra_cols + [k for k in ledger_rows[0].keys() if k not in extra_cols]
        with open(combined_ledger_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in ledger_rows:
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)
        print(f"Combined ledger written with {len(ledger_rows)} rows to {combined_ledger_path}")
    else:
        print("Warning: No ledger rows collected!")
        
    if bridge_rows:
        with open(combined_bridges_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["run_id", "BridgeId", "BridgeType", "Depth", "Coverage", "CrossDomainLabelMix", "TopRepresentativeQueries"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in bridge_rows:
                writer.writerow(row)
        print(f"Combined bridges written with {len(bridge_rows)} rows to {combined_bridges_path}")

def cmd_select(args):
    if not os.path.exists(args.spec):
        print(f"Error: Spec file not found: {args.spec}")
        sys.exit(1)
        
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = parse_toml(f.read())
        
    combined_ledger_path = spec.get("output", {}).get("combined_ledger", "tuning/combined_ledger.csv")
    combined_bridges_path = "tuning/combined_bridges.csv"
    
    if not os.path.exists(combined_ledger_path):
        print(f"Error: Combined ledger not found at {combined_ledger_path}. Run 'collect' subcommand first.")
        sys.exit(1)
        
    run_bridges = {}
    if os.path.exists(combined_bridges_path):
        with open(combined_bridges_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                run_id = row["run_id"]
                if row["BridgeType"] == "SourceB":
                    depth = 0
                    try:
                        depth = int(row["Depth"])
                    except ValueError:
                        pass
                    run_bridges.setdefault(run_id, []).append(depth)
                    
    candidates = []
    with open(combined_ledger_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
            
    results = []
    for c in candidates:
        run_id = c["run_id"]
        bridge_depths = run_bridges.get(run_id, [])
        
        hard_ok, hard_reasons = check_hard_gates(c, bridge_depths, spec)
        soft_ok, soft_reasons = check_soft_gates(c, spec)
        
        c["hard_gates_passed"] = hard_ok
        c["hard_gate_failures"] = "; ".join(hard_reasons)
        c["soft_gates_passed"] = soft_ok
        c["soft_gate_failures"] = "; ".join(soft_reasons)
        
        results.append(c)
        
    dom_counts = compute_dominance_counts(results)
    for c in results:
        c["dominance_count"] = dom_counts.get(c["run_id"], 0)
        
    ranked = sorted(results, key=lambda x: (
        1 if x["hard_gates_passed"] else 0,
        x["dominance_count"],
        float(x.get("Top1Accuracy", 0.0))
    ), reverse=True)
    
    finalists_csv_path = "tuning/finalists.csv"
    os.makedirs(os.path.dirname(finalists_csv_path), exist_ok=True)
    if ranked:
        factor_keys = list(spec.get("factors", {}).keys())
        base_meta_keys = ["run_id", "config_sha256", "stage", "seed", "hard_gates_passed", "soft_gates_passed", "dominance_count", "hard_gate_failures", "soft_gate_failures"]
        fieldnames = base_meta_keys + factor_keys + [k for k in ranked[0].keys() if k not in base_meta_keys and k not in factor_keys]
        with open(finalists_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in ranked:
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)
        print(f"Finalists CSV written to {finalists_csv_path}")
        
        finalists_md_path = "tuning/finalists.md"
        with open(finalists_md_path, "w", encoding="utf-8") as f:
            f.write("# TaxoArena — Tuning Finalists & Architectural Report\n\n")
            f.write("## 1. Executive Summary & Pareto Ranking\n\n")
            f.write("| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
            for idx, r in enumerate(ranked[:10]):
                hard_status = "PASSED" if r["hard_gates_passed"] else "FAILED"
                soft_status = "PASSED" if r["soft_gates_passed"] else "FAILED"
                
                top1_val = float(r.get('Top1Accuracy', 0.0))
                if top1_val <= 1.0:
                    top1_val *= 100.0
                anymatch_val = float(r.get('AnyMatchAccuracy', 0.0))
                if anymatch_val <= 1.0:
                    anymatch_val *= 100.0
                
                borderline = float(r.get('BorderlineRate', 0.0))
                migration = float(r.get('CrossAnchorMigrationRate', 0.0))
                delta_rho = float(r.get('DeltaRhoTotal', 0.0))
                small_leaf = float(r.get('SmallLeafFraction', 0.0))
                sb_depth2 = int(float(r.get('SourceBDepth2Count', 0)))

                bridge_cnt = float(r.get('BridgeCount', 0))
                leaf_cnt = float(r.get('LeafCount', 0))
                total_nodes = float(r.get('TotalNodes', bridge_cnt + leaf_cnt + 1))
                b_ratio = float(r.get('BridgeRatio', bridge_cnt / total_nodes if total_nodes > 0 else 0.0))
                b_ratio_str = f"{b_ratio * 100.0:.2f}%" if b_ratio <= 1.0 else f"{b_ratio:.2f}%"
                
                f.write(f"| {idx+1} | {r['run_id']} | {r['stage']} | {r['seed']} | {hard_status} | {soft_status} | {r['dominance_count']} | {top1_val:.2f}% | {anymatch_val:.2f}% | {float(r.get('RoutingECE', 0.0)):.4f} | {borderline:.4f} | {b_ratio_str} | {migration:.4f} | {delta_rho:.4f} | {small_leaf:.4f} | {sb_depth2} |\n")
                
            f.write("\n## 2. Gate Failure Explanations (Top 10 Runs)\n\n")
            for idx, r in enumerate(ranked[:10]):
                if not r["hard_gates_passed"] or not r["soft_gates_passed"]:
                    f.write(f"### {idx+1}. Run: {r['run_id']}\n")
                    if not r["hard_gates_passed"]:
                        f.write(f"- **Hard Gate Failures**: {r['hard_gate_failures']}\n")
                    if not r["soft_gates_passed"]:
                        f.write(f"- **Soft Gate Failures**: {r['soft_gate_failures']}\n")
                    f.write("\n")

            f.write("\n## 3. Categorized Metric Summaries (Top 5 Finalists)\n\n")
            for idx, r in enumerate(ranked[:5]):
                f.write(f"### Rank {idx+1}: {r['run_id']}\n\n")
                factor_kv = [f"`{k}`={r.get(k, '')}" for k in factor_keys]
                f.write("**Config Factors**: {}\n\n".format(", ".join(factor_kv)))
                
                # Category 1: Structural Integrity (Hard Gates)
                f.write("#### A. Structural Integrity (Hard Gates)\n")
                f.write("- **Acyclic**: {}\n".format(r.get("Acyclic", "")))
                f.write("- **RootReachable**: {}\n".format(r.get("RootReachable", "")))
                f.write("- **OrphanCount**: {}\n".format(r.get("OrphanCount", "")))
                f.write("- **DuplicateBridgeCount**: {} *(excl. empty child sets)*\n".format(r.get("DuplicateBridgeCount", "")))
                f.write("- **MaxAssignmentCapRate**: {}\n".format(r.get("MaxAssignmentCapRate", "")))
                f.write("- **SmallLeafFraction**: {}\n".format(r.get("SmallLeafFraction", "")))
                f.write("- **SelectedNodeStarvedLeafFraction**: {}\n".format(r.get("SelectedNodeStarvedLeafFraction", "")))
                f.write("- **SourceBPerAnchorMean**: {}\n".format(r.get("SourceBPerAnchorMean", "")))
                f.write("- **Topology Counts**: TotalNodes={}, LeafCount={}, BridgeCount={}, BridgeRatio={}, ResidualCount={}\n\n".format(
                    r.get("TotalNodes", ""), r.get("LeafCount", ""), r.get("BridgeCount", ""), r.get("BridgeRatio", ""), r.get("ResidualCount", "")
                ))

                # Category 2: Taxonomy Quality (Pareto Objectives)
                f.write("#### B. Taxonomy Quality (Pareto Objectives)\n")
                f.write("- **WeightedLeafPurity**: {}\n".format(r.get("WeightedLeafPurity", "")))
                f.write("- **DendrogramPurity**: {}\n".format(r.get("DendrogramPurity", "")))
                f.write("- **SphericalSilhouette**: {}\n".format(r.get("SphericalSilhouette", "")))
                f.write("- **DeltaRhoTotal**: {}\n".format(r.get("DeltaRhoTotal", "")))
                f.write("- **CanonicalAdaptedJaccard**: {}\n".format(r.get("CanonicalAdaptedJaccard", "")))
                f.write("- **TotalDasguptaCost**: {}\n".format(r.get("TotalDasguptaCost", "")))
                f.write("- **RoutingECE**: {}\n".format(r.get("RoutingECE", "")))
                f.write("- **BrierScore**: {}\n\n".format(r.get("BrierScore", "")))

                # Category 3: Routing & Arena Performance (Soft Gates)
                f.write("#### C. Routing & Arena Performance (Soft Gates)\n")
                f.write("- **Top1Accuracy**: {}%\n".format(r.get("Top1Accuracy", "")))
                f.write("- **AnyMatchAccuracy**: {}%\n".format(r.get("AnyMatchAccuracy", "")))
                f.write("- **MacroF1**: {}\n".format(r.get("MacroF1", "")))
                f.write("- **AvgMatchCount**: {}\n".format(r.get("AvgMatchCount", "")))
                f.write("- **BorderlineRate**: {}\n".format(r.get("BorderlineRate", "")))
                f.write("- **CrossAnchorMigrationRate**: {}\n\n".format(r.get("CrossAnchorMigrationRate", "")))

                # Category 4: Bridge & Cross-Domain Diagnostics
                f.write("#### D. Bridge & Cross-Domain Diagnostics\n")
                f.write("- **SourceA_Count**: {}\n".format(r.get("SourceA_Count", "")))
                f.write("- **SourceB_Count**: {}\n".format(r.get("SourceB_Count", "")))
                f.write("- **SourceBDepth2Count**: {}\n".format(r.get("SourceBDepth2Count", "")))
                f.write("- **SourceBPerAnchorMean**: {}\n".format(r.get("SourceBPerAnchorMean", "")))
                f.write("- **RhoCanonicalHard**: {}, **RhoAdaptedHard**: {}, **RhoAdaptedSoft**: {}\n".format(
                    r.get("RhoCanonicalHard", ""), r.get("RhoAdaptedHard", ""), r.get("RhoAdaptedSoft", "")
                ))
                f.write("- **DeltaRhoGeom**: {}, **DeltaRhoSoft**: {}\n\n".format(
                    r.get("DeltaRhoGeom", ""), r.get("DeltaRhoSoft", "")
                ))

                # Category 5: Distributional / Balance Diagnostics
                f.write("#### E. Distributional / Balance Diagnostics\n")
                f.write("- **NormalisedSackinIndex**: {}\n".format(r.get("NormalisedSackinIndex", "")))
                f.write("- **SoftDegreeMean**: {}\n".format(r.get("SoftDegreeMean", "")))
                f.write("- **EntropyGuardRate**: {}\n".format(r.get("EntropyGuardRate", "")))
                f.write("- **SoftEffSampleSize**: {}\n".format(r.get("SoftEffSampleSize", "")))
                f.write("- **SelectedNodeP10QueryCount**: {}\n".format(r.get("SelectedNodeP10QueryCount", "")))
                f.write("- **SelectedNodeLeafBalanceEntropy**: {}\n\n".format(r.get("SelectedNodeLeafBalanceEntropy", "")))

                # Category 6: Config Traceability
                f.write("#### F. Config Traceability\n")
                f.write("- **SHA256**: `{}`\n".format(r.get("config_sha256", "")))
                f.write("- **Hard Gates Passed**: {}, **Soft Gates Passed**: {}, **Dominance Count**: {}\n\n".format(
                    r.get("hard_gates_passed", ""), r.get("soft_gates_passed", ""), r.get("dominance_count", "")
                ))
                f.write("---\n\n")

        print(f"Finalists Markdown Summary written to {finalists_md_path}")
    else:
        print("Warning: No results found to rank!")

def cmd_pipeline(args):
    # Ensure all required attributes are present on args
    if not hasattr(args, "dry_run"):
        args.dry_run = False
    if not hasattr(args, "only"):
        args.only = None
    if not hasattr(args, "limit"):
        args.limit = None
        
    print(f"=== [Pipeline] Starting Tuning Stage: {args.stage} ===")
    
    print("\n=== [Pipeline Step 1/4] Generating configurations ===")
    cmd_generate(args)
    
    print("\n=== [Pipeline Step 2/4] Running configurations ===")
    cmd_run(args)
    
    print("\n=== [Pipeline Step 3/4] Collecting results ===")
    cmd_collect(args)
    
    print("\n=== [Pipeline Step 4/4] Selecting optimal configurations ===")
    cmd_select(args)
    
    print("\n=== [Pipeline] Stage Completed Successfully! ===")

def main():
    parser = argparse.ArgumentParser(description="TaxoArena Phase 3 Tuning Harness")
    subparsers = parser.add_subparsers(dest="command")
    
    gen_parser = subparsers.add_parser("generate", help="Generate TOML configs and runs manifest")
    gen_parser.add_argument("--spec", default="tools/tuning/sweep_spec.example.toml", help="Path to sweep spec TOML")
    gen_parser.add_argument("--stage", default="screen", choices=["screen", "validate"], help="Stage of tuning: screen or validate")
    gen_parser.add_argument("--finalists", help="Comma-separated finalist config SHAs to validate (omit to use top from finalists.csv)")
    gen_parser.add_argument("--dry-run", action="store_true", help="Print configuration overrides without writing files")
    gen_parser.add_argument("--clean", action="store_true", help="Force reset run status to pending and delete previous outputs")
    
    run_parser = subparsers.add_parser("run", help="Run pending configurations in manifest")
    run_parser.add_argument("--spec", default="tools/tuning/sweep_spec.example.toml", help="Path to sweep spec TOML")
    run_parser.add_argument("--stage", choices=["screen", "validate"], help="Filter runs by stage (screen or validate)")
    run_parser.add_argument("--only", help="Comma-separated run IDs to run exclusively")
    run_parser.add_argument("--limit", type=int, help="Maximum number of runs to execute")
    
    coll_parser = subparsers.add_parser("collect", help="Collect individual ledger and bridge files into a unified ledger")
    coll_parser.add_argument("--spec", default="tools/tuning/sweep_spec.example.toml", help="Path to sweep spec TOML")
    
    sel_parser = subparsers.add_parser("select", help="Perform Pareto front selection and hard-gate filtering")
    sel_parser.add_argument("--spec", default="tools/tuning/sweep_spec.example.toml", help="Path to sweep spec TOML")
    
    pipe_parser = subparsers.add_parser("pipeline", help="Run a full tuning pipeline (generate -> run -> collect -> select) in one command")
    pipe_parser.add_argument("--spec", default="tools/tuning/sweep_spec.example.toml", help="Path to sweep spec TOML")
    pipe_parser.add_argument("--stage", default="screen", choices=["screen", "validate"], help="Stage of tuning: screen or validate")
    pipe_parser.add_argument("--clean", action="store_true", help="Clean previous run data before starting")
    pipe_parser.add_argument("--finalists", help="Comma-separated finalist config SHAs to validate (omit to use top from finalists.csv)")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "collect":
        cmd_collect(args)
    elif args.command == "select":
        cmd_select(args)
    elif args.command == "pipeline":
        cmd_pipeline(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
