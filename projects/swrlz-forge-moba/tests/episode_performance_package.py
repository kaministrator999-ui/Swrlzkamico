#!/usr/bin/env python3
"""Validate the native animated episode and every preserved published asset."""
import argparse
import hashlib
import json
import math
from pathlib import Path

SCENE = 'scenes/ghosts-in-different-forms-ep01-performance.swyrl.json'
LEGACY_SCENE = 'scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json'
PATCH = 'patches/v11_62_mobile_adaptive.py'
ACTIONS = {'greet', 'reach', 'brace', 'cast', 'write', 'step', 'hover', 'recover'}
EFFECTS = {'page', 'burst', 'ink', 'portal'}
PRESERVED_ASSETS = {'assets/anime/cathedral.png': {'bytes': 3237216,
                                'sha256': '69a155ac1cbf004e6550c173e322e8fcaa59aac8c7f5487cb0dcd85d545ac88d'},
 'assets/anime/foreground.png': {'bytes': 339866,
                                 'sha256': 'd1795b3c23a7d2466ca8198004a1578d5c6e910dc093ebf36a1be7debd8a3856'},
 'assets/anime/kami-full-staff.png': {'bytes': 539698,
                                      'sha256': 'b487b5861a649bc2a92998251b832d9466500d87ecff34babd1ed4cdfd9a6393'},
 'assets/anime/kami-grip-layers.png': {'bytes': 685008,
                                       'sha256': 'bfa6d69ee88a67956d5065261ae3736050bb00b679d3b047de57f5d390e9ed28'},
 'assets/anime/kami-rig.png': {'bytes': 1013417,
                               'sha256': '0c3dd080cfcd38648fb498202bd22b127596b9e8863381e8472774ec555d543b'},
 'assets/anime/kami.png': {'bytes': 3248787,
                           'sha256': '09a206911ba27447b324b331e57cb0f6326d89abaabf9c5d3912dfa4b035bbcd'},
 'assets/anime/mage-faces-painted.png': {'bytes': 1910086,
                                         'sha256': '43ed49df9f2e2b7239a6f9f03d7c601c19b99278f0c4c8a511f8914eb215d024'},
 'assets/anime/scenery-parts.png': {'bytes': 1674349,
                                    'sha256': '315097f6210248ec59355c3579024617a847530b2c803fa3129d56507d963f41'},
 'assets/anime/swyrlz-rig.png': {'bytes': 1129785,
                                 'sha256': '1834822cd48362a387cef255d1c6598f4eaa01265349e37a0699cd5c15daf285'},
 'assets/anime/swyrlz.png': {'bytes': 2680403,
                             'sha256': '81a386cf09f14fc52e4998898242614a0c64e6c0982504dcd27b35b856a1286e'},
 'assets/anime/workshop.png': {'bytes': 863104,
                               'sha256': '08b1b037eeb3fa9cfd7f9e51a9e06545b7bf74688f70dff5629994fe06668198'},
 'episodes/ghosts-in-different-forms-ep01.html': {'bytes': 24568,
                                                  'sha256': '5bd4b1a2a9f28450e31a66c0959b238879c361b3536819e8993784d7a195e8a5'},
 'scenes/ghosts-in-different-forms-ep01-depth.swyrl.json': {'bytes': 404502,
                                                            'sha256': '2dc9ef80164c10ce48c3c35dad320e1f0295ea885d97756ff250051925e9471c'},
 'scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json': {'bytes': 442304,
                                                                 'sha256': '0f3a3dd1b748c3bac0cfdd147078c4ffdb911689498408d7a7aca387d543a44e'},
 'scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json': {'bytes': 442209,
                                                                   'sha256': 'c4e1897297360f17d929870595b183335717db0d8d607973661f3c18aa508b7c'},
 'scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json': {'bytes': 413579,
                                                                 'sha256': '5ca8bf9c6d8e8b737637de4d7023f8e552658c1217bd884fb645fe18053749ff'},
 'scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json': {'bytes': 259437,
                                                             'sha256': '8bf365c03e331e1ba6f4843592388285f81b6682eecf76a51081d8fbb206f0d8'},
 'scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json': {'bytes': 434408,
                                                              'sha256': 'd5b655ea7da9245cba9846e41db081ec4e44188c19660ac5f5d5c23e69e0f0ec'},
 'scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json': {'bytes': 442187,
                                                                 'sha256': '88a96437ffdcc675c8b5e7ca1d48220e1764dd00f8b0388ca62e22742ba5214b'},
 'scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json': {'bytes': 140812,
                                                                'sha256': '7e19e17d6f3a38507efdff46fd76a92dfa631814b7e79e4f487b52ae1aa2793a'},
 'scenes/ghosts-in-different-forms-ep01.swyrl.json': {'bytes': 100940,
                                                      'sha256': '381e17522948483a0f588c05f4b30b34952dd545ba4600deaa81d2b5d28e66ec'},
 'scenes/maul-frostveil-classic.swyrl.json': {'bytes': 108598,
                                              'sha256': '858552d9d8a9bdad89f445e6747641b34d9ac7c69c2e207e294ce83dd94718a2'},
 'scenes/maul-frostveil-groups.swyrl.json': {'bytes': 104646,
                                             'sha256': 'ec14513f38fabbb3a465b802b5c27d9701900c1d3d57652822339abf4d9e821d'},
 'scenes/maul-frostveil.swyrl.json': {'bytes': 110316,
                                      'sha256': 'f85a98463248d368321954ad1e407963f279fe28c717886a15b0cc1c46a7fc93'},
 'scenes/sheep-tag-meadow.swyrl.json': {'bytes': 86684,
                                        'sha256': '1785d35e0bb6bffb538aa4d0ef988aad4a0a4e17a33aff6f0712ee3830f39ae2'},
 'scenes/sheep-tag-moonbell-archive.swyrl.json': {'bytes': 121466,
                                                  'sha256': '4526290f2232081811e2762d980cd2cf8f52a28c41431f813ccaca15008c2c15'}}


