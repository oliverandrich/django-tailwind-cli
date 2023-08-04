"""Tailwind template tags."""


from typing import Dict, Union

from django import template
from django.conf import settings

from django_tailwind_cli.utils import Config

register = template.Library()


@register.inclusion_tag("tailwind_cli/tailwind_css.html")
def tailwind_css() -> Dict[str, Union[bool, str]]:
    """Template tag to include the css files into the html templates."""
    config = Config()
    return {"debug": settings.DEBUG, "tailwind_dist_css": config.dist_css}
