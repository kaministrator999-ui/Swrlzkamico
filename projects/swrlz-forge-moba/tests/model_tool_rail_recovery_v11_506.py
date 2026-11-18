#!/usr/bin/env python3
"""§E v11.506: browser check for the real persisted-rail fold and CSS layout."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def run():
    script = (ROOT / 'runtime/model_tool_rail_fold_v11_473.js').read_text('utf-8')
    script = script.replace(
        "const key='swyrl.engine.modeler.tool-rail-fold.v1';",
        "const key='swyrl.engine.modeler.tool-rail-fold.v2';"
    )
    assert "tool-rail-fold.v2" in script
    css = '\n'.join((ROOT / path).read_text('utf-8') for path in [
        'runtime/studio_editor_layout_v11_320.css',
        'runtime/model_folding_workspace_v11_473.css',
        'runtime/model_progressive_tools_v11_474.css',
        'runtime/model_mini_studios_v11_496.css',
        'runtime/model_tool_rail_recovery_v11_506.css'
    ])
    categories = 'Meshes Sculpt Lasso Topology Face Appearance Motion References'.split()
    buttons = ''.join(f'<button type="button">{name}</button>' for name in categories)
    fixture = f"""<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
    #modelAtelierPanel{{width:100vw;height:600px}}
    #modelAtelierPanel .atelier-body{{display:grid;height:570px;
      grid-template-columns:34px minmax(0,1fr) 88px 0px;}}
    #modelAtelierPanel .atelier-scene{{grid-column:2;grid-row:1}}
    #modelAtelierPanel .atelier-inspector{{grid-column:4;grid-row:1}}
    {css}
    </style></head><body>
    <section id="modelAtelierPanel" class="se187-modeler-page" data-se320-ui="true"
      data-se251-layout="desktop" data-se496-studio="model" data-se251-right-collapsed="true"
      data-se473-rail-collapsed="false" data-se474-progressive="true">
      <div class="atelier-body">
        <div class="atelier-scene">Viewport</div>
        <nav id="modelAtelierToolRail">{buttons}</nav>
        <aside class="atelier-inspector">Tool settings</aside>
      </div>
    </section></body></html>"""
    with sync_playwright() as p:
        chrome=next((str(x) for x in [Path('/usr/bin/chromium'),Path('/usr/bin/google-chrome'),Path('/usr/bin/google-chrome-stable')] if x.exists()),None)
        browser = p.chromium.launch(executable_path=chrome,headless=True,
            args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width, height, mobile in [(820,1700,False),(390,800,True)]:
                context = browser.new_context(
                    viewport={'width':width,'height':height},
                    is_mobile=mobile,has_touch=mobile)
                page = context.new_page()
                page.route('**/*',lambda route:route.fulfill(
                    status=200,content_type='text/html',body=fixture))
                page.goto('http://engine.test/editor',wait_until='domcontentloaded')
                page.evaluate("""() => {
                  localStorage.setItem('swyrl.engine.modeler.tool-rail-fold.v1','collapsed');
                  localStorage.removeItem('swyrl.engine.modeler.tool-rail-fold.v2');
                }""")
                page.add_script_tag(content=script)
                page.wait_for_function("""() => document.querySelector('#se473RailFold')
                  && document.querySelector('#modelAtelierPanel').dataset.se473RailCollapsed==='false'""")
                visible = page.locator('#modelAtelierToolRail > button:not(#se473RailFold)')
                assert visible.count()==8, 'all native category controls must survive'
                assert all(visible.nth(i).is_visible() for i in range(8)), 'category rail hidden'
                assert page.locator('#se473RailFold').get_attribute('aria-expanded')=='true'
                # Closed inspector remains closed when interacting with fold.
                page.locator('#se473RailFold').click()
                assert page.locator('#modelAtelierPanel').get_attribute('data-se473-rail-collapsed')=='true'
                assert page.evaluate("""() => localStorage.getItem(
                   'swyrl.engine.modeler.tool-rail-fold.v2')""")=='collapsed'
                page.locator('#se473RailFold').click()
                assert page.locator('#modelAtelierPanel').get_attribute('data-se473-rail-collapsed')=='false'
                assert all(visible.nth(i).is_visible() for i in range(8)), 'fold did not reopen'
                assert page.locator('#modelAtelierPanel').get_attribute('data-se251-right-collapsed')=='true'
                page.evaluate("""() => document.querySelector('#modelAtelierPanel').dataset.se496Studio='rig'""")
                assert page.locator('#modelAtelierToolRail').is_hidden(), 'rig studio must hide model rail'
                page.evaluate("""() => document.querySelector('#modelAtelierPanel').dataset.se496Studio='model'""")
                assert visible.first.is_visible(), 'model studio must restore rail on return'
                print(f'SE506_RAIL_BROWSER_PASS viewport={width}x{height} mobile={mobile} categories=8 fold=ok studio=ok',flush=True)
                context.close()
        finally:
            browser.close()

if __name__=='__main__':
    run()
