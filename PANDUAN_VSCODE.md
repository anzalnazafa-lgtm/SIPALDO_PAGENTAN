# 🧑‍💻 PANDUAN MENJALANKAN SIPALDO-PAGENTAN DI VS CODE

Panduan langkah demi langkah menjalankan aplikasi **SIPALDO-PAGENTAN** (Sistem Peringatan Dini Longsor Desa Pagentan) di komputer/laptop Anda memakai **Visual Studio Code**.

> Waktu pengerjaan: ±10 menit. Tidak perlu akun, API key, atau kartu kredit — semua sumber data gratis.

---

## 0. Yang Perlu Disiapkan

| Kebutuhan | Keterangan |
|---|---|
| **Python 3.10 – 3.13** | Unduh di <https://www.python.org/downloads/>. Saat instal di Windows, **centang “Add python.exe to PATH”**. |
| **VS Code** | Unduh di <https://code.visualstudio.com/> |
| **File ZIP proyek** | `SIPALDO-PAGENTAN.zip` |
| **Koneksi internet** | Untuk mengambil data cuaca Open-Meteo & peta OpenStreetMap (jika putus, aplikasi otomatis menampilkan *“estimasi offline”* — tidak crash). |

---

## 1. Ekstrak ZIP dan Buka Folder di VS Code

1. Ekstrak `SIPALDO-PAGENTAN.zip` (misalnya ke `D:\Project\SIPALDO-PAGENTAN` atau `~/Project/SIPALDO-PAGENTAN`).
2. Buka **VS Code** → menu **File → Open Folder…** → pilih folder **`SIPALDO-PAGENTAN`** (folder yang berisi `app.py`).
3. Pastikan di panel kiri terlihat: `app.py`, `gis_engine.py`, `weather_ews.py`, `charts_qr.py`, `requirements.txt`, `README.md`, folder `.streamlit`.

> Windows: jika folder `.streamlit` tidak terlihat, aktifkan **View → Show Hidden Files** / di Explorer centang *Hidden items*. Folder ini penting (berisi `config.toml`).

---

## 2. Pasang Ekstensi VS Code (opsional tapi disarankan)

Buka panel **Extensions** (`Ctrl+Shift+X`) lalu pasang:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Even Better TOML** (opsional, untuk `.streamlit/config.toml`)

---

## 3. Buat Virtual Environment (venv) — Disarankan

Buka terminal VS Code: menu **Terminal → New Terminal** (`Ctrl+~`), lalu jalankan sesuai sistem operasi Anda.

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Jika muncul error *“running scripts is disabled”*, jalankan sekali:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Lalu ulangi perintah aktivasi. (Alternatif: pakai **Command Prompt** → `.venv\Scripts\activate.bat`)

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Tanda venv aktif: ada tulisan `(.venv)` di awal baris terminal.

> Di VS Code, setelah venv dibuat biasanya muncul notifikasi **“We noticed a new environment … Select it”** → klik **Yes**. Jika tidak, tekan `Ctrl+Shift+P` → **Python: Select Interpreter** → pilih `.venv`.

---

## 4. Pasang Dependensi

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Isi `requirements.txt` (9 paket): `streamlit`, `folium`, `streamlit-folium`, `streamlit-js-eval`, `requests`, `pandas`, `plotly`, `qrcode`, `pillow`.

Cek cepat apakah sudah terpasang:
```bash
pip list
```

---

## 5. Jalankan Aplikasi

```bash
streamlit run app.py
```
Jika perintah `streamlit` tidak dikenali, pakai cara yang selalu berhasil:
```bash
python -m streamlit run app.py
```

Terminal akan menampilkan:
```
  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

Browser biasanya terbuka otomatis. Jika tidak, buka manual: **<http://localhost:8501>**

### Menghentikan aplikasi
Tekan `Ctrl+C` di terminal VS Code.

### Menjalankan ulang tanpa menghentikan terminal
Cukup simpan file (`Ctrl+S`). Streamlit mendeteksi perubahan dan menampilkan tombol **“Rerun”** di kanan atas aplikasi.

---

## 6. Uji Fitur “Lokasi Saya (GPS)” di Laptop

Fitur GPS **hanya aktif di `localhost` atau HTTPS**. Karena Anda membuka `http://localhost:8501`, fitur ini boleh dipakai:

1. Scroll ke bagian **📍 Lokasi Saya Sekarang (Real-Time GPS)**.
2. Klik **“Aktifkan Lokasi Saya (GPS HP)”**.
3. Browser menampilkan izin lokasi → klik **Allow / Izinkan**.
4. Peta akan memusat ke posisi Anda, muncul pin biru **“Lokasi Anda”**, lingkaran radius 250 m, serta kartu **“KONDISI DI LOKASI ANDA SEKARANG”**.

