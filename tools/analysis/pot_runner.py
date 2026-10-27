"""POT-RUNNER - executes a model-written program-of-thought (PoT) solve inside a Docker container and maps
the value it prints to an option letter (REF-FORM-BY-CELL, docs/judge_v2_program.md L7027-L7354, registered
2026-09-18 at d2f5393, engineering note item 1; the runner decision taken 2026-09-19: CONTAINER runner).

  python tools/analysis/pot_runner.py --selftest      # >= 6 cases, the container runs for real; 0 API calls, no DB
  python tools/analysis/pot_runner.py --build         # (re)build the pinned image from the embedded Dockerfile
  python tools/analysis/pot_runner.py --image         # print the local image id against the pinned one

No network, no DB, no API call anywhere in this module. It is imported by pot_ref.py (the solve stage).

THE RUNNER OF RECORD (the author's decision, 2026-09-19; Docker 28.4.0, Linux engine):
  docker run --rm --network none --read-only --memory 512m --cpus 1 --pids-limit 64 --tmpfs /tmp:rw,size=64m
             --stop-timeout 1 -i --name pot_<hex> <IMAGE>
  stdin = PRELUDE + the model's program; no bind mounts; the host kills the container after WALL_TIMEOUT_S = 10 s
  (`docker kill`); stdout capped at STDOUT_CAP bytes, stderr kept (last 2 kB). The image is python:3.11-slim
  pinned by digest (BASE_IMAGE) with numpy 1.26.3 / sympy 1.12 / scipy 1.14.1, built once by --build; the built
  image id is PINNED_IMAGE_ID; execute() REFUSES when the local image id differs (the pin is a registered constant).
  The host-side textual blocklist (BLOCKED / ALLOWED_IMPORTS / BLOCKED_TOKENS) stays as a SECOND layer: a refused
  program is status `blocked` and never reaches the container.

STATUSES (the registration's table): picked | no_pick | blocked | timeout | error | degenerate (content_filter and
length are decided by the caller from finish_reason before the runner is called). The letter of record is what the
program PRINTS (`ANSWER: <letter>`, the LAST such line); prose is never parsed.
"""
import os, sys, re, io, json, uuid, time, argparse, tokenize, subprocess, threading

HERE = os.path.dirname(os.path.abspath(__file__))
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

BASE_IMAGE = "python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534"
IMAGE_TAG = "taxoarena-pot:1"
PINNED_IMAGE_ID = "sha256:0a218a1ae4cc58b8dc05b750fd0d2e518223a5a602efdd7e6f703fc0d3c1891e"   # built 2026-09-19 from DOCKERFILE
DOCKERFILE = ("FROM %s\n"
              "RUN pip install --no-cache-dir numpy==1.26.3 sympy==1.12 scipy==1.14.1 && useradd -m -u 10001 pot\n"
              "USER pot\nWORKDIR /tmp\n"
              "ENTRYPOINT [\"python\", \"-I\", \"-B\", \"-\"]\n" % BASE_IMAGE)
DOCKER_ARGS = ["--rm", "--network", "none", "--read-only", "--memory", "512m", "--cpus", "1", "--pids-limit", "64",
               "--tmpfs", "/tmp:rw,size=64m", "--stop-timeout", "1", "-i"]
WALL_TIMEOUT_S = 10.0
STDOUT_CAP = 8192
STDERR_KEEP = 2048
LETTERS = "ABCDEFGHIJ"

ALLOWED_IMPORTS = ("math", "cmath", "fractions", "decimal", "itertools", "functools", "statistics", "re", "numpy", "sympy", "scipy")
BLOCKED = ("os", "sys", "subprocess", "socket", "shutil", "pathlib", "urllib", "http", "requests", "ctypes", "importlib",
           "multiprocessing", "threading", "signal", "builtins", "code", "pickle", "marshal", "io", "tempfile", "glob")
BLOCKED_TOKENS = re.compile(r"(?<![\w.])(open|exec|eval|input|globals|locals|vars|compile|getattr|setattr|delattr|breakpoint|memoryview)\s*\("
                            r"|__import__|__builtins__|__subclasses__|__class__|__loader__|__spec__")
