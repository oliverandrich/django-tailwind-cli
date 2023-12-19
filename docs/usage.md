---
hide:
  - navigation
---

# Usage

!!! question "Do I have to install the Tailwind CLI?"

    **No.** The management commands of this library handle the download and installation of the Tailwind CLI. You don't have to deal with this. But you can configure the installation location and the version of the CLI you want to use. Take a look at the [settings](settings.md) section.

!!! question "Do I have to create my own `tailwind.config.js`?"

    **No.** The management commands also take care of this step. If no `tailwind.config.js` is present in your project, a new one with sane defaults will be created. Afterwards this file will be used and be customized by you. The default location for the file is the `BASE_DIR` of your project, but you can change this. Take a look at the [settings](settings.md) section.

## During development

### Use the debug server of this library

The easiest way to use this library during development is to start the debug server provided by it.

```shell
python manage.py tailwind runserver
```

Optionally you can use `runserver_plus` which requires `django-extensions` to be installed
```shell
python manage.py tailwind runserver_plus
```

This command starts two processes. One is the standard debug server of Django which is normally started by running `python manage.py runserver or runserver_plus`. The other is the Tailwind CLI in watch mode by running `python manage.py tailwind watch`.

Two main advantages of using `runserver_plus` are the following:

- Debug server uses Werkzeug instead of the standard WSGI server for more debugging support.
- Can also use HTTPS with a self-signed certificate for local development.

### Use the standard debug server along with Tailwind CLI in watch mode

If you prefer to use the standard debug server or have written your own extended debug server, you have to start two seperate processes in different shells or with some kind of process manager. One is of course your debug server and the other is the Tailwind CLI in watch mode, which can be started with the following management command.

```shell
python manage.py tailwind watch
```

### Use of this library with Docker Compose

When used in the `watch` mode, the Tailwind CLI requires a TTY-enabled environment to function correctly. In a Docker Compose setup, ensure that the container executing the Tailwind style rebuild command (either `python manage.py tailwind runserver` or `python manage.py tailwind watch`, as noted above) is configured with the `tty: true` setting in your `docker-compose.yml`.

```yaml
web:
  command: python manage.py tailwind runserver
  tty: true

# or

tailwind-sidecar:
  command: python manage.py tailwind watch
  tty: true
```

## In your build process

To create an optimized production built of the stylesheet run the following command. Afterwards you are ready to deploy. Take care the this command is run before `python manage.py collectstatic`.

```shell
python manage.py tailwind build
```
