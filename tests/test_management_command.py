from __future__ import annotations

import shutil
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from django_tailwind_cli.utils import get_executable_path, get_theme_app_path


@pytest.fixture(autouse=True)
def with_tempdir(settings: Any, tmpdir_factory: Any):
    tmp = tmpdir_factory.mktemp("test_management_command")
    settings.TAILWIND_CLI_PATH = Path(tmp).joinpath("bin")
    settings.BASE_DIR = tmp
    yield
    shutil.rmtree(tmp)


def test_install_cli():
    call_command("tailwind", "installcli")
    cli = get_executable_path()
    assert cli.exists()
    assert cli.is_file()


def test_install_cli_twice(capsys: Any):
    call_command("tailwind", "installcli")
    call_command("tailwind", "installcli")
    captured = capsys.readouterr()
    assert "Warning. CLI is already installed." in captured.out.replace("\n", "")


@pytest.mark.parametrize("theme_app_name", ["theme", "snake_case_theme"])
def test_init_project(settings: Any, theme_app_name: str):
    settings.TAILWIND_THEME_APP = theme_app_name
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")

    theme_path = get_theme_app_path()
    assert theme_path.exists()
    assert theme_path.joinpath("tailwind.config.js").exists()
    assert theme_path.joinpath("src/styles.css").exists()
    assert theme_path.joinpath("static/css/styles.css").exists()

    assert theme_path.joinpath("apps.py").exists()
    apps_py = theme_path.joinpath("apps.py").read_text()
    assert theme_app_name.replace("_", " ").title().replace(" ", "") + "Config" in apps_py
    assert f'name = "{theme_app_name}"' in apps_py


def test_init_twice(capsys: Any):
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")
    call_command("tailwind", "init")
    theme_path = get_theme_app_path()
    captured = capsys.readouterr()
    assert f"Warning. Theme app {theme_path} is already initialized." in captured.out.replace(
        "\n", ""
    )


def test_build():
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")
    call_command("tailwind", "build")


def test_build_without_cli():
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")
    get_executable_path().unlink()
    with pytest.raises(CommandError):
        call_command("tailwind", "build")


@pytest.mark.parametrize("file_to_remove", ["src/styles.css"])
def test_build_provoke_exception(file_to_remove: str):
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")
    get_theme_app_path().joinpath(file_to_remove).unlink()
    with pytest.raises(CalledProcessError):
        call_command("tailwind", "build")


def test_start_watcher_without_cli():
    call_command("tailwind", "installcli")
    call_command("tailwind", "init")
    get_executable_path().unlink()
    with pytest.raises(CommandError):
        call_command("tailwind", "startwatcher")


def test_unsupported_subcommand():
    with pytest.raises(CommandError):
        call_command("tailwind", "notavalidcommand")
