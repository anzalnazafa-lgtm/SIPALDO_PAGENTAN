"""
Modul fitur lanjutan SIPALDO-PAGENTAN:

1. ANTISIPASI 6–12 JAM  → indikator "leading" memakai akumulasi hujan yang sudah turun
   ditambah prakiraan hujan 12 jam ke depan (Open-Meteo), lengkap dengan hitung mundur
   perkiraan jam ambang 50 mm akan terlampaui.
2. LOG PATROLI POS RONDA → pencatatan hasil ronda per dusun (aman / gejala ringan /
   gejala berat), rekap grafik, unduh CSV, dan format pesan WhatsApp untuk dilaporkan.
3. NOTIFIKASI TELEGRAM   → ringkasan harian otomatis + peringatan seketika bila status
   berubah menjadi WASPADA atau SIAGA. Berjalan tanpa server tambahan.

Semua fungsi di sini murni Python (tanpa state global) agar mudah diuji.
Penyimpanan log memakai st.session_state + berkas JSON lokal di direktori aplikasi.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import json

import pandas as pd
import requests

from weather_ews import TZ_WIB

# -----------------------------------------------------------------------------
# 1. ANTISIPASI 6–12 JAM (LEADING INDICATOR)
# -----------------------------------------------------------------------------
AMBANG_WASPADA = 20.0
AMBANG_SIAGA = 50.0


def _jam_label(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def analisis_antisipasi(weather: dict) -> dict:
    """
    Memperkirakan apakah desa akan mencapai ambang SIAGA (50 mm) dalam 6–12 jam ke depan.

    Dasar perhitungan:
      • `hujan_awal`      = akumulasi curah hujan 24 jam terakhir (sudah turun) → membasahi lereng
      • `prakiraan_12j`   = total prakiraan hujan 12 jam ke depan
      • `proyeksi`        = hujan_awal + prakiraan_12j

    Bila proyeksi > 50 mm → status "ANTISIPASI SIAGA" (banner kuning-oranye, bukan merah,
    karena belum terjadi). Waktu kedatangan dihitung dari akumulasi prakiraan per jam.
    """
    hujan_awal = float(weather.get("rain_24h") or 0.0)
    prakiraan = float(weather.get("rain_forecast_12h") or 0.0)
    proyeksi = round(hujan_awal + prakiraan, 1)

    sekarang = datetime.now(TZ_WIB).replace(tzinfo=None)
    per_jam = weather.get("forecast_12h_df")
    kumulatif = 0.0
    jam_capai = None
    if isinstance(per_jam, pd.DataFrame) and not per_jam.empty and "prakiraan_mm" in per_jam:
        for idx, nilai in enumerate(per_jam["prakiraan_mm"].fillna(0.0).tolist()):
            kumulatif += float(nilai)
            if hujan_awal + kumulatif >= AMBANG_SIAGA:
                jam_capai = sekarang + timedelta(hours=idx + 1)
                break

    if proyeksi >= AMBANG_SIAGA:
        level = "ANTISIPASI_SIAGA"
        judul = "ANTISIPASI SIAGA DALAM BEBERAPA JAM KE DEPAN"
        warna = "#EA580C"
        if jam_capai:
            sisa_jam = max((jam_capai - sekarang).total_seconds() / 3600.0, 0.5)
            pesan = (
                f"Hujan 24 jam sekarang {hujan_awal:.1f} mm, prakiraan 12 jam ke depan "
                f"{prakiraan:.1f} mm. Proyeksi mencapai ambang SIAGA (50 mm) sekitar "
                f"pukul {_jam_label(jam_capai)} WIB (±{sisa_jam:.0f} jam lagi). "
                "Siapkan evakuasi mandiri & tas siaga keluarga sekarang."
            )
        else:
            pesan = (
                f"Hujan 24 jam sekarang {hujan_awal:.1f} mm + prakiraan 12 jam ke depan "
                f"{prakiraan:.1f} mm = proyeksi {proyeksi:.1f} mm (>50 mm). Siapkan evakuasi mandiri."
            )
        arahan = (
            "Mulai sekarang: siapkan dokumen & obat, amankan hewan ternak, "
            "tentukan jalur ke Balai Desa / Lapangan Rawa Sakti, dan bunyikan kentongan 3x "
            "(tanda waspada) agar warga bersiap."
        )
    elif proyeksi >= AMBANG_WASPADA:
        level = "ANTISIPASI_WASPADA"
        judul = "POTENSI JENUH AIR (WASPADA) DALAM 12 JAM"
        warna = "#CA8A04"
        pesan = (
            f"Hujan 24 jam {hujan_awal:.1f} mm + prakiraan 12 jam {prakiraan:.1f} mm "
            f"= proyeksi {proyeksi:.1f} mm (ambang Waspada 20 mm). Lereng mulai jenuh air."
        )
        arahan = (
            "Periksa saluran air rumah & kebun, catat bila ada retakan baru di lereng, "
            "dan pastikan jalur evakuasi tidak tertutup material."
        )
    else:
        level = "AMAN_TERKENDALI"
        judul = "TIDAK ADA POTENSI HUJAN EKSTREM 12 JAM KE DEPAN"
        warna = "#15803D"
        pesan = (
            f"Hujan 24 jam {hujan_awal:.1f} mm + prakiraan 12 jam {prakiraan:.1f} mm "
            f"= proyeksi {proyeksi:.1f} mm (masih di bawah ambang Waspada 20 mm)."
        )
        arahan = "Kondisi terkendali. Tetap jalankan ronda rutin sesuai jadwal RT/RW."

    return {
        "level": level,
        "judul": judul,
        "warna": warna,
        "pesan": pesan,
        "arahan": arahan,
        "hujan_awal": round(hujan_awal, 1),
        "prakiraan_12j": round(prakiraan, 1),
        "proyeksi": proyeksi,
        "jam_capai": _jam_label(jam_capai) if jam_capai else None,
        "ambang_siaga": AMBANG_SIAGA,
        "ambang_waspada": AMBANG_WASPADA,
    }


# -----------------------------------------------------------------------------
# 2. LOG PATROLI POS RONDA
# -----------------------------------------------------------------------------
LOKASI_LOG = Path(__file__).parent / "log_patroli_pagentan.json"

KONDISI_PATROLI = {
    "AMAN": {
        "label": "Aman — tidak ada gejala",
        "bobot": 0,
        "warna": "#15803D",
        "pesan_wa": "kondisi aman, tidak ditemukan gejala longsor.",
    },
    "GEJALA_RINGAN": {
        "label": "Ada gejala ringan (rembesan / retakan kecil)",
        "bobot": 1,
        "warna": "#CA8A04",
        "pesan_wa": "ditemukan gejala ringan (rembesan/retakan kecil), perlu pemantauan.",
    },
    "GEJALA_BERAT": {
        "label": "Gejala berat (retakan membesar / suara gemuruh)",
        "bobot": 2,
        "warna": "#DC2626",
        "pesan_wa": "ditemukan gejala berat (retakan membesar/gemuruh) — mohon tindak lanjut segera.",
    },
}

# Slug pendek untuk URL QR per Pos Ronda (?pos=bulu)
DUSUN_SLUG = {
    "Dusun Krajan 1 (RW 01–02)": "krajan1",
    "Dusun Krajan 2 (RW 03–04)": "krajan2",
    "Dusun Bulu (RW 05–06)": "bulu",
    "Dusun Sawangan (RW 07)": "sawangan",
    "Dusun Tedunan (RW 08)": "tedunan",
}


def resolve_dusun_slug(param: str) -> str | None:
    """Ubah parameter URL (?pos=bulu / ?pos=Krajan 1) menjadi nama dusun resmi."""
    p = (param or "").strip().lower().replace(" ", "")
    if not p:
        return None
    for dusun, slug in DUSUN_SLUG.items():
        if p == slug or p in dusun.lower().replace(" ", ""):
            return dusun
    return None


DUSUN_POS = [
    "Dusun Krajan 1 (RW 01–02)",
    "Dusun Krajan 2 (RW 03–04)",
    "Dusun Bulu (RW 05–06)",
    "Dusun Sawangan (RW 07)",
    "Dusun Tedunan (RW 08)",
]


def muat_log() -> list[dict]:
    """Muat log patroli dari berkas JSON lokal (kosong bila belum ada / rusak)."""
    try:
        if LOKASI_LOG.exists():
            data = json.loads(LOKASI_LOG.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def simpan_log(entri: list[dict]) -> bool:
    """Simpan log patroli ke berkas JSON lokal. False bila gagal (mis. izin tulis)."""
    try:
        LOKASI_LOG.write_text(
            json.dumps(entri[-500:], ensure_ascii=False, indent=1), encoding="utf-8"
        )
        return True
    except Exception:
        return False


def tambah_entri_log(
    entri: list[dict],
    dusun: str,
    kondisi: str,
    petugas: str,
    catatan: str = "",
    cuaca: dict | None = None,
) -> list[dict]:
    """Tambahkan satu entri patroli (waktu WIB otomatis)."""
    now = datetime.now(TZ_WIB).replace(tzinfo=None)
    baru = {
        "waktu": now.strftime("%Y-%m-%d %H:%M"),
        "dusun": dusun,
        "kondisi": kondisi,
        "label_kondisi": KONDISI_PATROLI.get(kondisi, {}).get("label", kondisi),
        "petugas": petugas.strip() or "Petugas Ronda",
        "catatan": catatan.strip(),
        "hujan_24h": round(float((cuaca or {}).get("rain_24h") or 0.0), 1),
        "status_desa": (cuaca or {}).get("_status", ""),
    }
    return entri + [baru]


def rekap_log(entri: list[dict]) -> pd.DataFrame:
    """Rekap jumlah laporan patroli per dusun dan per kondisi."""
    if not entri:
        return pd.DataFrame(columns=["Dusun", "Aman", "Gejala Ringan", "Gejala Berat", "Total"])
    df = pd.DataFrame(entri)
    rows = []
    for dusun in DUSUN_POS:
        sub = df[df["dusun"] == dusun]
        rows.append(
            {
                "Dusun": dusun,
                "Aman": int((sub["kondisi"] == "AMAN").sum()),
                "Gejala Ringan": int((sub["kondisi"] == "GEJALA_RINGAN").sum()),
                "Gejala Berat": int((sub["kondisi"] == "GEJALA_BERAT").sum()),
                "Total": int(len(sub)),
            }
        )
    return pd.DataFrame(rows)


def log_ke_csv(entri: list[dict]) -> bytes:
    """Ekspor log patroli sebagai CSV (siap dibuka di Excel)."""
    if not entri:
        entri = []
    df = pd.DataFrame(entri)
    if df.empty:
        df = pd.DataFrame(
            columns=[
                "waktu", "dusun", "kondisi", "label_kondisi",
                "petugas", "catatan", "hujan_24h", "status_desa",
            ]
        )
    return df.to_csv(index=False).encode("utf-8-sig")


def pesan_wa_patroli(entri_terakhir: dict, cuaca: dict, antisipasi: dict) -> str:
    """Susun teks laporan patroli siap tempel ke WhatsApp grup desa."""
    k = KONDISI_PATROLI.get(entri_terakhir.get("kondisi"), {})
    return (
        f"*LAPORAN PATROLI SIPALDO-PAGENTAN*\n"
        f"Pos Ronda: {entri_terakhir.get('dusun', '-')}\n"
        f"Waktu: {entri_terakhir.get('waktu', '-')} WIB\n"
        f"Petugas: {entri_terakhir.get('petugas', '-')}\n"
        f"Hasil: {k.get('label', '-')}\n"
        f"Catatan: {entri_terakhir.get('catatan') or '-'}\n"
        f"\n*Kondisi Cuaca Desa*\n"
        f"Hujan 24 jam: {cuaca.get('rain_24h', 0):.1f} mm | "
        f"Akumulasi 3 hari: {cuaca.get('rain_3d_total', 0):.1f} mm\n"
        f"Status desa: {entri_terakhir.get('status_desa') or '-'}\n"
        f"Proyeksi 12 jam: {antisipasi.get('proyeksi', 0):.1f} mm "
        f"({antisipasi.get('judul', '-')})\n"
        f"\nMohon diteruskan ke Kepala Dusun & Posko Desa."
    )


# -----------------------------------------------------------------------------
# 3. NOTIFIKASI TELEGRAM
# -----------------------------------------------------------------------------
def telegram_terkonfigurasi(token: str | None, chat_id: str | None) -> bool:
    """True bila token bot & chat id sudah diisi."""
    return bool((token or "").strip()) and bool((chat_id or "").strip())


def kirim_telegram(token: str, chat_id: str, pesan: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Kirim pesan teks ke Telegram via Bot API.
    Mengembalikan (berhasil, keterangan) — tidak pernah melempar exception.
    """
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token.strip()}/sendMessage",
            data={
                "chat_id": chat_id.strip(),
                "text": pesan,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=timeout,
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            return True, "Terkirim"
        return False, f"HTTP {resp.status_code}: {resp.text[:160]}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)[:160]


def susun_pesan_status(
    weather: dict,
    risk: dict,
    antisipasi: dict,
    label_desa: str = "Desa Pagentan",
) -> str:
    """Susun pesan ringkasan status siap kirim ke Telegram (format Markdown)."""
    ikon = {"SIAGA": "🚨", "WASPADA": "⚠️", "AMAN": "✅"}.get(risk.get("level"), "ℹ️")
    return (
        f"{ikon} *SIPALDO-PAGENTAN — {label_desa}*\n"
        f"*Status: {risk.get('label_ui', '-')}*\n"
        f"Hujan 24 jam: *{weather.get('rain_24h', 0):.1f} mm* "
        f"(Siaga >50 | Waspada 20–50)\n"
        f"Akumulasi 3 hari: {weather.get('rain_3d_total', 0):.1f} mm\n"
        f"Kejenuhan tanah 3–9 cm: {weather.get('soil_moisture_pct', 0):.1f}%\n"
        f"Cuaca: {weather.get('weather_desc', '-')} {weather.get('temperature_c', 0):.1f} °C\n\n"
        f"*Antisipasi 12 jam:* {antisipasi.get('judul', '-')}\n"
        f"Proyeksi: {antisipasi.get('proyeksi', 0):.1f} mm"
        + (f" (capai 50 mm ± pukul {antisipasi['jam_capai']} WIB)" if antisipasi.get("jam_capai") else "")
        + f"\n\n{risk.get('citizen_action', '')}\n"
        f"Pembaruan: {weather.get('updated_at', '-')}\n"
        f"Peta & QR: https://sipaldo-pagentan.streamlit.app"
    )
