# type: ignore

import nox


@nox.session(venv_backend="uv")
@nox.parametrize(
    "python, django",
    [
        (python, tox_version)
        for python in ("3.9", "3.10", "3.11", "3.12")
        for tox_version in ("3.2", "4.2", "5.0")
        if (
            (python, tox_version) != ("3.9", "5.0")
            and (python, tox_version) != ("3.11", "3.2")
            and (python, tox_version) != ("3.12", "3.2")
        )
    ],
)
def run_testsuite(session, django):
    session.install("-r", "pyproject.toml", "--extra", "django-extensions", "--extra", "dev", ".")
    session.install(f"django~={django}")
    session.run("pytest")
