import platform
from adapters.model import require_adapter

def required_capabilities(manifest):
    req = manifest.get("requirements", {})
    result = set(req.get("capabilities", []))
    if req.get("persistentStorage") is True:
        result.add("persistent-storage")
    if req.get("database"):
        result.add(str(req["database"]))
    return sorted(result)

def validate_product(manifest, adapter_id: str):
    adapter = require_adapter(adapter_id)
    req = manifest.get("requirements", {})
    arch = platform.machine()
    supported_adapters = req.get("platformAdapters", [])
    supported_architectures = req.get("architectures", [])
    adapter_valid = not supported_adapters or adapter_id in supported_adapters
    architecture_valid = not supported_architectures or arch in supported_architectures
    capability_result = adapter.validate(required_capabilities(manifest))
    compatible = adapter_valid and architecture_valid and capability_result["compatible"]
    return {
        "compatible": compatible,
        "product": manifest["product"],
        "adapter": adapter.to_dict(),
        "architecture": {"current": arch, "supported": supported_architectures, "valid": architecture_valid},
        "adapterDeclaration": {"supported": supported_adapters, "valid": adapter_valid},
        "capabilities": capability_result,
    }
