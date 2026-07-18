import sqlite3
import json
import numpy as np
import sys
import os
from datetime import datetime

def hash_query_py(text):
    import hashlib
    digest = hashlib.sha256(text.encode('utf-8')).digest()
    return "".join(f"{b:02x}" for b in digest)

def clean_text(t):
    return t.strip().replace("\r\n", "\n")

def main():
    snapshots_db = "snapshots.db"
    embeddings_db = "embeddings_cache.db"
    ratings_db = "mmlu_pro_dataset_cache_v2.db"

    if not os.path.exists(snapshots_db):
        print(f"Error: {snapshots_db} not found!")
        sys.exit(1)
    if not os.path.exists(embeddings_db):
        print(f"Error: {embeddings_db} not found!")
        sys.exit(1)

    # 0. Load reserved test query texts to ensure information separation (no Q_test in baselines)
    reserved_texts = set()
    if os.path.exists(ratings_db):
        try:
            conn_rat = sqlite3.connect(ratings_db)
            cursor_rat = conn_rat.cursor()
            cursor_rat.execute("SELECT DISTINCT question_text FROM eval_results WHERE is_reserved = 1")
            for (txt,) in cursor_rat.fetchall():
                if txt:
                    reserved_texts.add(txt)
            conn_rat.close()
            print(f"Loaded {len(reserved_texts)} reserved test query texts from ratings.db.")
        except Exception as e:
            print(f"Warning: Failed to load reserved flags from ratings.db: {e}")

    # 1. Connect to database and find the latest snapshot
    conn_snap = sqlite3.connect(snapshots_db)
    cursor_snap = conn_snap.cursor()

    cursor_snap.execute("SELECT id, graph, metrics, settings, reserved_queries, config FROM snapshots ORDER BY timestamp DESC LIMIT 1")
    row = cursor_snap.fetchone()
    if not row:
        print("Error: No snapshots found in snapshots.db!")
        sys.exit(1)

    template_id, graph_json, metrics_json, settings_json, reserved_queries_json, config_json = row
    print(f"Using template snapshot: {template_id}")

    graph = json.loads(graph_json)
    nodes = graph["nodes"]
    root_id = graph["rootId"]

    # Count the leaf nodes in the template graph (nodes with no children)
    num_leaves = sum(1 for node in nodes if not node.get("childIds"))
    print(f"Detected {num_leaves} leaf nodes in the template graph.")
    if num_leaves <= 1:
        print("Warning: Template graph has 1 or fewer leaf nodes. Defaulting to 17.")
        num_leaves = 17

    # Collect all query IDs from nodes
    all_query_ids = []
    for node in nodes:
        if node.get("queryIds"):
            all_query_ids.extend(node["queryIds"])
    all_query_ids = list(set(all_query_ids))
    print(f"Found {len(all_query_ids)} unique query IDs in the template graph.")

    # 2. Connect to embeddings_cache.db to get query id -> raw_text mapping and raw_text -> vector mapping
    conn_emb = sqlite3.connect(embeddings_db)
    cursor_emb = conn_emb.cursor()

    # Load queries mapping
    query_id_to_text = {}
    cursor_emb.execute("SELECT id, raw_text FROM queries")
    for q_id, raw_text in cursor_emb.fetchall():
        query_id_to_text[q_id] = raw_text
    print(f"Loaded {len(query_id_to_text)} query mappings from queries table.")

    # Load embeddings
    text_to_emb = {}
    cursor_emb.execute("SELECT query, vector FROM embeddings")
    for q_text, vec_blob in cursor_emb.fetchall():
        # Interpret vector as big-endian float32
        vec = np.frombuffer(vec_blob, dtype='>f4').copy()
        if len(vec) == 0:
            continue
        text_to_emb[q_text] = vec
    print(f"Loaded {len(text_to_emb)} valid embeddings from cache.")

    # Map our template query IDs to their raw texts and embeddings, excluding Q_test
    valid_query_ids = []
    valid_query_texts = []
    embeddings_list = []
    
    text_to_id = {f"q_{hash_query_py(txt)}": txt for txt in text_to_emb.keys()}
    excluded_count = 0

    for q_id in all_query_ids:
        raw_text = query_id_to_text.get(q_id) or text_to_id.get(q_id)
        if raw_text and raw_text in text_to_emb:
            # Check if the query is in the reserved test set
            cleaned = clean_text(raw_text)
            is_reserved = False
            for r_txt in reserved_texts:
                if clean_text(r_txt) == cleaned:
                    is_reserved = True
                    break
            
            if is_reserved:
                excluded_count += 1
                continue

            valid_query_ids.append(q_id)
            valid_query_texts.append(raw_text)
            embeddings_list.append(text_to_emb[raw_text])

    print(f"Excluded {excluded_count} evaluation queries from baseline fitting.")
    print(f"Found construction embeddings for {len(valid_query_ids)} / {len(all_query_ids) - excluded_count} queries.")
    if not valid_query_ids:
        print("Error: No construction embeddings found for queries!")
        sys.exit(1)

    X = np.array(embeddings_list)
    print(f"Construction embedding matrix shape: {X.shape}")
    
    # L2 normalize embeddings safely
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    X = X / norms

    # Try importing sklearn
    try:
        from sklearn.cluster import KMeans, AgglomerativeClustering
    except ImportError:
        print("sklearn not installed. Installing scikit-learn...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn", "scipy"])
        from sklearn.cluster import KMeans, AgglomerativeClustering

    # Adjust num_leaves if it exceeds dataset size
    if num_leaves > len(valid_query_ids):
        print(f"Warning: Leaf count {num_leaves} exceeds dataset size {len(valid_query_ids)}. Adjusting k to {len(valid_query_ids)}.")
        num_leaves = len(valid_query_ids)

    # 3. Generate Flat k-means baseline
    print(f"Running Flat k-means (k={num_leaves})...")
    kmeans = KMeans(n_clusters=num_leaves, random_state=42, n_init=10)
    labels_kmeans = kmeans.fit_predict(X)

    # 4. Generate HAC Ward baseline
    print(f"Running HAC Ward (cut={num_leaves})...")
    ward = AgglomerativeClustering(n_clusters=num_leaves, linkage='ward')
    labels_ward = ward.fit_predict(X)

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Helper function to build flat SerializedGraph JSON
    def build_flat_graph(valid_query_ids, X, labels):
        flat_nodes = []
        
        # Root node
        root_node = {
            "id": "root",
            "label": "Root",
            "depth": 0,
            "childIds": [f"leaf_{i}" for i in range(num_leaves)],
            "crossLinkChildIds": [],
            "parentIds": [],
            "vmfMu": [0.0] * X.shape[1],
            "vmfKappa": 0.0,
            "vmfLogNormalizer": 0.0,
            "niwM0": None,
            "niwKappa0": 0.0,
            "niwNu0": 0.0,
            "niwLambda": None,
            "dasguptaDeltaNorm": 0.0,
            "phaseCompleted": 2,
            "treeParentId": None,
            "judgePrompt": "You are an expert evaluator for general queries.",
            "judgeRubric": "Grade based on domain correctness.",
            "queryIds": [],
            "proportionalWeight": 1.0,
            "judgeCorpusFingerprint": None,
            "judgeModelVersion": None
        }
        flat_nodes.append(root_node)

        for i in range(num_leaves):
            idx = np.where(labels == i)[0]
            cluster_query_ids = [valid_query_ids[j] for j in idx]
            cluster_embs = X[idx]
            
            # compute centroid
            if len(cluster_embs) > 0:
                mu = np.mean(cluster_embs, axis=0)
                mu_norm = np.linalg.norm(mu)
                if mu_norm > 0:
                    mu = mu / mu_norm
                mu_list = mu.tolist()
            else:
                mu_list = [0.0] * X.shape[1]

            leaf_node = {
                "id": f"leaf_{i}",
                "label": f"Cluster_{i}",
                "depth": 1,
                "childIds": [],
                "crossLinkChildIds": [],
                "parentIds": ["root"],
                "vmfMu": mu_list,
                "vmfKappa": 10.0,
                "vmfLogNormalizer": 0.0,
                "niwM0": None,
                "niwKappa0": 0.0,
                "niwNu0": 0.0,
                "niwLambda": None,
                "dasguptaDeltaNorm": 0.0,
                "phaseCompleted": 2,
                "treeParentId": "root",
                "judgePrompt": f"You are an expert evaluator for Cluster_{i}.",
                "judgeRubric": "Grade based on domain correctness.",
                "queryIds": cluster_query_ids,
                "proportionalWeight": 1.0,
                "judgeCorpusFingerprint": None,
                "judgeModelVersion": None
            }
            flat_nodes.append(leaf_node)

        return {
            "rootId": "root",
            "nodes": flat_nodes,
            "distillationEnabled": False
        }

    # 5. Generate Random Null baseline (shuffling queries preserving leaf topology sizes)
    print("Running Random Null baseline...")
    rng = np.random.default_rng(42)
    shuffled_query_ids = valid_query_ids.copy()
    rng.shuffle(shuffled_query_ids)

    # Reconstruct original graph but with shuffled queryIds in leaves
    shuffled_nodes = []
    query_ptr = 0
    
    # Map query ID to its L2 embedding for centroid calculation
    query_id_to_emb_map = {valid_query_ids[i]: X[i] for i in range(len(valid_query_ids))}

    for node in nodes:
        new_node = node.copy()
        if not node.get("childIds") and node.get("queryIds"):
            # Filter out any pre-existing Q_test IDs that might be in the node's query list
            node_con_queries = [q_id for q_id in node["queryIds"] if q_id in query_id_to_emb_map]
            orig_size = len(node_con_queries)
            
            new_query_ids = shuffled_query_ids[query_ptr : query_ptr + orig_size]
            query_ptr += orig_size
            new_node["queryIds"] = new_query_ids
            
            # Recompute centroid vmfMu
            leaf_embs = [query_id_to_emb_map[q_id] for q_id in new_query_ids if q_id in query_id_to_emb_map]
            if leaf_embs:
                mu = np.mean(leaf_embs, axis=0)
                mu_norm = np.linalg.norm(mu)
                if mu_norm > 0:
                    mu = mu / mu_norm
                new_node["vmfMu"] = mu.tolist()
        shuffled_nodes.append(new_node)

    shuffled_graph = {
        "rootId": root_id,
        "nodes": shuffled_nodes,
        "distillationEnabled": graph.get("distillationEnabled", False)
    }

    # Save to snapshots.db
    base_id = template_id.split("_Auto")[0] if "_Auto" in template_id else template_id
    
    def save_baseline(snap_id, desc, graph_obj):
        cursor_snap.execute("DELETE FROM snapshots WHERE id = ?", (snap_id,))
        cursor_snap.execute(
            "INSERT INTO snapshots (id, timestamp, description, graph, metrics, settings, reserved_queries, config) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                snap_id,
                timestamp_str,
                desc,
                json.dumps(graph_obj),
                metrics_json,
                settings_json,
                reserved_queries_json,
                config_json
            )
        )
        print(f"Saved snapshot: {snap_id} - {desc}")

    save_baseline(f"{base_id}_baseline_kmeans", f"Flat k-means (k={num_leaves}) baseline", build_flat_graph(valid_query_ids, X, labels_kmeans))
    save_baseline(f"{base_id}_baseline_ward", f"HAC Ward (cut={num_leaves}) baseline", build_flat_graph(valid_query_ids, X, labels_ward))
    save_baseline(f"{base_id}_baseline_randomnull", "Random null baseline (shuffled topology)", shuffled_graph)

    conn_snap.commit()
    conn_snap.close()
    conn_emb.close()
    print("All baseline snapshots generated successfully!")

if __name__ == "__main__":
    main()
