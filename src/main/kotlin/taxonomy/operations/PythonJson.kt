package taxonomy.operations

/**
 * A `json.dumps`-compatible serializer (Python 3 defaults) for the JUDGE-WIRING recipe path.
 *
 * WHY THIS EXISTS. The Python cache of record (`stack_judge.py --prompt v2 --judge grok`, posted through
 * `rejudge_reasoning.call_judge_full`) serializes the request body with `json.dumps(payload_body)` and
 * NO keyword arguments, so the bytes on the wire follow CPython's defaults exactly:
 *
 *   - separators `", "` and `": "` (one space after each), no indentation, no trailing newline;
 *   - `ensure_ascii=True`: every character outside `0x20..0x7E` is written as a lowercase `\uXXXX`
 *     escape; characters above the BMP come out as two escapes (the UTF-16 surrogate pair). About a
 *     quarter of the x12 rows carry non-ASCII (em dashes, `≤`, Greek letters, box-drawing rules in
 *     the templates themselves), so this rule decides byte-identity for most payloads;
 *   - `"`, `\` and the C0 controls `\b \f \n \r \t` use their short escapes; `/` is NOT escaped;
 *     DEL (`0x7f`) is escaped as `` because it is outside the printable range;
 *   - dict insertion order is preserved; ints are bare; floats use `float.__repr__`.
 *
 * kotlinx.serialization cannot be configured to do this (it never escapes non-ASCII and has no
 * separator control), hence a small dedicated writer. Supported inputs: `Map<String, *>` (iteration
 * order = output order, so use a `LinkedHashMap`), `List<*>`, `String`, `Boolean`, `Int`, `Long`,
 * `Double`, `Float`, `null`. Anything else is refused rather than guessed.
 */
object PythonJson {

    fun dumps(value: Any?): String = StringBuilder().also { write(it, value) }.toString()

    fun dumpsBytes(value: Any?): ByteArray = dumps(value).toByteArray(Charsets.UTF_8)

    private fun write(sb: StringBuilder, v: Any?) {
        when (v) {
            null -> sb.append("null")
            is String -> writeString(sb, v)
            is Boolean -> sb.append(if (v) "true" else "false")
            is Int -> sb.append(v)
            is Long -> sb.append(v)
            is Double -> sb.append(pythonFloatRepr(v))
            is Float -> sb.append(pythonFloatRepr(v.toDouble()))
            is Map<*, *> -> {
                sb.append('{')
                var first = true
                for ((k, e) in v) {
                    require(k is String) { "PythonJson: map keys must be strings (got ${k?.javaClass})" }
                    if (!first) sb.append(", ")
                    first = false
                    writeString(sb, k)
                    sb.append(": ")
                    write(sb, e)
                }
                sb.append('}')
            }
            is List<*> -> {
                sb.append('[')
                v.forEachIndexed { i, e ->
                    if (i > 0) sb.append(", ")
                    write(sb, e)
                }
                sb.append(']')
            }
            else -> throw IllegalArgumentException("PythonJson: unsupported value type ${v.javaClass.name}")
        }
    }

    /** CPython `encode_basestring_ascii`: `([\\"]|[^\ -~])` is escaped, everything else is copied. */
    fun writeString(sb: StringBuilder, s: String) {
        sb.append('"')
        for (c in s) {
            when {
                c == '"' -> sb.append("\\\"")
                c == '\\' -> sb.append("\\\\")
                c == '\n' -> sb.append("\\n")
                c == '\r' -> sb.append("\\r")
                c == '\t' -> sb.append("\\t")
                c == '\b' -> sb.append("\\b")
                c == '' -> sb.append("\\f")
                c in ' '..'~' -> sb.append(c)
                else -> {
                    // Kotlin strings are UTF-16, so a supplementary character arrives here as its two
                    // surrogates and each is escaped on its own: exactly Python's surrogate-pair output.
                    sb.append("\\u")
                    val hex = Integer.toHexString(c.code)
                    repeat(4 - hex.length) { sb.append('0') }
                    sb.append(hex)
                }
            }
        }
        sb.append('"')
    }

    /**
     * `float.__repr__`: shortest round-trip digits (Java 19+ `Double.toString` gives the same digit
     * string), positional notation when the decimal exponent is in `[-4, 16)`, otherwise
     * `d.ddde[+-]XX` with at least two exponent digits. `inf`/`nan` are refused: `json.dumps`
     * would emit `Infinity`/`NaN`, which the recipe never posts.
     */
    fun pythonFloatRepr(d: Double): String {
        require(!d.isNaN() && !d.isInfinite()) { "PythonJson: non-finite float $d" }
        if (d == 0.0) return if (1.0 / d < 0) "-0.0" else "0.0"
        // Double.toString yields the shortest round-trip digits (JDK 19+), the same digit string
        // CPython's repr chooses; BigDecimal only re-reads them as (unscaled digits, scale).
        val bd = java.math.BigDecimal(java.lang.Double.toString(Math.abs(d))).stripTrailingZeros()
        val digits = bd.unscaledValue().toString()
        val sci = digits.length - 1 - bd.scale()          // decimal exponent of the leading digit
        val sb = StringBuilder()
        if (d < 0) sb.append('-')
        when {
            sci < -4 || sci >= 16 -> {
                sb.append(digits[0])
                if (digits.length > 1) sb.append('.').append(digits, 1, digits.length)
                sb.append('e').append(if (sci < 0) '-' else '+')
                val ae = Math.abs(sci)
                if (ae < 10) sb.append('0')
                sb.append(ae)
            }
            sci < 0 -> {
                sb.append("0.")
                repeat(-sci - 1) { sb.append('0') }
                sb.append(digits)
            }
            sci + 1 >= digits.length -> {
                sb.append(digits)
                repeat(sci + 1 - digits.length) { sb.append('0') }
                sb.append(".0")
            }
            else -> sb.append(digits, 0, sci + 1).append('.').append(digits, sci + 1, digits.length)
        }
        return sb.toString()
    }
}
