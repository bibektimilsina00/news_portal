# Bump.sh API Documentation Setup

This project is configured to automatically deploy API documentation to Bump.sh using GitHub Actions.

## Setup

1. **Create a Bump.sh account** and obtain your API token at https://bump.sh

2. **Create a documentation project** on Bump.sh and note the documentation ID

3. **Set up GitHub Secrets** in your repository settings:
   - `BUMP_TOKEN`: Your Bump.sh API token
   - `BUMP_DOC_ID`: Your documentation ID from Bump.sh

## How it works

- The GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) runs on every push to main and pull requests
- It generates the OpenAPI specification using `scripts/generate_openapi.py`
- The spec is automatically deployed to Bump.sh using the official GitHub Action

## Manual generation

To generate the OpenAPI spec locally:

```bash
uv run python scripts/generate_openapi.py
```

This will create an `openapi.json` file in the project root.

## Configuration

- `.bump.yml`: Bump.sh configuration file
- The API documentation title and description can be updated in this file
