"""Find the deployment's throughput knee by sweeping concurrency with realistic payloads.

WHY A SEPARATE PROBE. The obvious way to find the best concurrency is to relaunch the
arena at each level and watch it, but that discards experiment progress every time and
takes ~10 minutes per data point. This sweeps the endpoint directly, so one short run
answers the question and the experiment is then launched ONCE at the chosen value.

WHY REALISTIC PAYLOADS. A probe with max_tokens=1 measures almost nothing useful:
in LLM serving, latency is dominated by GENERATION, which is sequential, not by prompt
prefill, which is parallel. A judge call sends ~1000 input tokens and generates a few
hundred (three free-text critiques plus a verdict). This probe mimics both sides, so
the latency it reports is comparable to what the arena actually experiences.

WHAT TO READ. Throughput is permits / latency, and latency RISES with permits because
of server-side queueing. The useful number is where throughput stops improving:

    calls/min climbing near-linearly  -> raise concurrency
    calls/min flattening              -> at the knee, stop here
    any 429                           -> over the limit, step back

Measured on this deployment before the sweep: 4 permits -> 10.4 s/call, 24 permits ->
16.9 s/call, i.e. ~0.235 s of added latency per permit, implying an asymptote near
255 calls/min -- BELOW the 500 RPM / 500k TPM quota. If that holds, the server's
concurrency handling binds before the quota ever does and no 429 will appear.

    python tools/analysis/azure_concurrency_sweep.py [--levels 24,48,64,96] [--calls 60]

Credentials come from the root .env. Neither the key nor the full endpoint is printed.
"""
import json, os, sys, time, threading, queue, urllib.request, urllib.error

API_VERSION = "2024-02-15-preview"
DEPLOYMENT = "Mistral-Large-3"
OUT_TOKENS = 250          # mimics the judge's three critiques + verdict


def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def build_prompt():
    """~1000 input tokens, matching a real judge call."""
    system = ("You are an expert academic evaluator. Critique each response against "
              "the rubric, compare them, and declare a winner. " + "Evaluate carefully. " * 90)
    trace = ("We refer to the standard approach for this problem. First we identify the "
             "governing relation, then substitute the given quantities and simplify. " * 6)
    user = (f"[Question]\nWhat is the resulting value under the stated conditions?\n\n"
            f"[Model A's Response]\n{trace}\n\n[Model B's Response]\n{trace}\n")
    return system, user


def one_call(url, key, system, user, results, timeout=180):
    body = json.dumps({
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": OUT_TOKENS, "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("api-key", key)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read()
            results.put(("ok", time.time() - t0))
    except urllib.error.HTTPError as e:
        try: e.read()
        except Exception: pass
        results.put((f"http{e.code}", time.time() - t0))
    except Exception as e:
        results.put((type(e).__name__, time.time() - t0))


def sweep(url, key, permits, total_calls):
    system, user = build_prompt()
    results = queue.Queue()
    pending = list(range(total_calls))
    lock = threading.Lock()
    t_start = time.time()

    def worker():
        while True:
            with lock:
                if not pending: return
                pending.pop()
            one_call(url, key, system, user, results)

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(permits)]
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = time.time() - t_start

    lat, codes = [], {}
    while not results.empty():
        c, d = results.get()
        codes[c] = codes.get(c, 0) + 1
        if c == "ok": lat.append(d)
    lat.sort()
    return dict(permits=permits, elapsed=elapsed, n=total_calls,
                ok=codes.get("ok", 0), codes=codes,
                cpm=60.0 * codes.get("ok", 0) / elapsed if elapsed > 0 else 0,
                p50=lat[len(lat)//2] if lat else 0.0,
                p90=lat[int(len(lat)*0.9)] if lat else 0.0)


def main():
    env = load_env()
    ep = os.environ.get("AZURE_AI_ENDPOINT") or env.get("AZURE_AI_ENDPOINT", "")
    key = os.environ.get("AZURE_AI_API_KEY") or env.get("AZURE_AI_API_KEY", "")
    if not ep or not key:
        print("AZURE_AI_ENDPOINT / AZURE_AI_API_KEY not found"); return 1
    url = f"{ep.rstrip('/')}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

    levels = [24, 48, 64, 96]
    calls = 60
    if '--levels' in sys.argv: levels = [int(x) for x in sys.argv[sys.argv.index('--levels')+1].split(',')]
    if '--calls' in sys.argv: calls = int(sys.argv[sys.argv.index('--calls')+1])

    print(f"concurrency sweep -- {DEPLOYMENT}, {calls} calls per level, ~{OUT_TOKENS} output tokens each")
    print(f"levels: {levels}\n")
    print(f"{'permits':>8}{'calls/min':>11}{'verdicts/min':>14}{'p50 lat':>9}{'p90 lat':>9}{'errors':>22}")
    print('-' * 74)
    prev = None
    for p in levels:
        r = sweep(url, key, p, calls)
        errs = {k: v for k, v in r['codes'].items() if k != 'ok'}
        gain = f"  (+{100*(r['cpm']/prev-1):.0f}%)" if prev and prev > 0 else ""
        print(f"{p:>8}{r['cpm']:>11.1f}{r['cpm']/2:>14.1f}{r['p50']:>9.1f}{r['p90']:>9.1f}"
              f"{str(errs) if errs else 'none':>22}{gain}")
        if any(k.startswith('http429') for k in errs):
            print(f"\n  429 at {p} permits -- this is the ceiling. Use the level below.")
            break
        prev = r['cpm']
        time.sleep(5)   # let the token bucket refill between levels
    print("\nverdicts/min = calls/min / 2 (each verdict is two calls, position-swapped)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
