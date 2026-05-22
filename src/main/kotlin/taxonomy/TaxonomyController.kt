package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.runBlocking
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/taxonomy")
class TaxonomyController(
    private val taxonomyService: TaxonomyService
) {

    @PostMapping("/query")
    fun queryTaxonomy(@RequestBody request: QueryRequest): Map<String, Any> = runBlocking {
        try {
            val hierarchy = taxonomyService.queryTaxonomy(request.text)
            mapOf(
                "query" to request.text,
                "matches" to hierarchy
            )
        } catch (e: Exception) {
            mapOf("error" to (e.message ?: "Unknown error"))
        }
    }
}

data class QueryRequest(
    val text: String
)
