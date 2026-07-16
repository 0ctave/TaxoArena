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
    val isHeadless = args.contains("--config")
    System.setProperty("spring.main.log-startup-info", "false")
    if (!isHeadless) {
        System.setProperty("logging.level.root", "WARN")
        System.setProperty("logging.level.org.springframework", "WARN")
    } else {
        System.setProperty("logging.level.root", "INFO")
        System.setProperty("logging.level.org.springframework", "WARN")
    }

    // Force UTF-8 everywhere we can. Mosaic emits raw UTF-8 bytes for box-drawing (─│┌┐) and
    // emoji-style icons (◆) straight to its own Tty. On Windows the *console output code page*
    // defaults to the active OEM page (e.g. 437 / 850 / 1252), which interprets those bytes as
    // garbage — the symptom the user reported was every glyph rendered as `?` or `◆`.
    // `chcp 65001` switches the current console to UTF-8 for the lifetime of this process. We
    // shell out *before* Mosaic binds the tty so the new code page is already active when the
    // first frame is drawn.
    System.setProperty("file.encoding", "UTF-8")
    System.setProperty("stdout.encoding", "UTF-8")
    System.setProperty("stderr.encoding", "UTF-8")
    if (System.getProperty("os.name").orEmpty().lowercase().contains("windows")) {
        runCatching {
            // `chcp` is a built-in of cmd.exe, so we must spawn cmd /c. Inherit the parent
            // console so the code-page change applies to *our* console, not a detached child.
            ProcessBuilder("cmd", "/c", "chcp", "65001")
                .inheritIO()
                .start()
                .waitFor()
        }.onFailure {
            System.err.println("[BOOT] chcp 65001 failed (${it.message}); TUI glyphs may render as ?")
        }
    }

    val app = SpringApplication(TaxoAdaptApplication::class.java)
    // Surface context-start failures loudly on the real stderr instead of exiting silently.
    app.addListeners(
        ApplicationListener<ApplicationFailedEvent> { ev ->
            System.err.println("[BOOT FAILED] Spring context failed: ${ev.exception?.message}")
            ev.exception?.printStackTrace(System.err)
        }
    )
    // app.run() can throw before the ApplicationFailedEvent listener above ever fires — e.g. the
    // autoconfigure-exclude validation in Spring Boot 3.4 runs so early that no failure event is
    // broadcast, so the JVM would otherwise exit silently. Catch here as the outermost net.
    try {
        val ctx = app.run(*args)
        // Confirm the context actually started and the TUI CommandLineRunner was registered. If no
        // runner beans exist, the TUI service was never wired (component scan / annotation problem)
        // and the process would otherwise exit silently right after startup.
        val runners = ctx.getBeansOfType(org.springframework.boot.CommandLineRunner::class.java)
        System.err.println("[BOOT] Spring context started; CommandLineRunner beans: ${runners.keys}")
        if (runners.isEmpty()) {
            System.err.println(
                "[BOOT FAILED] No CommandLineRunner beans found — TUI service was not registered. " +
                    "Check @ComponentScan packages and @Component annotations."
            )
        }
        System.err.flush()
    } catch (e: SpringApplication.AbandonedRunException) {
        // Not a failure: the AOT processor (processAot task) deliberately throws this to abort
        // after the context is prepared. Re-throw so the AOT machinery sees it as expected.
        throw e
    } catch (t: Throwable) {
        System.err.println("[BOOT FAILED] Exception during SpringApplication.run: ${t.message}")
        t.printStackTrace(System.err)
        System.err.flush()
        kotlin.system.exitProcess(1)
    }
}
