FROM python:3.10-slim

# Install dependency sistem yang dibutuhkan oleh OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements dan install dependensi python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy seluruh source code
COPY . .

# Environment variable default untuk Flask
ENV PORT=80

# Expose port internal 80
EXPOSE 80

# Jalankan aplikasi menggunakan Gunicorn pada port 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
