#!/usr/bin/env bash
pytest tests/unit -q --cov=app --cov-report=term-missing "$@"
