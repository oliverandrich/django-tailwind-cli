# type: ignore

import nox
import tomlkit

with open("pyproject.toml", "rb") as f:
    project_data = tomlkit.parse(f.read())["project"]

    # Read supported Python versions from pyproject.toml
    python_versions = []
    for classifier in project_data["classifiers"]:
        if "Programming Language" in classifier and "Python" in classifier:
            split_classifier = classifier.split("::")
            if len(split_classifier) == 3:
                python_versions.append(split_classifier[2].strip())

    # Read supported Django versions from pyproject.toml
    django_versions = []
    for classifier in project_data["classifiers"]:
        if "Framework" in classifier and "Django" in classifier:
            split_classifier = classifier.split("::")
            if len(split_classifier) == 3:
                django_versions.append(split_classifier[2].strip())

invalid_combinations = [("3.8", "5.0"), ("3.9", "5.0"), ("3.11", "3.2"), ("3.12", "3.2")]


@nox.session()
@nox.parametrize(
    "python, django",
    [
        (python, tox_version)
        for python in python_versions
        for tox_version in django_versions
        if (python, tox_version) not in invalid_combinations
    ],
)
def run_testsuite(session, django):
    if session.venv_backend == "uv":
        session.install("-r", "pyproject.toml", "--extra", "test", ".")
    else:
        session.install(".[test]")
    session.install(f"django~={django}")
    session.run("pytest", "--cov", "--cov-append", "--cov-report=")
