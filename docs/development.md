---
hide:
  - navigation
---

# Development Guide

This project is managed with [hatch](https://hatch.pypa.io/latest/). So in order to setup an development environment, you have to [install hatch](https://hatch.pypa.io/latest/install/) first. It might be also a good idea, if you are new to hatch, that you work through the [introduction](https://hatch.pypa.io/latest/intro/).

## Create default environment

To create the default environment for development, you can simply run the following command. This will setup the environment and install all the dependencies.

```shell
hatch env create
```

## Entering the default environment

Enter the fresh environment with the following command.

```shell
hatch env shell
```

## Running the test suite

The test suite uses the [matrix feature](https://hatch.pypa.io/latest/environment/#matrix) of hatch and runs the tests against the Python versions 3.8-3.12 and the Django versions 3.2, 4.1 and 4.2. Python versions that are not installed locally are skipped.

```shell
hatch run test:test
```

If you want to get coverage output, call the following command.

```shell
hatch run test:cov
```

### Testing individual Python and/or Django versions

Based on the matrix hatch creates a bunch of virtual environments to use for testing:

| Envs            |                 |                 |
| --------------- | --------------- | --------------- |
| test.py3.8-3.2  | test.py3.8-4.1  | test.py3.8-4.2  |
| test.py3.9-3.2  | test.py3.9-4.1  | test.py3.9-4.2  |
| test.py3.10-3.2 | test.py3.10-4.1 | test.py3.10-4.2 |
| test.py3.11-3.2 | test.py3.11-4.1 | test.py3.11-4.2 |
| test.py3.12-3.2 | test.py3.12-4.1 | test.py3.12-4.2 |

You can either test against a certain version of Python and all versions of Django by picking the Python version.

```
hatch run +py=3.8 test:test
```

Or you can pick a certain Django version and test against all Python versions.

```
hatch run +django=4.1 test:test
```

Or you can pick an individual environment.

```
hatch run test.py3.8-3.2:test
```

## Running formatters, linters and type checking

The projects uses [pyright](https://pypi.org/project/pyright/) for type checking, [black](https://pypi.org/project/black/) to check the code formatting, [ruff](https://pypi.org/project/ruff/) for linting Python code and [curlylint](https://pypi.org/project/curlylint/) for linting templates.

The `pyproject.toml` contains configuration for all the tools, which will also be used by the corresponding IDE extensions.

Run **all** linters and checkers.

```
hatch run lint:all
```

Run **pyright**, **ruff** and **black** on the Python code.

```
hatch run lint:python
```

Run **curlylint** on the template code.

```
hatch run lint:templates
```

## pre-commit setup

The project uses [pre-commit](https://pre-commit.com) to maintain the desired code quality. Instead of using the official `pre-commit` hooks, the project use the locally installed versions which are also used for the formatters, linters and type checkers.

```yaml
default_language_version:
  python: python3.8

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
        exclude: "^tests/__snapshots__"
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-symlinks
      - id: check-json

  - repo: local
    hooks:
      - id: pyright
        name: Run pyright
        entry: hatch run lint:run-pyright
        language: system
        files: \.py$
      - id: black
        name: Run black
        entry: hatch run lint:run-black
        language: system
        files: \.py$
      - id: ruff
        name: Run ruff
        entry: hatch run lint:run-ruff
        language: system
        files: \.py$
      - id: curlylint
        name: Run curlylint
        entry: hatch run lint:run-curlylint
        language: system
        files: \.html$
```

## Removing virtualenvs

From time to time you might want to give the virtual environments a fresh start. You can prune the envs with the following command.

```
hatch env prune
```
