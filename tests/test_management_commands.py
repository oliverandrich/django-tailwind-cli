import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Tuple
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase

from django_tailwind_cli.management.commands.tailwind import DEFAULT_TAILWIND_CONFIG
from django_tailwind_cli.management.commands.tailwind import Command as TailwindCommand
from django_tailwind_cli.utils import Config


def captured_call_command(command: str) -> Tuple[str, str]:
    with redirect_stdout(io.StringIO()) as stdout:
        with redirect_stderr(io.StringIO()) as stdin:
            call_command("tailwind", command)
    return stdout.getvalue(), stdin.getvalue()


@mock.patch("multiprocessing.Process.start", name="process_start")
@mock.patch("multiprocessing.Process.join", name="process_join")
@mock.patch("subprocess.run", name="subprocess_run")
@mock.patch("urllib.request.urlopen", name="urlopen")
@mock.patch("shutil.copyfileobj", name="copyfileobj")
class ManagementCommandsTestCase(TestCase):
    def test_calling_unknown_subcommand(self, *_args: Any):
        with self.assertRaisesRegex(CommandError, r"invalid choice: 'notavalidcommand'"):
            captured_call_command("notavalidcommand")

    def test_invalid_configuration(self, *_args: Any):
        with self.assertRaisesRegex(CommandError, r"Configuration error"):
            with self.settings(STATICFILES_DIRS=None):
                captured_call_command("build")

        with self.assertRaisesRegex(CommandError, r"Configuration error"):
            with self.settings(STATICFILES_DIRS=[]):
                captured_call_command("build")

    def test_download_cli(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                config = Config()
                self.assertFalse(config.get_full_cli_path().exists())
                captured_call_command("build")
                self.assertTrue(config.get_full_cli_path().exists())

    def test_download_cli_without_tailwind_cli_path(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=None, BASE_DIR=Path(tmpdirname)):
                config = Config()
                self.assertFalse(config.get_full_cli_path().exists())
                captured_call_command("build")
                self.assertTrue(config.get_full_cli_path().exists())

    def test_create_tailwind_config_if_non_exists(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                config = Config()

                self.assertFalse(config.get_full_config_file_path().exists())
                captured_call_command("build")
                self.assertTrue(config.get_full_config_file_path().exists())
                self.assertEqual(DEFAULT_TAILWIND_CONFIG, config.get_full_config_file_path().read_text())

    def test_with_existing_tailwind_config(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                config = Config()
                config.get_full_config_file_path().write_text("module.exports = {}")

                captured_call_command("build")
                self.assertTrue(config.get_full_config_file_path().exists())
                self.assertEqual("module.exports = {}", config.get_full_config_file_path().read_text())
                self.assertNotEqual(DEFAULT_TAILWIND_CONFIG, config.get_full_config_file_path().read_text())

    def test_build_subprocess_run_called(
        self,
        _copyfileobj: mock.MagicMock,
        _urlopen: mock.MagicMock,
        subprocess_run: mock.MagicMock,
        _process_join: mock.MagicMock,
        _process_start: mock.MagicMock,
    ):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                captured_call_command("build")
                self.assertGreaterEqual(subprocess_run.call_count, 1)
                self.assertLessEqual(subprocess_run.call_count, 2)

    def test_build_output_of_first_run(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                stdout, _ = captured_call_command("build")
                self.assertIn("Tailwind CSS CLI not found.", stdout)
                self.assertIn("Downloading Tailwind CSS CLI from ", stdout)
                self.assertIn("Built production stylesheet", stdout)

    def test_build_output_of_firtest_build_output_of_second_runt_run(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                captured_call_command("build")
                stdout, _ = captured_call_command("build")
                self.assertNotIn("Tailwind CSS CLI not found.", stdout)
                self.assertNotIn("Downloading Tailwind CSS CLI from ", stdout)
                self.assertIn("Built production stylesheet", stdout)

    @unittest.skipIf(sys.version_info < (3, 9), "The capturing of KeyboardInterupt fails with pytest every other time.")
    def test_build_keyboard_interrupt(
        self,
        _copyfileobj: mock.MagicMock,
        _urlopen: mock.MagicMock,
        subprocess_run: mock.MagicMock,
        _process_join: mock.MagicMock,
        _process_start: mock.MagicMock,
    ):
        subprocess_run.side_effect = KeyboardInterrupt

        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                stdout, _ = captured_call_command("build")
                self.assertIn("Canceled building production stylesheet.", stdout)

    def test_get_build_cmd(self, *_args: Any):
        self.assertNotIn("--input", TailwindCommand().get_build_cmd())
        with self.settings(TAILWIND_CLI_SRC_CSS="css/source.css"):
            self.assertIn("--input", TailwindCommand().get_build_cmd())

    def test_watch_subprocess_run_called(
        self,
        _copyfileobj: mock.MagicMock,
        _urlopen: mock.MagicMock,
        subprocess_run: mock.MagicMock,
        _process_join: mock.MagicMock,
        _process_start: mock.MagicMock,
    ):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                captured_call_command("watch")
                self.assertGreaterEqual(subprocess_run.call_count, 1)
                self.assertLessEqual(subprocess_run.call_count, 2)

    def test_watch_output_of_first_run(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                stdout, _ = captured_call_command("watch")
                self.assertIn("Tailwind CSS CLI not found.", stdout)
                self.assertIn("Downloading Tailwind CSS CLI from ", stdout)

    def test_watch_output_of_second_run(self, *_args: Any):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                captured_call_command("watch")
                stdout, _ = captured_call_command("watch")
                self.assertNotIn("Tailwind CSS CLI not found.", stdout)
                self.assertNotIn("Downloading Tailwind CSS CLI from ", stdout)

    @unittest.skipIf(sys.version_info < (3, 9), "The capturing of KeyboardInterupt fails with pytest every other time.")
    def test_watch_keyboard_interrupt(
        self,
        _copyfileobj: mock.MagicMock,
        _urlopen: mock.MagicMock,
        subprocess_run: mock.MagicMock,
        _process_join: mock.MagicMock,
        _process_start: mock.MagicMock,
    ):
        subprocess_run.side_effect = KeyboardInterrupt

        with tempfile.TemporaryDirectory() as tmpdirname:
            with self.settings(TAILWIND_CLI_PATH=tmpdirname, BASE_DIR=Path(tmpdirname)):
                stdout, _ = captured_call_command("watch")
                self.assertIn("Stopped watching for changes.", stdout)

    def test_get_watch_cmd(self, *_args: Any):
        self.assertNotIn("--input", TailwindCommand().get_watch_cmd())
        with self.settings(TAILWIND_CLI_SRC_CSS="css/source.css"):
            self.assertIn("--input", TailwindCommand().get_watch_cmd())

    def test_runserver(self, *_args: Any):
        captured_call_command("runserver")

    def test_runserver_plus_with_django_extensions_installed(self, *_args: Any):
        captured_call_command("runserver_plus")

    @mock.patch.dict(sys.modules, {"django_extensions": None})
    def test_runserver_plus_without_django_extensions_installed(self, *_args: Any):
        with self.assertRaisesRegex(CommandError, "Missing dependencies."):
            captured_call_command("runserver_plus")

    def test_list_project_templates(self, *_args: Any):
        stdout, _ = captured_call_command("list_templates")
        self.assertIn("templates/tailwind_cli/base.html", stdout)
        self.assertIn("templates/tailwind_cli/tailwind_css.html", stdout)
        self.assertIn("templates/tests/base.html", stdout)
        self.assertNotIn("templates/admin", stdout)

    def test_list_project_all_templates(self, *_args: Any):
        admin_installed_apps = [
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.auth",
            "django.contrib.admin",
            "django.contrib.staticfiles",
            "django_tailwind_cli",
        ]
        with self.settings(INSTALLED_APPS=admin_installed_apps):
            stdout, _ = captured_call_command("list_templates")
            self.assertIn("templates/tailwind_cli/base.html", stdout)
            self.assertIn("templates/tailwind_cli/tailwind_css.html", stdout)
            self.assertIn("templates/tests/base.html", stdout)
            self.assertIn("templates/admin", stdout)
