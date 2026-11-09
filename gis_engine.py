"""
Mesin WebGIS Desa Pagentan berbasis Folium & Leaflet.js (OpenStreetMap).
Memodelkan poligon grid kerawanan longsor mencakup seluruh 5 Dusun di Desa Pagentan
(Dusun Krajan 1, Dusun Krajan 2, Dusun Bulu, Dusun Sawangan, dan Dusun Tedunan)
pada Bounding Box Desa Pagentan:
Lat: -7.2960 s.d. -7.3160 | Lon: 109.7990 s.d. 109.8200
Pusat Koordinat Desa (Balai Desa Pagentan): -7.30583, 109.80944
"""

from __future__ import annotations

import math
import folium

# =============================================================================
# KONSTANTA SPASIAL RESMI DESA PAGENTAN (Kode Kemendagri: 33.04.14.2012)
# Pusat Desa: -7.30583, 109.80944  (7°18'21"S 109°48'34"E)
# Berada di Kec. Pagentan, Kab. Banjarnegara — berbatasan dengan
# Desa Plumbungan & Metawana (barat), Kalipinggan & Kalitlaga (selatan-barat),
# Buluslawang & Tedungan (timur), Kasmaran (utara).
# =============================================================================
MAP_CENTER = [-7.30583, 109.80944]

# Bounding Box wilayah Desa Pagentan (±1,2 km dari pusat desa)
LAT_NORTH = -7.2960
LAT_SOUTH = -7.3160
LON_WEST = 109.7990
LON_EAST = 109.8200

# Alur Sungai Utama: Kali Putih / saluran lereng Gunung Putih–Pagentan,
# melintasi Dusun Krajan 1 ke selatan menuju Dusun Sawangan.
RIVER_PATH = [
    [-7.2966, 109.8006],
    [-7.2998, 109.8036],
    [-7.3028, 109.8064],
    [-7.3058, 109.8092],
    [-7.3088, 109.8122],
    [-7.3120, 109.8154],
    [-7.3152, 109.8182],
]

# Garis Punggung Tebing Curam: gawir perbukitan utara (Bulu/Kasmaran)
# memanjang ke timur laut menuju jalur turunan Tedunan.
NORTH_CLIFF_LINE = [
    [-7.2972, 109.7992],
    [-7.2978, 109.8036],
    [-7.2988, 109.8080],
    [-7.3002, 109.8126],
    [-7.3020, 109.8170],
]

# Rute Evakuasi Warga Seluruh Dusun Menuju Balai Desa, Lapangan & Posko
EVACUATION_ROUTES = [
    # Dusun Bulu (utara) -> Pos Ronda Utara -> Balai Desa Pagentan
    [[-7.2996, 109.8062], [-7.3032, 109.8078], [-7.30583, 109.80944]],
    # Dusun Tedunan (timur) -> Pos Ronda Timur -> Posko Kebencanaan Desa
    [[-7.3042, 109.8154], [-7.3048, 109.8120], [-7.3045, 109.8106]],
    # Balai Desa (Krajan 1) <-> Posko Kebencanaan (Krajan 2)
    [[-7.30583, 109.80944], [-7.3045, 109.8106]],
    # Dusun Sawangan (selatan) -> Lapangan Desa -> Balai Desa
    [[-7.3112, 109.8126], [-7.3102, 109.8100], [-7.3080, 109.8096], [-7.30583, 109.80944]],
]

