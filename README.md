# django-tailwind-cli

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/oliverandrich/django-tailwind-cli/test.yml?style=flat-square)
[![PyPI](https://img.shields.io/pypi/v/django-tailwind-cli.svg?style=flat-square)](https://pypi.org/project/django-tailwind-cli/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/oliverandrich/django-tailwind-cli?style=flat-square)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json&style=flat-square)](https://python-poetry.org/)

This library provides an integration of [Tailwind CSS](https://tailwindcss.com) for Django that is using on the precompiled versions of the [Tailwind CSS CLI](https://tailwindcss.com/blog/standalone-cli).

The goal of this library is to provided the simplest possible Tailwind integration for your Django project. It took its inspiration from the [Tailwind integration for Phoenix](https://github.com/phoenixframework/tailwind) which completely skips the neccesity of a node installation.

## Installation

1. Install the library.

   ```shell
   python -m pip install django-tailwind-cli
   ```

2. Add `django_tailwind_cli` to `INSTALLED_APPS` in `settings.py`.

   ```python
   INSTALLED_APPS = [
       # other Django apps
       "django_tailwind_cli",
   ]
   ```

3. Configure the `STATICFILES_DIRS` parameter in your `settings.py` if not already configured.

   ```python
   STATICFILES_DIRS = [BASE_DIR / "assets"]
   ```

4. Add template code.

   ```htmldjango
   {% load tailwind_cli %}
   ...
   <head>
     ...
     {% tailwind_css %}
     ...
   </head>
   ```

5. Start the debug server.

   ```shell
   python manage.py tailwind runserver
   ```

Enjoy!

Checkout the detailed [installation guide](https://django-tailwind-cli.andrich.me/installation/) if you want to activate browser reload or the `runserver_plus` management command known from `django-extensions`.

## Features

- Simplest possible integration.
- Management commands:
  - To start the Tailwind CLI in watch mode during development.
  - To build the production grade CSS file for your project.
  - To start a debug server along with the Tailwind CLI in watch mode in a single session.
- Necessary configuration to adapt the library to your project, when the defaults don't fit you.
- A template tag to include the Tailwind CSS file in your project.
- A base template for your project.
- A sane tailwind.config.js that activates all the official plugins and includes a simple HTMX plugin.

## Requirements

Python 3.8 or newer with Django >= 3.2.

## Documentation

The documentation can be found at [https://django-tailwind-cli.andrich.me/](https://django-tailwind-cli.andrich.me/)

## Contributing

If you want to contribute to this project, checkout the [development guide](https://django-tailwind-cli.andrich.me/development/) for details to get your dev environment up and running.

## License

This software is licensed under [MIT license](https://github.com/oliverandrich/django-tailwind-cli/blob/main/LICENSE).
