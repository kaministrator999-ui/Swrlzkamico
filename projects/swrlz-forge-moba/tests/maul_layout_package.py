#!/usr/bin/env python3
"""Validate the sealed classic Maul package and its authored native map."""
import argparse
import hashlib
import json
import math
from pathlib import Path

SCENE = 'scenes/maul-frostveil-classic.swyrl.json'
PATCH = 'patches/v11_62_mobile_adaptive.py'


def require(condition, message):
    if not condition:
        raise AssertionError('Classic Maul package: ' + message)


def validate_scene(data):
    project=data['project'];actors=data['scene']['actors'];layers=data['editor']['layers']
    require(project['canonicalId']=='maul-frostveil' and project['template']=='maul-frostveil' and project['kind']=='maul', 'wrong native starter identity')
    require(project.get('maulLayout')=='classic-v2', 'missing classic-v2 layout identity')
    require(project['maul']['waves']==30 and project['maul']['lives']>0, 'invalid cooperative campaign rules')
    require(actors and len({a['id'] for a in actors})==len(actors), 'empty or duplicate actor identities')
    for kind in ('maul-builder','maul-spawn','maul-gate'):
        group=[a for a in actors if a['type']==kind]
        require(len(group)==9, 'expected nine '+kind+' actors')
        require({a.get('maul',{}).get('sector') for a in group}==set(range(9)), 'missing or duplicate '+kind+' sector connections')
    turns=[a for a in actors if a['type']=='maul-route-turn']
    turn_keys={'westEntry','westOuter','westReturn','eastEntry','eastOuter','eastReturn'}
    require(len(turns)==6 and {a.get('maul',{}).get('turnKey') for a in turns}==turn_keys,
            'expected six distinct authored lower-funnel route turns')
    require(sum(a['type']=='maul-exit' for a in actors)==1, 'expected one shared exit')
    require(any(a['type']=='maul-snowfield' for a in actors), 'missing native snowfield ground')
    require(any(a['type']=='maul-water' for a in actors), 'missing native shore water')
    require(any(a['type']=='maul-cliff' for a in actors), 'missing native cliff geometry')
    require(all(a.get('baked') and a.get('visible') for a in actors), 'every published map actor must be baked and visible')
    require(len(layers)==7 and len({l['id'] for l in layers})==7, 'expected seven distinct editor layers')
    layer_ids={l['id'] for l in layers}
    require(all(any(l['id'] in a.get('editorLayerIds',[]) for a in actors) for l in layers), 'empty map editor layer')
    for actor in actors:
        require(set(actor.get('editorLayerIds',[])) <= layer_ids and bool(actor.get('editorLayerIds')), 'unknown or missing actor layer')
        for key in ('position','rotation','scale'):
            values=actor[key]
            require(len(values)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in values), 'invalid '+key+' transform')
        require(all(v>0 for v in actor['scale']), 'nonpositive native actor scale')
    return {'actors':len(actors),'layers':len(layers),'builders':9,'spawns':9,'waypoints':9,'routeTurns':6,'exits':1}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    args=parser.parse_args();receipt=json.loads((args.package/'SOURCE.json').read_text())
    require(receipt['sourceVersion']=='§wyrl§ Engine v11.62', 'wrong source version')
    require(len(receipt['patches'])==94 and receipt['patches'][-1]==PATCH, 'wrong governed patch chain')
    require(len(receipt['assets'])==43 and SCENE in receipt['assets'] and 'scenes/maul-frostveil.swyrl.json' in receipt['assets'], 'wrong asset set or missing preserved v10.6 map')
    raw=(args.package/SCENE).read_bytes();meta=receipt['assets'][SCENE]
    require(len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'], 'authored scene differs from package receipt')
    proof=validate_scene(json.loads(raw))
    print('MAUL_LAYOUT_NATIVE_PACKAGE_VERIFIED '+json.dumps(proof,sort_keys=True))


if __name__=='__main__':
    main()
