from typing import Any

from django.core.management import call_command


def test_listtemplates(theme_app_path: Any, snapshot: Any, capsys: Any):
    """`tailwind listtemplates` lists all available templates."""
    call_command("tailwind", "listtemplates")
    captured = capsys.readouterr()
    assert captured.out == snapshot
