FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code
COPY simple_api.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "simple_api.py"] 