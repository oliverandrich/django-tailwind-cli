from pathlib import Path
from typing import Any

from django_tailwind_cli.utils import (
    DEFAULT_TAILWIND_VERSION,
    get_config,
    get_dist_css_path,
    get_download_url,
    get_executable_path,
    get_src_css_path,
    get_theme_app_name,
    get_theme_app_path,
)


def test_get_config():
    """`get_config` returns the config dict from the settings."""

    assert get_config() == {
        "TAILWIND_CLI_PATH": "~/.local/bin/",
        "TAILWIND_DIST_CSS": "css/styles.css",
        "TAILWIND_SRC_CSS": "src/styles.css",
        "TAILWIND_THEME_APP": "theme",
        "TAILWIND_VERSION": DEFAULT_TAILWIND_VERSION,
    }


def test_get_download_url(settings: Any):
    """Download url includes correct version number."""

    assert DEFAULT_TAILWIND_VERSION in get_download_url()
    settings.TAILWIND_VERSION = "3.1.9"
    assert "3.1.9" in get_download_url()


def test_get_executable_path(settings: Any):
    """CLI path includes correct version number."""

    p = get_executable_path()
    assert p.is_absolute()
    assert p.relative_to(Path.home())
    assert str(p).endswith(f"-{DEFAULT_TAILWIND_VERSION}")
    settings.TAILWIND_CLI_PATH = "/tmp/"
    p = get_executable_path()
    assert str(p).startswith("/tmp/tailwindcss-")


def test_get_theme_app_name(settings: Any):
    """`get_theme_app_name()` returns the correct theme app name."""

    assert get_theme_app_name() == "theme"
    settings.TAILWIND_THEME_APP = "another_theme"
    assert get_theme_app_name() == "another_theme"


def test_get_theme_app_path():
    """`get_theme_app_path()` returns the correct path to the theme app."""

    p = get_theme_app_path()
    assert p is not None
    assert p.is_absolute()
    assert str(p).endswith(get_theme_app_name())


def test_get_src_path(settings: Any):
    """`get_src_css_path()` returns the correct path to the input stylesheet."""

    assert str(get_src_css_path()).endswith("src/styles.css")
    settings.TAILWIND_SRC_CSS = "base.css"
    assert str(get_src_css_path()).endswith("base.css")


def test_get_dist_path(settings: Any):
    """`get_src_css_path()` returns the correct path to the compiled stylesheet."""

    assert str(get_dist_css_path()).endswith("static/css/styles.css")
    settings.TAILWIND_DIST_CSS = "built.css"
    assert str(get_dist_css_path()).endswith("static/built.css")
