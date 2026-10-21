#!/usr/bin/env python3
"""Validate the sealed grouped Maul starter and preserved classic native map."""
import argparse
import hashlib
import json
import math
from pathlib import Path

SCENE = 'scenes/maul-frostveil-groups.swyrl.json'
FLIGHT_SCENE = 'scenes/maul-frostveil-flight.swyrl.json'
PATCH = 'patches/v11_62_mobile_adaptive.py'
LEGACY_SCENE = 'scenes/maul-frostveil-classic.swyrl.json'
LEGACY_BYTES = 108598
LEGACY_SHA256 = '858552d9d8a9bdad89f445e6747641b34d9ac7c69c2e207e294ce83dd94718a2'
TOWER_TYPES = {'maul-arrow', 'maul-cannon', 'maul-frost', 'maul-storm', 'maul-maze-wall'}


def require(condition, message):
    if not condition:
        raise AssertionError('Grouped Maul package: ' + message)


def validate_scene(data):
    project=data['project'];actors=data['scene']['actors'];layers=data['editor']['layers']
    require(project['canonicalId']=='maul-frostveil' and project['template']=='maul-frostveil' and project['kind']=='maul', 'wrong native starter identity')
    require(project.get('maulLayout')=='classic-v2' and project.get('maulSpawnStyle')=='grouped-v1', 'missing classic grouped layout identity')
    require(project['maul']['waves']==30 and project['maul']['lives']>0, 'invalid cooperative campaign rules')
    require(len(actors)==78 and len({a['id'] for a in actors})==78, 'expected 78 distinct native map actors')
    require(not any(a['type'] in TOWER_TYPES for a in actors), 'starter gives a player free authored buildings')
    for kind in ('maul-builder','maul-spawn','maul-gate'):
        group=[a for a in actors if a['type']==kind]
        require(len(group)==9 and {a.get('maul',{}).get('sector') for a in group}==set(range(9)), 'missing or duplicate '+kind+' sector connections')
    turns=[a for a in actors if a['type']=='maul-route-turn']
    require(len(turns)==6 and {a.get('maul',{}).get('turnKey') for a in turns}=={'westEntry','westOuter','westReturn','eastEntry','eastOuter','eastReturn'}, 'expected six distinct lower-funnel turns')
    require(sum(a['type']=='maul-exit' for a in actors)==1, 'expected one shared exit')
    for kind in ('maul-snowfield','maul-water','maul-cliff'):
        require(any(a['type']==kind for a in actors), 'missing native '+kind+' geometry')
    require(all(a.get('baked') and a.get('visible') for a in actors), 'every published actor must be baked and visible')
    require(len(layers)==6 and len({l['id'] for l in layers})==6, 'expected six distinct editor layers')
    layer_ids={l['id'] for l in layers}
    require(all(any(l['id'] in a.get('editorLayerIds',[]) for a in actors) for l in layers), 'empty native map layer')
    for actor in actors:
        require(bool(actor.get('editorLayerIds')) and set(actor['editorLayerIds'])<=layer_ids, 'unknown or missing actor layer')
        for key in ('position','rotation','scale'):
            values=actor[key]
            require(len(values)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in values), 'invalid '+key+' transform')
        require(all(v>0 for v in actor['scale']), 'nonpositive native actor scale')
    return {'actors':78,'layers':6,'builders':9,'spawns':9,'waypoints':9,'routeTurns':6,'exits':1,'authoredTowers':0,'spawnStyle':'grouped-v1'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    args=parser.parse_args();receipt=json.loads((args.package/'SOURCE.json').read_text())
    require(receipt['sourceVersion']=='§wyrl§ Engine v11.62', 'wrong source version')
    require(len(receipt['patches'])==94 and receipt['patches'][-1]==PATCH, 'wrong governed patch chain')
    require(len(receipt['assets'])==43 and FLIGHT_SCENE in receipt['assets'] and SCENE in receipt['assets'] and LEGACY_SCENE in receipt['assets'], 'wrong asset set or missing preserved v10.7 scene')
    raw=(args.package/SCENE).read_bytes();meta=receipt['assets'][SCENE]
    require(len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'], 'native grouped scene differs from package receipt')
    legacy=(args.package/LEGACY_SCENE).read_bytes()
    require(len(legacy)==LEGACY_BYTES and hashlib.sha256(legacy).hexdigest()==LEGACY_SHA256, 'the published v10.7 scene was rewritten')
    old_scene=json.loads(raw)
    flight_raw=(args.package/FLIGHT_SCENE).read_bytes()
    flight_meta=receipt['assets'][FLIGHT_SCENE]
    require(len(flight_raw)==flight_meta['bytes'] and hashlib.sha256(flight_raw).hexdigest()==flight_meta['sha256'], 'flight starter source differs from packaged bytes')
    flight=json.loads(flight_raw)
    require(flight['engine']=='§wyrl§ Engine · Maker v11.2' and flight['version']==11.2, 'flying native starter file carries a stale engine version')
    require(flight['project']['maulBuilderFlight']=='hover-v1' and flight['project']['maulVisualStyle']=='glacial-v2', 'flying starter profile missing from native scene')
    require(flight['project']['maulConstruction']=='walk-v1' and flight['project']['maulSpawnProtection']=='full-pad-v1', 'flying starter lost construction safety')
    require(flight['scene']==old_scene['scene'] and flight['editor']==old_scene['editor'], 'flight pack changed 78 authored map actors or editor layers')
    require(validate_scene(flight)['actors']==78, 'flying starter must have nine sector builders and no authored towers')
    proof=validate_scene(old_scene)
    print('MAUL_FLIGHT_NATIVE_STARTER_PACKAGE_VERIFIED '+json.dumps({'source':FLIGHT_SCENE,'actors':78,'profiles':[flight['project']['maulBuilderFlight'],flight['project']['maulVisualStyle']]},sort_keys=True))
    print('MAUL_BATCH_NATIVE_PACKAGE_VERIFIED '+json.dumps(proof,sort_keys=True))


if __name__=='__main__':
    main()
