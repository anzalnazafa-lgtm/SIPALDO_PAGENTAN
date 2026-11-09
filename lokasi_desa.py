"""
DATA TITIK PENTING DESA PAGENTAN (satu sumber kebenaran / single source of truth).

STATUS AKURASI:
  ✅ "terverifikasi" : koordinat diberikan langsung oleh perangkat desa (survey GPS/Google Maps).
  ⚠️ "estimasi"      : belum disurvei lapangan. SAAT INI TIDAK ADA titik estimasi di peta —
                       titik pantau lereng, pantau drainase, dan pos ronda sudah dihapus.

Koordinat terverifikasi yang dipakai (input perangkat desa, November 2026):
  • Balai Desa Pagentan        -7.300433, 109.809946  → PUSAT DESA
  • Kantor Kecamatan Pagentan  -7.301041, 109.810175
  • Puskesmas Pagentan 1       -7.300635, 109.810107
  • Lapangan Rawa Sakti        -7.298135, 109.810761
  • SMP Negeri 1 Pagentan      -7.298747, 109.810458
  • MI Muhammadiyah Pagentan   -7.302191, 109.810094
  • SDN 1 Pagentan             -7.304172, 109.809849
  • Masjid Baitul Makmur       -7.302351, 109.810019
  • Masjid Baitul'nangim       -7.310211, 109.812041
  • Masjid Al Ikhlas           -7.306455, 109.801653
  • MI GUPPI Pagentan          -7.306774, 109.801244
  • Masjid An Nur              -7.306621, 109.800307

Catatan: titik pantau lereng, pantau drainase, dan pos ronda SUDAH DIHAPUS dari peta
karena belum memiliki koordinat resmi (sebelumnya hanya estimasi). Garis alur sungai &
garis tebing tetap ditampilkan sebagai ilustrasi medan untuk pewarnaan grid, bukan patokan titik.

Cara memperbarui: menu **🔧 Kalibrasi Titik Lokasi** di aplikasi, atau edit langsung
koordinat pada TITIK_LOKAL di berkas ini.
"""

from __future__ import annotations

# Pusat Desa Pagentan = Balai Desa Pagentan (koordinat terverifikasi)
PUSAT_DESA = [-7.300433, 109.809946]

# Bounding box wilayah Desa Pagentan (±1,1 km dari Balai Desa)
LAT_NORTH = -7.2932
LAT_SOUTH = -7.3110
LON_WEST = 109.8010
LON_EAST = 109.8190

LAPORAN_VERIFIKASI = (
    "Seluruh titik pada peta saat ini **terverifikasi** memakai koordinat resmi perangkat desa. "
    "Titik pantau lereng, pantau drainase, dan pos ronda sudah dihapus karena belum ada "
    "koordinat resminya. Bila nanti sudah ada patokannya, tambahkan lewat menu "
    "**🔧 Kalibrasi Titik Lokasi** (GPS HP) atau kirim koordinatnya untuk ditanam permanen."
)

