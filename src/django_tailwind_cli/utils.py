"""
Utility functions.

This module contains utility functions to read the configuration, download the CLI and determine
the various paths.
"""

import platform
import shutil
import ssl
import urllib.request
from pathlib import Path
from typing import Dict, Union

import certifi
from django.conf import settings

DEFAULT_TAILWIND_VERSION = "3.3.1"


def get_config() -> Dict[str, str]:
    """Extract configuration from settings."""
    return {
        "TAILWIND_VERSION": getattr(settings, "TAILWIND_VERSION", DEFAULT_TAILWIND_VERSION),
        "TAILWIND_CLI_PATH": getattr(settings, "TAILWIND_CLI_PATH", "~/.local/bin/"),
        "TAILWIND_THEME_APP": getattr(settings, "TAILWIND_THEME_APP", "theme"),
        "TAILWIND_SRC_CSS": getattr(settings, "TAILWIND_SRC_CSS", "src/styles.css"),
        "TAILWIND_DIST_CSS": getattr(settings, "TAILWIND_DIST_CSS", "css/styles.css"),
    }


def get_download_url() -> str:
    """Build download url for the Tailwind CSS CLI."""
    config = get_config()
    version = config["TAILWIND_VERSION"]

    system = platform.system().lower()
    if system == "darwin":  # pragma: no cover
        system = "macos"

    machine = platform.machine().lower()
    if machine == "x86_64":  # pragma: no cover
        machine = "x64"

    return "https://github.com/tailwindlabs/tailwindcss/releases/download/" f"v{version}/tailwindcss-{system}-{machine}"


def get_executable_path(basepath: Union[Path, str, None] = None) -> Path:
    """Build path where to store the Tailwind CSS CLI locally."""
    config = get_config()

    version = config["TAILWIND_VERSION"]

    system = platform.system().lower()
    if system == "darwin":  # pragma: no cover
        system = "macos"

    machine = platform.machine().lower()
    if machine == "x86_64":  # pragma: no cover
        machine = "x64"

    executable_name = f"tailwindcss-{system}-{machine}-{version}"

    if basepath is not None:
        return Path(basepath).expanduser() / executable_name
    else:
        return Path(config["TAILWIND_CLI_PATH"]).expanduser() / executable_name


def get_theme_app_path() -> Path:
    """Build path for the theme app."""
    config = get_config()
    return Path(settings.BASE_DIR) / config["TAILWIND_THEME_APP"]


def get_src_css_path() -> Path:
    """Build path to the source css."""
    config = get_config()
    return get_theme_app_path() / config["TAILWIND_SRC_CSS"]


def get_dist_css_path() -> Path:
    """Build path to the compiled css."""
    config = get_config()
    return get_theme_app_path() / "static" / config["TAILWIND_DIST_CSS"]


def download_file(src: str, destination: Path):
    """Download Tailwind CSS CLI to executable path."""
    certifi_context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(src, context=certifi_context) as source, destination.open(mode="wb") as dest:
        shutil.copyfileobj(source, dest)
    # make cli executable
    destination.chmod(0o755)
