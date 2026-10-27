import org.gradle.kotlin.dsl.kotlin


plugins {
    kotlin("jvm") version "2.1.10"
    kotlin("plugin.serialization") version "2.1.10"
    kotlin("plugin.spring") version "2.1.10"
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.10"
    id("org.springframework.boot") version "3.4.3"
    id("io.spring.dependency-management") version "1.1.7"
    id("org.graalvm.buildtools.native") version "0.10.2"
}

group = "org.eclipse.lmos.app"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

kotlin {
    compilerOptions {
        freeCompilerArgs.addAll("-Xjsr305=strict")
    }
}

tasks.withType<Test> {
    useJUnitPlatform()
    maxParallelForks = 1
}

// THREAD-CAP (registered 2026-09-27, docs/judge_v2_program.md section "THREAD-CAP", plan R-F, RP07).
// -PjvmThreads=N holds a forked JVM to N logical processors: -XX:ActiveProcessorCount=N makes
// Runtime.availableProcessors() return N, which is what Dispatchers.Default (the siteNull
// replicates, TaxonomySplitter, TaxonomyOperations) and ForkJoinPool.commonPool size from.
// Fail-closed: a value that is not a positive integer <= 24 REFUSES here, at configuration time,
// before any task (and so any fork) runs. ABSENT -> nothing is added to any fork: every recorded
// path is byte-inert. Applied to siteNull and bootRun (the forks the cap governs) and to the two
// zero-DB probes threadCapProbe / threadCapProbeExec that prove it by execution.
val jvmThreadsCap: Int? = providers.gradleProperty("jvmThreads").orNull?.let { raw ->
    require(Regex("^[1-9][0-9]?$").matches(raw) && raw.toInt() <= 24) {
        "[THREAD-CAP] -PjvmThreads='$raw' is not a positive integer <= 24; refusing before any fork (absent -> no cap)"
    }
    raw.toInt()
}

// The flag goes through jvmArgumentProviders, NOT jvmArgs(...): on bootRun a jvmArgs(...) entry
// added here is dropped (the Spring Boot plugin sets bootRun's jvm arguments from its own
// convention after this block runs), so the task-graph wiring leg read "-Dtaxoarena.jvmThreads=12"
// without the flag. A provider is appended to allJvmArgs by every JavaForkOptions task.
fun org.gradle.process.JavaForkOptions.applyThreadCap() {
    jvmThreadsCap?.let { n ->
        val capArg = "-XX:ActiveProcessorCount=$n"
        jvmArgumentProviders.add(CommandLineArgumentProvider { listOf(capArg) })
        systemProperty("taxoarena.jvmThreads", n.toString())
    }
}

// THREAD-CAP delta (READY_w0_rp07 H1): the Spring Boot AOT forks in the governed tasks' dependency
// chain (processAot before bootRun, it runs Application.main; processTestAot before siteNull) are
// JavaExec forks too and take the same cap. Absent -> applyThreadCap() adds nothing (byte-inert).
tasks.withType<org.springframework.boot.gradle.tasks.aot.ProcessAot>().configureEach { applyThreadCap() }
tasks.withType<org.springframework.boot.gradle.tasks.aot.ProcessTestAot>().configureEach { applyThreadCap() }

