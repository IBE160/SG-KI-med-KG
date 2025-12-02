FROM python:3.12-bookworm

# Set the working directory
WORKDIR /app

# The uv installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the uv installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . .

# Create start.sh with LF line endings and set permissions outside of volume mount
RUN printf "#!/bin/bash\n\nif [ -f /.dockerenv ]; then\n    echo \"Running in Docker\"\n    echo \"Running migrations...\"\n    alembic upgrade head\n    echo \"Starting FastAPI...\"\n    fastapi dev app/main.py --host 0.0.0.0 --port 8000 --reload &\n    python watcher.py\nelse\n    echo \"Running locally with uv\"\n    echo \"Running migrations...\"\n    uv run alembic upgrade head\n    echo \"Starting FastAPI...\"\n    uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000 --reload &\n    uv run python watcher.py\nfi\n\nwait\n" > /usr/local/bin/start-app.sh && chmod +x /usr/local/bin/start-app.sh

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["/usr/local/bin/start-app.sh"]