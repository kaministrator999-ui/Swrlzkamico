#!/usr/bin/env python3
"""Release checks for the exact standalone §C design preview source."""
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

from test_forge_validation_messages import verify as verify_validation_messages


CHAT = Path("chat/§wyrlz/index.html")
CSS_START = "    /* §C Design Studio:"
CSS_END = "    .swrlz-widget.forge-workspace"
WIDGET_START = '          }else if(widget.kind==="forge-design-preview"'
WIDGET_END = '          }else if(widget.kind==="forge-workspace"'
RENDER_START = "            const drawSvg=()=>{"
INTERACTION_START = "            let overlayKey=null,returnFocus=null;"


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.active = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.active = tag == "script" and not attributes.get("src") and attributes.get("type", "") in {
            "", "text/javascript", "application/javascript", "module"
        }
        if self.active:
            self.scripts.append((attributes.get("type"), []))

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.scripts[-1][1].append(data)


def isolate(source, start, end):
    assert source.count(start) == 1, start
    assert source.count(end) == 1, end
    left, rest = source.split(start, 1)
    section, right = rest.split(end, 1)
    return left, start + section, end + right


def project_widget_source(before, after):
    pre_css, before_css, tail_before = isolate(before, CSS_START, CSS_END)
    post_css, after_css, tail_after = isolate(after, CSS_START, CSS_END)
    assert pre_css == post_css
    before_rest, before_widget, before_tail = isolate(tail_before, WIDGET_START, WIDGET_END)
    after_rest, after_widget, after_tail = isolate(tail_after, WIDGET_START, WIDGET_END)
    assert before_rest == after_rest and before_tail == after_tail, "Changed source outside the design preview"
    assert before_css != after_css
    assert before_widget.split(RENDER_START)[0] == after_widget.split(RENDER_START)[0], "Proposal acceptance gates changed"
    assert before_widget.split(INTERACTION_START)[1] == after_widget.split(INTERACTION_START)[1], "Review and approval flow changed"
    assert 'const range=Math.max(4,' in before_widget
    assert '"font-size":12,"font-weight":700' in before_widget
    assert "const range=Math.max(4," not in after_widget
    assert '"vector-effect":"non-scaling-stroke"' in after_widget
    assert '"forge-design-current"' in after_widget and '"Step "+shown' in after_widget
    assert 'view==="side"?[z,-y]' in after_widget and '["side","Side view"]' in after_widget
    assert "include(cx-rx,cy-ry);include(cx+rx,cy+ry);" in after_widget
    assert ".forge-design-drawing{color:#bdd8f2}" in after_css and "700 13px/1.4" in after_css


def check_inline_js(source):
    parser = InlineScripts()
    parser.feed(source)
    parser.close()
    assert parser.scripts, "Missing Chat script"
    for kind, segments in parser.scripts:
        script = "".join(segments)
        command = ["node", "--check"]
        if kind == "module":
            command.append("--input-type=module")
        subprocess.run(command, input=script, text=True, check=True)


if __name__ == "__main__":
    before, after = [Path(directory) for directory in sys.argv[1:3]]
    old_html, new_html = [(directory / CHAT).read_text(encoding="utf-8") for directory in (before, after)]
    project_widget_source(old_html, new_html)
    check_inline_js(new_html)
    verify_validation_messages(before, after)
    print("Forge preview scope and JS verified, with actionable validation feedback before any editor write")
