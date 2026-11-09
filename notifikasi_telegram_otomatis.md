# 🤖 PANDUAN NOTIFIKASI TELEGRAM OTOMATIS

Tujuan: warga & petugas **menerima peringatan tanpa harus membuka aplikasi**.

Ada 2 tingkat:

| Tingkat | Cara | Biaya | Keterangan |
|---|---|---|---|
| **A. Kirim manual dari aplikasi** | Tombol **🚀 Kirim Ringkasan Status ke Telegram** di bagian *Log Patroli & Notifikasi Otomatis* | Rp0 | Sudah tersedia. Cocok untuk laporan harian petugas jaga. |
| **B. Otomatis setiap pagi & sore + peringatan seketika** | GitHub Actions (gratis 2.000 menit/bulan) | Rp0 | Tanpa server tambahan, jalan 24 jam. Panduan di bawah. |

---

## A. Kirim manual (paling cepat, 5 menit)

1. Buka Telegram → cari **@BotFather** → kirim `/newbot` → beri nama (mis. `SipaldoPagentanBot`)
   → BotFather memberi **token** seperti `123456789:AAH...`.
2. Buat **grup WhatsApp/Telegram desa** di Telegram (mis. "Siaga Desa Pagentan") → tambahkan bot sebagai anggota.
3. Kirim satu pesan apa pun di grup, lalu buka di browser:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   Cari bagian `"chat":{"id":-1001234567890, ...}` → salin angka negatif itu.
4. Buka aplikasi SIPALDO-PAGENTAN → bagian **Log Patroli & Notifikasi Otomatis** →
   tempel **Token** dan **Chat ID** → klik **🚀 Kirim Ringkasan Status**.

> Token hanya dipakai di sesi browser Anda dan tidak disimpan di server aplikasi.

---

## B. Otomatis setiap hari (GitHub Actions)

### Langkah 1 — Simpan token sebagai *Repository Secret*

1. Buka repo GitHub → **Settings → Secrets and variables → Actions → New repository secret**.
2. Buat dua secret:
   - `TELEGRAM_TOKEN` = token dari BotFather
   - `TELEGRAM_CHAT_ID` = chat id grup (angka negatif)

### Langkah 2 — Tambahkan berkas workflow

Buat berkas **`.github/workflows/notifikasi-pagentan.yml`** di repo Anda:

```yaml
name: Notifikasi Harian SIPALDO-PAGENTAN

on:
  schedule:
    - cron: "0 22 * * *"   # 05.00 WIB (22.00 UTC) — ringkasan pagi
    - cron: "0 9 * * *"    # 16.00 WIB (09.00 UTC) — ringkasan sore
  workflow_dispatch:        # tombol "Run workflow" untuk uji manual

jobs:
  kirim:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests pandas
      - name: Kirim ringkasan status
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python notifikasi_harian.py
```

### Langkah 3 — Berkas `notifikasi_harian.py`

Berkas ini **sudah disertakan** dalam paket ZIP. Isinya mengambil data Open-Meteo untuk
Balai Desa Pagentan, mengklasifikasi risiko, lalu mengirim pesan ke Telegram.
Uji manual: GitHub → tab **Actions** → pilih workflow → **Run workflow**.

### Langkah 4 (opsional) — Peringatan seketika

Jika ingin peringatan tiap 30 menit ketika status **SIAGA**, ubah bagian `on.schedule` menjadi:

```yaml
on:
  schedule:
    - cron: "*/30 * * * *"
```

Tambahkan di `notifikasi_harian.py`:

```python
# kirim hanya bila status berubah atau status SIAGA
if risk["level"] == "SIAGA" or status_berbeda_dari_terakhir:
    kirim_telegram(TOKEN, CHAT_ID, pesan)
```

> Tips: gunakan `state.json` (disimpan lewat `actions/cache` atau commit balik) untuk mengingat
> status terakhir agar grup tidak dibanjiri pesan berulang.

---

## C. Kalau ingin peringatan lewat WhatsApp

WhatsApp **tidak menyediakan API gratis** untuk pengiriman otomatis. Pilihan realistis:

1. **Manual (gratis, disarankan):** gunakan kotak **“Teks laporan siap kirim ke grup WhatsApp desa”**
   di aplikasi → salin → tempel ke grup. Sudah diformat rapi.
2. **Gratis via pihak ketiga:** layanan seperti CallMeBot (butuh verifikasi sekali) atau
   WhatsApp Cloud API (berbayar per percakapan).
3. **Kombinasi yang paling hemat:** bot Telegram untuk peringatan otomatis + broadcast WhatsApp
   manual 1x sehari oleh petugas jaga.

---

## D. Etika & keamanan pengiriman pesan

- Kirim ringkasan **maksimal 2–3 kali sehari** agar grup tidak jenuh.
- Untuk status **SIAGA**, kirim **segera** (jangan menunggu jadwal).
- Selalu sertakan: status, hujan 24 jam, proyeksi 12 jam, dan **tindakan yang harus dilakukan**.
- Jangan pernah menuliskan nomor pribadi warga di grup; gunakan daftar petugas RT/RW.
- Rotasi token bot setiap 6 bulan (BotFather → `/revoke`).
