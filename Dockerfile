FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    docker.io \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install OWASP ZAP
RUN docker pull owasp/zap2docker-stable

# Install Nuclei
RUN curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest \
    | grep "browser_download_url.*linux_amd64.zip" \
    | cut -d '"' -f 4 \
    | wget -i - && \
    unzip nuclei-*-linux_amd64.zip && \
    mv nuclei /usr/local/bin/ && \
    rm nuclei-*-linux_amd64.zip

# Install Dependency-Check
RUN wget https://github.com/jeremy-lin/dependency-check/releases/download/v6.5.3/dependency-check-6.5.3-release.zip && \
    unzip dependency-check-6.5.3-release.zip -d dependency-check && \
    rm dependency-check-6.5.3-release.zip

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "security_cli.py"]
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install wget and security tools
RUN apt-get update && apt-get install -y wget && \
    curl -s https://api.github.com/repos/projectdiscovery/nuclei/releases/latest | \
    grep 'browser_download_url.*linux_amd64.zip' | cut -d '"' -f 4 | wget -qi - && \
    unzip -q nuclei-*-linux_amd64.zip && \
    mv nuclei /usr/local/bin/ && \
    rm nuclei-*-linux_amd64.zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p .security_cache && chmod 755 .security_cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
ENTRYPOINT ["python", "-m", "src.agentic_security.security_cli"]
CMD ["--help"]
