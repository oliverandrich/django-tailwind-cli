from pathlib import Path

import pytest
from django.conf import LazySettings
from pytest_mock import MockerFixture

from django_tailwind_cli.utils import Config


@pytest.fixture(autouse=True)
def configure_settings(settings: LazySettings):
    settings.BASE_DIR = "/home/user/project"


def test_default_config(config: Config):
    assert "3.4.0" == config.tailwind_version
    assert Path("~/.local/bin/").expanduser() == config.cli_path
    assert config.src_css is None
    assert "css/tailwind.css" == config.dist_css
    assert "tailwind.config.js" == config.config_file
    assert "3.4.0" in config.get_download_url()
    assert "3.4.0" in str(config.get_full_cli_path())


def test_validate_settigns(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = []
    with pytest.raises(
        ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."
    ):
        config.validate_settings()


def test_get_full_config_file_path(config: Config):
    assert "/home/user/project/tailwind.config.js" == str(config.get_full_config_file_path())


def test_get_full_dist_css_path_without_staticfiles_dir_set(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = None
    with pytest.raises(
        ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."
    ):
        config.get_full_dist_css_path()


def test_get_full_dist_css_path_with_staticfiles_dir_set(config: Config, settings: LazySettings):
    settings.STATICFILES_DIRS = ["/home/user/project"]
    assert "/home/user/project/css/tailwind.css" == str(config.get_full_dist_css_path())


def test_get_full_src_css_path(config: Config):
    with pytest.raises(
        ValueError,
        match="No source CSS file specified. Please set TAILWIND_SRC_CSS in your settings.",
    ):
        config.get_full_src_css_path()


def test_get_full_src_css_path_with_changed_tailwind_cli_src_css(
    config: Config, settings: LazySettings
):
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    assert "/home/user/project/css/source.css" == str(config.get_full_src_css_path())


def test_get_system_and_machine(config: Config, mocker: MockerFixture):
    platform_system = mocker.patch("platform.system")

    platform_system.return_value = "Windows"
    [system, _] = config.get_system_and_machine()
    assert system == "windows"

    platform_system.return_value = "Darwin"
    [system, _] = config.get_system_and_machine()
    assert system == "macos"

    platform_machine = mocker.patch("platform.machine")

    platform_machine.return_value = "x86_64"
    [_, machine] = config.get_system_and_machine()
    assert machine == "x64"

    platform_machine.return_value = "amd64"
    [_, machine] = config.get_system_and_machine()
    assert machine == "x64"

    platform_machine.return_value = "aarch64"
    [_, machine] = config.get_system_and_machine()
    assert machine == "arm64"


def test_get_download_url(config: Config, mocker: MockerFixture):
    platform_system = mocker.patch("platform.system")
    platform_machine = mocker.patch("platform.machine")

    platform_system.return_value = "Windows"
    platform_machine.return_value = "x86_64"
    assert config.get_download_url().endswith("tailwindcss-windows-x64.exe")

    platform_system.return_value = "Windows"
    platform_machine.return_value = "amd64"
    assert config.get_download_url().endswith("tailwindcss-windows-x64.exe")

    platform_system.return_value = "Darwin"
    platform_machine.return_value = "aarch64"
    assert config.get_download_url().endswith("tailwindcss-macos-arm64")

    platform_system.return_value = "Darwin"
    platform_machine.return_value = "arm64"
    assert config.get_download_url().endswith("tailwindcss-macos-arm64")


def test_get_full_cli_path(config: Config, mocker: MockerFixture):
    assert "/.local/bin/tailwindcss-" in str(config.get_full_cli_path())

    platform_system = mocker.patch("platform.system")
    platform_machine = mocker.patch("platform.machine")

    platform_system.return_value = "Windows"
    platform_machine.return_value = "x86_64"
    assert str(config.get_full_cli_path()).endswith("tailwindcss-windows-x64-3.4.0.exe")

    platform_system.return_value = "Windows"
    platform_machine.return_value = "amd64"
    assert str(config.get_full_cli_path()).endswith("tailwindcss-windows-x64-3.4.0.exe")

    platform_system.return_value = "Darwin"
    platform_machine.return_value = "aarch64"
    assert str(config.get_full_cli_path()).endswith("tailwindcss-macos-arm64-3.4.0")

    platform_system.return_value = "Darwin"
    platform_machine.return_value = "arm64"
    assert str(config.get_full_cli_path()).endswith("tailwindcss-macos-arm64-3.4.0")


def test_get_full_cli_path_with_existing_executable(
    config: Config, tmp_path: Path, settings: LazySettings
):
    settings.TAILWIND_CLI_PATH = tmp_path / "tailwindcss.exe"
    settings.TAILWIND_CLI_PATH.touch(mode=0o755, exist_ok=True)
    assert config.get_full_cli_path() == tmp_path / "tailwindcss.exe"


def test_get_full_cli_path_with_changed_tailwind_cli_path(config: Config, settings: LazySettings):
    settings.TAILWIND_CLI_PATH = "/opt/bin"
    assert "/opt/bin/tailwindcss-" in str(config.get_full_cli_path())
