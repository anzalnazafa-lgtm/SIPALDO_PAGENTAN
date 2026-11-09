# 🔄 CARA MEMPERBARUI APLIKASI TANPA MENGULANG DARI AWAL

Setelah aplikasi berhasil di-deploy di Streamlit Cloud, Anda **tidak perlu** mengunggah ulang seluruh proyek.
Streamlit Cloud memantau repository GitHub Anda: **setiap kali ada commit baru, aplikasi otomatis dibangun ulang**.

Ada 3 cara, dari yang paling mudah:

---

## ⭐ CARA 0 (PALING PRAKTIS) — Edit langsung di GitHub, tanpa install apa pun

Cocok untuk perubahan kecil seperti **mengubah koordinat titik, nomor darurat, atau teks**.

1. Buka repo: `https://github.com/anzalnazafa-lgtm/SIPALDO_PAGENTAN`
2. Klik berkas yang ingin diubah, misalnya **`lokasi_desa.py`**.
3. Klik ikon **pensil (✏️ Edit this file)** di kanan atas.
4. Ubah angkanya, contoh:

   ```python
   {
       "name": "Balai Desa Pagentan",
       "coords": [-7.300433, 109.809946],     # ← ganti angka di sini
   ```

5. Scroll ke bawah → isi kotak **Commit changes** (mis. `koreksi koordinat balai desa`) →
   pastikan opsi **“Commit directly to the main branch”** terpilih → klik **Commit changes**.
6. Tunggu 30–90 detik. Buka aplikasi Streamlit Anda → klik **⋮ → Reboot app** (atau tunggu otomatis).
   Perubahan sudah aktif untuk semua warga. **Tidak ada upload ulang, tidak ada repo baru.**

> Tips: untuk menambah titik baru, **duplikat satu blok** `{ ... },` yang sudah ada, lalu ubah
> `name`, `coords`, `color`, dan `icon`. Jangan lupa koma di akhir blok.

---

## ⭐ CARA 1 — Upload file yang berubah saja (GitHub web)

Jika Anda mengedit di komputer/VS Code lalu ingin mengunggah **hanya 1–2 berkas**:

1. Buka repo → tombol **Add file → Upload files**.
2. Seret **hanya berkas yang berubah** (mis. `lokasi_desa.py`). Nama yang sama akan **menimpa** versi lama.
3. Isi pesan commit → **Commit changes**.
4. Streamlit Cloud otomatis rebuild.

---

## ⭐ CARA 2 — VS Code + Git (untuk perubahan rutin & banyak file)

Sekali setup, selanjutnya cukup 3 perintah:

```bash
git add .
git commit -m "update koordinat & data desa"
git push
```

Streamlit Cloud langsung mendeteksi commit dan memperbarui aplikasi.

Jika ini pertama kalinya di folder tersebut:
```bash
git clone https://github.com/anzalnazafa-lgtm/SIPALDO_PAGENTAN.git
# salin file proyek ke folder hasil clone, lalu:
git add .
git commit -m "update SIPALDO-PAGENTAN"
git push
```

---

## 🧭 Berkas mana yang harus diubah untuk kebutuhan tertentu?

| Ingin mengubah | Berkas | Bagian yang diedit |
|---|---|---|
| **Koordinat / nama titik** (Balai Desa, sekolah, masjid, dll.) | `lokasi_desa.py` | daftar `TITIK_LOKAL` |
| **Pusat desa** (titik awal peta & basis data cuaca) | `lokasi_desa.py` + `weather_ews.py` | `PUSAT_DESA` dan `PAGENTAN_LAT/PAGENTAN_LON` |
| **Batas wilayah grid (bounding box)** | `lokasi_desa.py` | `LAT_NORTH / LAT_SOUTH / LON_WEST / LON_EAST` |
| **Garis sungai / garis tebing / jalur evakuasi** | `gis_engine.py` | `RIVER_PATH`, `NORTH_CLIFF_LINE`, `EVACUATION_ROUTES` |
| **Ambang bahaya 20 mm & 50 mm** | `weather_ews.py` | fungsi `classify_landslide_risk` |
| **Nomor darurat (112 / BPBD / 119)** | `app.py` | bagian **Saluran Darurat Resmi** |
| **URL pada QR Code** | `app.py` | bagian **Kartu QR Code** (bisa juga diubah langsung di aplikasi, tanpa edit kode) |
| **Warna & tampilan** | `app.py` | fungsi `inject_custom_styles` |

---

## 🔁 Setelah commit: cara memaksa aplikasi memuat versi terbaru

Bila perubahan belum terlihat dalam 2 menit:

1. Buka **<https://share.streamlit.io>** → pilih aplikasi Anda.
2. Klik **⋮ (titik tiga)** di kanan atas → **Reboot app** / **Clear cache**.
3. Muat ulang halaman aplikasi di browser HP (`Ctrl+Shift+R` / tarik ke bawah untuk refresh).

Cek juga tab **Logs** di dashboard Streamlit untuk memastikan tidak ada error saat rebuild.

---

## ⚠️ Yang TIDAK perlu Anda lakukan

- ❌ Membuat repository baru
- ❌ Menghapus lalu membuat aplikasi baru di Streamlit Cloud
- ❌ Mengunggah ulang semua file setiap kali ada perubahan kecil
- ❌ Mengubah nama `app.py` (kalau diubah, sesuaikan **Main file path** di dashboard)

---

## 💡 Cara mengubah URL QR Code tanpa menyentuh kode

Buka aplikasi → scroll ke **📱 Kartu QR Code Akses Warga** → ubah kolom
**“Alamat URL Publik Aplikasi”** → klik **⬇️ Unduh Gambar QR Code Siap Cetak (PNG)**.
QR baru langsung siap dicetak; kode tidak perlu diubah sama sekali.
