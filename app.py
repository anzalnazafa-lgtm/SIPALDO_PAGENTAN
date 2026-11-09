"""
SIPALDO-PAGENTAN
Sistem Peringatan Dini Longsor Desa Pagentan
Kecamatan Pagentan, Kabupaten Banjarnegara, Provinsi Jawa Tengah (Kode Desa: 33.04.14.2012).

Mencakup seluruh 5 wilayah Dusun di Desa Pagentan:
Dusun Krajan 1, Dusun Krajan 2, Dusun Bulu, Dusun Sawangan, dan Dusun Tedunan.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

from charts_qr import (
    build_3day_rainfall_chart,
    build_hourly_timeline_chart,
    generate_village_qr_png,
)
import tampilan_lansia
from ews_features import (
    DUSUN_POS,
    DUSUN_SLUG,
    resolve_dusun_slug,
    KONDISI_PATROLI,
    analisis_antisipasi,
    kirim_telegram,
    log_ke_csv,
    muat_log,
    pesan_wa_patroli,
    rekap_log,
    simpan_log,
    susun_pesan_status,
    tambah_entri_log,
    telegram_terkonfigurasi,
)
from lokasi_desa import (
    LAPORAN_VERIFIKASI,
    TITIK_LOKAL,
    get_titik_lokal,
)
from gis_engine import (
    LAT_NORTH,
    LAT_SOUTH,
    LON_EAST,
    LON_WEST,
    MAP_CENTER,
    VITAL_LOCATIONS,
    build_pagentan_gis_map,
    describe_user_position,
    haversine_m,
    nearest_vital_location,
)
from weather_ews import (
    classify_landslide_risk,
    fetch_realtime_open_meteo,
    get_weather_data,
)

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN UTAMA (MOBILE-FRIENDLY)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SIPALDO-PAGENTAN | Peringatan Dini Longsor Desa Pagentan",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


KEYFRAMES_BLINK = """
<style>
@keyframes blink-siaga-emergency {
    0%, 100% { box-shadow: 0 0 26px rgba(220, 38, 38, 0.85); }
    50% { box-shadow: 0 0 4px rgba(220, 38, 38, 0.25); }
}
</style>
"""


def inject_custom_styles(is_emergency: bool) -> None:
    """Injeksi CSS responsif berfont besar untuk layar HP warga & Mode Darurat Merah."""
    page_bg = "#FEF2F2" if is_emergency else "#F8FAFC"
    card_border_default = "#FCA5A5" if is_emergency else "#E2E8F0"

    css = f"""
<style>
/* Tipografi Besar & Bersih Ramah Smartphone Warga & Pos Ronda */
.stApp {{
    background-color: {page_bg};
    color: #0F172A;
}}
.block-container {{
    max-width: 1120px !important;
    padding-top: 1.1rem !important;
    padding-bottom: 3rem !important;
}}
p, li, label, .stMarkdown {{
    font-size: 1.04rem;
    line-height: 1.58;
}}

/* Animasi Kedip Menyala Mode Darurat SIAGA (> 50 mm) */
@keyframes blink-siaga-emergency {{
    0%, 100% {{
        background: linear-gradient(90deg, #DC2626 0%, #EF4444 50%, #DC2626 100%);
        box-shadow: 0 0 28px rgba(220, 38, 38, 0.92);
        transform: scale(1.0);
    }}
    50% {{
        background: linear-gradient(90deg, #7F1D1D 0%, #991B1B 50%, #7F1D1D 100%);
        box-shadow: 0 0 8px rgba(220, 38, 38, 0.45);
        transform: scale(0.996);
    }}
}}

.top-banner-siaga {{
    animation: blink-siaga-emergency 1.05s infinite ease-in-out;
    color: #FFFFFF;
    font-weight: 900;
    font-size: clamp(1.12rem, 2.8vw, 1.45rem);
    text-align: center;
    padding: 18px 20px;
    border-radius: 14px;
    border: 3px solid #FEF08A;
    margin-bottom: 14px;
    letter-spacing: 0.2px;
}}

.top-banner-waspada {{
    background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
    color: #FFFFFF;
    font-weight: 800;
    font-size: clamp(1.1rem, 2.5vw, 1.35rem);
    text-align: center;
    padding: 15px 18px;
    border-radius: 14px;
    border: 2px solid #FDE68A;
    box-shadow: 0 6px 18px rgba(217, 119, 6, 0.25);
    margin-bottom: 14px;
}}

.top-banner-aman {{
    background: linear-gradient(135deg, #15803D 0%, #16A34A 100%);
    color: #FFFFFF;
    font-weight: 800;
    font-size: clamp(1.1rem, 2.5vw, 1.35rem);
    text-align: center;
    padding: 15px 18px;
    border-radius: 14px;
    border: 2px solid #BBF7D0;
    box-shadow: 0 6px 18px rgba(21, 128, 61, 0.20);
    margin-bottom: 14px;
}}

.offline-pill {{
    background: #FFF7ED;
    color: #9A3412;
    border: 1px solid #FDBA74;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 0.92rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 14px;
}}

/* Landing Page Hero */
.hero-landing {{
    background: {"linear-gradient(135deg, #450A0A 0%, #7F1D1D 55%, #991B1B 100%)" if is_emergency else "linear-gradient(135deg, #0F172A 0%, #14532D 60%, #15803D 100%)"};
    color: #FFFFFF;
    padding: 28px 26px;
    border-radius: 18px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.16);
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.16);
}}
.hero-kicker {{
    display: inline-block;
    background: rgba(255, 255, 255, 0.16);
    color: #F8FAFC;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 999px;
    margin-bottom: 10px;
}}
.hero-title {{
    font-size: clamp(1.65rem, 4vw, 2.45rem);
    font-weight: 900;
    line-height: 1.15;
    margin: 0 0 8px 0;
    color: #FFFFFF;
}}
.hero-subtitle {{
    font-size: clamp(1.02rem, 2.2vw, 1.18rem);
    color: #E2E8F0;
    margin: 0 0 16px 0;
    max-width: 820px;
}}
.hero-meta-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}}
.hero-chip {{
    background: rgba(15, 23, 42, 0.42);
    border: 1px solid rgba(255, 255, 255, 0.22);
    color: #F8FAFC;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 600;
}}

/* Kartu Fitur & Metrik */
.sipaldo-card {{
    background: #FFFFFF;
    border: 1.5px solid {card_border_default};
    border-radius: 14px;
    padding: 18px 18px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    height: 100%;
}}
.metric-tile {{
    background: #FFFFFF;
    border: 1.5px solid {card_border_default};
    border-radius: 14px;
    padding: 16px 16px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    margin-bottom: 10px;
}}
.metric-label {{
    font-size: 0.9rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
.metric-value {{
    font-size: 1.85rem;
    font-weight: 900;
    color: #0F172A;
    margin: 4px 0;
    line-height: 1.15;
}}
.metric-sub {{
    font-size: 0.88rem;
    color: #64748B;
    font-weight: 500;
}}

/* Bilah navigasi peta */
.map-nav-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    margin: 6px 0 10px 0;
}}
.map-nav-link {{
    display: inline-block;
    text-decoration: none !important;
    background: #FFFFFF;
    border: 2px solid #1D4ED8;
    color: #1D4ED8 !important;
    font-weight: 800;
    font-size: 0.95rem;
    padding: 9px 14px;
    border-radius: 10px;
    white-space: nowrap;
}}
.map-nav-link:hover {{
    background: #EFF6FF;
}}
.map-nav-note {{
    font-size: 0.86rem;
    color: #475569;
}}

/* Judul Seksi */
.section-header {{
    margin-top: 24px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #E2E8F0;
}}
.section-header h2 {{
    margin: 0;
    font-size: clamp(1.3rem, 2.8vw, 1.65rem);
    font-weight: 800;
    color: #0F172A;
}}
.section-header p {{
    margin: 4px 0 0 0;
    font-size: 0.96rem;
    color: #475569;
}}

