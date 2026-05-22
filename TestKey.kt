import com.jakewharton.mosaic.ui.KeyEvent
import com.jakewharton.mosaic.ui.Key

fun main() {
    val methods = KeyEvent::class.java.methods.map { it.name }
    println(methods)
}
