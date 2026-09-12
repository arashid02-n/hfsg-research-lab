"""Portable HFSG Core resolution and pre-flight helpers.

No developer-specific path is hard-coded anywhere in the Lab. The frozen HFSG
Core is located at runtime using the following priority (first match wins):

    1. Bundled / adjacent approved Core  (<lab>/hfsg_core or <lab>/core)
    2. Environment variable               HFSG_CORE_DIR (also HFSG_CORE)
    3. Local configuration file           <lab>/hfsg_core.config
    4. User-selectable Core directory     (persisted via save_core_dir)

The Core itself is NOT distributed with the Lab (see IP_AND_DISTRIBUTION_
BOUNDARY.md): the Research Lab repository and Academic package ship only the
Lab. The approved Core is supplied separately by the Project Owner and dropped
into the package's ``hfsg_core/`` folder, pointed to via an environment
variable, or selected once in the About / System Information page.

If no Core is resolved, ``resolve_core_dir()`` returns ``None`` and the Lab
surfaces a friendly "HFSG Core not found." message instead of a traceback.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

LAB_ROOT = Path(__file__).resolve().parents[1]

ENV_VARS = ("HFSG_CORE_DIR", "HFSG_CORE")
CONFIG_FILENAME = "hfsg_core.config"
BUNDLED_DIRS = ("hfsg_core", "core")

# Both markers must exist for a directory to be treated as an approved Core.
CORE_MARKERS = ("src/hfsg/__init__.py", "config/base.yaml")


class CoreNotFoundError(RuntimeError):
    """Raised when no usable HFSG Core could be resolved."""


def is_core_dir(path: Path | str) -> bool:
    p = Path(path)
    return all((p / marker).is_file() for marker in CORE_MARKERS)


def _bundled_candidates() -> List[Path]:
    candidates: List[Path] = []
    for name in BUNDLED_DIRS:
        candidates.append(LAB_ROOT / name)
        candidates.append(Path.cwd() / name)
    return candidates


def core_config_path() -> Path:
    return LAB_ROOT / CONFIG_FILENAME


def _read_config_file() -> Optional[Path]:
    path = core_config_path()
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        candidate = Path(line)
        if is_core_dir(candidate):
            return candidate
    return None


def resolve_core_dir() -> Optional[Path]:
    """Return the resolved Core directory, or None if none is available."""
    for candidate in _bundled_candidates():
        if is_core_dir(candidate):
            return candidate.resolve()

    for var in ENV_VARS:
        value = os.environ.get(var)
        if value:
            candidate = Path(value)
            if is_core_dir(candidate):
                return candidate.resolve()

    configured = _read_config_file()
    if configured is not None:
        return configured.resolve()

    return None


def save_core_dir(path: Path | str) -> Path:
    """Validate a Core directory and persist it to the local config file."""
    candidate = Path(path)
    if not is_core_dir(candidate):
        raise CoreNotFoundError(
            f"Not an HFSG Core directory (expected src/hfsg/__init__.py and "
            f"config/base.yaml): {candidate}"
        )
    core_config_path().write_text(
        str(candidate.resolve()) + "\n", encoding="utf-8"
    )
    return candidate.resolve()


def core_src_dir() -> Path:
    core = resolve_core_dir()
    if core is None:
        raise CoreNotFoundError("HFSG Core not found.")
    return core / "src"


def core_config_file() -> Path:
    core = resolve_core_dir()
    if core is None:
        raise CoreNotFoundError("HFSG Core not found.")
    return core / "config" / "base.yaml"


def core_released_manifest() -> Optional[Path]:
    core = resolve_core_dir()
    if core is None:
        return None
    manifest = core / "data" / "output" / "step9" / "dataset_manifest.json"
    return manifest if manifest.is_file() else None
