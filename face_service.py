# face_service.py - Layanan Pengolahan Citra & Pengenalan Wajah dengan OpenCV LBPH
import os
import cv2
import numpy as np
from pathlib import Path
from config import Config

# Pastikan modul face (modul tambahan berisi recognizer wajah) dari opencv-contrib tersedia.
# Jika tidak terpasang, variabel face bernilai None dan sistem akan menampilkan instruksi instalasi.
try:
    from cv2 import face
except ImportError:
    face = None

CASCADE_PATH = None

def get_cascade():
    """Membuat objek Haar Cascade Classifier untuk mendeteksi wajah depan (frontal face)."""
    global CASCADE_PATH
    if CASCADE_PATH is None:
        # Mengambil file cascade bawaan OpenCV
        CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    return cv2.CascadeClassifier(CASCADE_PATH)

def ensure_dirs():
    """
    Membuat folder penyimpanan (uploads, faces, pasfoto, dll)
    jika folder-folder tersebut belum ada saat sistem dijalankan.
    """
    for d in [Config.UPLOAD_FOLDER, Config.FACES_FOLDER, Config.PASFOTO_FOLDER, Config.SURAT_IZIN_FOLDER, Config.MODEL_FOLDER]:
        Path(d).mkdir(parents=True, exist_ok=True)

_profile_cascade = None

def get_profile_cascade():
    """Membuat objek Haar Cascade Classifier untuk deteksi profil wajah samping sebagai cadangan (fallback)."""
    global _profile_cascade
    if _profile_cascade is None:
        _profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    return _profile_cascade

# ==================== #Tahap 1 deteksi wajah (Haar Cascade) ====================
# Tahap ini bertujuan untuk mendeteksi koordinat area wajah pada gambar/kamera.
def detect_faces(gray_image):
    """
    Mendeteksi area wajah pada gambar berskala keabuan (grayscale).
    Memiliki toleransi kemiringan dengan fitur deteksi profil wajah samping jika deteksi depan gagal.
    """
    cascade = get_cascade()
    # scaleFactor=1.08: Mengurangi ukuran gambar 8% setiap iterasi agar deteksi lebih detail
    # minNeighbors=3: Menentukan batas toleransi pengelompokan piksel kandidat wajah (makin kecil makin sensitif)
    # minSize=(30, 30): Ukuran wajah minimal yang dideteksi (30x30 piksel)
    faces = cascade.detectMultiScale(gray_image, scaleFactor=1.08, minNeighbors=3, minSize=(30, 30))
    
    # Cadangan: Jika wajah menghadap depan tidak ditemukan, cari wajah yang menghadap samping/miring
    if len(faces) == 0:
        try:
            profile_cascade = get_profile_cascade()
            profile_faces = profile_cascade.detectMultiScale(gray_image, scaleFactor=1.08, minNeighbors=3, minSize=(30, 30))
            if len(profile_faces) > 0:
                return profile_faces
        except Exception:
            pass
            
    return faces

def get_face_roi(gray_image, face_rect):
    """
    Memotong area koordinat wajah (ROI - Region of Interest) 
    berdasarkan kotak hasil deteksi (x, y, lebar, tinggi).
    """
    x, y, w, h = face_rect
    return gray_image[y:y+h, x:x+w]

# ==================== #Tahap 2 pra-pemrosesan citra (Grayscale, Crop, Resize, CLAHE) ====================
# Tahap ini bertujuan membersihkan gambar, mengubah ke grayscale, meratakan cahaya (CLAHE), dan menyeragamkan ukuran.
def prepare_image_for_training(image_array):
    """
    Mempersiapkan gambar mentah dari webcam untuk disimpan sebagai sampel wajah:
    1. Konversi ke Grayscale (Keabuan).
    2. Deteksi wajah terbesar.
    3. Crop koordinat wajah.
    4. Resize ke resolusi standar 200x200 piksel.
    5. Normalisasi kontras pencahayaan menggunakan CLAHE (Contrast Limited Adaptive Histogram Equalization).
    """
    # Ubah gambar berwarna (BGR/RGB) ke grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    
    # Deteksi wajah pada gambar grayscale
    faces = detect_faces(gray)
    if len(faces) == 0:
        return None, None
        
    # Jika terdeteksi lebih dari satu wajah, ambil wajah dengan luas area kotak terbesar (paling dekat kamera)
    face_rect = max(faces, key=lambda r: r[2] * r[3])
    
    # Potong area wajah (Region of Interest)
    roi = get_face_roi(gray, face_rect)
    
    # Resize area wajah menjadi ukuran standar 200x200 piksel agar seragam saat di-training
    roi = cv2.resize(roi, (200, 200))
    
    # Terapkan CLAHE untuk meratakan dan menstabilkan pencahayaan wajah dari webcam
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    roi = clahe.apply(roi)
    return roi, face_rect

