package org.eclipse.lmos.arc.app.taxonomy.tui

import androidx.compose.runtime.*
import com.jakewharton.mosaic.modifier.Modifier
import com.jakewharton.mosaic.ui.*
import com.jakewharton.mosaic.layout.*
import com.jakewharton.mosaic.text.*
import com.jakewharton.mosaic.ui.TextStyle.Companion.Bold
import com.jakewharton.mosaic.ui.Color.Companion.Blue
import com.jakewharton.mosaic.ui.Color.Companion.Cyan
import com.jakewharton.mosaic.ui.Color.Companion.Green
import com.jakewharton.mosaic.ui.Color.Companion.Magenta
import com.jakewharton.mosaic.ui.Color.Companion.Yellow
import com.jakewharton.mosaic.ui.Color.Companion.White
import com.jakewharton.mosaic.ui.Color.Companion.Black
import com.jakewharton.mosaic.ui.Color.Companion.Red
import com.jakewharton.mosaic.animation.animateColorAsState
import kotlinx.coroutines.*
import kotlinx.serialization.json.*
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import org.eclipse.lmos.arc.app.taxonomy.*
import org.eclipse.lmos.arc.app.taxonomy.operations.*
import com.jakewharton.mosaic.LocalTerminalState
import com.jakewharton.mosaic.terminal.Terminal
import com.jakewharton.mosaic.terminal.*
import com.jakewharton.mosaic.animation.*
import org.fusesource.jansi.AnsiConsole

    @Composable
    internal fun TaxonomyTuiService.NodeInspector(pWidth: Int, pHeight: Int, node: GraphNode?, scroll: Int, lines: List<AnnotatedString>) {
        if (node == null) { Text("No node selected.", color = Yellow); return }
        val visibleH  = (pHeight - 2).coerceAtLeast(1)
        val maxScroll = maxOf(0, lines.size - visibleH)
        val startIdx  = scroll.coerceIn(0, maxScroll)
        val displayed = lines.drop(startIdx).take(visibleH)

        Column {
            // Node title bar
            Text(buildAnnotatedString {
                withStyle(SpanStyle(color = Cyan, textStyle = Bold)) {
                    val label = "  ◈  ${node.label}  ·  depth ${node.depth}  ·  ${node.queries.size} queries"
                    append(label.take(pWidth - 1))
                }
            }.take(pWidth - 1), modifier = Modifier.height(1))

            // Content + scrollbar
            Row {
                Column(modifier = Modifier.width(pWidth - 2)) {
                    displayed.forEach { line -> Text(line.take(pWidth - 3)) }
                    repeat(visibleH - displayed.size) { Text(" ".repeat(pWidth - 3)) }
                }
                // Scrollbar
                Column(modifier = Modifier.width(2)) {
                    if (maxScroll > 0) {
                        val thumbPos = ((startIdx.toDouble() / maxScroll) * (visibleH - 1)).toInt()
                        repeat(visibleH) { i ->
                            Text(if (i == thumbPos) " ▓" else " ░", color = if (i == thumbPos) Cyan else White)
                        }
                    } else {
                        repeat(visibleH) { Text("  ", color = White) }
                    }
                }
            }
        }
    }

    internal fun TaxonomyTuiService.buildInspectorLines(node: GraphNode?, pWidth: Int): List<AnnotatedString> {
        node ?: return emptyList()
        val list       = mutableListOf<AnnotatedString>()
        val innerWidth = (pWidth - 6).coerceAtLeast(20)
        val jsonParser = Json { ignoreUnknownKeys = true; isLenient = true; prettyPrint = true }

        // ── Meta header ──
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Cyan)) { append("  ID: ") }
            withStyle(SpanStyle(color = White)) { append(node.id.take(innerWidth)) }
        })
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Cyan)) { append("  Depth: ") }
            withStyle(SpanStyle(color = depthColor(node.depth), textStyle = Bold)) { append(node.depth.toString()) }
            withStyle(SpanStyle(color = Cyan)) { append("   Queries: ") }
            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(node.queries.size.toString()) }
            withStyle(SpanStyle(color = Cyan)) { append("   Recursive: ") }
            withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append(node.getRecursiveQueryCount().toString()) }
        })
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Cyan)) { append("  Parents: ") }
            withStyle(SpanStyle(color = White)) { append(node.parents.joinToString(", ") { it.label }.take(innerWidth)) }
        })
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Cyan)) { append("  Children: ") }
            withStyle(SpanStyle(color = White)) { append(if (node.children.isEmpty()) "none (leaf)" else node.children.joinToString(", ") { it.label }.take(innerWidth)) }
        })
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Cyan)) { append("  " + "─".repeat(maxOf(0, innerWidth))) }
        })

        // ── Judge content ──
        if (node.judgePrompt == null) {
            list.add(buildAnnotatedString {
                withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("  ○ No Expert Judge inducted yet.") }
            })
            list.add(buildAnnotatedString {
                withStyle(SpanStyle(color = White)) { append("  Press [ R ] to generate a judge for this node.") }
            })
        } else {
            fun addSection(content: String, fallbackLabel: String) {
                try {
                    val firstBrace = content.indexOf('{')
                    val lastBrace  = content.lastIndexOf('}')
                    val cleanJson  = if (firstBrace != -1 && lastBrace > firstBrace) content.substring(firstBrace, lastBrace + 1) else content
                    val parsed     = jsonParser.parseToJsonElement(cleanJson)
                    if (parsed is JsonObject) {
                        val isTopLevel = parsed.containsKey("system_prompt") || parsed.containsKey("rubric")
                        if (isTopLevel) parsed.entries.forEach { formatJsonEntry(it.key, it.value, list, innerWidth) }
                        else formatJsonEntry(fallbackLabel, parsed, list, innerWidth)
                    } else {
                        addMarkdownSection(fallbackLabel, content, list, innerWidth)
                    }
                } catch (e: Exception) {
                    addMarkdownSection(fallbackLabel, content, list, innerWidth)
                }
                list.add(buildAnnotatedString { append("") })
            }

            addSection(node.judgePrompt!!, "SYSTEM PERSONA")
            if (node.judgeRubric != null) addSection(node.judgeRubric!!, "GRADING RUBRIC")
        }

        return list
    }

    internal fun AnnotatedString.Builder.header(text: String) {
        withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append(text) }
    }

    internal fun AnnotatedString.Builder.hotkey(key: String, desc: String) {
        withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append("[$key]") }
        withStyle(SpanStyle(color = White)) { append(" $desc  ") }
    }

    internal fun TaxonomyTuiService.addMarkdownSection(label: String, content: String, list: MutableList<AnnotatedString>, innerWidth: Int) {
        list.add(buildAnnotatedString {
            withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("  $label:") }
        })
        renderMarkdown(content, innerWidth).forEach { line ->
            list.add(buildAnnotatedString { append("    "); append(line) })
        }
    }

    internal fun TaxonomyTuiService.formatJsonEntry(key: String, element: JsonElement, list: MutableList<AnnotatedString>, innerWidth: Int, indent: Int = 0) {
        val prefix     = "  " + "  ".repeat(indent)
        val formattedKey = key.replace("_", " ").uppercase()
        when (element) {
            is JsonPrimitive -> {
                if (element.isString) {
                    list.add(buildAnnotatedString {
                        append(prefix)
                        withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$formattedKey:") }
                    })
                    renderMarkdown(element.content, innerWidth - indent * 2).forEach { line ->
                        list.add(buildAnnotatedString { append("$prefix  "); append(line) })
                    }
                } else {
                    list.add(buildAnnotatedString {
                        append(prefix)
                        withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$formattedKey: ") }
                        withStyle(SpanStyle(color = Cyan)) { append(element.content) }
                    })
                }
            }
            is JsonArray -> {
                list.add(buildAnnotatedString {
                    append(prefix)
                    withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$formattedKey:") }
                })
                element.forEach { item ->
                    if (item is JsonObject) {
                        item.entries.forEachIndexed { i, entry ->
                            formatJsonEntry(if (i == 0) "▸ ${entry.key}" else entry.key, entry.value, list, innerWidth, indent + 1)
                        }
                    } else if (item is JsonPrimitive) {
                        renderMarkdown(item.content, innerWidth - indent * 2 - 4).forEachIndexed { i, line ->
                            list.add(buildAnnotatedString {
                                append(prefix)
                                if (i == 0) withStyle(SpanStyle(color = Magenta)) { append("  ▸ ") } else append("    ")
                                append(line)
                            })
                        }
                    }
                }
            }
            is JsonObject -> {
                list.add(buildAnnotatedString {
                    append(prefix)
                    withStyle(SpanStyle(color = Green, textStyle = Bold)) { append("$formattedKey:") }
                })
                element.entries.forEach { entry -> formatJsonEntry(entry.key, entry.value, list, innerWidth, indent + 1) }
            }
            else -> list.add(buildAnnotatedString { append("$prefix$formattedKey: $element") })
        }
    }

    internal fun TaxonomyTuiService.renderMarkdown(text: String, maxWidth: Int): List<AnnotatedString> {
        val result = mutableListOf<AnnotatedString>()
        text.lines().forEach { rawLine ->
            val line = rawLine.trim()
            if (line.isEmpty()) { result.add(buildAnnotatedString { append("") }); return@forEach }

            val formatted = buildAnnotatedString {
                var cur = line

                // H1 / H2 / H3 with distinct colours
                if (cur.startsWith("###")) {
                    withStyle(SpanStyle(color = Magenta, textStyle = Bold)) { append("▸▸ ${cur.drop(3).trim()}") }
                    return@buildAnnotatedString
                }
                if (cur.startsWith("##")) {
                    withStyle(SpanStyle(color = Cyan, textStyle = Bold)) { append("▸ ${cur.drop(2).trim()}") }
                    return@buildAnnotatedString
                }
                if (cur.startsWith("#")) {
                    withStyle(SpanStyle(color = Yellow, textStyle = Bold)) { append("◈ ${cur.drop(1).trim()}") }
                    return@buildAnnotatedString
                }

                // List bullets
                if (cur.startsWith("- ") || cur.startsWith("* ")) {
                    withStyle(SpanStyle(color = Magenta)) { append("▸ ") }
                    cur = cur.drop(2)
                }

                // Inline bold / code
                var i = 0
                while (i < cur.length) {
                    when {
                        cur.startsWith("**", i) -> {
                            val end = cur.indexOf("**", i + 2)
                            if (end != -1) {
                                withStyle(SpanStyle(textStyle = Bold, color = Yellow)) { append(cur.substring(i + 2, end)) }
                                i = end + 2
                            } else { append(cur[i]); i++ }
                        }
                        cur.startsWith("`", i) -> {
                            val end = cur.indexOf("`", i + 1)
                            if (end != -1) {
                                withStyle(SpanStyle(color = Yellow, background = Black)) { append(cur.substring(i + 1, end)) }
                                i = end + 1
                            } else { append(cur[i]); i++ }
                        }
                        else -> { append(cur[i]); i++ }
                    }
                }
            }
            result.addAll(formatted.safeChunked(maxWidth))
        }
        return result
    }

    internal fun AnnotatedString.take(n: Int): AnnotatedString =
        if (this.length <= n) this else this.subSequence(0, n)

    internal fun AnnotatedString.safeChunked(width: Int): List<AnnotatedString> {
        if (this.length <= width || width <= 0) return listOf(this)
        val result = mutableListOf<AnnotatedString>()
        var start = 0
        while (start < this.length) {
            val end = minOf(start + width, this.length)
            result.add(this.subSequence(start, end))
            start = end
        }
        return result
    }

    internal fun String.center(width: Int): String {
        val target = width - 1
        if (this.length >= target) return this.take(target)
        val padding = (target - this.length) / 2
        return " ".repeat(maxOf(0, padding)) + this
    }
