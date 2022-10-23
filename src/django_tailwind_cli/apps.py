from __future__ import annotations

from django.apps import AppConfig


class DjangoTailwindCliConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_tailwind_cli"
