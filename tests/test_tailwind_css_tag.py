from typing import Any


def test_tailwind_css_in_production(settings: Any, snapshot: Any, render_django: Any):
    """In production mode a stylesheet preloading directive is injected into the html."""

    settings.DEBUG = False
    template_string = """
        {% load tailwind_cli %}
        {% tailwind_css %}
        """
    context = {}

    assert render_django(template_string, context) == snapshot


def test_tailwind_css_in_devmode(settings: Any, snapshot: Any, render_django: Any):
    """In development mode no stylesheet preloading directive is injected into the html."""

    settings.DEBUG = True
    template_string = """
        {% load tailwind_cli %}
        {% tailwind_css %}
        """
    context = {}

    assert render_django(template_string, context) == snapshot
