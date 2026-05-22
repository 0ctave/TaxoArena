import json
import numpy as np
import pandas as pd
import umap
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from collections import deque

def create_ellipsoid(center, cov, color, name, n_std=1.5):
    """Generates a lower-poly 3D ellipsoid mesh for performance."""
    vals, vecs = np.linalg.eigh(cov)
    vals = np.maximum(vals, 0)
    radii = n_std * np.sqrt(vals)
    
    # Lower subdivisions (12x12 instead of 20x20) for faster browser parsing
    u = np.linspace(0, 2 * np.pi, 12)
    v = np.linspace(0, np.pi, 12)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    
    ellipsoid = np.stack([x.flatten(), y.flatten(), z.flatten()])
    ellipsoid = (vecs @ (radii[:, None] * ellipsoid)).T + center
    
    return go.Mesh3d(
        x=ellipsoid[:, 0],
        y=ellipsoid[:, 1],
        z=ellipsoid[:, 2],
        alphahull=0,
        opacity=0.08, # Lighter opacity for nested view
        color=color,
        name=name,
        showlegend=False,
        hoverinfo='skip',
        visible=True
    )

def get_all_descendants(node_id, adj):
    """Returns a set of all descendant IDs for a given node."""
    descendants = set()
    queue = deque([node_id])
    while queue:
        curr = queue.popleft()
        for child in adj.get(curr, []):
            if child not in descendants:
                descendants.add(child)
                queue.append(child)
    return descendants

