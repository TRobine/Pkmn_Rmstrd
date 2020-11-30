# Continous Integration Workflows

This package implements different workflows for CI.
They are organised as follows.

### Testing Suite

Tests are ensured in the `tests` workflow, which triggers on all pushes.
It runs on a matrix of all available operating systems for all supported Python versions (currently `3.6`, `3.7`, and `3.8` until `pyarrow` is good for `3.9`).

### Regular Testing

A `cron` workflow triggers every day at 3am (UTC time) and runs the full testing suite, on all available operating systems and supported Python versions.

### Publishing

Publishing to `PyPI` is done through the `publish` workflow, which triggers anytime a `release` is made of the Github repository.
It builds a `wheel`, checks it, and pushes to `PyPI` if checks are successful.