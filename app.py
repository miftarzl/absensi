# =====================================================================
# FILE UTAMA BACKEND: app.py (Controller / Routing Server)
# =====================================================================
# File ini berfungsi sebagai otak/pengendali utama web server absensi.
# Menggunakan framework Flask (Python) untuk:
# 1. Melayani file web statis (HTML, CSS, JS) di folder /static ke browser.
# 2. Menyediakan API Endpoint (rute JSON) untuk berinteraksi dengan basis data.
# 3. Menghubungkan fungsi deteksi & pengenalan wajah dari face_service.py.
# 4. Mengelola hak akses (login & session admin).
# =====================================================================

import os
import base64
import glob
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

# Konfigurasi Zona Waktu WIB (Waktu Indonesia Barat / UTC+7)
WIB = timezone(timedelta(hours=7))

def get_wib_now():
    """Mengembalikan datetime saat ini sesuai Waktu Indonesia Barat (WIB / UTC+7)."""
    return datetime.now(WIB).replace(tzinfo=None)

from config import Config
from database import get_cursor, init_db
from face_service import (
    ensure_dirs,
    prepare_image_for_training,
    train_lbph,
    recognize_face,
    decode_image_from_base64,
    detect_faces,
)

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
CORS(app, supports_credentials=True)

# Daftar direktorat DJKI (urutan resmi)
DIREKTORAT_LIST = [
    'Sekretariat',
    'Direktorat Merek',
    'Paten',
    'Hak Cipta',
    'Indikasi Geografis',
    'Kerjasama',
    'Teknologi Informasi',
]

def _auto_admin_session():
    """Dev: set session admin otomatis jika SKIP_ADMIN_LOGIN aktif."""
    if not Config.SKIP_ADMIN_LOGIN or session.get('admin_id'):
        return
    try:
        with get_cursor() as cur:
            cur.execute('SELECT id FROM admin ORDER BY id ASC LIMIT 1')
            row = cur.fetchone()
        if row:
            session['admin_id'] = row['id']
            session.permanent = True
    except Exception:
        pass

