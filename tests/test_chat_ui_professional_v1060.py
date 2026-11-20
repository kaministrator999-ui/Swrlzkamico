"""Static and continuity preflight for canonical §C professional UI v1.0.60."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "chat" / "§wyrlz" / "index.html"
VERSION = ROOT / "chat" / "§wyrlz" / "VERSION.txt"


class DocumentInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.tags = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "script":
            self.scripts.append(attrs.get("src", ""))


class ChatProfessionalUIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.dom = DocumentInventory()
        cls.dom.feed(cls.source)

    def test_canonical_version(self):
        self.assertEqual(VERSION.read_text(encoding="utf-8").strip(), "1.0.60")
        self.assertIn('name="swrlz-chat-version" content="1.0.60"', self.source)

    def test_one_owner_and_unique_component_ids(self):
        ids = self.dom.ids
        self.assertEqual(len(ids), len(set(ids)), "Duplicate IDs would break Chat event binding")
        for ident in (
            "topEdge", "menuButton", "sideMenu", "menuShade", "threadList",
            "newThreadButton", "accountCard", "chatViewport", "messageList",
            "prompt", "composer", "composerShell", "composerCollapse", "sendButton",
            "settingsSheet", "settingsShade", "settingsClose", "settingsSave",
            "workSurface", "workSurfaceButton", "workShade",
        ):
            self.assertIn(ident, ids, f"Required live Chat control missing: {ident}")

    def test_settings_navigation_matches_all_panes(self):
        sections = re.findall(r'data-settings-section="([^"]+)"', self.source)
        panes = re.findall(r'data-settings-pane="([^"]+)"', self.source)
        self.assertEqual(len(sections), 11)
        self.assertEqual(len(sections), len(set(sections)))
        self.assertEqual(set(sections), set(panes))
        self.assertEqual(self.source.count('class="settings-nav-group-label"'), 4)

    def test_transport_and_interaction_bindings_retained(self):
        for literal in (
            'newThreadButton.addEventListener("click",startDraft)',
            'sendButton.addEventListener("click",commitDraftFromPrompt)',
            'menuShade.addEventListener("click", () => setMenu(false))',
            'composerCollapse.addEventListener("click"',
            'workSurfaceButton.addEventListener("click"',
            'settingsSave.addEventListener("click"',
            'document.addEventListener("keydown",event=>{if(event.key==="Escape"&&document.body.classList.contains("menu-open"))',
        ):
            self.assertIn(literal, self.source)

    def test_responsive_and_user_motion_contracts(self):
        for token in (
            "§C 1.0.60 — Unified professional interface",
            "--ui-radius-lg:", "--conversation-width:790px",
            "@media(max-width:680px)", "@media(max-width:370px)",
            "@media(max-height:440px)", "prefers-reduced-motion:reduce",
            "body.motion-reduced .rendered-message",
            "body.a11y-reduced-transparency .composer-box",
            ".assistant-body .code-block", ".settings-nav-group-label",
            ".composer-shell.collapsed", ".settings-nav-button.active",
        ):
            self.assertIn(token, self.source)

    def test_single_html_document_and_inline_styles(self):
        self.assertEqual(len(re.findall(r"<html\\b", self.source)), 1)
        self.assertEqual(self.source.count("</html>"), 1)
        self.assertEqual(self.source.count("</style>"), 1)
        self.assertEqual(self.source.count("<body>"), 1)
        self.assertEqual(self.source.count("</body>"), 1)


if __name__ == "__main__":
    unittest.main()
