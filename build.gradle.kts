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
tasks.named<Test>("test") {
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
    maxHeapSize = "6g"
    workingDir = rootDir
    testLogging { showStandardStreams = true }
    outputs.upToDateWhen { false }
    systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))
    systemProperty("snapshotId", providers.systemProperty("snapshotId").getOrElse("20260727_042523_Headless_Run_Auto_ge"))
    filter { includeTestsMatching("*SeparationNullBySizeTest*siteNull*") }
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