# Lokasi Pin (Marker) Lokal Mencakup Seluruh Wilayah Desa Pagentan (5 Dusun, RW 01 - RW 08)
VITAL_LOCATIONS = [
    {
        "name": "Balai Desa Pagentan (Dusun Krajan 1)",
        "dusun": "Dusun Krajan 1 (RW 01–02)",
        "category": "Pusat Komando Desa",
        "coords": [-7.30583, 109.80944],
        "color": "blue",
        "icon": "home",
        "desc": "Jl. Raya Pagentan – Banjarnegara. Pusat pemerintahan Desa Pagentan & komando utama peringatan dini.",
        "info": "Pos Komando Utama Desa Pagentan",
    },
    {
        "name": "Posko Kebencanaan Desa (Dusun Krajan 2)",
        "dusun": "Dusun Krajan 2 (RW 03–04)",
        "category": "Titik Evakuasi & Logistik",
        "coords": [-7.3045, 109.8106],
        "color": "green",
        "icon": "plus-sign",
        "desc": "Lokasi pengungsian utama warga lintas dusun, dapur umum darurat, P3K, dan gudang logistik bencana.",
        "info": "Siaga Penuh 24 Jam saat Darurat",
    },
    {
        "name": "Titik Kumpul Aman Lapangan Desa",
        "dusun": "Dusun Krajan 1 / Krajan 2",
        "category": "Area Evakuasi Terbuka",
        "coords": [-7.3078, 109.8080],
        "color": "darkgreen",
        "icon": "flag",
        "desc": "Area terbuka datar di jantung Desa Pagentan yang aman dari jangkauan mahkota tebing maupun alur sungai.",
        "info": "Titik Kumpul Terbuka Warga",
    },
    {
        "name": "Layanan Medis / Puskesmas Pagentan",
        "dusun": "Dusun Krajan 1 (Jalur Utama)",
        "category": "Fasilitas Kesehatan Darurat",
        "coords": [-7.3064, 109.8072],
        "color": "cadetblue",
        "icon": "heart",
        "desc": "Titik rujukan pertolongan pertama medis & evakuasi kelompok rentan (lansia, ibu hamil, balita).",
        "info": "Rujukan Medis Kedaruratan Desa",
    },
    {
        "name": "Titik Pantau Lereng Dusun Bulu (RW 05–06)",
        "dusun": "Dusun Bulu (RW 05–06)",
        "category": "Pantauan Tebing Kritis",
        "coords": [-7.2996, 109.8062],
        "color": "red",
        "icon": "warning-sign",
        "desc": "Zona gawir perbukitan terjal sisi utara Desa Pagentan (>35°, arah Gunung Putih). Fokus pantauan retakan tanah podsolik.",
        "info": "Jauhi Bawah Tebing Saat Hujan >50 mm",
    },
    {
        "name": "Titik Pantau Lereng Dusun Sawangan (RW 07)",
        "dusun": "Dusun Sawangan (RW 07)",
        "category": "Pantauan Sungai & Rawa Tebing",
        "coords": [-7.3112, 109.8126],
        "color": "orange",
        "icon": "eye-open",
        "desc": "Zona pertemuan alur sungai & cekungan rawa lereng Dusun Sawangan. Rawan gerusan kaki tebing & lumpur.",
        "info": "Pantau Debit & Kekeruhan Air Sungai",
    },
    {
        "name": "Titik Pantau Lereng Dusun Tedunan (RW 08)",
        "dusun": "Dusun Tedunan (RW 08)",
        "category": "Pantauan Tebing & Turunan",
        "coords": [-7.3042, 109.8154],
        "color": "red",
        "icon": "warning-sign",
        "desc": "Jalur kelerengan menurun curam sisi timur Desa Pagentan (arah Tedungan) dengan lapisan tanah pelapukan tebal.",
        "info": "Waspada Longsoran Tebing Jalan",
    },
    {
        "name": "Titik Pantau Drainase Lereng Krajan 2 (RW 03–04)",
        "dusun": "Dusun Krajan 2 (RW 03–04)",
        "category": "Pantauan Drainase & Lembah",
        "coords": [-7.3084, 109.8122],
        "color": "orange",
        "icon": "tint",
        "desc": "Titik pantau limpasan selokan/gorong-gorong permukiman yang mengarah ke bibir lembah sungai desa.",
        "info": "Pastikan Selokan Tidak Tersumbat",
    },
    {
        "name": "Pos Ronda Siaga Sektor Utara–Barat (Bulu & Krajan 1)",
        "dusun": "Dusun Bulu / Dusun Krajan 1",
        "category": "Pos Ronda & Kentongan",
        "coords": [-7.3032, 109.8078],
        "color": "purple",
        "icon": "bell",
        "desc": "Pos jaga warga dilengkapi kentongan tanda bahaya & papan QR Code SIPALDO-PAGENTAN.",
        "info": "Ronda Malam Bergilir RT/RW",
    },
    {
        "name": "Pos Ronda Siaga Sektor Selatan–Timur (Sawangan & Tedunan)",
        "dusun": "Dusun Sawangan / Dusun Tedunan",
        "category": "Pos Ronda & Kentongan",
        "coords": [-7.3102, 109.8100],
        "color": "purple",
        "icon": "bell",
        "desc": "Pos pemantauan warga untuk peringatan dini kawasan lembah sungai Sawangan & lereng Tedunan.",
        "info": "Ronda Malam Bergilir RT/RW",
    },
]


