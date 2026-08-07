#!/usr/bin/env python3
"""Generate the only gameplay changes in this E2E:E fork.

The files are downloaded by Mod Director on first launch, keeping the fork's
custom diff isolated from E2E:E's generated CurseForge manifest.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "config" / "mod-director"
PREFIX = "e2ee-extra-"

# Stable Minecraft 1.12.2 combination:
# - Railcraft 12.0.0
# - Computronics 1.6.6
# - Project Red 4.9.4.120 full module set
MODS: list[dict[str, Any]] = [
    {
        "slug": "railcraft",
        "name": "Railcraft 12.0.0",
        "project_id": 51195,
        "file_name": "railcraft-12.0.0.jar",
        "url": "https://edge.forgecdn.net/files/2687/757/railcraft-12.0.0.jar",
    },
    {
        "slug": "computronics",
        "name": "Computronics 1.6.6",
        "keyword": "computronics",
        "file_name": "Computronics-1.12.2-1.6.6.jar",
        "url": "https://files.vexatos.com/Computronics/Computronics-1.12.2-1.6.6.jar",
    },
    {
        "slug": "project-red-core",
        "name": "Project Red Core 4.9.4.120",
        "project_id": 228702,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-Base.jar",
        "url": "https://edge.forgecdn.net/files/2745/545/ProjectRed-1.12.2-4.9.4.120-Base.jar",
    },
    {
        "slug": "project-red-compat",
        "name": "Project Red Compat 4.9.4.120",
        "project_id": 229050,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-compat.jar",
        "url": "https://edge.forgecdn.net/files/2745/546/ProjectRed-1.12.2-4.9.4.120-compat.jar",
    },
    {
        "slug": "project-red-fabrication",
        "name": "Project Red Fabrication 4.9.4.120",
        "project_id": 230111,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-fabrication.jar",
        "url": "https://edge.forgecdn.net/files/2745/547/ProjectRed-1.12.2-4.9.4.120-fabrication.jar",
    },
    {
        "slug": "project-red-integration",
        "name": "Project Red Integration 4.9.4.120",
        "project_id": 229045,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-integration.jar",
        "url": "https://edge.forgecdn.net/files/2745/548/ProjectRed-1.12.2-4.9.4.120-integration.jar",
    },
    {
        "slug": "project-red-illumination",
        "name": "Project Red Illumination 4.9.4.120",
        "project_id": 229046,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-lighting.jar",
        "url": "https://edge.forgecdn.net/files/2745/549/ProjectRed-1.12.2-4.9.4.120-lighting.jar",
    },
    {
        "slug": "project-red-expansion",
        "name": "Project Red Expansion 4.9.4.120",
        "project_id": 229048,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-mechanical.jar",
        "url": "https://edge.forgecdn.net/files/2745/550/ProjectRed-1.12.2-4.9.4.120-mechanical.jar",
    },
    {
        "slug": "project-red-exploration",
        "name": "Project Red Exploration 4.9.4.120",
        "project_id": 229049,
        "file_name": "ProjectRed-1.12.2-4.9.4.120-world.jar",
        "url": "https://edge.forgecdn.net/files/2745/551/ProjectRed-1.12.2-4.9.4.120-world.jar",
    },
]


def load_manifest_project_ids() -> set[int]:
    manifest_path = ROOT / "manifest.json"
    if not manifest_path.exists():
        return set()

    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    return {
        int(entry["projectID"])
        for entry in manifest.get("files", [])
        if isinstance(entry, dict) and "projectID" in entry
    }


def upstream_text() -> str:
    """Text used to detect a future upstream Computronics addition."""
    chunks: list[str] = []

    for relative in ("manifest.json", "MODS.md"):
        path = ROOT / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))

    if TARGET.exists():
        for path in TARGET.glob("*"):
            if path.is_file() and not path.name.startswith(PREFIX):
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))

    return "\n".join(chunks).lower()


def config_payload(mod: dict[str, Any]) -> dict[str, Any]:
    return {
        "url": mod["url"],
        "follows": [mod["name"]],
        "fileName": mod["file_name"],
        "installationPolicy": {
            "continueOnFailedDownload": False,
            "name": mod["name"],
            "description": "Required mod added by the E2E:E extra-mod fork.",
        },
    }


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    manifest_ids = load_manifest_project_ids()
    source_text = upstream_text()

    generated = 0
    skipped = 0

    for mod in MODS:
        destination = TARGET / f"{PREFIX}{mod['slug']}.url.json"

        already_upstream = (
            mod.get("project_id") in manifest_ids
            if mod.get("project_id") is not None
            else mod.get("keyword", "").lower() in source_text
        )

        if already_upstream:
            destination.unlink(missing_ok=True)
            print(f"upstream already contains {mod['name']}; managed file removed")
            skipped += 1
            continue

        destination.write_text(
            json.dumps(config_payload(mod), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"generated {destination.relative_to(ROOT)}")
        generated += 1

    print(f"done: {generated} generated, {skipped} supplied by upstream")


if __name__ == "__main__":
    main()
