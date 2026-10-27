"""Counted C-2 proof for one RP12 lane-r2 build (run-operator; zero calls; worktree read-only). Ported from R1's
verify_arm_member.py / verify_arm_graft.py (experiment_results/archv2/rp12/B0_run) with paths moved to lane r2; for
MMLU_PRO_LB the item-count line is the census bracket (6,992 items / 6,799 components; prog L22242-L22247).
Usage: verify.py <arm> <tag>   (arm B0|B0p|o1|o2; tag a member or graft_flatleaf|graft_descent)"""
import hashlib, json, os, re, sqlite3, subprocess, sys
R = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(R, "..", "..", "..", "..", ".claude", "worktrees", "rp12-r2-run"))
POOL, SHA = "pv2_1575de61bb20e977", "79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6"
M = "2703f2c25807393605f863345c3dc0c8bd132849"
ARM, tag = sys.argv[1], sys.argv[2]
graft = tag.startswith("graft_")
K = "C-2b" if graft else "C-2a"
log = open(os.path.join(R, ARM + "." + tag + ".build.txt"), encoding="utf-8", errors="replace").read().replace("\r", "")
L = log.split("\n")
res = []
def chk(name, ok, evid):
    res.append(ok); print("[%s %s/%s] %s %s :: %s" % (K, ARM, tag, "PASS" if ok else "FAIL", name, evid))
db = sqlite3.connect("file:%s?mode=ro" % os.path.join(WT, "snapshots.db").replace("\\", "/"), uri=True)
def stamp(sid):
    row = db.execute("select settings from snapshots where id=?", (sid,)).fetchone() if sid else None
    return (json.loads(row[0]) or {}).get("buildStamp") if row and row[0] else None
man = json.load(open(os.path.join(WT, "experiment_results", "archv2", "rp12_r2", ARM, tag, "seed_42", "diagnostics", "run_manifest.json"), encoding="utf-8"))
if not graft:
    tc = [l for l in L if l.startswith("[THREAD-CAP]")]
    chk("THREAD-CAP availableProcessors=12", len(tc) >= 1 and all("availableProcessors=12" in l for l in tc), "%d line(s): %s" % (len(tc), tc[-1] if tc else "-"))
    sv = [l for l in L if "[SPLIT-V2] split taken as given" in l]
    ok = len(sv) == 1 and "one-to-one TRAIN and RESERVED hold" in sv[0] and "0 TRAIN rows share a stem key with the 8186 global reserved keys" in sv[0]
    chk("SPLIT-V2 one-to-one + 0 TRAIN stem-key overlap with 8186", ok, sv[0].split(" - ", 1)[-1] if sv else "-")
    to = [l for l in L if "[TRAIN-ONLY] global reserved keys installed: 8186" in l]
    chk("TRAIN-ONLY global reserved keys installed: 8186", len(to) == 1, to[0].split(" - ", 1)[-1] if to else "-")
    tg = [l for l in L if "[TRAIN-ONLY] saveSnapshot: 0 EVAL texts" in l]
    chk("TrainOnlyGuard 0 EVAL members", len(tg) == 1, tg[0].split(" - ", 1)[-1] if tg else "-")
    m = re.findall(r"Snapshot ID: (\S+)", log); sid = m[-1] if m else None
    st = stamp(sid)
    ok = bool(st) and st.get("poolId") == POOL and st.get("enginePoolSha256Lf") == SHA
    chk("stored buildStamp poolId/enginePoolSha256Lf", ok, "snapshot %s poolId=%s enginePoolSha256Lf=%s configSha256Lf=%s" % (sid, st and st.get("poolId"), st and st.get("enginePoolSha256Lf"), st and st.get("configSha256Lf")))
    ok = bool(man.get("split_v2")) and man.get("dirty_src") is False and man["split_v2"].get("pool_id") == POOL and man.get("commit") == M
    chk("manifest split_v2 + dirty_src=false + commit=M", ok, "commit=%s dirty_src=%s split_v2.pool_id=%s train_rows=%s" % (man.get("commit"), man.get("dirty_src"), man["split_v2"].get("pool_id"), man["split_v2"].get("train_rows")))
    llm = [l for l in L if re.search(r"ArcTaxonomyLLMClient|\[ARENA-LAT\]|labelNode|LLM request|chat/completions|Generated label", l)]
    lab = [l for l in L if "Labeling:" in l]
    chk("0 labelling and 0 judge calls", len(llm) == 0 and all("false" in l for l in lab), "%d LLM-call log lines; %s" % (len(llm), lab[0].strip() if lab else "-"))
    if tag == "mmlu_pro_lb":
        out = subprocess.run([sys.executable, os.path.join(R, "census.py"), os.path.join(WT, "multicorpus_cache_v1.db")], capture_output=True, text=True).stdout.strip()
        ok = "TRAIN rows 7228 ->" in out and "-> 6992 items" in out and "/ 6799 components" in out
        chk("MMLU_PRO_LB census 6,992 items / 6,799 components (bracket e7348f3) with TRAIN rows; manifest train_rows", ok, "%s | manifest train_rows=%s" % (out, man["split_v2"].get("train_rows")))
else:
    um = [l.split(" - ", 1)[-1] for l in L if "[SPLIT-V2] UNION member" in l and "== the file's" in l]
    fo = [l for l in L if "[SPLIT-V2]" in l and "foreign" in l.lower()]
    chk("exactly 6 UNION member == the file's, 0 foreign", len(um) == 6 and not fo, "%d member lines, %d foreign lines" % (len(um), len(fo)))
    for u in um: print("    " + u)
    to = [l.split(" - ", 1)[-1] for l in L if "[TRAIN-ONLY] union graft: global reserved keys installed: 8186 (%s)" % POOL in l]
    chk("TRAIN-ONLY union graft 8186", len(to) == 1, to[0] if to else "-")
    pp = [l.split(" - ", 1)[-1] for l in L if "[POOL-PIN]" in l]
    chk("POOL-PIN line", len(pp) >= 1, " | ".join(p[:160] for p in pp))
    sid = ([re.search(r"Snapshot ID: (\S+)", l).group(1) for l in L if "union snapshot. Snapshot ID:" in l] or [None])[-1]
    toml = os.path.join(WT, "experiment_configs", "rp12_r2", ARM, tag + ".toml")
    lf = hashlib.sha256(open(toml, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    st = stamp(sid)
    chk("union snapshot buildStamp configSha256Lf == filled TOML LF sha", bool(st) and st.get("configSha256Lf") == lf, "snapshot %s stamp.configSha256Lf=%s toml_lf=%s poolId=%s" % (sid, st and st.get("configSha256Lf"), lf, st and st.get("poolId")))
    ok = bool(man.get("split_v2")) and man.get("union_routing_item_key") is True and man.get("commit") == M and man.get("dirty_src") is False
    chk("manifest split_v2 + union_routing_item_key=true + commit=M + dirty_src=false", ok, "split_v2.pool_id=%s union_routing_item_key=%s commit=%s dirty_src=%s" % ((man.get("split_v2") or {}).get("pool_id"), man.get("union_routing_item_key"), man.get("commit"), man.get("dirty_src")))
print("[%s %s/%s] COUNT %d/%d PASS; snapshot %s" % (K, ARM, tag, sum(res), len(res), sid))
sys.exit(0 if all(res) else 1)
