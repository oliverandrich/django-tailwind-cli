# Changelog

## 1.1.0

- Fixes for documentation.
- Bumped Tailwind CSS default version to 3.2.4.
- Updated dependencies.

## 1.0.0

- Introduced django-click to the project.
- Refactored the management commands to use [django-click](https://pypi.org/project/django-click/).
- Renamed the `startwatcher` command to `watch`. I'm a lazy guy. :smile:
- Switched to tox for local and CI testing.

## 0.9.2

- Removed `httpx` as a dependency. Downloading the cli is done with `urllib.request.urlopen` once again. Fixes [\#4](https://github.com/oliverandrich/django-tailwind-cli/issues/4)
- Removed rich-styling information from error strings. Fixes [\#5](https://github.com/oliverandrich/django-tailwind-cli/issues/5)
- Fixing more typos in the README.md.

## 0.9.1

- Fixing some typos in the documentation.

## 0.9.0

- Inital public release.
