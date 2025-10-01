# Lightweight Dockerfile for news_portal
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# copy only pyproject for better cache
COPY pyproject.toml uv.lock /app/

# install uv (package manager) and use it to install project dependencies
# we only invoke pip here to install the `uv` tool itself; `uv` will
# handle the rest of dependency installation (no direct pip installs).
## install standalone `uv` binary from official releases and use it to install deps
# Note: this uses the linux-amd64 release asset. If you need ARM support,
# replace the URL with the appropriate artifact for your target architecture.
RUN curl -fsSL -o /usr/local/bin/uv \
	"https://github.com/astral-sh/uv/releases/latest/download/uv-linux-amd64" && \
	chmod +x /usr/local/bin/uv && \
	uv sync --no-dev

# copy project
COPY . /app

# add entrypoint that runs migrations before starting the app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# expose
EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
