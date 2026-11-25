# cintel-06-continuous-intelligence-custom

[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](pyproject.toml)
[![CI](https://github.com/dstringer03/cintel-06-continuous-intelligence-custom/actions/workflows/ci-python-zensical.yml/badge.svg)](https://github.com/dstringer03/cintel-06-continuous-intelligence-custom/actions/workflows/ci-python-zensical.yml)
[![Documentation](https://img.shields.io/badge/docs-site-blue?logo=github)](https://dstringer03.github.io/cintel-06-continuous-intelligence-custom/)

> Combine monitoring signals and anomaly detection to assess system health.

## Project Overview

Author: Darrion Maurice Stringer

Date: 2026-11

Based on the example project by Denise Case.

I am learning how to combine monitoring techniques into one system assessment. My planned customization will bring together signals, anomaly detection, rolling monitoring, and drift comparisons from earlier projects.

## Data

The example uses stored system measurements from the data folder.

Each observation includes:

- requests: number of requests handled.
- errors: number of failed requests.
- total_latency_ms: total response time in milliseconds.

## Approach

The example pipeline uses Python and Polars to:

1. Read system measurements.
2. Calculate error rate and average latency.
3. Identify observations exceeding defined thresholds.
4. Summarize system behavior.
5. Classify the overall system as STABLE or DEGRADED.

Rolling monitoring and baseline drift comparisons are planned additions for my custom application.

## Project Files

- [pyproject.toml](pyproject.toml): project configuration and dependencies.
- [continuous_intelligence.py](src/cintel/continuous_intelligence.py): monitoring pipeline.
- [data](data/): input measurements.
- [artifacts](artifacts/): generated results.
- [tests](tests/): automated tests.
- [docs](docs/): project documentation.
- [zensical.toml](zensical.toml): documentation configuration.

## Set Up the Environment

Follow the [Professional Python Workflow Guide](https://denisecase.github.io/pro-analytics-02/) for machine setup.

Open a terminal in the project root and run each command separately:

```shell
uv self update
uv python pin 3.14
uv python install
uv sync
```

## Run the Project

From the project root:

```shell
uv run python -m cintel.continuous_intelligence
```

## Run the Reactive App

```shell
uv run marimo run src/cintel/app.py
```

Press Control + C in the terminal to stop the app.

## Expected Results

The pipeline saves its summary to:

```text
artifacts/system_assessment.csv
```

The system assessment uses these labels:

- STABLE: neither summary signal exceeds its configured threshold.
- DEGRADED: at least one summary signal exceeds its configured threshold.

Successful execution displays:

```text
Pipeline executed successfully!
```

The pipeline also creates a project.log file.

An overall STABLE result does not mean every individual observation is within the thresholds.

## Verification

Run the tests:

```shell
uv run pytest
```

Build the documentation:

```shell
uv run python -m zensical build
```

## Set Up Git Hooks

Run each command separately:

```shell
uvx prek install --force
uvx prek update --freeze --cooldown-days 7
git add -A
uvx prek run --all-files
```

If a hook changes files, review the changes, stage them again, and rerun the checks.

## Development Checks

```shell
uv run ruff check .
uv run ruff format .
uv run ty check
uv run pytest
uv run python -m zensical build
```

## Save Changes to GitHub

```shell
git add -A
git commit -m "Describe the changes"
git push
```

## Documentation and Automated Checks

The project uses Zensical and GitHub Pages to publish documentation.

- [Hosted Documentation](https://dstringer03.github.io/cintel-06-continuous-intelligence-custom/)
- [Python and Documentation Checks](https://github.com/dstringer03/cintel-06-continuous-intelligence-custom/actions/workflows/ci-python-zensical.yml)
- [Documentation Deployment](https://github.com/dstringer03/cintel-06-continuous-intelligence-custom/actions/workflows/deploy-zensical.yml)

## Tools

- Python: application code.
- Polars: data processing.
- datafun-toolkit: logging.
- marimo: reactive application.
- uv: Python environment and dependencies.
- Ruff: formatting and linting.
- ty: type checking.
- pytest: automated tests.
- prek: Git hooks.
- Zensical: documentation.
- Git and GitHub: version control and sharing.

## Links

- [My Repository](https://github.com/dstringer03/cintel-06-continuous-intelligence-custom)
- [Hosted Documentation](https://dstringer03.github.io/cintel-06-continuous-intelligence-custom/)
- [Original Example](https://github.com/denisecase/cintel-06-continuous-intelligence)
- [Professional Python Workflow Guide](https://denisecase.github.io/pro-analytics-02/)
- [Citation](CITATION.cff)
- [License](LICENSE)
## D2 Experiment: Adding Rolling Error Rates

I added a five-observation rolling average of error_rate using the rolling monitoring technique from Module 4.

Prediction: I expected a new rolling_error_rate_5 column, with the first four values blank because a complete window needs five observations.

Result: The pipeline processed 60 records and saved artifacts/rolling_signals.csv. The first four rolling values were blank, and the first complete average was approximately 1.76%. The anomaly count remained 7.

I learned how to add rolling monitoring to the existing pipeline. The rolling calculation assumes the CSV rows are in observation order because this file has no timestamps. It does not change the existing system classification rules.
