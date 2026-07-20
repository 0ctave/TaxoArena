import os
import subprocess
import csv

# Base TOML contents for the sweep
BASE_TOML = """# sweep_config_{id}.toml
datasetType   = "MMLU_PRO"
models        = ["gpt-4o-2024-08-06", "Meta-Llama-3_1-8B-Instruct"]
category      = ""
queryLimit    = 0
outputDir     = "experiment_results/dagmax_feature_on"
testRatio     = 0.3
seed          = 42

runPipeline    = true
runBenchmark   = false
runTrickle     = true
judgeInduction = false
enableLabeling = false

maxDepth          = 8
minClusterSize    = 25
separationEpsilon = 0.04
cosineTau         = 2.0
emaAlpha          = 0.7

maxLeafAssignments      = 5
refitMuPerIteration     = true

enableStableQuestionIds = true
enableResidualRouting   = true
enableResidualSplitGate = true
enableBridging          = true

hdlssThreshold          = 8.0
effectiveSupportFloor   = 2.0
numIterations           = 35

runBaselines            = false

# Sweep variables:
assignmentCosineGap     = {gap}
tauFunnelFloor          = {floor}
fusionSimilarityThreshold = {threshold}
"""

# L9 Orthogonal Array Design
sweep_configs = [
    {"id": 1, "gap": 0.02, "floor": 0.75, "threshold": 0.90},
    {"id": 2, "gap": 0.02, "floor": 0.80, "threshold": 0.92},
    {"id": 3, "gap": 0.02, "floor": 0.90, "threshold": 0.94},
    {"id": 4, "gap": 0.03, "floor": 0.75, "threshold": 0.92},
    {"id": 5, "gap": 0.03, "floor": 0.80, "threshold": 0.94},
    {"id": 6, "gap": 0.03, "floor": 0.90, "threshold": 0.90},
    {"id": 7, "gap": 0.05, "floor": 0.75, "threshold": 0.94},
    {"id": 8, "gap": 0.05, "floor": 0.80, "threshold": 0.90},
    {"id": 9, "gap": 0.05, "floor": 0.90, "threshold": 0.92},
]

def run_cmd(args):
    print(f"Running: {' '.join(args)}")
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing command: {res.stderr}")
        return False
    return True

def main():
    ledger_path = os.path.join("experiment_results", "dagmax_feature_on", "tuning_ledger.csv")
    
    # Backup existing ledger if any
    if os.path.exists(ledger_path):
        backup_path = ledger_path + ".bak"
        print(f"Backing up existing ledger to {backup_path}")
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(ledger_path, backup_path)
        
    for cfg in sweep_configs:
        toml_content = BASE_TOML.format(
            id=cfg["id"],
            gap=cfg["gap"],
            floor=cfg["floor"],
            threshold=cfg["threshold"]
        )
        
        toml_path = os.path.join("experiment_configs", f"sweep_config_{cfg['id']}.toml")
        with open(toml_path, "w") as f:
            f.write(toml_content)
            
        print(f"\n=== Running Sweep Config {cfg['id']} / {len(sweep_configs)} ===")
        print(f"Parameters: Gap={cfg['gap']}, Floor={cfg['floor']}, Threshold={cfg['threshold']}")
        
        success = run_cmd(["gradlew.bat", "bootRun", f"--args=--config {toml_path}"])
        if not success:
            print(f"Sweep config {cfg['id']} failed.")
            continue
            
        # Let's read the latest line appended to the ledger
        if os.path.exists(ledger_path):
            with open(ledger_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    print(f"Result for Config {cfg['id']}:")
                    print(f"  Top-1: {last_row.get('Top1Accuracy')}%")
                    print(f"  AnyMatch: {last_row.get('AnyMatchAccuracy')}%")
                    print(f"  RoutingECE: {last_row.get('RoutingECE')}")
                    print(f"  BridgeCount: {last_row.get('BridgeCount')}")
                    print(f"  DuplicateBridgeCount: {last_row.get('DuplicateBridgeCount')}")
                    print(f"  AvgMatchCount: {last_row.get('AvgMatchCount')}")
                    print(f"  ResidualCount: {last_row.get('ResidualCount')}")
        else:
            print("Ledger file not generated!")

if __name__ == "__main__":
    main()