def resolve_dusun_sector(center_lat: float, center_lon: float) -> str:
    """
    Memetakan koordinat sel grid ke sektor wilayah 5 Dusun resmi di Desa Pagentan:
    - Dusun Bulu (RW 05–06)     : Sektor perbukitan utara & barat laut
    - Dusun Tedunan (RW 08)     : Sektor kelerengan timur & timur laut
    - Dusun Krajan 1 (RW 01–02) : Sektor tengah–barat (pusat Balai Desa & jalur utama)
    - Dusun Krajan 2 (RW 03–04) : Sektor tengah–timur permukiman desa
    - Dusun Sawangan (RW 07)    : Sektor selatan & lembah pertemuan alur sungai
    """
    # Zona Utara (perbukitan Bulu) — lat lebih tinggi dari -7.3030
    if center_lat >= -7.3030:
        if center_lon <= 109.8105:
            return "Dusun Bulu (RW 05–06)"
        return "Dusun Tedunan (RW 08)"
    # Zona Selatan (lembah & alur sungai Sawangan) — lat lebih rendah dari -7.3090
    if center_lat <= -7.3090:
        if center_lon >= 109.8070:
            return "Dusun Sawangan (RW 07)"
        return "Dusun Krajan 1 (RW 01–02)"
    # Koridor tengah desa (-7.3030 s.d. -7.3090)
    if center_lon > 109.8145:
        return "Dusun Tedunan (RW 08)"
    if center_lon <= 109.8078:
        return "Dusun Krajan 1 (RW 01–02)"
    return "Dusun Krajan 2 (RW 03–04)"


def _min_dist_to_polyline(lat: float, lon: float, polyline: list[list[float]]) -> float:
    """Hitung jarak terdekat titik pusat sel ke segmen garis sungai/tebing."""
    best = 999.0
    for i in range(len(polyline) - 1):
        y1, x1 = polyline[i]
        y2, x2 = polyline[i + 1]
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            d = math.hypot(lat - y1, lon - x1)
        else:
            t = max(0.0, min(1.0, ((lon - x1) * dx + (lat - y1) * dy) / (dx * dx + dy * dy)))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            d = math.hypot(lat - proj_y, lon - proj_x)
        if d < best:
            best = d
    return best


def evaluate_cell_morphology(center_lat: float, center_lon: float) -> dict:
    """
    Klasifikasi kerentanan morfologi dasar setiap sel poligon (tanah podsolik pegunungan Pagentan)
    berdasarkan jarak ke alur sungai/rawa lereng, gawir tebing curam, dan dataran pusat desa.
    """
    dist_river = _min_dist_to_polyline(center_lat, center_lon, RIVER_PATH)
    dist_cliff = _min_dist_to_polyline(center_lat, center_lon, NORTH_CLIFF_LINE)
    dist_village_center = math.hypot(center_lat - MAP_CENTER[0], center_lon - MAP_CENTER[1])

    # Area inti sekitar Balai Desa, Posko & Lapangan merupakan punggung stabil
    if dist_village_center <= 0.0030 and dist_river > 0.0018:
        return {
            "zone_code": "ZONA_STABIL",
            "zone_name": "Dataran Punggung Desa (Stabil)",
            "slope_deg": "5° – 12°",
            "terrain_desc": "Area permukiman inti & titik kumpul evakuasi aman",
        }

    # Fokus zona rawa/lereng kritis di area tebing utara & koridor alur sungai desa
    if dist_cliff <= 0.0017 and dist_river <= 0.0025:
        return {
            "zone_code": "INTI_JURANG_SUNGAI",
            "zone_name": "Inti Jurang Tebing & Rawa Sungai",
            "slope_deg": "> 40° (Sangat Terjal)",
            "terrain_desc": "Pertemuan gawir terjal & lembah rawa sungai tanah podsolik",
        }

    if dist_cliff <= 0.0018:
        return {
            "zone_code": "KRITIS_TEBING",
            "zone_name": "Zona Tebing Curam Desa",
            "slope_deg": "> 35° (Curam)",
            "terrain_desc": "Gawir perbukitan terjal rawan longsoran tebing",
        }

    if dist_river <= 0.0016:
        return {
            "zone_code": "KRITIS_SUNGAI_RAWA",
            "zone_name": "Zona Alur Sungai & Rawa Lereng",
            "slope_deg": "28° – 40°",
            "terrain_desc": "Cekungan jenuh air/rembesan rawa tebing & bantaran sungai",
        }

    # Zona transisi lereng perbukitan sedang
    if dist_cliff <= 0.0038 or dist_river <= 0.0036 or (center_lon > 109.8130 and center_lat > -7.3060):
        return {
            "zone_code": "LERENG_SEDANG",
            "zone_name": "Lereng Perbukitan Sedang",
            "slope_deg": "16° – 28°",
            "terrain_desc": "Lereng kebun/permukiman miring yang sensitif kejenuhan air",
        }

    return {
        "zone_code": "ZONA_STABIL",
        "zone_name": "Area Landai / Stabil",
        "slope_deg": "8° – 15°",
        "terrain_desc": "Lereng landai dengan risiko gerakan tanah rendah",
    }


