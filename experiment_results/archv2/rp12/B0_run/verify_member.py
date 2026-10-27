"""B0-4 (a) counted C-2 proof for one RP12 B0 member build (run-operator; zero calls; reads the worktree read-only).
Usage: python verify_member.py <tag>. Prints each proof line with PASS/FAIL and a final COUNT line."""
import json, os, re, sqlite3, sys
R = os.path.dirname(os.path.abspath(__file__))
WT = os.path.join(R, "..", "..", "..", "..", ".claude", "worktrees", "rp12-b0-run")
POOL, SHA = "pv2_1575de61bb20e977", "79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6"
tag = sys.argv[1]
log = open(os.path.join(R, tag + ".build.txt"), encoding="utf-8", errors="replace").read().replace("\r", "")
L = log.split("\n")
res = []
def chk(name, ok, evid):
    res.append(ok); print("[C-2a %s] %s %s :: %s" % (tag, "PASS" if ok else "FAIL", name, evid))
tc = [l for l in L if l.startswith("[THREAD-CAP]")]
chk("THREAD-CAP availableProcessors=12", len(tc) >= 1 and all("availableProcessors=12" in l for l in tc), "%d line(s): %s" % (len(tc), tc[-1] if tc else "-"))
sv = [l for l in L if "[SPLIT-V2] split taken as given" in l]
ok = len(sv) == 1 and "one-to-one TRAIN and RESERVED hold" in sv[0] and "0 TRAIN rows share a stem key with the 8186 global reserved keys" in sv[0]
chk("SPLIT-V2 one-to-one + 0 TRAIN stem-key overlap with 8186", ok, sv[0].split(" - ", 1)[-1] if sv else "-")
to = [l for l in L if "[TRAIN-ONLY] global reserved keys installed: 8186" in l]
chk("TRAIN-ONLY global reserved keys installed: 8186", len(to) == 1, to[0].split(" - ", 1)[-1] if to else "-")
tg = [l for l in L if "[TRAIN-ONLY] saveSnapshot: 0 EVAL texts" in l]
chk("TrainOnlyGuard 0 EVAL members", len(tg) == 1, tg[0].split(" - ", 1)[-1] if tg else "-")
m = re.findall(r"Snapshot ID: (\S+)", log)
sid = m[-1] if m else None
c = sqlite3.connect("file:%s?mode=ro" % os.path.join(WT, "snapshots.db").replace("\\", "/"), uri=True)
row = c.execute("select settings from snapshots where id=?", (sid,)).fetchone() if sid else None
st = (json.loads(row[0]) or {}).get("buildStamp") if row and row[0] else None
ok = bool(st) and st.get("poolId") == POOL and st.get("enginePoolSha256Lf") == SHA
chk("stored buildStamp poolId/enginePoolSha256Lf", ok, "snapshot %s poolId=%s enginePoolSha256Lf=%s configSha256Lf=%s" % (sid, st and st.get("poolId"), st and st.get("enginePoolSha256Lf"), st and st.get("configSha256Lf")))
man = json.load(open(os.path.join(WT, "experiment_results", "archv2", "rp12", "B0", tag, "seed_42", "diagnostics", "run_manifest.json"), encoding="utf-8"))
ok = bool(man.get("split_v2")) and man.get("dirty_src") is False and man["split_v2"].get("pool_id") == POOL
chk("manifest split_v2 + dirty_src=false", ok, "commit=%s dirty_src=%s split_v2.pool_id=%s train_rows=%s" % (man.get("commit"), man.get("dirty_src"), man["split_v2"].get("pool_id"), man["split_v2"].get("train_rows")))
llm = [l for l in L if re.search(r"ArcTaxonomyLLMClient|\[ARENA-LAT\]|labelNode|LLM request|chat/completions|Generated label", l)]
lab = [l for l in L if "Labeling:" in l]
chk("0 labelling and 0 judge calls", len(llm) == 0 and all("false" in l for l in lab), "%d LLM-call log lines; %s" % (len(llm), lab[0].strip().lstrip("2502 ") if lab else "-"))
if tag == "mmlu_pro_lb":
    t = [l for l in L if re.search(r"TRAIN item", l)]
    rows = man["split_v2"].get("train_rows")
    chk("MMLU_PRO_LB TRAIN item count 6,994 with TRAIN row count", any("6994" in l for l in t), "item lines: %s | train_rows=%s" % (t, rows))
print("[C-2a %s] COUNT %d/%d PASS; snapshot %s" % (tag, sum(res), len(res), sid))
sys.exit(0 if all(res) else 1)
