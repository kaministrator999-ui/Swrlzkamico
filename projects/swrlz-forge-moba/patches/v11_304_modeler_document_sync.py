"""§E v11.304: project loaded documents into an already-open native Modeler."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def once(text, old, new):
    count=text.count(old)
    if count!=1:raise AssertionError(('v11.304 anchor',old[:120],count))
    return text.replace(old,new,1)


def apply(html):
    source=(ROOT/'runtime/model_atelier_document_sync_v11_304.js').read_text('utf8')
    html=once(html,'/* ATELIER_BRIDGE_START */',source+'\n/* ATELIER_BRIDGE_START */')
    old=" source.engine='§wyrl§ Engine · Maker v11.303';source.version=11.303;"
    if html.count(old)!=3:raise AssertionError(('v11.304 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.304';source.version=11.304;")
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_303_VANGUARD_ANATOMICAL_PORTRAIT',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_304_MODELER_DOCUMENT_VIEW_SYNC'),
        ('ENGINE · MAKER v11.303','ENGINE · MAKER v11.304'),
        ('v11.303 · anatomy sculpted face with aligned high-resolution UV portrait','v11.304 · loaded models refresh the existing viewport'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.303'","window.SWRLZ_FORGE_BUILD={version:'v11.304'"),
        ('<title>§wyrl§ Engine · Maker v11.303</title>','<title>§wyrl§ Engine · Maker v11.304</title>'),
    ):html=once(html,old,new)
    token='const SE_RELEASE_NOTES='
    at=html.index(token)+len(token)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Loaded native models refresh the open Modeler',date='2026-11-07',changes=[
        'Refresh the existing Model Atelier scene, mesh list and inspector when a native project replaces an already-open empty or previous document. Keep its renderer, canvas, camera and animation loop.',
        'Track the effective model and parts actually rendered, including the valid empty scratch facade. Repeated synchronization of the same rendered document leaves selection, history and display preferences intact.',
        'Clear stale document-specific selections, component targets, helper overlays and drag references before rebuilding a replacement document. Do not checkpoint, mark dirty, close/reopen the editor or initialize Game.',
        'Preserve the saved native geometry, palette, transforms, account revisions, Chat-only model authoring, v11.295 outward loft lighting and the current Vanguard rebuild/painted-UV features.',
        'Focused real-Three scene/list/GLB regressions and exact source packaging establish the loading path; owner phone/Quest visual acceptance remains separate.',
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
