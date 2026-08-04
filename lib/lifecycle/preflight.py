from __future__ import annotations

from typing import Any

from adapters.model import require_adapter
from core.compatibility import validate_product
from plugins.capabilities import plugin_required_capabilities


def validate_lifecycle_plan(
    *,
    manifest: dict[str, Any],
    action: str,
    adapter_id: str,
) -> dict[str, Any]:
    lifecycle = manifest.get("lifecycle", {})

    if action not in lifecycle:
        return {
            "compatible": False,
            "blocked": True,
            "reason": "unknown-lifecycle-action",
            "action": action,
            "steps": [],
            "missingCapabilities": [],
            "explicitlyDeniedCapabilities": [],
        }

    product_validation = validate_product(manifest, adapter_id)
    adapter = require_adapter(adapter_id)
    steps: list[dict[str, Any]] = []

    product_capabilities = product_validation["capabilities"]

    missing: set[str] = set(
        product_capabilities["missingCapabilities"]
    )
    denied: set[str] = set(
        product_capabilities["explicitlyDeniedCapabilities"]
    )

    for number, plugin_key in enumerate(lifecycle[action], start=1):
        required = plugin_required_capabilities(plugin_key)
        result = adapter.validate(required)
        missing.update(result["missingCapabilities"])
        denied.update(result["explicitlyDeniedCapabilities"])
        steps.append({
            "step": number,
            "plugin": plugin_key,
            "compatible": result["compatible"],
            "requiredCapabilities": required,
            "missingCapabilities": result["missingCapabilities"],
            "explicitlyDeniedCapabilities": result["explicitlyDeniedCapabilities"],
        })

    compatible = product_validation["compatible"] and all(
        step["compatible"] for step in steps
    )

    return {
        "compatible": compatible,
        "blocked": not compatible,
        "action": action,
        "adapter": adapter_id,
        "product": manifest["product"],
        "productValidation": product_validation,
        "steps": steps,
        "missingCapabilities": sorted(missing),
        "explicitlyDeniedCapabilities": sorted(denied),
    }
