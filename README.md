# SPK Persediaan Bahan Baku (Safety Stock dan Reorder Point)

Aplikasi Streamlit untuk menentukan kapan bahan baku harus dipesan ulang.
Rumus dari Brahmantyo, Wibowo, & Nurcahyawati (2023), Jurnal Sains dan Informatika 9(1).
Data awal adalah CONTOH BUATAN (jurnal tidak memuat tabel angka).

## Menjalankan di komputer
    pip install -r requirements.txt
    streamlit run app.py

## Deploy ke Streamlit Community Cloud
1. Buat repositori GitHub baru, lalu unggah app.py, stok.py, dan requirements.txt.
2. Buka https://share.streamlit.io dan masuk dengan akun GitHub.
3. Pilih "Create app", pilih repositori dan branch, isi Main file path dengan `app.py`.
4. Klik Deploy.

## Struktur
- `app.py`       : tampilan Streamlit
- `stok.py`      : perhitungan (tanpa Streamlit)
- `test_stok.py` : pengujian; jalankan dengan `pytest`
