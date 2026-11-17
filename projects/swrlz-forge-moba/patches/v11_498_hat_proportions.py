"""§E v11.498 — reference-aware, single-surface Sorting Hat proportion pass.
No project import or extra mesh: adjust v11.497 vertex deformation directly.
"""
import json
from pathlib import Path
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_498_HAT_PROPORTIONS'
def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.498',label,n))
    return s.replace(old,new,1)
def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT' in html
    # Remove computed but never used intermediate ring centroids.
    html=once(html,
       'const STRIDE=97, ROWS=81, N=96, means=[];\nfor(let row=0;row<ROWS;row++){\nlet x=0,z=0;\nfor(let j=0;j<N;j++){const k=(row*STRIDE+j)*3;x+=before[k];z+=before[k+2];}\nmeans.push([x/N,z/N]);\n}',
       'const STRIDE=97, ROWS=81, N=96;', 'unused centroids')
    html=once(html,'const back=Math.pow(Math.max(0,-s),3);\n','', 'unused rear falloff')
    # Compress vertical crown height without changing UVs or index topology.
    html=once(html,'coords[k]=Math.round((x+dx)*1e5)/1e5;',
       'dy-=.22*Math.max(0,y-.22);\ncoords[k]=Math.round((x+dx)*1e5)/1e5;', 'physical height proportion')
    # Use a restrained hat point, not a long laterally stretched spike.
    html=once(html,'dx += .68*lean-.075*gauss(y,3.32,.30);',
       'dx += .24*lean-.035*gauss(y,3.32,.30);', 'crown tip lean')
    html=once(html,'dz += .10*lean-.065*Math.sin(theta+1.0)*gauss(y,3.18,.40);',
       'dz += .04*lean-.025*Math.sin(theta+1.0)*gauss(y,3.18,.40);', 'tip depth curl')
    html=once(html,'dy -= .25*smooth(3.22,4.08,y);',
       'dy -= .10*smooth(3.22,4.08,y);', 'tip natural compression')
    html=once(html,'dx += .68*smooth(2.45,4.08,y)-.075*gauss(y,3.32,.30);',
       'dx += .24*smooth(2.45,4.08,y)-.035*gauss(y,3.32,.30);','liner lean')
    html=once(html,'dz += .10*smooth(2.45,4.08,y);',
       'dz += .04*smooth(2.45,4.08,y);','liner curl')
    html=once(html,'coords[apex]=Math.round((before[apex]+.68)*1e5)/1e5;',
       'coords[apex]=Math.round((before[apex]+.24)*1e5)/1e5;', 'apex x')
    html=once(html,'coords[apex+1]=Math.round((before[apex+1]-.25)*1e5)/1e5;',
       'coords[apex+1]=Math.round((before[apex+1]-.10-.22*(before[apex+1]-.22))*1e5)/1e5;', 'apex y')
    html=once(html,'coords[apex+2]=Math.round((before[apex+2]+.10)*1e5)/1e5;',
       'coords[apex+2]=Math.round((before[apex+2]+.04)*1e5)/1e5;', 'apex z')
    html=once(html,'coords[liner]=Math.round((before[liner]+.68*smooth(2.45,4.08,before[liner+1])\n-.075*gauss(before[liner+1],3.32,.30))*1e5)/1e5;',
       'coords[liner]=Math.round((before[liner]+.24*smooth(2.45,4.08,before[liner+1])\n-.035*gauss(before[liner+1],3.32,.30))*1e5)/1e5;\ncoords[liner+1]=Math.round((before[liner+1]-.22*(before[liner+1]-.22))*1e5)/1e5;',
       'inner cap closure')
    html=once(html,'coords[liner+2]=Math.round((before[liner+2]+.10*smooth(2.45,4.08,before[liner+1]))*1e5)/1e5;',
       'coords[liner+2]=Math.round((before[liner+2]+.04*smooth(2.45,4.08,before[liner+1]))*1e5)/1e5;', 'inner cap curl')
    # Face contours: stronger brow and eye recession. Avoid a featureless slit.
    html=once(html,'+.027*brow-.026*eye-.022*faceMouth+.030*mouthCorner;',
       '+.061*brow-.051*eye-.052*faceMouth+.034*mouthCorner;', 'face relief')
    html=once(html,'dy += preserveFace*(.022*wave*gauss(y,2.30,.80));',
       'dy += preserveFace*(.022*wave*gauss(y,2.30,.80))-.04*mouthCorner;', 'drooping mouth corners')
    # Instead of regularly stacked rubbery rings, retain broad directional folds.
    for old,new in (('.090*gauss(band1,0,.080)','.063*gauss(band1,0,.080)'),
                    ('+.075*gauss(band2,0,.089)','+.059*gauss(band2,0,.089)'),
                    ('+.115*gauss(band3,0,.105)','+.086*gauss(band3,0,.105)'),
                    ('+.071*gauss(band4,0,.092)','+.055*gauss(band4,0,.092)')):
        html=once(html,old,new,'fold depth')
    html=once(html,'const ripple=.082*Math.sin(3*theta+.55)+.062*Math.sin(5*theta-1.35)\n+.045*Math.sin(2*theta+1.7);',
       'const ripple=.023*Math.sin(3*theta+.55)+.019*Math.sin(5*theta-1.35)\n+.011*Math.sin(2*theta+1.7);', 'brim waves')
    html=once(html,'(.035*Math.sin(4*theta+.8)+.018*Math.sin(9*theta))',
       '(.015*Math.sin(4*theta+.8)+.008*Math.sin(9*theta))', 'brim radial x')
    html=once(html,'(.035*Math.sin(4*theta+.8)+.018*Math.sin(9*theta))',
       '(.015*Math.sin(4*theta+.8)+.008*Math.sin(9*theta))', 'brim radial z')
    # Retain original project registration, close surface, source mesh and UVs.
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT',MARKER),
      ('ENGINE · MAKER v11.497','ENGINE · MAKER v11.498'),
      ('v11.497 · a second sculpted Sorting Hat starter','v11.498 · compact Sorting Hat proportions'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.497'","window.SWRLZ_FORGE_BUILD={version:'v11.498'"),
      ('<title>§wyrl§ Engine · Maker v11.497</title>',
       '<title>§wyrl§ Engine · Maker v11.498</title>')
    ): html=once(html,old,new,'runtime version')
    old=" source.engine='§wyrl§ Engine · Maker v11.497';source.version=11.497;"
    assert html.count(old)==5,html.count(old)
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.498';source.version=11.498;")
    key='const SE_RELEASE_NOTES='
    start=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.497']
    notes['history'].insert(0,{'version':'v11.497','changes':notes.get('changes',[])})
    notes.update(version='v11.498',date='2026-11-17',
      title='Sorting Hat sculpt proportions and face depth',
      changes=['Adjusted the alternate one-mesh hat: shorter crown, restrained tip bend, deeper face contours, softer cloth folds and brim waves. Original starter and UVs are untouched.'])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[start+length:]
