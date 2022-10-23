from __future__ import annotations

from typing import Any

from django.template import Context, Template


def test_tailwind_css_in_production(settings: Any):
    settings.DEBUG = False
    output = Template(
        """
        {% load tailwind_cli %}
        {% tailwind_css %}
        """
    ).render(Context({}))

    assert '<link rel="preload" href="/static/css/styles.css" as="style">' in output
    assert '<link rel="stylesheet" href="/static/css/styles.css">' in output


def test_tailwind_css_in_sebug(settings: Any):
    settings.DEBUG = True
    output = Template(
        """
        {% load tailwind_cli %}
        {% tailwind_css %}
        """
    ).render(Context({}))

    assert '<link rel="preload" href="/static/css/styles.css" as="style">' not in output
    assert '<link rel="stylesheet" href="/static/css/styles.css">' in output