/* Kartu Telepon & Posko Kedaruratan */
.emergency-btn {{
    display: block;
    text-decoration: none !important;
    background: #FFFFFF;
    border: 2px solid #CBD5E1;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #0F172A !important;
    transition: all 0.15s ease;
}}
.emergency-btn:hover {{
    border-color: #15803D;
    background: #F0FDF4;
}}
.emergency-static {{
    background: #F8FAFC;
    border: 2px solid #CBD5E1;
    border-radius: 12px;
    padding: 14px 16px;
    color: #0F172A;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. STATE SIMULASI EDUKASI & GEJALA LAPANGAN POS RONDA
# -----------------------------------------------------------------------------
if "data_mode" not in st.session_state:
    st.session_state.data_mode = "REALTIME"

for key in ("chk_retakan", "chk_rembesan", "chk_pohon", "chk_gemuruh"):
    if key not in st.session_state:
        st.session_state[key] = False

# Fitur "Lokasi Saya Real-Time": posisi warga dari GPS HP / pilihan manual
if "user_loc" not in st.session_state:
    st.session_state.user_loc = None
if "manual_titik" not in st.session_state:
    st.session_state.manual_titik = "Pilih dusun / titik lokal…"
if "loc_message" not in st.session_state:
    st.session_state.loc_message = None

# Kalibrasi koordinat titik lokal oleh perangkat desa (tersimpan selama sesi/browser)
if "titik_overrides" not in st.session_state:
    st.session_state.titik_overrides = {}

# Log patroli Pos Ronda (tersimpan di berkas JSON lokal agar tidak hilang saat refresh)
if "log_patroli" not in st.session_state:
    st.session_state.log_patroli = muat_log()

# Antisipasi 6–12 jam: hitung setiap render setelah data cuaca tersedia
if "telegram_terakhir" not in st.session_state:
    st.session_state.telegram_terakhir = None

symptom_count = sum(
    int(bool(st.session_state[k]))
    for k in ("chk_retakan", "chk_rembesan", "chk_pohon", "chk_gemuruh")
)

# Bila warga sudah membagikan lokasi, cuaca diambil pada titik GPS warga tsb.
_active_loc = st.session_state.user_loc
if _active_loc and _active_loc.get("lat") is not None:
    weather = get_weather_data(
        st.session_state.data_mode, lat=_active_loc["lat"], lon=_active_loc["lon"]
    )
else:
    weather = get_weather_data(st.session_state.data_mode)

risk = classify_landslide_risk(weather, field_symptom_count=symptom_count)

# Titik lokal yang dipakai peta/analisis: sudah termasuk hasil kalibrasi petugas
titik_aktif = get_titik_lokal(st.session_state.titik_overrides)

# Antisipasi 6–12 jam ke depan (indikator "leading", bukan hanya kondisi saat ini)
antisipasi = analisis_antisipasi(weather)

inject_custom_styles(is_emergency=risk["is_emergency"])

# -----------------------------------------------------------------------------
# 2B. MODE LANSIA (?mode=mudah) — SATU LAYAR, TEKS BESAR & PENDEK
# -----------------------------------------------------------------------------
_mode_param = ""
try:
    _mode_param = (st.query_params.get("mode") or "").strip()
except Exception:
    try:
        _mode_param = (st.experimental_get_query_params().get("mode", [""])[0] or "").strip()
    except Exception:
        _mode_param = ""

MODE_LANSIA = tampilan_lansia.aktifkan(_mode_param)
st.markdown(KEYFRAMES_BLINK, unsafe_allow_html=True)

if MODE_LANSIA:
    if weather["is_offline"]:
        st.markdown(
            '<div style="text-align:center; font-size:1.05rem; font-weight:700; color:#92400E; '
            'background:#FEF3C7; border:2px solid #FCD34D; border-radius:12px; padding:10px; '
            'margin-bottom:12px;">⚠️ Sedang offline — data terakhir yang dipakai.</div>',
            unsafe_allow_html=True,
        )
    tampilan_lansia.render(weather, risk)

    st.markdown(
        f'<div style="max-width:760px;margin:18px auto 0 auto;text-align:center;">'
        f'<a href="?mode=normal" style="display:inline-block;padding:12px 18px;border-radius:12px;'
        f'border:2px solid #94A3B8;color:#334155;text-decoration:none;font-weight:700;font-size:1rem;">'
        f'Tampilan lengkap (petugas)</a></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# -----------------------------------------------------------------------------
# 3. BANNER PERINGATAN DINI PALING ATAS (REAL-TIME)
# -----------------------------------------------------------------------------
if risk["level"] == "SIAGA":
    st.markdown(
        f'<div class="top-banner-siaga">🚨 {risk["banner_text"]}</div>',
        unsafe_allow_html=True,
    )
elif risk["level"] == "WASPADA":
    st.markdown(
        f'<div class="top-banner-waspada">⚠️ {risk["banner_text"]}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="top-banner-aman">✅ {risk["banner_text"]}</div>',
        unsafe_allow_html=True,
    )

# --- Deteksi QR Pos Ronda: parameter ?pos=Dusun di URL ---
_pos_param = ""
try:
    _pos_param = (st.query_params.get("pos") or "").strip()
except Exception:
    try:
        _pos_param = (st.experimental_get_query_params().get("pos", [""])[0] or "").strip()
    except Exception:
        _pos_param = ""

if _pos_param:
    _cocok = resolve_dusun_slug(_pos_param)
    if _cocok:
        st.markdown(
            f"""<div style="background:#ECFDF5; border:2px solid #34D399; border-radius:12px;
            padding:12px 16px; margin-bottom:12px; font-size:1rem; color:#065F46;">
            🏠 <b>Anda memindai QR {_cocok}</b> — silakan lanjut ke bagian
            <b>Log Patroli Pos Ronda</b> di bawah untuk mencatat hasil ronda malam ini.
            </div>""",
            unsafe_allow_html=True,
        )

# Banner tambahan: ANTISIPASI 6–12 JAM KE DEPAN (hujan turun + prakiraan)
if antisipasi["level"] != "AMAN_TERKENDALI" and not weather["is_offline"]:
    _ikon = "🌧️" if antisipasi["level"] == "ANTISIPASI_WASPADA" else "⏳"
    st.markdown(
        f"""<div style="background:#FFF7ED; border:2.5px dashed {antisipasi['warna']};
        border-radius:14px; padding:14px 18px; margin-bottom:14px;">
<div style="font-size:0.82rem; font-weight:800; color:{antisipasi['warna']}; letter-spacing:0.5px;">
{_ikon} ANTISIPASI 6–12 JAM KE DEPAN (INDIKATOR AWAL)
</div>
<div style="font-size:clamp(1.02rem, 2.4vw, 1.22rem); font-weight:800; color:#7C2D12; margin:4px 0 6px 0;">
{antisipasi['judul']}
</div>
<div style="font-size:0.98rem; color:#1E293B; margin-bottom:6px;">{antisipasi['pesan']}</div>
<div style="font-size:0.95rem; color:#334155;"><b>Siapkan sekarang:</b> {antisipasi['arahan']}</div>
</div>""",
        unsafe_allow_html=True,
    )

# Penanda wajib saat API gagal merespons (mode fallback anti-crash)
if weather["is_offline"]:
    st.markdown(
        '<div class="offline-pill">📡 <b>Menampilkan estimasi offline</b> — '
        'Server cuaca sedang tidak terjangkau, menggunakan data cadangan terakhir agar sistem tetap aktif.</div>',
        unsafe_allow_html=True,
    )
elif weather.get("is_simulation"):
    st.info(
        f"🎓 **Mode Edukasi & Simulasi Aktif ({risk['label_ui']})** — "
        "Menampilkan contoh respons sistem untuk pembelajaran warga. Pilih **Live Real-Time (Open-Meteo)** untuk kembali ke kondisi asli Desa Pagentan."
    )

# -----------------------------------------------------------------------------
# 4. LANDING PAGE / HERO IDENTITY SELURUH DESA PAGENTAN
# -----------------------------------------------------------------------------
hero_html = f"""
<div class="hero-landing">
<div class="hero-kicker">⛰️ Sistem Peringatan Dini Kebencanaan Skala Desa • Kode Desa 33.04.14.2012</div>
<h1 class="hero-title">SIPALDO-PAGENTAN</h1>
<p class="hero-subtitle">
<b>Sistem Peringatan Dini Longsor Desa Pagentan</b> — Pemantauan curah hujan real-time, kejenuhan tanah,
dan peta kerawanan lintas <b>5 Dusun (Krajan 1, Krajan 2, Bulu, Sawangan, &amp; Tedunan)</b> di Kec. Pagentan, Kab. Banjarnegara.
</p>
<div class="hero-meta-row">
<span class="hero-chip">📍 Desa Pagentan, Kec. Pagentan, Banjarnegara</span>
<span class="hero-chip">✅ 12 titik terverifikasi perangkat desa</span>
<span class="hero-chip">🧭 Pusat Desa (Balai Desa): -7.30043, 109.80995</span>
<span class="hero-chip">⛰️ Elevasi: ±{weather['elevation_m']} mdpl</span>
<span class="hero-chip">🕒 Pembaruan: {weather['updated_at']}</span>
</div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# 3 Pilar Informasi Cepat pada Landing Page
pilar_col1, pilar_col2, pilar_col3 = st.columns(3)
with pilar_col1:
    st.markdown(
        """<div class="sipaldo-card">
<div style="font-size:1.35rem; margin-bottom:4px;">🌧️ <b>1. Cuaca &amp; Tanah Real-Time</b></div>
<div style="color:#475569; font-size:0.96rem;">
Menarik data curah hujan 24 jam &amp; akumulasi 3 hari langsung dari <b>Open-Meteo API</b> pada koordinat Desa Pagentan secara gratis.
</div>
</div>""",
        unsafe_allow_html=True,
    )
with pilar_col2:
    st.markdown(
        """<div class="sipaldo-card">
<div style="font-size:1.35rem; margin-bottom:4px;">🗺️ <b>2. Cakupan Seluruh 5 Dusun</b></div>
<div style="color:#475569; font-size:0.96rem;">
Memetakan 100 blok grid &amp; <b>12 titik resmi desa</b> (sekolah, masjid, puskesmas, balai desa) di <b>Krajan 1, Krajan 2, Bulu, Sawangan, dan Tedunan</b>.
</div>
</div>""",
        unsafe_allow_html=True,
    )
with pilar_col3:
    st.markdown(
        """<div class="sipaldo-card">
<div style="font-size:1.35rem; margin-bottom:4px;">🔔 <b>3. Siaga Warga &amp; Pos Ronda</b></div>
<div style="color:#475569; font-size:0.96rem;">
Fitur <b>Lokasi Saya (GPS)</b> menampilkan titik Anda di peta, kondisi lereng di sekitar, plus checklist patroli Pos Ronda.
</div>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown(
    """<div style="margin:6px 0 14px 0;">
<a href="?mode=mudah" style="display:block;text-align:center;text-decoration:none;
background:#1D4ED8;color:#FFFFFF;font-weight:900;font-size:clamp(1.05rem,3.2vw,1.25rem);
padding:16px;border-radius:14px;">👵 Tampilan Mudah untuk Lansia</a>
<div style="text-align:center;font-size:0.86rem;color:#475569;margin-top:6px;">
Huruf besar, kalimat pendek, tanpa grafik.</div>
</div>""",
    unsafe_allow_html=True,
)

st.write("")

# Panel Uji & Edukasi Fungsi Aplikasi (Tetap Ditampilkan di Halaman Utama untuk Edukasi Warga)
with st.container(border=True):
    ctrl_c1, ctrl_c2 = st.columns([3.7, 1.0])
    with ctrl_c1:
        mode_labels = {
            "REALTIME": "🟢 Live Real-Time (Open-Meteo)",
            "SIM_AMAN": "🎓 Edukasi AMAN (<20 mm)",
            "SIM_WASPADA": "🟡 Edukasi WASPADA (20–50 mm)",
            "SIM_SIAGA": "🔴 Edukasi SIAGA (>50 mm)",
            "SIM_OFFLINE": "📴 Edukasi Mode Offline",
        }
        selected_mode = st.radio(
            "🎓 **Panel Uji & Edukasi Fungsi Peringatan Dini (Klik untuk mempelajari perubahan status peta & sirine banner):**",
            options=list(mode_labels.keys()),
            format_func=lambda k: mode_labels[k],
            index=list(mode_labels.keys()).index(st.session_state.data_mode),
            horizontal=True,
        )
        if selected_mode != st.session_state.data_mode:
            st.session_state.data_mode = selected_mode
            st.rerun()
    with ctrl_c2:
        st.write("")
        if st.button("🔄 Segarkan Cuaca", width="stretch"):
            fetch_realtime_open_meteo.clear()
            st.rerun()

# -----------------------------------------------------------------------------
# 4B. LOKASI SAYA REAL-TIME (GPS HP WARGA) — INTI FITUR SCAN QR CODE
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>📍 Lokasi Saya Sekarang (Real-Time GPS)</h2>
<p>Tekan tombol di bawah agar aplikasi mengetahui posisi Anda, menampilkan nama dusun, kondisi lereng, bahaya longsor, dan titik aman terdekat.</p>
</div>""",
    unsafe_allow_html=True,
)

loc_col1, loc_col2, loc_col3 = st.columns([1.25, 1.5, 1.0])

with loc_col1:
    if st.button("📍 Aktifkan Lokasi Saya (GPS HP)", width="stretch", type="primary"):
        st.session_state["_gps_request"] = True
        st.session_state.loc_message = None
    if st.session_state.user_loc:
        if st.button("❌ Matikan Lokasi Saya", width="stretch"):
            st.session_state.user_loc = None
            st.session_state.loc_message = None
            st.rerun()

    st.caption(
        "Izin lokasi hanya dipakai di perangkat Anda untuk menampilkan posisi pada peta. "
        "Posisi **tidak disimpan** di server. Jika izin lokasi ditolak, gunakan pilihan dusun di samping."
    )

# Permintaan izin GPS ke browser HP
if st.session_state.get("_gps_request"):
    _geo = get_geolocation()
    if _geo and _geo.get("coords"):
        _c = _geo["coords"]
        st.session_state.user_loc = {
            "lat": float(_c["latitude"]),
            "lon": float(_c["longitude"]),
            "akurasi_m": int(round(float(_c.get("accuracy") or 0))) or None,
            "sumber": "GPS HP",
        }
        st.session_state["_gps_request"] = False
        st.session_state.loc_message = None
        st.rerun()
    elif _geo and _geo.get("error"):
        st.session_state["_gps_request"] = False
        st.session_state.loc_message = (
            "⚠️ Izin lokasi tidak diberikan atau GPS tidak aktif. "
            "Silakan pilih dusun/titik lokal Anda pada kolom di samping."
        )

with loc_col2:
    _manual_options = ["Pilih dusun / titik lokal…"] + [
        f"{loc['dusun'].split(' (')[0]} — {loc['name']}" for loc in VITAL_LOCATIONS
    ]
    _pilihan = st.selectbox(
        "Belum bisa pakai GPS? Pilih dusun / titik lokal terdekat:",
        options=_manual_options,
        index=0,
    )
    if _pilihan != _manual_options[0] and not st.session_state.user_loc:
        _idx = _manual_options.index(_pilihan) - 1
        _titik = VITAL_LOCATIONS[_idx]
        if st.button("✅ Gunakan Titik Ini sebagai Lokasi Saya", width="stretch"):
            st.session_state.user_loc = {
                "lat": _titik["coords"][0],
                "lon": _titik["coords"][1],
                "akurasi_m": None,
                "sumber": "Pilih manual",
                "label": _titik["name"],
            }
            st.session_state.loc_message = None
            st.rerun()

with loc_col3:
    if st.session_state.user_loc:
        _u = st.session_state.user_loc
        _pos = describe_user_position(_u["lat"], _u["lon"])
        _badge_color = "#15803D" if _pos["di_dalam_desa"] else "#B45309"
        _badge_text = "Di area Desa Pagentan" if _pos["di_dalam_desa"] else "Di luar area Desa Pagentan"
        st.markdown(
            f"""<div class="metric-tile" style="border-color:#93C5FD;">
<div class="metric-label">Status Lokasi</div>
<div class="metric-value" style="font-size:1.1rem; color:#1D4ED8;">{_pos['dusun']}</div>
<div class="metric-sub" style="color:{_badge_color}; font-weight:700;">{_badge_text}</div>
<div class="metric-sub">{_u['lat']:.5f}, {_u['lon']:.5f}</div>
</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div class="metric-tile" style="border-style:dashed;">
<div class="metric-label">Status Lokasi</div>
<div class="metric-value" style="font-size:1.15rem; color:#64748B;">Belum Aktif</div>
<div class="metric-sub">Aktifkan GPS di samping untuk melihat kondisi tepat di lokasi Anda.</div>
</div>""",
            unsafe_allow_html=True,
        )

if st.session_state.loc_message:
    st.warning(st.session_state.loc_message)

# Kartu hasil analisis lokasi warga
if st.session_state.user_loc:
    _u = st.session_state.user_loc
    _pos = describe_user_position(_u["lat"], _u["lon"])
    _terdekat = _pos["titik_terdekat"]
    _jarak_terdekat = _terdekat.get("jarak_m", 0)

    # Status ancaman pada titik warga: gabungkan status desa + karakter zona lokasi
    if risk["level"] == "SIAGA" and _pos["zone_code"] in ("INTI_JURANG_SUNGAI", "KRITIS_TEBING", "KRITIS_SUNGAI_RAWA"):
        _loc_color, _loc_bg, _loc_border = "#DC2626", "#FEF2F2", "#FCA5A5"
        _loc_status = "BAHAYA TINGGI DI TITIK ANDA"
        _loc_action = (
            "Anda berada di zona tebing/alur sungai saat curah hujan desa sangat tinggi. "
            "Segera menjauh dari kaki tebing dan bergerak ke Posko Kebencanaan Desa / Balai Desa Pagentan."
        )
    elif risk["level"] in ("SIAGA", "WASPADA") or _pos["zone_code"] != "ZONA_STABIL":
        _loc_color, _loc_bg, _loc_border = "#D97706", "#FFFBEB", "#FCD34D"
        _loc_status = "PERLU DIPANTAU"
        _loc_action = (
            "Lokasi Anda berada pada lereng/area yang mulai jenuh air. "
            "Periksa saluran air di sekitar rumah, waspadai retakan tanah, dan siapkan tas siaga."
        )
    else:
        _loc_color, _loc_bg, _loc_border = "#15803D", "#F0FDF4", "#BBF7D0"
        _loc_status = "RELATIF AMAN"
        _loc_action = (
            "Kondisi di sekitar lokasi Anda relatif stabil. Tetap ikuti informasi resmi "
            "dari Balai Desa dan Pos Ronda setempat."
        )

    st.markdown(
        f"""<div style="background:{_loc_bg}; border:2.5px solid {_loc_border}; border-radius:16px; padding:18px 20px;">
<div style="font-size:0.86rem; font-weight:800; color:{_loc_color}; text-transform:uppercase; letter-spacing:0.5px;">
KONDISI DI LOKASI ANDA SEKARANG • SUMBER: {_u.get('sumber', 'GPS HP').upper()}
</div>
<div style="font-size:clamp(1.35rem, 3.2vw, 1.8rem); font-weight:900; color:{_loc_color}; line-height:1.2; margin-bottom:8px;">
{_loc_status}
</div>
<div style="font-size:1rem; color:#1E293B; margin-bottom:10px;">
<b>{_pos['dusun']}</b> • {_pos['zone_name']} • Kemiringan {_pos['slope_deg']}<br>
{_pos['terrain_desc']}
</div>
<div style="background:#FFFFFF; border-left:5px solid {_loc_color}; padding:11px 13px; border-radius:8px; margin-bottom:8px;">
<b>Situasi cuaca di titik Anda:</b> hujan 24 jam <b>{weather['rain_24h']:.1f} mm</b>,
akumulasi 3 hari <b>{weather['rain_3d_total']:.1f} mm</b>,
kejenuhan tanah <b>{weather['soil_moisture_pct']:.1f}%</b>,
{weather['weather_desc']} ({weather['temperature_c']:.1f} °C), elevasi ±{weather['elevation_m']} mdpl.
</div>
<div style="background:#FFFFFF; border-left:5px solid #1D4ED8; padding:11px 13px; border-radius:8px; margin-bottom:8px;">
<b>Arahan untuk Anda:</b> {_loc_action}
</div>
<div style="display:flex; flex-wrap:wrap; gap:8px; font-size:0.92rem;">
<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:9px; padding:8px 11px;">
📍 <b>Titik aman terdekat:</b> {_terdekat.get('name', '-')} (±{_jarak_terdekat:.0f} m)
</div>
<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:9px; padding:8px 11px;">
🏛️ <b>Jarak ke Balai Desa:</b> {_pos['jarak_ke_balai_m']:.0f} m
</div>
<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:9px; padding:8px 11px;">
🕒 <b>Pembaruan:</b> {weather['updated_at']}
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )
    st.caption(
        "ℹ️ Posisi GPS hanya ditampilkan di perangkat Anda dan tidak dikirim/disimpan ke server. "
        "Anda dapat mematikan lokasi kapan saja dengan tombol **❌ Matikan Lokasi Saya**."
    )
else:
    st.info(
        "💡 **Tips untuk warga:** setelah menekan tombol lokasi, browser HP akan meminta izin "
        "*“Izinkan akses lokasi”* — tekan **Izinkan**. Peta akan langsung menandai titik Anda dan menampilkan kondisi lereng di sekitar Anda."
    )

# -----------------------------------------------------------------------------
# 5. BAGIAN 1: WIDGET STATUS HARI INI & METRIK CUACA DESA
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>📡 Status Peringatan Dini Hari Ini</h2>
<p>Klasifikasi bahaya tanah longsor dinamis berdasarkan akumulasi curah hujan 24 jam &amp; kejenuhan tanah podsolik perbukitan Pagentan.</p>
</div>""",
    unsafe_allow_html=True,
)

status_card_html = f"""
<div style="background:{risk['bg_soft']}; border:2.5px solid {risk['border_color']};
border-radius:16px; padding:20px 22px; margin-bottom:16px;">
<div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:10px; margin-bottom:10px;">
<div>
<span style="font-size:0.86rem; font-weight:800; color:{risk['color']}; text-transform:uppercase; letter-spacing:0.6px;">
WIDGET STATUS HARI INI • SELURUH WILAYAH DESA PAGENTAN
</span>
<div style="font-size:clamp(1.55rem, 3.5vw, 2.15rem); font-weight:900; color:{risk['color']}; line-height:1.15;">
STATUS: {risk['label_ui']}
</div>
</div>
<div style="background:{risk['color']}; color:#FFFFFF; padding:8px 16px; border-radius:999px; font-weight:800; font-size:0.95rem;">
Hujan 24 Jam: {weather['rain_24h']:.1f} mm
</div>
</div>
<div style="font-size:1.03rem; color:#1E293B; margin-bottom:10px;">
<b>Analisis Kondisi:</b> {risk['summary_reason']}
</div>
<div style="background:#FFFFFF; border-left:5px solid {risk['color']}; padding:12px 14px; border-radius:8px; margin-bottom:8px;">
<b>🏃 Arahan Warga Desa:</b> {risk['citizen_action']}
</div>
<div style="background:#FFFFFF; border-left:5px solid #334155; padding:12px 14px; border-radius:8px;">
<b>🔦 Instruksi Pos Ronda &amp; Kentongan:</b> {risk['ronda_instruction']}<br>
<span style="font-size:0.92rem; color:#475569;"><b>Isyarat Kentongan Desa:</b> {risk['kentongan_code']}</span>
</div>
</div>
"""
st.markdown(status_card_html, unsafe_allow_html=True)

# 4 Kartu Indikator Utama Berfont Besar
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"""<div class="metric-tile">
<div class="metric-label">🌧️ Hujan 24 Jam</div>
<div class="metric-value" style="color:{risk['color']};">{weather['rain_24h']:.1f} mm</div>
<div class="metric-sub">Aman &lt;20 | Waspada 20–50 | Siaga &gt;50</div>
</div>""",
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"""<div class="metric-tile">
<div class="metric-label">💧 Akumulasi 3 Hari</div>
<div class="metric-value">{weather['rain_3d_total']:.1f} mm</div>
<div class="metric-sub">Total simpanan air hujan di tanah</div>
</div>""",
        unsafe_allow_html=True,
    )
with m3:
    soil_status = (
        "Sangat Jenuh" if weather["soil_moisture_pct"] >= 70
        else ("Mulai Jenuh" if weather["soil_moisture_pct"] >= 50 else "Normal")
    )
    st.markdown(
        f"""<div class="metric-tile">
<div class="metric-label">🌱 Kejenuhan Tanah</div>
<div class="metric-value">{weather['soil_moisture_pct']:.1f}%</div>
<div class="metric-sub">Lapisan 3–9 cm ({soil_status})</div>
</div>""",
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"""<div class="metric-tile">
<div class="metric-label">{weather['weather_icon']} Cuaca Saat Ini</div>
<div class="metric-value">{weather['temperature_c']:.1f}°C</div>
<div class="metric-sub">{weather['weather_desc']} • RH {weather['humidity_pct']}%</div>
</div>""",
        unsafe_allow_html=True,
    )

# Kartu indikator antisipasi 6–12 jam
_persen = min(antisipasi["proyeksi"] / 50.0 * 100, 100)
st.markdown(
    f"""<div class="metric-tile" style="border:2px solid {antisipasi['warna']};">
<div class="metric-label">⏳ Proyeksi Hujan 12 Jam ke Depan</div>
<div style="display:flex; flex-wrap:wrap; gap:18px; align-items:baseline; margin:6px 0;">
<div class="metric-value" style="color:{antisipasi['warna']}; margin:0;">{antisipasi['proyeksi']:.1f} mm</div>
<div class="metric-sub" style="font-size:0.95rem;">
= hujan 24 jam <b>{antisipasi['hujan_awal']:.1f} mm</b> + prakiraan 12 jam <b>{antisipasi['prakiraan_12j']:.1f} mm</b>
</div>
</div>
<div style="background:#E2E8F0; border-radius:99px; height:10px; overflow:hidden; margin-bottom:6px;">
<div style="width:{_persen:.0f}%; height:100%; background:{antisipasi['warna']};"></div>
</div>
<div class="metric-sub">
Ambang SIAGA 50 mm {'· <b style="color:#DC2626;">diperkirakan tercapai ± pukul ' + antisipasi['jam_capai'] + ' WIB</b>' if antisipasi['jam_capai'] else '· belum diperkirakan tercapai'}
</div>
</div>""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 6. BAGIAN 2: PETA INTERAKTIF KERAWANAN LONGSOR SELURUH DESA PAGENTAN
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>🗺️ Peta Interaktif Kerawanan Longsor &amp; Titik Lokal Desa Pagentan</h2>
<p>Sebaran 100 blok grid &amp; <b>12 titik resmi desa</b> (semua terverifikasi perangkat desa) di Dusun Krajan 1, Krajan 2, Bulu, Sawangan, dan Tedunan — Lat -7.2932 s.d. -7.3110 &amp; Lon 109.8010 s.d. 109.8190.</p>
</div>""",
    unsafe_allow_html=True,
)

map_opt1, map_opt2, map_opt3, map_opt4 = st.columns([1.8, 1.1, 1.1, 1.1])
with map_opt1:
    basemap_choice = st.selectbox(
        "Jenis Peta Dasar (Basemap):",
        ["OpenStreetMap", "Topografi Perbukitan (OpenTopoMap)"],
        index=0,
    )
with map_opt2:
    st.write("")
    show_grid_layer = st.checkbox("Tampilkan Grid 5 Dusun", value=True)
with map_opt3:
    st.write("")
    show_hydro_layer = st.checkbox("Alur Sungai & Tebing", value=True)
with map_opt4:
    st.write("")
    show_evac_layer = st.checkbox("Jalur Evakuasi", value=True)

# Navigasi peta: tombol buka OpenStreetMap pada koordinat Desa Pagentan yang benar
_bbox = f"{LON_WEST},{LAT_NORTH},{LON_EAST},{LAT_SOUTH}"
osm_link = f"https://www.openstreetmap.org/?mlat={MAP_CENTER[0]}&mlon={MAP_CENTER[1]}#map=15/{MAP_CENTER[0]}/{MAP_CENTER[1]}"
osm_bbox_link = f"https://www.openstreetmap.org/?bbox={_bbox}"
gmap_link = f"https://www.google.com/maps?q={MAP_CENTER[0]},{MAP_CENTER[1]}"
st.markdown(
    f"""<div class="map-nav-row">
<a class="map-nav-link" href="{osm_link}" target="_blank">🗺️ Tampilkan Peta Desa (OpenStreetMap)</a>
<a class="map-nav-link" href="{gmap_link}" target="_blank">📍 Buka Titik Desa di Google Maps</a>
<span class="map-nav-note">Pusat desa: {MAP_CENTER[0]:.5f}, {MAP_CENTER[1]:.5f} (±{weather['elevation_m']} mdpl)</span>
</div>""",
    unsafe_allow_html=True,
)

folium_map, grid_counts, dusun_summary = build_pagentan_gis_map(
    risk_level=risk["level"],
    show_grid=show_grid_layer,
    show_hydrology=show_hydro_layer,
    show_evac_routes=show_evac_layer,
    basemap_style=basemap_choice,
    user_location=st.session_state.user_loc,
    titik_lokal=titik_aktif,
)

map_col, info_col = st.columns([2.35, 1.0])
with map_col:
    st_folium(
        folium_map,
        use_container_width=True,
        height=620,
        returned_objects=[],
        key=(
            f"pagentan_map_{risk['level']}_{basemap_choice}_{show_grid_layer}_"
            f"{show_hydro_layer}_{show_evac_layer}_"
            f"{(st.session_state.user_loc or {}).get('lat', 'x')}_"
            f"{(st.session_state.user_loc or {}).get('lon', 'x')}"
        ),
    )

with info_col:
    legend_html = f"""
<div class="sipaldo-card">
<div style="font-weight:800; font-size:1.06rem; margin-bottom:10px; color:#0F172A;">
📌 Ringkasan 100 Blok Desa Pagentan
</div>
<div style="display:flex; justify-content:space-between; align-items:center; background:#FEF2F2; border:1px solid #FECACA; padding:9px 12px; border-radius:10px; margin-bottom:8px;">
<span style="font-weight:700; color:#991B1B;">🟥 Zona Merah (Siaga Tebing/Sungai)</span>
<span style="font-weight:900; font-size:1.15rem; color:#DC2626;">{grid_counts['merah']}</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; background:#FFFBEB; border:1px solid #FDE68A; padding:9px 12px; border-radius:10px; margin-bottom:8px;">
<span style="font-weight:700; color:#92400E;">🟨 Zona Kuning (Waspada Lereng)</span>
<span style="font-weight:900; font-size:1.15rem; color:#D97706;">{grid_counts['kuning']}</span>
</div>
<div style="display:flex; justify-content:space-between; align-items:center; background:#F0FDF4; border:1px solid #BBF7D0; padding:9px 12px; border-radius:10px; margin-bottom:12px;">
<span style="font-weight:700; color:#166534;">🟩 Zona Hijau (Stabil / Aman)</span>
<span style="font-weight:900; font-size:1.15rem; color:#16A34A;">{grid_counts['hijau']}</span>
</div>
<hr style="border:none; border-top:1px solid #E2E8F0; margin:10px 0;">
<div style="font-weight:800; font-size:0.95rem; margin-bottom:6px;">📍 {len(titik_aktif)} Titik Resmi Desa (klik ikon layer di peta):</div>
<div style="font-size:0.86rem; color:#334155; line-height:1.55;">
🔵 <b>Balai Desa Pagentan</b> (pusat komando)<br>
🏳️ <b>Lapangan Rawa Sakti</b> (titik kumpul warga)<br>
🩵 <b>Puskesmas Pagentan 1</b><br>
🏛️ <b>Kantor Kecamatan Pagentan</b><br>
🎓 <b>SMPN 1, SDN 1, MI Muhammadiyah, MI GUPPI</b><br>
🕌 <b>Masjid Baitul Makmur, Baitul'nangim, Al Ikhlas, An Nur</b><br>
<span style="color:#15803D; font-weight:700;">✅ 12 dari 12 titik terverifikasi perangkat desa</span>
</div>
<hr style="border:none; border-top:1px solid #E2E8F0; margin:10px 0;">
<div style="font-size:0.82rem; color:#64748B;">
<b>Bounding Box Desa:</b><br>
Lat {LAT_NORTH:.4f} s.d. {LAT_SOUTH:.4f} | Lon {LON_WEST:.4f} s.d. {LON_EAST:.4f}<br>
Pusat Peta: {MAP_CENTER[0]}, {MAP_CENTER[1]}
</div>
</div>
"""
    st.markdown(legend_html, unsafe_allow_html=True)

# Ringkasan Sebaran Blok per Dusun (Seluruh 5 Dusun Desa Pagentan)
st.markdown("#### 🏘️ Sebaran Status Blok Kerawanan per Wilayah Dusun (RW 01 – RW 08)")
st.dataframe(
    pd.DataFrame(dusun_summary),
    width="stretch",
    hide_index=True,
)

with st.expander("📋 Lihat Rincian Lengkap 10 Titik Lokal, Koordinat & Status Akurasi"):
    st.caption(
        "Status koordinat: ✅ **terverifikasi** = sudah dicocokkan petugas desa; "
        "⚠️ **estimasi** = masih perkiraan dan perlu dikoreksi."
    )
    for idx, item in enumerate(titik_aktif, start=1):
        badge = "✅ terverifikasi" if item.get("sumber") == "terverifikasi" else "⚠️ estimasi"
        st.markdown(
            f"**{idx}. {item['name']}** — *{item['dusun']}*  \n"
            f"Koordinat: `{item['coords'][0]:.5f}, {item['coords'][1]:.5f}` — {badge}  \n"
            f"{item['desc']}"
        )
        if item.get("catatan"):
            st.caption(f"Catatan akurasi: {item['catatan']}")

# -----------------------------------------------------------------------------
# 6B. KALIBRASI TITIK LOKASI (VERIFIKASI KOORDINAT OLEH PERANGKAT DESA)
# -----------------------------------------------------------------------------
with st.expander("🔧 Kalibrasi Titik Lokasi — Perbaiki Koordinat Balai Desa, Posko, Puskesmas, dll."):
    st.warning(LAPORAN_VERIFIKASI)

    st.markdown(
        """
**Cara mengoreksi koordinat (2 pilihan):**

1. **Paling akurat — pakai GPS HP petugas:** berdiri tepat di lokasi (misal di depan Balai Desa),
   tekan tombol *“Gunakan Lokasi Saya (GPS HP) sebagai koordinat titik ini”*, lalu *“Simpan Koordinat Titik”*.
2. **Pakai koordinat Google Maps:** buka Google Maps di HP → tekan lama pada lokasi → salin koordinat yang muncul
   (format `-7.30583, 109.80944`) → tempelkan pada kolom Latitude / Longitude di bawah → *Simpan*.
        """
    )

    nama_pilihan = [t["name"] for t in TITIK_LOKAL]
    titik_pilih = st.selectbox(
        "Pilih titik yang ingin dikoreksi:",
        options=nama_pilihan,
        key="kalibrasi_pilih",
    )
    _entri_kini = next(t for t in titik_aktif if t["name"] == titik_pilih)

    k1, k2 = st.columns(2)
    with k1:
        lat_in = st.number_input(
            "Latitude (garis lintang)",
            value=float(_entri_kini["coords"][0]),
            format="%.6f",
            step=0.000010,
            key=f"kal_lat_{titik_pilih}",
        )
    with k2:
        lon_in = st.number_input(
            "Longitude (garis bujur)",
            value=float(_entri_kini["coords"][1]),
            format="%.6f",
            step=0.000010,
            key=f"kal_lon_{titik_pilih}",
        )

    tombol1, tombol2, tombol3 = st.columns(3)
    with tombol1:
        pakai_gps = st.button("📍 Gunakan Lokasi Saya (GPS HP)", width="stretch")
    with tombol2:
        simpan = st.button("💾 Simpan Koordinat Titik", width="stretch", type="primary")
    with tombol3:
        reset = st.button("↩️ Kembalikan ke Estimasi Awal", width="stretch")

    if pakai_gps:
        _g = get_geolocation()
        if _g and _g.get("coords"):
            st.session_state.titik_overrides[titik_pilih] = {
                "lat": float(_g["coords"]["latitude"]),
                "lon": float(_g["coords"]["longitude"]),
                "sumber": "terverifikasi",
                "catatan": "Koordinat diambil langsung dengan GPS HP petugas desa.",
            }
            st.success(
                f"📍 Koordinat titik **{titik_pilih}** diperbarui dari GPS HP: "
                f"{_g['coords']['latitude']:.6f}, {_g['coords']['longitude']:.6f}. Tekan **Simpan** bila sudah benar."
            )
        else:
            st.info(
                "Izin lokasi belum diberikan. Aktifkan izin lokasi pada browser, atau masukkan koordinat "
                "manual dari Google Maps pada kolom di atas."
            )

    if simpan:
        st.session_state.titik_overrides[titik_pilih] = {
            "lat": float(lat_in),
            "lon": float(lon_in),
            "sumber": "terverifikasi",
            "catatan": "Koordinat dikoreksi manual oleh pengguna aplikasi.",
        }
        st.success(f"✅ Koordinat **{titik_pilih}** disimpan: {lat_in:.6f}, {lon_in:.6f}. Peta akan diperbarui.")
        st.rerun()

    if reset:
        st.session_state.titik_overrides.pop(titik_pilih, None)
        st.info(f"↩️ Titik **{titik_pilih}** dikembalikan ke koordinat estimasi awal.")
        st.rerun()

    _n_verif = sum(1 for t in titik_aktif if t.get("sumber") == "terverifikasi")
    st.markdown(
        f"**Status verifikasi: {_n_verif} dari {len(titik_aktif)} titik sudah diverifikasi** "
        f"({'lengkap ✅' if _n_verif == len(titik_aktif) else 'masih ada titik estimasi ⚠️'})"
    )
    st.progress(_n_verif / max(len(titik_aktif), 1))

    if st.session_state.titik_overrides:
        st.download_button(
            "⬇️ Unduh Berkas Kalibrasi (JSON) — simpan agar tidak hilang",
            data=json.dumps(st.session_state.titik_overrides, indent=2, ensure_ascii=False),
            file_name="kalibrasi_titik_pagentan.json",
            mime="application/json",
        )
        st.caption(
            "Berkas JSON ini berisi koordinat hasil koreksi. Simpan di komputer/HP; "
            "agar permanen untuk semua warga, tempelkan nilai koordinatnya ke dalam berkas "
            "`lokasi_desa.py` (variabel `TITIK_LOKAL`) di repositori GitHub Anda."
        )

# -----------------------------------------------------------------------------
# 7. BAGIAN 3: GRAFIK TREN CURAH HUJAN 3 HARI TERAKHIR & PRAKIRAAN JAM-JAMAN
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>📊 Tren Curah Hujan &amp; Akumulasi Air Tanah (3 Hari Terakhir)</h2>
<p>Longsor pada tanah podsolik pegunungan Banjarnegara sering dipicu oleh tabungan air hujan 2–3 hari sebelumnya yang membuat lereng jenuh air.</p>
</div>""",
    unsafe_allow_html=True,
)

tab_3hari, tab_perjam = st.tabs([
    "📊 Tren Harian & Akumulasi 3 Hari Terakhir",
    "⏱️ Rincian Per Jam (24 Jam Terakhir & Prakiraan 12 Jam)",
])

with tab_3hari:
    fig_3d = build_3day_rainfall_chart(weather["daily_df"])
    st.plotly_chart(fig_3d, width="stretch", config={"displayModeBar": False})

    st.caption(
        "💡 **Cara Membaca Grafik untuk Warga & Petugas Ronda:** "
        "**Batang berwarna** menunjukkan curah hujan per hari (mm), sedangkan **garis biru** menunjukkan total air hujan "
        "yang menumpuk di dalam tanah selama beberapa hari terakhir. Jika garis biru terus menanjak tinggi meskipun hari ini hanya hujan sedang, "
        "tanah tebing di Dusun Bulu, Sawangan, maupun Tedunan sudah jenuh air dan perlu diwaspadai."
    )

with tab_perjam:
    fig_hr = build_hourly_timeline_chart(weather["hourly_24h_df"], weather["forecast_12h_df"])
    st.plotly_chart(fig_hr, width="stretch", config={"displayModeBar": False})
    st.info(
        f"🌧️ **Estimasi Prakiraan Hujan 12 Jam Ke Depan di Desa Pagentan:** **{weather['rain_forecast_12h']:.1f} mm**. "
        "Gunakan grafik ini untuk mengatur jadwal patroli malam di Pos Ronda tiap dusun."
    )

# -----------------------------------------------------------------------------
# 8. BAGIAN 4: CHECKLIST POS RONDA, SOP WARGA & SALURAN DARURAT RESMI
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>🛡️ Pos Ronda Siaga, Tanda Alam Longsor &amp; Saluran Darurat Resmi</h2>
<p>Panduan pemeriksaan lapangan bagi petugas ronda malam di 5 dusun serta saluran panggilan darurat resmi.</p>
</div>""",
    unsafe_allow_html=True,
)

ronda_col, kontak_col = st.columns([1.35, 1.0])

with ronda_col:
    with st.container(border=True):
        st.markdown("### 🔦 Checklist Patroli Lapangan Petugas Pos Ronda")
        st.caption(
            "Centang apabila warga/petugas ronda menemukan gejala fisik berikut di sekitar tebing atau alur sungai desa "
            "(mencentang ≥2 gejala akan otomatis menaikkan status kewaspadaan sistem):"
        )
        st.checkbox(
            "Muncul retakan tanah baru berbentuk lengkung / tapal kuda di atas lereng atau jalan dusun",
            key="chk_retakan",
        )
        st.checkbox(
            "Muncul rembesan / mata air baru yang keruh berlumpur pada kaki tebing",
            key="chk_rembesan",
        )
        st.checkbox(
            "Pohon, tiang listrik, atau pagar bambu di lereng tampak mulai miring",
            key="chk_pohon",
        )
        st.checkbox(
            "Terdengar suara gemuruh halus atau kerikil berjatuhan dari arah tebing",
            key="chk_gemuruh",
        )

        if symptom_count >= 2:
            st.error(
                f"🚨 **PERINGATAN LAPANGAN ({symptom_count} Gejala Ditemukan):** Segera bunyikan kentongan peringatan, "
                "laporkan ke Kepala Dusun / Balai Desa Pagentan, dan jauhi kaki tebing meskipun hujan sudah reda!"
            )
        elif symptom_count == 1:
            st.warning(
                "⚠️ **1 Gejala Awal Tercatat:** Pantau titik tersebut dari jarak aman dan jangan dekati bibir tebing sendirian pada malam hari."
            )
        else:
            st.success("✅ Belum ada gejala fisik keretakan lereng yang ditandai pada sesi pantauan ini.")

    with st.container(border=True):
        st.markdown("### 🎒 3 Aturan Keselamatan Utama Warga Pagentan")
        st.markdown(
            "1. **Waspadai Hujan Malam & Hujan Setelah Kemarau:** Segera matikan aliran listrik rumah jika air lumpur mulai masuk dan bersiap menuju titik kumpul.\n"
            "2. **Jangan Menyeberang Jembatan/Alur Sungai Saat Hujan Deras:** Aliran sungai yang melintasi lembah desa dapat membawa material longsoran hulu.\n"
            "3. **Siapkan Tas Siaga Keluarga:** Masukkan dokumen penting (KK/KTP), senter, jas hujan, obat rutin, pakaian hangat, dan peluit."
        )

with kontak_col:
    contacts_html = """
<div class="sipaldo-card">
<div style="font-weight:800; font-size:1.15rem; margin-bottom:6px;">📞 Saluran Darurat Resmi</div>
<div style="font-size:0.9rem; color:#475569; margin-bottom:12px;">
Ketuk tombol panggilan resmi berikut dari layar HP saat kondisi darurat:
</div>
<a class="emergency-btn" href="tel:112">
<div style="font-weight:800; font-size:1.05rem; color:#DC2626;">🚨 Layanan Darurat Terpadu (112)</div>
<div style="font-size:0.88rem; color:#475569;">Panggilan bebas pulsa kedaruratan nasional 24 jam</div>
</a>
<a class="emergency-btn" href="tel:0286591812">
<div style="font-weight:800; font-size:1.02rem; color:#0F172A;">🛟 Pusdalops BPBD Kab. Banjarnegara</div>
<div style="font-size:0.88rem; color:#475569;">Telp: (0286) 591812 • Komando Siaga Bencana Kabupaten</div>
</a>
<a class="emergency-btn" href="tel:119">
<div style="font-weight:800; font-size:1.02rem; color:#0284C7;">🚑 Layanan Medis / Puskesmas (119)</div>
<div style="font-size:0.88rem; color:#475569;">Ambulans &amp; pertolongan medis darurat warga</div>
</a>
<div class="emergency-static">
<div style="font-weight:800; font-size:1.0rem; color:#15803D;">🏛️ Posko Komando Balai Desa Pagentan</div>
<div style="font-size:0.88rem; color:#475569; margin-top:3px;">
Jl. Raya Pagentan – Banjarnegara (Dusun Krajan 1)<br>
Koordinasi langsung Kepala Dusun (Krajan 1, Krajan 2, Bulu, Sawangan, Tedunan) &amp; Pos Ronda RT/RW.
</div>
</div>
</div>
"""
    st.markdown(contacts_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8A. SKENARIO LATIHAN EVAKUASI (SIMULASI EDUKASI WARGA)
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>🎯 Skenario Latihan Evakuasi Desa</h2>
<p>Panduan singkat untuk simulasi di sekolah (SMPN 1 / SDN 1 / MI) atau saat pertemuan RT/RW — melatih warga bereaksi cepat sebelum bencana sebenarnya.</p>
</div>""",
    unsafe_allow_html=True,
)

