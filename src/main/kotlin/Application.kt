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

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

/**
 * TaxoAdapt Spring Boot Application entry point.
 */
@SpringBootApplication(scanBasePackages = ["org.eclipse.lmos.arc.app", "taxonomy"])
class TaxoAdaptApplication

fun main(args: Array<String>) {
    // Spring's banner + bean-wiring logs print BEFORE the TUI service runs and would spill onto
    // the terminal Mosaic is about to take over. Quiet them at the source, before the context
    // (and logback) finish initialising, so the alternate screen starts clean.
    System.setProperty("spring.main.log-startup-info", "false")
    System.setProperty("logging.level.root", "WARN")
    System.setProperty("logging.level.org.springframework", "WARN")
    runApplication<TaxoAdaptApplication>(*args)
}