def _resolve_cell_style(zone_code: str, risk_level: str) -> dict:
    """
    Tentukan warna & status sel poligon secara dinamis sesuai akumulasi hujan real-time:
    - AMAN    : Zona risiko standar (dominan hijau aman)
    - WASPADA : Sebagian besar grid (tebing, sungai, lereng sedang) naik menjadi kuning/amber
    - SIAGA   : Seluruh grid lereng kritis (tebing & sungai/rawa) menyala MERAH DARURAT
    """
    is_core_gorge = zone_code == "INTI_JURANG_SUNGAI"
    is_critical_terrain = zone_code in ("INTI_JURANG_SUNGAI", "KRITIS_TEBING", "KRITIS_SUNGAI_RAWA")
    is_moderate_terrain = zone_code == "LERENG_SEDANG"

    if risk_level == "SIAGA":
        if is_critical_terrain:
            return {
                "status_sel": "BAHAYA / SIAGA MERAH",
                "fill_color": "#DC2626",
                "border_color": "#991B1B",
                "fill_opacity": 0.62,
                "weight": 1.8,
                "bucket": "merah",
                "advice": "DILARANG MELINTAS / BERADA DI ZONA INI! Segera menjauh ke titik kumpul aman.",
            }
        if is_moderate_terrain:
            return {
                "status_sel": "WASPADA TINGGI (PENYANGGA)",
                "fill_color": "#F59E0B",
                "border_color": "#B45309",
                "fill_opacity": 0.45,
                "weight": 1.2,
                "bucket": "kuning",
                "advice": "Siaga evakuasi mandiri jika terdengar gemuruh atau muncul aliran lumpur.",
            }
        return {
            "status_sel": "ZONA AMAN / EVAKUASI",
            "fill_color": "#16A34A",
            "border_color": "#15803D",
            "fill_opacity": 0.22,
            "weight": 0.8,
            "bucket": "hijau",
            "advice": "Zona relatif stabil untuk jalur penyelamatan menuju Posko Desa.",
        }

    if risk_level == "WASPADA":
        if is_critical_terrain:
            return {
                "status_sel": "WASPADA UTAMA (JENUH AIR)",
                "fill_color": "#F59E0B",
                "border_color": "#D97706",
                "fill_opacity": 0.52,
                "weight": 1.4,
                "bucket": "kuning",
                "advice": "Tanah tebing/bantaran sungai mulai jenuh air. Hindari aktivitas di bawah tebing saat hujan.",
            }
        if is_moderate_terrain:
            return {
                "status_sel": "WASPADA LERENG",
                "fill_color": "#FACC15",
                "border_color": "#CA8A04",
                "fill_opacity": 0.40,
                "weight": 1.0,
                "bucket": "kuning",
                "advice": "Periksa aliran selokan dan waspadai retakan tanah di halaman/kebun.",
            }
        return {
            "status_sel": "AMAN",
            "fill_color": "#22C55E",
            "border_color": "#16A34A",
            "fill_opacity": 0.18,
            "weight": 0.7,
            "bucket": "hijau",
            "advice": "Kondisi stabil, tetap pantau informasi cuaca desa.",
        }

    # Mode AMAN (< 20 mm): Peta menampilkan zona risiko standar
    if is_core_gorge:
        return {
            "status_sel": "PANTAUAN TEBING STANDAR",
            "fill_color": "#EAB308",
            "border_color": "#CA8A04",
            "fill_opacity": 0.28,
            "weight": 1.0,
            "bucket": "kuning",
            "advice": "Titik jurang/tebing curam alami. Kondisi aman saat hujan rendah, jaga vegetasi lereng.",
        }
    if is_critical_terrain:
        return {
            "status_sel": "AMAN (KORIDOR TEBING/SUNGAI)",
            "fill_color": "#65A30D",
            "border_color": "#4D7C0F",
            "fill_opacity": 0.24,
            "weight": 0.8,
            "bucket": "hijau",
            "advice": "Zona kelerengan tepi sungai/tebing dalam kondisi stabil (curah hujan rendah).",
        }
    return {
        "status_sel": "AMAN STANDAR",
        "fill_color": "#22C55E",
        "border_color": "#16A34A",
        "fill_opacity": 0.18,
        "weight": 0.6,
        "bucket": "hijau",
        "advice": "Kondisi aman untuk aktivitas harian warga Desa Pagentan.",
    }


