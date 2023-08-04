import shutil
from tempfile import mkdtemp

from django.test import SimpleTestCase

from django_tailwind_cli.utils import Config


class ConfigTestCase(SimpleTestCase):
    """Test the Config class."""

    def setUp(self):
        """Set up the test case."""

        self.tempdir = mkdtemp()

    def tearDown(self) -> None:
        """Remove the temporary directory."""

        shutil.rmtree(self.tempdir)

    def test_defaults(self):
        """Default settings are correct."""
        config = Config()
        self.assertEqual(config.tailwind_version, "3.3.3")
        self.assertEqual(config.cli_path, "~/.local/bin/")
        self.assertIsNone(config.src_css)
        self.assertEqual(config.dist_css, "css/tailwind.css")
        self.assertEqual(config.config_file, "tailwind.config.js")
        self.assertIn("3.3.3", config.get_download_url())
        self.assertIn("3.3.3", str(config.get_full_cli_path()))

    def test_validate_settings(self):
        """Test that validate_settings raises an exception when STATICFILES_DIRS is empty."""

        with self.settings(STATICFILES_DIRS=[]):
            config = Config()
            with self.assertRaises(ValueError):
                config.validate_settings()

    def test_get_full_config_file_path(self):
        """Test that get_full_config_path returns the correct path."""

        with self.settings(BASE_DIR="/home/user/project"):
            config = Config()
            self.assertEqual(str(config.get_full_config_file_path()), "/home/user/project/tailwind.config.js")

        with self.settings(BASE_DIR="/home/user/project", TAILWIND_CLI_CONFIG_FILE="config/tailwind.config.js"):
            config = Config()
            self.assertEqual(str(config.get_full_config_file_path()), "/home/user/project/config/tailwind.config.js")

    def test_get_full_dist_css_path(self):
        """Test that get_full_dist_css_path returns the correct path."""

        with self.settings(BASE_DIR="/home/user/project", STATICFILES_DIRS=None):
            config = Config()
            with self.assertRaises(ValueError):
                config.get_full_dist_css_path()

        with self.settings(BASE_DIR="/home/user/project", STATICFILES_DIRS=["/home/user/project"]):
            config = Config()
            self.assertEqual(str(config.get_full_dist_css_path()), "/home/user/project/css/tailwind.css")

    def test_get_full_src_css_path(self):
        """Test that get_full_src_css_path returns the correct path."""

        with self.settings(BASE_DIR="/home/user/project"):
            config = Config()
            with self.assertRaises(ValueError):
                config.get_full_src_css_path()

        with self.settings(BASE_DIR="/home/user/project", TAILWIND_CLI_SRC_CSS="css/source.css"):
            config = Config()
            self.assertEqual(str(config.get_full_src_css_path()), "/home/user/project/css/source.css")

    def test_get_full_cli_path(self):
        """Test that get_full_dist_css_url returns the correct url."""

        with self.settings(BASE_DIR="/home/user/project"):
            config = Config()
            self.assertTrue("/.local/bin/tailwindcss-" in str(config.get_full_cli_path()))

        with self.settings(BASE_DIR="/home/user/project", TAILWIND_CLI_PATH="/opt/bin"):
            config = Config()
            self.assertTrue(str(config.get_full_cli_path()).startswith("/opt/bin/tailwindcss-"))
