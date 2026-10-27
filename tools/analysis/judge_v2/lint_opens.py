"""judge_v2.lint_opens: REFUSE any opening of a data_v2 corpus / view / verdict DB outside tools/analysis/data_v2/ that does
not go through the stage-gated openers, and any use of the loader's signing outside loader.py (READY_archv2_EJ C4; the
delta review 16212c4 D4). Changes nothing; exit 1 on any finding.

    python tools/analysis/judge_v2/lint_opens.py [--root <repo root>]

RULES (every .py under tools/, data_v2/ itself excluded):
  R1  any REFERENCE (a call, an attribute read, an assignment, an import by name) to data_v2.ro's openers (open_ro,
      open_run_writer, create_new, open_scratch_rw, seal): through a name bound to data_v2.ro (`from data_v2 import ro
      [as X]`, `import data_v2.ro as X`, judge_v2's re-export `dv2ro`), through the dotted chain `data_v2.ro.<opener>`, or
      imported by name (`from data_v2.ro import open_ro`). Reading a corpus_v2 / gen_view / eval_view file that way
      bypasses open_generation / open_eval.
  R2  a FILE that calls connect(...) anywhere and names a corpus_v2 / gen_view / eval_view ".db" file anywhere (the path may
      be set on another line than the connect; one finding per file, at its first connect).
  R3  any reference to the loader's signing (sign, _sign, _sign_for_selftest, _SECRET) outside judge_v2/loader.py:
      through a name bound to judge_v2.loader, the dotted chain `judge_v2.loader.<name>`, or an import by name.
  ALLOWLIST (file, function, rule) with the reason, printed on every run:
      judge_v2/writer.py match_verdicts R1   reads a v2 VERDICT run DB read-only (schema_id checked), never a corpus or view
      judge_v2/writer.py mixed_strata R1     reads run_meta of a v2 VERDICT run DB read-only (the D5 readout hook)
      judge_v2/induce_run_selftest.py * R1  reads its own scratch DBs under tempfile.gettempdir()
      judge_v2/selftest.py * R1             reads its own scratch DBs under tempfile.gettempdir()
      judge_v2/selftest.py * R3 (_sign_for_selftest only)   the one test hook; it refuses any caller but the selftest
      judge_v2/selftest.py s6_loader R3 (sign only)          the check that the public name loader.sign refuses
  archv2_arena's own ro.open_ro (pool_guard's) is NOT data_v2.ro and is not matched by R1 (its name is not bound to
  data_v2.ro); R2 still applies to every file.
[WIDENED 2026-09-24 on the delta review 16212c4 D4: R1 now covers dotted chains and any reference, not only calls; R2 is
file-level; R3 is new. The reviewer's four bypasses (scratchpad/lintroot) each give one finding.]
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OPENERS = {"open_ro", "open_run_writer", "create_new", "open_scratch_rw", "seal"}
SIGN_NAMES = {"sign", "_sign", "_sign_for_selftest", "_SECRET"}
ALLOW = {("judge_v2/writer.py", "match_verdicts", "R1"): "reads a v2 verdict run DB read-only (schema_id checked)",
         ("judge_v2/writer.py", "mixed_strata", "R1"): "reads run_meta of a v2 verdict run DB read-only (D5 readout)",
         ("judge_v2/induce_run_selftest.py", "*", "R1"): "reads its own scratch DBs under tempfile.gettempdir()",
         ("judge_v2/selftest.py", "*", "R1"): "reads its own scratch DBs under tempfile.gettempdir()",
         ("judge_v2/selftest.py", "*", "R3:_sign_for_selftest"): "the one test hook (refuses any other caller)",
         ("judge_v2/selftest.py", "s6_loader", "R3:sign"): "asserts that the public name loader.sign REFUSES (probe H1)"}
DBNAME = re.compile(r"(corpus_v2|gen_view|eval_view)\w*\.db")


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _bindings(tree, rel):
    ro_names, loader_names = {"dv2ro"}, set()
    ro_funcs, sign_funcs = {}, {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            mod = (n.module or "").lstrip(".")
            in_judge = rel.startswith("judge_v2/") and n.level > 0 and mod == ""
            for a in n.names:
                name = a.asname or a.name
                if a.name == "ro" and (mod.endswith("data_v2") or mod == "data_v2"):
                    ro_names.add(name)
                if a.name == "loader" and (mod.endswith("judge_v2") or in_judge):
                    loader_names.add(name)
                if a.name in OPENERS and mod.endswith("data_v2.ro"):
                    ro_funcs[name] = n.lineno
                if a.name in SIGN_NAMES and (mod.endswith("judge_v2.loader") or (rel.startswith("judge_v2/") and n.level > 0
                                                                                    and mod == "loader")):
                    sign_funcs[name] = (n.lineno, a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name.endswith("data_v2.ro") and a.asname:
                    ro_names.add(a.asname)
                if a.name.endswith("judge_v2.loader") and a.asname:
                    loader_names.add(a.asname)
    return ro_names, loader_names, ro_funcs, sign_funcs


def _enclosing(tree):
    owner = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in ast.walk(fn):
                owner.setdefault(id(n), fn.name)
    return owner


def _allowed(rel, fn, rule):
    return ALLOW.get((rel, fn, rule)) or ALLOW.get((rel, "*", rule))


def scan_file(p, rel):
    """-> (findings, allowed) of one file."""
    findings, allowed = [], []
    text = open(p, encoding="utf-8", errors="replace").read()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [(rel, 0, "R0", "does not parse")], []
    ro_names, loader_names, ro_funcs, sign_funcs = _bindings(tree, rel)
    owner = _enclosing(tree)

    def emit(node_or_line, rule, msg, allow_rule=None):
        line = node_or_line if isinstance(node_or_line, int) else node_or_line.lineno
        fn = owner.get(id(node_or_line), "<module>") if not isinstance(node_or_line, int) else "<module>"
        why = _allowed(rel, fn, allow_rule or rule)
        (allowed if why else findings).append((rel, line, rule, "%s in %s%s" % (msg, fn, (": " + why) if why else "")))

    for name, line in ro_funcs.items():
        emit(line, "R1", "import of data_v2.ro.%s by name" % name)
    is_loader = rel == "judge_v2/loader.py"
    if not is_loader:
        for name, (line, orig) in sign_funcs.items():
            emit(line, "R3", "import of judge_v2.loader.%s by name" % orig, "R3:" + orig)
    connects = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute):
            d = _dotted(n.value)
            if d is None:
                continue
            if n.attr in OPENERS and (d in ro_names or d == "data_v2.ro" or d.endswith(".data_v2.ro")):
                emit(n, "R1", "%s.%s" % (d, n.attr))
            if not is_loader and n.attr in SIGN_NAMES and (d in loader_names or d == "judge_v2.loader" or
                                                          d.endswith(".judge_v2.loader")):
                emit(n, "R3", "%s.%s" % (d, n.attr), "R3:" + n.attr)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            if n.id in ro_funcs:
                emit(n, "R1", "reference to %s (data_v2.ro)" % n.id)
            if not is_loader and n.id in sign_funcs:
                emit(n, "R3", "reference to %s (judge_v2.loader)" % n.id, "R3:" + sign_funcs[n.id][1])
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Attribute) and f.attr == "connect") or (isinstance(f, ast.Name) and f.id == "connect"):
                connects.append(n)
    if connects and DBNAME.search(text):
        first = min(connects, key=lambda c: c.lineno)
        emit(first, "R2", "connect(...) in a file naming a corpus_v2 / view .db (%s)" % DBNAME.search(text).group(0))
    return findings, allowed


def scan(root=ROOT):
    tools = os.path.join(root, "tools")
    dv2 = os.path.normcase(os.path.join(tools, "analysis", "data_v2")) + os.sep
    findings, allowed, files = [], [], 0
    for d, _dirs, fs in os.walk(tools):
        if "__pycache__" in d or os.path.normcase(d + os.sep).startswith(dv2):
            continue
        for f in sorted(fs):
            if not f.endswith(".py"):
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, os.path.join(tools, "analysis")).replace(os.sep, "/")
            files += 1
            fd, al = scan_file(p, rel)
            findings.extend(fd)
            allowed.extend(al)
    return files, findings, allowed


def main(argv):
    root = argv[argv.index("--root") + 1] if "--root" in argv else ROOT
    files, findings, allowed = scan(root)
    print("[LINT-OPENS] %d .py files under tools/ (data_v2/ excluded); %d finding(s); %d allowlisted reference(s)"
          % (files, len(findings), len(allowed)))
    for rel, ln, rule, msg in allowed:
        print("  ALLOWED %s:%d %s %s" % (rel, ln, rule, msg))
    for rel, ln, rule, msg in findings:
        print("  REFUSED %s:%d %s %s" % (rel, ln, rule, msg))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
