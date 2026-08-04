from __future__ import annotations

from pathlib import Path
import sys

repo = Path(sys.argv[1]).resolve()
path = repo / "bin/spi"
text = path.read_text()

# Ensure paused operations return a non-zero result from command_run while
# preserving the full operation record for inspection and resume.
old = '''    output(
        {
            "success": True,
            "safeMode": True,
            "changesApplied": False,
            "operation": result,
        }
    )
'''
new = '''    successful = result.get("status") == "simulated"

    output(
        {
            "success": successful,
            "safeMode": True,
            "changesApplied": False,
            "operation": result,
        },
        0 if successful else 1,
    )
'''
if old in text:
    text = text.replace(old, new, 1)

# Resume already emits success=True in earlier packages. Make it status-aware.
old_resume = '''    output(
        {
            "success": True,
            "safeMode": True,
            "changesApplied": False,
            "operation": result,
        }
    )
'''
if old_resume in text:
    text = text.replace(old_resume, new, 1)

path.write_text(text)
