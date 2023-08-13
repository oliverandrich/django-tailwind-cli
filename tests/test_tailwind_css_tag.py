from typing import Any, Dict, Union

from django.conf import LazySettings
from django.template import engines


def test_tailwind_css_in_production(settings: LazySettings, snapshot: Any):
    settings.DEBUG = False
    template_string = """
    {% load tailwind_cli %}
    {% tailwind_css %}
    """
    assert _render(template_string) == snapshot


def test_tailwind_css_in_devmode(settings: LazySettings, snapshot: Any):
    settings.DEBUG = False
    template_string = """
    {% load tailwind_cli %}
    {% tailwind_css %}
    """
    assert _render(template_string) == snapshot


def _render(text: str, context: Union[Dict[str, Any], None] = None):
    if context is None:
        context = {}
    template = engines["django"].from_string(text)
    return template.render(context or {})
