package taxonomy.dataset

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/**
 * Some upstream archives (`arx_3`, `arx_0314`) store the trace as a serialised JSON
 * envelope rather than prose:
 *
 *     {"response": "Let's think step-by-step:\n...", "reason_code": "A", "difficulty": 0}
 *
 * `reason_code` is a self-reported confidence signal that PREDICTS CORRECTNESS
 * (arx_3: A->83.2%, B->55.6%, C->36.5%; arx_0314: A->90.0%, B->57.5%), and only 2 of the
 * roster's models carry one. Passing the envelope to the judge hands it an asymmetric
 * side-channel pointing at the answer — strictly worse than a format artifact, because a
 * format preference is at least uncorrelated with correctness within a stratum.
 *
 * This is an ALLOW-LIST, not a strip-list: everything except `response` is discarded, so a
 * new metadata key in a future archive cannot reopen the channel by default.
 *
 * Measured on the full corpus: both archives parse at 100% (12031/12031 and 12005/12005),
 * so the fallback path below is currently unexercised — it exists so that a malformed row
 * degrades to the raw string instead of throwing, and the DB-level assertions in
 * TraceEnvelopeUnwrapTest catch it if that ever silently reintroduces the field.
 */
private val envelopeJson = Json { ignoreUnknownKeys = true; isLenient = true }

fun unwrapTraceEnvelope(output: String): String {
    val t = output.trimStart()
    if (!t.startsWith("{")) return output
    val obj = runCatching { envelopeJson.parseToJsonElement(t).jsonObject }.getOrNull() ?: return output
    val response = obj["response"]?.let { runCatching { it.jsonPrimitive.content }.getOrNull() }
    return if (response.isNullOrBlank()) output else response
}
