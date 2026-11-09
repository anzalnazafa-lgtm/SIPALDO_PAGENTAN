# 🚀 CARA MENGISI BRANCH & MAIN FILE PATH DI STREAMLIT CLOUD

Repo Anda **`anzalnazafa-lgtm/SIPALDO_PAGENTAN`** masih **kosong** — itu sebabnya Streamlit menampilkan:

> ❌ *This branch does not exist*
> ❌ *This file does not exist*

Streamlit membaca **langsung dari GitHub**, bukan dari komputer Anda. Jadi file harus diunggah dulu. Pilih **salah satu** dari 3 cara di bawah, lalu kembali ke halaman *Deploy an app*.

---

## ✅ Setelah file terunggah, isi form seperti ini

| Kolom | Isi | Catatan |
|---|---|---|
| **Repository** | `anzalnazafa-lgtm/SIPALDO_PAGENTAN` | sudah benar (boleh juga `anzalnazafa-lgtm/SIPALDO_PAGENTAN/` diakhiri garis miring) |
| **Branch** | `main` | Harus sama persis dengan nama branch di GitHub. Jika repo dibuat lewat web GitHub, biasanya `main`. Jika dari komputer lama, mungkin `master`. |
| **Main file path** | `app.py` | **Hanya** `app.py` — tanpa awalan folder, tanpa `SIPALDO-PAGENTAN/app.py`, tanpa tanda `/`. |
| **App URL (optional)** | `sipaldo-pagentan` | Maka alamatnya menjadi `https://sipaldo-pagentan.streamlit.app` — **sama dengan URL yang tertanam di QR Code aplikasi**. |

> ⚠️ **Penting:** di dalam repo, `app.py` harus berada di **folder paling atas** (root), sejajar dengan `requirements.txt`.

---

## CARA 1 — Lewat web GitHub (paling mudah, tanpa install apa pun)

1. Unduh `SIPALDO-PAGENTAN.zip` dari workspace, lalu **ekstrak**.
2. Buka <https://github.com/anzalnazafa-lgtm/SIPALDO_PAGENTAN>.
3. Karena repo masih kosong, klik tautan **“uploading an existing file”** (atau tombol **Add file → Upload files**).
4. Buka folder hasil ekstrak, lalu **seret seluruh isi folder** ke halaman GitHub:
   - `app.py`
   - `gis_engine.py`
   - `weather_ews.py`
   - `charts_qr.py`
   - `requirements.txt`
   - `README.md`
   - `PANDUAN_VSCODE.md`
   - `CARA_UPLOAD_GITHUB.md`
   - folder **`.streamlit`** (berisi `config.toml`)
   > Jangan menyeret folder induk `SIPALDO-PAGENTAN`-nya — yang diunggah adalah **isi** folder tersebut.
   > Folder `.streamlit` tidak terlihat di Windows Explorer? Aktifkan **View → Show → Hidden items**.
5. Pada kotak **Commit changes**, ketik misalnya `Upload SIPALDO-PAGENTAN`, lalu klik **Commit changes**.
6. Pastikan halaman repo kini menampilkan daftar file dengan **`app.py` di baris paling atas**.
7. Kembali ke <https://share.streamlit.io> → isi form seperti tabel di atas → **Deploy**.

---

## CARA 2 — Lewat VS Code (disarankan bila Anda sudah memakai VS Code)

Buka folder proyek di VS Code, buka terminal (`Ctrl+~`), lalu jalankan:

```bash
git init
git add .
git commit -m "Initial commit SIPALDO-PAGENTAN"
git branch -M main
git remote add origin https://github.com/anzalnazafa-lgtm/SIPALDO_PAGENTAN.git
git push -u origin main
```

Jika diminta login, gunakan **Personal Access Token** GitHub sebagai password:

1. GitHub → foto profil → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**.
2. Centang scope **`repo`** → **Generate** → salin token (`ghp_...`).
3. Saat terminal meminta *Password*, tempel token tersebut (karakter tidak akan terlihat — itu normal), lalu `Enter`.

