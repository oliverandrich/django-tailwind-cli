set export
set dotenv-load

VENV_DIRNAME := ".venv"

@_default:
    just --list

# setup development environment
@bootstrap:
    if [ -x .venv ]; then \
        echo "Already bootstraped. Exiting."; \
        exit; \
    fi

    if `which -s direnv`; then \
        echo "Creating .envrc and activating direnv"; \
        echo "export VIRTUAL_ENV=.venv" > .envrc; \
        echo "layout python3" >> .envrc; \
        direnv allow; \
    else \
        echo "Creating virtual env in .venv"; \
        just create_venv; \
    fi

    echo "Installing dependencies"
    just upgrade

# create a virtual environment
@create_venv:
    [ -d .venv ] || python3 -m venv $VENV_DIRNAME; \

# upgrade/install all dependencies defined in pyproject.toml
@upgrade: create_venv
    $VENV_DIRNAME/bin/python3 -m pip install --upgrade pip uv; \
    $VENV_DIRNAME/bin/python3 -m uv pip install --upgrade \
        --requirement pyproject.toml --all-extras -e .;

# run pre-commit rules on all files
@lint *ARGS: create_venv
    $VENV_DIRNAME/bin/python3 -m pre_commit run {{ ARGS }} --all-files

# run test suite
@test *ARGS: create_venv
    $VENV_DIRNAME/bin/python3 -m coverage erase
    $VENV_DIRNAME/bin/python3 -m nox --force-venv-backend uv {{ ARGS }}
    $VENV_DIRNAME/bin/python3 -m coverage report
    $VENV_DIRNAME/bin/python3 -m coverage html