IMPORT_RE = re.compile(r"^\s*(?:import\s+([\w\.,\s]+?)(?:\s+as\s+\w+)?\s*$|from\s+([\w\.]+)\s+import\b)", re.M)

# ── the number parser shared by the prelude (inside the container) and the eligibility rule (pot_ref.py) ──
# Printed by pot_ref --dry-run as the eligibility regex of record.
NUM_PATTERN = (r"^\s*[~\u2248]?\s*(?P<sign>[-+])?\s*(?:(?P<mant>\d+(?:,\d{3})*(?:\.\d*)?|\.\d+)"
               r"(?:\s*(?:x?\s*10\s*\^\s*(?P<e1>[-+]?\d+)|[eE](?P<e2>[-+]?\d+)))?|10\s*\^\s*(?P<e3>[-+]?\d+))"
               r"(?P<frac>\s*/\s*\d+(?![\d.]))?")
NUMBER_PARSER_SRC = r'''
import re as _re
_NUM = _re.compile(%r)
def _norm(s):
    s = str(s).replace("\u2212", "-").replace("\u00d7", "x").replace("\u22c5", "x").replace("\u00b7", "x")
    s = _re.sub(r"\\(?:times|cdot)", "x", s)
    s = _re.sub(r"\\(?:mathrm|text|textrm|mathit|operatorname)\s*\{([^{}]*)\}", r"\1", s)
    s = s.replace("$", "").replace("{", "").replace("}", "").replace("\\,", "").replace("\\!", "").replace("~", " ")
    s = _re.sub(r"(\d)\s*\*\s*10\s*\*\*", r"\1 x 10^", s)
    return s
def first_number(s):
    """The first number of an option string (sign, thousands, decimal, x10^n / e-n / 10^n forms, a simple a/b
    fraction), after LaTeX / unicode normalisation; None when the option does not START with a number."""
    m = _NUM.match(_norm(s))
    if not m: return None
    if m.group("e3") is not None: v = 10.0 ** int(m.group("e3"))
    else:
        v = float(m.group("mant").replace(",", ""))
        e = m.group("e1") if m.group("e1") is not None else m.group("e2")
        if e is not None: v *= 10.0 ** int(e)
    if m.group("frac") and m.group("mant") and "." not in m.group("mant") and m.group("e1") is None and m.group("e2") is None:
        d = float(m.group("frac").strip().lstrip("/").strip())
        if d: v /= d
    return -v if m.group("sign") == "-" else v
''' % NUM_PATTERN
exec(compile(NUMBER_PARSER_SRC, "<pot_runner.number_parser>", "exec"))   # defines first_number / _norm here too

PRELUDE_TEMPLATE = NUMBER_PARSER_SRC + r'''
OPTIONS = %s
_LETTERS = "ABCDEFGHIJ"
def pick(value, rel_tol=0.02):
    """The NEAREST option by RELATIVE distance |v - x| / max(|x|, |v|) to the first number of every option; prints
    ANSWER: <letter> when that nearest option is within rel_tol and unique (no other option at the same distance,
    e.g. duplicated leading numbers); ANSWER: NONE on a tie, no parse, or nothing within rel_tol."""
    try: v = float(value)
    except Exception: print("ANSWER: NONE"); return None
    if v != v or v in (float("inf"), float("-inf")): print("ANSWER: NONE"); return None
    d = []
    for i, o in enumerate(OPTIONS):
        x = first_number(o)
        if x is None: continue
        d.append((abs(v - x) / max(abs(x), abs(v), 1e-300) if (v or x) else 0.0, i))
    d.sort()
    if not d or d[0][0] > rel_tol or (len(d) > 1 and d[1][0] - d[0][0] <= 1e-9): print("ANSWER: NONE"); return None
    print("ANSWER: " + _LETTERS[d[0][1]]); return _LETTERS[d[0][1]]
def pick_text(s):
    """Exact, then case-folded / whitespace-folded match of a string against the options."""
    t = str(s).strip(); f = " ".join(t.casefold().split())
    hits = [i for i, o in enumerate(OPTIONS) if o.strip() == t] or [i for i, o in enumerate(OPTIONS) if " ".join(o.casefold().split()) == f]
    if len(hits) != 1: print("ANSWER: NONE"); return None
    print("ANSWER: " + _LETTERS[hits[0]]); return _LETTERS[hits[0]]
# ---- model program follows ----
'''


