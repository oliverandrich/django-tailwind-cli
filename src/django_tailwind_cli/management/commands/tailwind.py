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
from typing import Annotated, List, Optional, Union

import certifi
from django.conf import settings
from django.core.management.base import CommandError
from django.template.utils import get_app_template_dirs
from django_typer import TyperCommand, command, initialize
from typer import Argument, Option

from django_tailwind_cli.utils import Config


class Command(TyperCommand):
    help = """Create and manage a Tailwind CSS theme."""

    @initialize()
    def init(self):
        # Get the config from the settings and validate it.
        self.config = Config()
        try:
            self.config.validate_settings()
        except Exception as e:
            msg = "Configuration error"
            raise CommandError(msg) from e

        # Before running the actual subcommand, we need to make sure that the CLI is installed and
        # the config file exists.
        self._download_cli_if_not_exists()
        self._create_tailwind_config_if_not_exists()

    @command(help="Build a minified production ready CSS file.")
    def build(self):
        build_cmd = [
            str(self.config.get_full_cli_path()),
            "--output",
            str(self.config.get_full_dist_css_path()),
            "--minify",
        ]
        if self.config.src_css is not None:
            build_cmd.extend(
                [
                    "--input",
                    str(self.config.get_full_src_css_path()),
                ]
            )
        try:
            subprocess.run(build_cmd, cwd=settings.BASE_DIR, check=True)  # noqa: S603
        except KeyboardInterrupt:
            self._write_error("Canceled building production stylesheet.")
        else:
            self._write_success(f"Built production stylesheet '{self.config.get_full_dist_css_path()}'.")

    @command(help="Start Tailwind CLI in watch mode during development.")
    def watch(self):
        watch_cmd = [
            str(self.config.get_full_cli_path()),
            "--output",
            str(self.config.get_full_dist_css_path()),
            "--watch",
        ]
        if self.config.src_css is not None:
            watch_cmd.extend(
                [
                    "--input",
                    str(self.config.get_full_src_css_path()),
                ]
            )

        try:
            subprocess.run(watch_cmd, cwd=settings.BASE_DIR, check=True)  # noqa: S603
        except KeyboardInterrupt:
            self._write_success("Stopped watching for changes.")

    @command(name="list_templates", help="List the templates of your django project.")
    def list_templates(self):
        template_files: List[str] = []
        app_template_dirs = get_app_template_dirs("templates")
        for app_template_dir in app_template_dirs:
            template_files += self._list_template_files(app_template_dir)

        for template_dir in settings.TEMPLATES[0]["DIRS"]:
            template_files += self._list_template_files(template_dir)

        self.stdout.write("\n".join(template_files))

    @command(help="Start the Django development server and the Tailwind CLI in watch mode.")
    def runserver(
        self,
        addrport: Annotated[Optional[str], Argument(help="Optional port number, or ipaddr:port")] = None,
        *,
        use_ipv6: Annotated[bool, Option("--ipv6", "-6", help="Tells Django to use an IPv6 address.")] = False,
        no_threading: Annotated[bool, Option("--nothreading", help="Tells Django to NOT use threading.")] = False,
        no_static: Annotated[
            bool, Option("--nostatic", help="Tells Django to NOT automatically serve static files at STATIC_URL.")
        ] = False,
        no_reloader: Annotated[bool, Option("--noreload", help="Tells Django to NOT use the auto-reloader.")] = False,
        skip_checks: Annotated[bool, Option("--skip-checks", help="Skip system checks.")] = False,
    ):
        debug_server_cmd = [sys.executable, "manage.py", "runserver"]

        if use_ipv6:
            debug_server_cmd.append("--ipv6")
        if no_threading:
            debug_server_cmd.append("--nothreading")
        if no_static:
            debug_server_cmd.append("--nostatic")
        if no_reloader:
            debug_server_cmd.append("--noreload")
        if skip_checks:
            debug_server_cmd.append("--skip-checks")
        if addrport:
            debug_server_cmd.append(addrport)

        self._runserver(debug_server_cmd)

    @command(
        name="runserver_plus",
        help="Start the django-extensions runserver_plus development server and the Tailwind CLI in watch mode.",
    )
    def runserver_plus(
        self,
        addrport: Annotated[Optional[str], Argument(help="Optional port number, or ipaddr:port")] = None,
        *,
        use_ipv6: Annotated[bool, Option("--ipv6", "-6", help="Tells Django to use an IPv6 address.")] = False,
        no_threading: Annotated[bool, Option("--nothreading", help="Tells Django to NOT use threading.")] = False,
        no_static: Annotated[
            bool, Option("--nostatic", help="Tells Django to NOT automatically serve static files at STATIC_URL.")
        ] = False,
        no_reloader: Annotated[bool, Option("--noreload", help="Tells Django to NOT use the auto-reloader.")] = False,
        skip_checks: Annotated[bool, Option("--skip-checks", help="Skip system checks.")] = False,
        pdb: Annotated[bool, Option("--pdb", help="Drop into pdb shell at the start of any view.")] = False,
        ipdb: Annotated[bool, Option("--ipdb", help="Drop into ipdb shell at the start of any view.")] = False,
        pm: Annotated[bool, Option("--pm", help="Drop into (i)pdb shell if an exception is raised in a view.")] = False,
        print_sql: Annotated[bool, Option("--print-sql", help="Print SQL queries as they're executed.")] = False,
        print_sql_location: Annotated[
            bool, Option("--print-sql-location", help="Show location in code where SQL query generated from.")
        ] = False,
        cert_file: Annotated[
            Optional[str],
            Option(
                help=(
                    "SSL .crt file path. If not provided path from --key-file will be selected. Either --cert-file or "
                    "--key-file must be provided to use SSL."
                )
            ),
        ] = None,
        key_file: Annotated[
            Optional[str],
            Option(
                help=(
                    "SSL .key file path. If not provided path from --cert-file will be "
                    "selected. Either --cert-file or --key-file must be provided to use SSL."
                )
            ),
        ] = None,
    ):
        if not importlib.util.find_spec("django_extensions") and not importlib.util.find_spec("werkzeug"):
            msg = (
                "Missing dependencies. Follow the instructions found on "
                "https://django-tailwind-cli.andrich.me/installation/."
            )
            raise CommandError(msg)

        debug_server_cmd = [sys.executable, "manage.py", "runserver_plus"]

        if use_ipv6:
            debug_server_cmd.append("--ipv6")
        if no_threading:
            debug_server_cmd.append("--nothreading")
        if no_static:
            debug_server_cmd.append("--nostatic")
        if no_reloader:
            debug_server_cmd.append("--noreload")
        if skip_checks:
            debug_server_cmd.append("--skip-checks")
        if pdb:
            debug_server_cmd.append("--pdb")
        if ipdb:
            debug_server_cmd.append("--ipdb")
        if pm:
            debug_server_cmd.append("--pm")
        if print_sql:
            debug_server_cmd.append("--print-sql")
        if print_sql_location:
            debug_server_cmd.append("--print-sql-location")
        if cert_file:
            debug_server_cmd.append(f"--cert-file={cert_file}")
        if key_file:
            debug_server_cmd.append(f"--key-file={key_file}")
        if addrport:
            debug_server_cmd.append(addrport)

        self._runserver(debug_server_cmd)

    def _runserver(self, debug_server_cmd: List[str]) -> None:
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
        debugserver_process = Process(
            target=subprocess.run,
            args=(debug_server_cmd,),
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

    def _download_cli_if_not_exists(self) -> None:
        dest_file = self.config.get_full_cli_path()

        if not dest_file.exists() and self.config.automatic_download:
            download_url = self.config.get_download_url()
            self.stdout.write(self.style.ERROR("Tailwind CSS CLI not found."))
            self.stdout.write(self.style.WARNING(f"Downloading Tailwind CSS CLI from '{download_url}'"))
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            certifi_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(download_url, context=certifi_context) as source, dest_file.open(  # noqa: S310
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

    @staticmethod
    def _list_template_files(template_dir: Union[str, Path]) -> List[str]:
        template_files: List[str] = []
        for d, _, filenames in os.walk(str(template_dir)):
            for filename in filenames:
                if filename.endswith(".html") or filename.endswith(".txt"):
                    template_files.append(os.path.join(d, filename))
        return template_files

    def _write_error(self, message: str) -> None:
        self.stdout.write(self.style.ERROR(message))

    def _write_success(self, message: str) -> None:
        self.stdout.write(self.style.SUCCESS(message))


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
