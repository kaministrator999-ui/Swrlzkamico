#!/usr/bin/env python3
"""Regression checks for art/UV registration without changing a saved scene."""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
from PIL import Image

from register_concept_uv_to_native import register, REFERENCE

def main():
    assert REFERENCE.is_file(), REFERENCE
    with TemporaryDirectory() as td:
        td=Path(td)
        # Valid roundtrip using the native mesh-registered art as both inputs.
        out=td/'registered.png'
        report=register(REFERENCE,REFERENCE,out,1024)
        assert out.exists()
        assert report['resolution']==[1024,1024]
        assert report['islandIoUAfter']>=report['islandIoUBefore']
        assert not report['geometryModified'] and not report['nativeUvModified']
        arr=np.asarray(Image.open(out).convert('RGB'))
        assert arr.shape==(1024,1024,3)
        assert np.any(np.linalg.norm(arr.astype(float)-arr[0,0],axis=2)>30)
        # Unrelated artwork has no usable UV-island correspondence.
        bad=td/'wrong-atlas.png'
        Image.new('RGB',(512,512),(196,199,201)).save(bad)
        try:
            register(bad,REFERENCE,td/'should-not-exist.png',1024)
        except ValueError as exc:
            assert 'does not match native UV atlas' in str(exc)
        else:
            raise AssertionError('Unrelated artwork falsely accepted')
        assert not (td/'should-not-exist.png').exists()
    print('SE_UV_REGISTRATION_TEST_PASS')

if __name__=='__main__':
    main()
