package taxonomy

import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.slf4j.LoggerFactory
import taxonomy.utils.StatisticsUtils

/**
 * Hornik & Grün (2014, Eq. 9) κ bias correction for the high-dimensional vMF MLE.
 */
class KappaBiasCorrectionTest {

    /** Eq. (9) closed form, for asserting the corrected value. */
    private fun eq9(rBar: Double, d: Double) = rBar * (d - rBar * rBar) / (1.0 - rBar * rBar)

    @Test
    fun high_dimension_low_n_removes_positive_bias() {
        // d/N = 1024/20 = 51.2 > 5 → correction applies. The inflated MLE is
        // replaced by the (smaller) bias-corrected estimate.
        val rBar = 0.8
        val inflatedMle = 5000.0
        val corrected = StatisticsUtils.biasCorrectKappa(inflatedMle, rBar, 1024, 20)
        val expected = (inflatedMle * (20 - 1) / (20 + 1024 - 2)).coerceIn(1e-3, 1e4)
        assertEquals(expected, corrected, 1e-6)
        assertTrue(corrected < inflatedMle, "Bias correction must reduce the inflated MLE, got $corrected")
    }

    @Test
    fun low_dimension_high_n_leaves_mle_unchanged() {
        // d/N = 128/1000 = 0.128 < 5 → no correction, MLE returned verbatim.
        val mle = 123.45
        val corrected = StatisticsUtils.biasCorrectKappa(mle, 0.8, 128, 1000)
        assertEquals(mle, corrected, 1e-9, "Below d/N = 5 the MLE must pass through unchanged")
    }

    @Test
    fun extreme_ratio_emits_warning() {
        val logger = LoggerFactory.getLogger("taxonomy.Statistics") as Logger
        val appender = ListAppender<ILoggingEvent>().apply { start() }
        logger.addAppender(appender)
        try {
            // d/N = 1024/5 = 204.8 > 10 → WARN emitted, correction still applied.
            val corrected = StatisticsUtils.biasCorrectKappa(9_999_999.0, 0.95, 1024, 5)
            val expected = (9_999_999.0 * (5 - 1) / (5 + 1024 - 2)).coerceIn(1e-3, 1e4)
            assertEquals(expected, corrected, 1e-6)
        } finally {
            logger.detachAppender(appender)
        }

        val warned = appender.list.any { it.level == Level.WARN && it.formattedMessage.contains("[VMF]") }
        assertTrue(warned, "d/N > 10 must emit a WARN log; events=${appender.list.map { it.formattedMessage }}")
    }
}
