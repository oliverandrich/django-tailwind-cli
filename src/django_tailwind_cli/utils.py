"""
Utility functions.

This module contains utility functions to read the configuration, download the CLI and determine
the various paths.
"""

import platform
from pathlib import Path
from typing import Tuple, Union

from django.conf import settings


class Config:
    """Configuration for the Tailwind CSS CLI."""

    @property
    def tailwind_version(self) -> str:
        return getattr(settings, "TAILWIND_CLI_VERSION", "3.3.5")

    @property
    def cli_path(self) -> Union[str, None]:
        return getattr(settings, "TAILWIND_CLI_PATH", "~/.local/bin/")

    @property
    def src_css(self) -> Union[str, None]:
        return getattr(settings, "TAILWIND_CLI_SRC_CSS", None)

    @property
    def dist_css(self) -> str:
        return getattr(settings, "TAILWIND_CLI_DIST_CSS", "css/tailwind.css")

    @property
    def config_file(self) -> str:
        return getattr(settings, "TAILWIND_CLI_CONFIG_FILE", "tailwind.config.js")

    def validate_settings(self) -> None:
        """Validate the settings."""
        if settings.STATICFILES_DIRS is None or len(settings.STATICFILES_DIRS) == 0:
            msg = "STATICFILES_DIRS is empty. Please add a path to your static files."
            raise ValueError(msg)

    def get_system_and_machine(self) -> Tuple[str, str]:
        """Get the system and machine name."""
        system = platform.system().lower()
        if system == "darwin":  # pragma: no cover
            system = "macos"

        machine = platform.machine().lower()
        if machine == "x86_64":  # pragma: no cover
            machine = "x64"
        elif machine == "aarch64":  # pragma: no cover
            machine = "arm64"

        return (system, machine)

    def get_download_url(self) -> str:
        """Get the download url for the Tailwind CSS CLI."""
        system, machine = self.get_system_and_machine()
        return (
            "https://github.com/tailwindlabs/tailwindcss/releases/download/"
            f"v{self.tailwind_version}/tailwindcss-{system}-{machine}"
        )

    def get_full_cli_path(self) -> Path:
        """Get path to the Tailwind CSS CLI."""
        system, machine = self.get_system_and_machine()
        executable_name = f"tailwindcss-{system}-{machine}-{self.tailwind_version}"
        if self.cli_path is None:
            return Path(settings.BASE_DIR) / executable_name
        else:
            return Path(self.cli_path).expanduser() / executable_name

    def get_full_src_css_path(self) -> Path:
        """Get path to the source css."""
        if self.src_css is None:
            msg = "No source CSS file specified. Please set TAILWIND_SRC_CSS in your settings."
            raise ValueError(msg)
        return Path(settings.BASE_DIR) / self.src_css

    def get_full_dist_css_path(self) -> Path:
        """Get path to the compiled css."""
        if settings.STATICFILES_DIRS is None or len(settings.STATICFILES_DIRS) == 0:
            msg = "STATICFILES_DIRS is empty. Please add a path to your static files."
            raise ValueError(msg)

        return Path(settings.STATICFILES_DIRS[0]) / self.dist_css

    def get_full_config_file_path(self) -> Path:
        """Get path to the tailwind.config.js file."""
        return Path(settings.BASE_DIR) / self.config_file
