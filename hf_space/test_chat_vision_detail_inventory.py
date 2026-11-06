"""Focused, no-model regression tests for §C's visual-detail routing.

These tests check crop selection, prompt intent, cancellation and handoff
provenance, not SmolVLM's actual ability to identify an unseen image.
"""
import base64
import io
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

import chat_vision


def data_url(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def reference_sheet():
    image = Image.new("RGB", (1536, 800), "white")
    painter = ImageDraw.Draw(image)
    for index in range(4):
        x = index * 380 + 20
        for row in range(7):
            y = 50 + row * 98
            painter.rectangle(
                (x, y, x + 200, y + 70),
                outline="black", width=6,
                fill=["#7136be", "#ecb451", "#292929"][row % 3],
            )
            painter.line((x + 20, y + 5, x + 160, y + 60),
                         fill="white", width=3)
    return image


class FakeVisionModel:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        ordinal = len(self.calls)
        if ordinal == 1:
            caption = ("A plain red field." if "What is visible?" in kwargs["messages"][0]["content"][0]["text"]
                       else "Character turnaround sheet showing four views of a purple-clothed mage.")
        elif ordinal == 6:
            caption = "A purple mage wears a gold-trimmed robe with moon symbols and holds a staff."
        else:
            caption = "Region %d: purple sleeve, gold stitching and a staff." % ordinal
        yield {"choices": [{"delta": {"content": caption}}]}


class DetailedImageRoutingTests(unittest.TestCase):
    def test_solid_color_is_one_pass(self):
        picture = data_url(Image.new("RGB", (1536, 800), "#c83a43"))
        self.assertEqual(chat_vision._detail_regions(picture, "A red field"), [])
        model = FakeVisionModel()
        with patch.object(chat_vision, "_load_local_model", return_value=model):
            result = chat_vision._ask_vision_local(picture, "What is visible?")
        self.assertEqual(len(model.calls), 1)
        self.assertIn("A plain red field.", result)
        self.assertNotIn("Far-left detail (source-image crop)", result)

    def test_dense_reference_has_distinct_spatial_crops_not_repeated_resizes(self):
        picture = data_url(reference_sheet())
        crops = chat_vision._detail_regions(
            picture, "Character turnaround with different views"
        )
        self.assertEqual([label for label, _ in crops], [
            "Far-left detail", "Center-left detail",
            "Center-right detail", "Far-right detail",
        ])
        self.assertEqual(len({encoded for _, encoded in crops}), 4)
        # The wide sheet's top figure band is cropped; full-height
        # strips would mix the figures with title/footer swatches.
        for _, encoded in crops:
            raw = base64.b64decode(encoded.partition(",")[2])
            with Image.open(io.BytesIO(raw)) as view:
                self.assertLessEqual(max(view.size), 768)
                self.assertLessEqual(view.height, 545)

    def test_full_image_then_crops_uses_specific_instructions_and_observed_text(self):
        picture = data_url(reference_sheet())
        model = FakeVisionModel()
        phases = []
        with patch.object(chat_vision, "_load_local_model", return_value=model):
            result = chat_vision._ask_vision_local(
                picture, "Describe the mage's actual appearance.",
                report_phase=lambda phase, **fields: phases.append((phase, fields)),
            )
        self.assertEqual(len(model.calls), 6)
        self.assertIn("Integrated whole-image observation", result)
        self.assertIn("A purple mage wears a gold-trimmed robe", result)
        self.assertIn("Far-left detail (source-image crop):", result)
        self.assertIn("Far-right detail (source-image crop):", result)
        self.assertIn("gold stitching", result)
        self.assertEqual(sum(fields.get("inferenceStage") == "REGION_PREFILL" for _, fields in phases), 4)
        self.assertEqual(sum(fields.get("inferenceStage") == "FUSION_PREFILL" for _, fields in phases), 1)
        fused_input = model.calls[-1]["messages"][0]["content"]
        self.assertIn("Whole scene:", fused_input[0]["text"])
        self.assertIn("Center-right detail", fused_input[0]["text"])
        self.assertEqual(fused_input[1]["type"], "image_url")
        self.assertEqual(model.calls[-1]["max_tokens"], 192)
        self.assertTrue(any(fields.get("integratedSelected") is True for _, fields in phases))
        self.assertEqual(model.calls[0]["max_tokens"], chat_vision.MAX_VISION_OUTPUT_TOKENS)
        self.assertEqual(model.calls[1]["max_tokens"], 128)
        self.assertIn("subject you can SEE",
                      model.calls[0]["messages"][0]["content"][0]["text"])
        self.assertIn("Describe the ACTUAL SUBJECT",
                      model.calls[1]["messages"][0]["content"][0]["text"])

    def test_cancelled_job_stops_before_region_inference(self):
        picture = data_url(reference_sheet())
        model = FakeVisionModel()
        checks = {"count": 0}

        def cancelled():
            checks["count"] += 1
            return checks["count"] > 5

        with patch.object(chat_vision, "_load_local_model", return_value=model):
            with self.assertRaises(chat_vision.VisionCancelled):
                chat_vision._ask_vision_local(
                    picture, "Describe details.", should_cancel=cancelled
                )
        self.assertLessEqual(len(model.calls), 2)


if __name__ == "__main__":
    unittest.main()
