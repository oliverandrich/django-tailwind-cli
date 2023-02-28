# django-tailwind-cli

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/oliverandrich/django-tailwind-cli/test.yml?style=for-the-badge)
[![PyPI](https://img.shields.io/pypi/v/django-tailwind-cli.svg?style=for-the-badge)](https://pypi.org/project/django-tailwind-cli/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/oliverandrich/django-tailwind-cli?style=for-the-badge)

This project provides an integration of Tailwind CSS for Django that is based on the precompiled versions of the [Tailwind CSS CLI](https://tailwindcss.com/blog/standalone-cli).

It is inspired by the implementation of the [Tailwind integration for Phoenix](https://github.com/phoenixframework/tailwind) which completely skips the neccesity of a node installation. So it is a perfect match, if you are a user of [htmx](https://htmx.org) or any other framework that tries to avoid JavaScript coding in your web app. My personal motivation was, that I discovered that I never needed any other plugin besides the official plugins, which are already included in the CLI.

> If you want to use node or you have to use it because of other dependencies, then the package [django-tailwind](https://github.com/timonweb/django-tailwind) by [Tim Kamamin](https://github.com/timonweb) might be a better solution for you.

## Features

- Management Commands...
  - ...to install the the CLI for your operating system and machine architecture.
  - ...to start the CLI in watch mode to incrementally compile your style sheet.
  - ...to create a theme app which includes a basic stylesheet and a tailwind configuration which you can extend.
  - ...to build the production ready CSS file.
- A template tag to include the CSS file in your base template.
- All the official plugins (typography, form, line-clamp, and aspect-ratio) integrated in the CLI are activated in the default configuration.

## Requirements

Python 3.8 or newer with Django >= 3.2.

## Installation

1. Install the package inside your Django project.

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

3. Run the management command to install the cli and initialize the theme app.

    ```shell
    python manage.py tailwind installcli
    python manage.py tailwind init
    ```

    This installs the CLI to `$HOME/.local/bin/` and creates a new app in your project with the name `theme`.

4. Add the new theme app to `INSTALLED_APPS` in `settings.py`.

    ```python
    INSTALLED_APPS = [
        # other Django apps
        "django_tailwind_cli",
        "theme",
    ]
    ```

5. Edit your base template to include Tailwind's stylesheet.

    ```html
    {% load tailwind_cli %}
   ...
   <head>
      ...
      {% tailwind_css %}
      ...
   </head>
    ```

6. Start the Tailwind CLI in watch mode.

    ```shell
    python manage.py tailwind watch
    ```

7. (Optional) Add [django-browser-reload](https://github.com/adamchainz/django-browser-reload) if you enjoy automatic reloading during development.

## Configuration

The default configuration for this package is.

```python
{
    "TAILWIND_VERSION": "3.1.8",
    "TAILWIND_CLI_PATH": "~/.local/bin/",
    "TAILWIND_THEME_APP": "theme",
    "TAILWIND_SRC_CSS": "src/styles.css",
    "TAILWIND_DIST_CSS": "css/styles.css",
}
```

- Set `TAILWIND_VERSION` to the version of Tailwind you want to use.
- `TAILWIND_CLI_PATH` defines where the CLI is installed. The default makes sense on macOS or Linux. On Windows it might helpful to pick a different path.
- `TAILWIND_THEME_APP` defines the name of the theme application created by the management command `tailwind init`.
- `TAILWIND_SRC_CSS` and `TAILWIND_DIST_CSS` defines the internal structure of the theme app. `TAILWIND_DIST_CSS` is a path always relative to the `static` folder of the theme app.

## Management Commands

| Command                 | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| `tailwind installcli`   | Download the CLI version `TAILWIND_VERSION` to `TAILWIND_CLI_PATH`. |
| `tailwind init`         | Create a new theme app with the name `TAILWIND_THEME_APP` inside the `settings.BASE_DIR` of your project. |
| `tailwind watch`        | Start the CLI in watch and incremental compilation mode.            |
| `tailwind build`        | Create a production ready build of the Tailwind stylesheet. You have to run this before calling the `collectstatic` command. |

## Template Tags

This package provides a single template tag to include the Tailwind CSS. Depending on the value of `settings.DEBUG` it activates preload or not.

```html
{% load tailwind_cli %}
...
<head>
    ...
    {% tailwind_css %}
    ...
</head>
```

`DEBUG == False` creates the following output:

```html
<link rel="preload" href="/static/css/styles.css" as="style">
<link rel="stylesheet" href="/static/css/styles.css">
```

`DEBUG == True` creates this output:

```html
<link rel="stylesheet" href="/static/css/styles.css">
```

## License

This software is licensed under [MIT license](https://github.com/oliverandrich/django-tailwind-cli/blob/main/LICENSE). Copyright (c) 2022 Oliver Andrich.
