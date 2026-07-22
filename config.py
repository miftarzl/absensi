# config.py - Konfigurasi Utama Aplikasi Absensi Wajah
import os
from pathlib import Path

# BASE_DIR: Mendapatkan path/direktori folder utama proyek ini
BASE_DIR = Path(__file__).resolve().parent

class Config:
    # SECRET_KEY: Digunakan Flask untuk mengamankan data session (misal login admin)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-sistem-absensi-djki')
    
    # SKIP_ADMIN_LOGIN: Jika bernilai True (1), sistem otomatis masuk sebagai admin untuk kebutuhan pengembangan/sidang tanpa harus ketik username/password
    SKIP_ADMIN_LOGIN = os.environ.get('SKIP_ADMIN_LOGIN', '1') == '1'
    
    # DB_CONFIG: Konfigurasi koneksi ke database MySQL (XAMPP phpMyAdmin)
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'skripsi_absensi_djki'),
    }
    
    # UPLOAD_FOLDER: Lokasi folder utama untuk menyimpan file yang diunggah
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    
    # FACES_FOLDER: Lokasi folder untuk menyimpan sampel wajah hasil registrasi mahasiswa
    FACES_FOLDER = os.path.join(os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads')), 'faces')
    
    # PASFOTO_FOLDER: Lokasi folder untuk menyimpan pasfoto profil mahasiswa
    PASFOTO_FOLDER = os.path.join(os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads')), 'pasfoto')
    
    # SURAT_IZIN_FOLDER: Lokasi folder untuk menyimpan file surat izin format PDF dari mahasiswa
    SURAT_IZIN_FOLDER = os.path.join(os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads')), 'surat_izin')
    
    # MODEL_FOLDER: Lokasi folder untuk menyimpan file model wajah hasil training (lbph_model.yml)
    MODEL_FOLDER = os.environ.get('MODEL_FOLDER', str(BASE_DIR / 'recognizer'))
    
    # Parameter algoritma LBPH (Local Binary Pattern Histograms):
    LBPH_RADIUS = 1       # Radius bertingkat untuk pembentukan pola biner (tetangga piksel)
    LBPH_NEIGHBORS = 8    # Jumlah titik tetangga piksel yang dihitung
    LBPH_GRID_X = 8       # Pembagian grid horizontal pada gambar wajah untuk histogram
    LBPH_GRID_Y = 8       # Pembagian grid vertikal pada gambar wajah untuk histogram
    
    # CONFIDENCE_THRESHOLD: Batas toleransi kemiripan wajah.
    # Jika jarak histogram (confidence) di atas nilai ini, maka wajah dianggap TIDAK DIKENAL ("Unknown").
    # Semakin kecil nilai threshold ini, semakin ketat sistem mengenali wajah.
    # Diturunkan dari 65 ke 50 untuk mencegah salah deteksi pada mahasiswa yang memiliki wajah mirip.
    CONFIDENCE_THRESHOLD = 50

def get_cascade_path():
    """Mengembalikan path/lokasi file Haar Cascade untuk deteksi wajah bawaan OpenCV."""
    import cv2
    return cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

