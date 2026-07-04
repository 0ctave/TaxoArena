package taxonomy.controller

import kotlinx.coroutines.runBlocking
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import taxonomy.service.TaxonomyService

@RestController
@RequestMapping("/api/taxonomy")
class TaxonomyController(
    private val taxonomyService: TaxonomyService
) {

    @PostMapping("/query")
    suspend fun queryTaxonomy(@RequestBody request: QueryRequest): Map<String, Any> {
        return try {
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
