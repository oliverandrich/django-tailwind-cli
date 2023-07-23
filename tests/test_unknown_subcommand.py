import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_unknown_subcommand():
    """Unknown subcommands to the tailwind management command raise a `UsageError`."""

    with pytest.raises(
        CommandError, match=r"invalid choice: 'notavalidcommand' \(choose from 'build', 'watch', 'runserver'\)"
    ):
        call_command("tailwind", "notavalidcommand")
