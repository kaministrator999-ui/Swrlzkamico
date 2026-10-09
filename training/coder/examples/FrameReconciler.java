// EDUCATIONAL FIXTURE ONLY — not an existing Java service or Android dependency.
// Run: javac FrameReconciler.java && java FrameReconciler
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public final class FrameReconciler {
    record Frame(String requestId, int sequence, String text) {}

    static List<String> orderedFrames(List<Frame> input, String requestId) {
        Map<Integer, String> firstBySequence = new TreeMap<>();
        for (Frame frame : input) {
            if (frame.requestId().equals(requestId) && frame.sequence() > 0) {
                firstBySequence.putIfAbsent(frame.sequence(), frame.text());
            }
        }
        return List.copyOf(firstBySequence.values());
    }

    public static void main(String[] args) {
        var input = new ArrayList<>(List.of(
            new Frame("thread-A", 3, "!"), new Frame("thread-B", 1, "leak"),
            new Frame("thread-A", 1, "Hi"), new Frame("thread-A", 2, " there"),
            new Frame("thread-A", 2, "WRONG")
        ));
        var before = List.copyOf(input);
        if (!orderedFrames(input, "thread-A").equals(List.of("Hi", " there", "!"))) {
            throw new AssertionError("Incorrect ordered output");
        }
        if (!orderedFrames(input, "missing").isEmpty()) {
            throw new AssertionError("Cross-request leakage");
        }
        if (!input.equals(before)) {
            throw new AssertionError("Mutated caller input");
        }
        System.out.println("JAVA_FRAME_PASS");
    }
}
