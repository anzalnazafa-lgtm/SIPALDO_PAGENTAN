# ⛰️ SIPALDO-PAGENTAN
**Sistem Peringatan Dini Longsor Desa Pagentan**  
*Desa Pagentan (Kode Kemendagri: 33.04.14.2012), Kecamatan Pagentan, Kabupaten Banjarnegara, Jawa Tengah*

Aplikasi WebGIS interaktif skala desa yang ringan, responsif di layar smartphone warga dan petugas Pos Ronda, **100% gratis tanpa API Key**, serta siap dideploy ke **Streamlit Community Cloud (`https://sipaldo-pagentan.streamlit.app`)** untuk diakses warga melalui **QR Code**.

---

## ✨ Fitur Utama
1. **Cakupan Penuh Seluruh Wilayah Desa Pagentan (5 Dusun, RW 01–08)**:
   - **Dusun Krajan 1 (RW 01–02)**: Balai Desa Pagentan, Puskesmas/Layanan Medis, Jalur Utama.
   - **Dusun Krajan 2 (RW 03–04)**: Posko Kebencanaan Desa, Lapangan Desa, Titik Pantau Drainase.
   - **Dusun Bulu (RW 05–06)**: Titik Pantau Lereng Tebing Utara & Pos Ronda Sektor Utara–Barat.
   - **Dusun Sawangan (RW 07)**: Titik Pantau Alur Sungai & Rawa Tebing serta Pos Ronda Sektor Selatan–Timur.
   - **Dusun Tedunan (RW 08)**: Titik Pantau Kelerengan Turunan & Tebing Timur.
2. **📍 Lokasi Saya Real-Time (GPS HP Warga)** — fitur inti bagi warga yang memindai QR Code:
   - Warga menekan **“Aktifkan Lokasi Saya (GPS HP)”**; browser meminta izin lokasi (bekerja di semua HP Android/iPhone, tanpa aplikasi tambahan).
   - Sistem langsung menampilkan: **nama dusun**, **karakter lereng & kemiringan** di titik warga, **situasi cuaca real-time di titik tersebut** (hujan 24 jam, akumulasi 3 hari, kejenuhan tanah, suhu, elevasi), **status bahaya di titik warga** (Relatif Aman / Perlu Dipantau / Bahaya Tinggi), **arahan evakuasi**, **titik aman terdekat beserta jaraknya (meter)**, dan **jarak ke Balai Desa**.
   - Peta otomatis memusat ke posisi warga: pin **“Lokasi Anda”**, lingkaran radius pantau ±250 m, serta garis jalur menuju titik aman terdekat.
   - **Alternatif tanpa GPS**: dropdown 10 titik lokal (5 dusun) untuk memilih lokasi secara manual.
   - **Privasi**: koordinat hanya dipakai di perangkat warga, tidak disimpan di server, dan bisa dimatikan kapan saja.
3. **Integrasi Cuaca Real-Time Open-Meteo (Gratis & Tanpa API Key)**:
   - Menembak langsung ke koordinat pusat Desa Pagentan (`-7.30583, 109.80944`) untuk menarik akumulasi curah hujan 24 jam, tren historis 3 hari terakhir, prakiraan 12 jam ke depan, serta kelembaban tanah (`3–9 cm`).
4. **Logika Analisis Longsor Dinamis Banjarnegara**:
   - **Aman (Hijau)** `< 20 mm`: Banner *"Kondisi Desa Aman"*, peta menampilkan zona risiko standar.
   - **Waspada (Kuning)** `20 – 50 mm` *(atau hujan konstan hari sebelumnya)*: Banner *"Waspada: Lereng Mulai Jenuh Air"*, sebagian grid peta naik menjadi kuning.
   - **Bahaya / Siaga (Merah)** `> 50 mm`: Aplikasi otomatis beralih ke **Mode Darurat** dengan **Banner Merah Menyala Berkedip** (*"SIAGA: Curah Hujan Tinggi di Pagentan! Hindari Area Tebing & Jalur Rawan!"*) dan blok tebing/sungai di peta menyala merah.
5. **Panel Edukasi & Simulasi Fungsi Aplikasi**:
   - Memudahkan warga, perangkat desa, dan petugas Pos Ronda mempelajari respons sistem untuk setiap skenario bahaya maupun gangguan jaringan.
6. **Anti-Crash Offline Fallback (`try-except`)**:
   - Otomatis memuat data estimasi terakhir disertai keterangan *"Menampilkan estimasi offline"* jika server API cuaca tidak merespons.
7. **Generator Kartu QR Code Warga**:
   - Menghasilkan gambar QR Code resolusi tinggi (`https://sipaldo-pagentan.streamlit.app`) siap unduh (PNG) dan cetak untuk ditempel di Balai Desa & Pos Ronda tiap dusun.

---

## 🚀 Cara Menjalankan secara Lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```
📘 Panduan langkah demi langkah untuk **VS Code** (Windows/macOS/Linux, termasuk pembuatan `venv`, uji GPS lokal, dan solusi error) tersedia di **[`PANDUAN_VSCODE.md`](PANDUAN_VSCODE.md)**.

## ☁️ Cara Deploy Gratis di Streamlit Sharing (Community Cloud)
1. Unggah seluruh isi folder ini (`app.py`, `gis_engine.py`, `weather_ews.py`, `charts_qr.py`, `requirements.txt`, `.streamlit/config.toml`) ke repositori GitHub publik Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io) lalu klik **Create app / New app**.
3. Pilih repositori GitHub Anda, branch `main`, isi **Main file path** dengan `app.py`, dan set **App URL** menjadi `sipaldo-pagentan.streamlit.app`.
4. Klik **Deploy!** — Aplikasi langsung online dan siap diakses warga via scan QR Code.
