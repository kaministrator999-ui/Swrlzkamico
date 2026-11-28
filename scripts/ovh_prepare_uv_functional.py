#!/usr/bin/env python3
"""Apply narrowly scoped UV layout delivery patch and optional isolated functional fixture."""
import sys
from pathlib import Path
root=Path('candidate-source/projects/swrlz-forge-moba/runtime')
p=root/'uv_auto_unwrap_v11_555.js'
s=p.read_text()
assert s.count('/* SE557_UNIVERSAL_UV_END */')==1
# No mutation to sealed source; this file is injected by the existing delivery transform.
s+='\n'+Path('scripts/ovh_uv_layout_v11_558.js').read_text()+'\n'
if sys.argv[1]=='qa':
    s+=Path('scripts/ovh_uv_functional_fixture_v11_558.js').read_text()+'\n'
else:
    assert sys.argv[1]=='clean'
p.write_text(s)