def _build_map_impl(
    risk_level: str = "AMAN",
    show_grid: bool = True,
    show_hydrology: bool = True,
    show_evac_routes: bool = True,
    basemap_style: str = "OpenStreetMap",
    user_location: dict | None = None,
    radius_m: int = 250,
) -> tuple[folium.Map, dict, list[dict]]:
    """
    Membangun objek peta interaktif Folium lengkap beserta statistik grid
    dan ringkasan status per Dusun di seluruh Desa Pagentan.

    `user_location` = {"lat": ..., "lon": ..., "sumber": "GPS HP" | "Pilih manual",
    "label": ..., "akurasi_m": ...}. Bila diisi, peta otomatis memusat ke posisi
    warga, memasang pin "Lokasi Anda", lingkaran jangkauan, dan penanda
    titik lokal terdekat.
    """
    tiles_url = "OpenStreetMap"
    attr = None
    if basemap_style == "Topografi Perbukitan (OpenTopoMap)":
        tiles_url = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
        attr = "Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap"

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=15,
        min_zoom=12,
        max_zoom=18,
        tiles=tiles_url,
        attr=attr,
        control_scale=True,
    )

    # 1. Batas Bounding Box Wilayah Pemantauan Desa Pagentan
    folium.Rectangle(
        bounds=[[LAT_SOUTH, LON_WEST], [LAT_NORTH, LON_EAST]],
        color="#1E293B",
        weight=2,
        dash_array="6, 6",
        fill=False,
        tooltip="Batas Area Pemantauan Grid Seluruh Desa Pagentan",
    ).add_to(m)

    # 2. Bangun Matriks Poligon Grid 10x10 (100 Blok Spasial Lintas 5 Dusun)
    n_rows, n_cols = 10, 10
    lat_step = (LAT_NORTH - LAT_SOUTH) / n_rows  # +0.0020 derajat (~222 m)
    lon_step = (LON_EAST - LON_WEST) / n_cols    # +0.0020 derajat (~220 m)

    counts = {"merah": 0, "kuning": 0, "hijau": 0, "total": n_rows * n_cols}
    dusun_stats_map: dict[str, dict] = {
        "Dusun Krajan 1 (RW 01–02)": {"merah": 0, "kuning": 0, "hijau": 0, "total": 0},
        "Dusun Krajan 2 (RW 03–04)": {"merah": 0, "kuning": 0, "hijau": 0, "total": 0},
        "Dusun Bulu (RW 05–06)": {"merah": 0, "kuning": 0, "hijau": 0, "total": 0},
        "Dusun Sawangan (RW 07)": {"merah": 0, "kuning": 0, "hijau": 0, "total": 0},
        "Dusun Tedunan (RW 08)": {"merah": 0, "kuning": 0, "hijau": 0, "total": 0},
    }

    grid_group = folium.FeatureGroup(name="Grid Kerawanan Longsor (5 Dusun)", show=show_grid)

    for r in range(n_rows):
        row_south = LAT_NORTH - (r + 1) * lat_step
        row_north = LAT_NORTH - r * lat_step
        center_lat = (row_south + row_north) / 2.0
        row_letter = chr(65 + r)

        for c in range(n_cols):
            col_west = LON_WEST + c * lon_step
            col_east = col_west + lon_step
            center_lon = (col_west + col_east) / 2.0
            block_id = f"{row_letter}{c + 1}"

            dusun_name = resolve_dusun_sector(center_lat, center_lon)
            morph = evaluate_cell_morphology(center_lat, center_lon)
            style = _resolve_cell_style(morph["zone_code"], risk_level)

            counts[style["bucket"]] += 1
            dusun_stats_map[dusun_name][style["bucket"]] += 1
            dusun_stats_map[dusun_name]["total"] += 1

            popup_html = f"""
            <div style="font-family:sans-serif; min-width:230px; font-size:13px; line-height:1.45;">
                <div style="font-size:11px; font-weight:700; color:#475569; text-transform:uppercase;">
                    {dusun_name}
                </div>
                <div style="font-weight:800; font-size:14px; color:#0F172A; margin-bottom:4px;">
                    Blok Grid {block_id} — {morph['zone_name']}
                </div>
                <div style="display:inline-block; padding:2px 8px; border-radius:4px; color:#FFF;
                            background:{style['fill_color']}; font-weight:700; font-size:11px; margin-bottom:6px;">
                    {style['status_sel']}
                </div>
                <div><b>Kemiringan:</b> {morph['slope_deg']}</div>
                <div><b>Karakteristik:</b> {morph['terrain_desc']}</div>
                <div><b>Koordinat:</b> {center_lat:.4f}, {center_lon:.4f}</div>
                <hr style="margin:6px 0; border:none; border-top:1px solid #CBD5E1;">
                <div style="color:#1E293B;"><b>Arahan Warga:</b> {style['advice']}</div>
            </div>
            """

            folium.Rectangle(
                bounds=[[row_south, col_west], [row_north, col_east]],
                color=style["border_color"],
                weight=style["weight"],
                fill=True,
                fill_color=style["fill_color"],
                fill_opacity=style["fill_opacity"],
                tooltip=f"Blok {block_id} ({dusun_name.split(' (')[0]}) — {style['status_sel']}",
                popup=folium.Popup(popup_html, max_width=290),
            ).add_to(grid_group)

    grid_group.add_to(m)

    # 3. Koridor Alur Sungai & Garis Bibir Tebing Curam
    if show_hydrology:
        hydro_group = folium.FeatureGroup(name="Alur Sungai & Bibir Tebing", show=True)
        folium.PolyLine(
            locations=RIVER_PATH,
            color="#0284C7",
            weight=4,
            opacity=0.85,
            tooltip="Alur Sungai & Lembah Rawa Lereng (Bulu – Krajan – Sawangan)",
        ).add_to(hydro_group)

        folium.PolyLine(
            locations=NORTH_CLIFF_LINE,
            color="#991B1B" if risk_level == "SIAGA" else "#B45309",
            weight=3.5,
            dash_array="8, 5",
            opacity=0.9,
            tooltip="Garis Mahkota Tebing Curam (Dusun Bulu & Dusun Tedunan)",
        ).add_to(hydro_group)
        hydro_group.add_to(m)

    # 4. Rute Jalur Evakuasi Aman & Lingkaran Radius Posko
    if show_evac_routes:
        evac_group = folium.FeatureGroup(name="Jalur Evakuasi Lintas Dusun", show=True)
        for route in EVACUATION_ROUTES:
            folium.PolyLine(
                locations=route,
                color="#15803D",
                weight=4,
                dash_array="5, 7",
                opacity=0.9,
                tooltip="Jalur Evakuasi Warga Menuju Balai Desa / Lapangan / Posko Aman",
            ).add_to(evac_group)

        if risk_level in ("WASPADA", "SIAGA"):
            folium.Circle(
                location=[-7.3284, 109.7728],
                radius=110,
                color="#16A34A",
                weight=2,
                fill=True,
                fill_color="#22C55E",
                fill_opacity=0.25,
                tooltip="Zona Radius Aman Posko Kebencanaan Desa (Krajan 2)",
            ).add_to(evac_group)
        evac_group.add_to(m)

    # 5. Marker (Pin) Lokasi Penting Seluruh Desa Pagentan (10 Titik Lokal)
    marker_group = folium.FeatureGroup(name="Titik Penting Seluruh Desa Pagentan", show=True)
    for loc in VITAL_LOCATIONS:
        pin_html = f"""
        <div style="font-family:sans-serif; min-width:225px; font-size:13px; line-height:1.45;">
            <div style="font-size:11px; font-weight:700; color:#15803D; text-transform:uppercase;">
                {loc['dusun']} • {loc['category']}
            </div>
            <div style="font-size:15px; font-weight:800; color:#0F172A; margin:2px 0 6px 0;">
                {loc['name']}
            </div>
            <div style="margin-bottom:6px; color:#334155;">{loc['desc']}</div>
            <div style="background:#F1F5F9; padding:5px 8px; border-radius:6px; font-size:12px;">
                <b>Keterangan:</b> {loc['info']}<br>
                <b>Koordinat:</b> {loc['coords'][0]:.4f}, {loc['coords'][1]:.4f}
            </div>
        </div>
        """
        folium.Marker(
            location=loc["coords"],
            tooltip=f"📍 {loc['name']}",
            popup=folium.Popup(pin_html, max_width=280),
            icon=folium.Icon(color=loc["color"], icon=loc["icon"]),
        ).add_to(marker_group)

    marker_group.add_to(m)

    # 6. Penanda Posisi Real-Time Warga (GPS HP) + Lingkaran Jangkauan
    if user_location and user_location.get("lat") is not None:
        u_lat = float(user_location["lat"])
        u_lon = float(user_location["lon"])
        sumber = user_location.get("sumber", "GPS HP")
        akurasi = user_location.get("akurasi_m")
        di_desa = is_inside_pagentan(u_lat, u_lon)
        posisi = describe_user_position(u_lat, u_lon)
        terdekat = posisi["titik_terdekat"] or {}
        evac_lat, evac_lon = (terdekat.get("coords") or MAP_CENTER)

        user_group = folium.FeatureGroup(name="Lokasi Anda (Real-Time)", show=True)

        folium.Circle(
            location=[u_lat, u_lon],
            radius=int(radius_m),
            color="#2563EB",
            weight=2,
            dash_array="6, 6",
            fill=True,
            fill_color="#3B82F6",
            fill_opacity=0.10,
            tooltip=f"Radius pantau sekitar posisi Anda (±{radius_m} m)",
        ).add_to(user_group)

        folium.CircleMarker(
            location=[u_lat, u_lon],
            radius=9,
            color="#1D4ED8",
            weight=3,
            fill=True,
            fill_color="#3B82F6",
            fill_opacity=1.0,
            tooltip="📍 LOKASI ANDA SEKARANG",
        ).add_to(user_group)

        if terdekat.get("coords"):
            folium.PolyLine(
                locations=[[u_lat, u_lon], [evac_lat, evac_lon]],
                color="#1D4ED8",
                weight=2.5,
                dash_array="4, 6",
                opacity=0.85,
                tooltip=f"Jalur terdekat menuju {terdekat.get('name', 'titik aman')} ({terdekat.get('jarak_m', 0)} m)",
            ).add_to(user_group)

        home_popup = f"""
        <div style="font-family:sans-serif; min-width:235px; font-size:13px; line-height:1.45;">
            <div style="font-size:11px; font-weight:800; color:#1D4ED8; text-transform:uppercase;">
                Posisi Anda ({sumber})
            </div>
            <div style="font-weight:800; font-size:14.5px; color:#0F172A; margin-bottom:5px;">
                {posisi['dusun']}
            </div>
            <div style="display:inline-block; padding:2px 8px; border-radius:4px; color:#FFF; background:#2563EB;
                        font-weight:700; font-size:11px; margin-bottom:6px;">
                {posisi['zone_name']} • {posisi['slope_deg']}
            </div>
            <div><b>Koordinat:</b> {u_lat:.5f}, {u_lon:.5f}</div>
            {f'<div><b>Akurasi GPS:</b> ±{akurasi} m</div>' if akurasi else ''}
            <div><b>Jarak ke Balai Desa:</b> {posisi['jarak_ke_balai_m']:.0f} m</div>
            <hr style="margin:6px 0; border:none; border-top:1px solid #CBD5E1;">
            <div><b>Karakter lahan di lokasi Anda:</b> {posisi['terrain_desc']}</div>
            <div style="color:#1E293B; margin-top:4px;"><b>Arahan:</b> {posisi['arahan']}</div>
        </div>
        """

        folium.Marker(
            location=[u_lat, u_lon],
            tooltip="📍 LOKASI ANDA SEKARANG (klik untuk detail)",
            popup=folium.Popup(home_popup, max_width=290),
            icon=folium.Icon(color="blue", icon="user", prefix="glyphicon"),
        ).add_to(user_group)

        # Legenda kotak posisi di pojok peta
        legend_pos = f"""
        <div style="position:fixed; bottom:26px; left:26px; z-index:9999; background:#FFFFFF;
                    border:2px solid #1D4ED8; border-radius:10px; padding:9px 12px;
                    font-family:sans-serif; font-size:12.5px; color:#0F172A;
                    box-shadow:0 3px 12px rgba(15,23,42,.22);">
            <b style="color:#1D4ED8;">📍 LOKASI ANDA</b><br>
            {posisi['dusun']} • {posisi['zone_name']}<br>
            <span style="color:#475569;">{u_lat:.5f}, {u_lon:.5f}</span><br>
            <span style="color:{'#15803D' if di_desa else '#B45309'}; font-weight:700;">
                {'Di area Desa Pagentan' if di_desa else 'Di luar area Desa Pagentan'}
            </span>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_pos))

        user_group.add_to(m)
        m.location = [u_lat, u_lon]
        m.options["zoom"] = 16

    folium.LayerControl(collapsed=True).add_to(m)

    dusun_summary = [
        {
            "Wilayah Dusun": d_name,
            "Blok Merah (Siaga)": st_val["merah"],
            "Blok Kuning (Waspada)": st_val["kuning"],
            "Blok Hijau (Aman)": st_val["hijau"],
            "Total Blok": st_val["total"],
        }
        for d_name, st_val in dusun_stats_map.items()
    ]

    return m, counts, dusun_summary


# -----------------------------------------------------------------------------
# MODUL LOKASI REAL-TIME WARGA (GPS HP / Titik Manual)
# -----------------------------------------------------------------------------
EARTH_RADIUS_M = 6371008.8


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Jarak dua koordinat (meter) memakai formula haversine."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return round(2 * EARTH_RADIUS_M * math.asin(math.sqrt(a)), 1)


def is_inside_pagentan(lat: float, lon: float, buffer_deg: float = 0.0025) -> bool:
    """True bila koordinat warga berada di dalam (atau dekat) area Desa Pagentan."""
    return (
        (LAT_SOUTH - buffer_deg) <= lat <= (LAT_NORTH + buffer_deg)
        and (LON_WEST - buffer_deg) <= lon <= (LON_EAST + buffer_deg)
    )


def nearest_vital_location(lat: float, lon: float) -> dict:
    """Titik lokal (posko, balai desa, titik pantau lereng, pos ronda) terdekat dari posisi warga."""
    best = None
    for loc in VITAL_LOCATIONS:
        dist = haversine_m(lat, lon, loc["coords"][0], loc["coords"][1])
        if best is None or dist < best["jarak_m"]:
            best = {**loc, "jarak_m": dist}
    return best or {}


def describe_user_position(lat: float, lon: float) -> dict:
    """
    Menerjemahkan koordinat GPS warga menjadi informasi yang mudah dipahami:
    nama dusun, karakter lereng, kemiringan, arahan evakuasi, dan titik terdekat.
    """
    dusun = resolve_dusun_sector(lat, lon)
    morph = evaluate_cell_morphology(lat, lon)
    if morph["zone_code"] == "ZONA_STABIL":
        arahan = "Lokasi Anda relatif stabil. Tetap ikuti arahan resmi Balai Desa / Pos Ronda setempat."
    elif morph["zone_code"] == "LERENG_SEDANG":
        arahan = "Anda berada di lereng miring. Pastikan selokan di sekitar tidak tersumbat dan jangan menimbun tanah di bibir lereng."
    elif morph["zone_code"] == "KRITIS_SUNGAI_RAWA":
        arahan = "Anda berada dekat alur sungai/rawa lereng. Jauhi bantaran saat hujan deras dan pantau kekeruhan air."
    else:
        arahan = "Anda berada di zona tebing curam. Segera menjauh dari kaki tebing bila hujan tinggi dan ikuti jalur evakuasi ke Posko Kebencanaan Desa."

    return {
        "dusun": dusun,
        "zone_code": morph["zone_code"],
        "zone_name": morph["zone_name"],
        "slope_deg": morph["slope_deg"],
        "terrain_desc": morph["terrain_desc"],
        "arahan": arahan,
        "jarak_ke_balai_m": haversine_m(lat, lon, MAP_CENTER[0], MAP_CENTER[1]),
        "titik_terdekat": nearest_vital_location(lat, lon),
        "di_dalam_desa": is_inside_pagentan(lat, lon),
    }


def build_pagentan_gis_map(
    risk_level: str = "AMAN",
    show_grid: bool = True,
    show_hydrology: bool = True,
    show_evac_routes: bool = True,
    basemap_style: str = "OpenStreetMap",
    user_location: dict | None = None,
    radius_m: int = 250,
) -> tuple[folium.Map, dict, list[dict]]:
    """Versi lanjutan build_pagentan_gis_map dengan penanda posisi real-time warga."""
    return _build_map_impl(
        risk_level=risk_level,
        show_grid=show_grid,
        show_hydrology=show_hydrology,
        show_evac_routes=show_evac_routes,
        basemap_style=basemap_style,
        user_location=user_location,
        radius_m=radius_m,
    )
