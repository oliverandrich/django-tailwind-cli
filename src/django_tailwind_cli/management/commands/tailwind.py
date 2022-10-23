from __future__ import annotations

import subprocess
from typing import Any

import httpx
from django.core.management.base import CommandError, LabelCommand

from django_tailwind_cli.utils import (
    get_dist_css_path,
    get_download_url,
    get_executable_path,
    get_src_css_path,
    get_theme_app_name,
    get_theme_app_path,
)


class Command(LabelCommand):
    # TODO: document command
    def handle_label(self, label: str, **options: Any) -> None:
        if label not in ["init", "installcli", "startwatcher", "build"]:
            raise CommandError(f"Subcommand {label} doesn't exist")

        if label == "init":
            self.init_project()
        elif label == "installcli":
            self.install_cli()
        elif label == "startwatcher":
            self.start_watcher()
        elif label == "build":
            self.build_css(minify=True)

    def install_cli(self) -> None:
        """Install the given version of the tailwindcss cli."""

        # build path for cli
        dest_file = get_executable_path()

        # check if cli is already installed
        if dest_file.exists():
            raise CommandError("CLI is already installed.")

        # create parent directory for cli
        if not dest_file.parent.exists():
            dest_file.parent.mkdir(parents=True)

        # build download_url
        download_url = get_download_url()

        # download cli
        response = httpx.get(download_url, follow_redirects=True)

        if response.is_error:
            raise CommandError(
                f"Unable to download {download_url}. "
                f"HTTP Status: {response.status_code} {response.reason_phrase}"
            )

        with dest_file.open(mode="wb") as f:
            f.write(response.content)
            dest_file.chmod(0o755)

        # print success message
        self.stdout.write(self.style.SUCCESS(f"Downloaded Tailwind CSS CLI to `{dest_file}`.\n"))

    def init_project(self) -> None:
        """Creates a new theme with tailwind config and a base stylesheet."""

        # check if theme app is already initialized
        theme_path = get_theme_app_path()
        if theme_path.exists():
            raise CommandError("Theme app {} is already initialized.")

        # create directory structure for theme app
        get_src_css_path().parent.mkdir(parents=True)
        get_dist_css_path().parent.mkdir(parents=True)

        # create files of the theme app
        theme_path.joinpath("__init__.py").open("w").close()

        with theme_path.joinpath("tailwind.config.js").open("w") as f:
            f.write(DEFAULT_TAILWIND_CONFIG)

        with theme_path.joinpath("apps.py").open("w") as f:
            theme_name = get_theme_app_name()
            theme_name_camel = theme_name.replace("_", " ").title().replace(" ", "")
            f.write(DEFAULT_APPS_PY.format(theme_name_camel, theme_name))

        with get_src_css_path().open("w") as f:
            f.write(DEFAULT_BASE_CSS)

        get_dist_css_path().open("w").close()

        # finally build the css once
        self.build_css()

        # print success message
        self.stdout.write(self.style.SUCCESS(f"Initialized the theme app in `{theme_path}`.\n"))

    def start_watcher(self):
        if not get_executable_path().exists():
            raise CommandError(
                "CLI is not installed. Please run [yellow]manage.py tailwind installcli[/yellow]."
            )

        subprocess.run(
            [
                str(get_executable_path()),
                "-i",
                str(get_src_css_path()),
                "-o",
                str(get_dist_css_path()),
                "--watch",
            ],
            cwd=get_theme_app_path(),
            check=True,
        )

    def build_css(self, minify: bool = False):
        if not get_executable_path().exists():
            raise CommandError(
                "CLI is not installed. Please run [yellow]manage.py tailwind installcli[/yellow]."
            )

        subprocess.run(
            [
                str(get_executable_path()),
                "-i",
                str(get_src_css_path()),
                "-o",
                str(get_dist_css_path()),
                "--minify" if minify else "",
            ],
            cwd=get_theme_app_path(),
            check=True,
        )

        # print success message
        self.stdout.write(self.style.SUCCESS("Built production stylesheet.\n"))


DEFAULT_TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
"""

DEFAULT_BASE_CSS = """@tailwind base;
@tailwind components;
@tailwind utilities;
"""

DEFAULT_APPS_PY = """from django.apps import AppConfig


class {}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{}"
"""
