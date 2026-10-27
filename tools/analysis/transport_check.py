"""READY-TEMPLATE-TRANSPORT (RP32a): the zero-call transport check every READY of a POSTING instrument runs.

ORIGIN. The ARCH-V2-PILOT-K46 pilot 12 of 2026-09-25 (incident state 64ff708): all 24 attempts raised "unknown url type: 'None'"
because the K46 posting path never called rejudge_reasoning.load_env(); a PRESENCE check (configure_rr called) passed where a COUNT
check would have failed, and a fake call_full at the boundary hid the only line that differs from production. The reviewer's
proposed standing check (docs/reviews/READY_archv2_pilot_k46.md at 1f58df5, item 4; programme L18448-L18455, process lesson item 7;
queue item READY-TEMPLATE-TRANSPORT; plan docs/agents/plans/2026-10-02_rp21_rp20_drafts.md section 3, row RP32a):
  (a) name the function that fills the transport globals (rejudge_reasoning.load_env) and COUNT its call sites on the posting path
      (required >= 1);
  (b) the dry-run executes the SAME transport preflight the launch executes, and prints its line;
  (c) the READY lists "transport configuration (zero-call)" apart from "provider behaviour (pilot)".
ACCEPTANCE (registered in the plan): the check REFUSES on the K46 incident state 64ff708, by execution (`--acceptance`; it also shows
the fix 5e9de0f PASSES, so the refusal is not vacuous).

  python tools/analysis/transport_check.py --script tools/analysis/archv2_pilot_k46.py [--rev 64ff708]      (a) static count
  python tools/analysis/transport_check.py --script <s> --dry-run-cmd "<python s --dry-run ...>" [--env-var V] (b) executed
  python tools/analysis/transport_check.py --ready docs/reviews/READY_<x>.md                                  (c) lint
  python tools/analysis/transport_check.py --acceptance        (a) at 64ff708 -> REFUSED, at 5e9de0f -> PASS (git objects only)
  python tools/analysis/transport_check.py --selftest          fixtures under tempfile; every branch asserted by VALUE
  python tools/analysis/transport_check.py --mutants           the mutant table below, each run against the selftest

(a) STATIC, at a git revision (`git show <rev>:<path>`, nothing checked out) or on the working tree. Modules are the files under
tools/analysis (scripts put that directory on sys.path). Reachability starts at the ENTRY script's `if __name__ == "__main__":`
block and its top-level statements; edges are references (calls or not) to module-level functions, classes (every method of a
referenced class), methods through `self.`, and attributes of imported modules, with imports collected anywhere in a module
(function-level imports included) and followed through re-exports (`from judge_v2._base import rr`). A non-entry module's own
`__main__` block is NEVER reachable. Counted on the reachable nodes: POSTING REFERENCES (any reference resolving to
rejudge_reasoning.call_judge_full) and LOADER CALL SITES (a CALL whose callee resolves to rejudge_reasoning.load_env; a bare
reference is not a call site). Verdict: PASS iff posting references >= 1 AND loader call sites >= 1; otherwise REFUSED (no posting
reference = the check cannot certify a posting path, REFUSED, not "not applicable"). Attribute calls on objects of unknown type
are NOT resolved (printed as a count): the analysis under-approximates the path, so its errors fall on the REFUSE side.
LIMIT (stated, not hidden): "reachable from the entry" over-approximates "on the posting path" (a loader in an unrelated
reachable branch counts); (b) is the binding check for that reason.

(b) EXECUTED. The dry-run command is run twice in a child process with a sitecustomize that BLOCKS every socket connect (a
connect attempt is printed "[NO-NET]" and fails the check) and with <env-var> (default TAXOARENA_DATA_ROOT) pointing at a temp
root whose .env holds a FAKE endpoint https://transport-check.invalid and a fake key: leg 1 must print a line starting
"TRANSPORT PREFLIGHT: OK" naming host=transport-check.invalid (the preflight READ the configured .env); leg 2, with the key
removed from that .env, must exit non-zero and print a TRANSPORT refusal (the preflight BINDS). A hard-coded OK line fails leg 1
or leg 2; a missing line fails leg 1.

(c) LINT. The READY must carry a line naming "transport configuration" with "zero-call" and a DIFFERENT line naming "provider
behaviour" (or "behavior") with "pilot".

MUTANT TABLE (`--mutants`; each mutant is a module-level switch read by the code under test; KILLED = the selftest fails):
  M1 reach_all        loader sites counted in every loaded module, reachable or not        KILLED
  M2 refs_as_calls    a bare reference to load_env counted as a call site                  KILLED
  M3 no_refusal_leg   (b) skips leg 2 (a hard-coded OK line passes)                        KILLED
  M4 same_line        (c) accepts both phrases on one line                                  KILLED
  M5 no_post_needed   (a) passes with 0 posting references                                  KILLED
  M6 foreign_main     a non-entry module's __main__ block is reachable                      KILLED
  M7 no_netblock      (b) runs without the socket block                                     KILLED
  (the run of record of the table is printed by --mutants and copied into the commit message)
Zero calls; writes only under tempfile; no database is opened.
"""
import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ANALYSIS_REL = "tools/analysis"
LOADER = ("rejudge_reasoning", "load_env")
POSTER = ("rejudge_reasoning", "call_judge_full")
INCIDENT_REV, FIX_REV = "64ff708", "5e9de0f"
K46_ENTRY = "tools/analysis/archv2_pilot_k46.py"
FAKE_HOST = "transport-check.invalid"
FAKE_ENDPOINT = "https://%s" % FAKE_HOST
FAKE_KEY = "TRANSPORT-CHECK-FAKE-KEY-not-a-secret"
MUTANT = os.environ.get("TRANSPORT_CHECK_MUTANT") or None
MUTANTS = ("reach_all", "refs_as_calls", "no_refusal_leg", "same_line", "no_post_needed", "foreign_main", "no_netblock")


