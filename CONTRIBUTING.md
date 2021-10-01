# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the `MIT` and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

## How to report a bug

Report bugs on the [Issue Tracker](https://github.com/Darkflame72/defectio/issues)

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.


## How to request a feature

Request features on the [Issue Tracker](https://github.com/Darkflame72/defectio/issues)


## How to set up your development environment

You need Python 3.9+ and the following tools:

- [Poetry](https://python-poetry.org)

Install the package with development requirements:

```bash
poetry install
```


## How to test the project

Run the full test suite:

```bash
nox
```

List the available Nox sessions:

```bash
nox --list-sessions
```

You can also run a specific Nox session.
For example, invoke the unit test suite like this:

```bash
nox --session=tests
```

Unit tests are located in the `tests` directory,
and are written using the pytest_ testing framework.


## How to submit changes

Open a pull request to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The Nox test suite should pass without errors and warnings.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before commiting your change, you can install pre-commit as a Git hook by running the following command:

```bash
nox --session=pre-commit -- install
```

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.
