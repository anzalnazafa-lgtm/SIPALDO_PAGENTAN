"""
TAMPILAN MUDAH UNTUK LANSIA (Mode Sederhana) — SIPALDO-PAGENTAN.

Prinsip desain:
  • 1 layar = 1 jawaban: "sekarang aman atau tidak?"
  • Huruf sangat besar (hingga ±2,4x ukuran normal), kontras tinggi.
  • Kalimat pendek: maksimal ±8 kata per baris.
  • Hanya 3 angka penting, tanpa istilah teknis
    ("curah hujan" → "hujan", "kejenuhan tanah" → "tanah basah").
  • Hanya 3 langkah tindakan, memakai ikon.
  • Satu tombol besar: Telepon 112.
  • Semua grafik, tabel, log, dan menu disembunyikan.
"""

from __future__ import annotations

import streamlit as st

# Kalimat pendek per tingkat status (dibuat khusus untuk lansia)
TEKS_STATUS = {
    "AMAN": {
        "judul": "AMAN",
        "emoji": "😊",
        "warna": "#15803D",
        "latar": "#F0FDF4",
        "garis": "#86EFAC",
        "kalimat": "Desa Pagentan aman hari ini.",
        "langkah": [
            ("🚶", "Boleh beraktivitas seperti biasa."),
            ("🧹", "Bersihkan selokan di depan rumah."),
            ("🌧️", "Kalau hujan turun, jangan ke tebing."),
        ],
    },
    "WASPADA": {
        "judul": "HATI-HATI",
        "emoji": "⚠️",
        "warna": "#B45309",
        "latar": "#FFFBEB",
        "garis": "#FCD34D",
        "kalimat": "Tanah mulai basah. Hati-hati.",
        "langkah": [
            ("🎒", "Siapkan tas: obat, KTP, senter."),
            ("🚫", "Jangan dekat tebing dan sungai."),
            ("👂", "Dengar kentongan dari Pos Ronda."),
        ],
    },
    "SIAGA": {
        "judul": "BAHAYA",
        "emoji": "🚨",
        "warna": "#B91C1C",
        "latar": "#FEF2F2",
        "garis": "#FCA5A5",
        "kalimat": "Segera mengungsi sekarang.",
        "langkah": [
            ("🏃", "Pergi ke Balai Desa atau Lapangan."),
            ("🎒", "Bawa obat dan dokumen saja."),
            ("📞", "Minta bantuan: telepon 112."),
        ],
    },
}


def _css_lansia() -> str:
    return """
<style>
/* ==== MODE LANSIA: huruf besar & tombol lebar ==== */
.lansia-wrap { max-width: 760px; margin: 0 auto; }
.lansia-status {
    border-radius: 22px;
    padding: 26px 20px 22px 20px;
    text-align: center;
    border: 5px solid;
    margin-bottom: 18px;
}
.lansia-emoji { font-size: 72px; line-height: 1; }
.lansia-judul {
    font-size: clamp(2.6rem, 11vw, 4.2rem);
    font-weight: 900;
    letter-spacing: 2px;
    line-height: 1.05;
    margin: 6px 0 8px 0;
}
.lansia-kalimat {
    font-size: clamp(1.35rem, 5.4vw, 1.85rem);
    font-weight: 700;
    line-height: 1.35;
    color: #0F172A;
}
.lansia-angka {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}
.lansia-angka > div {
    flex: 1;
    background: #FFFFFF;
    border: 3px solid #CBD5E1;
    border-radius: 18px;
    padding: 14px 8px;
    text-align: center;
}
.lansia-angka .label {
    font-size: clamp(0.95rem, 3.6vw, 1.1rem);
    font-weight: 700;
    color: #475569;
    line-height: 1.25;
}
.lansia-angka .nilai {
    font-size: clamp(1.7rem, 7.5vw, 2.5rem);
    font-weight: 900;
    color: #0F172A;
    line-height: 1.15;
}
.lansia-langkah {
    background: #FFFFFF;
    border: 3px solid #CBD5E1;
    border-radius: 18px;
    padding: 8px 16px;
    margin-bottom: 16px;
}
.lansia-langkah .baris {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 2px dashed #E2E8F0;
    font-size: clamp(1.2rem, 4.8vw, 1.55rem);
    font-weight: 700;
    color: #0F172A;
    line-height: 1.3;
}
.lansia-langkah .baris:last-child { border-bottom: none; }
.lansia-langkah .ikon { font-size: 2rem; line-height: 1; }
.lansia-tombol {
    display: block;
    width: 100%;
    text-align: center;
    text-decoration: none !important;
    background: #B91C1C;
    color: #FFFFFF !important;
    font-size: clamp(1.3rem, 5.2vw, 1.7rem);
    font-weight: 900;
    padding: 20px 12px;
    border-radius: 18px;
    margin-bottom: 12px;
    box-shadow: 0 6px 16px rgba(185, 28, 28, 0.28);
}
.lansia-catatan {
    text-align: center;
    font-size: clamp(0.95rem, 3.6vw, 1.1rem);
    color: #475569;
    line-height: 1.45;
    margin-top: 6px;
}
/* Sembunyikan elemen Streamlit yang tidak perlu di mode lansia */
.lansia-hide { display: none !important; }
</style>
"""


