"""
Modul Visualisasi Grafik Tren Curah Hujan & Generator QR Code Pos Ronda
SIPALDO-PAGENTAN (Desa Pagentan, Banjarnegara).
"""

from __future__ import annotations

import io
import pandas as pd
import plotly.graph_objects as go
import qrcode
from PIL import Image, ImageDraw, ImageFont


def add_threshold_bands(fig: go.Figure) -> go.Figure:
    """
    Beri latar berwarna pada area grafik: hijau (<20 mm), kuning (20–50 mm),
    merah (>50 mm) agar ambang bahaya langsung terlihat tanpa membaca angka.
    """
    fig.add_hrect(y0=0, y1=20, fillcolor="#16A34A", opacity=0.05, line_width=0, layer="below")
    fig.add_hrect(y0=20, y1=50, fillcolor="#F59E0B", opacity=0.08, line_width=0, layer="below")
    fig.add_hrect(y0=50, y1=90, fillcolor="#DC2626", opacity=0.07, line_width=0, layer="below")
    return fig


def build_3day_rainfall_chart(daily_df: pd.DataFrame) -> go.Figure:
    """
    Grafik kombinasi Batang (Curah Hujan Harian) & Garis (Akumulasi Air di Dalam Tanah)
    selama 3 hari terakhir hingga hari ini, dilengkapi garis batas Waspada & Siaga.
    """
    bar_colors = []
    for val in daily_df["curah_hujan_mm"]:
        if val > 50.0:
            bar_colors.append("#DC2626")
        elif val >= 20.0:
            bar_colors.append("#F59E0B")
        else:
            bar_colors.append("#16A34A")

    fig = go.Figure()

    # Batang: Curah hujan per hari
    fig.add_trace(
        go.Bar(
            x=daily_df["label"],
            y=daily_df["curah_hujan_mm"],
            name="Hujan Harian (mm)",
            marker=dict(color=bar_colors, line=dict(color="#0F172A", width=1), cornerradius=6),
            text=[f"<b>{v:.1f} mm</b>" for v in daily_df["curah_hujan_mm"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Curah Hujan Harian: %{y:.1f} mm<extra></extra>",
        )
    )

    # Garis: Akumulasi simpanan air hujan 3 hari terakhir di tanah
    fig.add_trace(
        go.Scatter(
            x=daily_df["label"],
            y=daily_df["akumulasi_mm"],
            name="Akumulasi 3 Hari (mm)",
            mode="lines+markers+text",
            line=dict(color="#1D4ED8", width=3.5),
            marker=dict(size=10, color="#1D4ED8", line=dict(color="#FFFFFF", width=2)),
            text=[f"{v:.1f}" for v in daily_df["akumulasi_mm"]],
            textposition="top center",
            textfont=dict(color="#1E3A8A", size=12),
            hovertemplate="<b>%{x}</b><br>Total Akumulasi Tanah: %{y:.1f} mm<extra></extra>",
        )
    )

    # Garis referensi ambang batas harian/24 jam
    fig.add_hline(
        y=20.0,
        line_dash="dash",
        line_color="#D97706",
        line_width=2,
        annotation_text="Batas Waspada (20 mm)",
        annotation_position="top left",
        annotation_font=dict(color="#B45309", size=12),
    )
    fig.add_hline(
        y=50.0,
        line_dash="dot",
        line_color="#DC2626",
        line_width=2,
        annotation_text="Batas Siaga Darurat (50 mm)",
        annotation_position="top left",
        annotation_font=dict(color="#B91C1C", size=12),
    )

    max_y = max(
        62.0,
        float(daily_df["akumulasi_mm"].max()) * 1.18 if not daily_df.empty else 62.0,
    )

    fig.update_layout(
        height=370,
        margin=dict(l=16, r=16, t=28, b=16),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family="sans-serif", size=14, color="#0F172A"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=13),
        ),
        yaxis=dict(
            title="Tinggi Curah Hujan (mm)",
            range=[0, max_y],
            gridcolor="#E2E8F0",
            zerolinecolor="#CBD5E1",
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(size=13),
        ),
        bargap=0.38,
    )
    return add_threshold_bands(fig)