_skenario = pd.DataFrame(
    [
        {
            "Skenario": "A. Hujan deras malam hari",
            "Pemicu": "Hujan >50 mm sejak sore, tanah jenuh",
            "Tindakan warga": "Matikan listrik, bawa tas siaga, menuju Balai Desa / Lapangan Rawa Sakti",
            "Isyarat": "Kentongan titir (cepat, terus-menerus)",
        },
        {
            "Skenario": "B. Retakan baru di lereng",
            "Pemicu": "Retakan tapal kuda / pohon miring",
            "Tindakan warga": "Menjauh dari kaki tebing, lapor Kadus, catat di log patroli",
            "Isyarat": "Kentongan 3x berulang",
        },
        {
            "Skenario": "C. Gemuruh dari arah tebing",
            "Pemicu": "Suara gemuruh / kerikil berjatuhan",
            "Tindakan warga": "Evakuasi segera tanpa mengambil barang, jangan melintas lembah",
            "Isyarat": "Kentongan titir + pengeras suara masjid",
        },
        {
            "Skenario": "D. Malam hari, listrik padam",
            "Pemicu": "Hujan ekstrem + jaringan listrik mati",
            "Tindakan warga": "Pakai senter/lampu kepala, ikuti jalur evakuasi bertanda, jangan sendirian",
            "Isyarat": "Kentongan titir + kentongan pos terdekat",
        },
    ]
)
st.dataframe(_skenario, width="stretch", hide_index=True, height=210)

