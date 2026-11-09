"""
Modul Integrasi Cuaca Real-Time (Open-Meteo API) & Mesin Analisis Peringatan Dini Longsor
Desa Pagentan, Kecamatan Pagentan, Kabupaten Banjarnegara, Jawa Tengah.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import pandas as pd
import requests
import streamlit as st

# Koordinat Resmi Pusat Desa Pagentan, Banjarnegara
PAGENTAN_LAT = -7.300433
PAGENTAN_LON = 109.809946
TZ_WIB = ZoneInfo("Asia/Jakarta")
BACKUP_CACHE_FILE = Path("/tmp/sipaldo_pagentan_last_weather.json")

INDONESIAN_MONTHS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
    9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}

INDONESIAN_DAYS = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu",
}


def format_tanggal_id(dt: datetime, with_day_name: bool = False) -> str:
    """Format tanggal ramah warga dalam Bahasa Indonesia."""
    tgl = f"{dt.day:02d} {INDONESIAN_MONTHS[dt.month]}"
    if with_day_name:
        return f"{INDONESIAN_DAYS[dt.weekday()]}, {tgl}"
    return tgl


def translate_wmo_weather(code: int) -> tuple[str, str]:
    """Terjemahkan kode cuaca WMO Open-Meteo ke Bahasa Indonesia & ikon."""
    code = int(code or 0)
    if code == 0:
        return "Cerah", "☀️"
    if code in (1, 2):
        return "Cerah Berawan", "⛅"
    if code == 3:
        return "Mendung / Berawan Tebal", "☁️"
    if code in (45, 48):
        return "Berkabut (Kabut Pegunungan)", "🌫️"
    if code in (51, 53, 55):
        return "Gerimis", "🌦️"
    if code == 61:
        return "Hujan Ringan", "🌧️"
    if code == 63:
        return "Hujan Sedang", "🌧️"
    if code in (65, 67):
        return "Hujan Lebat", "⛈️"
    if code in (80, 81):
        return "Hujan Lokal Sedang", "🌧️"
    if code == 82:
        return "Hujan Deras Mengguyur", "⛈️"
    if code in (95, 96, 99):
        return "Hujan Lebat Disertai Petir", "⛈️"
    return "Berawan", "☁️"


def _build_offline_fallback_data(reason: str = "Gangguan koneksi API") -> dict:
    """
    Data tiruan terakhir (fallback/mock data) anti-crash apabila API Open-Meteo
    gagal merespons atau tidak ada jaringan internet.
    """
    now_wib = datetime.now(TZ_WIB).replace(tzinfo=None)

    # Cek apakah ada snapshot lokal terakhir yang sempat tersimpan
    if BACKUP_CACHE_FILE.exists():
        try:
            cached = json.loads(BACKUP_CACHE_FILE.read_text(encoding="utf-8"))
            cached["daily_df"] = pd.DataFrame(cached["daily_records"])
            cached["hourly_24h_df"] = pd.DataFrame(cached["hourly_24h_records"])
            cached["forecast_12h_df"] = pd.DataFrame(cached["forecast_12h_records"])
            cached["is_offline"] = True
            cached["offline_reason"] = reason
            return cached
        except Exception:
            pass

    # Fallback murni bawaan sistem (tanpa bergantung file eksternal)
    daily_dates = [now_wib - timedelta(days=d) for d in (3, 2, 1, 0)]
    labels_hari = ["3 Hari Lalu", "2 Hari Lalu", "Kemarin", "Hari Ini"]
    mock_precip = [14.5, 11.2, 8.6, 9.4]
    mock_hours = [9.0, 7.0, 6.0, 6.0]

    daily_df = pd.DataFrame({
        "tanggal_iso": [d.strftime("%Y-%m-%d") for d in daily_dates],
        "label": [f"{lbl}\n({format_tanggal_id(d)})" for lbl, d in zip(labels_hari, daily_dates)],
        "tanggal_pendek": [format_tanggal_id(d) for d in daily_dates],
        "curah_hujan_mm": mock_precip,
        "durasi_hujan_jam": mock_hours,
    })
    daily_df["akumulasi_mm"] = daily_df["curah_hujan_mm"].cumsum().round(1)

    # Data jam-jaman tiruan 24 jam terakhir & prakiraan 12 jam
    past_hours = [now_wib.replace(minute=0, second=0, microsecond=0) - timedelta(hours=h) for h in range(23, -1, -1)]
    past_vals = [0.0, 0.2, 0.5, 1.1, 1.8, 1.4, 0.6, 0.2, 0.0, 0.0, 0.0, 0.1,
                 0.4, 0.9, 1.2, 0.8, 0.3, 0.0, 0.0, 0.0, 0.1, 0.3, 0.4, 0.2]
    hourly_24h_df = pd.DataFrame({
        "jam": [t.strftime("%H:%M") for t in past_hours],
        "waktu_penuh": [t.strftime("%d/%m %H:%M WIB") for t in past_hours],
        "curah_hujan_mm": past_vals,
    })

    next_hours = [now_wib.replace(minute=0, second=0, microsecond=0) + timedelta(hours=h) for h in range(1, 13)]
    next_vals = [0.3, 0.6, 1.1, 1.5, 0.9, 0.4, 0.1, 0.0, 0.0, 0.0, 0.2, 0.4]
    forecast_12h_df = pd.DataFrame({
        "jam": [t.strftime("%H:%M") for t in next_hours],
        "waktu_penuh": [t.strftime("%d/%m %H:%M WIB") for t in next_hours],
        "prakiraan_mm": next_vals,
    })

    return {
        "rain_24h": round(sum(past_vals), 1),
        "rain_today": 9.4,
        "rain_3d_total": round(float(daily_df["curah_hujan_mm"].sum()), 1),
        "rain_forecast_12h": round(sum(next_vals), 1),
        "soil_moisture_pct": 48.5,
        "temperature_c": 21.2,
        "humidity_pct": 94,
        "wind_kmh": 4.2,
        "weather_desc": "Berawan / Gerimis Lokal",
        "weather_icon": "🌦️",
        "coord_lat": PAGENTAN_LAT,
        "coord_lon": PAGENTAN_LON,
        "elevation_m": 810,
        "daily_df": daily_df,
        "hourly_24h_df": hourly_24h_df,
        "forecast_12h_df": forecast_12h_df,
        "updated_at": f"{format_tanggal_id(now_wib, with_day_name=True)} • {now_wib.strftime('%H:%M')} WIB",
        "is_offline": True,
        "is_simulation": False,
        "offline_reason": reason,
    }


@st.cache_data(ttl=600, show_spinner=False)
def fetch_realtime_open_meteo(lat: float = PAGENTAN_LAT, lon: float = PAGENTAN_LON) -> dict:
    """
    Menarik data cuaca & curah hujan real-time + historis 3 hari terakhir
    dari Open-Meteo API pada titik koordinat yang diminta.

    Default: Balai Desa Pagentan (-7.300433, 109.809946).
    Bila warga membagikan titik GPS HP-nya (fitur "Lokasi Saya"), fungsi ini
    dipanggil ulang memakai koordinat warga tersebut sehingga kondisi yang
    ditampilkan benar-benar kondisi di lokasi tempat warga berdiri.
    Dibungkus try-except penuh agar aplikasi anti-crash.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": round(float(lat), 5),
        "longitude": round(float(lon), 5),
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m",
        "hourly": "precipitation,soil_moisture_3_to_9cm",
        "daily": "precipitation_sum,precipitation_hours",
        "past_days": 3,
        "forecast_days": 2,
        "timezone": "Asia/Jakarta",
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        payload = response.json()

        now_wib = datetime.now(TZ_WIB).replace(tzinfo=None)
        current_hour = now_wib.replace(minute=0, second=0, microsecond=0)

        # 1. Olah data per jam (akumulasi rolling 24 jam + kelembaban tanah + prakiraan 12 jam)
        hourly_raw = payload.get("hourly", {})
        hourly_df = pd.DataFrame({
            "time": pd.to_datetime(hourly_raw.get("time", [])),
            "precip": hourly_raw.get("precipitation", []),
            "soil": hourly_raw.get("soil_moisture_3_to_9cm", []),
        })
        hourly_df["precip"] = pd.to_numeric(hourly_df["precip"], errors="coerce").fillna(0.0)
        hourly_df["soil"] = pd.to_numeric(hourly_df["soil"], errors="coerce").ffill().bfill().fillna(0.45)

        mask_24h = (hourly_df["time"] > current_hour - timedelta(hours=24)) & (hourly_df["time"] <= current_hour)
        df_24h = hourly_df.loc[mask_24h].copy()
        rain_24h = round(float(df_24h["precip"].sum()), 1)

        # Kelembaban tanah saat ini (konversi m³/m³ ke persentase volumetrik %)
        latest_soil_row = hourly_df.loc[hourly_df["time"] <= current_hour]
        soil_val = float(latest_soil_row["soil"].iloc[-1]) if not latest_soil_row.empty else 0.46
        soil_moisture_pct = round(min(max(soil_val * 100.0, 5.0), 99.0), 1)

        hourly_24h_df = pd.DataFrame({
            "jam": df_24h["time"].dt.strftime("%H:%M").tolist(),
            "waktu_penuh": df_24h["time"].dt.strftime("%d/%m %H:%M WIB").tolist(),
            "curah_hujan_mm": df_24h["precip"].round(1).tolist(),
        })

        mask_next_12h = (hourly_df["time"] > current_hour) & (hourly_df["time"] <= current_hour + timedelta(hours=12))
        df_next_12h = hourly_df.loc[mask_next_12h].copy()
        forecast_12h_df = pd.DataFrame({
            "jam": df_next_12h["time"].dt.strftime("%H:%M").tolist(),
            "waktu_penuh": df_next_12h["time"].dt.strftime("%d/%m %H:%M WIB").tolist(),
            "prakiraan_mm": df_next_12h["precip"].round(1).tolist(),
        })
        rain_forecast_12h = round(float(df_next_12h["precip"].sum()), 1)

        # 2. Olah data harian (3 hari terakhir + hari ini = 4 titik tren akumulasi)
        daily_raw = payload.get("daily", {})
        daily_all = pd.DataFrame({
            "date": pd.to_datetime(daily_raw.get("time", [])),
            "precip_sum": daily_raw.get("precipitation_sum", []),
            "precip_hours": daily_raw.get("precipitation_hours", []),
        })
        daily_all["precip_sum"] = pd.to_numeric(daily_all["precip_sum"], errors="coerce").fillna(0.0)
        daily_all["precip_hours"] = pd.to_numeric(daily_all["precip_hours"], errors="coerce").fillna(0.0)

        today_date = now_wib.date()
        daily_hist = daily_all.loc[daily_all["date"].dt.date <= today_date].tail(4).copy()

        rel_names = ["3 Hari Lalu", "2 Hari Lalu", "Kemarin", "Hari Ini"]
        if len(daily_hist) < 4:
            rel_names = rel_names[-len(daily_hist):]

        daily_df = pd.DataFrame({
            "tanggal_iso": daily_hist["date"].dt.strftime("%Y-%m-%d").tolist(),
            "label": [
                f"{nm}\n({format_tanggal_id(dt)})"
                for nm, dt in zip(rel_names, daily_hist["date"])
            ],
            "tanggal_pendek": [format_tanggal_id(dt) for dt in daily_hist["date"]],
            "curah_hujan_mm": daily_hist["precip_sum"].round(1).tolist(),
            "durasi_hujan_jam": daily_hist["precip_hours"].round(0).tolist(),
        })
        daily_df["akumulasi_mm"] = daily_df["curah_hujan_mm"].cumsum().round(1)

        rain_today = float(daily_df["curah_hujan_mm"].iloc[-1]) if not daily_df.empty else rain_24h
        rain_3d_total = round(float(daily_df["curah_hujan_mm"].sum()), 1)

        # 3. Kondisi cuaca terkini
        current_raw = payload.get("current", {})
        weather_desc, weather_icon = translate_wmo_weather(current_raw.get("weather_code", 2))

        result = {
            "coord_lat": round(float(lat), 5),
            "coord_lon": round(float(lon), 5),
            "rain_24h": rain_24h,
            "rain_today": round(rain_today, 1),
            "rain_3d_total": rain_3d_total,
            "rain_forecast_12h": rain_forecast_12h,
            "soil_moisture_pct": soil_moisture_pct,
            "temperature_c": round(float(current_raw.get("temperature_2m", 21.0)), 1),
            "humidity_pct": int(round(float(current_raw.get("relative_humidity_2m", 90)))),
            "wind_kmh": round(float(current_raw.get("wind_speed_10m", 3.5)), 1),
            "weather_desc": weather_desc,
            "weather_icon": weather_icon,
            "elevation_m": int(round(float(payload.get("elevation", 810)))),
            "daily_df": daily_df,
            "hourly_24h_df": hourly_24h_df,
            "forecast_12h_df": forecast_12h_df,
            "updated_at": f"{format_tanggal_id(now_wib, with_day_name=True)} • {now_wib.strftime('%H:%M')} WIB",
            "is_offline": False,
            "is_simulation": False,
            "offline_reason": "",
        }

        # Simpan cadangan lokal non-kritis untuk fallback bila koneksi putus di kemudian waktu
        try:
            serializable = {
                k: v for k, v in result.items()
                if k not in ("daily_df", "hourly_24h_df", "forecast_12h_df")
            }
            serializable["daily_records"] = daily_df.to_dict(orient="records")
            serializable["hourly_24h_records"] = hourly_24h_df.to_dict(orient="records")
            serializable["forecast_12h_records"] = forecast_12h_df.to_dict(orient="records")
            BACKUP_CACHE_FILE.write_text(json.dumps(serializable), encoding="utf-8")
        except Exception:
            pass

        return result

    except Exception as exc:
        return _build_offline_fallback_data(reason=str(exc))