// Two research harnesses, not tests: measurement only, zero assertions, minutes rather than
// the ~5.4s every real test takes combined, and they open embeddings_cache.db and the 8.4 GB
// snapshots.db with read-write handles. Both are excluded from `test` rather than deleted so
// they still compile and cannot rot silently.
//
// SeparationNullBySizeTest (`gradlew nullBySize`) is the CURRENT calibration path. It drives
// the production TaxonomySplitter.splitSingleNode and is validated by replaying the frozen
// Philosophy node (reproduces sep=0.02077 against the canonical run's logged 0.0208).
// Measured curve: docs/separation_null_by_size.md.
//
// NullSeparationCalibrationTest (`gradlew calibration`) is SUPERSEDED. It scores EM's hard
// assignment in the PCA subspace with the k-gate disabled, which is ~3x off the routed 256-d
// statistic the bar actually gates, so its 0.0209 is not the isotropic null of the production
// path. Kept for provenance only -- see the class KDoc.
// TEMP-SPRAWL (2026-10-04): the unit suite's temp files (java.io.tmpdir: Files.createTempDirectory, @TempDir,
// the sqlite-jdbc native library) go to E: -- TAXOARENA_TMP if set, else E:/TaxoArena_tmp -- in a per-worktree dir
// gradle/<worktree>_<hash>/test that the finalizer cleanTestTmp deletes (with its <worktree>_<hash> parent) after the test JVM has exited, pass or fail
// (tests whose service keeps an SQLite connection open cannot delete their own dirs on Windows; see TestTmp.kt).
// E: absent and TAXOARENA_TMP unset -> nothing is set, the JVM default applies. Only the `test` task: the harness
// tasks of record (siteNull, judgeWiring, trainOnlyAudit, nullBySize, ...) are untouched.
val testTmpDir: File? = System.getenv("TAXOARENA_TMP").let { env ->
    val base = File(env ?: "E:/TaxoArena_tmp")
    val driveRoot = base.absoluteFile.toPath().root?.toFile()
    if (env == null && (driveRoot == null || !driveRoot.isDirectory)) null
    else File(base, "gradle/" + rootDir.name + "_" + Integer.toHexString(rootDir.absolutePath.hashCode()) + "/test")
}
val cleanTestTmp = tasks.register<Delete>("cleanTestTmp") {
    description = "TEMP-SPRAWL: deletes the unit suite's java.io.tmpdir on E: after the test JVM has exited."
    testTmpDir?.let { delete(it.parentFile) }
}
tasks.named<Test>("test") {
    // JUDGE-WIRING: MistralJudgePathUnchangedTest re-records its parent-commit golden only under
    // -DrecordMistralGolden=true (forwarded to the forked test JVM here).
    providers.systemProperty("recordMistralGolden").orNull?.let { systemProperty("recordMistralGolden", it) }
    testTmpDir?.let { d ->
        doFirst { d.mkdirs() }
        systemProperty("java.io.tmpdir", d.absolutePath)
        finalizedBy(cleanTestTmp)
    }
    exclude("**/NullSeparationCalibrationTest*")
    // Fifth harness (`gradlew placementReplay`): replays the settled r8 verdicts through the
    // placement stopping rule, refitting Bradley-Terry at every step. Seconds per domain,
    // read-only against the results databases, prints a table and asserts nothing.
    exclude("**/PlacementReplayHarness*")
    exclude("**/SeparationNullBySizeTest*")
    // Third harness (`gradlew randomCellRubrics`): it makes REAL Azure judge-induction calls,
    // so it must never run as part of the suite.
    exclude("**/RandomCellRubricNullHarness*")
    // Fourth harness (`gradlew routeReserved`): routes the reserved pool through the
    // production trickler to dump per-cell assignments. Minutes of runtime, opens the
    // 215 MB embeddings cache and the 275 MB snapshots DB, writes a CSV. No assertions.
    exclude("**/ReserveRoutingHarness*")
    // Sixth harness (`gradlew matchFilterPlan`): plan-only, zero judge calls. Rebuilds the x12
    // schedule from the promoted tree's routing and the frozen pool and drives it to completion
    // twice, once per matchFilter arm, with a stub judge. Opens the 2 GB dataset cache.
    exclude("**/MatchFilterPlanHarness*")
    // Seventh harness (`gradlew trainOnlyAudit`): the TRAIN-ONLY reading of the three trees of
    // record by content (FRAMEWORK item 18). Opens snapshots_frozen.db, snapshots.db, the two
    // dataset caches and embeddings_cache.db READ-ONLY and asserts the pre-registered counts
    // 2,437 / 37 / 427. Real DBs, so it runs only by name.
    exclude("**/TreesOfRecordEvalMembershipAudit*")
    // Eighth harness (`gradlew judgeWiring`): JUDGE-WIRING payload dump / sha diff / parse replay at
    // zero calls, and the 600-match paired run (refused without -Dconfirm=JUDGE-WIRING and a clean
    // sha diff). Opens the 975 MB dataset cache and ratings_x12.db read-only; the run mode posts
    // REAL grok judge calls, so it must never run as part of the suite.
    exclude("**/JudgeWiringHarness*")
    // THREAD-CAP probe (`gradlew threadCapProbe -PjvmThreads=N`): asserts the fork sees N
    // processors, so it only makes sense run by name with the property.
    exclude("**/ThreadCapProbeHarness*")
}

