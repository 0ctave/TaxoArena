#!/usr/bin/env python3
"""
Utility script to list and export a snapshot JSON from snapshots.db.
Usage:
  python export_snapshot.py --list
  python export_snapshot.py --id <snapshot_id> --out <output_path.json>
  python export_snapshot.py --latest --out <output_path.json>
"""
import sqlite3
import json
import argparse
import sys

def list_snapshots(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, description FROM snapshots ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("No snapshots found in snapshots.db.")
        return
        
    print(f"{'Snapshot ID':<60} | {'Timestamp':<20} | {'Description'}")
    print("-" * 110)
    for r in rows:
        print(f"{r[0]:<60} | {r[1]:<20} | {r[2]}")

def export_snapshot(db_path, snapshot_id, out_path, latest=False):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if latest:
        c.execute("SELECT id, graph FROM snapshots ORDER BY timestamp DESC LIMIT 1")
    else:
        c.execute("SELECT id, graph FROM snapshots WHERE id = ?", (snapshot_id,))
        
    row = c.fetchone()
    conn.close()
    
    if not row:
        if latest:
            print("No snapshots found in database.")
        else:
            print(f"Snapshot with ID '{snapshot_id}' not found.")
        sys.exit(1)
        
    sid, graph_str = row
    # Parse and pretty print the graph JSON
    graph_json = json.loads(graph_str)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph_json, f, indent=2)
    print(f"Successfully exported snapshot '{sid}' to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Export TaxoArena snapshots from snapshots.db to JSON.")
    parser.add_argument("--db", default="snapshots.db", help="Path to snapshots.db (default: snapshots.db)")
    parser.add_argument("--list", action="store_true", help="List all available snapshots")
    parser.add_argument("--id", help="ID of the snapshot to export")
    parser.add_argument("--latest", action="store_true", help="Export the latest snapshot")
    parser.add_argument("--out", default="exported_snapshot.json", help="Path to write the output JSON file")
    
    args = parser.parse_args()
    
    if args.list:
        list_snapshots(args.db)
    elif args.latest:
        export_snapshot(args.db, None, args.out, latest=True)
    elif args.id:
        export_snapshot(args.db, args.id, args.out, latest=False)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
