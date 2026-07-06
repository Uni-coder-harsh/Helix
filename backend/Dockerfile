# Stage 1: Build virtual environment with dependencies
FROM python:3.13-slim AS builder

# Install uv for rapid Python packaging management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy only pyproject.toml and source code layout configuration
COPY pyproject.toml ./

# Install project dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime image
FROM python:3.13-slim AS runner

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Set runtime paths and flags
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HELIX_ENV=prod

# Copy backend codebase to workspace
COPY . .

# Run as non-privileged app user for container hardening
RUN useradd -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "services.main:app", "--host", "0.0.0.0", "--port", "8000"]