// THREAD-CAP proof by execution on a synthetic fixture (no DB, no snapshot, no network). Two
// probes, one per fork mechanism the cap governs: a Test fork (as siteNull) and a JavaExec fork
// (BootRun extends JavaExec). Both take the cap through the SAME applyThreadCap() as siteNull
// and bootRun.
tasks.register<Test>("threadCapProbe") {
    description = "THREAD-CAP probe (Test fork, as siteNull): prints the [THREAD-CAP] line and measures the pools. No DB."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    applyThreadCap()
    filter { includeTestsMatching("*ThreadCapProbeHarness*") }
}

tasks.register<JavaExec>("threadCapProbeExec") {
    description = "THREAD-CAP probe (JavaExec fork, as bootRun): prints the [THREAD-CAP] line and measures the pools. No DB."
    group = "verification"
    classpath = sourceSets["test"].runtimeClasspath
    mainClass.set("taxonomy.ThreadCapProbeKt")
    outputs.upToDateWhen { false }
    applyThreadCap()
}

tasks.register<JavaExec>("fixedTreeLabels") {
    description = "FIXED-TREE LABELS (D-2026-10-20-2): the production post-pass labeller on an exported fixed tree; " +
        "--args=\"--in <labeller_input.json> --out <labels.json> [--dry-run]\". Needs the root .env exported for a real run."
    group = "application"
    classpath = sourceSets["test"].runtimeClasspath  // the entry point lives in src/test: one main class in src/main
    mainClass.set("taxonomy.FixedTreeLabelMainKt")
    workingDir = rootDir
    outputs.upToDateWhen { false }
}

tasks.register<Test>("trainOnlyAudit") {
    description = "TRAIN-ONLY audit of the trees of record by content (read-only; asserts the pre-registered 2437/37/427)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("dataRoot", providers.systemProperty("dataRoot").getOrElse(rootDir.absolutePath))
    filter { includeTestsMatching("*TreesOfRecordEvalMembershipAudit*") }
}

tasks.register<Test>("judgeWiring") {
    description = "JUDGE-WIRING harness: -Dmode=dump|shas|parse-replay|run (run posts real judge calls; needs -Dconfirm=JUDGE-WIRING)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "4g"
    workingDir = rootDir
    testLogging { showStandardStreams = true; showExceptions = true; exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL }
    outputs.upToDateWhen { false }
    for (p in listOf("mode", "matchId", "set", "setJson", "kit", "evalDb", "x12Db", "out", "outDir", "workers", "pilot", "confirm")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    filter { includeTestsMatching("*JudgeWiringHarness*") }
}

tasks.register<Test>("routeReserved") {
    description = "Routes the reserved pool through the production trickler; dumps query->leaf assignments."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("snapshotId", providers.systemProperty("snapshotId").getOrElse("20260727_042523_Headless_Run_Auto_ge"))
    systemProperty("routeOut", providers.systemProperty("routeOut").getOrElse("reserved_leaf_assignments.csv"))
    filter { includeTestsMatching("*ReserveRoutingHarness*") }
}

tasks.register<Test>("matchFilterPlan") {
    description = "Plan-only: scheduled-match count with matchFilter none vs answerDisagreement. Zero judge calls."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    filter { includeTestsMatching("*MatchFilterPlanHarness*") }
}

tasks.register<Test>("calibration") {
    description = "Runs the separation-null calibration harness (slow, no assertions)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    filter { includeTestsMatching("*NullSeparationCalibrationTest*") }
}

tasks.register<Test>("placementReplay") {
    description = "Replays the settled r8 verdicts through the placement stopping rule."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    filter { includeTestsMatching("*PlacementReplayHarness*") }
    testLogging { showStandardStreams = true }
}

tasks.register<Test>("nullBySize") {
    description = "Measures the split-acceptance separation null as a function of node population n."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    testLogging { showStandardStreams = true }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("400"))
    filter { includeTestsMatching("*SeparationNullBySizeTest*") }
    // CERT-POSITIVE-CONTROL (READY_cert_positive_control C-2): the declared-site arm runs only under its own task
    // (certPositiveControl); excluded here so nullBySize runs exactly the methods it ran before.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certPositiveControl*") }
    // CERT-PC-SIZE: the subsampled declared-site arm runs only under its own task (certPcSize); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certPcSize*") }
    // CERT-PC-K2: the declared two-family arm runs only under its own task (certPcK2); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certPcK2*") }
    // GEMMA-OWN-BAR: the TRAIN-root null calibration arm runs only under its own task (gemmaOwnBar); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*gemmaOwnBar*") }
    // CERT-PC-K2-KNOWN: the merged-pair arm runs only under its own task (certKnownPair); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certKnownPair*") }
    // CERT-K2-DEFLATED: the deflated-only declared-site arm runs only under its own task (certK2Deflated); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certK2Deflated*") }
    // CERT-PLANTED: the planted two-way shift arm runs only under its own task (certPlanted); excluded here likewise.
    filter { excludeTestsMatching("*SeparationNullBySizeTest*certPlanted*") }
}

