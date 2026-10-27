package taxonomy

import taxonomy.runner.FixedTreeLabels

/**
 * Entry point of the JavaExec task `fixedTreeLabels` (FIXED-TREE LABELS, D-2026-10-20-2). Kept in the test source set
 * so that the main source set keeps exactly one main class (Spring Boot's resolveMainClassName for bootRun / bootJar).
 */
fun main(args: Array<String>) {
    kotlin.system.exitProcess(FixedTreeLabels.run(args))
}
