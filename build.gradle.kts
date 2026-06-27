import org.gradle.kotlin.dsl.kotlin

// SPDX-FileCopyrightText: 2025 Deutsche Telekom AG and others
//
// SPDX-License-Identifier: Apache-2.0

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
