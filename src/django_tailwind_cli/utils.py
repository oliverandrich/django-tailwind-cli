from __future__ import annotations

import platform
from pathlib import Path

from django.conf import settings

DEFAULT_TAILWIND_VERSION = "3.1.8"


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
    machine = platform.machine().lower()
    system = platform.system().lower()
    system = "macos" if system == "darwin" else system
    return (
        "https://github.com/tailwindlabs/tailwindcss/releases/download/"
        f"v{version}/tailwindcss-{system}-{machine}"
    )


def get_executable_path() -> Path:
    config = get_config()
    return (
        Path(config["TAILWIND_CLI_PATH"]).expanduser() / f"tailwindcss-{config['TAILWIND_VERSION']}"
    )


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
