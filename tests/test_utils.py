import pytest
from django.conf import LazySettings

from django_tailwind_cli.utils import Config


@pytest.fixture(autouse=True)
def configure_settings(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"


def test_default_config(config: Config):
    assert "3.3.3" == config.tailwind_version
    assert "~/.local/bin/" == config.cli_path
    assert config.src_css is None
    assert "css/tailwind.css" == config.dist_css
    assert "tailwind.config.js" == config.config_file
    assert "3.3.3" in config.get_download_url()
    assert "3.3.3" in str(config.get_full_cli_path())


def test_validate_settigns(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = []
    with pytest.raises(ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."):
        config.validate_settings()


def test_get_full_config_file_path(config: Config):
    assert "/home/user/project/tailwind.config.js" == str(config.get_full_config_file_path())


def test_get_full_dist_css_path_without_staticfiles_dir_set(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = None
    with pytest.raises(ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."):
        config.get_full_dist_css_path()


def test_get_full_dist_css_path_with_staticfiles_dir_set(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = ["/home/user/project"]
    assert "/home/user/project/css/tailwind.css" == str(config.get_full_dist_css_path())


def test_get_full_src_css_path(config: Config):
    with pytest.raises(ValueError, match="No source CSS file specified. Please set TAILWIND_SRC_CSS in your settings."):
        config.get_full_src_css_path()


def test_get_full_src_css_path_with_changed_tailwind_cli_src_css(config: Config, settings: LazySettings):
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    assert "/home/user/project/css/source.css" == str(config.get_full_src_css_path())


def test_get_full_cli_path(config: Config):
    assert "/.local/bin/tailwindcss-" in str(config.get_full_cli_path())


def test_get_full_cli_path_with_changed_tailwind_cli_path(config: Config, settings: LazySettings):
    settings.TAILWIND_CLI_PATH = "/opt/bin"
    assert "/opt/bin/tailwindcss-" in str(config.get_full_cli_path())
