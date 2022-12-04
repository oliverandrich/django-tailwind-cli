from __future__ import annotations

import platform
import shutil
import ssl
import urllib.request
from pathlib import Path

import certifi
from django.conf import settings

DEFAULT_TAILWIND_VERSION = "3.2.4"


def get_config() -> dict[str, str]:
    return {
        "TAILWIND_VERSION": getattr(settings, "TAILWIND_VERSION", DEFAULT_TAILWIND_VERSION),
        "TAILWIND_CLI_PATH": getattr(settings, "TAILWIND_CLI_PATH", "~/.local/bin/"),
        "TAILWIND_THEME_APP": getattr(settings, "TAILWIND_THEME_APP", "theme"),
        "TAILWIND_SRC_CSS": getattr(settings, "TAILWIND_SRC_CSS", "src/styles.css"),
        "TAILWIND_DIST_CSS": getattr(settings, "TAILWIND_DIST_CSS", "css/styles.css"),
    }


def get_download_url() -> str:
    config = get_config()
    version = config["TAILWIND_VERSION"]

    system = platform.system().lower()
    if system == "darwin":  # pragma: no cover
        system = "macos"

    machine = platform.machine().lower()
    if machine == "x86_64":  # pragma: no cover
        machine = "x64"

    return (
        "https://github.com/tailwindlabs/tailwindcss/releases/download/"
        f"v{version}/tailwindcss-{system}-{machine}"
    )


def get_executable_name() -> str:
    config = get_config()
    version = config["TAILWIND_VERSION"]

    system = platform.system().lower()
    if system == "darwin":  # pragma: no cover
        system = "macos"

    machine = platform.machine().lower()
    if machine == "x86_64":  # pragma: no cover
        machine = "x64"

    return f"tailwindcss-{system}-{machine}-{version}"


def get_executable_path() -> Path:
    config = get_config()
    return Path(config["TAILWIND_CLI_PATH"]).expanduser() / get_executable_name()


def get_theme_app_name() -> str:
    config = get_config()
    return config["TAILWIND_THEME_APP"]


def get_theme_app_path() -> Path:
    return Path(settings.BASE_DIR) / get_theme_app_name()


def get_src_css_path() -> Path:
    config = get_config()
    return get_theme_app_path() / config["TAILWIND_SRC_CSS"]


def get_dist_css_path() -> Path:
    config = get_config()
    return get_theme_app_path() / "static" / config["TAILWIND_DIST_CSS"]


def download_file(src: str, destination: Path):
    certifi_context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(src, context=certifi_context) as input, destination.open(
        mode="wb"
    ) as output:
        shutil.copyfileobj(input, output)
    # make cli executable
    destination.chmod(0o755)