tasks.register<Test>("withinNull") {
    description = "Re-derives the within-node (anisotropy-preserving) separation null on the frozen mcs=55 artifact's depth-1 anchors."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    systemProperty("snapshotId", providers.systemProperty("snapshotId").getOrElse("20260727_042523_Headless_Run_Auto_ge"))
    filter { includeTestsMatching("*SeparationNullBySizeTest*withinNull*") }
}

tasks.register<Test>("siteNull") {
    description = "Site-level + deflated within-node separation nulls on every accepted split of the frozen mcs=55 artifact (P2 certification)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    // Heap. The harness runs `reps` replicates of the site's OWN population concurrently on
    // Dispatchers.Default (parallelism = availableProcessors), and EVERY live replicate holds
    // ~8 arrays of n x sliceDim doubles at the pcaProject peak: the synthetic cloud, the
    // Embedding FloatArrays, their cached projectTo DoubleArrays, pcaProjectMemo's `input`
    // copy, pcaProject's `centered` and `residual`, and 3 copies of the n x 128 output.
    // Peak live set ~= cores * n * (7 * sliceDim + 3 * 128) * 8 bytes.
    // 20NG root site n=11845, 24 cores: 4.2 GB at sliceDim=256 (fits 6g -- T1 ran 53 min,
    // exit 0), 7.5 GB at sliceDim=512 (does NOT fit -- T1b died at 168 s with
    // "OutOfMemoryError: Java heap space: failed reallocation of scalar replaced objects"
    // inside runArm, build/test-results/siteNull/TEST-Gradle#20Test#20Executor#202.xml).
    // Default unchanged at 6g, so every arm already on the record is byte-inert; a large-n
    // 512-dim arm passes -DsiteNullHeap=14g. Fail-closed: the value must parse.
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    // A worker that dies on heap exhaustion leaves an EMPTY system-err and a test JUnit marks
    // SKIPPED; the heap dump is the only artefact that says which site and how big.
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/siteNull-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    systemProperty("snapshotId", providers.systemProperty("snapshotId").getOrElse("20260727_042523_Headless_Run_Auto_ge"))
    // D1 sweep: put the harness on the build's geometry and keep its table out of the frozen one.
    providers.systemProperty("sliceDim").orNull?.let { systemProperty("sliceDim", it) }
    providers.systemProperty("dropTop").orNull?.let { systemProperty("dropTop", it) }
    providers.systemProperty("whiten").orNull?.let { systemProperty("whiten", it) }
    providers.systemProperty("outCsv").orNull?.let { systemProperty("outCsv", it) }
    // TOPIC-PARTITION-20NG: the arm's own bar (T1b 0.0145, T2 its computed bar); absent -> 0.025 (byte-inert).
    providers.systemProperty("sepBar").orNull?.let { systemProperty("sepBar", it) }
    // THREAD-CAP (RP07): -PjvmThreads=N -> -XX:ActiveProcessorCount=N; absent -> nothing added.
    applyThreadCap()
    // EMBEDDER-PLUMBING (RP08, programme L21754-L21772): the embedding cache the harness reads and the model its
    // vectors must come from. Forwarded only when set, so an absent flag leaves the test JVM's properties exactly
    // as before (byte-inert); validated fail-closed inside the harness (EmbedderReadGuard), before any replicate.
    providers.systemProperty("embeddingCacheFile").orNull?.let { systemProperty("embeddingCacheFile", it) }
    providers.systemProperty("embeddingModel").orNull?.let { systemProperty("embeddingModel", it) }
    filter { includeTestsMatching("*SeparationNullBySizeTest*siteNull*") }
}

