# Changelog

## 2.0.5

-   Fixed a regression with the default path for the Tailwind CLI.

## 2.0.4

-   The reworked testing setup broke the package. Had to pull 2.0.3 from PyPI.

## 2.0.3

-   Readded support for Python 3.8.
-   Added Python 3.12 to the testing matrix.

## 2.0.2

-   Bugfixes for typing errors.
-   Added missing test code.

## 2.0.0

-   Version 2.0.0 is major refactoring compared to version 1.4.3.
-   No more theme app required.
-   Easier to install.
-   Better out of the box DX.
-   A custom runserver that starts the Tailwind CLI watcher and the debug server in a single terminal session.
-   Less dependencies.

## 1.4.3

-   Fixed broken links in the documentation and README.

## 1.4.0

-   Refactored the project for future extensions.
-   Added proper documetation which is hosted at <https://oliverandrich.github.io/django-tailwind-cli/>.
-   Swichted from django-click to django-rich to implement the management commands.

## 1.3.1

-   Switched back to poetry after a long discussion.

## 1.3.0

-   Switched from poetry to pdm.

## 1.2.2

-   Fixed docstrings.
-   Extended ruff configuration.

## 1.2.1

-   Bumped default tailwind version to 3.2.7.

## 1.2.0

-   Added support for Django 4.2.

## 1.1.0

-   Fixes for documentation.
-   Bumped Tailwind CSS default version to 3.2.4.
-   Updated dependencies.

## 1.0.0

-   Introduced django-click to the project.
-   Refactored the management commands to use [django-click](https://pypi.org/project/django-click/).
-   Renamed the `startwatcher` command to `watch`. I'm a lazy guy. :smile:
-   Switched to tox for local and CI testing.

## 0.9.2

-   Removed `httpx` as a dependency. Downloading the cli is done with `urllib.request.urlopen` once again. Fixes [\#4](https://github.com/oliverandrich/django-tailwind-cli/issues/4)
-   Removed rich-styling information from error strings. Fixes [\#5](https://github.com/oliverandrich/django-tailwind-cli/issues/5)
-   Fixing more typos in the README.md.

## 0.9.1

-   Fixing some typos in the documentation.

## 0.9.0

-   Inital public release.