_lat1, _lat2 = st.columns([1.2, 1.0])
with _lat1:
    with st.container(border=True):
        st.markdown("#### ✅ Checklist Persiapan Latihan (dicentang petugas)")
        for _kunci, _teks in [
            ("lat_jalur", "Jalur evakuasi ke Balai Desa & Lapangan Rawa Sakti sudah diperiksa bebas hambatan"),
            ("lat_titik", "Titik kumpul ditandai dan diketahui seluruh warga"),
            ("lat_rentan", "Daftar warga rentan (lansia, ibu hamil, balita, disabilitas) sudah diperbarui"),
            ("lat_kentongan", "Kentongan di setiap Pos Ronda diuji dan terdengar jelas"),
            ("lat_kontak", "Nomor darurat (112 / BPBD / Puskesmas) ditempel di papan pengumuman"),
            ("lat_tas", "Contoh tas siaga keluarga diperlihatkan kepada warga"),
            ("lat_waktu", "Target waktu evakuasi dicatat (contoh: < 15 menit)"),
        ]:
            st.checkbox(_teks, key=_kunci)

        _jumlah_cek = sum(
            1
            for _k in ("lat_jalur", "lat_titik", "lat_rentan", "lat_kentongan", "lat_kontak", "lat_tas", "lat_waktu")
            if st.session_state.get(_k)
        )
        st.progress(_jumlah_cek / 7)
        if _jumlah_cek == 7:
            st.success("✅ Seluruh persiapan latihan lengkap. Siap dilaksanakan bersama warga.")
        else:
            st.info(f"{_jumlah_cek} dari 7 butir persiapan sudah dicentang.")

