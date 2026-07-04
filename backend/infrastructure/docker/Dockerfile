# ── Builder Stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --user --upgrade pip setuptools wheel && pip install --user --no-cache-dir -r requirements.txt

# ── Runner Stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim as runner

WORKDIR /app

# Create non-root user
RUN groupadd -r gpa && useradd -r -g gpa gpa

# Copy dependencies from builder
COPY --from=builder /root/.local /home/gpa/.local
ENV PATH=/home/gpa/.local/bin:$PATH

# Copy application code
COPY . .

# Set ownership
RUN chown -R gpa:gpa /app

# Switch to non-root user
USER gpa

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
