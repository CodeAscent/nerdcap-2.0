FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for GIS and psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_VERSION=3.6.2
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
