FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose ports for API and Streamlit
EXPOSE 8000
EXPOSE 8501

# Default command (can be overridden)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
