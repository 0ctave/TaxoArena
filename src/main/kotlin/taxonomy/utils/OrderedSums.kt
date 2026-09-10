package taxonomy.utils

/**
 * Order-independent sum of a map's values (sorted by key). ConcurrentHashMaps filled by parallel
 * routing iterate in a thread-timing-dependent order, and floating-point sums taken in that order
 * differ at the last bit run to run; on the construction path that bit reaches kappa, the ESS
 * gate and the bootstrap SE and flips near-tie decisions (measured 2026-09-10, hygiene replicas).
 */
fun orderedSum(m: Map<String, Double>): Double {
    var s = 0.0
    for (k in m.keys.sorted()) s += m.getValue(k)
    return s
}

fun orderedSumOf(m: Map<String, Double>, f: (Double) -> Double): Double {
    var s = 0.0
    for (k in m.keys.sorted()) s += f(m.getValue(k))
    return s
}
