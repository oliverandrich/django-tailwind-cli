import shutil
import subprocess
import sys
import urllib.request
from contextlib import contextmanager
from io import StringIO
from tempfile import mkdtemp
from unittest.mock import MagicMock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase

from django_tailwind_cli.management.commands.tailwind import DEFAULT_TAILWIND_CONFIG
from django_tailwind_cli.management.commands.tailwind import Command as TailwindCommand
from django_tailwind_cli.utils import Config


class DownloadCliTestCase(SimpleTestCase):
    """Test the download of the Tailwind CLI."""

    def setUp(self) -> None:
        """Mock subprocesses."""

        subprocess.run = MagicMock()
        self.tempdir = mkdtemp()

    def tearDown(self) -> None:
        """Remove the temporary directory."""

        shutil.rmtree(self.tempdir)

    def test_download_cli(self):
        """Test that the CLI is downloaded if it does not exist."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            config = Config()
            self.assertFalse(config.get_full_cli_path().exists())
            with captured_output():
                call_command("tailwind", "build")
            self.assertTrue(config.get_full_cli_path().exists())


class MockedNetworkingProcessesAndShellToolsTestCase(SimpleTestCase):
    """Test the management commands with mocked networking, subprocesses and shell tools."""

    def setUp(self) -> None:
        """Mock the networking, subprocesses and shell tools."""

        subprocess.run = MagicMock()
        urllib.request.urlopen = MagicMock()
        shutil.copyfileobj = MagicMock()

        self.tempdir = mkdtemp()

    def tearDown(self) -> None:
        """Remove the temporary directory."""

        shutil.rmtree(self.tempdir)


class BasicManagementCommandFunctionalityTestCase(MockedNetworkingProcessesAndShellToolsTestCase):
    """Test the basic functionality of all management commands."""

    def test_calling_unknown_subcommand(self):
        """Unknown subcommands to the tailwind management command raise a `CommandError`."""

        with self.assertRaisesRegex(
            CommandError,
            r"invalid choice: 'notavalidcommand' \(choose from 'build', 'watch', 'list_templates', 'runserver'\)",
        ):
            with captured_output():
                call_command("tailwind", "notavalidcommand")

    def test_invalid_configuration(self):
        """An invalid configuration raises a `CommandError`."""

        with self.settings(STATICFILES_DIRS=None):
            with self.assertRaisesRegex(CommandError, r"Configuration error"):
                with captured_output():
                    call_command("tailwind", "build")

        with self.settings(STATICFILES_DIRS=[]):
            with self.assertRaisesRegex(CommandError, r"Configuration error"):
                with captured_output():
                    call_command("tailwind", "build")

    def test_create_tailwind_config_if_non_exists(self):
        """Test creation of the Tailwind config file if it does not exist."""

        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            config = Config()
            self.assertFalse(config.get_full_config_file_path().exists())
            with captured_output():
                call_command("tailwind", "build")
            self.assertTrue(config.get_full_config_file_path().exists())
            self.assertEqual(config.get_full_config_file_path().read_text(), DEFAULT_TAILWIND_CONFIG)

    def test_with_existing_tailwind_config(self):
        """Test that an existing Tailwind config file is not overwritten."""

        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            config = Config()
            config.get_full_config_file_path().write_text("module.exports = {}")
            with captured_output():
                call_command("tailwind", "build")
            self.assertTrue(config.get_full_config_file_path().exists())
            self.assertEqual(config.get_full_config_file_path().read_text(), "module.exports = {}")
            self.assertNotEqual(config.get_full_config_file_path().read_text(), DEFAULT_TAILWIND_CONFIG)


class BuildCommandTestCase(MockedNetworkingProcessesAndShellToolsTestCase):
    """Test the `build` management command."""

    def test_subprocess_run_called(self):
        """Test that the subprocess is called with the correct arguments."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output():
                call_command("tailwind", "build")
            subprocess.run.assert_called_once_with(TailwindCommand().get_build_cmd(), cwd=settings.BASE_DIR, check=True)  # type: ignore  # noqa: E501

    def test_output_of_first_run(self):
        """On the first run, the CLI should be downloaded."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output() as (out, _err):
                call_command("tailwind", "build")
        self.assertIn("Tailwind CSS CLI not found.", out.getvalue())
        self.assertIn("Downloading Tailwind CSS CLI from ", out.getvalue())
        self.assertIn("Built production stylesheet", out.getvalue())

    def test_output_of_second_run(self):
        """On a second run, the CLI should be found and not downloaded again."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output():
                call_command("tailwind", "build")
            with captured_output() as (out, _err):
                call_command("tailwind", "build")
        self.assertNotIn("Tailwind CSS CLI not found.", out.getvalue())
        self.assertNotIn("Downloading Tailwind CSS CLI from ", out.getvalue())
        self.assertIn("Built production stylesheet", out.getvalue())

    def test_build_keyboard_interrupt(self):
        """Test the `build` command with a keyboard interrupt."""
        subprocess.run = MagicMock(side_effect=KeyboardInterrupt)

        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output() as (out, _err):
                call_command("tailwind", "build")
            self.assertIn("Canceled building production stylesheet.", out.getvalue().strip())
            subprocess.run.assert_called_once_with(TailwindCommand().get_build_cmd(), cwd=settings.BASE_DIR, check=True)

    def test_get_build_cmd(self):
        """Test that the `get_build_cmd` method returns the correct command array."""

        build_cmd = TailwindCommand().get_build_cmd()
        self.assertNotIn("--input", build_cmd)

        with self.settings(TAILWIND_CLI_SRC_CSS="css/source.css"):
            build_cmd = TailwindCommand().get_build_cmd()
            self.assertIn("--input", build_cmd)


