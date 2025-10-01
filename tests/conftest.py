import os,sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
pytest_plugins = [
    "tests.unit.conftest",
    "tests.integration.conftest",
    "tests.e2e.conftest",
]
