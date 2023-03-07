import pytest
from click import UsageError  # type: ignore
from django.core.management import call_command


def test_unsupported_subcommand():
    """Unknown subcommands to the tailwind management command raise a `UsageError`."""

    with pytest.raises(UsageError):
        call_command("tailwind", "notavalidcommand")
