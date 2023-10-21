from typing import Any, Dict, Union

import pytest
from django.conf import LazySettings
from django.template import engines


@pytest.fixture
def template_string() -> str:
    return "{% spaceless %}{% load tailwind_cli %}{% tailwind_css %}{% endspaceless %}"


def test_tailwind_css_tag_in_production(settings: LazySettings, template_string: str):
    settings.DEBUG = False
    assert (
        '<link rel="preload" href="/static/css/tailwind.css" as="style"><link rel="stylesheet" href="/static/css/tailwind.css">'  # noqa: E501
        == _render(template_string)
    )


def test_tailwind_css_tag_in_devmode(settings: LazySettings, template_string: str):
    settings.DEBUG = True
    assert '<link rel="stylesheet" href="/static/css/tailwind.css">' == _render(template_string)


def _render(text: str, context: Union[Dict[str, Any], None] = None):
    template = engines["django"].from_string(text)
    return template.render(context or {})
