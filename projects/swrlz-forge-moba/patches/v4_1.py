"""Deterministic v4 -> v4.1 source patch for SWRLZ Forge."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v4.1 patch source token missing: " + old[:120])
    return s.replace(old, new, 1)

def apply(html: str) -> str:
    s = html

    replacements = {
        "<!-- SWRLZ_FORGE_DEPLOY_MARKER: V4_SOLID_TERRAIN_LOCKED_VIEWS -->":
            "<!-- SWRLZ_FORGE_DEPLOY_MARKER: V4_1_GROUND_ADHESION_RUNTIME_CLEANUP -->",
        "<title>SWRLZ Forge · Editor v4</title>":
            "<title>SWRLZ Forge · Editor v4.1</title>",
        '<div class="brand"><b>SWRLZ</b> FORGE · EDITOR v4</div>':
            '<div class="brand"><b>SWRLZ</b> FORGE · EDITOR v4.1</div>',
        '<div class="build-stamp" id="buildStamp">FORGE v4 · 2026.10.05</div>':
            '<div class="build-stamp" id="buildStamp">FORGE v4.1 · 2026.10.05</div>',
        "toast('Rebuilt MOBA Lab v4 with solid terrain, scenic pass, and physics.');":
            "toast('Rebuilt MOBA Lab v4.1 with grounded movement and cleaned gameplay scenery.');",
        "saveBlob('swrlz-forge-project-v4.json'":
            "saveBlob('swrlz-forge-project-v4-1.json'",
        "<title>SWRLZ Forge v4 Playable</title>":
            "<title>SWRLZ Forge v4.1 Playable</title>",
        "<b>SWRLZ Forge v4 Playable</b>":
            "<b>SWRLZ Forge v4.1 Playable</b>",
        "saveBlob('swrlz-forge-playable-v4.html'":
            "saveBlob('swrlz-forge-playable-v4-1.html'",
        "window.SWRLZ_FORGE_BUILD={version:'v4'":
            "window.SWRLZ_FORGE_BUILD={version:'v4.1'",
        "editorLog('Forge v4 editor initialized · locked ortho views · solid terrain shell','ok')":
            "editorLog('Forge v4.1 editor initialized · grounded hero · clean PIE · relocated blockers','ok')",
        "v4: locked authoring views, solid terrain shell, brighter renderer, terrain snapping, mobile tool sheet, improved physics collisions, transactions, PIE/SIE, components, content drawer, validation, and agent API.":
            "v4.1: grounded slope adhesion, clean PIE selection/UI, relocated jungle blockers, solid terrain shell, physics collisions, transactions, PIE/SIE, components, content drawer, validation, and agent API.",
        "Forge v4 Tools":
            "Forge v4.1 Tools",
    }
    for old, new in replacements.items():
        s = _once(s, old, new)

    s = _once(
        s,
        "  .help span:last-child{display:none}.viewport-toolbar{display:none}.badgeBox{top:8px;max-width:52vw}.build-stamp{top:64px}.content-drawer.show{height:min(48vh,360px)}\n}",
        "  .help span:last-child{display:none}.viewport-toolbar{display:none}.badgeBox{top:8px;max-width:52vw}.build-stamp{top:64px}.content-drawer.show{height:min(48vh,360px)}\n"
        "  .banner{top:auto;bottom:10px;left:10px;right:10px;transform:none;border-radius:9px;text-align:center;font-size:10px;padding:6px 8px}\n"
        "  .app.runtime-play .mobile-tabs,.app.runtime-play .help{display:none!important}\n"
        "  .app.runtime-play #mobileToolsBtn,.app.runtime-play #bakeBtn,.app.runtime-play #playBtn{display:none!important}\n"
        "}"
    )

    s = _once(s, '<div class="help">', '<div class="help" id="editorHelp">')

    s = _once(
        s,
        "let heroVel = new THREE.Vector3();\nlet heroGrounded = false;\nlet heroJumpQueued = false;",
        "let heroVel = new THREE.Vector3();\nlet heroGrounded = false;\nlet heroJumpQueued = false;\n"
        "const HERO_GROUND_OFFSET = 0.03;\nconst HERO_STEP_DOWN = 1.25;"
    )

    s = _once(
        s,
        "  makeWall([-2,0,-7],[3.2,1.3,0.7], true, 'North Jungle Wall');\n"
        "  makeWall([2,0,7],[3.2,1.3,0.7], true, 'South Jungle Wall');",
        "  const northWall=makeWall([-12.0,0,-5.5],[2.35,0.9,0.55], true, 'North Jungle Wall'); northWall.rotation.y=0.42;\n"
        "  const southWall=makeWall([12.0,0,5.5],[2.35,0.9,0.55], true, 'South Jungle Wall'); southWall.rotation.y=0.42;"
    )

    s = _once(
        s,
        "  const showcaseRock=makeRock([-3,0,12],[0.85,0.85,0.85],true,'Physics Showcase Rock'); addComponent(showcaseRock,'PhysicsBody'); showcaseRock.userData.folder='Examples/Physics';\n"
        "  const rotator=makeWall([3,0,-12],[1.2,.35,1.2],true,'BP_Rotator'); rotator.userData.blueprintClass='BP_Rotator'; rotator.userData.folder='Examples/Blueprints'; addComponent(rotator,'RotatingMovement');\n",
        "  // Blueprint/physics examples remain available in the Content Drawer instead of cluttering the gameplay map.\n"
    )

    s = _once(
        s,
        "function setSessionButtons(){\n"
        "  const active=playing||simulating; $('playBtn').disabled=active; $('simulateBtn').disabled=active; $('pauseBtn').classList.toggle('hidden',!active); $('stopBtn').classList.toggle('hidden',!active); $('keepBtn').classList.toggle('hidden',!simulating); $('pauseBtn').textContent=paused?'▶ Resume':'Ⅱ Pause';\n"
        "}",
        "function setSessionButtons(){\n"
        "  const active=playing||simulating; app.classList.toggle('runtime-play',playing); app.classList.toggle('runtime-sim',simulating); $('playBtn').disabled=active; $('simulateBtn').disabled=active; $('pauseBtn').classList.toggle('hidden',!active); $('stopBtn').classList.toggle('hidden',!active); $('keepBtn').classList.toggle('hidden',!simulating); $('pauseBtn').textContent=paused?'▶ Resume':'Ⅱ Pause';\n"
        "}"
    )

    s = _once(
        s,
        "  playing=true;simulating=false;paused=false;keepSimulationChanges=false;savePlaySnapshot();transform.detach();orbit.enabled=false;heroClickTarget=null;heroVel.set(0,0,0);heroGrounded=false;lastWave=-999;beginRuntimeComponents();\n"
        "  const h=heroActor(); if(h){if(fromHere){h.position.x=fromHere.x;h.position.z=fromHere.z;}h.position.y=terrainHeight(h.position.x,h.position.z)+1.05;}\n"
        "  $('playBanner').classList.add('show');$('playBanner').textContent='PIE · WASD / ARROWS · SPACE jump · click terrain to move';$('viewLabel').textContent='Play In Editor';setSessionButtons();editorLog('Play In Editor started','ok');toast('Play In Editor started.');",
        "  playing=true;simulating=false;paused=false;keepSimulationChanges=false;savePlaySnapshot();transform.detach();if(selectionBox)selectionBox.visible=false;orbit.enabled=false;heroClickTarget=null;heroVel.set(0,0,0);heroGrounded=true;lastWave=-999;beginRuntimeComponents();\n"
        "  $('mobileDrawer').classList.remove('show');$('mobileToolsPanel').classList.remove('show');$('contentDrawer').classList.remove('show');\n"
        "  const h=heroActor(); if(h){if(fromHere){h.position.x=fromHere.x;h.position.z=fromHere.z;}h.position.y=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;}\n"
        "  $('playBanner').classList.add('show');$('playBanner').textContent='PIE · move WASD/arrows · jump Space · tap terrain';$('viewLabel').textContent='Play In Editor';setSessionButtons();editorLog('Play In Editor started','ok');toast('Play In Editor started.');"
    )

    s = _once(
        s,
        "setCameraView(restoreView);orbit.enabled=true;if(selected)transform.attach(selected);$('playBanner').classList.remove('show');updateViewLabel();setSessionButtons();editorLog('Editor session stopped','ok');toast('Returned to editor.');",
        "setCameraView(restoreView);orbit.enabled=true;if(selectionBox)selectionBox.visible=true;if(selected)transform.attach(selected);$('playBanner').classList.remove('show');updateViewLabel();setSessionButtons();editorLog('Editor session stopped','ok');toast('Returned to editor.');"
    )

    s = _once(
        s,
        "  const groundY = terrainHeight(h.position.x,h.position.z) + 1.05;\n"
        "  if(heroJumpQueued && heroGrounded){\n"
        "    heroVel.y = 6.5;\n"
        "    heroGrounded = false;\n"
        "  }\n"
        "  heroJumpQueued = false;\n"
        "  heroVel.y -= 14 * dt;\n"
        "  h.position.y += heroVel.y * dt;\n"
        "  if(h.position.y <= groundY){\n"
        "    h.position.y = groundY;\n"
        "    heroVel.y = 0;\n"
        "    heroGrounded = true;\n"
        "  }else{\n"
        "    heroGrounded = false;\n"
        "  }",
        "  const groundY = terrainHeight(h.position.x,h.position.z) + HERO_GROUND_OFFSET;\n"
        "  if(heroJumpQueued && heroGrounded){\n"
        "    heroVel.y = 6.5;\n"
        "    heroGrounded = false;\n"
        "  }\n"
        "  heroJumpQueued = false;\n"
        "  if(heroGrounded && heroVel.y <= 0 && (h.position.y-groundY) <= HERO_STEP_DOWN){\n"
        "    // Ground adhesion keeps walking characters glued to rolling terrain and river dips.\n"
        "    h.position.y = groundY;\n"
        "    heroVel.y = 0;\n"
        "  }else{\n"
        "    heroVel.y -= 14 * dt;\n"
        "    h.position.y += heroVel.y * dt;\n"
        "    if(h.position.y <= groundY){\n"
        "      h.position.y = groundY;\n"
        "      heroVel.y = 0;\n"
        "      heroGrounded = true;\n"
        "    }else{\n"
        "      heroGrounded = false;\n"
        "    }\n"
        "  }"
    )

    s = _once(
        s,
        "let keys=new Set(), clickTarget=null, heroVel=new THREE.Vector3(), heroGrounded=false, jumpQueued=false;",
        "const HERO_GROUND_OFFSET=.03,HERO_STEP_DOWN=1.25; let keys=new Set(), clickTarget=null, heroVel=new THREE.Vector3(), heroGrounded=true, jumpQueued=false;"
    )

    s = _once(
        s,
        "let groundY=terrainHeight(h.position.x,h.position.z)+1.05; if(jumpQueued && heroGrounded){heroVel.y=6.5; heroGrounded=false} jumpQueued=false; heroVel.y -= 14*dt; h.position.y += heroVel.y*dt; if(h.position.y<=groundY){h.position.y=groundY; heroVel.y=0; heroGrounded=true}else heroGrounded=false; attack(h,t);",
        "let groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET; if(jumpQueued && heroGrounded){heroVel.y=6.5; heroGrounded=false} jumpQueued=false; if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0}else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true}else heroGrounded=false} attack(h,t);"
    )

    s = _once(s, "version:'forge-agent-v2',", "version:'forge-agent-v2.1',")
    return s
