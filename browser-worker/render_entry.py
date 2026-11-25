import runpy,sys
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root))
runpy.run_path(str(root/"render.py"),run_name="__main__")
