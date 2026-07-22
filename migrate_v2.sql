-- =====================================================================
-- FILE MIGRASI DATABASE: migrate_v2.sql
-- =====================================================================
-- File SQL ini digunakan untuk memperbarui (migrasi) struktur tabel 
-- mahasiswa dan absensi dari versi lama ke versi baru (v2).
-- PERINGATAN: Menjalankan file ini akan menghapus tabel lama 
-- beserta seluruh data mahasiswa & riwayat absensi yang ada di dalamnya!
-- =====================================================================

USE skripsi_absensi_djki;

-- Nonaktifkan pengecekan Foreign Key sementara agar tabel bisa dihapus tanpa error
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS absensi;
DROP TABLE IF EXISTS mahasiswa;
SET FOREIGN_KEY_CHECKS = 1;

-- Membuat kembali tabel mahasiswa dengan skema terbaru (v2)
CREATE TABLE mahasiswa (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  npm VARCHAR(30) NOT NULL UNIQUE,                       -- Menggunakan kolom NPM (bukan NIM)
  jurusan VARCHAR(100),
  asal_universitas VARCHAR(150),
  email VARCHAR(100),
  nama_direktorat_lantai_magang VARCHAR(150) NOT NULL,   -- Penambahan kolom direktorat magang
  jobdesc_magang TEXT,                                   -- Penambahan kolom jobdesc magang
  periode_mulai DATE,
  periode_selesai DATE,
  periode_label VARCHAR(50),
  nama_mentor VARCHAR(100),
  wajah_selesai TINYINT(1) NOT NULL DEFAULT 0,
  label_id INT NOT NULL UNIQUE,
  foto_path VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat kembali tabel absensi dengan skema terbaru (v2)
CREATE TABLE absensi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mahasiswa_id INT NOT NULL,
  waktu DATETIME NOT NULL,
  status ENUM('masuk','keluar') DEFAULT 'masuk',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id) ON DELETE CASCADE,
  INDEX idx_waktu (waktu),
  INDEX idx_mahasiswa_id (mahasiswa_id)
);
