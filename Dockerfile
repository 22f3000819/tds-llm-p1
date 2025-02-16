FROM python:3.12-slim-bookworm

# Install dependencies, Git, and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Upgrade system and ensure Node.js is installed
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin:$PATH"

# Set up the application directory
WORKDIR /tdsp1

# Copy application files
COPY . .

# Explicitly set the correct binary path and use `sh -c`
CMD ["/root/.local/bin/uv", "run", "app.py"]
