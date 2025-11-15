# Use Python 3.11 Alpine for minimal size
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies without cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the bot
CMD ["python", "main.py"]
