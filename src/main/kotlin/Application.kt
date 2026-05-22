// SPDX-FileCopyrightText: 2025 Deutsche Telekom AG and others
//
// SPDX-License-Identifier: Apache-2.0

package org.eclipse.lmos.arc.app

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

/**
 * TaxoAdapt Spring Boot Application entry point.
 */
@SpringBootApplication
class TaxoAdaptApplication

fun main(args: Array<String>) {
    runApplication<TaxoAdaptApplication>(*args)
}
