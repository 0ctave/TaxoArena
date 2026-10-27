import sys, json, urllib.request, urllib.error
sys.path.insert(0, "tools/analysis")
import embedder_arms as EA
texts = EA.needed_texts(); arm = EA.ARMS["gemma_card"]
def post(inp):
    body = json.dumps({"model": arm.model, "input": inp}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/embed", data=body, headers={"Content-Type":"application/json"}), timeout=600) as r: return None
    except urllib.error.HTTPError as e: return "HTTP %d %s" % (e.code, e.read().decode()[:400])
for s in range(0, len(texts), EA.BATCH):
    ch = texts[s:s+EA.BATCH]; err = post([arm.prefix + t for t in ch])
    if err:
        print("batch", s // EA.BATCH, "at", s, err, "chars", [len(t) for t in ch])
        for i, t in enumerate(ch):
            e1 = post([arm.prefix + t])
            if e1: print(" single", i, e1, "len", len(t), repr(t[:120]))
        e2 = post(ch); print(" batch WITHOUT prefix:", e2 or "OK")
        break