Verifikasi: buka repo di browser, `app.py` harus terlihat.

> Jika muncul error `remote origin already exists`, jalankan dulu:
> `git remote set-url origin https://github.com/anzalnazafa-lgtm/SIPALDO_PAGENTAN.git`

---

## CARA 3 — Lewat GitHub Desktop (paling ramah untuk pemula)

1. Unduh & pasang <https://desktop.github.com> → login akun GitHub Anda.
2. **File → Add local repository…** → pilih folder proyek `SIPALDO-PAGENTAN` → **Add**.
   (Jika ditanya *“create a repository?”* → klik **create a repository**, lalu **Publish repository**.)
3. Isi kolom **Summary** (mis. `Upload SIPALDO-PAGENTAN`) → klik **Commit to main**.
4. Klik **Publish repository** / **Push origin**.
5. **Pastikan “Keep this code private” TIDAK dicentang** — Streamlit Cloud gratis hanya bisa membaca repo **publik**.

---

## 🔍 Cara memastikan Branch & PATH benar

Setelah unggah, buka repo di GitHub dan perhatikan:

- **Branch**: lihat dropdown di kiri atas daftar file — tulisannya harus `main` (atau `master`). **Itu yang Anda isi di kolom Branch.**
- **Main file path**: `app.py` harus terlihat langsung di halaman utama repo (bukan di dalam subfolder).
  Jika di repo Anda file berada di dalam folder, misalnya `SIPALDO-PAGENTAN/app.py`,
  maka kolom **Main file path** diisi **`SIPALDO-PAGENTAN/app.py`** — tetapi cara ini **tidak disarankan**;
  lebih baik pindahkan file ke root (GitHub: buka file → ikon pensil → ubah nama dengan menghapus `SIPALDO-PAGENTAN/` di depan).

Contoh struktur repo yang **benar**:

```
SIPALDO_PAGENTAN/            ← repo GitHub
├── .streamlit/
│   └── config.toml
├── app.py                   ← main file path: app.py
├── charts_qr.py
├── gis_engine.py
├── weather_ews.py
├── requirements.txt
├── README.md
├── PANDUAN_VSCODE.md
└── CARA_UPLOAD_GITHUB.md
```

---

## ⚠️ 6 Kesalahan yang Paling Sering Terjadi

| Gejala | Penyebab | Perbaikan |
|---|---|---|
| *This branch does not exist* | Repo masih kosong / branch beda nama | Unggah file dulu; cek nama branch (`main` vs `master`) |
| *This file does not exist* | `app.py` tidak ada di root, atau salah tulis | Isi cukup `app.py`; pastikan file ada di halaman utama repo |
| Deploy gagal: *repository not found* | Repo **private** | Settings repo → **Change visibility → Public** |
| App error saat start | `requirements.txt` tidak terunggah | Unggah `requirements.txt` di root |
| Tema/warna tidak muncul | folder `.streamlit` tidak terunggah | Unggah `.streamlit/config.toml` (aktifkan *show hidden files*) |
| URL `sipaldo-pagentan.streamlit.app` tidak bisa dipakai | Sudah dipakai akun lain | Pakai `sipaldo-pagentan-banjarnegara`, lalu ubah URL di aplikasi (kolom **Alamat URL Publik** pada bagian QR Code) |

---

## 📝 Setelah aplikasi online

1. Tunggu proses *“Your app is in the oven”* selesai (±2–5 menit).
2. Buka aplikasi → scroll ke bagian **📱 Kartu QR Code Akses Warga** → ubah kolom **Alamat URL Publik** sesuai URL final Anda → klik **⬇️ Unduh Gambar QR Code Siap Cetak (PNG)**.
3. Cetak QR tersebut untuk ditempel di Balai Desa Pagentan dan 5 Pos Ronda dusun.

> Fitur **📍 Lokasi Saya (GPS HP)** hanya aktif pada alamat **HTTPS** — dan Streamlit Cloud sudah otomatis HTTPS, jadi fitur ini langsung berfungsi di HP warga.