with _lat2:
    with st.container(border=True):
        st.markdown("#### ⏱️ Catat Hasil Latihan")
        _tanggal_latih = st.date_input("Tanggal latihan:", key="lat_tanggal")
        _peserta = st.number_input("Jumlah peserta:", min_value=0, value=50, step=5, key="lat_peserta")
        _durasi = st.number_input("Waktu evakuasi tercapai (menit):", min_value=0.0, value=12.0, step=0.5, key="lat_durasi")
        _catatan_latih = st.text_input("Catatan perbaikan:", placeholder="mis. jalur utara berlumpur, perlu diberi papan petunjuk", key="lat_catatan")
        _ringkas = (
            f"*LAPORAN LATIHAN EVAKUASI — DESA PAGENTAN*\n"
            f"Tanggal: {_tanggal_latih}\n"
            f"Peserta: {int(_peserta)} orang\n"
            f"Waktu evakuasi: {_durasi:.1f} menit\n"
            f"Persiapan tercentang: {_jumlah_cek}/7\n"
            f"Catatan: {_catatan_latih or '-'}\n"
            f"Status desa saat latihan: {risk['label_ui']} (hujan 24 jam {weather['rain_24h']:.1f} mm)"
        )
        st.download_button(
            "⬇️ Unduh Ringkasan Latihan (TXT)",
            data=_ringkas.encode("utf-8"),
            file_name="laporan_latihan_evakuasi_pagentan.txt",
            mime="text/plain",
            width="stretch",
        )

