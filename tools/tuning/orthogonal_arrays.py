# orthogonal_arrays.py

L9_ARRAY = [
    [1, 1, 1, 1],
    [1, 2, 2, 2],
    [1, 3, 3, 3],
    [2, 1, 2, 3],
    [2, 2, 3, 1],
    [2, 3, 1, 2],
    [3, 1, 3, 2],
    [3, 2, 1, 3],
    [3, 3, 2, 1]
]

COLUMN_KEYS = ["A", "B", "C", "D"]

def verify_orthogonality():
    # Verify that for every pair of columns (A, B, C, D),
    # all 9 possible pairs (i, j) for i, j in {1, 2, 3} appear exactly once.
    num_rows = len(L9_ARRAY)
    num_cols = len(L9_ARRAY[0])
    
    for col1 in range(num_cols):
        for col2 in range(col1 + 1, num_cols):
            pairs = []
            for row in range(num_rows):
                pairs.append((L9_ARRAY[row][col1], L9_ARRAY[row][col2]))
            
            # Check unique pairs count
            unique_pairs = set(pairs)
            assert len(unique_pairs) == 9, f"Columns {col1} and {col2} are not orthogonal: {pairs}"
            
            # Check range of values
            for p in unique_pairs:
                assert p[0] in [1, 2, 3] and p[1] in [1, 2, 3], f"Invalid level value: {p}"
    return True

def map_levels_to_values(factors_spec):
    # factors_spec is a dict with 4 keys, e.g.
    # {
    #   "assignmentCosineGap": [0.02, 0.03, 0.05],
    #   "tauFunnelFloor": [0.75, 0.80, 0.90],
    #   "minBridgeCoverage": [25, 50, 75],
    #   "splitThreshold": [0.01, 0.02, 0.03]
    # }
    factor_names = sorted(list(factors_spec.keys()))
    if len(factor_names) != 4:
        raise ValueError(f"L9 requires exactly 4 factors. Found {len(factor_names)}: {factor_names}")
        
    mapped_configs = []
    for i, row in enumerate(L9_ARRAY):
        config_factors = {}
        for col_idx, factor_name in enumerate(factor_names):
            level = row[col_idx]  # 1, 2, or 3
            val_list = factors_spec[factor_name]
            if len(val_list) != 3:
                raise ValueError(f"Factor {factor_name} must have exactly 3 levels. Found: {val_list}")
            config_factors[factor_name] = val_list[level - 1]
        mapped_configs.append(config_factors)
        
    return mapped_configs

if __name__ == "__main__":
    verify_orthogonality()
    print("Orthogonality assertions passed successfully!")
