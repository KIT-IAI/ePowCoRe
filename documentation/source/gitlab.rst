Gitlab Pipelines
================

The project contains a Gitlab CI that generates a HTML version of the documentation and generates a code quality report with mypy.

The documentation pipeline is configured to run on every push to the master branch, the codequality is checked on every push.

Tests are not run on the CI, as the required software is not available on the Gitlab runners or licensing does not allow it.