def visualize_taxonomy(file_path="taxonomy_visualization.json"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"Loading data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    queries = data['queries']
    nodes = data['nodes']

    if not queries:
        print("No queries found in export.")
        return

    # 1. Build DAG Structure and Assign Hierarchical Colors
    adj = {n['id']: n['childIds'] for n in nodes}
    
    # Propagate branch ownership (find which depth-1 root every node belongs to)
    roots = [n for n in nodes if n['depth'] == 1]
    branch_map = {} # node_id -> root_id
    colors = px.colors.qualitative.Prism # High contrast palette
    color_assignments = {}
    
    for i, root in enumerate(roots):
        root_color = colors[i % len(colors)]
        branch_map[root['id']] = root['id']
        color_assignments[root['id']] = root_color
        
        queue = deque([root['id']])
        while queue:
            parent_id = queue.popleft()
            for child_id in adj.get(parent_id, []):
                if child_id not in branch_map:
                    branch_map[child_id] = root['id']
                    color_assignments[child_id] = root_color
                    queue.append(child_id)

    for n in nodes:
        if n['id'] not in color_assignments:
            color_assignments[n['id']] = "#888888"

    # 2. UMAP Dimensionality Reduction
    df_queries = pd.DataFrame(queries)
    vectors = np.array(df_queries['vector'].tolist())
    
    centroid_data = []
    for node in nodes:
        for i, comp in enumerate(node['gmmComponents']):
            centroid_data.append({
                'label': node['label'],
                'vector': comp['mean'],
                'node_id': node['id'],
                'branch_id': branch_map.get(node['id'], 'other')
            })
    
    all_vectors = vectors
    if centroid_data:
        all_vectors = np.vstack([vectors, np.array([c['vector'] for c in centroid_data])])

    print(f"Running UMAP on {len(all_vectors)} points...")
    reducer = umap.UMAP(n_components=3, random_state=42, n_neighbors=15, min_dist=0.1, metric='cosine', low_memory=True)
    embedding = reducer.fit_transform(all_vectors)

    query_embeddings = embedding[:len(vectors)]
    centroid_embeddings = embedding[len(vectors):] if centroid_data else None

    df_queries['x'] = query_embeddings[:, 0]
    df_queries['y'] = query_embeddings[:, 1]
    df_queries['z'] = query_embeddings[:, 2]
    df_queries['branch_id'] = df_queries['assignedNodeId'].map(lambda x: branch_map.get(x, 'other'))

    # 3. Build Figure
    fig = go.Figure()
    trace_metadata = []

    # CONSOLIDATION: Group queries by depth-1 branch instead of individual node
    # This reduces trace count from ~200 to ~10
    unique_branches = df_queries['branch_id'].unique()
    for branch_id in unique_branches:
        sub = df_queries[df_queries['branch_id'] == branch_id]
        branch_node = next((n for n in nodes if n['id'] == branch_id), None)
        label = branch_node['label'] if branch_node else "Outliers"
        
        fig.add_trace(go.Scatter3d(
            x=sub['x'], y=sub['y'], z=sub['z'],
            mode='markers',
            marker=dict(size=1.5, color=color_assignments.get(branch_id, "#888888"), opacity=0.6),
            name=label,
            text=sub['text'],
            hoverinfo='text',
            customdata=sub['assignedNodeId'] # Store for isolation
        ))
        trace_metadata.append(('branch', branch_id))

    # B. Add Distribution Boundaries (Ellipsoids)
    if centroid_data:
        for i, c in enumerate(centroid_data):
            node_queries = df_queries[df_queries['assignedNodeId'] == c['node_id']]
            if len(node_queries) > 5:
                coords = node_queries[['x', 'y', 'z']].values
                center = centroid_embeddings[i]
                cov = np.cov(coords.T)
                
                fig.add_trace(create_ellipsoid(
                    center, cov, color_assignments[c['node_id']], f"Box {c['label']}"
                ))
                trace_metadata.append(('boundary', c['node_id']))

    # C. Add Centroids
    if centroid_data:
        for i, c in enumerate(centroid_data):
            fig.add_trace(go.Scatter3d(
                x=[centroid_embeddings[i, 0]],
                y=[centroid_embeddings[i, 1]],
                z=[centroid_embeddings[i, 2]],
                mode='markers',
                marker=dict(size=4, color=color_assignments[c['node_id']], symbol='diamond', 
                            line=dict(width=1, color='black')),
                name=f"Centroid {c['label']}",
                showlegend=False,
                visible=True
            ))
            trace_metadata.append(('centroid', c['node_id']))

    # 4. Interactive Menus
    boundary_indices = [i for i, m in enumerate(trace_metadata) if m[0] == 'boundary']
    centroid_indices = [i for i, m in enumerate(trace_metadata) if m[0] == 'centroid']
    query_indices = [i for i, m in enumerate(trace_metadata) if m[0] == 'branch']

    node_options = [{"label": "Show All", "id": "all"}] + [{"label": n['label'], "id": n['id']} for n in sorted(nodes, key=lambda x: x['label'])]
    dropdown_buttons = []
    
    for opt in node_options:
        if opt['id'] == 'all':
            visibility = [True] * len(fig.data)
        else:
            targets = get_all_descendants(opt['id'], adj) | {opt['id']}
            visibility = []
            for m_type, m_id in trace_metadata:
                if m_type == 'branch':
                    # A branch trace is visible if it IS the target OR one of its descendants is in that branch
                    # Simplified: only show if branch_id is in target set
                    visibility.append(m_id in targets)
                else:
                    visibility.append(m_id in targets)
        
        dropdown_buttons.append(dict(label=opt['label'], method="update", args=[{"visible": visibility}]))

    fig.update_layout(
        title=f"ArcTaxoAdapat: Optimized DAG Visualization (File: {os.path.basename(file_path)})",
        scene=dict(xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False), zaxis=dict(showticklabels=False)),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(itemsizing='constant'),
        updatemenus=[
            dict(buttons=dropdown_buttons, direction="down", showactive=True, x=0.02, xanchor="left", y=1.05, yanchor="top"),
            dict(
                type="buttons", direction="left",
                buttons=[
                    dict(label="Boxes On", method="restyle", args=[{"visible": True}, boundary_indices]),
                    dict(label="Boxes Off", method="restyle", args=[{"visible": False}, boundary_indices]),
                    dict(label="Centroids On", method="restyle", args=[{"visible": True}, centroid_indices]),
                    dict(label="Centroids Off", method="restyle", args=[{"visible": False}, centroid_indices]),
                ],
                pad={"r": 10, "t": 10}, x=0.5, xanchor="center", y=1.05, yanchor="top"
            ),
        ]
    )

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}.html"
    fig.write_html(output_file, include_plotlyjs='cdn') # Use CDN to reduce file size
    print(f"Optimized visualization saved to {output_file}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "taxonomy_visualization.json"
    visualize_taxonomy(path)
