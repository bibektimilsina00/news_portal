#!/usr/bin/env/bash
pytest tests/integration -q --cov=app --cov-report=term-missing "$@"
