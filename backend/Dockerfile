FROM python:3.10-slim

# Create non-root user with home directory and matching host UID/GID
ARG USER_ID=501
ARG GROUP_ID=20
RUN groupadd -g $GROUP_ID appuser || true
RUN useradd -u $USER_ID -g $GROUP_ID -m appuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Claude Code CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Install uv with retry mechanism for network reliability
USER appuser
RUN --mount=type=cache,target=/tmp/uv-cache,uid=501,gid=20 \
    if [ ! -f /tmp/uv-cache/uv-installer.sh ]; then \
        curl --retry 5 --retry-all-errors -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-cache/uv-installer.sh; \
    fi && \
    sh /tmp/uv-cache/uv-installer.sh
ENV PATH="/home/appuser/.local/bin:$PATH"

# Switch back to root for file operations
USER root

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY backend/ ./backend/
COPY .mcp.json ./

# Change ownership to appuser (group ID 20)
RUN chown -R appuser:20 /app

# Switch to appuser for uv operations
USER appuser

# Install Python dependencies using uv with retry
RUN for i in 1 2 3; do uv sync --frozen && break || sleep 5; done

# Create necessary directories
RUN mkdir -p /app/temp /app/papers

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]