import subprocess
from typing import Any
from unittest.mock import MagicMock

from django.core.management import call_command
from django_tailwind_cli.management.commands.tailwind import Command as TailwindCommand


def test_build(capsys: Any, settings: Any, tmp_path: Any):
    """Test that the build method runs the correct command and prints the correct output."""

    settings.BASE_DIR = tmp_path
    subprocess.run = MagicMock()

    # On the first run, the CLI should be downloaded.
    call_command("tailwind", "build")
    subprocess.run.assert_called_once_with(TailwindCommand().get_build_cmd(), cwd=settings.BASE_DIR, check=True)
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." in captured.out
    assert "Downloading Tailwind CSS CLI from 'https://github.com/tailwindlabs" in captured.out
    assert "Built production stylesheet" in captured.out

    # On a second run, the CLI should be found and not downloaded again.
    call_command("tailwind", "build")
    captured = capsys.readouterr()
    assert "Tailwind CSS CLI not found." not in captured.out
    assert "Downloading Tailwind CSS CLI from 'https://github.com/tailwindlabs" not in captured.out
    assert "Built production stylesheet" in captured.out


def test_build_keyboard_interrupt(capsys: Any, settings: Any, tmp_path: Any):
    """Test that the build method runs the correct command and prints the correct output."""

    settings.BASE_DIR = tmp_path
    subprocess.run = MagicMock(side_effect=KeyboardInterrupt)

    call_command("tailwind", "build")
    subprocess.run.assert_called_once_with(TailwindCommand().get_build_cmd(), cwd=settings.BASE_DIR, check=True)
    assert "Canceled building production stylesheet." in capsys.readouterr().out


def test_build_cmd(capsys: Any, settings: Any, tmp_path: Any):
    """Test that the get_build_cmd method returns the correct command array."""

    build_cmd = TailwindCommand().get_build_cmd()
    assert "--input" not in build_cmd

    settings.TAILWIND_CLI_SRC_CSS = "css/source.css"
    build_cmd = TailwindCommand().get_build_cmd()
    assert "--input" in build_cmd
