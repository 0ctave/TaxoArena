package org.eclipse.lmos.arc.app.domain

import kotlinx.serialization.Serializable
import kotlinx.serialization.Transient

/**
 * Represents a user query (e.g., from MMLU or user sessions).
 */
@Serializable
data class UserQuery(
    val id: String,
    val text: String,
    val context: String? = null
)

/**
 * Represents a Domain/Capability in a Hierarchical Graph (DAG).
 */
@Serializable
class DomainNode(
    val label: String,
    val description: String,
    val children: MutableList<DomainNode> = mutableListOf()
) {
    // In a Graph, a node can have multiple parents
    @Transient val parents: MutableList<DomainNode> = mutableListOf()
    @Transient val mappedQueries: MutableList<UserQuery> = mutableListOf()

    fun addChild(node: DomainNode) {
        if (!children.contains(node)) {
            children.add(node)
            node.parents.add(this)
        }
    }

    val depth: Int
        get() = if (parents.isEmpty()) 0 else parents.minOf { it.depth } + 1

}

@Serializable
data class ClassificationResponse(
    val explanation: String? = null,
    val class_labels: List<String>
)

@Serializable
data class ExpansionResponse(
    val explanation: String? = null,
    val new_classes: List<DomainClassDef>
)

@Serializable
data class DomainClassDef(
    val label: String,
    val description: String,
    val potential_parent_links: List<String>? = emptyList() // LLM suggests other existing domains to link to
)

@Serializable
data class ClusterLabelResponse(
    val label: String,
    val description: String
)