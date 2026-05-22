package org.eclipse.lmos.arc.app.taxonomy

import kotlinx.coroutines.runBlocking
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/taxonomy/arena")
class TaxonomyArenaController(
    private val arenaService: TaxonomyArenaService
) {

    @PostMapping("/compare")
    fun compareModels(@RequestBody request: ArenaRequest): ArenaResult = runBlocking {
        arenaService.compareModels(request.query, request.modelA, request.modelB)
    }
}

data class ArenaRequest(
    val query: String,
    val modelA: String,
    val modelB: String
)
