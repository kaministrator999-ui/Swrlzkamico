#!/usr/bin/env python3
"""Inspect effective preview and camera runtime source for 11.254 bug reproduction."""
import base64,gzip,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
s=gzip.decompress(base64.b64decode(''.join((ROOT/n).read_text().strip() for n in m['chunks']))).decode()
for name in m['patches']:s=load_patch(ROOT/name)(s)
for key,aft,bef in [
 ('function se225Open(mode,push=true)',3600,0),
 ('function se225Hide(clearRoute=false)',1000,0),
 ('const stageActive=window.SWYRL_ENGINE_PARTICLE_STAGE_240',1500,450),
 ("   se223State.panel=true;se223State.preview=true;se223UIRefresh();",900,200),
 ("function se223UIPreview()",700,0),
 ("function se223UIOpen()",450,0),
 ("const SE223_PRESETS=Object.freeze({",850,0),
 ("SWYRL_ENGINE_STUDIOS=Object.freeze",900,550),
 ("function tick(",1600,0),
 ("#se225Shell{",550,0),
 ("#se240ParticleStageOrbit",550,0),
 ("se223Frame(dt,t)",450,350),
]:
 at=s.find(key)
 print('\n############ '+key+' offset '+str(at))
 if at>=0:print(s[max(0,at-bef):at+aft])
