import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Union

import pytest
from django.core.management import call_command
from django.template import engines
from django_tailwind_cli.utils import (
    download_file,
    get_download_url,
    get_executable_path,
    get_theme_app_path,
)


@pytest.fixture(scope="session")
def installed_cli_path():
    """Install the Tailwind CSS cli."""

    tmpdir = tempfile.mkdtemp()

    # Download CLI
    download_url = get_download_url()
    cli_path = get_executable_path(tmpdir)
    download_file(download_url, cli_path)

    # Yield CLI path
    yield tmpdir

    # Cleanup afterwards
    shutil.rmtree(tmpdir)


@pytest.fixture()
def theme_app_path(settings: Any, installed_cli_path: str, tmpdir: str):
    """Create the tailwind theme app to use during tests."""

    settings.BASE_DIR = Path(tmpdir)
    settings.TAILWIND_CLI_PATH = installed_cli_path

    call_command("tailwind", "init")

    yield get_theme_app_path()


@pytest.fixture()
def render_django():
    """Render a django template."""

    def render(text: str, context: Union[Dict[str, Any], None] = None):
        if context is None:
            context = {}
        template = engines["django"].from_string(text)
        return template.render(context or {})

    return render
