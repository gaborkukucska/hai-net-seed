# HAI-Net Seed Framework - Constitutional Docker Container
# Multi-stage build for production-ready deployment
# Constitutional compliance: Privacy First + Decentralization + Security

# Stage 1: Python Backend Build
FROM python:3.12-slim as backend-builder

# Constitutional principle: Minimize attack surface
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (Constitutional Human Rights principle)
RUN groupadd -r hainet && useradd -r -g hainet hainet

# Set working directory
WORKDIR /app

# Copy Python requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Node.js Frontend Build  
FROM node:18-slim as frontend-builder

# Constitutional principle: Minimize dependencies
WORKDIR /app/web

# Copy package files
COPY web/package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy frontend source
COPY web/ .

# Build frontend for production
RUN npm run build

# Stage 3: Production Runtime
FROM python:3.12-slim as production

# Constitutional metadata
LABEL maintainer="HAI-Net Community" \
      description="Constitutional AI Network Seed Framework" \
      version="1.0.0" \
      constitutional-compliance="true" \
      privacy-first="true" \
      decentralized="true" \
      community-focused="true"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (Constitutional Human Rights + Security)
RUN groupadd -r hainet && useradd -r -g hainet hainet

# Create application directories with proper permissions
RUN mkdir -p /app /app/data /app/config /app/logs /app/web/dist && \
    chown -R hainet:hainet /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built frontend from builder
COPY --from=frontend-builder --chown=hainet:hainet /app/web/dist /app/web/dist
COPY --from=frontend-builder --chown=hainet:hainet /app/web/package.json /app/web/

# Copy application code
COPY --chown=hainet:hainet . .

# Create constitutional configuration directory
RUN mkdir -p /app/constitutional && \
    echo "constitutional_version: 1.0" > /app/constitutional/version.yaml && \
    echo "privacy_first: true" >> /app/constitutional/version.yaml && \
    echo "human_rights: true" >> /app/constitutional/version.yaml && \
    echo "decentralization: true" >> /app/constitutional/version.yaml && \
    echo "community_focus: true" >> /app/constitutional/version.yaml && \
    chown -R hainet:hainet /app/constitutional

# Create data persistence directories
RUN mkdir -p /app/data/identity /app/data/network /app/data/storage && \
    chown -R hainet:hainet /app/data

# Switch to non-root user (Constitutional security principle)
USER hainet

# Configure environment for constitutional compliance
ENV HAINET_NODE_ROLE=slave \
    HAINET_DEBUG_MODE=false \
    HAINET_LOG_LEVEL=INFO \
    HAINET_DATA_SHARING_CONSENT=false \
    HAINET_CENTRAL_AUTHORITY_DISABLED=true \
    HAINET_LOCAL_FIRST=true \
    HAINET_COMMUNITY_PARTICIPATION=true \
    HAINET_GUARDIAN_ENABLED=true \
    HAINET_ENCRYPTION_ENABLED=true \
    HAINET_WATERMARKING_ENABLED=true \
    HAINET_USER_OVERRIDE_ENABLED=true \
    PYTHONPATH=/app \
    PATH=/home/hainet/.local/bin:$PATH

# Health check for constitutional compliance monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "from core.config.settings import HAINetSettings; \
                   settings = HAINetSettings(); \
                   violations = []; \
                   from core.config.settings import validate_constitutional_compliance; \
                   violations = validate_constitutional_compliance(settings); \
                   exit(0 if not violations else 1)" || exit 1

# Expose ports (constitutional principle: minimal necessary access)
EXPOSE 8000 8080 4001

# Create startup script with constitutional checks
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🏛️ HAI-Net Constitutional Startup Check"\n\
echo "======================================"\n\
\n\
# Verify constitutional compliance\n\
python -c "\n\
from core.config.settings import HAINetSettings, validate_constitutional_compliance\n\
settings = HAINetSettings()\n\
violations = validate_constitutional_compliance(settings)\n\
if violations:\n\
    print(\"❌ Constitutional violations detected:\")\n\
    for v in violations: print(f\"  - {v}\")\n\
    exit(1)\n\
else:\n\
    print(\"✅ All constitutional principles verified\")\n\
"\n\
\n\
echo "🚀 Starting HAI-Net Seed Framework..."\n\
\n\
# Start web server with constitutional middleware\n\
exec python -m core.web.server\n\
' > /app/start.sh && chmod +x /app/start.sh

# Use dumb-init for proper signal handling (Constitutional reliability)
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command with constitutional compliance verification
CMD ["/app/start.sh"]

# Docker build arguments for customization
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Constitutional compliance labels
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.url="https://github.com/hai-net/hai-net-seed" \
      org.opencontainers.image.source="https://github.com/hai-net/hai-net-seed" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.vendor="HAI-Net Community" \
      org.opencontainers.image.title="HAI-Net Seed Framework" \
      org.opencontainers.image.description="Constitutional AI Network Framework" \
      org.opencontainers.image.documentation="https://github.com/hai-net/hai-net-seed/blob/main/README.md" \
      constitutional.compliance="verified" \
      constitutional.privacy-first="enforced" \
      constitutional.decentralized="true" \
      constitutional.community-focus="enabled" \
      constitutional.human-rights="protected"

# Constitutional volume declarations (Privacy First - local data only)
VOLUME ["/app/data", "/app/config", "/app/logs"]
