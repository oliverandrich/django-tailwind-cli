# Installation

## Install `django-tailwind-cli`

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

    ```htmldjango
    {% load tailwind_cli %}
    ...
    <head>
      ...
      {% tailwind_css %}
      ...
    </head>
    ```

    Or use the [base template](/base_template/) provided by this package.

6. Start the Tailwind CLI in watch mode.

    ```shell
    python manage.py tailwind watch
    ```

## Optional steps

### Install `django-browser-reload`

If you enjoy automatic reloading during development. Install the [django-browser-reload](https://github.com/adamchainz/django-browser-reload) app. The following installation steps are taken from the README of the project.

1. Install `django-browser-reload` inside your Django project.

    ```shell
    python -m pip install django-browser-reload
    ```

2. Ensure you have `django.contrib.staticfiles` in your `INSTALLED_APPS`.

3. Add `django_browser_reload` app to your `INSTALLED_APPS`.

    ```python
    INSTALLED_APPS = [
        ...,
        "django_browser_reload",
        ...,
    ]
    ```

4. Include the app URL’s in your root URLconf(s).

    ```python
    from django.urls import include, path

    urlpatterns = [
        ...,
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    ```

5. Add the middleware.

    ```python
    MIDDLEWARE = [
        # ...
        "django_browser_reload.middleware.BrowserReloadMiddleware",
        # ...
    ]
    ```

    The middleware should be listed after any that encode the response, such as Django’s GZipMiddleware.

    The middleware automatically inserts the required script tag on HTML responses before </body> when DEBUG is True. It does so to every HTML response, meaning it will be included on Django’s debug pages, admin pages, etc. If you want more control, you can instead insert the script tag in your templates—see below.
