import json
import platform
from pathlib import Path


def read_os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    path = Path("/etc/os-release")

    if not path.exists():
        return result

    for line in path.read_text().splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')

    return result


def detect_platform() -> dict:
    os_release = read_os_release()

    is_umbrel = (
        Path("/opt/umbreld").exists()
        or Path("/home/umbrel/umbrel/umbrel.yaml").exists()
    )

    if is_umbrel:
        adapter = "umbrel"
    elif Path("/.dockerenv").exists():
        adapter = "docker"
    elif os_release.get("ID") == "ubuntu":
        adapter = "ubuntu"
    elif os_release.get("ID") == "debian":
        adapter = "debian"
    else:
        adapter = "unsupported"

    return {
        "success": True,
        "platform": {
            "adapter": adapter,
            "supported": adapter != "unsupported",
            "operatingSystem": os_release.get(
                "PRETTY_NAME",
                platform.system(),
            ),
            "osId": os_release.get("ID", "unknown"),
            "osVersion": os_release.get("VERSION_ID", "unknown"),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "isUmbrel": is_umbrel,
            "dockerAvailable": (
                Path("/usr/bin/docker").exists()
                or Path("/usr/local/bin/docker").exists()
            ),
        },
    }


if __name__ == "__main__":
    print(json.dumps(detect_platform(), indent=2))