def require_admin(f):
    """Decorator: hanya admin yang sudah login yang bisa akses."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        _auto_admin_session()
        if not session.get('admin_id'):
            return jsonify({'success': False, 'error': 'Harus login sebagai admin.'}), 401
        return f(*args, **kwargs)
    return wrapped

# Inisialisasi folder dan database saat startup
@app.before_request
def _ensure_folders():
    ensure_dirs()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/absensi')
def page_absensi():
    """Halaman absensi publik (tanpa login) — untuk jam kerja."""
    return send_from_directory(app.static_folder, 'absensi.html')

@app.route('/api/me', methods=['GET'])
def api_me():
    """Cek apakah user sudah login (untuk frontend)."""
    _auto_admin_session()
    if session.get('admin_id'):
        profile = _get_admin_profile_row(session['admin_id'])
        return jsonify({
            'success': True,
            'logged_in': True,
            'skip_login': Config.SKIP_ADMIN_LOGIN,
            'username': profile.get('username') if profile else '',
            'nama_lengkap': profile.get('nama_lengkap') if profile else '',
        })
    return jsonify({'success': True, 'logged_in': False, 'skip_login': Config.SKIP_ADMIN_LOGIN})

def _get_admin_profile_row(admin_id):
    try:
        with get_cursor() as cur:
            cur.execute('''SELECT id, username, nama_lengkap, email, nip, jabatan, unit_kerja, no_hp, created_at
                FROM admin WHERE id = %s''', (admin_id,))
            return cur.fetchone()
    except Exception:
        return None

def _admin_profile_payload(row):
    if not row:
        return None
    display_name = (row.get('nama_lengkap') or '').strip() or row.get('username') or 'Admin'
    return {
        'id': row['id'],
        'username': row.get('username') or '',
        'nama_lengkap': row.get('nama_lengkap') or '',
        'display_name': display_name,
        'email': row.get('email') or '',
        'nip': row.get('nip') or '',
        'jabatan': row.get('jabatan') or '',
        'unit_kerja': row.get('unit_kerja') or '',
        'no_hp': row.get('no_hp') or '',
        'created_at': row['created_at'].isoformat() if row.get('created_at') else '',
    }

@app.route('/api/admin/profile', methods=['GET', 'PUT'])
@require_admin
def api_admin_profile():
    """Profil admin yang sedang login — GET lihat, PUT ubah data & akun."""
    if request.method == 'GET':
        row = _get_admin_profile_row(session['admin_id'])
        if not row:
            return jsonify({'success': False, 'error': 'Admin tidak ditemukan.'}), 404
        return jsonify({'success': True, 'data': _admin_profile_payload(row)})

    data = request.get_json() or {}
    current = data.get('current_password') or ''
    new_username = (data.get('username') or '').strip()
    new_password = data.get('new_password') or ''
    profile_fields = {
        'nama_lengkap': (data.get('nama_lengkap') or '').strip(),
        'email': (data.get('email') or '').strip(),
        'nip': (data.get('nip') or '').strip(),
        'jabatan': (data.get('jabatan') or '').strip(),
        'unit_kerja': (data.get('unit_kerja') or '').strip(),
        'no_hp': (data.get('no_hp') or '').strip(),
    }
    changing_creds = bool(new_username or new_password)
    try:
        with get_cursor() as cur:
            cur.execute('SELECT id, username, password_hash FROM admin WHERE id = %s', (session['admin_id'],))
            row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Admin tidak ditemukan.'}), 404
        if changing_creds:
            if not current:
                return jsonify({'success': False, 'error': 'Password saat ini wajib diisi untuk mengubah username/password.'}), 400
            if not check_password_hash(row['password_hash'], current):
                return jsonify({'success': False, 'error': 'Password saat ini salah.'}), 401
        if new_username and new_username != row['username']:
            with get_cursor() as cur:
                cur.execute('SELECT id FROM admin WHERE username = %s AND id != %s', (new_username, session['admin_id']))
                if cur.fetchone():
                    return jsonify({'success': False, 'error': 'Username sudah dipakai.', 'field': 'username'}), 400
                cur.execute('UPDATE admin SET username = %s WHERE id = %s', (new_username, session['admin_id']))
        if new_password:
            with get_cursor() as cur:
                cur.execute('UPDATE admin SET password_hash = %s WHERE id = %s',
                            (generate_password_hash(new_password, method='pbkdf2:sha256'), session['admin_id']))
        sets = []
        params = []
        for key, val in profile_fields.items():
            sets.append(f'{key} = %s')
            params.append(val or None)
        if sets:
            params.append(session['admin_id'])
            with get_cursor() as cur:
                cur.execute(f"UPDATE admin SET {', '.join(sets)} WHERE id = %s", params)
        updated = _get_admin_profile_row(session['admin_id'])
        return jsonify({'success': True, 'message': 'Profil berhasil diperbarui.', 'data': _admin_profile_payload(updated)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login admin. Body: { "username": "...", "password": "..." }"""
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username dan password wajib diisi.'}), 400
    try:
        with get_cursor() as cur:
            cur.execute('SELECT id, password_hash FROM admin WHERE username = %s', (username,))
            row = cur.fetchone()
        if not row or not check_password_hash(row['password_hash'], password):
            return jsonify({'success': False, 'error': 'Username atau password salah.'}), 401
        session['admin_id'] = row['id']
        session.permanent = True
        return jsonify({'success': True, 'message': 'Login berhasil.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout admin."""
    session.pop('admin_id', None)
    return jsonify({'success': True})

@app.route('/api/init-db', methods=['POST'])
def api_init_db():
    """Inisialisasi tabel database (untuk development/setup)."""
    try:
        init_db()
        return jsonify({'success': True, 'message': 'Database diinisialisasi.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Direktorat (list tetap) ---
@app.route('/api/direktorat', methods=['GET'])
@require_admin
def api_direktorat():
    """Daftar direktorat DJKI (untuk dropdown & pengelompokan)."""
    return jsonify({'success': True, 'data': DIREKTORAT_LIST})

# --- Mahasiswa (hanya admin) ---

def _mahasiswa_foto_url(mahasiswa_id, foto_path):
    if foto_path:
        return f'/api/mahasiswa/{mahasiswa_id}/foto'
    return None

@app.route('/api/mahasiswa/<int:id>/foto')
@require_admin
def api_mahasiswa_foto(id):
    """Pasfoto mahasiswa."""
    try:
        with get_cursor() as cur:
            cur.execute('SELECT foto_path FROM mahasiswa WHERE id = %s', (id,))
            row = cur.fetchone()
        if not row or not row.get('foto_path'):
            return jsonify({'success': False, 'error': 'Pasfoto belum tersedia.'}), 404
        return send_from_directory(Config.PASFOTO_FOLDER, row['foto_path'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mahasiswa', methods=['GET'])
@require_admin
def api_list_mahasiswa():
    """Daftar semua mahasiswa magang."""
    try:
        with get_cursor() as cur:
            cur.execute('''SELECT id, nama, npm, jurusan, asal_universitas, email,
                nama_direktorat_lantai_magang, jobdesc_magang,
                periode_mulai, periode_selesai, periode_label, nama_mentor,
                wajah_selesai,
                label_id, foto_path, created_at
                FROM mahasiswa ORDER BY nama_direktorat_lantai_magang, nama''')
            rows = cur.fetchall()
        # Tambahkan info apakah sudah punya sampel wajah (folder faces/<label_id> berisi file)
        for r in rows:
            r['has_wajah'] = bool(r.get('wajah_selesai'))
            r['foto_url'] = _mahasiswa_foto_url(r['id'], r.get('foto_path'))
            # Format dates to ISO string YYYY-MM-DD so HTML inputs display them correctly
            for key in ('periode_mulai', 'periode_selesai'):
                if r.get(key):
                    r[key] = r[key].isoformat() if hasattr(r[key], 'isoformat') else str(r[key])
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mahasiswa', methods=['POST'])
@require_admin
def api_tambah_mahasiswa():
    """Tambah mahasiswa magang dengan pasfoto."""
    data = request.get_json() or {}
    npm = (data.get('npm') or '').strip()
    nama = (data.get('nama') or '').strip()
    direktorat = (data.get('nama_direktorat_lantai_magang') or '').strip()
    pasfoto_b64 = data.get('pasfoto')
    fields = {}
    if not nama:
        fields['nama'] = 'Nama wajib diisi.'
    if not npm:
        fields['npm'] = 'NPM wajib diisi.'
    if not direktorat:
        fields['nama_direktorat_lantai_magang'] = 'Direktorat wajib dipilih.'
    elif direktorat not in DIREKTORAT_LIST:
        fields['nama_direktorat_lantai_magang'] = 'Pilih direktorat dari daftar yang tersedia.'
    if not pasfoto_b64:
        fields['pasfoto_file'] = 'Pasfoto wajib diunggah.'

    if fields:
        return jsonify({'success': False, 'error': 'Periksa kembali data yang diisi.', 'fields': fields}), 400
    try:
        # Decode pasfoto
        img = decode_image_from_base64(pasfoto_b64)
        if img is None:
            return jsonify({'success': False, 'error': 'Periksa kembali data yang diisi.', 'fields': {'pasfoto_file': 'File pasfoto tidak valid.'}}), 400

        # Simpan pasfoto
        filename = f"pasfoto_{npm}_{get_wib_now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(Config.PASFOTO_FOLDER, filename)
        import cv2
        cv2.imwrite(filepath, img)

        with get_cursor() as cur:
            cur.execute('SELECT id FROM mahasiswa WHERE npm = %s', (npm,))
            if cur.fetchone():
                # Hapus file pasfoto yang baru disimpan karena NPM duplikat
                if os.path.isfile(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                return jsonify({'success': False, 'error': 'NPM sudah terdaftar.', 'fields': {'npm': 'NPM sudah terdaftar.'}}), 400
            cur.execute('SELECT COALESCE(MAX(label_id), 0) + 1 AS next_id FROM mahasiswa')
            next_label = cur.fetchone()['next_id']
            cur.execute(
                '''INSERT INTO mahasiswa (nama, npm, jurusan, asal_universitas, email,
                nama_direktorat_lantai_magang, jobdesc_magang,
                periode_mulai, periode_selesai, periode_label, nama_mentor,
                label_id, foto_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    nama,
                    npm,
                    data.get('jurusan'),
                    data.get('asal_universitas'),
                    data.get('email'),
                    direktorat,
                    data.get('jobdesc_magang'),
                    data.get('periode_mulai'),
                    data.get('periode_selesai'),
                    data.get('periode_label'),
                    data.get('nama_mentor'),
                    next_label,
                    filename,
                ),
            )
            cur.execute('SELECT LAST_INSERT_ID() AS id')
            id_ = cur.fetchone()['id']
        return jsonify({'success': True, 'id': id_, 'label_id': next_label})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/mahasiswa/<int:id>', methods=['GET'])
@require_admin
def api_get_mahasiswa(id):
    try:
        with get_cursor() as cur:
            cur.execute('''SELECT id, nama, npm, jurusan, asal_universitas, email,
                nama_direktorat_lantai_magang, jobdesc_magang,
                periode_mulai, periode_selesai, periode_label, nama_mentor,
                label_id, foto_path, created_at
                FROM mahasiswa WHERE id = %s''', (id,))
            row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Mahasiswa tidak ditemukan.'}), 404
        # Format dates to ISO string YYYY-MM-DD so HTML inputs display them correctly
        for key in ('periode_mulai', 'periode_selesai'):
            if row.get(key):
                row[key] = row[key].isoformat() if hasattr(row[key], 'isoformat') else str(row[key])
        return jsonify({'success': True, 'data': row})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mahasiswa/<int:id>', methods=['PUT'])
@require_admin
def api_update_mahasiswa(id):
    """Update data mahasiswa magang."""
    data = request.get_json() or {}
    npm = (data.get('npm') or '').strip()
    nama = (data.get('nama') or '').strip()
    direktorat = (data.get('nama_direktorat_lantai_magang') or '').strip()
    pasfoto_b64 = data.get('pasfoto')
    fields = {}
    if not nama:
        fields['nama'] = 'Nama wajib diisi.'
    if not npm:
        fields['npm'] = 'NPM wajib diisi.'
    if not direktorat:
        fields['nama_direktorat_lantai_magang'] = 'Direktorat wajib dipilih.'
    elif direktorat not in DIREKTORAT_LIST:
        fields['nama_direktorat_lantai_magang'] = 'Pilih direktorat dari daftar yang tersedia.'
    if fields:
        return jsonify({'success': False, 'error': 'Periksa kembali data yang diisi.', 'fields': fields}), 400
    try:
        with get_cursor() as cur:
            # pastikan npm unik (kecuali untuk id ini sendiri)
            cur.execute('SELECT id FROM mahasiswa WHERE npm = %s AND id <> %s', (npm, id))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'NPM sudah terdaftar.', 'fields': {'npm': 'NPM sudah terdaftar.'}}), 400
            
            # Ambil foto_path lama untuk dihapus jika diupdate
            cur.execute('SELECT foto_path FROM mahasiswa WHERE id = %s', (id,))
            row = cur.fetchone()
            old_foto_path = row.get('foto_path') if row else None

        new_foto_filename = None
        if pasfoto_b64:
            img = decode_image_from_base64(pasfoto_b64)
            if img is not None:
                new_foto_filename = f"pasfoto_{npm}_{get_wib_now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(Config.PASFOTO_FOLDER, new_foto_filename)
                import cv2
                cv2.imwrite(filepath, img)
                # Hapus file lama jika ada
                if old_foto_path:
                    old_filepath = os.path.join(Config.PASFOTO_FOLDER, old_foto_path)
                    if os.path.isfile(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except Exception:
                            pass
            else:
                return jsonify({'success': False, 'error': 'Periksa kembali data yang diisi.', 'fields': {'pasfoto_file': 'File pasfoto tidak valid.'}}), 400

        with get_cursor() as cur:
            if new_foto_filename:
                cur.execute(
                    '''UPDATE mahasiswa
                       SET nama=%s,
                           npm=%s,
                           jurusan=%s,
                           asal_universitas=%s,
                           email=%s,
                           nama_direktorat_lantai_magang=%s,
                           jobdesc_magang=%s,
                           periode_mulai=%s,
                           periode_selesai=%s,
                           periode_label=%s,
                           nama_mentor=%s,
                           foto_path=%s
                       WHERE id=%s''',
                    (
                        nama,
                        npm,
                        data.get('jurusan'),
                        data.get('asal_universitas'),
                        data.get('email'),
                        direktorat,
                        data.get('jobdesc_magang'),
                        data.get('periode_mulai'),
                        data.get('periode_selesai'),
                        data.get('periode_label'),
                        data.get('nama_mentor'),
                        new_foto_filename,
                        id,
                    ),
                )
            else:
                cur.execute(
                    '''UPDATE mahasiswa
                       SET nama=%s,
                           npm=%s,
                           jurusan=%s,
                           asal_universitas=%s,
                           email=%s,
                           nama_direktorat_lantai_magang=%s,
                           jobdesc_magang=%s,
                           periode_mulai=%s,
                           periode_selesai=%s,
                           periode_label=%s,
                           nama_mentor=%s
                       WHERE id=%s''',
                    (
                        nama,
                        npm,
                        data.get('jurusan'),
                        data.get('asal_universitas'),
                        data.get('email'),
                        direktorat,
                        data.get('jobdesc_magang'),
                        data.get('periode_mulai'),
                        data.get('periode_selesai'),
                        data.get('periode_label'),
                        data.get('nama_mentor'),
                        id,
                    ),
                )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mahasiswa/<int:id>', methods=['DELETE'])
@require_admin
def api_hapus_mahasiswa(id):
    try:
        # ambil label_id untuk hapus folder wajah dan pasfoto
        label_id = None
        foto_path = None
        with get_cursor() as cur:
            cur.execute('SELECT label_id, foto_path FROM mahasiswa WHERE id = %s', (id,))
            row = cur.fetchone()
            if row:
                label_id = row.get('label_id')
                foto_path = row.get('foto_path')
            cur.execute('DELETE FROM mahasiswa WHERE id = %s', (id,))
        if label_id is not None:
            face_dir = os.path.join(Config.FACES_FOLDER, str(label_id))
            if os.path.isdir(face_dir):
                import shutil
                shutil.rmtree(face_dir, ignore_errors=True)
        if foto_path:
            filepath = os.path.join(Config.PASFOTO_FOLDER, foto_path)
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Registrasi wajah (tambah sampel foto) ---
@app.route('/api/mahasiswa/<int:id>/wajah', methods=['POST'])
@require_admin
def api_tambah_wajah(id):
    """
    Tambah sampel wajah untuk mahasiswa (base64 image).
    Body: { "image": "data:image/jpeg;base64,..." }
    """
    data = request.get_json() or {}
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'success': False, 'error': 'Gambar (image) wajib dikirim.'}), 400
    try:
        # [PROSES DEKODE] Mengubah gambar dari format string base64 menjadi format matriks BGR OpenCV
        img = decode_image_from_base64(image_b64)
        if img is None:
            return jsonify({'success': False, 'error': 'Gambar tidak valid.'}), 400
            
        # #Tahap 2 pra-pemrosesan citra
        # (Di dalamnya juga menjalankan #Tahap 1 deteksi wajah untuk mencari koordinat area wajah)
        # Meliputi konversi grayscale, deteksi wajah, crop ROI wajah, resize ke 200x200 piksel, dan pemerataan cahaya (CLAHE)
        roi, _ = prepare_image_for_training(img)
        if roi is None:
            return jsonify({'success': False, 'error': 'Wajah tidak terdeteksi. Pastikan wajah tampak jelas.'}), 400
        with get_cursor() as cur:
            cur.execute('SELECT label_id FROM mahasiswa WHERE id = %s', (id,))
            row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Mahasiswa tidak ditemukan.'}), 404
        label_id = row['label_id']
        # Simpan ROI ke folder faces untuk nanti di-train
        ensure_dirs()
        face_dir = os.path.join(Config.FACES_FOLDER, str(label_id))
        os.makedirs(face_dir, exist_ok=True)
        import cv2
        filename = f"{get_wib_now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(face_dir, filename)
        cv2.imwrite(filepath, roi)
        return jsonify({'success': True, 'message': 'Sampel wajah berhasil disimpan.', 'file': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/mahasiswa/<int:id>/wajah-selesai', methods=['POST'])
@require_admin
def api_tandai_wajah_selesai(id):
    """Tandai bahwa registrasi wajah mahasiswa sudah selesai (semua pose diambil)."""
    try:
        with get_cursor() as cur:
            cur.execute('UPDATE mahasiswa SET wajah_selesai = 1 WHERE id = %s', (id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Training model LBPH ---
@app.route('/api/train', methods=['POST'])
@require_admin
def api_train():
    """Latih ulang model LBPH dari semua sampel wajah di folder faces."""
    import cv2
    import glob
    ensure_dirs()
    face_images = []
    labels = []
    for label_dir in os.listdir(Config.FACES_FOLDER):
        path_dir = os.path.join(Config.FACES_FOLDER, label_dir)
        if not os.path.isdir(path_dir):
            continue
        try:
            label_id = int(label_dir)
        except ValueError:
            continue
        for fp in glob.glob(os.path.join(path_dir, '*.jpg')):
            img = cv2.imread(fp, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (200, 200))
                face_images.append(img)
                labels.append(label_id)
    if len(face_images) < 2:
        return jsonify({'success': False, 'error': 'Minimal 2 sampel wajah dari minimal 1 mahasiswa untuk training.'}), 400
    try:
        # #Tahap 3 pelatihan model (Training LBPH)
        # Melatih model recognizer OpenCV LBPH dengan sampel wajah dan menyimpannya sebagai file 'lbph_model.yml'
        train_lbph(face_images, labels)
        return jsonify({'success': True, 'message': f'Model berhasil dilatih dengan {len(face_images)} sampel.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Absensi (publik, tanpa login — dipakai saat jam kerja) ---
@app.route('/api/absensi', methods=['POST'])
def api_absensi():
    """
    Catat absensi dari gambar wajah (base64).
    Body: { "image": "data:image/jpeg;base64,...", "status": "masuk" | "keluar" }
    """
    data = request.get_json() or {}
    image_b64 = data.get('image')
    status = (data.get('status') or 'masuk').strip().lower()
    if status not in ('masuk', 'keluar'):
        status = 'masuk'
    if not image_b64:
        return jsonify({'success': False, 'error': 'Gambar wajah wajib dikirim.'}), 400
    try:
        # [PROSES DEKODE] Mengubah string base64 dari webcam menjadi format matriks BGR OpenCV
        img = decode_image_from_base64(image_b64)
        if img is None:
            return jsonify({'success': False, 'error': 'Gambar tidak valid.'}), 400
            
        # #Tahap 1 deteksi wajah
        # Mengonversi gambar ke grayscale dan mendeteksi koordinat wajah menggunakan Haar Cascade.
        # Menghitung jumlah wajah untuk memastikan hanya 1 orang yang melakukan absen di depan kamera.
        try:
            import cv2
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)
            if len(faces) == 0:
                return jsonify({'success': False, 'error': 'Wajah tidak terdeteksi.'}), 400
            if len(faces) > 1:
                return jsonify({'success': False, 'error': 'Terdeteksi lebih dari 1 wajah. Pastikan hanya 1 orang di depan kamera.'}), 400
        except Exception:
            faces = None
            
        # #Tahap 2 pra-pemrosesan citra
        # Melakukan crop pada area wajah terdeteksi, resize ke 200x200 piksel, dan perataan cahaya dengan CLAHE.
        roi, _ = prepare_image_for_training(img)
        if roi is None:
            return jsonify({'success': False, 'error': 'Wajah tidak terdeteksi.'}), 400
            
        # #Tahap 4 pengenalan wajah (Recognition / Prediksi)
        # Membandingkan histogram wajah masukan dengan histogram model LBPH ('lbph_model.yml') untuk memprediksi identitas (label_id).
        label_id, confidence = recognize_face(roi)
        if label_id is None:
            return jsonify({'success': False, 'error': 'Wajah tidak dikenali.', 'confidence': confidence}), 404
        with get_cursor() as cur:
            cur.execute('SELECT id, nama, asal_universitas, nama_direktorat_lantai_magang, wajah_selesai FROM mahasiswa WHERE label_id = %s', (label_id,))
            mhs = cur.fetchone()
        if not mhs:
            return jsonify({'success': False, 'error': 'Data mahasiswa tidak ditemukan.'}), 404
        if not mhs.get('wajah_selesai'):
            return jsonify({'success': False, 'error': 'Registrasi wajah mahasiswa ini belum lengkap. Lengkapi 5 pose dan klik "Selesai" di admin.'}), 400
        # Cek absensi terakhir: tidak boleh double (masuk dua kali atau keluar dua kali berurutan)
        with get_cursor() as cur:
            cur.execute(
                'SELECT status FROM absensi WHERE mahasiswa_id = %s ORDER BY waktu DESC LIMIT 1',
                (mhs['id'],)
            )
            last = cur.fetchone()
        last_status = (str(last['status']).strip().lower() if last and last.get('status') else None)
        if last_status and last_status == status:
            other = 'keluar' if status == 'masuk' else 'masuk'
            return jsonify({
                'success': False,
                'error': f'Sudah absen {status} sebelumnya. Silakan lakukan absen {other} terlebih dahulu (absen masuk saat datang, absen keluar saat pulang).',
                'last_status': last_status,
                'next_allowed': other,
            }), 400
        waktu = get_wib_now()
        with get_cursor() as cur:
            cur.execute('INSERT INTO absensi (mahasiswa_id, waktu, status) VALUES (%s, %s, %s)',
                        (mhs['id'], waktu, status))
        return jsonify({
            'success': True,
            'message': f"Absensi {status} berhasil dicatat.",
            'mahasiswa': {'id': mhs['id'], 'nama': mhs['nama'], 'asal_universitas': mhs.get('asal_universitas'), 'nama_direktorat_lantai_magang': mhs.get('nama_direktorat_lantai_magang')},
            'waktu': waktu.isoformat(),
            'status': status,
            'confidence': confidence,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Laporan absensi (hanya admin), filter by direktorat ---
@app.route('/api/laporan', methods=['GET'])
@require_admin
def api_laporan():
    """Laporan absensi.

    Query:
      - dari, sampai: YYYY-MM-DD (range tanggal)
      - direktorat: nama direktorat
      - mahasiswa_id: optional, untuk lihat detail per mahasiswa (dipakai dari halaman laporan)
    """
    dari = request.args.get('dari')
    sampai = request.args.get('sampai')
    direktorat = request.args.get('direktorat', '').strip()
    mahasiswa_id = request.args.get('mahasiswa_id')
    try:
        with get_cursor() as cur:
            sql = '''
                SELECT a.id,
                       a.mahasiswa_id,
                       m.npm,
                       m.nama,
                       m.nama_direktorat_lantai_magang,
                       m.asal_universitas,
                       m.periode_mulai,
                       m.periode_selesai,
                       m.periode_label,
                       m.nama_mentor,
                       a.waktu,
                       a.status,
                       a.tipe_izin,
                       a.surat_izin_path
                FROM absensi a
                JOIN mahasiswa m ON m.id = a.mahasiswa_id
                WHERE 1=1
            '''
            params = []
            if dari:
                sql += ' AND DATE(a.waktu) >= %s'
                params.append(dari)
            if sampai:
                sql += ' AND DATE(a.waktu) <= %s'
                params.append(sampai)
            if direktorat and direktorat in DIREKTORAT_LIST:
                sql += ' AND m.nama_direktorat_lantai_magang = %s'
                params.append(direktorat)
            if mahasiswa_id:
                sql += ' AND m.id = %s'
                params.append(mahasiswa_id)
            sql += ' ORDER BY a.waktu DESC'
            cur.execute(sql, params)
            rows = cur.fetchall()
        for r in rows:
            if r.get('waktu'):
                r['waktu'] = r['waktu'].isoformat() if hasattr(r['waktu'], 'isoformat') else str(r['waktu'])
            for key in ('periode_mulai', 'periode_selesai'):
                if r.get(key):
                    r[key] = r[key].isoformat() if hasattr(r[key], 'isoformat') else str(r[key])
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/absensi/manual', methods=['POST'])
@require_admin
def api_absensi_manual():
    """Catat ketidakhadiran (izin/tanpa keterangan) secara manual oleh admin."""
    try:
        mahasiswa_id = request.form.get('mahasiswa_id')
        tanggal_str = request.form.get('tanggal')
        status = request.form.get('status')
        tipe_izin = request.form.get('tipe_izin')
        
        if not mahasiswa_id or not tanggal_str or not status:
            return jsonify({'success': False, 'error': 'Mahasiswa, tanggal, dan status wajib diisi.'}), 400
            
        if status not in ('izin', 'tanpa keterangan'):
            return jsonify({'success': False, 'error': 'Status tidak valid.'}), 400
            
        try:
            # Format expected: YYYY-MM-DD
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d')
            # Set time to 08:00:00 for the absence record
            waktu = tanggal.replace(hour=8, minute=0, second=0, microsecond=0)
        except ValueError:
            return jsonify({'success': False, 'error': 'Format tanggal tidak valid.'}), 400

        with get_cursor() as cur:
            cur.execute('SELECT id FROM mahasiswa WHERE id = %s', (mahasiswa_id,))
            if not cur.fetchone():
                return jsonify({'success': False, 'error': 'Mahasiswa tidak ditemukan.'}), 404

        filename = None
        if status == 'izin':
            if tipe_izin not in ('sakit', 'lainnya'):
                return jsonify({'success': False, 'error': 'Tipe izin wajib dipilih (sakit atau lainnya).'}), 400
                
            # Handle PDF upload
            file = request.files.get('surat_izin')
            if file:
                if not file.filename.lower().endswith('.pdf'):
                    return jsonify({'success': False, 'error': 'File harus berformat PDF.'}), 400
                
                ensure_dirs()
                import uuid
                filename = f"surat_izin_{mahasiswa_id}_{waktu.strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}.pdf"
                filepath = os.path.join(Config.SURAT_IZIN_FOLDER, filename)
                file.save(filepath)
            else:
                return jsonify({'success': False, 'error': 'Surat izin PDF wajib diunggah.'}), 400
        else:
            tipe_izin = None

        with get_cursor() as cur:
            cur.execute(
                '''INSERT INTO absensi (mahasiswa_id, waktu, status, tipe_izin, surat_izin_path)
                   VALUES (%s, %s, %s, %s, %s)''',
                (mahasiswa_id, waktu, status, tipe_izin, filename)
            )
            
        return jsonify({'success': True, 'message': 'Ketidakhadiran berhasil disimpan.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/absensi/<int:id>/surat-izin', methods=['GET'])
@require_admin
def api_download_surat_izin(id):
    """Melihat/mengunduh berkas PDF surat izin."""
    try:
        with get_cursor() as cur:
            cur.execute('SELECT surat_izin_path FROM absensi WHERE id = %s', (id,))
            row = cur.fetchone()
        if not row or not row.get('surat_izin_path'):
            return jsonify({'success': False, 'error': 'Berkas surat izin tidak ditemukan.'}), 404
        return send_from_directory(Config.SURAT_IZIN_FOLDER, row['surat_izin_path'])
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Deteksi wajah (untuk preview di frontend) ---
@app.route('/api/detect', methods=['POST'])
@require_admin
def api_detect():
    """Cek apakah ada wajah di gambar (untuk validasi sebelum simpan/training)."""
    data = request.get_json() or {}
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'success': False, 'error': 'Gambar wajib dikirim.'}), 400
    try:
        img = decode_image_from_base64(image_b64)
        if img is None:
            return jsonify({'success': False, 'error': 'Gambar tidak valid.'}), 400
        import cv2
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)
        return jsonify({'success': True, 'count': len(faces), 'detected': len(faces) > 0})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
