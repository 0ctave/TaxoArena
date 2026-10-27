# Emits judge_example.tex: one leaf's complete induced judge, plus the two user
# templates and the generic system prompt, reproduced verbatim from the sources
# rather than transcribed.
#
# WHY GENERATED. The prompts are the thesis's experimental treatment. A
# hand-copied prompt in the appendix can drift from the one the runs used, and
# nothing would catch it. This script reads the rubric from the frozen snapshot
# and the templates from the Kotlin sources, so the appendix is checkable
# against the artefacts and fails loudly if either moves.
#
# Sources:
#   snapshots.db, snapshot 20260727_042523_Headless_Run_Auto_ge (read-only)
#       node n00000066 "Geometric Optics of Thin and Thick Lenses" -- chosen
#       because its rubric length (2,909 chars) is close to the 87-leaf median
#       (2,670) and its domain needs no specialist knowledge to follow.
#   src/main/kotlin/taxonomy/prompts/GenericPairwiseJudgePrompt.kt
#   src/main/kotlin/taxonomy/service/TaxonomyArenaService.kt
#
# Two transformations are applied and both are declared in the output:
#   - U+2019 in the stored rubric is rendered as an ASCII
#     apostrophe, so the emitted fragment is encoding-independent.
#   - The box-drawing rule in the rubric-arm user template is rendered as ASCII
#     hyphens; T1-encoded pdfLaTeX has no glyph for U+2500.
#
# Run from anywhere:  python report/Figures/make_judge_example.py
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "judge_example.tex")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
if not os.path.exists(SNAP_DB):  # clone without the full local store
    SNAP_DB = os.path.join(ROOT, "snapshots_frozen.db")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
LEAF = "n00000066"
LEAF_LABEL = "Geometric Optics of Thin and Thick Lenses"

GEN_KT = os.path.join(ROOT, "src/main/kotlin/taxonomy/prompts/GenericPairwiseJudgePrompt.kt")
ARENA_KT = os.path.join(ROOT, "src/main/kotlin/taxonomy/service/TaxonomyArenaService.kt")

# ---- read the induced judge from the frozen snapshot --------------------
db = sqlite3.connect("file:%s?mode=ro" % SNAP_DB.replace(os.sep, "/"), uri=True)
row = db.execute("select graph from snapshots where id = ?", (SNAP_ID,)).fetchone()
if row is None:
    raise SystemExit("snapshot %s not found" % SNAP_ID)
nodes = {n["id"]: n for n in json.loads(row[0])["nodes"]}
db.close()

if LEAF not in nodes:
    raise SystemExit("leaf %s not in snapshot" % LEAF)
leaf = nodes[LEAF]
if leaf["label"] != LEAF_LABEL:
    raise SystemExit("leaf %s is %r, expected %r" % (LEAF, leaf["label"], LEAF_LABEL))
sys_prompt = leaf.get("judgePrompt") or ""
rubric = leaf.get("judgeRubric") or ""
if not sys_prompt or not rubric:
    raise SystemExit("leaf %s carries no judge prompt/rubric" % LEAF)

# ---- read the templates from the Kotlin sources -------------------------
gen_src = open(GEN_KT, encoding="utf8", errors="replace").read()
m = re.search(r'const val SYSTEM_PROMPT = """(.*?)"""', gen_src, re.S)
if not m:
    raise SystemExit("SYSTEM_PROMPT not found in %s" % GEN_KT)
gen_system = m.group(1)
m = re.search(r'const val USER_TEMPLATE = """(.*?)"""', gen_src, re.S)
if not m:
    raise SystemExit("USER_TEMPLATE not found in %s" % GEN_KT)
gen_user = m.group(1)

arena_src = open(ARENA_KT, encoding="utf8", errors="replace").read()
m = re.search(r'private fun buildJudgeUserPrompt\([^)]*\): String \{\s*return """(.*?)"""',
              arena_src, re.S)
if not m:
    raise SystemExit("buildJudgeUserPrompt template not found in %s" % ARENA_KT)
main_user = m.group(1)