// CERT-POSITIVE-CONTROL (registered 2026-10-02; docs/judge_v2_program.md "## Registered 2026-10-02 (before any code or
// call) — CERT-POSITIVE-CONTROL: ..."): the declared-site arm of SeparationNullBySizeTest (the method
// `certPositiveControl - ...`), launched by tools/analysis/cert_positive_control.py's printed command, read by its
// --analyze. A NEW task: siteNull above is untouched and its filter does not match the new method. Same fork settings
// as siteNull (heap 6g default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); the arm's own inputs are
// forwarded only when set and are required inside the arm (refused when absent). The embedder flags are NOT forwarded:
// the arm reads the qwen3 cache of record only.
tasks.register<Test>("certPositiveControl") {
    description = "CERT-POSITIVE-CONTROL: declared partitions (14 categories at the member root; src inside each anchor) scored against their own site nulls."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certPositiveControl-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "declaredLabels", "g12Sites", "outDir", "i1Form", "i1Bracket")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certPositiveControl*") }
}

// CERT-PC-SIZE (registered 2026-10-03; docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) —
// CERT-PC-SIZE: ..."): the subsampled declared-site arm of SeparationNullBySizeTest (the method `certPcSize - ...`),
// launched by tools/analysis/cert_pc_size.py's printed command, read by its --analyze. A NEW task with certPositiveControl's
// fork settings (heap 6g default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); its own inputs (-DsiteLabels,
// -DoutDir, -DsnapshotId) forwarded only when set and required inside the arm. The embedder flags are NOT forwarded.
tasks.register<Test>("certPcSize") {
    description = "CERT-PC-SIZE: the declared 14-category partition on stratified subsamples of the member root, each against its own site null and C0."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certPcSize-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "siteLabels", "outDir")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certPcSize*") }
}

// CERT-PC-K2 (registered 2026-10-03; docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) —
// CERT-PC-K2: ..."): the declared two-family arm of SeparationNullBySizeTest (the method `certPcK2 - ...`), launched by
// tools/analysis/cert_pc_k2.py's printed command, read by its --analyze. A NEW task with certPcSize's fork settings (heap 6g
// default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); its own inputs (-DsiteLabels, -DoutDir, -DsnapshotId)
// forwarded only when set and required inside the arm. The embedder flags are NOT forwarded.
tasks.register<Test>("certPcK2") {
    description = "CERT-PC-K2: the declared 2-way source-family partition inside math / physics / economics on stratified subsamples, each against its own site null and C0."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certPcK2-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "siteLabels", "outDir")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certPcK2*") }
}

// GEMMA-OWN-BAR (registered 2026-10-03; docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) —
// GEMMA-OWN-BAR: ..." L23915-L23927): the TRAIN-root null calibration arm of SeparationNullBySizeTest (the method
// `gemmaOwnBar - ...`), launched by tools/analysis/gemma_own_bar.py --calibrate-plan's printed commands and read by its
// --calibrate. certPcSize's fork settings (heap 6g default / -DsiteNullHeap, the THREAD-CAP); its own inputs (-DgobArm,
// -DoutDir, -DgobBuildDb, -DgobEmbDb, -DgobEmbSha256) forwarded only when set and required inside the arm. The geometry and
// embedder flags are forwarded only so that the arm can REFUSE them (the registration fixes the slice and the bar).
tasks.register<Test>("gemmaOwnBar") {
    description = "GEMMA-OWN-BAR: moment-matched TRAIN-root null p95 (gemma 768 / qwen3 256) and the isotropic width leg at n 406."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/gemmaOwnBar-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("gobArm", "outDir", "gobBuildDb", "gobEmbDb", "gobEmbSha256",
                     "sliceDim", "dropTop", "whiten", "sepBar", "embeddingCacheFile", "embeddingModel")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*gemmaOwnBar*") }
}

