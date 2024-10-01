"""Tailwind template tags."""

from typing import Union

from django import template

from django_tailwind_cli.conf import settings

register = template.Library()


@register.inclusion_tag("tailwind_cli/tailwind_css.html")
def tailwind_css() -> dict[str, Union[bool, str]]:
    """Template tag to include the css files into the html templates."""
    return {"debug": settings.DEBUG, "tailwind_dist_css": settings.TAILWIND_CLI_DIST_CSS}
