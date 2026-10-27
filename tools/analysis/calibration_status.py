"""The calibration status word of record: ONE home for FRAMEWORK.md L101's rule.

FRAMEWORK L101 (calibration statement per board): "one status word: UNDETERMINED when nominal < 3; UNDETERMINED
(power: 2x undetectable) when 3 <= nominal < 9 ...; NOT DETECTABLY MISCALIBRATED when nominal >= 9 and Poisson
P(>= observed | nominal) > 0.05; MISCALIBRATED otherwise. The word "calibrated" is never emitted."

Moved VERBATIM on 2026-09-23 (zero calls) from tools/analysis/unfiltered_adopt.py, where it was defined at
L151-157, so that systematic_budget.py's criterion (1) prints the registered word without a second copy of the
rule. unfiltered_adopt imports it back under the same name; it could not be imported from there directly because
unfiltered_adopt imports systematic_budget (a circular import). Note: cert_corpus.py:260 and frontier_fit.py:157
carry their own `status_word` definitions; they were not touched by this move.
"""
from scipy.stats import poisson


def status_word(nominal, observed):
    if nominal < 3:
        return "UNDETERMINED (nominal < 3)"
    if nominal < 9:
        return "UNDETERMINED (power: 2x undetectable; Poisson P(>= %d | %.2f) = %.3f)" % (observed, nominal, 1 - poisson.cdf(observed - 1, nominal))
    p = 1 - poisson.cdf(observed - 1, nominal)
    return ("NOT DETECTABLY MISCALIBRATED" if p > 0.05 else "MISCALIBRATED") + " (Poisson P = %.3f)" % p