// CERT-PC-K2-KNOWN (registered 2026-10-03; docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) —
// CERT-PC-K2-KNOWN: ..." L24036-L24052): the merged-pair arm of SeparationNullBySizeTest (the method `certKnownPair - ...`),
// launched by tools/analysis/cert_pc_k2_known.py's printed command, read by its --analyze. A NEW task with certPcK2's fork
// settings (heap 6g default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); its own inputs (-DsiteLabels, -DoutDir,
// -DsnapshotId) forwarded only when set and required inside the arm. The embedder flags are NOT forwarded.
tasks.register<Test>("certKnownPair") {
    description = "CERT-PC-K2-KNOWN: two declared categories merged into one site (STRONG / MID / EDGE pairs), full size and stratified subsamples at n 486 / 441, each against its own site null and C0."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certKnownPair-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "siteLabels", "outDir")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certKnownPair*") }
}

// CERT-K2-DEFLATED (registered 2026-10-04; docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) —
// CERT-K2-DEFLATED: ..." L24123-L24141): the deflated-only declared-site arm of SeparationNullBySizeTest (the method
// `certK2Deflated - ...`), launched by tools/analysis/cert_k2_deflated.py's printed command, read by its --analyze. A NEW task with
// certKnownPair's fork settings (heap 6g default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); its own inputs (-DsiteLabels,
// -DoutDir, -DsnapshotId) forwarded only when set and required inside the arm. The embedder flags are NOT forwarded.
tasks.register<Test>("certK2Deflated") {
    description = "CERT-K2-DEFLATED: the 33 KK merged-pair sites, the 33 K2 source-split sites, 20 random-relabelling controls and 10 elongation-cut controls, each against its own DEFLATED site null (fresh seed base 20261004)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certK2Deflated-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "siteLabels", "outDir")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certK2Deflated*") }
}

tasks.register<Test>("isoNullByDim") {
    description = "Isotropic separation null of the production splitter at slice widths 128/256/512 (D1 sweep confound readout)."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    providers.systemProperty("isoDims").orNull?.let { systemProperty("isoDims", it) }
    filter { includeTestsMatching("*SeparationNullBySizeTest*isoNullByDim*") }
}

// CERT-PLANTED (registered 2026-10-04; docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) —
// CERT-PLANTED: ..." L24304-L24315): the planted two-way shift arm of SeparationNullBySizeTest (the method `certPlanted - ...`),
// launched by tools/analysis/cert_planted.py's printed command, read by its --analyze. A NEW task with certPcK2's fork settings
// (heap 6g default / -DsiteNullHeap, the THREAD-CAP, the geometry flags); its own inputs (-DsiteLabels, -DplantedVectors,
// -DoutDir, -DsnapshotId) forwarded only when set and required inside the arm. The embedder flags are NOT forwarded.
tasks.register<Test>("certPlanted") {
    description = "CERT-PLANTED: a planted 2-way shift (random direction, random half-split, delta x SD) in math / physics / economics TRAIN subsamples at n 486 / 441, each against its own plain site null."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    maxHeapSize = providers.systemProperty("siteNullHeap").getOrElse("6g").also {
        require(Regex("^[0-9]+[kKmMgG]$").matches(it)) {
            "[SITENULL-HEAP] -DsiteNullHeap='$it' is not a JVM size (e.g. 14g); refusing (absent -> 6g)"
        }
    }
    jvmArgs("-XX:+HeapDumpOnOutOfMemoryError", "-XX:HeapDumpPath=build/reports/certPlanted-oom.hprof")
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    for (p in listOf("snapshotId", "sliceDim", "dropTop", "whiten", "sepBar", "siteLabels", "plantedVectors", "outDir")) {
        providers.systemProperty(p).orNull?.let { systemProperty(p, it) }
    }
    applyThreadCap()
    filter { includeTestsMatching("*SeparationNullBySizeTest*certPlanted*") }
}

tasks.register<Test>("randomCellRubrics") {
    description = "Induces judge rubrics on synthetic random cells (null arm of the rubric-specificity prereg). MAKES REAL AZURE CALLS."
    group = "verification"
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    useJUnitPlatform()
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("rubricNullDryRun", providers.systemProperty("rubricNullDryRun").getOrElse("false"))
    filter { includeTestsMatching("*RandomCellRubricNullHarness*") }
}

