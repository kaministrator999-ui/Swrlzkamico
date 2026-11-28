#!/usr/bin/env python3
"""Bundle the exact renderer version into the existing OVH runtime module.
No production writes. The five-file runtime overlay and sealed source stay intact.
"""
import hashlib,json,subprocess,sys,tempfile,shutil
from pathlib import Path
root=Path('.deploy/engine-runtime/payload')
manifest=root/'manifest.json'
m=json.loads(manifest.read_text())
rel='swrlz-engine-v11.552.js'
dist=Path(sys.argv[3])
receipt=json.loads((dist/'SOURCE.json').read_text())
assert receipt['finalSha256']==m['sealedSourceSha256']
assert hashlib.sha256((dist/rel).read_bytes()).hexdigest()==receipt['staticDelivery']['moduleSha256']
assert hashlib.sha256((dist/'modeler.html').read_bytes()).hexdigest()==receipt['staticDelivery']['modelerSha256']
assert hashlib.sha256((dist/'index.html').read_bytes()).hexdigest()==receipt['staticDelivery']['indexSha256']
for name in m['assets']:
    src=dist/name
    data=src.read_bytes()
    if name.startswith('assets/'):
        assert hashlib.sha256(data).hexdigest()==receipt['lscmModuleDelivery']['files'][src.name]['sha256']
    assert len(data)<16*1024*1024
    shutil.copyfile(src,root/'overlay'/name)
    m['assets'][name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
p=root/'overlay'/rel
original=p.read_bytes()
assert hashlib.sha256(original).hexdigest()==m['assets'][rel]['sha256']
assert len(original)==m['assets'][rel]['bytes']
assert m['assets'][rel]['sha256']==receipt['staticDelivery']['moduleSha256'],'Unexpected candidate build'
s=original.decode('utf8')
urls={
'https://cdn.jsdelivr.net/npm/three@0.169.0/+esm':'three',
'https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/OrbitControls.js/+esm':'three/examples/jsm/controls/OrbitControls.js',
'https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/controls/TransformControls.js/+esm':'three/examples/jsm/controls/TransformControls.js'
}
for url,local in urls.items():
    old='import("'+url+'")'
    assert s.count(old)==1,url
    s=s.replace(old,'import("'+local+'")',1)
s=s.replace('Internet required for Three.js CDN.','Bundled renderer initialization failed.')
with tempfile.TemporaryDirectory(prefix='swrlz-renderer-') as d:
    d=Path(d)
    (d/'package.json').write_text('{"private":true,"type":"module"}')
    subprocess.run(['npm','install','--ignore-scripts','--no-audit','--no-fund','--save-exact','three@0.169.0','esbuild@0.25.12'],cwd=d,check=True,timeout=120)
    lock=json.loads((d/'package-lock.json').read_text())
    assert lock['packages']['node_modules/three']['version']=='0.169.0'
    assert lock['packages']['node_modules/esbuild']['version']=='0.25.12'
    src=d/'engine.mjs';out=d/'engine-bundled.mjs'
    src.write_text(s)
    subprocess.run([str(d/'node_modules/.bin/esbuild'),str(src),'--bundle','--format=esm','--platform=browser','--target=es2022','--minify-whitespace','--legal-comments=inline','--outfile='+str(out),'--metafile='+str(d/'meta.json')],cwd=d,check=True,timeout=120)
    meta=json.loads((d/'meta.json').read_text())
    assert any('three.module.js' in x for x in meta['inputs'])
    assert any('OrbitControls.js' in x for x in meta['inputs'])
    assert any('TransformControls.js' in x for x in meta['inputs'])
    license=(d/'node_modules/three/LICENSE').read_text()
    assert 'MIT License' in license and '*/' not in license
    data=('/* Bundled Three.js 0.169.0 license:\n'+license+'\n*/\n').encode()+out.read_bytes()
    out.write_bytes(data)
    subprocess.run(['node','--check',str(out)],check=True)
    bundle={'version':'0.169.0','threeIntegrity':lock['packages']['node_modules/three']['integrity'],'esbuildVersion':'0.25.12','previousModuleSha256':m['assets'][rel]['sha256'],'startupImportsBundled':list(urls)}
assert all(('import("'+u+'")').encode() not in data for u in urls)
assert len(data)<16*1024*1024
p.write_bytes(data)
m['assets'][rel]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
m['rendererBundle']=bundle
m['previousCandidateBrowserReceipt']=m.pop('browserReceipt')
m['uvSourceCommit']='d49eec1d29fc2cc3202ce497111147fcaa05fb37'
m['browserReceipt']={'realStarterCard':False,'errors':['Awaiting OVH browser verification']}
m['sourceCommit']=sys.argv[1]
m['browserRun']=sys.argv[2]
manifest.write_text(json.dumps(m,indent=2)+'\n')
print('SWRLZ_LOCAL_RENDERER_CANDIDATE_READY',json.dumps(m['assets'][rel]),flush=True)
