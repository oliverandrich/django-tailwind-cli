import pytest

from django_tailwind_cli.utils import Config


@pytest.fixture
def config():
    return Config()