def prelude(options):
    return PRELUDE_TEMPLATE % json.dumps([str(o) for o in options], ensure_ascii=True)


# ── static guards (host side, before the container) ──
def static_check(code):
    """Returns (status, reason): ('ok', '') | ('blocked', why) | ('degenerate', why)."""
    for m in IMPORT_RE.finditer(code):
        names = [n.strip().split(" ")[0] for n in (m.group(1) or m.group(2)).split(",")]
        for n in names:
            top = n.split(".")[0]
            if top in BLOCKED or top not in ALLOWED_IMPORTS:
                return "blocked", "import %s (allowed: %s)" % (n, ", ".join(ALLOWED_IMPORTS))
    t = BLOCKED_TOKENS.search(code)
    if t: return "blocked", "token %r" % t.group(0)
    if re.search(r"\b(?:import|__import__)\b", re.sub(r"(?m)^\s*(?:import|from)\s.*$", "", code)):
        return "blocked", "import outside a top-level import statement"
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, SyntaxError, IndentationError) as e:
        return "error", "tokenize: %s" % e
    names = [(i, t) for i, t in enumerate(toks) if t.type == tokenize.NAME]
    calls = {t.string for i, t in names if i + 1 < len(toks) and toks[i + 1].string == "("}
    if not ({"pick", "pick_text"} & calls):
        return "degenerate", "no pick() / pick_text() call"
    binary = False
    for i, t in enumerate(toks):
        if t.type == tokenize.OP and t.string in ("+", "-", "*", "/", "//", "**", "%", "@", "<<", ">>"):
            prev = toks[i - 1] if i else None
            if prev is not None and (prev.type in (tokenize.NAME, tokenize.NUMBER) or prev.string in (")", "]")):
                binary = True; break
    other_calls = calls - {"pick", "pick_text", "print", "float", "int", "str", "round", "abs", "len", "range"}
    if not binary and not other_calls:
        return "degenerate", "no arithmetic operator and no computation call (the answer was recalled, not computed)"
    return "ok", ""


