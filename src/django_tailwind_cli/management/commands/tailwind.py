"""`tailwind` management command."""

import importlib.util
import os
import shutil
import ssl
import subprocess
import sys
import urllib.request
from multiprocessing import Process
from pathlib import Path
from typing import Any, List, Union

import certifi
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.utils import get_app_template_dirs

from django_tailwind_cli.utils import Config


class Command(BaseCommand):
    """Create and manage a Tailwind CSS theme."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize the command."""

        super().__init__(*args, **kwargs)

        # Get the config from the settings and validate it.
        self.config = Config()
        try:
            self.config.validate_settings()
        except Exception as e:
            msg = "Configuration error"
            raise CommandError(msg) from e

    def add_arguments(self, parser: Any) -> None:
        """Add arguments to the command."""
        subparsers = parser.add_subparsers(dest="tailwind", required=True)

        subparsers.add_parser("build", help="Build a minified production ready CSS file.")

        subparsers.add_parser("watch", help="Start Tailwind CLI in watch mode during development.")

        subparsers.add_parser("list_templates", help="List the templates of your django project.")

        runserver_parser = subparsers.add_parser(
            "runserver",
            help="Start the Django development server and the Tailwind CLI in watch mode.",
        )
        parser.add_argument(
            "--ipv6",
            "-6",
            action="store_true",
            dest="use_ipv6",
            help="Tells Django to use an IPv6 address.",
        )
        parser.add_argument(
            "--nothreading",
            action="store_true",
            dest="no_threading",
            help="Tells Django to NOT use threading.",
        )
        parser.add_argument(
            "--noreload",
            action="store_true",
            dest="no_reloader",
            help="Tells Django to NOT use the auto-reloader.",
        )
        runserver_parser.add_argument(
            "--skip-checks",
            action="store_true",
            help="Skip system checks.",
        )
        runserver_parser.add_argument(
            "addrport", nargs="?", help="Optional port number, or ipaddr:port"
        )

        runserver_plus_parser = subparsers.add_parser(
            "runserver_plus",
            help=(
                "Start the django-extensions runserver_plus development server and the "
                "Tailwind CLI in watch mode."
            ),
        )
        runserver_plus_parser.add_argument(
            "--ipv6",
            "-6",
            action="store_true",
            dest="use_ipv6",
            help="Tells Django to use an IPv6 address.",
        )
        runserver_plus_parser.add_argument(
            "--nothreading",
            action="store_true",
            dest="no_threading",
            help="Do not run in multithreaded mode.",
        )
        runserver_plus_parser.add_argument(
            "--noreload",
            action="store_true",
            dest="no_reloader",
            help="Tells Django to NOT use the auto-reloader.",
        )
        runserver_plus_parser.add_argument(
            "--pdb",
            action="store_true",
            help="Drop into pdb shell at the start of any view.",
        )
        runserver_plus_parser.add_argument(
            "--ipdb",
            action="store_true",
            help="Drop into ipdb shell at the start of any view.",
        )
        runserver_plus_parser.add_argument(
            "--pm",
            action="store_true",
            help="Drop into (i)pdb shell if an exception is raised in a view.",
        )
        runserver_plus_parser.add_argument(
            "--print-sql",
            action="store_true",
            help="Print SQL queries as they're executed.",
        )
        runserver_plus_parser.add_argument(
            "--cert-file", help="Optional SSL certificate file to use for the development server."
        )
        runserver_plus_parser.add_argument(
            "--cert",
            help="[DEPRECATED] Optional SSL certificate file to use for the development server.",
        )
        runserver_plus_parser.add_argument(
            "--key-file", help="Optional SSL certificate file to use for the development server."
        )
        runserver_plus_parser.add_argument(
            "--reloader-interval",
            help="Optional SSL certificate file to use for the development server.",
        )
        runserver_plus_parser.add_argument(
            "addrport", nargs="?", help="Optional port number, or ipaddr:port"
        )

    def handle(self, *_args: Any, **kwargs: Any) -> None:
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
            self.build()
        elif label == "watch":
            self.watch()
        elif label == "runserver":
            kwargs["runserver_cmd"] = "runserver"
            self.runserver(**kwargs)
        elif label == "runserver_plus":
            if importlib.util.find_spec("django_extensions") and importlib.util.find_spec(
                "werkzeug"
            ):
                kwargs["runserver_cmd"] = "runserver_plus"
                self.runserver(**kwargs)
            else:
                msg = "Missing dependencies. Follow the instructions found on https://django-tailwind-cli.andrich.me/installation/."
                raise CommandError(msg)
        elif label == "list_templates":
            self.list_templates()

    def build(self) -> None:
        """Build a minified production ready CSS file."""
        try:
            subprocess.run(self.get_build_cmd(), cwd=settings.BASE_DIR, check=True)  # noqa: S603
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("Canceled building production stylesheet."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Built production stylesheet '{self.config.get_full_dist_css_path()}'."
                )
            )

    def watch(self) -> None:
        """Start Tailwind CLI in watch mode during development."""
        try:
            subprocess.run(self.get_watch_cmd(), cwd=settings.BASE_DIR, check=True)  # noqa: S603
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopped watching for changes."))

    def runserver(self, **kwargs: Any) -> None:  # pragma: no cover
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
        debugserver_cmd = [sys.executable, "manage.py", kwargs["runserver_cmd"]]

        if addrport := kwargs.get("addrport"):
            debugserver_cmd.append(addrport)

        if kwargs.get("use_ipv6", False):
            debugserver_cmd.append("--ipv6")
        if kwargs.get("no_threading", False):
            debugserver_cmd.append("--nothreading")
        if kwargs.get("no_reloader", False):
            debugserver_cmd.append("--noreload")
        if kwargs.get("skip_checks", False):
            debugserver_cmd.append("--skip-checks")

        if kwargs.get("print_sql", False):
            debugserver_cmd.append("--print-sql")
        if kwargs.get("pdb", False):
            debugserver_cmd.append("--pdb")
        if kwargs.get("ipdb", False):
            debugserver_cmd.append("--ipdb")
        if kwargs.get("pm", False):
            debugserver_cmd.append("--pm")

        if cert_file := kwargs.get("cert_file"):
            debugserver_cmd.append(f"--cert-file={cert_file}")
        elif cert := kwargs.get("cert"):
            debugserver_cmd.append(f"--cert-file={cert}")
        if key_file := kwargs.get("key_file"):
            debugserver_cmd.append(f"--key-file={key_file}")

        if reloader_interval := kwargs.get("reloader_interval"):
            debugserver_cmd.append(f"--reloader-interval={reloader_interval}")

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

    def list_templates(self):
        template_files: List[str] = []
        app_template_dirs = get_app_template_dirs("templates")
        for app_template_dir in app_template_dirs:
            template_files += self.list_template_files(app_template_dir)

        for template_dir in settings.TEMPLATES[0]["DIRS"]:
            template_files += self.list_template_files(template_dir)

        self.stdout.write("\n".join(template_files))

    def list_template_files(self, template_dir: Union[str, Path]) -> List[str]:
        template_files: List[str] = []
        for dirpath, _, filenames in os.walk(str(template_dir)):
            for filename in filenames:
                if filename.endswith(".html") or filename.endswith(".txt"):
                    template_files.append(os.path.join(dirpath, filename))
        return template_files

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

        if not dest_file.exists() and self.config.automatic_download:
            download_url = self.config.get_download_url()
            self.stdout.write(self.style.ERROR("Tailwind CSS CLI not found."))
            self.stdout.write(
                self.style.WARNING(f"Downloading Tailwind CSS CLI from '{download_url}'")
            )
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            certifi_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(  # noqa: S310
                download_url, context=certifi_context
            ) as source, dest_file.open(mode="wb") as dest:
                shutil.copyfileobj(source, dest)
            # make cli executable
            dest_file.chmod(0o755)
            self.stdout.write(self.style.SUCCESS(f"Downloaded Tailwind CSS CLI to '{dest_file}'"))

    def _create_tailwind_config_if_not_exists(self) -> None:
        tailwind_config_file = self.config.get_full_config_file_path()

        if not tailwind_config_file.exists():
            self.stdout.write(self.style.ERROR("Tailwind CSS config not found."))
            tailwind_config_file.write_text(DEFAULT_TAILWIND_CONFIG)
            self.stdout.write(
                self.style.SUCCESS(f"Created Tailwind CSS config at '{tailwind_config_file}'")
            )


