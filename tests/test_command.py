import subprocess
from tempfile import mkdtemp
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.core.management import CommandError, call_command
from django_tailwind_cli.management.commands.tailwind import DEFAULT_TAILWIND_CONFIG
from django_tailwind_cli.utils import Config


def test_invalid_configuration(settings: Any):
    """Invalid configuration raises a `CommandError`."""

    subprocess.run = MagicMock()
    settings.STATICFILES_DIRS = None
    with pytest.raises(CommandError, match=r"Configuration error"):
        call_command("tailwind", "build")


def test_download_cli(settings: Any):
    """Test that the CLI is downloaded if it does not exist."""

    subprocess.run = MagicMock()
    settings.TAILWIND_CLI_PATH = mkdtemp()
    config = Config()
    assert not config.get_full_cli_path().exists()
    call_command("tailwind", "build")
    assert config.get_full_cli_path().exists()


def test_create_tailwind_config_if_non_exists(settings: Any, tmp_path: Any):
    """Test that the CLI is downloaded if it does not exist."""

    subprocess.run = MagicMock()
    settings.BASE_DIR = tmp_path
    config = Config()
    assert not config.get_full_config_file_path().exists()
    call_command("tailwind", "build")
    assert config.get_full_config_file_path().exists()
    assert config.get_full_config_file_path().read_text() == DEFAULT_TAILWIND_CONFIG


def test_use_existing_tailwind_config(settings: Any, tmp_path: Any):
    """Test that the CLI is downloaded if it does not exist."""

    subprocess.run = MagicMock()
    settings.BASE_DIR = tmp_path
    config = Config()
    config.get_full_config_file_path().write_text("module.exports = {}")
    call_command("tailwind", "build")
    assert config.get_full_config_file_path().exists()
    assert config.get_full_config_file_path().read_text() == "module.exports = {}"
    assert config.get_full_config_file_path().read_text() != DEFAULT_TAILWIND_CONFIG
