from __future__ import annotations

import pytest
from click import UsageError  # type: ignore
from django.core.management import call_command


def test_unsupported_subcommand():
    with pytest.raises(UsageError):
        call_command("tailwind", "notavalidcommand")
