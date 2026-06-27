// SPDX-FileCopyrightText: 2025 Deutsche Telekom AG and others
//
// SPDX-License-Identifier: Apache-2.0

package org.eclipse.lmos.arc.app

import taxonomy.*
import taxonomy.arena.*
import taxonomy.prompts.*
import taxonomy.utils.*
import taxonomy.config.*
import taxonomy.model.*
import taxonomy.controller.*
import taxonomy.service.*
import taxonomy.dataset.*
import taxonomy.operations.*
import taxonomy.tui.*
import taxonomy.runner.*

import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.event.ApplicationFailedEvent
import org.springframework.context.ApplicationListener

/**
 * TaxoAdapt Spring Boot Application entry point.
 */
@SpringBootApplication(scanBasePackages = ["org.eclipse.lmos.arc.app", "taxonomy"])
class TaxoAdaptApplication

fun main(args: Array<String>) {
    // Emit one line on the real stderr before Spring/logback initialise, so the user always has
    // proof the JVM is alive even if the context fails to start (the silent-exit symptom PR #61
    // chased down). Uses System.err, not a logger, because logback isn't configured yet.
    System.err.println(
        "[BOOT] TaxoAdapt starting — pid=${ProcessHandle.current().pid()}, " +
            "java=${System.getProperty("java.version")}, " +
            "jar=${TaxoAdaptApplication::class.java.protectionDomain.codeSource?.location}"
    )

    // Spring's banner + bean-wiring logs print BEFORE the TUI service runs and would spill onto
    // the terminal Mosaic is about to take over. Quiet them at the source, before the context
    // (and logback) finish initialising, so the alternate screen starts clean.
    System.setProperty("spring.main.log-startup-info", "false")
    System.setProperty("logging.level.root", "WARN")
    System.setProperty("logging.level.org.springframework", "WARN")

    val app = SpringApplication(TaxoAdaptApplication::class.java)
    // Surface context-start failures loudly on the real stderr instead of exiting silently.
    app.addListeners(
        ApplicationListener<ApplicationFailedEvent> { ev ->
            System.err.println("[BOOT FAILED] Spring context failed: ${ev.exception?.message}")
            ev.exception?.printStackTrace(System.err)
        }
    )
    app.run(*args)
}
