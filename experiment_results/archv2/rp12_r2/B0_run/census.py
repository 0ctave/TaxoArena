"""[OPERATOR-CENSUS] MMLU_PRO_LB TRAIN items (i:+stem_key) under the side export (zero calls; DB opened read-only).
Same counting as the data-steward's [ITEM-CENSUS] (prog L22245-L22247) and mmlu_gold_geometry.member: corpus_questions
source MMLU_PRO, non-blank, side TRAIN, tagged mc6-2026-09-11. Usage: census.py <multicorpus_db> [snapshot_db snapshot_id]"""
import os, sys, json, sqlite3
TA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools", "analysis")
sys.path.insert(0, os.path.normpath(TA)); sys.path.insert(0, os.path.normpath(os.path.join(TA, "..", "..")))
import v2_engine_pool as EP
from data_v2 import common as DC
db = sys.argv[1]
side, smeta = EP.read_side(os.path.join(os.path.normpath(os.path.join(TA, "..", "..")), EP.DEFAULT_SIDE))
con = sqlite3.connect("file:%s?mode=ro&immutable=1" % db.replace("\\", "/"), uri=True)
rows = con.execute("SELECT question_id, text FROM corpus_questions WHERE source='MMLU_PRO' ORDER BY question_id").fetchall()
k = DC.KeyCache(); n = tr = 0; items = {}; texts = set(); other = 0
for qid, text in rows:
    if text is None or EP._kotlin_blank(text): continue
    it = "i:" + k.stem(text); si = side.get(it)
    if si is None or "mc6-2026-09-11" not in si[2]: continue
    n += 1
    if si[1] == "TRAIN": tr += 1; items[it] = si[0]; texts.add(text)
    else: other += 1
print("[OPERATOR-CENSUS] MMLU_PRO_LB rows %d (tagged); TRAIN rows %d -> %d texts -> %d items (i:+stem_key) / %d components; EVAL/GATE rows %d; side export sha256-lf %s"
      % (n, tr, len(texts), len(items), len(set(items.values())), other, smeta.get("sha256_lf", "")[:16]))