def get_weather_data(
    mode: str = "REALTIME",
    lat: float = PAGENTAN_LAT,
    lon: float = PAGENTAN_LON,
) -> dict:
    """
    Mengambil data cuaca sesuai mode:
    - REALTIME     : Data asli langsung dari Open-Meteo API
    - SIM_AMAN     : Simulasi skenario Aman (< 20 mm)
    - SIM_WASPADA  : Simulasi skenario Waspada (20 - 50 mm & hujan konstan)
    - SIM_SIAGA    : Simulasi skenario Bahaya/Siaga (> 50 mm, Mode Darurat Merah Berkedip)
    - SIM_OFFLINE  : Uji ketahanan error / fallback saat API gagal merespons
    """
    if mode == "SIM_OFFLINE":
        return _build_offline_fallback_data(reason="Simulasi uji gangguan jaringan API Open-Meteo")

    base = fetch_realtime_open_meteo(lat, lon)
    if mode == "REALTIME":
        return base

    # Salin struktur untuk skenario simulasi latihan kesiapsiagaan desa
    sim = dict(base)
    sim["daily_df"] = base["daily_df"].copy()
    sim["hourly_24h_df"] = base["hourly_24h_df"].copy()
    sim["forecast_12h_df"] = base["forecast_12h_df"].copy()
    sim["is_simulation"] = True
    sim["is_offline"] = False

    if mode == "SIM_AMAN":
        vals = [4.2, 6.0, 5.5, 8.2]
        sim["daily_df"]["curah_hujan_mm"] = vals[-len(sim["daily_df"]):]
        sim["daily_df"]["durasi_hujan_jam"] = [3.0, 4.0, 3.0, 4.0][-len(sim["daily_df"]):]
        sim["daily_df"]["akumulasi_mm"] = sim["daily_df"]["curah_hujan_mm"].cumsum().round(1)
        sim["rain_24h"] = 8.2
        sim["rain_today"] = 8.2
        sim["rain_3d_total"] = round(float(sim["daily_df"]["curah_hujan_mm"].sum()), 1)
        sim["soil_moisture_pct"] = 36.4
        sim["weather_desc"] = "Cerah Berawan"
        sim["weather_icon"] = "⛅"
        sim["rain_forecast_12h"] = 2.5

    elif mode == "SIM_WASPADA":
        vals = [18.5, 22.0, 19.4, 34.6]
        sim["daily_df"]["curah_hujan_mm"] = vals[-len(sim["daily_df"]):]
        sim["daily_df"]["durasi_hujan_jam"] = [11.0, 14.0, 13.0, 15.0][-len(sim["daily_df"]):]
        sim["daily_df"]["akumulasi_mm"] = sim["daily_df"]["curah_hujan_mm"].cumsum().round(1)
        sim["rain_24h"] = 34.6
        sim["rain_today"] = 34.6
        sim["rain_3d_total"] = round(float(sim["daily_df"]["curah_hujan_mm"].sum()), 1)
        sim["soil_moisture_pct"] = 64.8
        sim["weather_desc"] = "Hujan Sedang Konstan"
        sim["weather_icon"] = "🌧️"
        sim["rain_forecast_12h"] = 16.2
        if len(sim["hourly_24h_df"]) > 0:
            sim["hourly_24h_df"]["curah_hujan_mm"] = [
                round(34.6 / len(sim["hourly_24h_df"]) * (1.4 if i % 3 == 0 else 0.8), 1)
                for i in range(len(sim["hourly_24h_df"]))
            ]

    elif mode == "SIM_SIAGA":
        vals = [26.4, 31.8, 38.5, 68.4]
        sim["daily_df"]["curah_hujan_mm"] = vals[-len(sim["daily_df"]):]
        sim["daily_df"]["durasi_hujan_jam"] = [14.0, 16.0, 18.0, 20.0][-len(sim["daily_df"]):]
        sim["daily_df"]["akumulasi_mm"] = sim["daily_df"]["curah_hujan_mm"].cumsum().round(1)
        sim["rain_24h"] = 68.4
        sim["rain_today"] = 68.4
        sim["rain_3d_total"] = round(float(sim["daily_df"]["curah_hujan_mm"].sum()), 1)
        sim["soil_moisture_pct"] = 86.2
        sim["humidity_pct"] = 99
        sim["weather_desc"] = "Hujan Lebat Ekstrem"
        sim["weather_icon"] = "⛈️"
        sim["rain_forecast_12h"] = 28.5
        if len(sim["hourly_24h_df"]) > 0:
            sim["hourly_24h_df"]["curah_hujan_mm"] = [
                round(1.5 + (i % 6) * 0.9, 1)
                for i in range(len(sim["hourly_24h_df"]))
            ]

    return sim


