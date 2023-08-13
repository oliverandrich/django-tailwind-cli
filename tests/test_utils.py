import pytest
from django.conf import LazySettings

from django_tailwind_cli.utils import Config


def test_default_config():
    """Default that the settings are correct."""

    config = Config()
    assert config.tailwind_version == "3.3.3"
    assert config.cli_path == "~/.local/bin/"
    assert config.src_css is None
    assert config.dist_css == "css/tailwind.css"
    assert config.config_file == "tailwind.config.js"
    assert "3.3.3" in config.get_download_url()
    assert "3.3.3" in str(config.get_full_cli_path())


def test_validate_settigns(settings: LazySettings):
    """Test that validate_settings raises an exception when STATICFILES_DIRS is empty."""

    settings.STATICFILES_DIRS = []
    config = Config()
    with pytest.raises(ValueError):
        config.validate_settings()


def test_get_full_config_file_path(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"
    config = Config()
    assert str(config.get_full_config_file_path()) == "/home/user/project/tailwind.config.js"

    settings.BASE_DIR = "/home/user/project"
    settings.TAILWIND_CLI_CONFIG_FILE = "config/tailwind.config.js"
    config = Config()
    assert str(config.get_full_config_file_path()) == "/home/user/project/config/tailwind.config.js"


def test_get_full_dist_css_path(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"
    settings.STATICFILES_DIRS = None
    config = Config()
    with pytest.raises(ValueError):
        config.get_full_dist_css_path()

    settings.BASE_DIR = "/home/user/project"
    settings.STATICFILES_DIRS = ["/home/user/project"]
    config = Config()
    assert str(config.get_full_dist_css_path()) == "/home/user/project/css/tailwind.css"


def test_get_full_src_css_path(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"
    config = Config()
    with pytest.raises(ValueError):
        config.get_full_src_css_path()

    settings.BASE_DIR = "/home/user/project"
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    config = Config()
    assert str(config.get_full_src_css_path()) == "/home/user/project/css/source.css"


def test_get_full_cli_path(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"
    config = Config()
    assert "/.local/bin/tailwindcss-" in str(config.get_full_cli_path())

    settings.BASE_DIR = "/home/user/project"
    settings.TAILWIND_CLI_PATH = "/opt/bin"
    config = Config()
    assert str(config.get_full_cli_path()).startswith("/opt/bin/tailwindcss-")
