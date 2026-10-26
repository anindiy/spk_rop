"""Mesin hitung SPK persediaan: safety stock (stok pengaman) dan reorder point (titik pesan ulang).

Rumus mengikuti jurnal Brahmantyo, Wibowo, & Nurcahyawati (2023),
Jurnal Sains dan Informatika 9(1):
    Stok pengaman (SS)  = jumlah hari cadangan x rata-rata pemakaian per hari
    Titik pesan ulang   = (pemakaian per hari x lama pengiriman) + SS

Aturan status (Aman / Segera pesan / Kritis) adalah rancangan aplikasi ini,
bukan bagian dari jurnal. Fungsi di sini murni perhitungan (tanpa Streamlit)
supaya mudah diuji.
"""
import numpy as np
import pandas as pd

KOLOM = ["Bahan", "Satuan", "Total pemakaian", "Jumlah hari periode",
         "Lama pengiriman (hari)", "Stok sekarang"]
SATUAN = ["kg", "liter", "butir", "pcs", "pack"]
HARI_CADANGAN_AWAL = 3

# DATA CONTOH BUATAN (bukan dari jurnal). Pemakaian dihitung dari 7 hari terakhir.
DATA_CONTOH = pd.DataFrame({
    "Bahan": ["Ayam", "Beras", "Minyak goreng", "Telur", "Bawang putih"],
    "Satuan": ["kg", "kg", "liter", "kg", "kg"],
    "Total pemakaian": [140.0, 105.0, 42.0, 63.0, 14.0],
    "Jumlah hari periode": [7, 7, 7, 7, 7],
    "Lama pengiriman (hari)": [2, 3, 2, 1, 2],
    "Stok sekarang": [85.0, 130.0, 14.0, 40.0, 9.0],
})


def hitung(data: pd.DataFrame, hari_cadangan: float) -> pd.DataFrame:
    """Hitung pemakaian harian, stok pengaman, titik pesan ulang, dan status tiap bahan."""
    d = data["Total pemakaian"].astype(float) / data["Jumlah hari periode"].astype(float)
    ss = hari_cadangan * d
    rop = d * data["Lama pengiriman (hari)"].astype(float) + ss
    stok = data["Stok sekarang"].astype(float)
    status = np.where(stok <= ss + 1e-9, "Kritis",
                      np.where(stok <= rop + 1e-9, "Segera pesan", "Aman"))
    sisa = np.where(d > 0, stok / d.replace(0, np.nan), np.nan)
    hasil = pd.DataFrame({
        "Bahan": data["Bahan"].values,
        "Satuan": data["Satuan"].values,
        "Pemakaian per hari": d.values,
        "Stok pengaman": ss.values,
        "Titik pesan ulang": rop.values,
        "Stok sekarang": stok.values,
        "Sisa hari stok": sisa,
        "Status": status,
    })
    return hasil


def validasi(data: pd.DataFrame, hari_cadangan) -> list:
    """Daftar pesan kesalahan (kosong jika data aman)."""
    err = []
    if hari_cadangan is None or hari_cadangan < 0:
        err.append("Jumlah hari cadangan tidak boleh negatif.")
    if len(data) < 1:
        err.append("Isi minimal satu bahan baku.")
        return err
    if data["Bahan"].isna().any() or (data["Bahan"].astype(str).str.strip() == "").any():
        err.append("Nama bahan tidak boleh kosong.")
    elif data["Bahan"].duplicated().any():
        err.append("Nama bahan tidak boleh kembar.")
    angka = ["Total pemakaian", "Jumlah hari periode", "Lama pengiriman (hari)", "Stok sekarang"]
    if data[angka + ["Satuan"]].isna().any().any():
        err.append("Masih ada kolom yang kosong. Lengkapi semua data bahan.")
    else:
        if (data["Jumlah hari periode"] < 1).any():
            err.append("Jumlah hari periode minimal 1.")
        if (data[["Total pemakaian", "Lama pengiriman (hari)", "Stok sekarang"]] < 0).any().any():
            err.append("Pemakaian, lama pengiriman, dan stok tidak boleh negatif.")
    return err