def require(condition, message):
    if not condition:
        raise AssertionError('Episode performance package: ' + message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def finite_values(value):
    if isinstance(value, dict):
        return all(finite_values(item) for item in value.values())
    if isinstance(value, list):
        return all(finite_values(item) for item in value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return math.isfinite(value)
    return True


def validate_scene(data, legacy=None):
    project = data['project']; actors = data['scene']['actors']; layers = data['editor']['layers']
    require(data['engine'] == '§wyrl§ Engine · Maker v10.9' and data['version'] == 10.9, 'expected a current native Save Project export')
    require(project['template'] == 'blank' and project['canonicalId'] == 'ghosts-different-forms-ep01' and project['kind'] == 'anime-production-set', 'wrong native starter identity')
    require(len(actors) == 70 and len({a['id'] for a in actors}) == 70, 'expected 70 distinct native actors')
    require(len(layers) == 11 and len({l['id'] for l in layers}) == 11, 'expected 11 distinct editor layers')
    layer_ids = {layer['id'] for layer in layers}
    require(all(any(layer['id'] in actor.get('editorLayerIds', []) for actor in actors) for layer in layers), 'empty native layer')
    for actor in actors:
        require(set(actor.get('editorLayerIds', [])) <= layer_ids, 'unknown actor layer')
        require(bool(actor.get('editorLayerIds')) or actor['id'] in ('a_ep_ground', 'a_ep0061'), 'missing actor layer')
        for key in ('position', 'rotation', 'scale'):
            require(len(actor[key]) == 3 and all(finite(v) for v in actor[key]), 'invalid actor '+key)
        require(all(v > 0 for v in actor['scale']), 'nonpositive native actor scale')
    timeline = project['animeTimeline']; beats = timeline['beats']; tracks = timeline['tracks']
    require(timeline['schema'] == 'anime-timeline-v1' and timeline['duration'] == 134, 'wrong episode duration/schema')
    require(len(beats) == 8 and beats[0]['time'] == 0 and beats[-1]['end'] == 134, 'expected eight full-episode story beats')
    previous = 0; dialogue = 0
    for beat in beats:
        require(beat['time'] == previous and finite(beat['time']) and finite(beat['end']) and beat['end'] > beat['time'], 'story beats leave a gap or overlap')
        require(isinstance(beat['title'], str) and beat['title'].strip(), 'untitled story beat')
        previous = beat['end']; last_cue = -1
        require(len(beat.get('cues', [])) >= 2, 'story beat lacks dialogue/action captions')
        for cue in beat['cues']:
            require(finite(cue['time']) and beat['time'] <= cue['time'] < beat['end'] and cue['time'] > last_cue, 'invalid or unordered dialogue cue')
            require(isinstance(cue['text'], str) and cue['text'].strip(), 'empty dialogue cue')
            last_cue = cue['time']; dialogue += 1
    require(len(tracks) == 9 and 'camera' in tracks and {'kami', 'swyrlz'} <= set(tracks), 'expected nine character/stage/camera tracks')
    for name, keys in tracks.items():
        require(len(keys) >= 2 and keys[0]['time'] == 0 and keys[-1]['time'] == 134, 'track does not cover the episode: '+name)
        require(all(finite_values(key) and finite(key['time']) for key in keys), 'nonfinite track key: '+name)
        require(all(a['time'] < b['time'] for a, b in zip(keys, keys[1:])), 'unordered or duplicate track keys: '+name)
    stage_keys = sum(len(keys) for keys in tracks.values())
    rig_keys = sum(len(model['face']) + sum(len(keys) for keys in model['joints'].values()) for model in project['animeRigs']['characters'].values())
    scenery_keys = sum(len(model['keys']) for model in project['animeScenery']['objects'].values())
    require((stage_keys, rig_keys, scenery_keys) == (175, 468, 383), 'saved native stage/character/scenery key counts changed')
    require(finite_values(project['animeRigs']) and finite_values(project['animeScenery']), 'nonfinite character/scenery keys')
    performance = project['animePerformance']
    require(performance['schema'] == 'anime-performance-v1' and performance['enabled'] is True, 'missing enabled native story actions')
    require(performance.get('limitDialogue') is True and finite(performance['maxDialogueSeconds']) and 0 < performance['maxDialogueSeconds'] <= 4.5, 'dialogue lacks a timed listening pause')
    clips = performance['clips']
    require(len(clips) == 36 and len({clip['id'] for clip in clips}) == len(clips), 'missing or duplicate saved story actions')
    require({clip['character'] for clip in clips} == {'kami', 'swyrlz'}, 'both mages need saved action clips')
    require({clip['action'] for clip in clips} == ACTIONS, 'starter lacks a story action kind')
    for clip in clips:
        require(clip['character'] in ('kami', 'swyrlz') and clip['action'] in ACTIONS and clip['side'] in ('left', 'right'), 'invalid action target/type/side')
        require(all(finite(clip[key]) for key in ('time', 'duration', 'strength')), 'nonfinite action timing or strength')
        require(0 <= clip['time'] < 134 and clip['duration'] > 0 and clip['time'] + clip['duration'] <= 134 and clip['strength'] > 0, 'action falls outside the story')
        require(isinstance(clip.get('label'), str) and clip['label'].strip(), 'unnamed story action')
    effects = project['animeStoryEffects']
    require(effects['schema'] == 'anime-story-effects-v1' and effects['enabled'] is True, 'missing enabled native story effects')
    cues = effects['cues']
    require(len(cues) == 11 and len({cue['id'] for cue in cues}) == len(cues), 'missing or duplicate saved story effects')
    require({cue['effect'] for cue in cues} == EFFECTS, 'expected page, burst, ink and portal effects')
    for cue in cues:
        require(all(finite(cue[key]) for key in ('time', 'duration', 'strength', 'x', 'y', 'z', 'width', 'height', 'rotation')), 'nonfinite effect event')
        require(0 <= cue['time'] < 134 and cue['duration'] > 0 and cue['time'] + cue['duration'] <= 134 and cue['strength'] > 0 and cue['width'] > 0 and cue['height'] > 0, 'invalid effect extent/timing')
        require(isinstance(cue.get('label'), str) and cue['label'].strip(), 'unnamed story effect')
    require(project['animeEmergence']['duration'] == 12 and project['animeEmergence']['enabled'] is True, 'book opening changed')
    require(project['animeRigs']['characters']['kami']['staffArt'] == 'painted-full-v1', 'full-length staff artwork lost')
    if legacy is not None:
        require(actors == legacy['scene']['actors'], 'published character/scenery actor definitions changed')
        require(layers == legacy['editor']['layers'], 'published editor layer definitions changed')
        for key in ('animePopUp', 'animeSockets', 'animeEmergence', 'animeRelief'):
            require(project[key] == legacy['project'][key], 'published fitting/depth/socket settings changed: '+key)
        for character in ('kami', 'swyrlz'):
            current = {k:v for k,v in project['animeRigs']['characters'][character].items() if k not in ('joints', 'face')}
            previous = {k:v for k,v in legacy['project']['animeRigs']['characters'][character].items() if k not in ('joints', 'face')}
            require(current == previous, 'published rig/rest/full-staff configuration changed: '+character)
    return {'actors':70, 'layers':11, 'beats':8, 'duration':134, 'tracks':9,
            'stageKeys':stage_keys, 'rigKeys':rig_keys, 'sceneryKeys':scenery_keys,
            'dialogueCues':dialogue, 'actions':len(clips), 'actionKinds':sorted(ACTIONS),
            'effects':len(cues), 'effectKinds':sorted(EFFECTS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    args = parser.parse_args(); receipt = json.loads((args.package/'SOURCE.json').read_text())
    require(receipt['sourceVersion'] == '§wyrl§ Engine v11.62', 'wrong source version')
    require(len(receipt['patches'])==94 and receipt['patches'][-1] == PATCH, 'wrong governed patch chain')
    require(set(receipt['assets']) == set(PRESERVED_ASSETS) | {SCENE, 'scenes/maul-frostveil-flight.swyrl.json', 'scenes/model-atelier-prism-jester.swyrl.json', 'scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json', 'scenes/model-atelier-prism-jester-festival-v11-5.swyrl.json','scenes/model-atelier-prism-jester-festival-v11-6.swyrl.json','scenes/model-atelier-prism-jester-festival-v11-7.swyrl.json','scenes/model-atelier-prism-jester-festival-v11-8.swyrl.json','scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json','scenes/model-atelier-festival-reference-v11-13.swyrl.json','scenes/model-atelier-festival-refined-v11-14.swyrl.json','scenes/model-atelier-festival-surface-v11-15.swyrl.json','scenes/model-atelier-festival-detail-v11-16.swyrl.json','scenes/model-atelier-festival-hd-v11-17.swyrl.json','scenes/model-atelier-festival-reference-v11-18.swyrl.json','scenes/model-atelier-festival-polish-v11-19.swyrl.json', 'scenes/model-atelier-festival-anatomy-v11-20.swyrl.json'}, 'wrong asset set or missing preserved media')
    for path, expected in PRESERVED_ASSETS.items():
        raw = (args.package/path).read_bytes(); meta = receipt['assets'][path]
        require(meta == expected and len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], 'published v10.8 asset was rewritten: '+path)
    raw = (args.package/SCENE).read_bytes(); meta = receipt['assets'][SCENE]
    require(len(raw) == meta['bytes'] and hashlib.sha256(raw).hexdigest() == meta['sha256'], 'native performance export differs from SOURCE receipt')
    legacy = json.loads((args.package/LEGACY_SCENE).read_text())
    proof = validate_scene(json.loads(raw), legacy)
    print('EPISODE_PERFORMANCE_NATIVE_PACKAGE_VERIFIED '+json.dumps(proof, sort_keys=True))


if __name__ == '__main__':
    main()
