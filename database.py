# database.py - Manajemen Koneksi dan Skema Basis Data MySQL
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from config import Config

# Variabel global untuk menyimpan pool koneksi database
_connection_pool = None

def get_pool():
    """
    Membuat MySQL Connection Pool jika belum ada.
    Connection pool berguna agar aplikasi tidak perlu membuka-tutup koneksi
    berkali-kali ke MySQL, sehingga menghemat memori dan meningkatkan kecepatan respon.
    """
    global _connection_pool
    if _connection_pool is None:
        try:
            from mysql.connector import pooling
            pool_config = Config.DB_CONFIG.copy()
            # Nama pool koneksi agar mudah diidentifikasi di server MySQL
            pool_config['pool_name'] = "skripsi_absensi_pool"
            # Menentukan maksimal 5 koneksi aktif yang berjalan bersamaan
            pool_config['pool_size'] = 5
            _connection_pool = pooling.MySQLConnectionPool(**pool_config)
        except Exception as e:
            print(f"Error saat membuat connection pool: {e}. Fallback ke koneksi langsung.")
            _connection_pool = False
    return _connection_pool

def get_connection():
    """
    Mengambil koneksi database aktif dari pool.
    Jika pool bermasalah, akan dialihkan (fallback) ke koneksi langsung ke MySQL.
    """
    pool = get_pool()
    if pool:
        try:
            return pool.get_connection()
        except Exception as e:
            print(f"Koneksi pool gagal: {e}. Dialihkan ke koneksi langsung.")
    try:
        # Melakukan koneksi langsung ke server MySQL menggunakan kredensial dari config
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        return conn
    except Error as e:
        raise RuntimeError(f"Koneksi ke database gagal: {e}")

@contextmanager
def get_cursor(dictionary=True):
    """
    Context manager (menggunakan sintaks 'with') untuk mempermudah penggunaan kursor database.
    Kursor ini otomatis melakukan 'commit' jika operasi sukses, atau 'rollback' jika terjadi error,
    serta otomatis menutup koneksi setelah selesai agar koneksi tidak menggantung.
    """
    conn = get_connection()
    try:
        # dictionary=True membuat hasil query dibaca dalam bentuk objek dictionary/key-value (nama_kolom: nilai)
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor
        conn.commit()  # Simpan perubahan ke database
    except Exception:
        conn.rollback()  # Batalkan perubahan jika ada error demi keamanan data
        raise
    finally:
        cursor.close()  # Tutup kursor
        conn.close()    # Kembalikan koneksi ke pool / tutup koneksi

