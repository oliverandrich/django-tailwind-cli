from django.test import TestCase, override_settings

from django_tailwind_cli.utils import Config


@override_settings(BASE_DIR="/home/user/project")
class UtilsTestCase(TestCase):
    def test_default_config(self):
        config = Config()
        self.assertEqual("3.3.3", config.tailwind_version)
        self.assertEqual("~/.local/bin/", config.cli_path)
        self.assertIsNone(config.src_css)
        self.assertEqual("css/tailwind.css", config.dist_css)
        self.assertEqual("tailwind.config.js", config.config_file)
        self.assertIn("3.3.3", config.get_download_url())
        self.assertIn("3.3.3", str(config.get_full_cli_path()))

    @override_settings(STATICFILES_DIRS=[])
    def test_validate_settigns(self):
        config = Config()
        with self.assertRaises(ValueError):
            config.validate_settings()

    def test_get_full_config_file_path(self):
        config = Config()
        self.assertEqual("/home/user/project/tailwind.config.js", str(config.get_full_config_file_path()))

    @override_settings(STATICFILES_DIRS=None)
    def test_get_full_dist_css_path_without_staticfiles_dir_set(self):
        config = Config()
        with self.assertRaises(ValueError):
            config.get_full_dist_css_path()

    @override_settings(STATICFILES_DIRS=["/home/user/project"])
    def test_get_full_dist_css_path_with_staticfiles_dir_set(self):
        config = Config()
        self.assertEqual("/home/user/project/css/tailwind.css", str(config.get_full_dist_css_path()))

    def test_get_full_src_css_path(self):
        config = Config()
        with self.assertRaises(ValueError):
            config.get_full_src_css_path()

    @override_settings(TAILWIND_CLI_SRC_CSS="css/source.css")
    def test_get_full_src_css_path_with_changed_tailwind_cli_src_css(self):
        config = Config()
        self.assertEqual("/home/user/project/css/source.css", str(config.get_full_src_css_path()))

    def test_get_full_cli_path(self):
        config = Config()
        self.assertIn("/.local/bin/tailwindcss-", str(config.get_full_cli_path()))

    @override_settings(TAILWIND_CLI_PATH="/opt/bin")
    def test_get_full_cli_path_with_changed_tailwind_cli_path(self):
        config = Config()
        self.assertIn("/opt/bin/tailwindcss-", str(config.get_full_cli_path()))
