-- =====================================================================
-- SKEMA BASIS DATA: database.sql (MySQL)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS skripsi_absensi_djki
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE skripsi_absensi_djki;

-- 1. Membuat Tabel Mahasiswa
CREATE TABLE IF NOT EXISTS mahasiswa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  npm VARCHAR(30) NOT NULL UNIQUE,
  jurusan VARCHAR(100),
  asal_universitas VARCHAR(150),
  email VARCHAR(100),
  nama_direktorat_lantai_magang VARCHAR(150) NOT NULL,
  jobdesc_magang TEXT,
  periode_mulai DATE,
  periode_selesai DATE,
  periode_label VARCHAR(50),
  nama_mentor VARCHAR(100),
  wajah_selesai TINYINT(1) NOT NULL DEFAULT 0,
  label_id INT NOT NULL UNIQUE COMMENT 'ID numerik untuk model LBPH',
  foto_path VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Membuat Tabel Absensi
CREATE TABLE IF NOT EXISTS absensi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mahasiswa_id INT NOT NULL,
  waktu DATETIME NOT NULL,
  status ENUM('masuk','keluar','izin','tanpa keterangan') DEFAULT 'masuk',
  tipe_izin VARCHAR(50) NULL,
  surat_izin_path VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id) ON DELETE CASCADE,
  INDEX idx_waktu (waktu),
  INDEX idx_mahasiswa_id (mahasiswa_id)
);

-- 3. Membuat Tabel Admin
CREATE TABLE IF NOT EXISTS admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nama_lengkap VARCHAR(100),
  email VARCHAR(100),
  nip VARCHAR(30),
  jabatan VARCHAR(100),
  unit_kerja VARCHAR(150),
  no_hp VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert admin default jika belum ada (username: admin, password: admin123)
-- Menggunakan hash pbkdf2:sha256 yang kompatibel dengan Werkzeug
INSERT IGNORE INTO admin (id, username, password_hash, nama_lengkap) 
VALUES (1, 'admin', 'pbkdf2:sha256:600000$c1n38mNq9hYJ15Wp$7c71e21bca961cbbceae41ebff71f65ca24fa3b1d7d0ddb5ca7bfae8cbcf55e3', 'Administrator');
