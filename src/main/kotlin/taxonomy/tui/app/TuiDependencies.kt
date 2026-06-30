package taxonomy.tui.app

import kotlinx.coroutines.CoroutineScope
import taxonomy.service.TaxonomyTuiService
import taxonomy.tui.controller.CommandController
import taxonomy.tui.controller.DefaultTuiEffects
import taxonomy.tui.controller.TuiController
import taxonomy.tui.service.TuiConfigFacade
import taxonomy.tui.service.TuiGatewayImpl

data class TuiDependencies(
    val host: TaxonomyTuiService,
    val tuiScope: CoroutineScope,
    val log: org.slf4j.Logger,
) {
    val taxonomyService get() = host.taxonomyService
    val arenaService get() = host.arenaService
    val snapshotManager get() = host.snapshotManager
    val datasetFetcher get() = host.datasetFetcher
    val judgeService get() = host.judgeService
    val trickleService get() = host.trickleService
    val embeddingCache get() = host.embeddingCache
    val monitor get() = host.inferenceMonitor
    val config get() = host.config
    val taxonomyEngine get() = host.taxonomyEngine
    val benchmarkService get() = host.benchmarkService
    val evalLoader get() = host.evalLoader
    val evalStore get() = host.evalStore
}

fun TaxonomyTuiService.toTuiDependencies(): TuiDependencies =
    TuiDependencies(
        host = this,
        tuiScope = tuiScope,
        log = log,
    )

fun TuiDependencies.buildController(onQuit: () -> Unit = {}): TuiController {
    val gateway = TuiGatewayImpl(this)
    val effects = DefaultTuiEffects(tuiScope, gateway)
    val facade = TuiConfigFacade(this)
    val commandController = CommandController(effects, settingItemsProvider = facade::buildSettingItems)
    return TuiController(
        effects = effects,
        commandController = commandController,
        settingItemsProvider = facade::buildSettingItems,
        availableDomainsProvider = facade::getAvailableDomains,
        treeLinesProvider = { expanded ->
            taxonomy.tui.components.buildTreeLines(taxonomyService.rootNodeFlow.value, expanded)
        },
        metricsHistorySizeProvider = { taxonomyService.getMetricsHistory().size },
        onQuit = onQuit,
    )
}
