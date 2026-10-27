package taxonomy.tui.utils

import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import org.slf4j.LoggerFactory
import java.io.File

object ClipboardHelper {
    private val log = LoggerFactory.getLogger(ClipboardHelper::class.java)

    fun copyToClipboard(text: String): Boolean {
        // 1. Try AWT toolkit if not headless
        try {
            if (System.getProperty("java.awt.headless") != "true") {
                val selection = StringSelection(text)
                val clipboard = Toolkit.getDefaultToolkit().systemClipboard
                clipboard.setContents(selection, selection)
                log.info("Successfully copied snapshot ID to system clipboard via AWT: $text")
                return true
            }
        } catch (t: Throwable) {
            // Fall through to OS native clipboards
        }

        // 2. Try OS-specific clipboard command-line utilities
        val os = System.getProperty("os.name").lowercase()
        if (os.contains("win")) {
            try {
                val pb = ProcessBuilder("clip")
                val process = pb.start()
                process.outputStream.bufferedWriter().use { it.write(text) }
                if (process.waitFor() == 0) {
                    log.info("Successfully copied snapshot ID to Windows clipboard via clip utility.")
                    return true
                }
            } catch (t: Throwable) {
                log.warn("Windows clip command failed: ${t.message}")
            }
        } else if (os.contains("mac")) {
            try {
                val pb = ProcessBuilder("pbcopy")
                val process = pb.start()
                process.outputStream.bufferedWriter().use { it.write(text) }
                if (process.waitFor() == 0) {
                    log.info("Successfully copied snapshot ID to macOS clipboard via pbcopy.")
                    return true
                }
            } catch (t: Throwable) {
                log.warn("macOS pbcopy command failed: ${t.message}")
            }
        } else {
            // Linux/Unix systems: try xclip first, then wl-copy (Wayland)
            for (cmd in listOf("xclip", "wl-copy")) {
                try {
                    val args = if (cmd == "xclip") listOf("xclip", "-selection", "clipboard") else listOf(cmd)
                    val pb = ProcessBuilder(args)
                    val process = pb.start()
                    process.outputStream.bufferedWriter().use { it.write(text) }
                    if (process.waitFor() == 0) {
                        log.info("Successfully copied snapshot ID to Linux clipboard via $cmd.")
                        return true
                    }
                } catch (t: Throwable) {
                    // Try next fallback command
                }
            }
        }

        // 3. Fallback: Write local text file
        try {
            File("copied_snapshot_id.txt").writeText(text)
            log.info("Wrote copied snapshot ID to copied_snapshot_id.txt in the workspace root.")
            return true
        } catch (t: Throwable) {
            log.error("Fallback file write failed: ${t.message}", t)
        }
        return false
    }
}
