from __future__ import annotations

import shutil
from typing import Any

import pytest
from click import ClickException  # type: ignore
from django.core.management import call_command
from django_tailwind_cli.utils import get_executable_path


def test_install_cli(settings: Any, tmpdir: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    call_command("tailwind", "installcli")
    assert get_executable_path().exists()


def test_install_cli_if_already_installed_cli(settings: Any, tmpdir: str):
    settings.TAILWIND_CLI_PATH = tmpdir
    call_command("tailwind", "installcli")
    with pytest.raises(ClickException):
        call_command("tailwind", "installcli")


def test_install_cli_with_nonexisting_cli_path(settings: Any, tmpdir: str):
    settings.TAILWIND_CLI_PATH = tmpdir
    shutil.rmtree(tmpdir)
    assert not get_executable_path().exists()
    call_command("tailwind", "installcli")
    assert get_executable_path().exists()
