from typing import Any, Callable, Dict, Union

import pytest
from django.template import engines
from django_tailwind_cli.utils import Config


@pytest.fixture()
def tailwind_config() -> Config:
    """Return the settings for the django-tailwind-cli module read from the settings."""
    return Config()


@pytest.fixture()
def render_django() -> Callable[[str, Union[Dict[str, Any], None]], str]:
    """Render a django template."""

    def render(text: str, context: Union[Dict[str, Any], None] = None):
        if context is None:
            context = {}
        template = engines["django"].from_string(text)
        return template.render(context or {})

    return render
