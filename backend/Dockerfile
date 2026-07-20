FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for some packages (like PyMuPDF and psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download default models at build time to speed up startup
RUN python -m spacy download en_core_web_sm

COPY . .

# Create unprivileged user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
