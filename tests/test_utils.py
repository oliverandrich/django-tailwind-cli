from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def configure_settings(settings):
    settings.BASE_DIR = "/home/user/project"


def test_default_config(config):
    assert "3.4.3" == config.tailwind_version
    assert Path("~/.local/bin/").expanduser() == config.cli_path
    assert config.src_css is None
    assert "css/tailwind.css" == config.dist_css
    assert "tailwind.config.js" == config.config_file
    assert "3.4.3" in config.get_download_url()
    assert "3.4.3" in str(config.get_full_cli_path())


def test_validate_settigns(config, settings):
    settings.STATICFILES_DIRS = []
    with pytest.raises(ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."):
        config.validate_settings()


def test_get_full_config_file_path(config):
    assert "/home/user/project/tailwind.config.js" == str(config.get_full_config_file_path())


def test_get_full_dist_css_path_without_staticfiles_dir_set(config, settings):
    settings.STATICFILES_DIRS = None
    with pytest.raises(ValueError, match="STATICFILES_DIRS is empty. Please add a path to your static files."):
        config.get_full_dist_css_path()


def test_get_full_dist_css_path_with_staticfiles_dir_set(config, settings):
    settings.STATICFILES_DIRS = ["/home/user/project"]
    assert "/home/user/project/css/tailwind.css" == str(config.get_full_dist_css_path())


def test_get_full_src_css_path(config):
    with pytest.raises(
        ValueError,
        match="No source CSS file specified. Please set TAILWIND_SRC_CSS in your settings.",
    ):
        config.get_full_src_css_path()


def test_get_full_src_css_path_with_changed_tailwind_cli_src_css(config, settings):
    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    assert "/home/user/project/css/source.css" == str(config.get_full_src_css_path())


def test_get_system_and_machine(config, mocker):
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


@pytest.mark.parametrize(
    "platform,machine,result",
    [
        ("Windows", "x86_64", "tailwindcss-windows-x64.exe"),
        ("Windows", "amd64", "tailwindcss-windows-x64.exe"),
        ("Darwin", "aarch64", "tailwindcss-macos-arm64"),
        ("Darwin", "arm64", "tailwindcss-macos-arm64"),
    ],
)
def test_get_download_url(config, mocker, platform, machine, result):
    platform_system = mocker.patch("platform.system")
    platform_machine = mocker.patch("platform.machine")

    platform_system.return_value = platform
    platform_machine.return_value = machine
    assert config.get_download_url().endswith(result)


@pytest.mark.parametrize(
    "platform,machine,result",
    [
        ("Windows", "x86_64", "tailwindcss-windows-x64-3.4.3.exe"),
        ("Windows", "amd64", "tailwindcss-windows-x64-3.4.3.exe"),
        ("Darwin", "aarch64", "tailwindcss-macos-arm64-3.4.3"),
        ("Darwin", "arm64", "tailwindcss-macos-arm64-3.4.3"),
    ],
)
def test_get_full_cli_path(config, mocker, platform, machine, result):
    assert "/.local/bin/tailwindcss-" in str(config.get_full_cli_path())

    platform_system = mocker.patch("platform.system")
    platform_machine = mocker.patch("platform.machine")

    platform_system.return_value = platform
    platform_machine.return_value = machine
    assert str(config.get_full_cli_path()).endswith(result)


def test_get_full_cli_path_with_existing_executable(config, tmp_path, settings):
    settings.TAILWIND_CLI_PATH = tmp_path / "tailwindcss.exe"
    settings.TAILWIND_CLI_PATH.touch(mode=0o755, exist_ok=True)
    assert config.get_full_cli_path() == tmp_path / "tailwindcss.exe"


def test_get_full_cli_path_with_changed_tailwind_cli_path(config, settings):
    settings.TAILWIND_CLI_PATH = "/opt/bin"
    assert "/opt/bin/tailwindcss-" in str(config.get_full_cli_path())
