import org.gradle.kotlin.dsl.kotlin

// SPDX-FileCopyrightText: 2025 Deutsche Telekom AG and others
//
// SPDX-License-Identifier: Apache-2.0

plugins {
    kotlin("jvm") version "2.1.10"
    kotlin("plugin.serialization") version "2.1.10"
    kotlin("plugin.spring") version "2.4.0"
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


    // Coroutines for asynchronous LLM calls
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")

    // Kotlinx Serialization for robust JSON parsing from LLM outputs
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")


    // Arc
    implementation("org.eclipse.lmos:arc-azure-client:$arcVersion")
    implementation("org.eclipse.lmos:arc-langchain4j-client:$arcVersion")
    implementation("org.eclipse.lmos:arc-spring-boot-starter:$arcVersion")
    implementation("org.eclipse.lmos:arc-assistants:$arcVersion")
    implementation("org.eclipse.lmos:arc-readers:$arcVersion")
    implementation("org.eclipse.lmos:arc-api:$arcVersion")
    implementation("org.eclipse.lmos:arc-graphql-spring-boot-starter:$arcVersion")
    implementation("org.eclipse.lmos:arc-view-spring-boot-starter:$arcVersion")

    // Tracing
    implementation(platform("io.micrometer:micrometer-tracing-bom:1.4.5"))
    implementation("io.micrometer:micrometer-tracing")
    implementation("io.opentelemetry:opentelemetry-exporter-otlp")
    implementation("io.micrometer:micrometer-tracing-bridge-otel")

    // Azure
    implementation("com.azure:azure-identity:1.15.4")

    // Spring Boot
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.ai:spring-ai-starter-mcp-server-webflux:1.1.1")
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

    // Metrics
    implementation("io.micrometer:micrometer-registry-prometheus")

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
