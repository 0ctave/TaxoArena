package org.eclipse.lmos.arc.app

import dev.langchain4j.model.chat.ChatModel
import dev.langchain4j.model.embedding.EmbeddingModel
import dev.langchain4j.model.ollama.OllamaChatModel
import dev.langchain4j.model.ollama.OllamaEmbeddingModel
import dev.langchain4j.model.azure.AzureOpenAiChatModel
import dev.langchain4j.model.azure.AzureOpenAiEmbeddingModel
import org.eclipse.lmos.arc.agents.ArcException
import org.eclipse.lmos.arc.agents.agents
import org.eclipse.lmos.arc.agents.conversation.AssistantMessage
import org.eclipse.lmos.arc.agents.conversation.ConversationMessage
import org.eclipse.lmos.arc.agents.conversation.UserMessage
import org.eclipse.lmos.arc.agents.functions.LLMFunction
import org.eclipse.lmos.arc.agents.llm.ChatCompleter
import org.eclipse.lmos.arc.agents.llm.ChatCompletionSettings
import org.eclipse.lmos.arc.core.Failure
import org.eclipse.lmos.arc.core.Success
import org.eclipse.lmos.arc.core.getOrThrow
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.stereotype.Component
import kotlin.time.Duration.Companion.minutes
import kotlin.time.toJavaDuration

/**
 * Spring Configuration for Eclipse LMOS Arc Agents.
 */
@Configuration
class ArcConfig {

    /**
     * Explicitly defines the ChatLanguageModel bean.
     * The Arc Spring Boot starter will automatically detect this and construct
     * the 'ChatCompleter' bean required by the rest of the application.
     */
    @Bean
    fun chatLanguageModel(
        @Value("\${arc.ollama.base-url:http://localhost:11434}") baseUrl: String,
        @Value("\${arc.ollama.model:}") arcOllamaModel: String,
        config: org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
    ): ChatModel {
        return if (config.llm.provider == org.eclipse.lmos.arc.app.taxonomy.LlmProviderType.AZURE) {
            AzureOpenAiChatModel.builder()
                .endpoint(config.llm.azure.endpoint)
                .apiKey(config.llm.azure.apiKey)
                .deploymentName(config.llm.azure.deploymentName)
                .serviceVersion(config.llm.azure.apiVersion)
                .timeout(5.minutes.toJavaDuration())
                .build()
        } else {
            val modelName = System.getenv("ARC_MODEL")
                ?: if (arcOllamaModel.isNotBlank()) arcOllamaModel else config.llm.labelingModel
            OllamaChatModel.builder()
                .baseUrl(baseUrl)
                .modelName(modelName)
                .timeout(5.minutes.toJavaDuration())
                .numCtx(8192)
                .build()
        }
    }

    /**
     * Core Integration for Geometric Clustering: The Embedding Model
     */
    @Bean
    fun embeddingModel(
        @Value("\${arc.ollama.base-url:http://localhost:11434}") baseUrl: String,
        @Value("\${arc.ollama.embed-model:qwen3-embedding}") embedModelName: String,
        config: org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig
    ): EmbeddingModel {
        return if (config.llm.embeddingProvider == org.eclipse.lmos.arc.app.taxonomy.LlmProviderType.AZURE) {
            val deploymentName = if (config.llm.azure.embeddingDeploymentName.isNotBlank()) {
                config.llm.azure.embeddingDeploymentName
            } else {
                config.llm.embeddingModel
            }
            AzureOpenAiEmbeddingModel.builder()
                .endpoint(config.llm.azure.endpoint)
                .apiKey(config.llm.azure.apiKey)
                .deploymentName(deploymentName)
                .serviceVersion(config.llm.azure.apiVersion)
                .timeout(1.minutes.toJavaDuration())
                .build()
        } else {
            val modelName = if (config.llm.embeddingModel.isNotBlank()) {
                config.llm.embeddingModel
            } else {
                embedModelName
            }
            OllamaEmbeddingModel.builder()
                .baseUrl(baseUrl)
                .modelName(modelName)
                .timeout(1.minutes.toJavaDuration())
                .build()
        }
    }

    @Bean
    fun chatCompleter(chatModel: ChatModel): ChatCompleter {
        return object : ChatCompleter {
            override suspend fun complete(
                messages: List<ConversationMessage>,
                functions: List<LLMFunction>?,
                settings: ChatCompletionSettings?
            ): org.eclipse.lmos.arc.core.Result<AssistantMessage, ArcException> {
                return try {
                    val promptText = messages.joinToString("\n") { it.content }

                    val response = chatModel.chat(promptText)

                    Success(AssistantMessage(content = response))
                } catch (e: Exception) {
                    // Wrap the exception in an ArcException and return Arc's Failure wrapper
                    Failure(ArcException("Failed to complete chat: ${e.message}", e))
                }
            }
        }
    }


    @Bean
    fun taxoAgents(config: org.eclipse.lmos.arc.app.taxonomy.TaxonomyConfig) = agents {
        agent {
            name = "TaxoClassifier"
            description = "Classifies research papers into existing taxonomy categories."
            model { System.getenv("ARC_MODEL") ?: "gpt-4o" }
        }

        agent {
            name = "TaxoExpander"
            description = "Dynamically expands taxonomies based on document corpus density."
            model { System.getenv("ARC_MODEL") ?: config.llm.labelingModel }
        }

        agent {
            name = "TaxoDistiller"
            description = "Denoises raw queries into core taxonomic keywords."
            model { System.getenv("ARC_MODEL") ?: config.llm.labelingModel }
        }
    }
}

interface LLMProvider {
    suspend fun completePrompt(agentName: String, prompt: String): String
}

/**
 * The ArcLlmProvider is now a Spring Component.
 * The Arc Spring Boot starter automatically injects the fully configured ChatCompleter
 * generated from the ChatLanguageModel bean above.
 */
@Component
class ArcLLMProvider(private val chatCompleter: ChatCompleter) : LLMProvider {

    private val log = LoggerFactory.getLogger(ArcLLMProvider::class.java)

    override suspend fun completePrompt(agentName: String, prompt: String): String {
        log.debug("Routing prompt to Arc Agent: {}", agentName)

        val result = chatCompleter.complete(
            messages = listOf(UserMessage(prompt))
        )

        return result.getOrThrow().content
    }
}