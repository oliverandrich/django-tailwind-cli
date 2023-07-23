from typing import Any

import pytest
from django_tailwind_cli.utils import Config


def test_defaults(tailwind_config: Config, settings: Any):
    """Default settings are correct."""
    assert tailwind_config.tailwind_version == "3.3.3"
    assert tailwind_config.cli_path is None
    assert tailwind_config.src_css is None
    assert tailwind_config.dist_css == "css/tailwind.css"
    assert tailwind_config.config_file == "tailwind.config.js"
    assert "3.3.3" in tailwind_config.get_download_url()
    assert "3.3.3" in str(tailwind_config.get_full_cli_path())


def test_validate_settings(settings: Any):
    """Test that validate_settings raises an exception when STATICFILES_DIRS is empty."""

    settings.STATICFILES_DIRS = []
    config = Config()
    with pytest.raises(ValueError):
        config.validate_settings()


def test_get_full_config_file_path(settings: Any):
    """Test that get_full_config_path returns the correct path."""

    settings.BASE_DIR = "/home/user/project"
    config = Config()
    assert str(config.get_full_config_file_path()) == "/home/user/project/tailwind.config.js"

    settings.TAILWIND_CLI_CONFIG_FILE = "config/tailwind.config.js"
    config = Config()
    assert str(config.get_full_config_file_path()) == "/home/user/project/config/tailwind.config.js"


def test_get_full_dist_css_path(settings: Any):
    """Test that get_full_dist_css_path returns the correct path."""

    settings.STATICFILES_DIRS = []
    config = Config()
    with pytest.raises(ValueError):
        config.get_full_dist_css_path()

    settings.STATICFILES_DIRS = ["/home/user/project"]
    config = Config()
    assert str(config.get_full_dist_css_path()) == "/home/user/project/css/tailwind.css"


def test_get_full_src_css_path(settings: Any):
    """Test that get_full_src_css_path returns the correct path."""

    config = Config()
    with pytest.raises(ValueError):
        config.get_full_src_css_path()

    settings.BASE_DIR = "/home/user/project"
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    config = Config()
    assert str(config.get_full_src_css_path()) == "/home/user/project/css/source.css"


def test_get_full_cli_path(settings: Any):
    """Test that get_full_cli_path returns the correct path."""

    settings.BASE_DIR = "/home/user/project"
    config = Config()
    assert str(config.get_full_cli_path()).startswith("/home/user/project/tailwindcss-")

    settings.TAILWIND_CLI_PATH = "/opt/bin"
    config = Config()
    assert str(config.get_full_cli_path()).startswith("/opt/bin/tailwindcss-")
