from appconf import AppConf
from django.conf import settings  # noqa: F401

DEFAULT_SRC_REPO = "tailwindlabs/tailwindcss"


class TailwindCliAppConfig(AppConf):
    VERSION = "3.4.11"
    PATH = "~/.local/bin/"
    AUTOMATIC_DOWNLOAD = True
    SRC_CSS = None
    DIST_CSS = "css/tailwind.css"
    CONFIG_FILE = "tailwind.config.js"
    SRC_REPO = "tailwindlabs/tailwindcss"
    ASSET_NAME = "tailwindcss"

    class Meta:
        prefix = "TAILWIND_CLI"