def aktifkan(mode: str | None) -> bool:
    """True bila parameter URL menunjukkan mode mudah (?mode=mudah / lansia / simple)."""
    nilai = (mode or "").strip().lower()
    return nilai in ("mudah", "lansia", "simple", "easy")


def _label_tanah(persen: float) -> str:
    if persen >= 70:
        return "Penuh"
    if persen >= 50:
        return "Basah"
    return "Kering"


def render(weather: dict, risk: dict) -> None:
    """Gambar satu layar sederhana: status besar, 3 angka, 3 langkah, 1 tombol."""
    info = TEKS_STATUS.get(risk.get("level", "AMAN"), TEKS_STATUS["AMAN"])

    st.markdown(_css_lansia(), unsafe_allow_html=True)

    denyut = (
        "animation: blink-siaga-emergency 1.05s infinite ease-in-out;"
        if risk.get("level") == "SIAGA"
        else ""
    )

    st.markdown(
        f"""
<div class="lansia-wrap">
  <div class="lansia-status"
       style="background:{info['latar']}; border-color:{info['garis']}; {denyut}">
    <div class="lansia-emoji">{info['emoji']}</div>
    <div class="lansia-judul" style="color:{info['warna']};">{info['judul']}</div>
    <div class="lansia-kalimat">{info['kalimat']}</div>
  </div>

  <div class="lansia-angka">
    <div>
      <div class="label">Hujan<br>1 hari</div>
      <div class="nilai" style="color:{info['warna']};">{weather['rain_24h']:.0f}<span style="font-size:0.5em;"> mm</span></div>
    </div>
    <div>
      <div class="label">Hujan<br>3 hari</div>
      <div class="nilai">{weather['rain_3d_total']:.0f}<span style="font-size:0.5em;"> mm</span></div>
    </div>
    <div>
      <div class="label">Tanah</div>
      <div class="nilai" style="font-size:clamp(1.25rem,5.2vw,1.7rem);">{_label_tanah(weather['soil_moisture_pct'])}</div>
    </div>
  </div>

  <div class="lansia-langkah">
    {''.join(
        f'<div class="baris"><span class="ikon">{ikon}</span><span>{teks}</span></div>'
        for ikon, teks in info['langkah']
    )}
  </div>

  <a class="lansia-tombol" href="tel:112">📞 TELEPON 112 (DARURAT)</a>

  <div class="lansia-catatan">
    Dipasang oleh Balai Desa Pagentan.<br>
    Diperbarui: {weather['updated_at']}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
