"""judge_v2._base: paths, the pins of every recipe component E-J builds on, and the shared imports of record.

PINS (hash kinds named, CONTEXT rule 8; the LF rendering is the rendering of record):
  E-D data layer AS ON MAIN (d98b247; re-pinned 2026-09-24 on READY_archv2_EJ C1: the DEV copies of 5618b78 are no
  longer carried; judge_v2 is merged by path against main's tools/analysis/data_v2) (blob = git blob of the LF bytes,
  each checked against `git rev-parse main:tools/analysis/data_v2/<f>`):
    data_v2/ro.py        blob:1fdf7d75222f803a4cffc41d0baf05a908a7dd69   (unchanged from 5618b78)
    data_v2/views.py     blob:7a0f0ab31a09e02fcc54db6b8ce26d99284b1603   [re-pinned 2026-09-24 to main 5b89159 for the SPLIT-2
                         views (CK-CLOSE-v2): build_view leaves U-excluded items out; the openers unchanged; was fe75c7c8]
    data_v2/verdicts.py  blob:1013804233b7ccfc0df699acdcaf518b089ad526   (the no-rekey triggers: REPLACE refused)
    data_v2/common.py    blob:462ffef3b839624685cfea7b8abd3181d7b5a8c7   [re-pinned 2026-09-24 to main 5b89159: loads the pinned
                         passage_closure.py at import; was 1e140335]
    data_v2/__init__.py  blob:225c4c496c4c57963436114a9e004093933f89aa   (unchanged)
    data_v2/ingest.py    blob:fd76b4392a0eafa7ee551bc267b9f2495453595f   (SOLVER_MODEL, read by the loader)
  the ONE body builder and the call of record (CONTEXT rule 9):
    rejudge_reasoning.py blob:1339592ae5205d6d93cdb1f38b8936b819e24d87   (payload_body / payload_bytes / call_judge_full)
  the v2 verify-first system template (derived at runtime from TaxonomyArenaService.kt's v1 template):
    prompt_v2.py         blob:52b369657f968b5dde2540fc405ac7f4720ed94c
  the template STRINGS as posted (sha256 of the UTF-8 bytes; the .kt file itself changes for unrelated reasons, so the
  extracted text is pinned, not the file):
    TEMPLATE_SHAS below: v2 system template, user template, schema instruction, reference marker, and the FIXED
    $systemPrompt persona (rubric_value_contrast.GENERIC_SYSTEM; ruling 4aac08e: the induced artefact fills the rubric
    slot only).
  rejudge_grok.combine_orders and rejudge_grok.parse_judge: sha256 of ast.dump(FunctionDef) (combiner.py / writer.py).
A different blob or sha is REFUSED at import (raise SystemExit): a new version needs a new pin and a review, never a
silent pickup.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ANALYSIS))
if ANALYSIS not in sys.path:
    sys.path.insert(0, ANALYSIS)


def refuse(msg):
    raise SystemExit("[JUDGE-V2] " + msg)


def git_blob_lf(path):
    with open(path, "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256_lf16(path):
    with open(path, "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:16]


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


ED_PINS = {
    "data_v2/ro.py": "1fdf7d75222f803a4cffc41d0baf05a908a7dd69",
    "data_v2/views.py": "7a0f0ab31a09e02fcc54db6b8ce26d99284b1603",
    "data_v2/verdicts.py": "1013804233b7ccfc0df699acdcaf518b089ad526",
    "data_v2/common.py": "462ffef3b839624685cfea7b8abd3181d7b5a8c7",
    "data_v2/__init__.py": "225c4c496c4c57963436114a9e004093933f89aa",
    "data_v2/ingest.py": "fd76b4392a0eafa7ee551bc267b9f2495453595f",
}
MODULE_PINS = {
    "rejudge_reasoning.py": "1339592ae5205d6d93cdb1f38b8936b819e24d87",
    "prompt_v2.py": "52b369657f968b5dde2540fc405ac7f4720ed94c",
}


def _check_pins():
    for rel, pin in list(ED_PINS.items()) + list(MODULE_PINS.items()):
        path = os.path.join(ANALYSIS, *rel.split("/"))
        if not os.path.isfile(path):
            refuse("%s is missing (E-J builds on it; pinned blob:%s)" % (path, pin))
        got = git_blob_lf(path)
        if got != pin:
            refuse("%s is blob:%s, not the pinned blob:%s; a new version needs a new pin in judge_v2/_base.py" % (rel, got, pin))


_check_pins()

import rejudge_grok as rj  # noqa: E402
import rejudge_reasoning as rr  # noqa: E402
import prompt_v2  # noqa: E402
import rubric_value_contrast as rvc  # noqa: E402
from data_v2 import common as dv2c  # noqa: E402
from data_v2 import ingest as dv2ingest  # noqa: E402
from data_v2 import ro as dv2ro  # noqa: E402
from data_v2 import verdicts as dv2verdicts  # noqa: E402
from data_v2 import views as dv2views  # noqa: E402

for _m, _rel in ((rr, "rejudge_reasoning.py"), (prompt_v2, "prompt_v2.py"), (dv2verdicts, "data_v2/verdicts.py"),
                 (dv2views, "data_v2/views.py"), (dv2ro, "data_v2/ro.py"), (dv2c, "data_v2/common.py"),
                 (dv2ingest, "data_v2/ingest.py")):
    _want = os.path.normcase(os.path.join(ANALYSIS, *_rel.split("/")))
    if os.path.normcase(os.path.abspath(_m.__file__)) != _want:
        refuse("module %s was imported from %s, not the pinned %s" % (_m.__name__, _m.__file__, _want))

V2_SYSTEM_TEMPLATE = prompt_v2.v2_system_template()
USER_TEMPLATE = rj.USER_TEMPLATE
SCHEMA_INSTRUCTION = rj.SCHEMA_INSTRUCTION
REFERENCE_MARKER = "[Reference solution — produced independently, may be wrong]"
# The FIXED text of the template's $systemPrompt (persona) slot. Registrar ruling 2026-09-24 on E-J choice 2 (programme
# L15159-L15177, 4aac08e): the induced artefact fills the RUBRIC slot ONLY; the system prompt stays fixed. The fixed text
# is the de-induced persona of record: rubric_value_contrast.GENERIC_SYSTEM (TaxonomyArenaService's GENERIC_JUDGE branch),
# IMPORTED, never retyped, exactly as STACK-NORUBRIC fills $systemPrompt (plan Amendment 1 D3). The mechanics (verify-first,
# the reference block, the confidence field, no length instruction) are the v2 template itself (prompt_v2), unchanged.
FIXED_SYSTEM_PERSONA = rvc.GENERIC_SYSTEM

TEMPLATE_SHAS = {
    "v2_system_template": "0d064ee28dd10f6c65ac3a59e62d1d4896e74c54abcac81c812eccd79f6b62f5",
    "user_template": "4c142bc1da0edd75b80b744f453b93c067af35e573c0291a7c679902c9ca01ee",
    "schema_instruction": "708a6cb3e3d5e647d67ec7975209eea216b34cf8924f98cfdaf2fa0ce2dc775f",
    "reference_marker": "977ceb714172552445ec117289bbd9dfe78f372edfd770ae90071e9b35607661",
    "fixed_system_persona": "3a5e223c26f32c8e68a1a40b05f1fc9e63a36434eb9613830f5641c06253ddb9",
}
_got = {"v2_system_template": sha256_text(V2_SYSTEM_TEMPLATE), "user_template": sha256_text(USER_TEMPLATE),
        "schema_instruction": sha256_text(SCHEMA_INSTRUCTION), "reference_marker": sha256_text(REFERENCE_MARKER),
        "fixed_system_persona": sha256_text(FIXED_SYSTEM_PERSONA)}
for _k, _v in TEMPLATE_SHAS.items():
    if _got[_k] != _v:
        refuse("template %s is sha256:%s, not the pinned sha256:%s (a prompt change is never a side effect)" % (_k, _got[_k], _v))

# the reference marker of record must be the one rejudge_reference.with_reference renders (checked on the source text,
# so rejudge_reference is not imported: it opens caches in its helpers)
_rref_src = open(os.path.join(ANALYSIS, "rejudge_reference.py"), encoding="utf-8").read()
if REFERENCE_MARKER not in _rref_src:
    refuse("rejudge_reference.py no longer carries the reference marker of record %r" % REFERENCE_MARKER)


def pin_table():
    """Every pin E-J checks, for the run manifest (hash kinds named)."""
    t = {rel: "blob:" + pin for rel, pin in ED_PINS.items()}
    t.update({rel: "blob:" + pin for rel, pin in MODULE_PINS.items()})
    t.update({k: "sha256:" + v for k, v in TEMPLATE_SHAS.items()})
    for name in ("_base.py", "payload.py", "leakage.py", "combiner.py", "writer.py", "induction.py", "loader.py"):
        p = os.path.join(HERE, name)
        if os.path.isfile(p):
            t["judge_v2/" + name] = "blob:" + git_blob_lf(p)
    return t