# ============================================================================================ sources
class Tree:
    """The tools/analysis files of a git revision (rev) or of a directory on disk (rev None)."""

    def __init__(self, root, rev=None):
        self.root, self.rev = root, rev
        self._cache = {}
        if rev:
            out = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, ANALYSIS_REL], cwd=root, capture_output=True,
                                 text=True)
            if out.returncode != 0:
                raise SystemExit("[TREE] git ls-tree %s failed: %s" % (rev, out.stderr.strip()[:200]))
            self.files = [p for p in out.stdout.split("\n") if p.endswith(".py")]
        else:
            base = os.path.join(root, ANALYSIS_REL)
            self.files = []
            for d, _dirs, fs in os.walk(base):
                if "__pycache__" in d:
                    continue
                for f in fs:
                    if f.endswith(".py"):
                        self.files.append(os.path.relpath(os.path.join(d, f), root).replace("\\", "/"))

    def read(self, rel):
        if rel not in self._cache:
            if self.rev:
                out = subprocess.run(["git", "show", "%s:%s" % (self.rev, rel)], cwd=self.root, capture_output=True)
                if out.returncode != 0:
                    raise SystemExit("[TREE] git show %s:%s failed" % (self.rev, rel))
                txt = out.stdout.decode("utf-8")
            else:
                txt = open(os.path.join(self.root, rel), encoding="utf-8").read()
            self._cache[rel] = txt.replace("\r\n", "\n")
        return self._cache[rel]


def modname_of(rel):
    p = rel[len(ANALYSIS_REL) + 1:-3].split("/")
    if p[-1] == "__init__":
        p = p[:-1]
    return ".".join(p)


