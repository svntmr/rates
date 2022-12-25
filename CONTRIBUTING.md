# Contributing

Contributions to the project are welcome! To contribute, please create a pull
request and make sure that the changes pass the CI pipeline.

## Virtual Environment

To use the right version of Python, Python 3.10, and the right versions of the
libraries, it's recommended to use a virtual environment for development:

```sh
# Make sure that python3.10 exists before executing this command.
python3.10 -m venv .env
source .env/bin/activate
python3 --version # Should return `Python 3.10.x`
# Upgrade pip
python3 -m pip install --upgrade pip
# Install python packages required for development
make install
# or
python3 -m pip install -r requirements.txt
```

### Small note on requirements files

Project has three files with requirements divided by their usage:

- [requirements.txt](requirements.txt) is a 'compilation' file that installs everything you need for development
- [requirements-additional.txt](requirements-additional.txt) is a file with dependencies used in linting/testing/CI scripts
- [requirements-core.txt](requirements-core.txt) is a file with core dependencies needed by project to run

## CI pipeline

The GitHub CI pipeline consists of several workflows defined in [.github/workflows](.github/workflows) folder.

The following subsections will help you to keep a CI pipeline green.

### Pre-commit hooks

To prevent some types of errors such as formatting errors from making the CI
pipeline fail, we recommend to use pre-commit hooks. You can either edit the Git
file `.git/hooks/pre-commit`, or use the Python
[pre-commit](https://pre-commit.com/) program:

```sh
python3 -m pip install pre-commit
pre-commit --version
```

Install the pre-commit hooks defined in
[.pre-commit-config.yaml](.pre-commit-config.yaml) with the following command:

```sh
pre-commit install
pre-commit install --hook-type post-commit
```

Each `git commit` command will trigger these hooks and prevent from committing
some types of errors.

To start pre-commit checks manually:

```shell
pre-commit run --all-files
```

### Formatting code

If you want to understand why it is important to format code, have a look at
this page about [Why Prettier](https://prettier.io/docs/en/why-prettier.html).

### Formatting Python code

#### CLI

Repo uses [black](https://github.com/psf/black) as code formatter. To run `black` locally, execute the following commands:

```sh
# Installs `black` using `pip`
python3 -m pip install black
# Checks if the Python files in the current directory are correctly formatted
black --diff --check .
# Executes `black` on the current directory
black .
```

To reduce the risk of committing changes that are not correctly formatted, we
recommend to use pre-commit hooks, see the previous section
[Pre-commit hooks](#pre-commit-hooks).

### Running tests

`rates` uses `pytest`-based tests to ensure that code works as
expected and that new changes didn't break anything

```shell
pytest  # execute tests
# or
make run-tests  # execute tests using make
```