def classify_landslide_risk(weather: dict, field_symptom_count: int = 0) -> dict:
    """
    Logika Analisis Longsor Dinamis Banjarnegara berdasarkan Akumulasi Curah Hujan 24 Jam
    & Kejenuhan Air Tanah dari Hujan Konstan Hari Sebelumnya:
    - Aman (Hijau)    : < 20 mm (tanpa hujan konstan hari sebelumnya)
    - Waspada (Kuning): 20 - 50 mm (atau hujan konstan dari hari sebelumnya)
    - Bahaya/Siaga    : > 50 mm (Mode Darurat Merah Menyala Berkedip)
    """
    rain_24h = float(weather.get("rain_24h", 0.0))
    daily_df: pd.DataFrame = weather.get("daily_df", pd.DataFrame())

    # Deteksi hujan konstan dari hari-hari sebelumnya (tanah vulkanik lereng Pagentan jenuh air)
    constant_prev_rain = False
    prev_rain_note = ""
    if not daily_df.empty and len(daily_df) >= 2:
        prev_days = daily_df.iloc[:-1]
        days_moderate = int((prev_days["curah_hujan_mm"] >= 14.0).sum())
        days_long_drizzle = int((prev_days["durasi_hujan_jam"] >= 14.0).sum())
        prev_sum = float(prev_days["curah_hujan_mm"].sum())

        if days_moderate >= 2 or (days_long_drizzle >= 2 and prev_sum >= 35.0) or prev_sum >= 50.0:
            constant_prev_rain = True
            prev_rain_note = (
                f"Terdeteksi akumulasi hujan hari-hari sebelumnya sebesar {prev_sum:.1f} mm "
                "sehingga pori tanah lereng masih menyimpan air (jenuh)."
            )

    if rain_24h > 50.0:
        return {
            "level": "SIAGA",
            "label_ui": "BAHAYA / SIAGA (MERAH)",
            "short_badge": "SIAGA DARURAT",
            "color": "#DC2626",
            "bg_soft": "#FEF2F2",
            "border_color": "#EF4444",
            "banner_text": "SIAGA: Curah Hujan Tinggi di Pagentan! Hindari Area Tebing & Jalur Rawan!",
            "is_emergency": True,
            "ConstantPrevRain": constant_prev_rain,
            "summary_reason": (
                f"Akumulasi curah hujan 24 jam mencapai {rain_24h:.1f} mm (melampaui batas kritis 50 mm). "
                "Tekanan air pori pada lereng tebing dan alur sungai sangat tinggi!"
            ),
            "citizen_action": (
                "SEGERA JAUHI area bawah tebing, bantaran sungai, dan jalur rawan longsor! "
                "Warga di zona merah diimbau bersiap/bergeser menuju Posko Kebencanaan Desa atau Balai Desa Pagentan."
            ),
            "ronda_instruction": (
                "Bunyikan tanda peringatan dini (kentongan nada cepat terus-menerus), aktifkan patroli jarak aman, "
                "prioritaskan evakuasi lansia, ibu hamil, anak-anak, dan penyandang disabilitas."
            ),
            "kentongan_code": "Titir (Dipukul cepat & terus-menerus) — Tanda Bahaya / Evakuasi Segera",
            "field_symptom_count": field_symptom_count,
        }

    if (20.0 <= rain_24h <= 50.0) or constant_prev_rain or field_symptom_count >= 2:
        reasons = []
        if 20.0 <= rain_24h <= 50.0:
            reasons.append(f"Curah hujan 24 jam tercatat {rain_24h:.1f} mm (rentang Waspada 20–50 mm).")
        if constant_prev_rain:
            reasons.append(prev_rain_note)
        if field_symptom_count >= 2:
            reasons.append(f"Dilaporkan {field_symptom_count} tanda gejala fisik lereng dari daftar pantau Pos Ronda.")

        return {
            "level": "WASPADA",
            "label_ui": "WASPADA (KUNING)",
            "short_badge": "WASPADA LERENG",
            "color": "#D97706",
            "bg_soft": "#FFFBEB",
            "border_color": "#F59E0B",
            "banner_text": "Waspada: Lereng Mulai Jenuh Air",
            "is_emergency": False,
            "ConstantPrevRain": constant_prev_rain,
            "summary_reason": " ".join(reasons),
            "citizen_action": (
                "Tingkatkan kewaspadaan terutama saat hujan turun pada sore–malam hari. "
                "Periksa saluran drainase rumah/kebun agar air tidak meresap langsung ke bibir tebing, dan siapkan Tas Siaga Bencana."
            ),
            "ronda_instruction": (
                "Lakukan ronda keliling setiap 1–2 jam pada Titik Pantau Lereng tiap dusun, periksa retakan tanah baru "
                "atau rembesan air keruh di kaki tebing, serta siagakan kentongan & komunikasi antar-Pos Ronda."
            ),
            "kentongan_code": "Ganda (Dua pukulan berulang: Thok-Thok ... Thok-Thok) — Tanda Waspada / Siaga Warga",
            "field_symptom_count": field_symptom_count,
        }

    return {
        "level": "AMAN",
        "label_ui": "AMAN (HIJAU)",
        "short_badge": "KONDISI AMAN",
        "color": "#15803D",
        "bg_soft": "#F0FDF4",
        "border_color": "#22C55E",
        "banner_text": "Kondisi Desa Aman",
        "is_emergency": False,
        "ConstantPrevRain": False,
        "summary_reason": (
            f"Akumulasi curah hujan 24 jam rendah ({rain_24h:.1f} mm, di bawah ambang 20 mm) "
            "dan kondisi kejenuhan lereng berada pada batas normal."
        ),
        "citizen_action": (
            "Aktivitas warga Desa Pagentan dapat berjalan normal. Tetap jaga kebersihan saluran air/selokan "
            "dan hindari pemotongan tebing tegak tanpa penguat (talud)."
        ),
        "ronda_instruction": (
            "Pemantauan rutin terjadwal. Pastikan papan QR Code SIPALDO-PAGENTAN dan jalur evakuasi desa bebas hambatan."
        ),
        "kentongan_code": "Tunggal Teratur — Tanda Ronda Malam Kondusif / Aman",
        "field_symptom_count": field_symptom_count,
    }