# ============================================================================================ module model
class Module:
    def __init__(self, name, rel, src):
        self.name, self.rel = name, rel
        self.is_pkg = rel.endswith("__init__.py")
        self.tree = ast.parse(src)
        self.funcs, self.classes, self.imports = {}, {}, {}
        self.main_body, self.top_body = [], []
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = {n.name: n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            elif _is_main_guard(node):
                self.main_body.extend(node.body)
            else:
                self.top_body.append(node)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.asname:
                        self.imports[a.asname] = ("module", a.name)
                    else:
                        self.imports[a.name.split(".")[0]] = ("module", a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                base = self._abs(node.module, node.level)
                for a in node.names:
                    if a.name != "*":
                        self.imports[a.asname or a.name] = ("from", base, a.name)

    def _abs(self, mod, level):
        if not level:
            return mod or ""
        pkg = self.name.split(".") if self.is_pkg else self.name.split(".")[:-1]
        if level > 1:
            pkg = pkg[:len(pkg) - (level - 1)]
        return ".".join([x for x in pkg + ([mod] if mod else []) if x])


def _is_main_guard(node):
    if not isinstance(node, ast.If):
        return False
    t = node.test
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name) and t.left.id == "__name__"
            and any(isinstance(c, ast.Constant) and c.value == "__main__" for c in t.comparators))


class Program:
    def __init__(self, tree):
        self.tree = tree
        self.by_name = {modname_of(r): r for r in tree.files}
        self.mods = {}
        self.unresolved = 0

    def mod(self, name):
        if name not in self.by_name:
            return None
        if name not in self.mods:
            rel = self.by_name[name]
            self.mods[name] = Module(name, rel, self.tree.read(rel))
        return self.mods[name]

    def symbol(self, modname, attr, depth=0):
        """('func', mod, name) | ('class', mod, name) | ('module', name) | None for attr looked up in module modname."""
        if depth > 12:
            return None
        m = self.mod(modname)
        if m is None:
            return None
        if attr in m.funcs:
            return ("func", modname, attr)
        if attr in m.classes:
            return ("class", modname, attr)
        if attr in m.imports:
            return self.follow(m.imports[attr], depth + 1)
        sub = modname + "." + attr if modname else attr
        if sub in self.by_name:
            return ("module", sub)
        return None

    def follow(self, imp, depth=0):
        if imp[0] == "module":
            return ("module", imp[1]) if imp[1] in self.by_name else ("extmodule", imp[1])
        base, name = imp[1], imp[2]
        if base in self.by_name:
            s = self.symbol(base, name, depth)
            if s is not None:
                return s
        full = base + "." + name if base else name
        if full in self.by_name:
            return ("module", full)
        return None

    def resolve_expr(self, m, expr, cls=None):
        """Resolve a Name / Attribute chain in module m to a symbol, or None."""
        chain = []
        e = expr
        while isinstance(e, ast.Attribute):
            chain.append(e.attr)
            e = e.value
        if not isinstance(e, ast.Name):
            return None
        chain.reverse()
        base = e.id
        if base == "self" and cls is not None and chain:
            if chain[0] in m.classes.get(cls, {}):
                return ("method", m.name, cls, chain[0]) if len(chain) == 1 else None
            return None
        if base in m.funcs:
            sym = ("func", m.name, base)
        elif base in m.classes:
            sym = ("class", m.name, base)
        elif base in m.imports:
            sym = self.follow(m.imports[base])
        else:
            return None
        for a in chain:
            if sym is None:
                return None
            if sym[0] == "module":
                sym = self.symbol(sym[1], a)
            elif sym[0] == "class":
                meths = self.mod(sym[1]).classes[sym[2]]
                sym = ("method", sym[1], sym[2], a) if a in meths else None
            else:
                return None
        return sym


def node_body(prog, node):
    kind = node[0]
    if kind == "main":
        return prog.mod(node[1]).main_body, None
    if kind == "top":
        return prog.mod(node[1]).top_body, None
    if kind == "func":
        return [prog.mod(node[1]).funcs[node[2]]], None
    if kind == "method":
        return [prog.mod(node[1]).classes[node[2]][node[3]]], node[2]
    return [], None