# ── the container ──
def docker_image_id(tag=IMAGE_TAG):
    r = subprocess.run(["docker", "image", "inspect", tag, "--format", "{{.Id}}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def assert_image():
    iid = docker_image_id()
    if iid is None:
        raise SystemExit("[POT-RUNNER] image %s not present: run `python tools/analysis/pot_runner.py --build`" % IMAGE_TAG)
    if iid != PINNED_IMAGE_ID:
        raise SystemExit("[POT-RUNNER] image %s is %s, pinned %s: refused (the pin is a registered constant; rebuild with --build "
                         "and register the new id before any solve)" % (IMAGE_TAG, iid, PINNED_IMAGE_ID))
    return iid


def build_image():
    d = os.path.join(os.environ.get("TEMP", HERE), "pot_image_%s" % uuid.uuid4().hex[:8]); os.makedirs(d)
    open(os.path.join(d, "Dockerfile"), "w", newline="\n").write(DOCKERFILE)
    subprocess.run(["docker", "build", "-t", IMAGE_TAG, d], check=True)
    print("[POT-RUNNER] built %s -> %s (pinned %s)" % (IMAGE_TAG, docker_image_id(), PINNED_IMAGE_ID))


def _reader(stream, buf, cap, proc_name):
    total = 0
    while True:
        chunk = stream.read(4096)
        if not chunk: break
        if total < cap: buf.append(chunk[:cap - total])
        total += len(chunk)
        if total > 4 * cap and proc_name is not None:
            subprocess.run(["docker", "kill", proc_name], capture_output=True); proc_name = None
    buf.append(b"" if total <= cap else b"\n[stdout truncated at %d bytes, %d produced]" % (cap, total))


def run_in_container(program, timeout=WALL_TIMEOUT_S):
    """Raw execution (no static guard): returns dict(stdout, stderr, exit_code, wall, timed_out)."""
    name = "pot_" + uuid.uuid4().hex[:12]
    cmd = ["docker", "run", "--name", name] + DOCKER_ARGS + [IMAGE_TAG]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = [], []
    th = [threading.Thread(target=_reader, args=(p.stdout, out, STDOUT_CAP, name), daemon=True),
          threading.Thread(target=_reader, args=(p.stderr, err, STDERR_KEEP * 8, None), daemon=True)]
    for t in th: t.start()
    try:
        p.stdin.write(program.encode("utf-8")); p.stdin.close()
    except OSError: pass
    timed_out = False
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(["docker", "kill", name], capture_output=True)
        try: p.wait(timeout=15)
        except subprocess.TimeoutExpired: p.kill()
    for t in th: t.join(timeout=5)
    wall = time.time() - t0
    return dict(stdout=b"".join(out).decode("utf-8", "replace"), stderr=b"".join(err).decode("utf-8", "replace")[-STDERR_KEEP:],
                exit_code=(-9 if timed_out else p.returncode), wall=wall, timed_out=timed_out)


ANSWER_RE = re.compile(r"^ANSWER: ([A-J]|NONE)\s*$", re.M)


def execute(code, options, timeout=WALL_TIMEOUT_S):
    """The runner's contract: dict(status, letter, reason, stdout, stderr, exit_code, wall). Static guard first;
    then the container; the letter is the LAST `ANSWER:` line the program printed."""
    st, why = static_check(code)
    if st != "ok":
        return dict(status=st, letter="", reason=why, stdout="", stderr="", exit_code=None, wall=0.0)
    r = run_in_container(prelude(options) + code + "\n", timeout)
    if r["timed_out"]:
        return dict(status="timeout", letter="", reason="wall clock > %.0fs" % timeout, **{k: r[k] for k in ("stdout", "stderr", "exit_code", "wall")})
    if r["exit_code"] != 0:
        last = r["stderr"].strip().splitlines()[-1] if r["stderr"].strip() else ""
        return dict(status="error", letter="", reason="exit %s: %s" % (r["exit_code"], last[:200]), **{k: r[k] for k in ("stdout", "stderr", "exit_code", "wall")})
    hits = ANSWER_RE.findall(r["stdout"])
    if not hits:
        return dict(status="no_pick", letter="", reason="no ANSWER line printed (malformed output)", **{k: r[k] for k in ("stdout", "stderr", "exit_code", "wall")})
    last = hits[-1]
    if last == "NONE" or LETTERS.find(last) >= len(options):
        return dict(status="no_pick", letter="", reason="pick() printed NONE (tie / no parse / nothing within rel_tol)", **{k: r[k] for k in ("stdout", "stderr", "exit_code", "wall")})
    return dict(status="picked", letter=last, reason="", **{k: r[k] for k in ("stdout", "stderr", "exit_code", "wall")})


# ── selftest ──
def selftest():
    print("[POT-RUNNER] docker image %s id %s | pinned %s | base %s" % (IMAGE_TAG, docker_image_id(), PINNED_IMAGE_ID, BASE_IMAGE))
    assert_image()
    lbs = ["6 lbs", "7 lbs", "4.5 lbs", "5.8 lbs", "6.2 lbs", "5.6 lbs", "4.8 lbs", "7.2 lbs", "5.2 lbs", "6.5 lbs"]
    sci = ["1.00 \u00d7 10^6 N/m^2", "750 mm Hg", "$4.20 \\times 10^{-2}$ $\\text{atm}$", "16,704 years old", "-18 joules, -18 joules", "3/4 of the total"]
    # number parser (host side, no container)
    got = [first_number(o) for o in sci]
    assert got == [1e6, 750.0, 0.042, 16704.0, -18.0, 0.75], got
    assert first_number("3.00 $10^4 \\mathrm{~g}$") == 3e4 and first_number("1 in 7500") == 1.0 and first_number("36.1%, 0.763") == 36.1
    assert first_number("Lake B is alkaline.") is None and first_number("m + 25m") is None
    cases = [
        ("arithmetic pick", lbs, "import math\nm = 2.9 * 2\npick(m)\n", "picked", "D"),                       # 5.8
        ("option pick_text", lbs, "x = 4 + 2\npick_text('%d lbs' % x)\n", "picked", "A"),
        ("timeout", lbs, "i = 0\nwhile True:\n    i = i + 1\npick(i)\n", "timeout", ""),
        ("blocked import", lbs, "import os\npick(1 + 1)\n", "blocked", ""),
        ("blocked token", lbs, "x = eval('6')\npick(x + 0)\n", "blocked", ""),
        ("exception", lbs, "pick(1 / 0)\n", "error", ""),
        ("degenerate (recalled)", lbs, "pick_text('6 lbs')\n", "degenerate", ""),
        ("degenerate (no pick)", lbs, "print('the answer is A')\n", "degenerate", ""),
        ("no pick: far from every option", lbs, "pick(100 * 3)\n", "no_pick", ""),
        ("no pick: tie (duplicate leading numbers)", ["578 r1", "578 r2", "509"], "pick(2 * 289)\n", "no_pick", ""),
        ("dense options: nearest wins", ["277.3 K", "276.8 K", "272.8 $\\mathrm{K}$", "274.0 K"], "pick(273.15 + 1.0)\n", "picked", "D"),
        ("all options share the number: NONE", ["1 in 7500", "1 in 3000", "1 in 1000"], "pick(1 / 7500)\n", "no_pick", ""),
        ("malformed output (pick shadowed)", lbs, "def pick(v):\n    print('banana', v * 2)\npick(2.9)\n", "no_pick", ""),
        ("scientific notation pick", sci, "pick(4.2e-2 * 1.0)\n", "picked", "C"),
        ("numpy / sympy / scipy available", lbs, "import numpy as np, sympy, scipy\npick(float(np.sqrt(36.0)))\n", "picked", "A"),
    ]
    fails = 0; walls = []
    for name, opts, code, want_status, want_letter in cases:
        r = execute(code, opts)
        ok = r["status"] == want_status and r["letter"] == want_letter
        walls.append(r["wall"]); fails += not ok
        print("  %-36s -> %-10s %-2s wall %5.2fs  %s  %s" % (name, r["status"], r["letter"] or "-", r["wall"], "OK " if ok else "FAIL", (r["reason"] or "")[:70]))
    # the container's own isolation, bypassing the static guard on purpose (the guard would refuse these on the host)
    r = run_in_container("import socket\ns = socket.create_connection(('1.1.1.1', 80), timeout=3)\nprint('CONNECTED')\n")
    ok = r["exit_code"] != 0 and "CONNECTED" not in r["stdout"]
    fails += not ok
    print("  %-36s -> exit %s wall %5.2fs  %s  %s" % ("network attempt inside the container", r["exit_code"], r["wall"], "OK " if ok else "FAIL", r["stderr"].strip().splitlines()[-1:][0][:70] if r["stderr"].strip() else ""))
    r = run_in_container("open('/etc/pot_probe', 'w').write('x')\nprint('WROTE')\n")
    ok = r["exit_code"] != 0 and "WROTE" not in r["stdout"]
    fails += not ok
    print("  %-36s -> exit %s wall %5.2fs  %s  %s" % ("write to the read-only root fs", r["exit_code"], r["wall"], "OK " if ok else "FAIL", r["stderr"].strip().splitlines()[-1:][0][:70] if r["stderr"].strip() else ""))
    r = run_in_container("import os\nprint(sorted(os.environ), os.getcwd(), os.listdir('/'))\n")
    print("  %-36s -> %s" % ("container view (env, cwd, /)", r["stdout"].strip()[:150]))
    print("[POT-RUNNER] selftest %s: %d of %d cases failed | container wall min %.2fs median %.2fs max %.2fs (the timeout case included)"
          % ("PASS" if not fails else "FAIL", fails, len(cases) + 2, min(walls), sorted(walls)[len(walls) // 2], max(walls)))
    return fails == 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--build", action="store_true"); ap.add_argument("--image", action="store_true")
    a = ap.parse_args()
    if a.build: build_image()
    elif a.image: print("local %s | pinned %s | base %s" % (docker_image_id(), PINNED_IMAGE_ID, BASE_IMAGE))
    elif a.selftest: sys.exit(0 if selftest() else 1)
    else: ap.print_help()