# -----------------------------------------------------------------------------
# 8B. LOG PATROLI POS RONDA + NOTIFIKASI TELEGRAM
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>📝 Log Patroli Pos Ronda &amp; Notifikasi Otomatis</h2>
<p>Catat hasil ronda malam per dusun, pantau rekapnya, lalu kirim laporan ke grup WhatsApp desa atau bot Telegram.</p>
</div>""",
    unsafe_allow_html=True,
)

_log = st.session_state.log_patroli
_log_col, _notif_col = st.columns([1.45, 1.0])

with _log_col:
    with st.container(border=True):
        st.markdown("### 🗒️ Catat Hasil Patroli Malam")
        _f1, _f2 = st.columns(2)
        with _f1:
            _dusun_log = st.selectbox("Pos Ronda / Dusun:", DUSUN_POS, key="log_dusun")
        with _f2:
            _kondisi_log = st.selectbox(
                "Hasil pemeriksaan:",
                options=list(KONDISI_PATROLI.keys()),
                format_func=lambda k: KONDISI_PATROLI[k]["label"],
                key="log_kondisi",
            )
        _petugas_log = st.text_input(
            "Nama petugas ronda:", placeholder="mis. Pak Sutris (RT 03)", key="log_petugas"
        )
        _catatan_log = st.text_input(
            "Catatan temuan (opsional):",
            placeholder="mis. rembesan keruh di kaki tebing utara, retakan ±2 cm",
            key="log_catatan",
        )
        if st.button("💾 Simpan Laporan Patroli", type="primary", width="stretch"):
            st.session_state.log_patroli = tambah_entri_log(
                st.session_state.log_patroli,
                dusun=_dusun_log,
                kondisi=_kondisi_log,
                petugas=_petugas_log,
                catatan=_catatan_log,
                cuaca={**weather, "_status": risk["label_ui"]},
            )
            simpan_log(st.session_state.log_patroli)
            st.success("✅ Laporan patroli tersimpan.")
            st.rerun()

        if _log:
            st.markdown("#### 📊 Rekap Laporan Patroli per Dusun")
            st.dataframe(rekap_log(_log), width="stretch", hide_index=True)

            _terakhir = _log[-1]
            st.markdown("#### 📋 Laporan Terakhir")
            st.markdown(
                f"- **{_terakhir['dusun']}** — {_terakhir['waktu']} WIB  \n"
                f"  Petugas: {_terakhir['petugas']}  \n"
                f"  Hasil: **{_terakhir['label_kondisi']}**  \n"
                f"  Catatan: {_terakhir['catatan'] or '—'}"
            )
            if _terakhir["kondisi"] == "GEJALA_BERAT":
                st.error(
                    "🚨 Laporan terakhir berisi gejala berat. Segera koordinasikan dengan Kepala Dusun & Posko Desa, "
                    "dan pertimbangkan evakuasi mandiri warga di sekitar titik tersebut."
                )
            elif _terakhir["kondisi"] == "GEJALA_RINGAN":
                st.warning(
                    "⚠️ Laporan terakhir berisi gejala ringan. Tambah frekuensi pantau (setiap 1–2 jam) "
                    "dan catat perubahan kondisi pada laporan berikutnya."
                )

            st.text_area(
                "📱 Teks laporan siap kirim ke grup WhatsApp desa (salin/tempel):",
                value=pesan_wa_patroli(_terakhir, weather, antisipasi),
                height=190,
            )

            _d1, _d2 = st.columns(2)
            with _d1:
                st.download_button(
                    "⬇️ Unduh Log Patroli (CSV)",
                    data=log_ke_csv(_log),
                    file_name="log_patroli_pagentan.csv",
                    mime="text/csv",
                    width="stretch",
                )
            with _d2:
                if st.button("🗑️ Hapus Semua Log Patroli", width="stretch"):
                    st.session_state.log_patroli = []
                    simpan_log([])
                    st.info("Log patroli dikosongkan.")
                    st.rerun()

            with st.expander("📄 Lihat Seluruh Riwayat Laporan"):
                st.dataframe(pd.DataFrame(_log[::-1]), width="stretch", hide_index=True)
        else:
            st.info(
                "Belum ada laporan patroli. Setelah petugas ronda mencatat hasil pemeriksaan, "
                "rekap per dusun dan teks laporan WhatsApp akan muncul di sini."
            )

with _notif_col:
    with st.container(border=True):
        st.markdown("### 📨 Notifikasi Otomatis (Telegram)")
        st.caption(
            "Aplikasi web tidak bisa mengirim pesan tanpa izin. Dengan bot Telegram desa, "
            "peringatan bisa sampai ke warga **tanpa harus membuka aplikasi**."
        )

        _tg_token = st.text_input(
            "Token Bot Telegram:",
            type="password",
            placeholder="123456789:AAH...",
            help="Dapatkan dari @BotFather di Telegram.",
            key="tg_token",
        )
        _tg_chat = st.text_input(
            "Chat ID / ID Grup:",
            placeholder="mis. -1001234567890",
            help="Kirim 1 pesan ke bot, lalu buka https://api.telegram.org/bot<TOKEN>/getUpdates untuk melihat chat.id.",
            key="tg_chat",
        )
        _label_desa = st.text_input(
            "Label desa pada pesan:", value="Desa Pagentan", key="tg_label"
        )

        _pesan_status = susun_pesan_status(weather, risk, antisipasi, _label_desa)
        with st.expander("👀 Pratinjau pesan yang akan dikirim"):
            st.code(_pesan_status, language="markdown")

        if st.button("🚀 Kirim Ringkasan Status ke Telegram", width="stretch", type="primary"):
            if not telegram_terkonfigurasi(_tg_token, _tg_chat):
                st.warning("Isi **Token Bot** dan **Chat ID** terlebih dahulu.")
            else:
                _ok, _ket = kirim_telegram(_tg_token, _tg_chat, _pesan_status)
                if _ok:
                    st.success("✅ Pesan terkirim ke Telegram.")
                    st.session_state.telegram_terakhir = f"Status {risk['label_ui']} • {weather['updated_at']}"
                else:
                    st.error(f"❌ Gagal mengirim: {_ket}")

        if st.button("📢 Kirim Laporan Patroli Terakhir", width="stretch"):
            if not st.session_state.log_patroli:
                st.warning("Belum ada laporan patroli untuk dikirim.")
            elif not telegram_terkonfigurasi(_tg_token, _tg_chat):
                st.warning("Isi **Token Bot** dan **Chat ID** terlebih dahulu.")
            else:
                _pesan = pesan_wa_patroli(st.session_state.log_patroli[-1], weather, antisipasi)
                _ok, _ket = kirim_telegram(_tg_token, _tg_chat, _pesan.replace("*", "*"))
                if _ok:
                    st.success("✅ Laporan patroli terkirim ke Telegram.")
                else:
                    st.error(f"❌ Gagal mengirim: {_ket}")

        st.divider()
        st.markdown("**🤖 Cara membuat bot (5 menit, gratis):**")
        st.markdown(
            "1. Buka Telegram → cari **@BotFather** → kirim `/newbot` → ikuti petunjuk → salin **token**.\n"
            "2. Buat grup desa → tambahkan bot tersebut sebagai anggota.\n"
            "3. Kirim satu pesan di grup, lalu buka `https://api.telegram.org/bot<TOKEN>/getUpdates` "
            "dan salin angka **`chat.id`** (untuk grup biasanya negatif, mis. `-100...`).\n"
            "4. Tempel token & chat id di kolom atas → klik **Kirim Ringkasan Status**."
        )
        st.caption(
            "⚠️ Jangan bagikan token bot kepada publik. Untuk peringatan otomatis setiap pagi/sore "
            "(tanpa membuka aplikasi), lihat panduan singkat **notifikasi_telegram_otomatis.md** "
            "di dalam paket ZIP."
        )

# -----------------------------------------------------------------------------
# 9. BAGIAN 5: AKSES WARGA VIA QR CODE (SIAP TEMPEL DI POS RONDA & BALAI DESA)
# -----------------------------------------------------------------------------
st.markdown(
    """<div class="section-header">