def analyse(tree, entry_rel):
    """-> dict(posts, loaders, loader_sites, post_sites, reachable, unresolved, verdict, reason)."""
    prog = Program(tree)
    ename = modname_of(entry_rel)
    em = prog.mod(ename)
    if em is None:
        raise SystemExit("[STATIC] the entry %s is not in %s" % (entry_rel, ANALYSIS_REL))
    start = [("main", ename), ("top", ename)]
    seen, stack = set(), list(start)
    posts, loaders = [], []
    unresolved_calls = 0
    if MUTANT == "foreign_main":
        for name in list(prog.by_name):
            if prog.mod(name).main_body:
                stack.append(("main", name))
    while stack:
        nd = stack.pop()
        if nd in seen:
            continue
        seen.add(nd)
        m = prog.mod(nd[1])
        body, cls = node_body(prog, nd)
        call_funcs = set()
        for stmt in body:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Call):
                    call_funcs.add(id(sub.func))
        for stmt in body:
            for sub in ast.walk(stmt):
                if not isinstance(sub, (ast.Name, ast.Attribute)):
                    continue
                if isinstance(sub, ast.Name) and not isinstance(sub.ctx, ast.Load):
                    continue
                sym = prog.resolve_expr(m, sub, cls)
                if sym is None:
                    if id(sub) in call_funcs and isinstance(sub, ast.Attribute):
                        unresolved_calls += 1
                    continue
                where = "%s:%d (%s)" % (m.rel, getattr(sub, "lineno", 0), "/".join(str(x) for x in nd[1:]))
                if sym == ("func",) + POSTER:
                    posts.append(where)
                if sym == ("func",) + LOADER and (id(sub) in call_funcs or MUTANT == "refs_as_calls"):
                    loaders.append(where)
                if sym[0] == "func":
                    stack.append(("func", sym[1], sym[2]))
                elif sym[0] == "method":
                    stack.append(("method", sym[1], sym[2], sym[3]))
                elif sym[0] == "class":
                    for meth in prog.mod(sym[1]).classes[sym[2]]:
                        stack.append(("method", sym[1], sym[2], meth))
    # remove duplicates of the same AST node visited through nested walks (a Name inside an Attribute chain is not re-resolved
    # because resolve_expr on the inner Name gives the base symbol, never the poster / loader itself unless imported by name)
    posts, loaders = sorted(set(posts)), sorted(set(loaders))
    if MUTANT == "reach_all":
        loaders = sorted(set(loaders) | set(_all_loader_sites(prog)))
    if MUTANT == "no_post_needed":
        ok = len(loaders) >= 1
    else:
        ok = len(posts) >= 1 and len(loaders) >= 1
    if not posts:
        reason = "no reference to rejudge_reasoning.call_judge_full is reachable from the entry: no posting path to certify"
    elif not loaders:
        reason = ("%d posting reference(s) reachable, 0 call sites of rejudge_reasoning.load_env on the path (the K46 incident "
                  "class: the transport globals are never filled)" % len(posts))
    else:
        reason = "%d posting reference(s), %d load_env call site(s) reachable" % (len(posts), len(loaders))
    return dict(posts=posts, loaders=loaders, reachable=len(seen), unresolved=unresolved_calls,
                verdict="PASS" if ok else "REFUSED", reason=reason, modules=len(prog.mods))


def _all_loader_sites(prog):
    out = []
    for name in list(prog.by_name):
        m = prog.mod(name)
        for sub in ast.walk(m.tree):
            if isinstance(sub, ast.Call) and prog.resolve_expr(m, sub.func) == ("func",) + LOADER:
                out.append("%s:%d (anywhere)" % (m.rel, sub.lineno))
    return out


def static_line(res, entry, rev):
    return ("(a) STATIC %s @ %s: posting references %d | load_env call sites %d | reachable nodes %d | modules parsed %d | "
            "unresolved attribute calls %d -> %s (%s)" % (entry, rev or "working tree", len(res["posts"]), len(res["loaders"]),
                                                        res["reachable"], res["modules"], res["unresolved"], res["verdict"],
                                                        res["reason"]))


# ============================================================================================ (b) executed
SITECUSTOMIZE = r'''
import socket, sys
_real = socket.socket.connect
def _blocked(self, *a, **k):
    sys.stdout.write("[NO-NET] a socket connect was attempted and BLOCKED by transport_check\n"); sys.stdout.flush()
    raise OSError("transport_check: network blocked")
socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
'''


