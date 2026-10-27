package taxonomy.model

/**
 * The [POOL-PIN] decision a judged run makes before scoring (FRAMEWORK item 18), as a pure
 * function so it can be tested without a runner. A run names the pool it scores; a snapshot run
 * must name the pool its snapshot pinned; the declared `pool` (when set) must agree; and a
 * snapshot whose tree holds EVAL texts among its members is refused unless the exact count is
 * acknowledged, in which case the disclosure line is returned for printing.
 */
object PoolPin {

    data class Verdict(val poolId: String?, val disclosure: String?)

    /**
     * @param requestPool the pool the request scores (null = unrestricted arena)
     * @param snapshotRun true when the tree was loaded from a snapshot (not built or grafted here)
     * @param pinnedPool the pool loadSnapshot pinned, when [snapshotRun]
     * @param evalMembersKnown whether the loaded tree's EVAL-member count could be computed
     * @param evalMembers the loaded tree's EVAL-member count (by content)
     * @param acknowledged `"<snapshotId>:<count>"` entries from the config
     * @param snapshotId the base snapshot id the tree came from
     * @param declaredPool the config's `pool` key, when set
     */
    fun decide(
        condition: String,
        requestPool: String?,
        snapshotRun: Boolean,
        pinnedPool: String?,
        evalMembersKnown: Boolean,
        evalMembers: Int,
        acknowledged: List<String>,
        snapshotId: String?,
        declaredPool: String?
    ): Verdict {
        if (requestPool == null) return Verdict(null, null)
        var disclosure: String? = null
        if (snapshotRun) {
            check(pinnedPool != null && requestPool == pinnedPool) {
                "[POOL-PIN] refusing to judge $condition: snapshot pool=$pinnedPool, request pool=$requestPool"
            }
            check(evalMembersKnown) {
                "[TRAIN-ONLY] refusing to judge $condition: the loaded snapshot's EVAL-member count could not be computed" +
                    " (pool $pinnedPool resolves to no texts)"
            }
            if (evalMembers != 0) {
                check(TrainOnlyGuard.acknowledged(acknowledged, snapshotId, evalMembers)) {
                    "[TRAIN-ONLY] refusing to judge $condition: the loaded tree holds $evalMembers EVAL texts among its members;" +
                        " acknowledge with acknowledgedEvalMembers = [\"$snapshotId:$evalMembers\"] to judge with a disclosure"
                }
                disclosure = "[TRAIN-ONLY] DISCLOSURE: snapshot $snapshotId holds $evalMembers EVAL texts among its tree's members (acknowledged in config)"
            }
        }
        if (declaredPool != null) {
            check(requestPool == declaredPool) { "[POOL-PIN] refusing to judge $condition: resolved pool $requestPool != declared pool $declaredPool" }
        }
        return Verdict(requestPool, disclosure)
    }
}
