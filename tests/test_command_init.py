from typing import Any

import pytest
from click import ClickException  # type: ignore
from django.core.management import call_command
from django_tailwind_cli.utils import get_theme_app_path


@pytest.mark.parametrize("theme_app_name", ["theme", "snake_case_theme"])
def test_init_project(settings: Any, theme_app_name: str, installed_cli_path: str, tmpdir: str):
    """`tailwind init` creates a theme app inside the project."""

    settings.BASE_DIR = tmpdir
    settings.TAILWIND_CLI_PATH = installed_cli_path
    settings.TAILWIND_THEME_APP = theme_app_name

    call_command("tailwind", "init")

    theme_path = get_theme_app_path()
    assert theme_path.exists()
    assert theme_path.joinpath("tailwind.config.js").exists()
    assert theme_path.joinpath("src/styles.css").exists()
    assert theme_path.joinpath("apps.py").exists()

    apps_py = theme_path.joinpath("apps.py").read_text()
    assert theme_app_name.replace("_", " ").title().replace(" ", "") + "Config" in apps_py
    assert f'name = "{theme_app_name}"' in apps_py


def test_init_when_already_initialized(settings: Any, installed_cli_path: str, tmpdir: str):
    """`tailwind init` raises a `ClickException` when a theme is already created."""

    settings.BASE_DIR = tmpdir
    settings.TAILWIND_CLI_PATH = installed_cli_path

    call_command("tailwind", "init")
    with pytest.raises(ClickException):
        call_command("tailwind", "init")