def init_db():
    """
    Menginisialisasi tabel-tabel database yang diperlukan jika belum ada di phpMyAdmin.
    Fungsi ini otomatis dipanggil saat server Flask pertama kali dijalankan.
    """
    with get_cursor() as cur:
        # 1. Membuat tabel 'mahasiswa'
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                npm VARCHAR(30) NOT NULL UNIQUE,
                jurusan VARCHAR(100),
                asal_universitas VARCHAR(150),
                email VARCHAR(100),
                nama_direktorat_lantai_magang VARCHAR(150) NOT NULL, -- Lokasi penempatan magang
                jobdesc_magang TEXT,                                -- Deskripsi pekerjaan magang
                periode_mulai DATE,                                 -- Tanggal mulai magang
                periode_selesai DATE,                               -- Tanggal selesai magang
                periode_label VARCHAR(50),                           -- Label penanda periode
                nama_mentor VARCHAR(100),                           -- Nama pembimbing magang
                wajah_selesai TINYINT(1) NOT NULL DEFAULT 0,        -- Status apakah registrasi wajah sudah selesai (1=Ya, 0=Belum)
                label_id INT NOT NULL UNIQUE COMMENT 'ID numerik untuk LBPH recognizer', -- ID unik untuk model LBPH (bernilai angka)
                foto_path VARCHAR(255),                             -- Path pasfoto profil
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- Waktu pembuatan baris data
            )
        """)
        
        # 2. Membuat tabel 'absensi'
        cur.execute("""
            CREATE TABLE IF NOT EXISTS absensi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mahasiswa_id INT NOT NULL,                          -- Relasi ke tabel mahasiswa
                waktu DATETIME NOT NULL,                            -- Waktu absen dilakukan
                status ENUM('masuk','keluar','izin','tanpa keterangan') DEFAULT 'masuk', -- Status kehadiran
                tipe_izin VARCHAR(50) NULL,                         -- Keterangan sakit / keperluan izin
                surat_izin_path VARCHAR(255) NULL,                  -- File surat izin PDF
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id) ON DELETE CASCADE -- Jika data mahasiswa dihapus, data absensinya juga ikut terhapus
            )
        """)
        
        # 3. Membuat tabel 'admin'
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,               -- Username login admin
                password_hash VARCHAR(255) NOT NULL,                -- Password yang sudah di-hash (tidak disimpan dalam teks polos demi keamanan)
                nama_lengkap VARCHAR(100),
                email VARCHAR(100),
                nip VARCHAR(30),
                jabatan VARCHAR(100),
                unit_kerja VARCHAR(150),
                no_hp VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Melakukan pengecekan kolom baru secara otomatis (migrasi database) jika ada pembaruan tabel
        _ensure_admin_profile_columns(cur)
        _ensure_absensi_columns(cur)
        
        # Membuat akun admin default jika tabel admin masih kosong (Username: admin, Password: admin123)
        cur.execute('SELECT COUNT(*) AS n FROM admin')
        if cur.fetchone()['n'] == 0:
            cur.execute(
                'INSERT INTO admin (username, password_hash) VALUES (%s, %s)',
                ('admin', generate_password_hash('admin123', method='pbkdf2:sha256'))
            )

def _ensure_admin_profile_columns(cur):
    """Menambahkan kolom profil admin secara dinamis ke tabel admin jika belum terbuat di MySQL."""
    db_name = Config.DB_CONFIG.get('database')
    cur.execute("""
        SELECT COLUMN_NAME FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'admin'
    """, (db_name,))
    existing = {row['COLUMN_NAME'] for row in cur.fetchall()}
    for col_name, col_type in [
        ('nama_lengkap', 'VARCHAR(100)'),
        ('email', 'VARCHAR(100)'),
        ('nip', 'VARCHAR(30)'),
        ('jabatan', 'VARCHAR(100)'),
        ('unit_kerja', 'VARCHAR(150)'),
        ('no_hp', 'VARCHAR(20)'),
    ]:
        if col_name not in existing:
            cur.execute(f'ALTER TABLE admin ADD COLUMN {col_name} {col_type} NULL')

def _ensure_absensi_columns(cur):
    """Menambahkan kolom tipe_izin dan surat_izin_path ke tabel absensi jika belum terbuat di MySQL."""
    db_name = Config.DB_CONFIG.get('database')
    
    # Memastikan ENUM status pada tabel absensi mendukung semua status izin/kehadiran
    try:
        cur.execute("""
            ALTER TABLE absensi MODIFY COLUMN status 
            ENUM('masuk','keluar','izin','tanpa keterangan') DEFAULT 'masuk'
        """)
    except Exception as e:
        print(f"Error saat mengubah enum status absensi: {e}")
        
    cur.execute("""
        SELECT COLUMN_NAME FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'absensi'
    """, (db_name,))
    existing = {row['COLUMN_NAME'] for row in cur.fetchall()}
    
    if 'tipe_izin' not in existing:
        cur.execute('ALTER TABLE absensi ADD COLUMN tipe_izin VARCHAR(50) NULL')
    if 'surat_izin_path' not in existing:
        cur.execute('ALTER TABLE absensi ADD COLUMN surat_izin_path VARCHAR(255) NULL')

