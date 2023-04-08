"""`tailwind` management command."""

import shutil
import subprocess
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from django.conf import settings

# We need to import click and djclick to make pyright happy
from django.core.management.base import CommandError, LabelCommand
from django_rich.management import RichCommand

from django_tailwind_cli.utils import (
    download_file,
    get_config,
    get_dist_css_path,
    get_download_url,
    get_executable_path,
    get_src_css_path,
    get_theme_app_path,
)


class Command(RichCommand, LabelCommand):
    """Create and manage a Tailwind CSS theme."""

    def handle_label(self, label: str, **options: Any) -> None:
        """Perform the command's actions for ``label``, which will be the string as given on the command line."""
        if label == "installcli":
            self.installcli()
        elif label == "init":
            self.init_theme_app()
        elif label == "build":
            self.build()
        elif label == "watch":
            self.watch()
        else:
            raise CommandError(f"Unsupported subcommand `{label}` called.")

    def installcli(self):
        """Install the Tailwind CSS cli in the version defined by TAILWIND_VERSION."""

        # build path for cli
        dest_file = get_executable_path()

        # check if cli is already installed
        if dest_file.exists():
            raise CommandError(f"CLI is already installed at `{dest_file}`.")

        # create parent directory for cli
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # download cli to dest_file
        download_url = get_download_url()
        download_file(download_url, dest_file)

        # print success message
        self.console.print(f"[green]Downloaded Tailwind CSS CLI to `{dest_file}`.[/green]")

    def init_theme_app(self):
        """Create a new theme app with a tailwind config and a base stylesheet."""

        config = get_config()

        # Get the path to the django_tailwind_cli module.
        module_spec = find_spec("django_tailwind_cli")
        if module_spec and module_spec.origin:
            module_path = Path(module_spec.origin).parent
        else:
            raise CommandError("Unable to determine the path to the django_tailwind_cli module.")

        # check if theme app is already initialized. Otherwise create it.
        theme_app_path = settings.BASE_DIR / config["TAILWIND_THEME_APP"]
        if not theme_app_path.exists():
            theme_app_path.mkdir(parents=True)
        else:
            raise CommandError(f"Theme app {config['TAILWIND_THEME_APP']} is already initialized.")

        # create directory structure for theme app
        src_css_path = (theme_app_path / config["TAILWIND_SRC_CSS"]).parent
        src_css_path.mkdir(parents=True)

        dist_css_path = (theme_app_path / "static" / config["TAILWIND_DIST_CSS"]).parent
        dist_css_path.mkdir(parents=True)

        # create files of the theme app
        (theme_app_path / "__init__.py").open("w").close()
        shutil.copyfile(module_path / "tailwind.config.js", theme_app_path / "tailwind.config.js")
        shutil.copyfile(module_path / "styles.css", src_css_path / "styles.css")
        shutil.copytree(module_path / "templates", theme_app_path / "templates")

        # print success message
        self.console.print(f"[green]Initialized the theme app in `{theme_app_path}`.[/green]")

    def build(self):
        """Build a minified production ready CSS file."""
        if not get_executable_path().exists():
            raise CommandError("CLI is not installed. Please run `manage.py tailwind installcli`.")

        subprocess.run(
            [
                str(get_executable_path()),
                "--input",
                str(get_src_css_path()),
                "--output",
                str(get_dist_css_path()),
                "--minify",
            ],
            cwd=get_theme_app_path(),
            check=True,
        )

        # print success message
        self.console.print("[green]Built production stylesheet.[/green]")

    def watch(self):
        """Start Tailwind CLI in watch mode during development."""
        if not get_executable_path().exists():
            raise CommandError("CLI is not installed. Please run `manage.py tailwind installcli`.")

        subprocess.run(
            [
                str(get_executable_path()),
                "--input",
                str(get_src_css_path()),
                "--output",
                str(get_dist_css_path()),
                "--watch",
            ],
            cwd=get_theme_app_path(),
            check=True,
        )