**Jika izin lokasi ditolak atau GPS laptop tidak ada:** gunakan dropdown **“Belum bisa pakai GPS? Pilih dusun / titik lokal terdekat”** (10 titik di 5 dusun), lalu klik **“✅ Gunakan Titik Ini sebagai Lokasi Saya”**. Semua fitur analisis tetap berjalan.

> Menguji dengan lokasi Desa Pagentan padahal Anda di luar kota: di Chrome tekan `F12` → `Ctrl+Shift+P` → ketik **Sensors** → *Show Sensors* → **Location → Custom location** → isi `-7.2996` (latitude) dan `109.8062` (longitude) — koordinat Dusun Bulu, Desa Pagentan → refresh halaman.

---

## 7. Uji Semua Skenario di Panel Edukasi

Di bagian **Panel Uji & Edukasi Fungsi Peringatan Dini**, klik bergantian:
- `🟢 Live Real-Time (Open-Meteo)` — data asli hari ini.
- `🎓 Edukasi AMAN (<20 mm)` — banner hijau, peta dominan hijau.
- `🟡 Edukasi WASPADA (20–50 mm)` — banner kuning, 65 blok kuning.
- `🔴 Edukasi SIAGA (>50 mm)` — **banner merah berkedip**, 36 blok tebing/sungai merah, kentongan *titir*.
- `📴 Edukasi Mode Offline` — muncul pil *“Menampilkan estimasi offline”* (bukti anti-crash).

---

## 8. Mematikan Mode Pengembang / Mengubah Data Desa

Semua data mudah diedit langsung di VS Code:

| Ingin mengubah | File | Bagian |
|---|---|---|
| Nama titik lokal, koordinat pin, pos ronda | `gis_engine.py` | daftar `VITAL_LOCATIONS` |
| Alur sungai & garis tebing | `gis_engine.py` | `RIVER_PATH`, `NORTH_CLIFF_LINE` |
| Jalur evakuasi | `gis_engine.py` | `EVACUATION_ROUTES` |
| Batas wilayah desa (bounding box) | `gis_engine.py` | `LAT_NORTH/LAT_SOUTH/LON_WEST/LON_EAST` |
| Ambang bahaya 20 mm / 50 mm | `weather_ews.py` | fungsi `classify_landslide_risk` |
| Nomor darurat & URL QR Code | `app.py` | bagian **Saluran Darurat** & **Kartu QR Code** |
| Warna & font | `app.py` | fungsi `inject_custom_styles` |

Setelah mengedit, simpan (`Ctrl+S`) dan klik **Rerun**.

---

## 9. Masalah Umum & Solusinya

| Gejala | Penyebab | Solusi |
|---|---|---|
| `streamlit: command not found` | venv belum aktif / PATH | Pakai `python -m streamlit run app.py` |
| `ModuleNotFoundError: No module named 'streamlit_folium'` | Dependensi belum lengkap | Aktifkan venv lalu `pip install -r requirements.txt` |
| `Port 8501 is already in use` | Aplikasi lain masih jalan | `streamlit run app.py --server.port 8502` (lalu buka `localhost:8502`) |
| Peta kosong / abu-abu | Internet terputus (tile OpenStreetMap tidak termuat) | Cek koneksi; data hujan tetap tampil dari cache/offline |
| Muncul *“Menampilkan estimasi offline”* | API Open-Meteo tidak terjangkau | Normal — sistem tetap jalan. Klik **🔄 Segarkan Cuaca** saat online |
| Tombol GPS tidak memunculkan izin | Browser memblokir / bukan localhost | Buka via `http://localhost:8501` (bukan IP LAN), atau pakai dropdown manual |
| Komponen GPS tampak kosong sekejap | Komponen JS butuh 1–2 detik | Tunggu, atau klik tombol sekali lagi |
| Perubahan kode tidak muncul | Cache Streamlit | Tekan `R` → **Rerun**, atau `Ctrl+C` lalu jalankan ulang |

---

## 10. (Opsional) Deploy ke Internet agar Bisa Diakses Warga via QR Code

1. Unggah seluruh isi folder (termasuk `.streamlit/config.toml`) ke **repositori GitHub publik**.
2. Buka <https://share.streamlit.io> → **Create app** → pilih repo & branch `main`.
3. **Main file path**: `app.py` → **Advanced settings → URL**: `sipaldo-pagentan`.
4. Klik **Deploy**. Aplikasi online di `https://sipaldo-pagentan.streamlit.app` — URL ini sama dengan yang sudah tertanam di QR Code aplikasi.

---

## 11. Perintah Ringkas (Cheat Sheet)

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Selamat mencoba! 🌧️⛰️