DEFAULT_TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
const plugin = require("tailwindcss/plugin");
const { spawnSync } = require("child_process");

// Calls Django to fetch template files
const getTemplateFiles = () => {
  const command = "python3";
  const args = ["manage.py", "tailwind", "list_templates"];
  // Assumes tailwind.config.js is located in the BASE_DIR of your Django project.
  const options = { cwd: __dirname };

  const result = spawnSync(command, args, options);

  if (result.error) {
    throw result.error;
  }

  if (result.status !== 0) {
    console.log(result.stdout.toString(), result.stderr.toString());
    throw new Error(
      `Django management command exited with code ${result.status}`
    );
  }

  const templateFiles = result.stdout
    .toString()
    .split("\\n")
    .map((file) => file.trim())
    .filter(function (e) {
      return e;
    }); // Remove empty strings, including last empty line.
  return templateFiles;
};

module.exports = {
  content: [].concat(getTemplateFiles()),
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/aspect-ratio"),
    require("@tailwindcss/container-queries"),
    plugin(function ({ addVariant }) {
      addVariant("htmx-settling", ["&.htmx-settling", ".htmx-settling &"]);
      addVariant("htmx-request", ["&.htmx-request", ".htmx-request &"]);
      addVariant("htmx-swapping", ["&.htmx-swapping", ".htmx-swapping &"]);
      addVariant("htmx-added", ["&.htmx-added", ".htmx-added &"]);
    }),
  ],
};
"""