# kategori_layer: "vital" = fasilitas komando/evakuasi & titik pantau bahaya
#                 "fasum" = sekolah, masjid, kantor (bisa disembunyikan di peta)
TITIK_LOKAL = [
    # ---------------------------------------------------------------- VITAL ---
    {
        "name": "Balai Desa Pagentan",
        "dusun": "Dusun Krajan 1 (RW 01–02)",
        "category": "Pusat Komando Desa",
        "coords": [-7.300433, 109.809946],
        "color": "blue",
        "icon": "home",
        "desc": "Pusat pemerintahan Desa Pagentan & komando utama peringatan dini longsor.",
        "info": "Pos Komando Utama Desa Pagentan",
        "sumber": "terverifikasi",
        "kategori_layer": "vital",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Lapangan Rawa Sakti (Titik Kumpul Warga)",
        "dusun": "Dusun Krajan 1",
        "category": "Area Evakuasi Terbuka",
        "coords": [-7.298135, 109.810761],
        "color": "darkgreen",
        "icon": "flag",
        "desc": "Lapangan desa di utara kompleks pemerintahan. Area terbuka & datar untuk titik kumpul warga.",
        "info": "Titik Kumpul Terbuka Warga",
        "sumber": "terverifikasi",
        "kategori_layer": "vital",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Puskesmas Pagentan 1",
        "dusun": "Dusun Krajan 1 (Jalur Utama)",
        "category": "Fasilitas Kesehatan Darurat",
        "coords": [-7.300635, 109.810107],
        "color": "cadetblue",
        "icon": "heart",
        "desc": "Rujukan pertolongan pertama medis & evakuasi kelompok rentan (lansia, ibu hamil, balita).",
        "info": "Rujukan Medis Kedaruratan Desa",
        "sumber": "terverifikasi",
        "kategori_layer": "vital",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    # ---------------------------------------------------------------- FASUM ---
    {
        "name": "Kantor Kecamatan Pagentan",
        "dusun": "Dusun Krajan 1",
        "category": "Pemerintahan Kecamatan",
        "coords": [-7.301041, 109.810175],
        "color": "darkblue",
        "icon": "tower",
        "desc": "Kantor Kecamatan Pagentan — koordinasi lintas desa & dukungan sumber daya saat bencana.",
        "info": "Koordinasi Kecamatan",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "SMP Negeri 1 Pagentan",
        "dusun": "Dusun Krajan 1",
        "category": "Fasilitas Pendidikan",
        "coords": [-7.298747, 109.810458],
        "color": "lightblue",
        "icon": "education",
        "desc": "Sekolah menengah di utara kompleks pemerintahan desa; dapat dipakai sebagai lokasi pengungsian sementara.",
        "info": "Alternatif Titik Kumpul Warga",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "SDN 1 Pagentan",
        "dusun": "Dusun Krajan 2",
        "category": "Fasilitas Pendidikan",
        "coords": [-7.304172, 109.809849],
        "color": "lightblue",
        "icon": "education",
        "desc": "Sekolah dasar di sisi selatan jalur utama desa; titik kumpul alternatif warga Krajan/Sawangan.",
        "info": "Alternatif Titik Kumpul Warga",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "MI Muhammadiyah Pagentan",
        "dusun": "Dusun Krajan 2",
        "category": "Fasilitas Pendidikan",
        "coords": [-7.302191, 109.810094],
        "color": "lightblue",
        "icon": "education",
        "desc": "Madrasah ibtidaiyah di jalur tengah desa.",
        "info": "Fasilitas Pendidikan",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "MI GUPPI Pagentan",
        "dusun": "Dusun Sawangan (RW 07)",
        "category": "Fasilitas Pendidikan",
        "coords": [-7.306774, 109.801244],
        "color": "lightblue",
        "icon": "education",
        "desc": "Madrasah di sisi barat–selatan desa (koridor Kaliglagah/Kalipinggan).",
        "info": "Fasilitas Pendidikan",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Masjid Baitul Makmur",
        "dusun": "Dusun Krajan 2",
        "category": "Tempat Ibadah & Titik Kumpul",
        "coords": [-7.302351, 109.810019],
        "color": "lightgreen",
        "icon": "star",
        "desc": "Masjid di jalur tengah desa; biasa dipakai warga berkumpul & pengeras suara untuk pengumuman darurat.",
        "info": "Pengumuman Darurat via Pengeras Suara",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Masjid Baitul'nangim",
        "dusun": "Dusun Sawangan (RW 07)",
        "category": "Tempat Ibadah & Titik Kumpul",
        "coords": [-7.310211, 109.812041],
        "color": "lightgreen",
        "icon": "star",
        "desc": "Masjid di sisi selatan desa dekat kawasan lembah sungai Sawangan.",
        "info": "Pengumuman Darurat via Pengeras Suara",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Masjid Al Ikhlas",
        "dusun": "Dusun Sawangan (RW 07)",
        "category": "Tempat Ibadah & Titik Kumpul",
        "coords": [-7.306455, 109.801653],
        "color": "lightgreen",
        "icon": "star",
        "desc": "Masjid di sisi barat–selatan desa.",
        "info": "Pengumuman Darurat via Pengeras Suara",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
    {
        "name": "Masjid An Nur",
        "dusun": "Dusun Sawangan (RW 07)",
        "category": "Tempat Ibadah & Titik Kumpul",
        "coords": [-7.306621, 109.800307],
        "color": "lightgreen",
        "icon": "star",
        "desc": "Masjid paling barat di koridor Sawangan–Kaliglagah.",
        "info": "Pengumuman Darurat via Pengeras Suara",
        "sumber": "terverifikasi",
        "kategori_layer": "fasum",
        "aman": True,
        "catatan": "Koordinat terverifikasi dari perangkat desa.",
    },
]


def get_titik_lokal(overrides: dict | None = None) -> list[dict]:
    """
    Kembalikan daftar titik lokal, dengan penimpaan koordinat hasil kalibrasi petugas.

    `overrides` = {"Nama Titik": {"lat": ..., "lon": ..., "sumber": "terverifikasi", "catatan": "..."}}
    """
    titik = []
    for item in TITIK_LOKAL:
        entri = dict(item)
        entri["coords"] = list(item["coords"])
        ov = (overrides or {}).get(item["name"])
        if ov and ov.get("lat") is not None and ov.get("lon") is not None:
            entri["coords"] = [float(ov["lat"]), float(ov["lon"])]
            entri["sumber"] = ov.get("sumber", "terverifikasi")
            entri["catatan"] = ov.get("catatan", "Koordinat sudah dikalibrasi oleh petugas desa.")
        titik.append(entri)
    return titik


def titik_aman(overrides: dict | None = None) -> list[dict]:
    """Hanya titik yang layak dijadikan tujuan evakuasi (Balai Desa, lapangan, sekolah, masjid, dll.)."""
    return [t for t in get_titik_lokal(overrides) if t.get("aman")]
