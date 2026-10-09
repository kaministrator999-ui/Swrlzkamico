// EDUCATIONAL FIXTURE ONLY — not an Android app module.
// Run: kotlinc FrameReconciler.kt -include-runtime -d frame-kotlin.jar && java -jar frame-kotlin.jar
data class Frame(val requestId: String, val sequence: Int, val text: String)

fun orderedFrames(frames: List<Frame>, requestId: String): List<String> =
    frames.asSequence()
        .filter { it.requestId == requestId && it.sequence > 0 }
        .distinctBy { it.sequence }
        .sortedBy { it.sequence }
        .map { it.text }
        .toList()

fun main() {
    val input = listOf(
        Frame("thread-A", 3, "!"), Frame("thread-B", 1, "leak"),
        Frame("thread-A", 1, "Hi"), Frame("thread-A", 2, " there"),
        Frame("thread-A", 2, "WRONG")
    )
    val before = input.toList()
    check(orderedFrames(input, "thread-A") == listOf("Hi", " there", "!"))
    check(orderedFrames(input, "missing").isEmpty())
    check(input == before)
    println("KOTLIN_FRAME_PASS")
}
