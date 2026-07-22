-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 22 Jul 2026 pada 16.56
-- Versi server: 10.4.25-MariaDB
-- Versi PHP: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `skripsi_absensi_djki`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `absensi`
--

CREATE TABLE `absensi` (
  `id` int(11) NOT NULL,
  `mahasiswa_id` int(11) NOT NULL,
  `waktu` datetime NOT NULL,
  `status` enum('masuk','keluar','izin','tanpa keterangan') COLLATE utf8mb4_unicode_ci DEFAULT 'masuk',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `tipe_izin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `surat_izin_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `absensi`
--

INSERT INTO `absensi` (`id`, `mahasiswa_id`, `waktu`, `status`, `created_at`, `tipe_izin`, `surat_izin_path`) VALUES
(23, 21, '2026-07-21 11:34:08', 'masuk', '2026-07-21 04:34:08', NULL, NULL),
(24, 20, '2026-07-21 11:34:23', 'masuk', '2026-07-21 04:34:23', NULL, NULL),
(25, 19, '2026-07-21 11:35:02', 'masuk', '2026-07-21 04:35:02', NULL, NULL),
(26, 18, '2026-07-21 11:35:46', 'masuk', '2026-07-21 04:35:46', NULL, NULL),
(27, 17, '2026-07-21 11:36:04', 'masuk', '2026-07-21 04:36:04', NULL, NULL),
(28, 16, '2026-07-21 11:36:17', 'masuk', '2026-07-21 04:36:17', NULL, NULL),
(29, 15, '2026-07-21 11:36:35', 'masuk', '2026-07-21 04:36:35', NULL, NULL),
(30, 18, '2026-07-21 11:37:17', 'keluar', '2026-07-21 04:37:17', NULL, NULL),
(31, 18, '2026-07-21 11:37:41', 'masuk', '2026-07-21 04:37:41', NULL, NULL),
(32, 12, '2026-07-21 11:38:03', 'masuk', '2026-07-21 04:38:03', NULL, NULL),
(33, 12, '2026-07-21 11:38:16', 'keluar', '2026-07-21 04:38:16', NULL, NULL),
(34, 10, '2026-07-21 11:41:56', 'masuk', '2026-07-21 04:41:56', NULL, NULL),
(35, 13, '2026-07-22 14:20:51', 'masuk', '2026-07-22 07:20:51', NULL, NULL),
(36, 11, '2026-07-22 14:22:28', 'masuk', '2026-07-22 07:22:28', NULL, NULL),
(37, 25, '2026-07-22 15:15:21', 'masuk', '2026-07-22 08:15:21', NULL, NULL),
(38, 25, '2026-07-22 15:15:28', 'keluar', '2026-07-22 08:15:28', NULL, NULL),
(39, 22, '2026-07-22 15:15:52', 'masuk', '2026-07-22 08:15:52', NULL, NULL),
(40, 18, '2026-07-22 15:16:34', 'keluar', '2026-07-22 08:16:34', NULL, NULL),
(41, 23, '2026-07-22 15:18:37', 'masuk', '2026-07-22 08:18:37', NULL, NULL),
(42, 23, '2026-07-22 15:18:49', 'keluar', '2026-07-22 08:18:49', NULL, NULL),
(43, 22, '2026-07-22 15:19:16', 'keluar', '2026-07-22 08:19:16', NULL, NULL),
(44, 24, '2026-07-22 15:20:00', 'masuk', '2026-07-22 08:20:00', NULL, NULL),
(45, 24, '2026-07-22 15:20:30', 'keluar', '2026-07-22 08:20:30', NULL, NULL),
(46, 26, '2026-07-22 21:00:05', 'masuk', '2026-07-22 14:00:05', NULL, NULL),
(47, 27, '2026-07-22 21:05:36', 'masuk', '2026-07-22 14:05:36', NULL, NULL),
(48, 28, '2026-07-22 21:10:15', 'masuk', '2026-07-22 14:10:15', NULL, NULL),
(49, 29, '2026-07-22 21:12:52', 'masuk', '2026-07-22 14:12:52', NULL, NULL),
(50, 30, '2026-07-22 21:19:55', 'masuk', '2026-07-22 14:19:55', NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `nama_lengkap` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nip` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jabatan` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_kerja` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_hp` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `admin`
--

INSERT INTO `admin` (`id`, `username`, `password_hash`, `created_at`, `nama_lengkap`, `email`, `nip`, `jabatan`, `unit_kerja`, `no_hp`) VALUES
(1, 'Dedes', 'pbkdf2:sha256:1000000$PBpalfzrCpO9ABUj$18e44750150127441431e14606d8135b83cea9d7132a55d15bb055820ea498f0', '2026-03-15 05:40:09', 'DESVITA DAMAYANTI', 'desvitadamayanti2018@gmail.com', '20030611202609250', 'STAFF KEPEGAWAIAN', 'DIREKTORAT TEKNOLOGI INFORMASI', '081315996562');

-- --------------------------------------------------------

--
-- Struktur dari tabel `mahasiswa`
--

CREATE TABLE `mahasiswa` (
  `id` int(11) NOT NULL,
  `nama` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `npm` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `jurusan` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `asal_universitas` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nama_direktorat_lantai_magang` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `jobdesc_magang` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `periode_mulai` date DEFAULT NULL,
  `periode_selesai` date DEFAULT NULL,
  `periode_label` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nama_mentor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `wajah_selesai` tinyint(1) NOT NULL DEFAULT 0,
  `label_id` int(11) NOT NULL,
  `foto_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data untuk tabel `mahasiswa`
--

INSERT INTO `mahasiswa` (`id`, `nama`, `npm`, `jurusan`, `asal_universitas`, `email`, `nama_direktorat_lantai_magang`, `jobdesc_magang`, `periode_mulai`, `periode_selesai`, `periode_label`, `nama_mentor`, `wajah_selesai`, `label_id`, `foto_path`, `created_at`) VALUES
(10, 'AIDA SALSABILA', '24020100084', 'HUKUM', 'Universitas Muhammadiyah Jakarta', 'ayydslsbla@gmail.com', 'Sekretariat', 'Mahasiswa', '2026-07-13', '2026-08-13', '1 bulan', 'Najla ', 1, 4, 'pasfoto_24020100084_20260722_111105.jpg', '2026-07-21 03:55:24'),
(11, 'NADZRI MARZUKI FASI', '24020100068', 'HUKUM', 'Universitas Muhammadiyah Jakarta', 'marzukinadzri@gmail.com', 'Direktorat Merek', 'input data pegawai', '2026-07-13', '2026-08-13', '1 bulan', 'abil', 1, 5, 'pasfoto_24020100068_20260722_111126.jpg', '2026-07-21 04:00:37'),
(12, 'SHANDY PUTRA JAYA', '24020100124', 'HUKUM', 'Universitas Muhammadiyah Jakarta', 'shandyputrajaya.13@gmail.com', 'Sekretariat', 'umum', '2026-07-13', '2026-08-13', '1 bulan', 'yusuf', 1, 6, 'pasfoto_24020100124_20260722_111154.jpg', '2026-07-21 04:04:54'),
(13, 'CUT BALQIS SALSABILLA ARIFIN', '24020100045', 'HUKUM', 'Universitas Muhammadiyah Jakarta', 'balqis.salsa07@gmail.com', 'Direktorat Merek', 'umum', '2026-07-13', '2026-08-13', '1 bulan', 'abil', 1, 7, 'pasfoto_24020100045_20260722_111033.jpg', '2026-07-21 04:08:56'),
(14, 'RENDI AHMAD FAUZI', '24020100031', 'HUKUM', 'Universitas Muhammadiyah Jakarta', 'rendiahmadf15@gmail.com', 'Sekretariat', 'P2', '2026-07-13', '2026-08-13', '1 bulan', 'Nisa', 1, 8, 'pasfoto_24020100031_20260722_111148.jpg', '2026-07-21 04:11:19'),
(15, 'REYANDO SAGUNA MAGANI', '131231223', 'HUKUM', 'Universitas Airlangga', 'doni.magani@gmail.com', 'Direktorat Merek', 'Revisi Surat Kuasa Perkara Sengketa Merek', '2026-07-13', '2026-08-14', '1 bulan', 'Bu Sarah', 1, 9, 'pasfoto_131231223_20260722_111141.jpg', '2026-07-21 04:15:20'),
(16, 'RAYNOR DWIKI HARFIANTO', '131231288', 'HUKUM', 'Universitas Airlangga', 'renodwiki15@gmail.com', 'Direktorat Merek', 'Revisi Surat Kuasa Sengketa Merek', '2026-07-13', '2026-08-14', '1 bulan', 'Bu Sarah', 1, 10, 'pasfoto_131231288_20260722_111133.jpg', '2026-07-21 04:17:42'),
(17, 'ALINE ZALFA ALYSSA', '131231295', 'HUKUM', 'Universitas Airlangga', 'alinezalfaalyssa@gmail.com', 'Direktorat Merek', 'Revisi Surat Kuasa Sengketa Merek', '2026-07-13', '2026-08-14', '1 bulan', 'Bu Sarah', 1, 11, 'pasfoto_131231295_20260722_110829.jpg', '2026-07-21 04:19:46'),
(18, 'ANGGITA NASHWA TAUFIQA', '2406488080', 'HUKUM', 'Universitas Indonesia', 'anggitanashwa@gmail.com', 'Direktorat Merek', 'Pelayanan Hukum Direktorat Merek', '2026-07-20', '2026-08-20', '1 bulan', 'Bu Nova', 1, 12, 'pasfoto_2406488080_20260722_110915.jpg', '2026-07-21 04:24:18'),
(19, 'ARETHA RAJWA SANDYAHANA', '2406359506', 'HUKUM', 'Universitas Indonesia', 'aretharajwas@gmail.com', 'Direktorat Merek', 'Pelayanan Hukum Direktorat Merek', '2026-07-19', '2026-08-18', 'Kurang dari 1 bulan', 'Ibu Nova', 1, 13, 'pasfoto_2406359506_20260722_111022.jpg', '2026-07-21 04:26:59'),
(20, 'TAZKIYATUN NAFSI HERDIAWANTO', '2406359411', 'Ilmu Hukum', 'Universitas Indonesia', 'tazkeey2006@gmail.com', 'Direktorat Merek', 'Pelayanan hukum', '2026-07-19', '2026-08-18', 'Kurang dari 1 bulan', 'Ibu Nova', 1, 14, 'pasfoto_2406359411_20260722_111056.jpg', '2026-07-21 04:29:40'),
(21, 'GEOVARA SOAMBINGON SIREGAR', '2406417153', 'Ilmu Hukum', 'Universitas Indonesia', 'geovara.soambingon@ui.ac.id', 'Direktorat Merek', 'Legal assistance', '2006-07-19', '2026-08-18', '240 bulan', 'Ibu Nova', 1, 15, 'pasfoto_2406417153_20260722_111119.jpg', '2026-07-21 04:33:00'),
(22, 'KAYLA CARISSA NAZHALI', '110110230381', 'Ilmu Hukum', 'Universitas Padjadjaran', 'kaylacn12@gmail.com', 'Sekretariat', 'Membantu membuat laporan', '2026-07-06', '2026-08-06', '1 bulan', 'Bu Nuralia', 1, 16, 'pasfoto_110110230381_20260722_150450.jpg', '2026-07-22 08:04:50'),
(23, 'FAIZAH CALLISTA', '170710240041', 'sosiologi', 'Universitas Padjadjaran', 'faizah.callista18@gmail.com', 'Sekretariat', 'membuat dan merapikan laporan', '2026-07-06', '2026-08-10', '1 bulan', 'ardi tri harssoni', 1, 17, 'pasfoto_170710240041_20260722_150753.jpg', '2026-07-22 08:07:53'),
(24, 'MOHAMAD RAFI ATHALLAH', '24020100039', 'Ilmu Hukum', 'Universitas Muhammadiyah Jakarta', 'athallahrafi447@gmail.com', 'Sekretariat', 'Merapihkan dan Menyusun laporan', '2026-07-13', '2026-09-13', '2 bulan', 'abil', 1, 18, 'pasfoto_24020100039_20260722_151132.jpg', '2026-07-22 08:11:32'),
(25, 'SYIFA AULIA ZAHRA', '13010124140156', 'SASTRA INDONESIA', 'Universitas Diponegoro', 'syifaaul6@gmail.com', 'Direktorat Merek', 'Notulensi', '2026-07-01', '2026-08-03', '1 bulan', 'abil', 1, 19, 'pasfoto_13010124140156_20260722_151442.jpg', '2026-07-22 08:14:42'),
(26, 'HANY NURFALLAH', '444421053', 'MANAJEMEN', 'UNIVERSITAS SULTAN AGENG TIRTAYASA', NULL, 'Hak Cipta', 'Pencatatan', '2026-07-01', '2026-10-01', '3 bulan', 'Darwanto', 1, 20, 'pasfoto_444421053_20260722_205422.jpg', '2026-07-22 13:54:22'),
(27, 'NAZWA CENDRA SWARI', '1414422049', 'HUBUNGAN MASYARAKAT DAN KOMUNIKASI DIGITAL', 'UNIVERSITAS NEGERI JAKARTA', 'nazwa_1414422049@mhs.unj.ac.id', 'Kerjasama', 'MEDIA MONITORING', '2026-03-22', '2026-07-30', '4 bulan', 'DARA PUSPITA ', 1, 21, 'pasfoto_1414422049_20260722_210353.jpg', '2026-07-22 14:03:53'),
(28, 'HYLERI RAYA SYLVANA', '10122390', 'SISTEM INFORMASI', 'UNIVERSITAS GUNADARMA', 'hyleriraya2007@gmail.com', 'Teknologi Informasi', 'SOFTWARE ENGINEER', '2026-06-01', '2026-09-30', '3 bulan', 'BUDI SUSWANTO', 1, 22, 'pasfoto_10122390_20260722_210846.jpg', '2026-07-22 14:08:46'),
(29, 'DESVITA DAMAYANTI', '10122357', 'SISTEM INFORMASI', 'UNIVERSITAS GUNADARMA', 'desvitadamayantii20@gmail.com', 'Teknologi Informasi', 'SOFTWARE ENGINEER', '2026-06-01', '2026-09-30', '3 bulan', 'DEDI IMMANUEL GULTOM', 1, 23, 'pasfoto_10122357_20260722_211155.jpg', '2026-07-22 14:11:55'),
(30, 'VIOLET GHAISANI NAGARI', '0105216695', 'ILMU KOMUNIKASI', 'UNIVERSITAS BRAWIJAYA', NULL, 'Kerjasama', 'ILKOM', '2026-06-01', '2026-08-31', '2 bulan', 'SIMAN', 1, 24, 'pasfoto_0105216695_20260722_211813.jpg', '2026-07-22 14:18:13');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_waktu` (`waktu`),
  ADD KEY `idx_mahasiswa_id` (`mahasiswa_id`);

--
-- Indeks untuk tabel `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indeks untuk tabel `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `npm` (`npm`),
  ADD UNIQUE KEY `label_id` (`label_id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `absensi`
--
ALTER TABLE `absensi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT untuk tabel `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `mahasiswa`
--
ALTER TABLE `mahasiswa`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `absensi`
--
ALTER TABLE `absensi`
  ADD CONSTRAINT `absensi_ibfk_1` FOREIGN KEY (`mahasiswa_id`) REFERENCES `mahasiswa` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