# ==================== #Tahap 3 pelatihan model (Training LBPH) ====================
# Tahap ini mengekstrak histogram wajah mahasiswa terdaftar dan menyimpannya sebagai file model 'lbph_model.yml'.
def train_lbph(face_images, labels):
    """
    Melatih (training) model recognizer OpenCV LBPH menggunakan seluruh sampel wajah mahasiswa.
    Hasil training berupa histogram pola biner wajah yang disimpan ke file 'lbph_model.yml'.
    """
    if face is None:
        raise RuntimeError("Modul cv2.face tidak tersedia. Silakan install: pip install opencv-contrib-python")
    
    ensure_dirs()
    
    # Inisialisasi recognizer LBPH dengan parameter yang ditentukan di config.py
    recognizer = face.LBPHFaceRecognizer_create(
        radius=Config.LBPH_RADIUS,
        neighbors=Config.LBPH_NEIGHBORS,
        grid_x=Config.LBPH_GRID_X,
        grid_y=Config.LBPH_GRID_Y,
    )
    
    # Melatih recognizer dengan list matriks wajah (face_images) dan array label ID numerik (labels)
    recognizer.train(face_images, np.array(labels, dtype=np.int32))
    
    # Menyimpan model hasil training ke disk
    model_path = os.path.join(Config.MODEL_FOLDER, 'lbph_model.yml')
    recognizer.save(model_path)
    
    # Menghapus cache agar model baru otomatis dimuat ulang oleh sistem saat ada absensi
    reset_cached_recognizer()
    return model_path

# Cache model agar sistem tidak perlu membaca ulang file YML dari disk di setiap detik absensi
_cached_recognizer = None

def get_recognizer(force_reload=False):
    """Mengambil instance model recognizer LBPH yang sedang aktif di memori cache."""
    global _cached_recognizer
    if _cached_recognizer is None or force_reload:
        _cached_recognizer = load_recognizer()
    return _cached_recognizer

def reset_cached_recognizer():
    """Mengosongkan cache recognizer dan memicu pemuatan ulang model."""
    global _cached_recognizer
    _cached_recognizer = None
    get_recognizer(force_reload=True)

def load_recognizer():
    """Membaca file model terlatih 'lbph_model.yml' dari media penyimpanan."""
    if face is None:
        return None
    model_path = os.path.join(Config.MODEL_FOLDER, 'lbph_model.yml')
    if not os.path.isfile(model_path):
        return None
    recognizer = face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)
    return recognizer

# ==================== #Tahap 4 pengenalan wajah (Recognition / Prediksi) ====================
# Tahap ini memprediksi wajah baru dengan mencocokkan histogramnya terhadap model 'lbph_model.yml'.
def recognize_face(gray_face_image, confidence_threshold=None):
    """
    Mengenali (recognize) wajah dari area ROI grayscale wajah masukan:
    1. Ukuran wajah masukan disamakan ke 200x200 piksel.
    2. Recognizer memprediksi wajah dan menghasilkan label_id serta confidence score.
    3. Nilai confidence score (jarak Chi-Square histogram) dibandingkan dengan threshold.
       * Catatan: Pada algoritma LBPH, semakin KECIL nilai confidence, wajah semakin COCOK/MIRIP.
    """
    threshold = confidence_threshold if confidence_threshold is not None else Config.CONFIDENCE_THRESHOLD
    recognizer = get_recognizer()
    if recognizer is None:
        return None, 0
        
    # Resize area wajah agar cocok dengan input model
    gray_face_image = cv2.resize(gray_face_image, (200, 200))
    
    # Prediksi wajah menggunakan model LBPH
    label_id, confidence = recognizer.predict(gray_face_image)
    
    # Jika jarak kemiripan (confidence) melebihi threshold, anggap wajah tidak dikenal (Unknown)
    if confidence > threshold:
        return None, float(confidence)
        
    return int(label_id), float(confidence)

def decode_image_from_base64(data_url_or_bytes):
    """
    Utilitas dekode gambar: Mengubah gambar string base64 (format data url dari webcam frontend)
    menjadi matriks gambar (numpy array) yang bisa diproses oleh OpenCV.
    """
    import base64
    if isinstance(data_url_or_bytes, str):
        # Memisahkan header metadata base64 (contoh: "data:image/jpeg;base64,") jika ada
        if data_url_or_bytes.startswith('data:image'):
            data_url_or_bytes = data_url_or_bytes.split(',', 1)[1]
        img_bytes = base64.b64decode(data_url_or_bytes)
    else:
        img_bytes = data_url_or_bytes
        
    # Konversi bytes gambar mentah menjadi numpy array lalu dekode ke format BGR OpenCV
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

