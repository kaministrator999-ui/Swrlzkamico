"""v248: Chat mobile edge alignment and canonical HF composer staging contract.

No network, credentials, model inference or repository mutation. Pure source checks.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"chat/§wyrlz/index.html").read_text(encoding="utf-8")
stager=(ROOT/"scripts/prepare_hf_space.py").read_text(encoding="utf-8")
station=(ROOT/"hf_space/station.py").read_text(encoding="utf-8")
hf_app=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")

def test_mobile_response_uses_viewport():
    query=re.search(r"@media\(max-width:600px\)\{\.top-edge\{[^\n]*",html)
    assert query, "canonical mobile layout breakpoint missing"
    css=query.group(0)
    assert ".assistant-body{margin-left:0!important;" in css, "assistant message still indented from left"
    assert ".assistant-actions{margin-left:0}" in css, "response controls must follow assistant alignment"
    assert ".user-message{max-width:91%}" in css, "preserve familiar outgoing bubble treatment"
    assert ".assistant-body{margin-left:38px!important" in html, "do not alter desktop message styling"
    assert "overflow-wrap:anywhere" in css and "width:100%;max-width:100%" in css

def test_clean_composer_and_export():
    composer=html.split('<footer class="composer-shell" id="composerShell"',1)[1].split("</footer>",1)[0]
    for forbidden in ("hfModel","hfProfile","hfUserProfile","Inference Laboratory",
                      "Original Test Bench","hf-lab-link","hf-profile-panel"):
        assert forbidden not in html, f"HF-only test control leaked into canonical Chat: {forbidden}"
        assert forbidden not in composer
    assert 'id="prompt"' in composer and 'id="sendButton"' in composer and 'id="stopButton"' in composer
    menu=html.split('<aside class="side-menu"',1)[1].split("</aside>",1)[0]
    assert 'href="/api/lalm_station/export"' in menu, "chat export belongs in side menu"
    assert 'download="swrlz-dragon-chat.json"' in menu
    assert 'href="/api/lalm_station/export"' not in composer
    assert html.count('href="/api/lalm_station/export"')==1
    assert "modelId:String(settingsState.model.defaultModel||\"700m\")" in html
    assert "profileId:String(settingsState.general.personalityProfile||\"default\")" in html
    assert "ingress:\"SWRLZ_LALM_STATION\"" in html

def test_staging_and_separate_test_lanes():
    assert 'if rel!="chat/§wyrlz/index.html"' not in stager, "Chat staging exception silently bypasses parity"
    assert 'ui.read_bytes()==canonical.read_bytes()' in stager
    assert 'source.read_bytes()).digest()' in stager
    assert 'html=html.replace(' not in stager, "no staging-time Chat markup injection"
    assert "profile:hfProfile.value" not in stager
    assert 'app=gr.mount_gradio_app(station_app,demo,path="/probe"' in hf_app
    assert 'app=gr.mount_gradio_app(app,legacy["demo"],path="/legacy"' in hf_app
    assert 'return HTMLResponse(_chat_document()' in station
    assert "chat/§wyrlz/index.html" in stager

if __name__=="__main__":
    test_mobile_response_uses_viewport()
    test_clean_composer_and_export()
    test_staging_and_separate_test_lanes()
    print("v248: mobile edge, clean composer, export and exact HF staging PASS")