def _env_root(tmp, with_key):
    d = os.path.join(tmp, "envroot_%s" % ("key" if with_key else "nokey"))
    os.makedirs(d, exist_ok=True)
    lines = ["AZURE_AI_ENDPOINT=%s" % FAKE_ENDPOINT]
    if with_key:
        lines.append("AZURE_GROK_API_KEY=%s" % FAKE_KEY)
    open(os.path.join(d, ".env"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    return d


def run_leg(cmd, env_var, root, tmp, cwd, timeout=900):
    env = dict(os.environ)
    env[env_var] = root
    env["PYTHONIOENCODING"] = "utf-8"
    if MUTANT != "no_netblock":
        sc = os.path.join(tmp, "netblock")
        os.makedirs(sc, exist_ok=True)
        open(os.path.join(sc, "sitecustomize.py"), "w", encoding="utf-8").write(SITECUSTOMIZE)
        env["PYTHONPATH"] = sc + os.pathsep + env.get("PYTHONPATH", "")
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       shell=isinstance(cmd, str), timeout=timeout)
    return p.returncode, (p.stdout or "") + "\n" + (p.stderr or "")


def executed_check(cmd, env_var="TAXOARENA_DATA_ROOT", cwd=None):
    tmp = tempfile.mkdtemp(prefix="transport_check_")
    try:
        rc1, out1 = run_leg(cmd, env_var, _env_root(tmp, True), tmp, cwd or ROOT)
        ok_lines = [l.strip() for l in out1.split("\n") if l.strip().startswith("TRANSPORT PREFLIGHT: OK")]
        net1 = "[NO-NET]" in out1
        leg1 = bool(ok_lines) and any("host=%s" % FAKE_HOST in l for l in ok_lines) and not net1
        if MUTANT == "no_refusal_leg":
            rc2, out2, leg2 = None, "", True
        else:
            rc2, out2 = run_leg(cmd, env_var, _env_root(tmp, False), tmp, cwd or ROOT)
            net2 = "[NO-NET]" in out2
            refused = any(("TRANSPORT PREFLIGHT: REFUSED" in l or l.strip().startswith("[ARCHV2-PILOT] TRANSPORT")
                           or "TRANSPORT: " in l) for l in out2.split("\n"))
            leg2 = rc2 not in (0, None) and refused and not net2 and not any(
                l.strip().startswith("TRANSPORT PREFLIGHT: OK") for l in out2.split("\n"))
        verdict = "PASS" if (leg1 and leg2) else "REFUSED"
        why = []
        if not ok_lines:
            why.append("leg 1 printed no 'TRANSPORT PREFLIGHT: OK' line")
        elif not any("host=%s" % FAKE_HOST in l for l in ok_lines):
            why.append("leg 1's OK line does not name the configured fake host (the preflight did not read the configured .env)")
        if net1:
            why.append("leg 1 attempted a network connection")
        if not leg2:
            why.append("leg 2 (key removed) did not refuse non-zero with a TRANSPORT refusal (rc %s)" % rc2)
        line = ("(b) EXECUTED %r with %s -> fake root: leg 1 rc %s, OK line %s | leg 2 (no key) rc %s, %s -> %s%s"
                % (cmd if isinstance(cmd, str) else " ".join(cmd), env_var, rc1, ok_lines[0] if ok_lines else "ABSENT", rc2,
                   "refused" if leg2 else "NOT refused", verdict, "" if verdict == "PASS" else " (" + "; ".join(why) + ")"))
        return dict(verdict=verdict, line=line, leg1=leg1, leg2=leg2, out1=out1, out2=out2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================================================ (c) lint
def ready_check(text):
    lines = text.replace("\r\n", "\n").split("\n")
    t_lines = [i for i, l in enumerate(lines) if re.search(r"transport configuration", l, re.I) and re.search(r"zero[- ]call", l, re.I)]
    p_lines = [i for i, l in enumerate(lines) if re.search(r"provider behaviou?r", l, re.I) and re.search(r"\bpilot", l, re.I)]
    if MUTANT == "same_line":
        ok = bool(t_lines) and bool(p_lines)
    else:
        ok = bool(t_lines) and bool(p_lines) and bool(set(t_lines) ^ set(p_lines)) and any(
            a != b for a in t_lines for b in p_lines)
    return dict(verdict="PASS" if ok else "REFUSED", t=t_lines, p=p_lines,
                line="(c) READY lint: 'transport configuration (zero-call)' at line(s) %s | 'provider behaviour (pilot)' at line(s) %s"
                     " | separate items %s -> %s" % ([i + 1 for i in t_lines], [i + 1 for i in p_lines],
                                                    any(a != b for a in t_lines for b in p_lines), "PASS" if ok else "REFUSED"))


# ============================================================================================ acceptance
def acceptance(root=ROOT):
    out = {}
    for rev in (INCIDENT_REV, FIX_REV):
        res = analyse(Tree(root, rev), K46_ENTRY)
        out[rev] = res
        print(static_line(res, K46_ENTRY, rev), flush=True)
    ok = out[INCIDENT_REV]["verdict"] == "REFUSED" and len(out[INCIDENT_REV]["loaders"]) == 0 \
        and len(out[INCIDENT_REV]["posts"]) >= 1 and out[FIX_REV]["verdict"] == "PASS"
    print("ACCEPTANCE: the K46 incident state %s is REFUSED (load_env call sites %d, posting references %d) and the fix %s PASSES "
          "(load_env call sites %d at %s) -> %s" % (INCIDENT_REV, len(out[INCIDENT_REV]["loaders"]), len(out[INCIDENT_REV]["posts"]),
                                                  FIX_REV, len(out[FIX_REV]["loaders"]), "; ".join(out[FIX_REV]["loaders"]) or "-",
                                                  "MET" if ok else "NOT MET"), flush=True)
    return 0 if ok else 1


# ============================================================================================ selftest
FIX_RR = '''
AZURE_ENDPOINT = None
AZURE_KEY = None
ROOT = "."
def load_env():
    global AZURE_ENDPOINT, AZURE_KEY
    AZURE_ENDPOINT = "x"; AZURE_KEY = "y"
def payload_bytes(s, u):
    return b""
def call_judge_full(system, user, retries=6):
    return payload_bytes(system, user)
def run():
    load_env()
    call_judge_full("s", "u")
if __name__ == "__main__":
    load_env()
    run()
'''
FIX_HELPER = '''
import rejudge_reasoning as rr
def load_transport():
    rr.load_env()
def unused_loader():
    rr.load_env()
'''
FIX_PKG_INIT = ""
FIX_PKG_BASE = '''
import rejudge_reasoning as rr
'''
FIX_PKG_TR = '''
from ._base import rr
def load_transport():
    rr.load_env()
'''
FIX_FOREIGN = '''
import rejudge_reasoning as rr
def nothing():
    return 1
if __name__ == "__main__":
    rr.load_env()
'''
ENTRIES = {
    # name: (source, expected verdict, expected posts, expected loaders)
    "e_pass_helper": ('''
import rejudge_reasoning as rr
import helper
def main():
    helper.load_transport()
    post(rr.call_judge_full)
def post(f):
    return f("s", "u")
if __name__ == "__main__":
    main()
''', "PASS", 1, 1),
    "e_refuse_none": ('''
import rejudge_reasoning as rr
def main():
    return rr.call_judge_full("s", "u")
if __name__ == "__main__":
    main()
''', "REFUSED", 1, 0),
    "e_refuse_unreachable": ('''
import rejudge_reasoning as rr
def main():
    return rr.call_judge_full("s", "u")
def never_called():
    rr.load_env()
if __name__ == "__main__":
    main()
''', "REFUSED", 1, 0),
    "e_pass_alias": ('''
from rejudge_reasoning import load_env as le, call_judge_full as cjf
def main():
    le()
    cjf("s", "u")
if __name__ == "__main__":
    main()
''', "PASS", 1, 1),
    "e_refuse_reference_only": ('''
import rejudge_reasoning as rr
def main():
    f = rr.load_env
    return rr.call_judge_full("s", "u"), f
if __name__ == "__main__":
    main()
''', "REFUSED", 1, 0),
    "e_pass_reexport": ('''
def main():
    from pkg import transport as T
    from pkg._base import rr
    T.load_transport()
    rr.call_judge_full("s", "u")
if __name__ == "__main__":
    main()
''', "PASS", 1, 1),
    "e_refuse_noposting": ('''
import rejudge_reasoning as rr
def main():
    rr.load_env()
if __name__ == "__main__":
    main()
''', "REFUSED", 0, 1),
    "e_pass_method": ('''
import rejudge_reasoning as rr
class Poster:
    def go(self):
        self.prep()
        return rr.call_judge_full("s", "u")
    def prep(self):
        rr.load_env()
def main():
    Poster().go()
if __name__ == "__main__":
    main()
''', "PASS", 1, 1),
    "e_refuse_foreign_main": ('''
import rejudge_reasoning as rr
import foreign
def main():
    foreign.nothing()
    return rr.call_judge_full("s", "u")
if __name__ == "__main__":
    main()
''', "REFUSED", 1, 0),
}

DRY_GOOD = r'''
import os, sys
from urllib.parse import urlparse
root = os.environ["%s"]
kv = dict(l.strip().split("=", 1) for l in open(os.path.join(root, ".env")) if "=" in l)
ep, key = kv.get("AZURE_AI_ENDPOINT"), kv.get("AZURE_GROK_API_KEY")
if not ep or not key:
    raise SystemExit("[X] TRANSPORT PREFLIGHT: REFUSED before any post: key is None")
print("TRANSPORT PREFLIGHT: OK (endpoint host=%%s, deployment=grok)" %% urlparse(ep).hostname)
print("[DRY-RUN] 0 posted")
'''
DRY_HARDCODED = r'''
print("TRANSPORT PREFLIGHT: OK (endpoint host=transport-check.invalid, deployment=grok)")
print("[DRY-RUN] 0 posted")
'''
DRY_ABSENT = r'''
print("[DRY-RUN] 0 posted (no preflight)")
'''
DRY_NET = r'''
import os, socket
from urllib.parse import urlparse
root = os.environ["%s"]
kv = dict(l.strip().split("=", 1) for l in open(os.path.join(root, ".env")) if "=" in l)
if not kv.get("AZURE_GROK_API_KEY"):
    raise SystemExit("TRANSPORT PREFLIGHT: REFUSED: key is None")
try:
    socket.create_connection(("127.0.0.1", 9), timeout=1)
except OSError:
    pass
print("TRANSPORT PREFLIGHT: OK (endpoint host=%%s, deployment=grok)" %% urlparse(kv["AZURE_AI_ENDPOINT"]).hostname)
'''
READY_GOOD = ("# READY\n- transport configuration (zero-call): load_env sites 1; the dry-run preflight line printed\n"
              "- provider behaviour (pilot): left to the pilot 12\n")
READY_SAME = "# READY\n- transport configuration (zero-call) and provider behaviour (pilot) were both checked\n"
READY_MISSING = "# READY\n- transport configuration (zero-call): checked\n"


def selftest():
    fails = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        print("  [%s] %s%s" % ("OK" if ok else "FAIL", name, "" if ok else "  -> " + str(detail)[:300]), flush=True)
        if not ok:
            fails.append(name)

    print("[SELFTEST] transport_check.py | mutant %s | 0 calls; tempfile fixtures only" % (MUTANT or "none"), flush=True)
    tmp = tempfile.mkdtemp(prefix="transport_check_selftest_")
    try:
        base = os.path.join(tmp, ANALYSIS_REL)
        os.makedirs(os.path.join(base, "pkg"))
        for rel, src in (("rejudge_reasoning.py", FIX_RR), ("helper.py", FIX_HELPER), ("pkg/__init__.py", FIX_PKG_INIT),
                         ("pkg/_base.py", FIX_PKG_BASE), ("pkg/transport.py", FIX_PKG_TR), ("foreign.py", FIX_FOREIGN)):
            open(os.path.join(base, rel), "w", encoding="utf-8").write(src)
        for name, (src, *_rest) in ENTRIES.items():
            open(os.path.join(base, name + ".py"), "w", encoding="utf-8").write(src)
        tree = Tree(tmp)
        for name, (src, want, n_post, n_load) in ENTRIES.items():
            res = analyse(tree, "%s/%s.py" % (ANALYSIS_REL, name))
            check("(a) %-26s -> %s, posting refs %d, load_env call sites %d" % (name, want, n_post, n_load),
                  res["verdict"] == want and len(res["posts"]) == n_post and len(res["loaders"]) == n_load,
                  (res["verdict"], len(res["posts"]), len(res["loaders"]), res["loaders"]))
        # (b) executed: four fixture dry-runs
        ev = "TRANSPORT_CHECK_FIXTURE_ROOT"
        for name, src, want in (("dry_good", DRY_GOOD % ev, "PASS"), ("dry_hardcoded", DRY_HARDCODED, "REFUSED"),
                                ("dry_absent", DRY_ABSENT, "REFUSED"), ("dry_net", DRY_NET % ev, "REFUSED")):
            p = os.path.join(tmp, name + ".py")
            open(p, "w", encoding="utf-8").write(src)
            r = executed_check([sys.executable, p], env_var=ev, cwd=tmp)
            check("(b) %-14s -> %s" % (name, want), r["verdict"] == want, r["line"])
        # (c) lint
        for name, txt, want in (("ready_good", READY_GOOD, "PASS"), ("ready_same_line", READY_SAME, "REFUSED"),
                                ("ready_missing", READY_MISSING, "REFUSED")):
            r = ready_check(txt)
            check("(c) %-15s -> %s" % (name, want), r["verdict"] == want, r["line"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("[SELFTEST] %s" % ("%d check(s) FAILED: %s" % (len(fails), fails) if fails else "all checks passed"), flush=True)
    return 1 if fails else 0


def mutants():
    rows = []
    for m in MUTANTS:
        env = dict(os.environ, TRANSPORT_CHECK_MUTANT=m, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--selftest"], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        failed = [l.strip() for l in p.stdout.split("\n") if l.strip().startswith("[FAIL]")]
        rows.append((m, "KILLED" if p.returncode != 0 and failed else "SURVIVED", failed[0][7:90] if failed else "-"))
    base = subprocess.run([sys.executable, os.path.abspath(__file__), "--selftest"], capture_output=True, text=True,
                          env=dict(os.environ, PYTHONIOENCODING="utf-8"), encoding="utf-8", errors="replace")
    print("MUTANT TABLE (baseline selftest rc %d):" % base.returncode)
    for m, st, first in rows:
        print("  %-16s %-9s first failing check: %s" % (m, st, first))
    killed = sum(1 for r in rows if r[1] == "KILLED")
    print("KILLED %d of %d" % (killed, len(rows)))
    return 0 if killed == len(rows) and base.returncode == 0 else 1


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="the posting entry script, repo-relative (tools/analysis/<x>.py)")
    ap.add_argument("--rev", default=None, help="a git revision (default: the working tree)")
    ap.add_argument("--dry-run-cmd", default=None, help="(b) the dry-run command line to execute twice")
    ap.add_argument("--env-var", default="TAXOARENA_DATA_ROOT", help="(b) the variable naming the root whose .env is read")
    ap.add_argument("--ready", default=None, help="(c) a READY markdown file")
    ap.add_argument("--acceptance", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return mutants()
    if a.acceptance:
        return acceptance()
    rc = 0
    if a.script:
        rel = a.script.replace("\\", "/")
        res = analyse(Tree(ROOT, a.rev), rel)
        print(static_line(res, rel, a.rev))
        for w in res["loaders"]:
            print("    load_env call site: %s" % w)
        for w in res["posts"]:
            print("    posting reference:  %s" % w)
        rc |= res["verdict"] != "PASS"
    if a.dry_run_cmd:
        r = executed_check(a.dry_run_cmd, env_var=a.env_var)
        print(r["line"])
        rc |= r["verdict"] != "PASS"
    if a.ready:
        r = ready_check(open(a.ready, encoding="utf-8").read())
        print(r["line"])
        rc |= r["verdict"] != "PASS"
    if not (a.script or a.dry_run_cmd or a.ready):
        ap.error("nothing to check: give --script, --dry-run-cmd, --ready, --acceptance, --selftest or --mutants")
    print("TRANSPORT CHECK: %s" % ("PASS" if rc == 0 else "REFUSED"))
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main())
