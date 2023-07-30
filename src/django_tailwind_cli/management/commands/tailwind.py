"""`tailwind` management command."""

import shutil
import ssl
import subprocess
import sys
import urllib.request
from multiprocessing import Process
from typing import Any, List

import certifi
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_tailwind_cli.utils import Config


class Command(BaseCommand):
    """Create and manage a Tailwind CSS theme."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the command."""

        super().__init__(*args, **kwargs)

        # Get the config from the settings and validate it.
        self.config = Config()
        try:
            self.config.validate_settings()
        except Exception as e:
            raise CommandError("Configuration error") from e

    def add_arguments(self, parser: Any) -> None:
        """Add arguments to the command."""
        subparsers = parser.add_subparsers(dest="tailwind", required=True)

        subparsers.add_parser("build", help="Build a minified production ready CSS file.")

        subparsers.add_parser("watch", help="Start Tailwind CLI in watch mode during development.")

        runserver_parser = subparsers.add_parser(
            "runserver", help="Start the Django development server and the Tailwind CLI in watch mode."
        )
        runserver_parser.add_argument("addrport", nargs="?", help="Optional port number, or ipaddr:port")

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Perform the command's actions."""

        # Get the subcommand from the kwargs.
        label = kwargs.get("tailwind")
        del kwargs["tailwind"]

        # Before running the actual subcommand, we need to make sure that the CLI is installed and
        # the config file exists.
        self._download_cli_if_not_exists()
        self._create_tailwind_config_if_not_exists()

        # Start the subcommand.
        if label == "build":
            self.build(*args[1:], **kwargs)
        elif label == "watch":
            self.watch(*args[1:], **kwargs)
        elif label == "runserver":  # pragma: no cover
            self.runserver(*args[1:], **kwargs)

    def build(self, *args: Any, **kwargs: Any) -> None:
        """Build a minified production ready CSS file."""
        try:
            subprocess.run(self.get_build_cmd(), cwd=settings.BASE_DIR, check=True)
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("Canceled building production stylesheet."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Built production stylesheet '{self.config.get_full_dist_css_path()}'.")
            )

    def watch(self, *args: Any, **kwargs: Any) -> None:
        """Start Tailwind CLI in watch mode during development."""
        try:
            subprocess.run(self.get_watch_cmd(), cwd=settings.BASE_DIR, check=True)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopped watching for changes."))

    def runserver(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        """Start the Django development server and the Tailwind CLI in watch mode."""

        # Start the watch process in a separate process.
        watch_cmd = [sys.executable, "manage.py", "tailwind", "watch"]
        watch_process = Process(
            target=subprocess.run,
            args=(watch_cmd,),
            kwargs={
                "cwd": settings.BASE_DIR,
                "check": True,
            },
        )

        # Start the runserver process in the current process.
        debugserver_cmd = [sys.executable, "manage.py", "runserver"]
        if addrport := kwargs.get("addrport"):
            debugserver_cmd.append(addrport)
        debugserver_process = Process(
            target=subprocess.run,
            args=(debugserver_cmd,),
            kwargs={
                "cwd": settings.BASE_DIR,
                "check": True,
            },
        )

        try:
            watch_process.start()
            debugserver_process.start()
            watch_process.join()
            debugserver_process.join()
        except KeyboardInterrupt:
            watch_process.terminate()
            debugserver_process.terminate()

    def get_build_cmd(self) -> List[str]:
        """Get the command to build the CSS."""
        if self.config.src_css is None:
            return [
                str(self.config.get_full_cli_path()),
                "--output",
                str(self.config.get_full_dist_css_path()),
                "--minify",
            ]
        else:
            return [
                str(self.config.get_full_cli_path()),
                "--input",
                str(self.config.get_full_src_css_path()),
                "--output",
                str(self.config.get_full_dist_css_path()),
                "--minify",
            ]

    def get_watch_cmd(self) -> List[str]:
        """Get the command to watch the CSS."""
        if self.config.src_css is None:
            return [
                str(self.config.get_full_cli_path()),
                "--output",
                str(self.config.get_full_dist_css_path()),
                "--watch",
            ]
        else:
            return [
                str(self.config.get_full_cli_path()),
                "--input",
                str(self.config.get_full_src_css_path()),
                "--output",
                str(self.config.get_full_dist_css_path()),
                "--watch",
            ]

    def _download_cli_if_not_exists(self) -> None:
        dest_file = self.config.get_full_cli_path()
        download_url = self.config.get_download_url()

        if not dest_file.exists():
            self.stdout.write(self.style.ERROR("Tailwind CSS CLI not found."))
            self.stdout.write(self.style.WARNING(f"Downloading Tailwind CSS CLI from '{download_url}'"))
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            certifi_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(download_url, context=certifi_context) as source, dest_file.open(
                mode="wb"
            ) as dest:
                shutil.copyfileobj(source, dest)
            # make cli executable
            dest_file.chmod(0o755)
            self.stdout.write(self.style.SUCCESS(f"Downloaded Tailwind CSS CLI to '{dest_file}'"))

    def _create_tailwind_config_if_not_exists(self) -> None:
        tailwind_config_file = self.config.get_full_config_file_path()

        if not tailwind_config_file.exists():
            self.stdout.write(self.style.ERROR("Tailwind CSS config not found."))
            tailwind_config_file.write_text(DEFAULT_TAILWIND_CONFIG)
            self.stdout.write(self.style.SUCCESS(f"Created Tailwind CSS config at '{tailwind_config_file}'"))


DEFAULT_TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
const plugin = require("tailwindcss/plugin");

module.exports = {
  content: [
    './templates/**/*.html',
    '**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
    plugin(function ({ addVariant }) {
      addVariant("htmx-settling", ["&.htmx-settling", ".htmx-settling &"]);
      addVariant("htmx-request", ["&.htmx-request", ".htmx-request &"]);
      addVariant("htmx-swapping", ["&.htmx-swapping", ".htmx-swapping &"]);
      addVariant("htmx-added", ["&.htmx-added", ".htmx-added &"]);
    }),
  ],
}
"""
