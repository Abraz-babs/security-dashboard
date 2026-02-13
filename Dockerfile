FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/

WORKDIR /app/backend

# Expose port (Railway sets PORT env var, default to 8000)
EXPOSE 8000

# Use shell form to properly expand $PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
