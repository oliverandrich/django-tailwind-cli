import shutil
from typing import Any

import pytest
from click import ClickException  # type: ignore
from django.core.management import call_command
from django_tailwind_cli.utils import get_executable_path


def test_install_cli(settings: Any, tmpdir: Any):
    """`tailwind installcli` installs the CLI to the `TAILWIND_CLI_PATH`."""

    settings.TAILWIND_CLI_PATH = tmpdir
    call_command("tailwind", "installcli")
    assert get_executable_path().exists()


def test_install_cli_if_already_installed_cli(settings: Any, tmpdir: str):
    """`tailwind installcli` raises a `ClickException` if run a second time."""

    settings.TAILWIND_CLI_PATH = tmpdir
    call_command("tailwind", "installcli")
    with pytest.raises(ClickException):
        call_command("tailwind", "installcli")


def test_install_cli_with_nonexisting_cli_path(settings: Any, tmpdir: str):
    """`tailwind installcli` recreates the `TAILWIND_CLI_PATH` if it is missing."""

    settings.TAILWIND_CLI_PATH = tmpdir
    shutil.rmtree(tmpdir)
    assert not get_executable_path().exists()
    call_command("tailwind", "installcli")
    assert get_executable_path().exists()