class WatchCommandTestCase(MockedNetworkingProcessesAndShellToolsTestCase):
    """Test the `build` management command."""

    def test_subprocess_run_called(self):
        """Test that the `watch` command calls the subprocess run method."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output():
                call_command("tailwind", "watch")
            subprocess.run.assert_called_once_with(TailwindCommand().get_watch_cmd(), cwd=settings.BASE_DIR, check=True)  # type: ignore  # noqa: E501

    def test_output_of_first_run(self):
        """On the first run, the CLI should be downloaded."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output() as (out, _err):
                call_command("tailwind", "watch")
        self.assertIn("Tailwind CSS CLI not found.", out.getvalue())
        self.assertIn("Downloading Tailwind CSS CLI from ", out.getvalue())

    def test_output_of_second_run(self):
        """On a second run, the CLI should be found and not downloaded again."""
        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output():
                call_command("tailwind", "watch")
            with captured_output() as (out, _err):
                call_command("tailwind", "watch")
        self.assertNotIn("Tailwind CSS CLI not found.", out.getvalue())
        self.assertNotIn("Downloading Tailwind CSS CLI from ", out.getvalue())

    def test_build_keyboard_interrupt(self):
        """Test the `build` command with a keyboard interrupt."""
        subprocess.run = MagicMock(side_effect=KeyboardInterrupt)

        with self.settings(TAILWIND_CLI_PATH=self.tempdir, BASE_DIR=self.tempdir):
            with captured_output() as (out, _err):
                call_command("tailwind", "watch")
            self.assertIn("Stopped watching for changes.", out.getvalue().strip())

    def test_get_build_cmd(self):
        """Test that the `get_build_cmd` method returns the correct command array."""

        build_cmd = TailwindCommand().get_watch_cmd()
        self.assertNotIn("--input", build_cmd)

        with self.settings(TAILWIND_CLI_SRC_CSS="css/source.css"):
            build_cmd = TailwindCommand().get_watch_cmd()
            self.assertIn("--input", build_cmd)


class ListTemplateCommandTestCase(MockedNetworkingProcessesAndShellToolsTestCase):
    """Test that list_templates command works."""

    def test_list_project_templates(self):
        """Test that the list_templates command returns our two templates."""
        with captured_output() as (out, _err):
            call_command("tailwind", "list_templates")
        self.assertIn("templates/tailwind_cli/base.html", out.getvalue().strip())
        self.assertIn("templates/tailwind_cli/tailwind_css.html", out.getvalue().strip())
        self.assertIn("templates/tests/base.html", out.getvalue().strip())
        self.assertNotIn("templates/admin", out.getvalue().strip())

    def test_list_all_templates(self):
        """Test that app templates are also included."""
        admin_installed_apps = [
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.auth",
            "django.contrib.admin",
            "django.contrib.staticfiles",
            "django_tailwind_cli",
        ]
        with self.settings(INSTALLED_APPS=admin_installed_apps):
            with captured_output() as (out, _err):
                call_command("tailwind", "list_templates")
        self.assertIn("templates/admin", out.getvalue().strip())
        self.assertIn("templates/tailwind_cli/base.html", out.getvalue().strip())
        self.assertIn("templates/tailwind_cli/tailwind_css.html", out.getvalue().strip())


@contextmanager
def captured_output():
    """Capture the output of a function."""

    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
