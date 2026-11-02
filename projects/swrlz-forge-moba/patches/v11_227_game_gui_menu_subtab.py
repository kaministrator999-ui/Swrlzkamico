"""§E candidate: Game Engine > GUI / Menus authoring mini-tab.
Append-only addition after v11.225; not enabled until the versioned manifest
is resealed from the actual generated HTML by the authoritative builder.
"""
from pathlib import Path
import json

def once(html, old, new):
    count = html.count(old)
    if count != 1:
        raise AssertionError(("GUI/Menu patch anchor", old[:150], count))
    return html.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    js = (root / 'runtime/game_gui_menu_subtab_v11_227.js').read_text('utf8')
    css = (root / 'runtime/game_gui_menu_subtab_v11_227.css').read_text('utf8')
    # The native Game tab owns the scene and input. The sub-tab only controls
    # authored DOM GUI layers and the existing Sheep Tag level menu inspector.
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, '</head>', '<style id="se227GuiMenu">' + css + '</style>\n</head>')
    html = once(html,
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_225_MATERIAL_TEXTURE_STUDIO_TABS',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_227_GAME_GUI_MENU_STUDIO')
    for before, after in [
        ('ENGINE · MAKER v11.225', 'ENGINE · MAKER v11.227'),
        ('v11.225 · Material Texture Studio and four workspace tabs',
         'v11.227 · Game Engine GUI and Menu Setup mini-tab'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.225'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.227'"),
        ('<title>§wyrl§ Engine · Maker v11.225</title>',
         '<title>§wyrl§ Engine · Maker v11.227</title>'),
        ("source.engine='§wyrl§ Engine · Maker v11.225';source.version=11.225;",
         "source.engine='§wyrl§ Engine · Maker v11.227';source.version=11.227;")
    ]:
        html = once(html, before, after)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    obj,n=json.JSONDecoder().raw_decode(html[pos:])
    obj.update(title='Game Engine GUI and Menu Setup sub-tab with editable GUI layers',
      date='2026-11-02',changes=[
       'Game Engine now contains a compact Scene / GUI-Menus mini-tab and a Show/Hide UI preview toggle; the main Modeling, Particle Studio and Materials workspaces remain unchanged.',
       'GUI/Menu inspector reuses the existing Sheep Tag authored Main Menu and edits its text, button color and orbit duration through the native project-level menu editor, rather than creating a competing runtime menu.',
       'Create up to 24 project GUI labels, buttons and panels. Edit names, text, colors, viewport-position/size and safe button actions. Toggle any layer editor-only or set independent visibility in Play.',
       'GUI definitions are bounded, validated project metadata, saved in exported projects and native level snapshots, and use native Undo/Redo transactions. Runtime buttons use only approved native Start/Next/Stop actions, with no injected scripts.',
       'Native menu Play behavior, Quest controls, Sheep Tag gameplay, other four workspaces, authored levels and the existing renderer are unchanged. The GUI overlay uses the existing HTML canvas wrapper, with no second render loop.',
       'Owner mobile and Quest hardware visual acceptance remains pending.']
    )
    return html[:pos]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