// spring-dotenv resolves .env relative to the JVM working directory.
// Without an explicit workingDir, Gradle uses whatever directory the
// task was invoked from (often a module subdirectory in an IDE run config),
// so the .env at the repo root is never found and all ${...} placeholders
// stay blank. Pinning to rootDir makes `./gradlew bootRun` and IDE run
// configurations behave identically.
tasks.named<org.springframework.boot.gradle.tasks.run.BootRun>("bootRun") {
    workingDir = rootDir
    // Spring Boot's "optimized launch" adds -XX:TieredStopAtLevel=1 (C1 only) to the forked
    // JVM: good for a web app's startup, but construction spends 94% of its wall time in
    // tight double loops (PCA power iteration, EM, J) that never reached the optimising
    // tier, while the test-harness JVMs (siteNull, isoNullByDim) always had it. Disabled so
    // the build runs under the same JIT as the harnesses. Replay-verified bit-identical
    // structure (docs/perf_review_2026-09-09.md, gate #1).
    optimizedLaunch.set(false)
    // bootRun forks a JVM, so a -D on the Gradle command line reaches Gradle's JVM and NOT the
    // application. Forward the ones that matter explicitly. `ranking.db.path` isolates a run
    // onto a throwaway ratings DB: match_history is keyed by (snapshot_id, condition), so a
    // re-run against a frozen snapshot CLEARS that snapshot's rows before writing -- which is
    // how a smoke test destroyed the frozen Math MAIN results (1736/11/241 -> 66/1/1).
    providers.systemProperty("ranking.db.path").orNull?.let { systemProperty("ranking.db.path", it) }
    // Embedding-model override for the H9 embedder arms: the EmbeddingModel bean and the
    // per-model EmbeddingCache file both read this at Spring startup, so it must arrive as
    // a system property (a TOML key would be applied too late to matter).
    providers.systemProperty("taxoadapt.llm.embedding-model").orNull?.let { systemProperty("taxoadapt.llm.embedding-model", it) }
    // EMB-TARGET2 C-ET-5: an explicit embedding cache file (an EMBEDDER-CROSS-FLAT --target-dir copy, e.g. a card file);
    // forwarded ONLY when given, so a bootRun without it is unchanged (EmbeddingCache.resolveCacheFile, fail-closed).
    providers.systemProperty("taxoarena.embeddingCacheFile").orNull?.let { systemProperty("taxoarena.embeddingCacheFile", it) }
    // E1-ROUTE R2: the working copy's source sha256 (tools/analysis/e1_route_launch.py); forwarded ONLY when given.
    providers.systemProperty("taxoarena.embeddingCacheSourceSha256").orNull?.let { systemProperty("taxoarena.embeddingCacheSourceSha256", it) }
    // Global LLM permit count (ArcTaxonomyLLMClient's semaphore). It has a value in
    // config/application.yml, so this forward exists only to override it per run without
    // editing that file -- which matters mid-run: if the endpoint starts returning 429s the
    // fix is to relaunch at a lower number, and a command-line flag is the fast path.
    providers.systemProperty("arc.ollama.max-parallel").orNull?.let {
        systemProperty("arc.ollama.max-parallel", it)
    }
    // Request-start pacing, in calls/second. Sized from the TOKEN budget: the token
    // ceiling binds before the request ceiling at these prompt sizes, and pacing to the
    // request ceiling produced a 429 feedback loop. Forwarded so a run can be re-paced
    // without editing config/application.yml.
    providers.systemProperty("arc.ollama.target-rps").orNull?.let {
        systemProperty("arc.ollama.target-rps", it)
    }
    // THREAD-CAP (RP07): -PjvmThreads=N -> -XX:ActiveProcessorCount=N on the forked application
    // JVM; absent -> nothing added. The app prints its [THREAD-CAP] line first thing in main().
    applyThreadCap()
    // Never up-to-date: an experiment run has no meaningful input/output fingerprint, and a
    // silently skipped run reads exactly like a completed one.
    outputs.upToDateWhen { false }
}

