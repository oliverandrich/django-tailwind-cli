def test_default_settings(settings):
    assert settings.TAILWIND_CLI_VERSION == "3.4.11"
    assert settings.TAILWIND_CLI_PATH == "~/.local/bin/"
    assert settings.TAILWIND_CLI_AUTOMATIC_DOWNLOAD is True
    assert settings.TAILWIND_CLI_SRC_CSS is None
    assert settings.TAILWIND_CLI_DIST_CSS == "css/tailwind.css"
    assert settings.TAILWIND_CLI_CONFIG_FILE == "tailwind.config.js"
    assert settings.TAILWIND_CLI_SRC_REPO == "tailwindlabs/tailwindcss"
    assert settings.TAILWIND_CLI_ASSET_NAME == "tailwindcss"
