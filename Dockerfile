FROM python:3.10-slim

# Install dependency sistem yang dibutuhkan oleh OpenCV dan tzdata
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements dan install dependensi python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy seluruh source code
COPY . .

# Environment variable default untuk Flask dan Zona Waktu (WIB)
ENV PORT=80
ENV TZ=Asia/Jakarta

# Expose port internal 80
EXPOSE 80

# Jalankan aplikasi menggunakan Gunicorn pada port 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
