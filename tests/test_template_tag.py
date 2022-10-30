from __future__ import annotations

from typing import Any

from django.template import Context, Template


def test_tailwind_css_in_production(settings: Any):
    settings.DEBUG = False
    h = render_template()
    assert '<link rel="preload" href="/static/css/styles.css" as="style">' in h
    assert '<link rel="stylesheet" href="/static/css/styles.css">' in h


def test_tailwind_css_in_devmode(settings: Any):
    settings.DEBUG = True
    h = render_template()
    assert '<link rel="preload" href="/static/css/styles.css" as="style">' not in h
    assert '<link rel="stylesheet" href="/static/css/styles.css">' in h


def render_template():
    return Template(
        """
        {% load tailwind_cli %}
        {% tailwind_css %}
        """
    ).render(Context({}))
