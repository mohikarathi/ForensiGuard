FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code, trained models, benchmark data, and pre-built React frontend
COPY . .

# Hugging Face Spaces defaults to port 7860, standard web to 8000
EXPOSE 7860 8000

CMD ["python", "-m", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"]
