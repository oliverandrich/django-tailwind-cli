from __future__ import annotations

from django import template
from django.conf import settings

from django_tailwind_cli.utils import get_config

register = template.Library()


@register.inclusion_tag("tailwind_cli/tags/tailwind_css.html")
def tailwind_css():
    config = get_config()
    return {
        "debug": settings.DEBUG,
        "tailwind_dist_css": config["TAILWIND_DIST_CSS"],
    }
