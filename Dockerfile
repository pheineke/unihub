# Use Python 3.11 slim image for a smaller footprint
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout and stderr are not buffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set work directory
WORKDIR /app

# Install dependencies first (for better layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port Gunicorn will run on
EXPOSE 5000

# Start Gunicorn server to serve the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]