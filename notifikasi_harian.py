"""
Skrip notifikasi harian SIPALDO-PAGENTAN (dijalankan oleh GitHub Actions).

Cara pakai lokal:
    TELEGRAM_TOKEN=xxx TELEGRAM_CHAT_ID=-100xxx python notifikasi_harian.py

Tanpa token, skrip hanya mencetak pesan ke layar (mode uji / dry-run).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ews_features import (  # noqa: E402
    analisis_antisipasi,
    kirim_telegram,
    susun_pesan_status,
    telegram_terkonfigurasi,
)
from weather_ews import classify_landslide_risk, get_weather_data  # noqa: E402


def main() -> int:
    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    label = os.environ.get("LABEL_DESA", "Desa Pagentan").strip()

    weather = get_weather_data("REALTIME")
    risk = classify_landslide_risk(weather)
    antisipasi = analisis_antisipasi(weather)

    pesan = susun_pesan_status(weather, risk, antisipasi, label)

    print("=" * 60)
    print(pesan)
    print("=" * 60)

    if weather.get("is_offline"):
        print("[!] Data cuaca sedang offline (estimasi). Pesan tetap dikirim dengan penanda.")

    if not telegram_terkonfigurasi(token, chat_id):
        print("[i] TELEGRAM_TOKEN / TELEGRAM_CHAT_ID belum diisi → mode dry-run (tidak mengirim).")
        return 0

    ok, ket = kirim_telegram(token, chat_id, pesan)
    print(("[OK] " if ok else "[GAGAL] ") + ket)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
