"""Read the Azure deployment's live rate-limit margin.

WHY THIS EXISTS. The portal shows the quota (TPM/RPM ceilings). It does not show how
much of it a running arena is consuming right now. Azure returns that per response, in
headers, and langchain4j does not surface them -- so the only way to see the margin is
to ask the endpoint directly.

Run it alongside a live arena run. One probe costs a single request and ~1 output token,
which is noise against a 500-request-per-minute budget.

    python tools/analysis/azure_ratelimit_probe.py           # one reading
    python tools/analysis/azure_ratelimit_probe.py --watch   # every 30s until Ctrl-C

Credentials come from the root .env (AZURE_AI_ENDPOINT, AZURE_AI_API_KEY). Neither the
key nor the full endpoint host is ever printed.
"""
import json, os, sys, time, urllib.request, urllib.error

API_VERSION = "2024-02-15-preview"   # matches config/application.yml
DEPLOYMENT = "Mistral-Large-3"       # matches config/application.yml


def load_env(path=".env"):
    env = {}
    if not os.path.exists(path):
        return env
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def probe(endpoint, key, deployment=DEPLOYMENT):
    """Minimal chat completion. Returns (status, headers, error_text)."""
    base = endpoint.rstrip("/")
    # Azure OpenAI-style deployment path first; fall back to the Foundry-style
    # direct path, which some model deployments use instead.
    urls = [
        f"{base}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}",
        f"{base}/chat/completions?api-version={API_VERSION}",
    ]
    body = json.dumps({
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "temperature": 0,
    }).encode()

    last = None
    for url in urls:
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("api-key", key)              # Azure OpenAI
        req.add_header("Authorization", f"Bearer {key}")  # Foundry serverless
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, dict(r.headers), None
        except urllib.error.HTTPError as e:
            hdrs = dict(e.headers or {})
            # 429 is a successful probe: the headers are exactly what we came for.
            if e.code == 429:
                return e.code, hdrs, e.read().decode("utf-8", "replace")[:200]
            last = (e.code, hdrs, e.read().decode("utf-8", "replace")[:200])
        except Exception as e:  # network, DNS, TLS
            last = (0, {}, str(e)[:200])
    return last if last else (0, {}, "no response")


def report(status, headers, err):
    keys = {k.lower(): v for k, v in headers.items()}
    interesting = {k: v for k, v in keys.items()
                   if "ratelimit" in k or "retry-after" in k or k == "x-request-id"}
    ts = time.strftime("%H:%M:%S")
    if status == 429:
        print(f"[{ts}] HTTP 429 THROTTLED — you are at the ceiling. "
              f"retry-after={keys.get('retry-after', '?')}s")
    elif status and 200 <= status < 300:
        print(f"[{ts}] HTTP {status} ok")
    else:
        print(f"[{ts}] HTTP {status} — {err}")
        return
    if interesting:
        for k in sorted(interesting):
            print(f"        {k}: {interesting[k]}")
    else:
        print("        no x-ratelimit-* headers returned by this deployment.")
        print("        Some Azure AI Foundry model deployments omit them; in that case the")
        print("        only signal is the 429 itself, so raise concurrency in steps and")
        print("        treat the first 429 as the wall.")


def main():
    env = load_env()
    endpoint = os.environ.get("AZURE_AI_ENDPOINT") or env.get("AZURE_AI_ENDPOINT", "")
    key = os.environ.get("AZURE_AI_API_KEY") or env.get("AZURE_AI_API_KEY", "")
    if not endpoint or not key:
        print("AZURE_AI_ENDPOINT / AZURE_AI_API_KEY not found in environment or .env")
        return 1
    host = endpoint.split("//")[-1].split(".")[0]
    print(f"probing deployment '{DEPLOYMENT}' at {host[:6]}...  (api-version {API_VERSION})\n")

    watch = "--watch" in sys.argv
    while True:
        status, headers, err = probe(endpoint, key)
        report(status, headers, err)
        if not watch:
            return 0
        time.sleep(30)


if __name__ == "__main__":
    sys.exit(main())
