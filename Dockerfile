FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/

# Copy start script
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Use shell script to properly handle PORT env var
CMD ["./start.sh"]
