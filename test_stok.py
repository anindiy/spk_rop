import pandas as pd
from stok import *


def test_contoh_ayam():
    h = hitung(DATA_CONTOH, 3).set_index("Bahan")
    a = h.loc["Ayam"]
    assert a["Pemakaian per hari"] == 20 and a["Stok pengaman"] == 60 and a["Titik pesan ulang"] == 100
    assert a["Status"] == "Segera pesan"


def test_status_semua_bahan():
    h = hitung(DATA_CONTOH, 3).set_index("Bahan")["Status"].to_dict()
    assert h == {"Ayam": "Segera pesan", "Beras": "Aman", "Minyak goreng": "Kritis",
                 "Telur": "Aman", "Bawang putih": "Segera pesan"}


def test_hari_cadangan_nol():
    h = hitung(DATA_CONTOH, 0).set_index("Bahan")
    assert h.loc["Ayam", "Stok pengaman"] == 0
    assert h.loc["Ayam", "Titik pesan ulang"] == 40  # 20 x 2 hari


def test_batas_tepat():
    d = DATA_CONTOH.head(1).copy(); d["Stok sekarang"] = 100.0
    assert hitung(d, 3).loc[0, "Status"] == "Segera pesan"   # tepat di titik pesan ulang
    d["Stok sekarang"] = 60.0
    assert hitung(d, 3).loc[0, "Status"] == "Kritis"         # tepat di stok pengaman


def test_pemakaian_nol():
    d = DATA_CONTOH.head(1).copy(); d["Total pemakaian"] = 0.0
    h = hitung(d, 3)
    assert h.loc[0, "Status"] == "Aman"


def test_validasi():
    assert validasi(DATA_CONTOH, 3) == []
    assert validasi(DATA_CONTOH, -1)
    d = DATA_CONTOH.copy(); d.loc[1, "Bahan"] = "Ayam"
    assert validasi(d, 3)
    d = DATA_CONTOH.copy(); d.loc[0, "Jumlah hari periode"] = 0
    assert validasi(d, 3)
    assert validasi(DATA_CONTOH.head(0), 3)
