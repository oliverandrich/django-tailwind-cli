from __future__ import annotations

import subprocess

# We need to import click and djclick to make pyright happy
import click
import djclick  # type: ignore

from django_tailwind_cli.utils import (
    download_file,
    get_dist_css_path,
    get_download_url,
    get_executable_path,
    get_src_css_path,
    get_theme_app_name,
    get_theme_app_path,
)


@djclick.group()  # type: ignore
def tailwind():
    """A management to create and manage a Tailwind CSS theme."""
    pass


@tailwind.command()  # type: ignore
def installcli():
    """Install the Tailwind CSS cli in the version defined by
    TAILWIND_VERSION."""

    # build path for cli
    dest_file = get_executable_path()

    # check if cli is already installed
    if dest_file.exists():
        raise click.ClickException(f"CLI is already installed at `{dest_file}`.")

    # create parent directory for cli
    if not dest_file.parent.exists():
        dest_file.parent.mkdir(parents=True)

    # download cli to dest_file
    download_url = get_download_url()
    download_file(download_url, dest_file)

    # print success message
    click.secho(f"Downloaded Tailwind CSS CLI to `{dest_file}`.", fg="green")


@tailwind.command()  # type: ignore
def init():
    """Creates a new theme app with a tailwind config and a base stylesheet."""

    # check if theme app is already initialized
    theme_app_name = get_theme_app_name()
    theme_path = get_theme_app_path()
    if theme_path.exists():
        raise click.ClickException(f"Theme app {theme_app_name} is already initialized.")

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

    # print success message
    click.secho(f"Initialized the theme app in `{theme_path}`.", fg="green")


@tailwind.command()  # type: ignore
def build():
    """Builds a minified production ready CSS file."""

    if not get_executable_path().exists():
        raise click.ClickException(
            "CLI is not installed. Please run `manage.py tailwind installcli`."
        )

    subprocess.run(
        [
            str(get_executable_path()),
            "-i",
            str(get_src_css_path()),
            "-o",
            str(get_dist_css_path()),
            "--minify",
        ],
        cwd=get_theme_app_path(),
        check=True,
    )

    # print success message
    click.secho("Built production stylesheet.", fg="green")


@tailwind.command()  # type: ignore
def watch():
    """Starts Tailwind CLI in watch mode during development."""

    if not get_executable_path().exists():
        raise click.ClickException(
            "CLI is not installed. Please run `manage.py tailwind installcli`."
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
