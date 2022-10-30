from __future__ import annotations

from typing import Any

import pytest
from click import ClickException  # type: ignore
from django.core.management import call_command

# def test_build(theme_app_path: Any):
#     call_command("tailwind", "build")
#     assert theme_app_path.joinpath("static/css/styles.css").exists()


def test_watch_without_installed_cli(theme_app_path: Any, settings: Any, tmpdir: str):
    # This just changes the tailwind cli path without actually deleting the session scoped cli
    settings.TAILWIND_CLI_PATH = tmpdir
    with pytest.raises(ClickException):
        call_command("tailwind", "watch")
