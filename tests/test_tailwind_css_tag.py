from typing import Any, Dict, Union

from django.template import engines
from django.test import TestCase, override_settings


class TailwindCssTagTestcase(TestCase):
    def setUp(self):
        self.template_string = """{% spaceless %}
            {% load tailwind_cli %}
            {% tailwind_css %}
            {% endspaceless %}"""

    @override_settings(DEBUG=False)
    def test_tailwind_css_tag_in_production(self):
        rendered_output = self._render(self.template_string)
        self.assertEqual(
            '<link rel="preload" href="/static/css/tailwind.css" as="style"><link rel="stylesheet" href="/static/css/tailwind.css">',  # noqa: E501
            rendered_output,
        )

    @override_settings(DEBUG=True)
    def test_tailwind_css_tag_in_devmode(self):
        rendered_output = self._render(self.template_string)
        self.assertEqual('<link rel="stylesheet" href="/static/css/tailwind.css">', rendered_output)

    def _render(self, text: str, context: Union[Dict[str, Any], None] = None):
        if context is None:
            context = {}
        template = engines["django"].from_string(text)
        return template.render(context or {})
