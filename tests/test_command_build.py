from __future__ import annotations

from subprocess import CalledProcessError
from typing import Any

import pytest
from click import ClickException  # type: ignore
from django.core.management import call_command


def test_build(theme_app_path: Any):
    call_command("tailwind", "build")
    assert theme_app_path.joinpath("static/css/styles.css").exists()


def test_build_without_installed_cli(theme_app_path: Any, settings: Any, tmpdir: str):
    # This just changes the tailwind cli path without actually deleting the session scoped cli
    settings.TAILWIND_CLI_PATH = tmpdir
    with pytest.raises(ClickException):
        call_command("tailwind", "build")


@pytest.mark.parametrize("file_to_remove", ["src/styles.css"])
def test_build_provoke_exception(theme_app_path: Any, file_to_remove: str):
    theme_app_path.joinpath(file_to_remove).unlink()
    with pytest.raises(CalledProcessError):
        call_command("tailwind", "build")
