"""judge_v2.combiner: the dual-order MATCH VERDICT from two POSITIONAL votes (judge proposal §2.3; E-D ruling 9).

Frame: each call's vote is POSITIONAL (data_v2.verdicts.VOTES: FIRST, SECOND, TIE, INVALID, NON_TERMINATED,
CONTENT_FILTER). Order 1 shows contestant A first; order 2 shows B first. The contestant-frame vote is DERIVED:
  order 1: FIRST -> A, SECOND -> B;  order 2: FIRST -> B, SECOND -> A;  every other class passes through unchanged.
combine(pos1, pos2) -> (winner, flip, invalid):
  CONTENT_FILTER if either order is CONTENT_FILTER; else NON_TERMINATED if either is NON_TERMINATED  (their own classes,
  in this precedence, never TIE and never INVALID: the extension of rejudge_grok.combine_orders the proposal names);
  else INVALID if either is INVALID; else TIE when the two contestant-frame votes differ (a FLIP); else the common vote.
  flip   = both contestant-frame votes in {A, B, TIE} and different (data_v2 match_verdict's `flip`);
  invalid = the winner is INVALID (rejudge_grok's `invalid`; NON_TERMINATED / CONTENT_FILTER are NOT folded into it).
This is the same rule and precedence as data_v2.verdicts' match_verdict VIEW (the schema's default reading); the COMBINER
OF RECORD is this function, pinned by blob in the run manifest (combiner_blob).

THE FLIP LEG IS rejudge_grok.combine_orders. On the domain both rules share (each order in FIRST / SECOND / TIE /
INVALID), combine() equals combine_orders(to_rj_raw(pos1), to_rj_raw(pos2)) with winners mapped Model A -> A, Model B -> B:
  TABLE: rj_equivalence_table() evaluates all 16 cases through BOTH functions (the selftest requires 16 / 16 equal);
  AST:   RJ_COMBINE_AST_SHAS pins sha256(ast.dump(rejudge_grok.combine_orders)); a changed function REFUSES the
         equivalence claim (rj_ast_sha() is checked by the selftest and by the writer at start).
to_rj_raw maps a positional vote to the judge's own label in its presentation ("Model A" = shown first), which is what
rejudge_grok's caches store as vote1 / vote2_raw; combine_orders inverts order 2 itself.
"""
import ast
import hashlib
import inspect
import textwrap

from ._base import refuse, rj

POSITIONAL = ("FIRST", "SECOND", "TIE", "INVALID", "NON_TERMINATED", "CONTENT_FILTER")
SHARED_DOMAIN = ("FIRST", "SECOND", "TIE", "INVALID")
WINNERS = ("A", "B", "TIE", "INVALID", "NON_TERMINATED", "CONTENT_FILTER")
COMBINER_VERSION = "jv2-combine-1"
# ast.dump is interpreter-version dependent: the pin is per CPython minor version (pinned under 3.11.1)
RJ_COMBINE_AST_SHAS = {(3, 11): "63c38ee4ee02aa5a0a28280c0b6708dfde1a571c87cf64ae02b9f7482e3ba325"}


def to_contestant(vote, order):
    if vote not in POSITIONAL:
        refuse("positional vote %r is not one of %s" % (vote, POSITIONAL))
    if order == 1:
        return {"FIRST": "A", "SECOND": "B"}.get(vote, vote)
    if order == 2:
        return {"FIRST": "B", "SECOND": "A"}.get(vote, vote)
    refuse("order %r is not 1 or 2" % (order,))


def combine(pos1, pos2):
    c1, c2 = to_contestant(pos1, 1), to_contestant(pos2, 2)
    if "CONTENT_FILTER" in (c1, c2):
        return "CONTENT_FILTER", False, False
    if "NON_TERMINATED" in (c1, c2):
        return "NON_TERMINATED", False, False
    if "INVALID" in (c1, c2):
        return "INVALID", False, True
    if c1 != c2:
        return "TIE", True, False
    return c1, False, False


def to_rj_raw(vote):
    """The judge's own label in its presentation, as rejudge_grok stores it (vote1 / vote2_raw)."""
    m = {"FIRST": "Model A", "SECOND": "Model B", "TIE": "TIE", "INVALID": "INVALID"}
    if vote not in m:
        refuse("to_rj_raw: %r is outside the shared domain %s" % (vote, SHARED_DOMAIN))
    return m[vote]


_RJ_WINNER = {"Model A": "A", "Model B": "B", "TIE": "TIE", "INVALID": "INVALID"}


def rj_equivalence_table():
    """[(pos1, pos2, ours, theirs, equal)] over the 16 shared-domain cases, each evaluated through BOTH functions."""
    rows = []
    for p1 in SHARED_DOMAIN:
        for p2 in SHARED_DOMAIN:
            ours = combine(p1, p2)
            w, flip, inv = rj.combine_orders(to_rj_raw(p1), to_rj_raw(p2))
            theirs = (_RJ_WINNER.get(w, "?" + str(w)), bool(flip), bool(inv))
            rows.append((p1, p2, ours, theirs, bool(ours == theirs)))
    return rows


def rj_ast_sha():
    src = textwrap.dedent(inspect.getsource(rj.combine_orders))
    fn = ast.parse(src).body[0]
    return hashlib.sha256(ast.dump(fn, annotate_fields=True, include_attributes=False).encode("utf-8")).hexdigest()


def check_rj_pin():
    import sys
    pin = RJ_COMBINE_AST_SHAS.get(tuple(sys.version_info[:2]))
    if pin is None:
        refuse("no rejudge_grok.combine_orders AST pin for Python %d.%d (ast.dump differs across versions): run the table"
               " test and add a pin" % tuple(sys.version_info[:2]))
    got = rj_ast_sha()
    if got != pin:
        refuse("rejudge_grok.combine_orders AST sha256 %s != the pinned %s: the flip-leg equivalence is unproven for the"
               " changed function (re-run the table test and re-pin)" % (got, pin))
    return got
