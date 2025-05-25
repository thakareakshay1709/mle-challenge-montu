FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY src/ src/
COPY data/ data/
COPY requirements.txt .

# Create models directory
RUN mkdir -p models

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.src.main:redact_app", "--host", "0.0.0.0", "--port", "8000"]