dependencies {
    val arcVersion = "0.203.0"
    val langchain4jVersion = "1.8.0"


    // Transparently loads a root-level `.env` file into the Spring Environment
    implementation("me.paulschwarz:spring-dotenv:5.1.0")

    // Coroutines for asynchronous LLM calls
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")

    // Kotlinx Serialization for robust JSON parsing from LLM outputs
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")


    // Arc
    implementation("org.eclipse.lmos:arc-azure-client:$arcVersion")
    implementation("org.eclipse.lmos:arc-langchain4j-client:$arcVersion")
    // arc-spring-boot-starter transitively pulls org.eclipse.lmos:arc-mcp -> io.modelcontextprotocol.sdk:mcp,
    // a Model Context Protocol server stack the TUI never uses. Excluded so no MCP autoconfig/beans can
    // load (the silent context-start failure under web-application-type=none that PR #61 fixed) and to
    // keep the MCP SDK off the classpath entirely.
    implementation("org.eclipse.lmos:arc-spring-boot-starter:$arcVersion") {
        exclude(group = "org.eclipse.lmos", module = "arc-mcp")
        exclude(group = "io.modelcontextprotocol.sdk")
    }
    implementation("org.eclipse.lmos:arc-assistants:$arcVersion")
    implementation("org.eclipse.lmos:arc-readers:$arcVersion")
    implementation("org.eclipse.lmos:arc-api:$arcVersion")
    implementation("org.eclipse.lmos:arc-graphql-spring-boot-starter:$arcVersion")
    implementation("org.eclipse.lmos:arc-view-spring-boot-starter:$arcVersion")

    // Tracing/metrics/actuator deps removed in PR #65.
    //
    // Root cause (proven by jstack): with these on the classpath, Spring Boot's
    // PrometheusExemplarsAutoConfiguration wires a Micrometer MetricsTurboFilter
    // onto the Logback root logger. Every log.info(...) call then runs through
    // ExemplarSampler -> LazyTracingSpanContext.currentSpan, which lazily
    // resolves the Tracer bean from Spring. When a JVM GC notification fires
    // during early bean construction (e.g. EmbeddingCache.init), the
    // Notification Thread takes the same path concurrently with the main
    // thread, and DefaultSingletonBeanRegistry's ReentrantLocks deadlock.
    // Symptom: `[BOOT] TaxoAdapt starting` prints and the JVM hangs forever
    // with the TUI never rendering.
    //
    // No source under src/ uses any micrometer / opentelemetry / actuator API,
    // so removing these is purely subtractive. The TUI is headless
    // (web-application-type=none) and serves no /actuator endpoints.

    // Azure
    implementation("com.azure:azure-identity:1.15.4")

    // Spring Boot
    // spring-boot-starter-actuator removed in PR #65 (see deadlock note above).
    // Kept for spring-web: the @RestController endpoints in taxonomy.controller need it to compile
    // (the unused spring-ai-starter-mcp-server-webflux was removed in PR #61).
    implementation("org.springframework.boot:spring-boot-starter-webflux")

    // Langchain4j
    implementation("dev.langchain4j:langchain4j-bedrock:$langchain4jVersion")
    implementation("dev.langchain4j:langchain4j:$langchain4jVersion")
    implementation("dev.langchain4j:langchain4j-google-ai-gemini:$langchain4jVersion")
    implementation("dev.langchain4j:langchain4j-ollama:$langchain4jVersion")
    implementation("dev.langchain4j:langchain4j-open-ai:$langchain4jVersion")
    implementation("dev.langchain4j:langchain4j-azure-open-ai:$langchain4jVersion")

    // TUI - Mosaic (Jetpack Compose for Terminal)
    implementation("com.jakewharton.mosaic:mosaic-animation:0.18.0")
    implementation("com.jakewharton.mosaic:mosaic-runtime:0.18.0")
    implementation("com.jakewharton.mosaic:mosaic-terminal:0.18.0")
    implementation("org.fusesource.jansi:jansi:2.4.1")

    implementation("org.xerial:sqlite-jdbc:3.51.3.0")

    // micrometer-registry-prometheus removed in PR #65 (see deadlock note above).

    // Test
    testImplementation("org.springframework.boot:spring-boot-testcontainers")
    testImplementation("org.testcontainers:mongodb:1.20.6")
    testImplementation("org.springframework.boot:spring-boot-starter-test")


}

repositories {
    mavenLocal()
    mavenCentral()
    google() // REQUIRED for androidx.lifecycle and other Compose deps
    maven(url = "https://oss.sonatype.org/content/repositories/snapshots/")
}
