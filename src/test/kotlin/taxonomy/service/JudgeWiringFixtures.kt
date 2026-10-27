package taxonomy.service

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import java.io.File

/**
 * Loader for the JUDGE-WIRING fixtures under `src/test/resources/judge_wiring/`, generated once by
 * `python tools/analysis/judge_wiring.py --gen-fixtures` (ASCII-escaped JSON, so git eol conversion
 * cannot touch a byte inside a value). Every Kotlin/Python parity test reads through this.
 */
object JudgeWiringFixtures {
    val json = Json { ignoreUnknownKeys = true }
    private val dir = File("src/test/resources/judge_wiring")

    fun read(name: String): JsonElement {
        val f = File(dir, name)
        require(f.isFile) { "fixture ${f.path} missing: run `python tools/analysis/judge_wiring.py --gen-fixtures`" }
        return json.parseToJsonElement(f.readText(Charsets.US_ASCII))
    }

    fun str(o: JsonObject, key: String): String = (o[key] as JsonPrimitive).content
    fun strOrNull(o: JsonObject, key: String): String? = o[key]?.let { if (it is JsonNull) null else (it as JsonPrimitive).content }
    fun strings(o: JsonObject, key: String): List<String> = (o[key] as JsonArray).map { (it as JsonPrimitive).content }

    /**
     * A JSON element as the Kotlin value PythonJson.dumps takes: objects -> LinkedHashMap (order kept),
     * arrays -> List, strings, booleans, null; numbers -> Double when the literal carries `.`/`e`, else Long.
     */
    fun toValue(e: JsonElement): Any? = when (e) {
        is JsonNull -> null
        is JsonObject -> LinkedHashMap<String, Any?>().also { m -> e.forEach { (k, v) -> m[k] = toValue(v) } }
        is JsonArray -> e.map { toValue(it) }
        is JsonPrimitive -> when {
            e.isString -> e.content
            e.content == "true" -> true
            e.content == "false" -> false
            e.content.any { it == '.' || it == 'e' || it == 'E' } -> e.content.toDouble()
            else -> e.content.toLong().let { if (it in Int.MIN_VALUE..Int.MAX_VALUE) it.toInt() else it }
        }
    }
}
