package taxonomy.utils

import org.slf4j.Logger
import java.io.ByteArrayOutputStream
import java.io.OutputStream

/**
 * Splits writes to a replaced System.out / System.err into two channels:
 *
 *  - **Terminal control sequences** (anything containing an ESC byte, i.e. the ANSI frames Mosaic
 *    prints via System.out) are passed straight through to [passthrough] — the real terminal —
 *    so the TUI keeps rendering. They are NOT buffered: a frame may not end in a newline, and
 *    holding it back would freeze the screen.
 *  - **Plain text** (stray println, stack traces, third-party banners) is line-buffered and
 *    emitted to [log], so it lands in the file/TUI log instead of corrupting the alt-screen.
 *
 * [passthrough] is null for the stderr stream, where there is nothing legitimate to render.
 */
class SlfBufferStream(
    private val log: Logger,
    private val isError: Boolean,
    private val passthrough: OutputStream?,
) : OutputStream() {

    private val buffer = ByteArrayOutputStream(256)

    override fun write(b: Int) = write(byteArrayOf(b.toByte()), 0, 1)

    @Synchronized
    override fun write(b: ByteArray, off: Int, len: Int) {
        var containsEsc = false
        for (i in off until off + len) {
            if (b[i] == ESC) { containsEsc = true; break }
        }
        if (containsEsc) {
            // Hand terminal control output to the real terminal untouched.
            flushLine()
            passthrough?.write(b, off, len)
            passthrough?.flush()
            return
        }
        for (i in off until off + len) {
            val c = b[i].toInt()
            if (c == NEWLINE) flushLine() else buffer.write(c)
        }
    }

    private fun flushLine() {
        if (buffer.size() == 0) return
        val line = buffer.toString(Charsets.UTF_8.name()).trimEnd('\r')
        buffer.reset()
        if (line.isBlank()) return
        if (isError) log.warn(line) else log.info(line)
    }

    @Synchronized
    override fun flush() {
        passthrough?.flush()
    }

    private companion object {
        private const val ESC_INT = 0x1B
        private val ESC = ESC_INT.toByte()
        private const val NEWLINE = '\n'.code
    }
}
