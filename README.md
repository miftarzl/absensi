# Sistem Absensi Mahasiswa Magang — Direktorat Jenderal Kekayaan Intelektual

Aplikasi web absensi berbasis **pengenalan wajah (face recognition)** dengan metode **OpenCV LBPH** (Local Binary Pattern Histograms) untuk skripsi.

## Fitur

- **Login admin**: Data mahasiswa dan laporan hanya dapat diakses oleh admin (tidak terbuka untuk umum).
- **Daftar mahasiswa magang**: NIM, nama, email, prodi, institusi. Setelah simpan, langkah berikutnya adalah registrasi wajah.
- **Registrasi wajah**: Pengambilan 5 foto dari berbagai sisi (hadap depan, nengok kiri/kanan, lihat atas/bawah) dengan peringatan untuk melepas kacamata, masker, dan penutup wajah.
- **Training model LBPH**: melatih model dari semua sampel wajah.
- **Absensi**: absen masuk/keluar dengan pengenalan wajah (webcam); hanya admin yang mengoperasikan.
- **Laporan**: filter absensi berdasarkan tanggal dan mahasiswa; hanya admin yang dapat melihat.

## Persyaratan

- Python 3.8+
- MySQL (XAMPP sudah menyertakan MySQL)
- Webcam (untuk registrasi wajah dan absensi)

## Instalasi

1. **Buat virtual environment (opsional):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
   **Catatan:** Paket `opencv-contrib-python` menyertakan modul `cv2.face` (LBPH). Jangan install bersamaan dengan `opencv-python` (uninstall `opencv-python` jika sudah terpasang).

3. **Database MySQL:**
   - Buat database dan tabel (bisa lewat phpMyAdmin atau CLI):
     ```bash
     mysql -u root -p < database.sql
     ```
   - Atau salin `.env.example` ke `.env` dan sesuaikan:
     - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

4. **Jalankan aplikasi:**
   ```bash
   python app.py
   ```
   Buka browser: **http://localhost:5000**

## Login Admin

- **Default:** username `admin`, password `admin123`. Ganti password setelah pertama kali login (kelola lewat database atau fitur ubah password jika ditambahkan).
- Semua data mahasiswa dan laporan **hanya untuk admin**; tidak terbuka untuk umum.

## Alur Penggunaan

1. **Login** dengan akun admin.
2. **Tambah mahasiswa** di "Daftar Mahasiswa" (isi NIM, nama, dll.) → klik "Simpan & Lanjut Registrasi Wajah".
3. **Registrasi wajah** (langkah berikutnya): lepaskan kacamata/masker/penutup kepala, lalu ambil 5 foto sesuai panduan (hadap depan, nengok kiri, kanan, lihat atas, lihat bawah).
4. **Latih model**: klik "Latih Model" setelah semua mahasiswa punya sampel wajah.
5. **Absensi**: di halaman "Absensi", klik "Absen Masuk" atau "Absen Keluar" lalu hadapkan wajah ke kamera.
6. **Laporan**: filter tanggal/mahasiswa di "Laporan" (hanya admin).

## Metode Face Recognition

- **Deteksi wajah:** Haar Cascade (`haarcascade_frontalface_default.xml`) dari OpenCV.
- **Pengenalan wajah:** **LBPH** (Local Binary Pattern Histograms) dari modul `cv2.face` (opencv-contrib-python). Model disimpan di folder `recognizer/lbph_model.yml`. Sampel wajah disimpan di `uploads/faces/<label_id>/`.

## Struktur Proyek

```
skripsyit/
├── app.py              # Aplikasi Flask & API
├── config.py           # Konfigurasi
├── database.py         # Koneksi MySQL & init tabel
├── face_service.py     # Deteksi & pengenalan wajah (OpenCV LBPH)
├── requirements.txt
├── database.sql        # Skrip pembuatan tabel
├── .env.example
├── static/
│   └── index.html      # Frontend (dashboard, mahasiswa, registrasi, absensi, laporan)
├── uploads/            # Dibuat otomatis
│   └── faces/          # Sampel wajah per label_id
└── recognizer/         # Dibuat otomatis; menyimpan lbph_model.yml
```

## API Endpoint (ringkas)

| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/api/mahasiswa` | Daftar mahasiswa |
| POST | `/api/mahasiswa` | Tambah mahasiswa |
| GET | `/api/mahasiswa/<id>` | Detail mahasiswa |
| DELETE | `/api/mahasiswa/<id>` | Hapus mahasiswa |
| POST | `/api/mahasiswa/<id>/wajah` | Tambah sampel wajah (body: `{ "image": "data:image/..." }`) |
| POST | `/api/train` | Latih model LBPH |
| POST | `/api/absensi` | Catat absensi (body: `{ "image": "...", "status": "masuk" \| "keluar" }`) |
| GET | `/api/laporan?dari=&sampai=&mahasiswa_id=` | Laporan absensi |
| POST | `/api/detect` | Cek deteksi wajah (body: `{ "image": "..." }`) |

## Skripsi

Judul: **Sistem Absensi Mahasiswa Magang di Direktorat Jenderal Kekayaan Intelektual**  
Metode: Face recognition dengan OpenCV (LBPH).

Untuk pengembangan lanjutan bisa ditambah: login admin, ekspor laporan (PDF/Excel), dan notifikasi.
