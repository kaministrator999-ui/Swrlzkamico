"""§E v11.186: bootstrap the visual splash in initial HTML, before the engine module.

The v11.185 startup graphic was inserted inside the large application module;
the older body::after fallback could paint while that module had not run.
This patch retains existing styles and readiness logic while making decorative
markup available at first paint, even if the module fails or takes longer.
"""
from pathlib import Path
import re,json

def once(s,old,new):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.186 anchor',old[:120],count))
    return s.replace(old,new,1)

def visual_markup():
    dots=[]
    for i in range(32):
        angle=(i*137.508)%360
        radius=48+(i*29)%130
        delay=-((i*17)%31)/10
        speed=2.6+((i*7)%11)/10
        dots.append(
            '<i style="--se185-angle:%0.3fdeg;--se185-radius-out:%0.1fpx;'
            '--se185-delay:%0.1fs;--se185-speed:%0.1fs"></i>'
            %(angle,radius*1.3,delay,speed)
        )
    return (
        '<div id="se185Init" data-se186-early="1" class="se185-init" '
        'role="status" aria-label="§E is initializing">'
        '<div class="se185-halo" aria-hidden="true">'
        '<span class="se185-ring se185-ring-a"></span>'
        '<span class="se185-ring se185-ring-b"></span>'
        '<span class="se185-core" data-ghost="§E">§E</span>'
        '<span class="se185-wisp se185-wisp-a"></span>'
        '<span class="se185-wisp se185-wisp-b"></span>'
        '<span class="se185-wisp se185-wisp-c"></span>'
        '<div class="se185-particles">'+''.join(dots)+'</div></div>'
        '<div class="se185-boot-copy">'
        '<strong>§wyrl§ ENGINE</strong>'
        '<span class="se185-boot-sub">GLITCH · WISP · INITIALIZATION</span>'
        '<span id="se185BootStage" class="se185-boot-stage" aria-live="polite">'
        'Loading engine interface</span>'
        '<div id="se186BootRecovery" hidden>'
        '<span>Startup is taking longer than expected</span>'
        '<button id="se186BootRetry" type="button">Reload §E</button>'
        '</div></div>'
        '<span class="se185-boot-track" aria-hidden="true"></span></div>'
    )

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/engine_boot_first_paint_v11_186.css').read_text(encoding='utf8')
    early=(root/'runtime/engine_boot_first_paint_v11_186.js').read_text(encoding='utf8')
    # Match first *real* body after the document's original closing head.
    head_end=html.find('</head>')
    assert head_end>=0
    body=re.search(r'<body\b[^>]*>',html[head_end+7:],re.I)
    assert body, 'Cannot locate real body in §E HTML'
    body_end=head_end+7+body.end()
    assert body_end<html.index('window.SWRLZ_FORGE_BUILD='), 'Splash must precede engine module'
    startup='\n'+visual_markup()+'\n<script id="se186StartupBeforeEngine">\n'+early+'\n</script>\n'
    html=html[:body_end]+startup+html[body_end:]
    html=html.replace('</head>','<style id="se186BootFirstPaint">\n'+css+'\n</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_185_WISP_GLITCH_BOOT_ATELIER_COLLAPSE','SWYRL_ENGINE_DEPLOY_MARKER: V11_186_FIRST_PAINT_WISP_BOOT'),
      ('ENGINE · MAKER v11.185','ENGINE · MAKER v11.186'),
      ('v11.185 · glitch-wisp startup and collapsible modeling settings','v11.186 · immediate glitch-wisp startup'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.185'","window.SWRLZ_FORGE_BUILD={version:'v11.186'"),
      ('<title>§wyrl§ Engine · Maker v11.185</title>','<title>§wyrl§ Engine · Maker v11.186</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
       title='Glitch-wisp artwork now available at first paint, before engine initialization',
       date='2026-10-31',
       changes=[
        'Fix blank/fallback-only launch on mobile: the animated §E sigil, 32 glowing fragments and three wisp trails now exist in the initial HTML before the heavy engine module starts.',
        'Keep the original v11.127 startup readiness signal and safe fallback, without fake percentages; update status from a tiny independent early script.',
        'Show a user-controlled Reload §E button if loading has not completed in 18 seconds; never auto-discard the current page or replace a project.',
        'Retain v11.185 collapsible Model Atelier settings, per-device state, native model project storage and VR/Sheep Tag code.',
        'Focused browser first-paint acceptance, physical Android and Quest owner acceptance remain release verification gates.'
       ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
