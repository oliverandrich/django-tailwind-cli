# Based on https://noumenal.es/notes/tailwind/django-integration/
import os
from pathlib import Path
from typing import Any, List, Union

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.utils import get_app_template_dirs


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        template_files: List[str] = []
        app_template_dirs = get_app_template_dirs("templates")
        for app_template_dir in app_template_dirs:
            template_files += self.list_template_files(app_template_dir)
        template_files += self.list_template_files(settings.TEMPLATES[0]["DIRS"])

        self.stdout.write("\n".join(template_files))

    def list_template_files(self, template_dir: Union[str, Path]) -> List[str]:
        template_files: List[str] = []
        for dirpath, _, filenames in os.walk(str(template_dir)):
            for filename in filenames:
                if filename.endswith(".html") or filename.endswith(".txt"):
                    template_files.append(os.path.join(dirpath, filename))
        return template_files
