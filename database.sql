-- =====================================================================
-- SKEMA BASIS DATA: database.sql (MySQL)
-- =====================================================================
-- Script SQL ini digunakan untuk membuat struktur basis data
-- proyek skripsi "Sistem Absensi Mahasiswa Magang DJKI".
-- Database ini dioperasikan menggunakan MySQL (XAMPP / phpMyAdmin).
-- =====================================================================

-- 1. Membuat Database Baru jika belum ada
CREATE DATABASE IF NOT EXISTS skripsi_absensi_djki
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Gunakan database yang baru saja dibuat
USE skripsi_absensi_djki;

-- 2. Membuat Tabel Mahasiswa
-- Menyimpan semua profil mahasiswa magang
CREATE TABLE IF NOT EXISTS mahasiswa (
  id INT AUTO_INCREMENT PRIMARY KEY,                     -- Primary Key (Auto Increment)
  nama VARCHAR(100) NOT NULL,                            -- Nama lengkap mahasiswa magang
  npm VARCHAR(30) NOT NULL UNIQUE,                       -- Nomor Pokok Mahasiswa (NIM/NPM) - harus unik
  jurusan VARCHAR(100),                                  -- Program studi atau Jurusan
  asal_universitas VARCHAR(150),                         -- Perguruan tinggi asal mahasiswa
  email VARCHAR(100),                                    -- Alamat email aktif
  nama_direktorat_lantai_magang VARCHAR(150) NOT NULL,   -- Direktorat penempatan magang di DJKI
  jobdesc_magang TEXT,                                   -- Tugas atau deskripsi pekerjaan magang
  periode_mulai DATE,                                    -- Tanggal mulai magang
  periode_selesai DATE,                                  -- Tanggal selesai magang
  periode_label VARCHAR(50),                             -- Nama periode magang (misal: "Magang Batch 1")
  nama_mentor VARCHAR(100),                              -- Nama mentor pembimbing dari DJKI
  wajah_selesai TINYINT(1) NOT NULL DEFAULT 0,           -- Penanda apakah registrasi wajah sudah selesai (1=selesai, 0=belum)
  label_id INT NOT NULL UNIQUE COMMENT 'ID numerik untuk model LBPH', -- ID integer untuk pemetaan wajah di recognizer LBPH
  foto_path VARCHAR(255),                                -- Menyimpan lokasi file pasfoto profil
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- Tanggal pendaftaran data mahasiswa
);

-- 3. Membuat Tabel Absensi
-- Menyimpan seluruh riwayat log kehadiran masuk dan keluar
CREATE TABLE IF NOT EXISTS absensi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mahasiswa_id INT NOT NULL,                             -- Foreign Key mengarah ke tabel mahasiswa
  waktu DATETIME NOT NULL,                               -- Waktu tepat dilakukannya scan wajah absensi
  status ENUM('masuk','keluar') DEFAULT 'masuk',         -- Status absensi (masuk / keluar)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id) ON DELETE CASCADE, -- Hapus data absensi otomatis jika data mahasiswa dihapus
  INDEX idx_waktu (waktu),                               -- Index untuk mempercepat pencarian data berdasarkan waktu (filter tanggal)
  INDEX idx_mahasiswa_id (mahasiswa_id)                  -- Index relasi mahasiswa
);

-- 4. Membuat Tabel Admin
-- Menyimpan data admin/petugas yang berwenang mengelola sistem
CREATE TABLE IF NOT EXISTS admin (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,                  -- Kredensial untuk masuk ke aplikasi
  password_hash VARCHAR(255) NOT NULL,                   -- Kata sandi terenkripsi (PBKDF2)
  nama_lengkap VARCHAR(100),                             -- Nama lengkap admin
  email VARCHAR(100),
  nip VARCHAR(30),                                       -- Nomor Induk Pegawai admin
  jabatan VARCHAR(100),
  unit_kerja VARCHAR(150),
  no_hp VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
