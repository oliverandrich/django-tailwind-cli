from typing import Any, Dict, Union

from django.template import engines
from django.test import SimpleTestCase


class CssTagTestCase(SimpleTestCase):
    """Test the tailwind_css tag."""

    def test_tailwind_css_in_production(self):
        """In production mode a stylesheet preloading directive is injected into the html."""
        with self.settings(DEBUG=False):
            template_string = """
                {% load tailwind_cli %}
                {% tailwind_css %}
                """
            context = {}
            self.assertHTMLEqual(
                """
                <link rel="preload" href="/static/css/tailwind.css" as="style">
                <link rel="stylesheet" href="/static/css/tailwind.css">
                """,
                self._render(template_string, context),
            )

    def test_tailwind_css_in_devmode(self):
        """In development mode no stylesheet preloading directive is injected into the html."""
        with self.settings(DEBUG=True):
            template_string = """
                {% load tailwind_cli %}
                {% tailwind_css %}
                """
            context = {}
            self.assertHTMLEqual(
                """<link rel="stylesheet" href="/static/css/tailwind.css">""",
                self._render(template_string, context),
            )

    def _render(self, text: str, context: Union[Dict[str, Any], None] = None):
        if context is None:
            context = {}
        template = engines["django"].from_string(text)
        return template.render(context or {})
