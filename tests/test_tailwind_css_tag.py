import pytest
from django.template import engines


@pytest.fixture
def template_string():
    return "{% spaceless %}{% load tailwind_cli %}{% tailwind_css %}{% endspaceless %}"


def test_tailwind_css_tag_in_production(settings, template_string):
    settings.DEBUG = False
    template = engines["django"].from_string(template_string)
    assert (
        '<link rel="preload" href="/static/css/tailwind.css" as="style"><link rel="stylesheet" href="/static/css/tailwind.css">'  # noqa: E501
        == template.render({})
    )


def test_tailwind_css_tag_in_devmode(settings, template_string):
    settings.DEBUG = True
    template = engines["django"].from_string(template_string)
    assert '<link rel="stylesheet" href="/static/css/tailwind.css">' == template.render({})
