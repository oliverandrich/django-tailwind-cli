import subprocess
import sys
from typing import Any

import pytest
from django.conf import LazySettings
from django.core.management import CommandError, call_command
from pytest_mock import MockerFixture

from django_tailwind_cli.management.commands.tailwind import DEFAULT_TAILWIND_CONFIG
from django_tailwind_cli.management.commands.tailwind import Command as TailwindCommand
from django_tailwind_cli.utils import Config


@pytest.mark.mock_network_and_subprocess
def test_download_cli(settings: LazySettings, tmpdir: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    config = Config()

    assert not config.get_full_cli_path().exists()
    call_command("tailwind", "build")
    assert config.get_full_cli_path().exists()


@pytest.mark.mock_network_and_subprocess
def test_download_cli_without_tailwind_cli_path(settings: LazySettings, tmpdir: Any):
    settings.TAILWIND_CLI_PATH = None
    settings.BASE_DIR = tmpdir
    config = Config()

    assert not config.get_full_cli_path().exists()
    call_command("tailwind", "build")
    assert config.get_full_cli_path().exists()


def test_calling_unknown_subcommand():
    """Unknown subcommands to the tailwind management command raise a `CommandError`."""

    with pytest.raises(
        CommandError,
        match=r"invalid choice: 'notavalidcommand' \(choose from 'build', 'watch', 'list_templates', 'runserver', 'runserver_plus'\)",  # noqa: E501
    ):
        call_command("tailwind", "notavalidcommand")


def test_invalid_configuration(settings: LazySettings):
    """An invalid configuration raises a `CommandError`."""

    settings.STATICFILES_DIRS = None
    with pytest.raises(CommandError, match=r"Configuration error"):
        call_command("tailwind", "build")

    settings.STATICFILES_DIRS = []
    with pytest.raises(CommandError, match=r"Configuration error"):
        call_command("tailwind", "build")


@pytest.mark.mock_network_and_subprocess
def test_create_tailwind_config_if_non_exists(settings: LazySettings, tmpdir: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    config = Config()

    assert not config.get_full_config_file_path().exists()
    call_command("tailwind", "build")
    assert config.get_full_config_file_path().exists()
    assert config.get_full_config_file_path().read_text() == DEFAULT_TAILWIND_CONFIG


@pytest.mark.mock_network_and_subprocess
def test_with_existing_tailwind_config(settings: LazySettings, tmpdir: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    config = Config()
    config.get_full_config_file_path().write_text("module.exports = {}")

    call_command("tailwind", "build")
    assert config.get_full_config_file_path().exists()
    assert config.get_full_config_file_path().read_text() == "module.exports = {}"
    assert config.get_full_config_file_path().read_text() != DEFAULT_TAILWIND_CONFIG


@pytest.mark.mock_network_and_subprocess
def test_build_subprocess_run_called(settings: LazySettings, tmpdir: Any, mocker: MockerFixture):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    subprocess_run = mocker.spy(subprocess, "run")

    call_command("tailwind", "build")
    assert 1 <= subprocess_run.call_count <= 2


@pytest.mark.mock_network_and_subprocess
def test_build_output_of_first_run(settings: LazySettings, tmpdir: Any, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir

    call_command("tailwind", "build")
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." in captured.out
    assert "Downloading Tailwind CSS CLI from " in captured.out
    assert "Built production stylesheet" in captured.out


@pytest.mark.mock_network_and_subprocess
def test_build_output_of_second_run(settings: LazySettings, tmpdir: Any, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir

    call_command("tailwind", "build")
    captured = capsys.readouterr()

    call_command("tailwind", "build")
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." not in captured.out
    assert "Downloading Tailwind CSS CLI from " not in captured.out
    assert "Built production stylesheet" in captured.out


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="The capturing of KeyboardInterupt fails with pytest every other time."
)
@pytest.mark.mock_network_and_subprocess
def test_build_keyboard_interrupt(settings: LazySettings, tmpdir: Any, mocker: MockerFixture, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    subprocess_run = mocker.spy(subprocess, "run")
    subprocess_run.side_effect = KeyboardInterrupt

    call_command("tailwind", "build")
    captured = capsys.readouterr()
    assert "Canceled building production stylesheet." in captured.out


def test_get_build_cmd(settings: LazySettings):
    assert "--input" not in TailwindCommand().get_build_cmd()
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    assert "--input" in TailwindCommand().get_build_cmd()


@pytest.mark.mock_network_and_subprocess
def test_watch_subprocess_run_called(settings: LazySettings, tmpdir: Any, mocker: MockerFixture):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    subprocess_run = mocker.spy(subprocess, "run")

    call_command("tailwind", "watch")
    assert 1 <= subprocess_run.call_count <= 2


@pytest.mark.mock_network_and_subprocess
def test_watch_output_of_first_run(settings: LazySettings, tmpdir: Any, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir

    call_command("tailwind", "watch")
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." in captured.out
    assert "Downloading Tailwind CSS CLI from " in captured.out


@pytest.mark.mock_network_and_subprocess
def test_watch_output_of_second_run(settings: LazySettings, tmpdir: Any, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir

    call_command("tailwind", "watch")
    captured = capsys.readouterr()

    call_command("tailwind", "watch")
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." not in captured.out
    assert "Downloading Tailwind CSS CLI from " not in captured.out


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="The capturing of KeyboardInterupt fails with pytest every other time."
)
@pytest.mark.mock_network_and_subprocess
def test_watch_keyboard_interrupt(settings: LazySettings, tmpdir: Any, mocker: MockerFixture, capsys: Any):
    settings.TAILWIND_CLI_PATH = tmpdir
    settings.BASE_DIR = tmpdir
    subprocess_run = mocker.spy(subprocess, "run")
    subprocess_run.side_effect = KeyboardInterrupt

    call_command("tailwind", "watch")
    captured = capsys.readouterr()
    assert "Stopped watching for changes." in captured.out


def test_get_watch_cmd(settings: LazySettings):
    assert "--input" not in TailwindCommand().get_watch_cmd()
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    assert "--input" in TailwindCommand().get_watch_cmd()


@pytest.mark.mock_network_and_subprocess
def test_runserver():
    call_command("tailwind", "runserver")


@pytest.mark.mock_network_and_subprocess
def test_runserver_plus_with_django_extensions_installed():
    call_command("tailwind", "runserver_plus")


@pytest.mark.mock_network_and_subprocess
def test_runserver_plus_without_django_extensions_installed(mocker: MockerFixture):
    mocker.patch.dict(sys.modules, {"django_extensions": None})
    with pytest.raises(CommandError, match=r"Missing dependencies."):
        call_command("tailwind", "runserver_plus")


def test_list_project_templates(capsys: Any):
    call_command("tailwind", "list_templates")
    captured = capsys.readouterr()
    assert "templates/tailwind_cli/base.html" in captured.out
    assert "templates/tailwind_cli/tailwind_css.html" in captured.out
    assert "templates/tests/base.html" in captured.out
    assert "templates/admin" not in captured.out


def test_list_all_templates(settings: LazySettings, capsys: Any):
    admin_installed_apps = [
        "django.contrib.contenttypes",
        "django.contrib.messages",
        "django.contrib.auth",
        "django.contrib.admin",
        "django.contrib.staticfiles",
        "django_tailwind_cli",
    ]
    settings.INSTALLED_APPS = admin_installed_apps

    call_command("tailwind", "list_templates")
    captured = capsys.readouterr()
    assert "templates/tailwind_cli/base.html" in captured.out
    assert "templates/tailwind_cli/tailwind_css.html" in captured.out
    assert "templates/tests/base.html" in captured.out
    assert "templates/admin" in captured.out
