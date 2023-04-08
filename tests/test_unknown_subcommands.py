import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_unsupported_subcommand():
    """Unknown subcommands to the tailwind management command raise a `UsageError`."""

    with pytest.raises(CommandError):
        call_command("tailwind", "notavalidcommand")
