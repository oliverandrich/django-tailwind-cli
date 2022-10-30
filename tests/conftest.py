from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command

from django_tailwind_cli.utils import (
    download_file,
    get_download_url,
    get_executable_name,
    get_theme_app_path,
)


@pytest.fixture(scope="session")
def installed_cli_path():
    tmpdir = tempfile.mkdtemp()

    # Download CLI
    download_url = get_download_url()
    cli_path = Path(tmpdir) / get_executable_name()
    download_file(download_url, cli_path)

    # Yield CLI path
    yield tmpdir

    # Cleanup afterwards
    shutil.rmtree(tmpdir)


@pytest.fixture()
def theme_app_path(settings: Any, installed_cli_path: str, tmpdir: str):
    settings.BASE_DIR = tmpdir
    settings.TAILWIND_CLI_PATH = installed_cli_path

    call_command("tailwind", "init")

    yield get_theme_app_path()
