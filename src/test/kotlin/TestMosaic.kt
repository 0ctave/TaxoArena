import com.jakewharton.mosaic.modifier.Modifier
import java.io.File

fun main() {
    val methods = Modifier.Companion::class.java.methods.map { it.name }
    println("Methods in Modifier.Companion: $methods")
    
    // Check package com.jakewharton.mosaic.modifier for any extension functions
    // We can't easily do this, but we can check if onKeyEvent exists as a top-level function.
}