# ---- normalise -----------------------------------------------------------
# The stored rubric uses typographic punctuation (U+2019). Map it to ASCII so
# the fragment is encoding-independent; assert it is there, so a change in how
# rubrics are stored fails here rather than silently altering the reproduction.
had_curly = chr(0x2019) in rubric
rubric = rubric.replace(chr(0x2019), "'")
had_rule = chr(0x2500) in main_user
main_user = re.sub(chr(0x2500) + "+", "-" * 40, main_user)
main_user = main_user.replace(chr(0x2264), "<=").replace(chr(0x2014), "--")

if not had_curly:
    raise SystemExit("expected U+2019 in the stored rubric; the data changed")
if not had_rule:
    raise SystemExit("expected a box-drawing rule in the user template")


def esc(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"),
                 ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}"),
                 # The document loads German babel, which makes '"' an active
                 # character: an unescaped '"M' in the JSON schema came out as
                 # 'MM'. '<' and '>' have no glyph in the typewriter font and
                 # rendered as guillemets.
                 ('"', r"\textquotedbl{}"), ("<", r"\textless{}"),
                 (">", r"\textgreater{}")):
        s = s.replace(a, b)
    return s


def block(text, mono=False):
    """A quote block. Blank lines become paragraph breaks; mono keeps line breaks."""
    out = [r"\begin{quote}\small" + (r"\ttfamily" if mono else "")]
    if mono:
        lines = [esc(l) if l.strip() else "" for l in text.split("\n")]
        # A line starting with "[" would be swallowed as the optional length
        # argument of the preceding "\\". Brace it.
        lines = ["{}" + l if l.startswith("[") else l for l in lines]
        out.append(" \\\\\n".join(l if l else "~" for l in lines))
    else:
        for para in [p for p in text.split("\n") if p.strip()]:
            out.append(esc(para) + r"\par")
    out.append(r"\end{quote}")
    return "\n".join(out)


L = []
L.append("% GENERATED by report/Figures/make_judge_example.py -- do not edit.")
L.append("%% Leaf %s (%s) of snapshot %s." % (LEAF, LEAF_LABEL, SNAP_ID))

L.append(r"\subsection{The Induced System Prompt}\label{sec:judge-example-system}")
L.append("")
L.append(r"Leaf \texttt{%s}, \emph{%s}. This half is generated once at "
         r"snapshot-freeze time and is what the rubric arm sends as the judge's "
         r"system prompt. It names the domain, its formalism and its failure "
         r"modes; it says nothing about how to compare two responses."
         % (LEAF, esc(LEAF_LABEL)))
L.append("")
L.append(block(sys_prompt))

L.append(r"\subsection{The Induced Rubric}\label{sec:judge-example-rubric}")
L.append("")
L.append(r"The rubric for the same leaf, reproduced in full. Its criteria are "
         r"domain conditions --- sign conventions, unit consistency, physical "
         r"plausibility --- and none of them is a comparison instruction, a tie "
         r"rule, or an output format. That separation is the control described "
         r"in Section~\ref{sec:judge-template-full}.")
L.append("")
L.append(block(rubric))

L.append(r"\subsection{The Two User Messages}\label{sec:judge-example-user}")
L.append("")
L.append(r"The rubric arm's user message, from "
         r"\texttt{TaxonomyArenaService.buildJudgeUserPrompt}. The horizontal "
         r"rule is a box-drawing character in the source and is shown here as "
         r"hyphens.")
L.append("")
L.append(block(main_user, mono=True))
L.append("")
L.append(r"The generic arm's user message, from "
         r"\texttt{GenericPairwiseJudgePrompt.USER\_TEMPLATE}, is the MT-Bench "
         r"pairwise template unchanged.")
L.append("")
L.append(block(gen_user, mono=True))
L.append("")
L.append(r"Its system prompt is likewise the MT-Bench text verbatim.")
L.append("")
L.append(block(gen_system))

open(OUT, "w", encoding="utf8").write("\n".join(L) + "\n")
print("wrote %s" % OUT)
print("  leaf %s, system prompt %d chars, rubric %d chars"
      % (LEAF, len(sys_prompt), len(rubric)))
print("  templates read from source: main %d chars, generic %d + %d chars"
      % (len(main_user), len(gen_user), len(gen_system)))
