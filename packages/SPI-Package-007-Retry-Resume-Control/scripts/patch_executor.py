from pathlib import Path
import shutil
import sys
repo = Path(sys.argv[1]).resolve()
source = Path(__file__).resolve().parents[1] / 'payload/lib/lifecycle/executor.py'
shutil.copy2(source, repo / 'lib/lifecycle/executor.py')
