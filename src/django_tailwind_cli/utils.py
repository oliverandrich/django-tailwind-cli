"""
Utility functions.

This module contains utility functions to read the configuration, download the CLI and determine
the various paths.
"""

import os
import platform
from pathlib import Path

from django_tailwind_cli.conf import settings


def get_system_and_machine() -> tuple[str, str]:
    """Get the system and machine name."""
    system = platform.system().lower()
    if system == "darwin":
        system = "macos"

    machine = platform.machine().lower()
    if machine in ["x86_64", "amd64"]:
        machine = "x64"
    elif machine == "aarch64":
        machine = "arm64"

    return system, machine


def get_download_url() -> str:
    """Get the download url for the Tailwind CSS CLI."""
    system, machine = get_system_and_machine()
    extension = ".exe" if system == "windows" else ""
    return (
        f"https://github.com/{settings.TAILWIND_CLI_SRC_REPO}/releases/download/"
        f"v{settings.TAILWIND_CLI_VERSION}/{settings.TAILWIND_CLI_ASSET_NAME}-{system}-{machine}{extension}"
    )


def get_full_cli_path() -> Path:
    """Get path to the Tailwind CSS CLI."""

    cli_path = Path(settings.TAILWIND_CLI_PATH).expanduser() if settings.TAILWIND_CLI_PATH else None

    # If Tailwind CSS CLI path points to an existing executable use is.
    if cli_path and cli_path.exists() and cli_path.is_file() and os.access(cli_path, os.X_OK):
        return cli_path

    # Otherwise try to calculate the full cli path as usual.
    system, machine = get_system_and_machine()
    extension = ".exe" if system == "windows" else ""
    executable_name = f"tailwindcss-{system}-{machine}-{settings.TAILWIND_CLI_VERSION}{extension}"
    if cli_path is None:
        return Path(settings.BASE_DIR) / executable_name
    else:
        return cli_path / executable_name


def get_full_src_css_path() -> Path:
    """Get path to the source css."""
    if settings.TAILWIND_CLI_SRC_CSS is None:
        msg = "No source CSS file specified. Please set TAILWIND_SRC_CSS in your settings."
        raise ValueError(msg)
    return Path(settings.BASE_DIR) / settings.TAILWIND_CLI_SRC_CSS


def get_full_dist_css_path() -> Path:
    """Get path to the compiled css."""
    if settings.STATICFILES_DIRS is None or len(settings.STATICFILES_DIRS) == 0:
        msg = "STATICFILES_DIRS is empty. Please add a path to your static files."
        raise ValueError(msg)

    return Path(settings.STATICFILES_DIRS[0]) / settings.TAILWIND_CLI_DIST_CSS


def get_full_config_file_path() -> Path:
    """Get path to the tailwind.config.js file."""
    return Path(settings.BASE_DIR) / settings.TAILWIND_CLI_CONFIG_FILE


def validate_settings() -> None:
    """Validate the settings."""
    if settings.STATICFILES_DIRS is None or len(settings.STATICFILES_DIRS) == 0:
        msg = "STATICFILES_DIRS is empty. Please add a path to your static files."
        raise ValueError(msg)