<h2>📱 Kartu QR Code Akses Warga &amp; Pos Ronda (5 Dusun)</h2>
<p>Cetak dan tempelkan QR Code ini di Balai Desa Pagentan, Pos Ronda tiap dusun, Masjid/Mushola, dan papan pengumuman warga.</p>
</div>""",
    unsafe_allow_html=True,
)

qr_col1, qr_col2 = st.columns([1.6, 1.0])
with qr_col1:
    with st.container(border=True):
        app_public_url = st.text_input(
            "🔗 Alamat URL Publik Aplikasi (Streamlit Sharing):",
            value="https://sipaldo-pagentan.streamlit.app",
            help="URL resmi aplikasi SIPALDO-PAGENTAN yang tertanam di dalam QR Code warga.",
        )
        st.markdown(
            """
            **Cara Penggunaan oleh Warga Desa Pagentan:**
            1. Buka kamera HP atau pemindai QR di smartphone.
            2. Arahkan ke **QR Code SIPALDO-PAGENTAN** di papan Pos Ronda dusun atau Balai Desa.
            3. Tanpa perlu login atau instal aplikasi, warga langsung melihat status **Aman / Waspada / Siaga** beserta peta blok rawan seluruh 5 dusun secara real-time.
            """
        )
        qr_bytes = generate_village_qr_png(app_public_url)
        st.download_button(
            label="⬇️ Unduh Gambar QR Code Siap Cetak (PNG)",
            data=qr_bytes,
            file_name="QR_SIPALDO_PAGENTAN.png",
            mime="image/png",
            width="stretch",
        )

        st.divider()
        st.markdown("#### 👵 QR Code Tampilan Mudah untuk Lansia")
        st.caption(
            "QR ini membuka halaman sangat sederhana: satu status besar, tiga angka, "
            "tiga langkah, dan tombol telepon 112. Cocok ditempel di rumah lansia, posyandu, dan masjid."
        )
        _lansia_url = f"{app_public_url.rstrip('/')}/?mode=mudah"
        _lansia_qr = generate_village_qr_png(
            _lansia_url,
            judul="TAMPILAN MUDAH UNTUK LANSIA",
            subjudul="SIPALDO-PAGENTAN - DESA PAGENTAN",
            label="HURUF BESAR & RINGKAS",
        )
        _lq1, _lq2 = st.columns([1, 1])
        with _lq1:
            st.image(_lansia_qr, width="stretch")
        with _lq2:
            st.markdown(
                f"**Untuk warga lansia**  \n"
                f"Tautan: `{_lansia_url}`  \n\n"
                "Hanya menampilkan: **AMAN / HATI-HATI / BAHAYA**, tiga angka penting, dan tiga langkah singkat."
            )
            st.download_button(
                "⬇️ Unduh QR Lansia (PNG)",
                data=_lansia_qr,
                file_name="QR_SIPALDO_TAMPILAN_LANSIA.png",
                mime="image/png",
                width="stretch",
            )

        st.divider()
        st.markdown("#### 🏠 QR Code Khusus per Pos Ronda")
        st.caption(
            "Setiap pos ronda mendapat QR sendiri. Saat petugas memindainya, aplikasi otomatis "
            "menyorot dusun tersebut dan membuka bagian checklist patroli."
        )
        _pos_pilih = st.selectbox("Pilih Pos Ronda / Dusun:", DUSUN_POS, key="qr_pos_pilih")
        _pos_slug = DUSUN_SLUG.get(_pos_pilih, "pagentan")
        _pos_url = f"{app_public_url.rstrip('/')}/?pos={_pos_slug}"
        _pos_qr = generate_village_qr_png(
            _pos_url,
            judul=f"POS RONDA DUSUN {_pos_pilih.split(' (')[0].replace('Dusun ', '').upper()}",
            subjudul="SIPALDO-PAGENTAN - DESA PAGENTAN",
            label=_pos_pilih.split("(")[-1].rstrip(")") if "(" in _pos_pilih else "",
        )
        _q1, _q2 = st.columns([1, 1])
        with _q1:
            st.image(_pos_qr, width="stretch")
        with _q2:
            st.markdown(
                f"**{_pos_pilih}**  \n"
                f"Tautan QR: `{_pos_url}`  \n\n"
                "Tempel kartu ini di dinding Pos Ronda, lalu petugas cukup memindai "
                "untuk mencatat hasil patroli malam."
            )
            st.caption("Kode pos: `" + _pos_slug + "` • QR sudah berisi label dusun & RW.")
            st.download_button(
                "⬇️ Unduh QR Pos Ronda (PNG)",
                data=_pos_qr,
                file_name=f"QR_POS_RONDA_{_pos_slug.replace(' ', '_').upper()}.png",
                mime="image/png",
                width="stretch",
            )

with qr_col2:
    with st.container(border=True):
        st.image(qr_bytes, width="stretch")
        st.markdown(
            "<div style='text-align:center; font-size:0.86rem; color:#475569;'>"
            "<b>SIPALDO-PAGENTAN</b> • Kab. Banjarnegara<br>"
            "https://sipaldo-pagentan.streamlit.app</div>",
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# 10. FOOTER RESMI DESA
# -----------------------------------------------------------------------------
st.markdown(
    """
<div style="margin-top:32px; padding:18px; border-radius:14px; background:#0F172A; color:#CBD5E1; text-align:center; font-size:0.9rem;">
<b style="color:#FFFFFF;">SIPALDO-PAGENTAN — Sistem Peringatan Dini Longsor Desa Pagentan</b><br>
Melayani Seluruh Wilayah Dusun Krajan 1, Krajan 2, Bulu, Sawangan, &amp; Tedunan • Kec. Pagentan, Kab. Banjarnegara, Jawa Tengah<br>
<span style="font-size:0.82rem; color:#94A3B8;">
Koordinat Pusat (Balai Desa): -7.30043, 109.80995 • Sumber Cuaca: Open-Meteo API (Real-Time) • Peta Dasar: © OpenStreetMap Contributors
</span>
</div>
""",
    unsafe_allow_html=True,
)
