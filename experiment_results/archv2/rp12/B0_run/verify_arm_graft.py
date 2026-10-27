"""B0-4 (b) counted C-2 proof for one RP12 B0 union graft (run-operator; zero calls; worktree read-only). Usage: verify_graft.py <graft_tag>"""
import hashlib, json, os, re, sqlite3, sys
R = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(R, "..", "..", "..", "..", ".claude", "worktrees", "rp12-b0-run"))
POOL = "pv2_1575de61bb20e977"
ARM, tag = sys.argv[1], sys.argv[2]
L = open(os.path.join(R, ARM + "." + tag + ".build.txt"), encoding="utf-8", errors="replace").read().replace("\r", "").split("\n")
res = []
def chk(name, ok, evid):
    res.append(ok); print("[C-2b %s/%s] %s %s :: %s" % (ARM, tag, "PASS" if ok else "FAIL", name, evid))
um = [l.split(" - ", 1)[-1] for l in L if "[SPLIT-V2] UNION member" in l and "== the file's" in l]
fo = [l for l in L if "[SPLIT-V2]" in l and "foreign" in l.lower()]  # the config dump line carries v2ForeignMembers=[]; only [SPLIT-V2] foreign-member lines count
chk("exactly 6 UNION member == the file's, 0 foreign", len(um) == 6 and not fo, "%d member lines, %d foreign lines" % (len(um), len(fo)))
for u in um: print("    " + u)
to = [l.split(" - ", 1)[-1] for l in L if "[TRAIN-ONLY] union graft: global reserved keys installed: 8186 (%s)" % POOL in l]
chk("TRAIN-ONLY union graft 8186", len(to) == 1, to[0] if to else "-")
pp = [l.split(" - ", 1)[-1] for l in L if "[POOL-PIN]" in l]
chk("POOL-PIN line", len(pp) >= 1, " | ".join(p[:160] for p in pp))
sid = ([re.search(r"Snapshot ID: (\S+)", l).group(1) for l in L if "union snapshot. Snapshot ID:" in l] or [None])[-1]
toml = os.path.join(WT, "experiment_configs", "rp12", ARM, tag + ".toml")
lf = hashlib.sha256(open(toml, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
c = sqlite3.connect("file:%s?mode=ro" % os.path.join(WT, "snapshots.db").replace("\\", "/"), uri=True)
row = c.execute("select settings from snapshots where id=?", (sid,)).fetchone() if sid else None
st = (json.loads(row[0]) or {}).get("buildStamp") if row and row[0] else None
chk("union snapshot buildStamp configSha256Lf == filled TOML LF sha", bool(st) and st.get("configSha256Lf") == lf, "snapshot %s stamp.configSha256Lf=%s toml_lf=%s poolId=%s" % (sid, st and st.get("configSha256Lf"), lf, st and st.get("poolId")))
man = json.load(open(os.path.join(WT, "experiment_results", "archv2", "rp12", ARM, tag, "seed_42", "diagnostics", "run_manifest.json"), encoding="utf-8"))
chk("manifest split_v2 + union_routing_item_key=true", bool(man.get("split_v2")) and man.get("union_routing_item_key") is True, "split_v2.pool_id=%s union_routing_item_key=%s commit=%s dirty_src=%s" % ((man.get("split_v2") or {}).get("pool_id"), man.get("union_routing_item_key"), man.get("commit"), man.get("dirty_src")))
print("[C-2b %s/%s] COUNT %d/%d PASS; snapshot %s" % (ARM, tag, sum(res), len(res), sid))
sys.exit(0 if all(res) else 1)