def build_hourly_timeline_chart(hourly_24h_df: pd.DataFrame, forecast_12h_df: pd.DataFrame) -> go.Figure:
    """
    Grafik per jam (24 jam terakhir + prakiraan 12 jam ke depan) untuk membantu
    petugas jaga malam Pos Ronda mengantisipasi guyuran hujan lanjutan.
    """
    fig = go.Figure()

    if not hourly_24h_df.empty:
        fig.add_trace(
            go.Bar(
                x=hourly_24h_df["waktu_penuh"],
                y=hourly_24h_df["curah_hujan_mm"],
                name="Realisasi 24 Jam Terakhir",
                marker_color="#0284C7",
                hovertemplate="<b>%{x}</b><br>Hujan Tercatat: %{y:.1f} mm/jam<extra></extra>",
            )
        )

    if not forecast_12h_df.empty:
        fig.add_trace(
            go.Bar(
                x=forecast_12h_df["waktu_penuh"],
                y=forecast_12h_df["prakiraan_mm"],
                name="Prakiraan 12 Jam Ke Depan",
                marker_color="#F59E0B",
                opacity=0.85,
                hovertemplate="<b>%{x}</b><br>Prakiraan Hujan: %{y:.1f} mm/jam<extra></extra>",
            )
        )

    fig.update_layout(
        height=310,
        margin=dict(l=14, r=14, t=28, b=40),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        font=dict(family="sans-serif", size=13, color="#0F172A"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        yaxis=dict(title="Intensitas (mm/jam)", gridcolor="#E2E8F0"),
        xaxis=dict(title=None, tickangle=-35, nticks=10),
    )
    return add_threshold_bands(fig)


def _load_font(size: int):
    """Muat font TrueType bila tersedia (agar teks QR rapi); fallback ke font bawaan PIL."""
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_village_qr_png(
    target_url: str,
    judul: str = "SCAN PANTAU LONGSOR",
    subjudul: str = "DESA PAGENTAN - KAB. BANJARNEGARA",
    label: str = "",
) -> bytes:
    """
    Membuat gambar QR Code resolusi tinggi berbingkai rapi siap cetak untuk Pos Ronda
    dan papan pengumuman Balai Desa Pagentan.

    `judul`/`subjudul`/`label` dipakai untuk kartu QR per Pos Ronda
    (mis. judul="POS RONDA DUSUN BULU", label="RW 05-06").
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(target_url.strip() or "https://sipaldo-pagentan.streamlit.app")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGB")

    # Tambahkan bingkai hijau-putih rapi agar mudah dipindai kamera HP warga
    pad = 24
    canvas = Image.new("RGB", (qr_img.width + pad * 2, qr_img.height + pad * 2), "#FFFFFF")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [6, 6, canvas.width - 7, canvas.height - 7],
        radius=18,
        outline="#15803D",
        width=5,
    )
    canvas.paste(qr_img, (pad, pad))

    # Bingkai kartu + judul (untuk QR per Pos Ronda)
    if judul or subjudul or label:
        f_header = _load_font(30)
        f_sub = _load_font(19)
        f_label = _load_font(22)

        width = max(canvas.width + 34, 640)
        header_h = 74 + (34 if label else 0)
        footer_h = 46

        card = Image.new("RGB", (width, header_h + canvas.height + footer_h), "#FFFFFF")
        d2 = ImageDraw.Draw(card)
        d2.rectangle([0, 0, width, header_h], fill="#15803D")

        def _center_text(txt, font, y, fill):
            try:
                tw = d2.textlength(txt, font=font)
            except Exception:
                tw = len(txt) * 9
            d2.text(((width - tw) / 2, y), txt, font=font, fill=fill)

        _center_text(judul.upper(), f_header, 14, "#FFFFFF")
        _center_text(subjudul.upper(), f_sub, 50, "#DCFCE7")
        if label:
            _center_text(label.upper(), f_label, 78, "#FEF08A")

        card.paste(canvas, (int((width - canvas.width) / 2), header_h))

        footer_y = header_h + canvas.height
        d2.rectangle([0, footer_y, width, footer_y + footer_h], fill="#F0FDF4")
        _center_text(
            "Pindai untuk status & checklist patroli",
            f_sub,
            footer_y + 12,
            "#14532D",
        )
        buf = io.BytesIO()
        card.save(buf, format="PNG")
        return buf.getvalue()

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()
