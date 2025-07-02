FROM mcr.microsoft.com/devcontainers/python:3.11

# Set the working directory
WORKDIR /workspace

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Switch to non-root user (vscode user already exists in base image)
USER vscode

# Keep container running
CMD ["sleep", "infinity"]