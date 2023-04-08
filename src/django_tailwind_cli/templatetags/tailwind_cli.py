"""Tailwind template tags."""


from django import template
from django.conf import settings

from django_tailwind_cli.utils import get_config

register = template.Library()


@register.inclusion_tag("tailwind_cli/tailwind_css.html")
def tailwind_css():
    """Template tag to include the css files into the html templates."""
    config = get_config()
    return {
        "debug": settings.DEBUG,
        "tailwind_dist_css": config["TAILWIND_DIST_CSS"],
    }
