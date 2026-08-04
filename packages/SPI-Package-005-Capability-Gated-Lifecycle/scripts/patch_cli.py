from __future__ import annotations

from pathlib import Path
import sys

repo = Path(sys.argv[1]).resolve()
spi = repo / "bin" / "spi"
text = spi.read_text()

if "from lifecycle.preflight import validate_lifecycle_plan" not in text:
    text = text.replace(
        "from lifecycle.executor import LifecycleExecutor\n",
        "from lifecycle.executor import LifecycleExecutor\n"
        "from lifecycle.preflight import validate_lifecycle_plan\n",
    )

function = '''
def command_plan_check(
    product_id: str,
    action: str = "install",
) -> None:
    manifest = load_product(product_id)
    adapter_id = detect_platform()["platform"]["adapter"]

    validation = validate_lifecycle_plan(
        manifest=manifest,
        action=action,
        adapter_id=adapter_id,
    )

    output(
        {
            "success": validation["compatible"],
            "safeMode": True,
            "changesApplied": False,
            "validation": validation,
        },
        0 if validation["compatible"] else 1,
    )


'''

marker = "\ndef command_doctor() -> None:\n"
if "def command_plan_check(" not in text:
    if marker not in text:
        raise SystemExit("Could not locate command_doctor")
    text = text.replace(marker, "\n" + function + "def command_doctor() -> None:\n")

if "spi plan-check <product-id>" not in text:
    text = text.replace(
        "  spi validate <product-id>\n",
        "  spi validate <product-id>\n"
        "  spi plan-check <product-id> [install|repair|upgrade]\n",
    )

dispatch_marker = '    elif command == "plan" and len(args) >= 2:\n'
if 'elif command == "plan-check"' not in text:
    if dispatch_marker not in text:
        raise SystemExit("Could not locate plan dispatch")
    text = text.replace(
        dispatch_marker,
        '    elif command == "plan-check" and len(args) >= 2:\n'
        '        command_plan_check(\n'
        '            args[1],\n'
        '            args[2] if len(args) >= 3 else "install",\n'
        '        )\n\n'
        + dispatch_marker,
    )

run_anchor = "    store = StateStore(ROOT)\n    registry = build_default_registry()\n"
run_gate = '''    preflight = validate_lifecycle_plan(
        manifest=manifest,
        action=action,
        adapter_id=detected["adapter"],
    )

    if not preflight["compatible"]:
        output(
            {
                "success": False,
                "safeMode": True,
                "changesApplied": False,
                "blocked": True,
                "error": "Lifecycle plan failed capability validation.",
                "validation": preflight,
            },
            1,
        )

    store = StateStore(ROOT)
    registry = build_default_registry()
'''
if "Lifecycle plan failed capability validation" not in text:
    if run_anchor not in text:
        raise SystemExit("Could not locate command_run setup")
    text = text.replace(run_anchor, run_gate, 1)

spi.write_text(text)
