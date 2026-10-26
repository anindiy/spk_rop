import pandas as pd
import streamlit as st

import stok

st.set_page_config(page_title="SPK Persediaan Bahan Baku", page_icon="📦", layout="wide")

EMOJI = {"Kritis": "🔴 Kritis", "Segera pesan": "🟠 Segera pesan", "Aman": "🟢 Aman"}

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Pengaturan")
hari_cadangan = st.sidebar.number_input(
    "Hari cadangan (untuk stok pengaman)", min_value=0.0, max_value=60.0,
    value=float(stok.HARI_CADANGAN_AWAL), step=1.0, key="hari_cadangan",
    help="Berapa hari pemakaian yang ingin selalu tersimpan sebagai cadangan. "
         "Jurnal tidak menyebut angka ini, jadi nilai awal 3 hari hanyalah usulan.")
st.sidebar.caption("Contoh: 3 hari artinya selalu simpan bahan untuk pemakaian 3 hari ke depan sebagai cadangan.")

# ---------------------------------------------------------------- header
st.title("SPK Persediaan Bahan Baku")
st.caption("Menentukan kapan bahan baku harus dipesan ulang dengan stok pengaman (safety stock) "
           "dan titik pesan ulang (reorder point). Rumus dari Brahmantyo, Wibowo, & Nurcahyawati (2023), "
           "Jurnal Sains dan Informatika 9(1).")

tab_panduan, tab_data, tab_hasil, tab_langkah = st.tabs(
    ["Panduan", "1. Data", "2. Hasil keputusan", "3. Langkah hitung"])

# ---------------------------------------------------------------- panduan
with tab_panduan:
    st.subheader("Apa yang dihitung aplikasi ini?")
    st.markdown(
        "Bayangkan bensin motor. Kamu mengisi bensin bukan saat sudah kosong, tetapi saat sisa masih cukup "
        "untuk sampai ke SPBU, ditambah sedikit cadangan. Bahan baku restoran sama. Aplikasi ini menghitung "
        "kapan waktunya \"mengisi\" (memesan) bahan baku.")
    st.markdown(
        "**Dua rumus (dari jurnal)**\n\n"
        "- **Stok pengaman** = jumlah hari cadangan x pemakaian per hari\n"
        "- **Titik pesan ulang** = (pemakaian per hari x lama pengiriman) + stok pengaman")
    st.markdown(
        "**Contoh dengan ayam:** dipakai 20 kg per hari, cadangan 3 hari, pengiriman 2 hari.  \n"
        "Stok pengaman = 3 x 20 = **60 kg**.  \n"
        "Titik pesan ulang = (20 x 2) + 60 = **100 kg**.  \n"
        "Jadi begitu stok ayam tinggal 100 kg, saatnya pesan lagi.")
    st.subheader("Cara mengisi")
    st.markdown(
        "1. Buka tab **1. Data**. Tabel sudah berisi data **contoh buatan**, jadi tinggal ganti dengan data usahamu.\n"
        "2. **Total pemakaian**: berapa banyak bahan terpakai selama satu periode (misalnya 7 hari terakhir).\n"
        "3. **Jumlah hari periode**: lamanya periode itu (misalnya 7).\n"
        "4. **Lama pengiriman**: berapa hari dari pesan sampai barang datang.\n"
        "5. **Stok sekarang**: sisa bahan di gudang hari ini.\n"
        "6. Atur **hari cadangan** di panel kiri, lalu buka tab **2. Hasil keputusan**.")
    st.subheader("Cara membaca status")
    st.markdown(
        "- 🟢 **Aman**: stok masih di atas titik pesan ulang.\n"
        "- 🟠 **Segera pesan**: stok sudah sampai atau di bawah titik pesan ulang, tetapi masih di atas stok pengaman.\n"
        "- 🔴 **Kritis**: stok sudah menyentuh stok pengaman atau di bawahnya. Cadangan mulai terpakai.")
    with st.expander("Catatan tentang jurnal dan aplikasi ini"):
        st.markdown(
            "- Jurnal tidak memuat tabel angka, jadi data awal di sini adalah **contoh buatan**.\n"
            "- Jurnal tidak menyebut berapa hari cadangan yang dipakai. Nilai 3 hari adalah usulan.\n"
            "- Aturan status (Aman, Segera pesan, Kritis) dirancang untuk aplikasi ini, bukan dari jurnal.\n"
            "- Rumus stok pengaman di jurnal memakai rata-rata saja dan tidak memperhitungkan seberapa "
            "naik-turun pemakaian harian.\n"
            "- Aplikasi tidak menghitung jumlah yang harus dipesan, karena jurnal tidak membahasnya.")

# ---------------------------------------------------------------- data
with tab_data:
    st.subheader("Data bahan baku")
    st.write("Ubah nilai, tambah baris, atau hapus baris. Data awal adalah **contoh buatan**.")
    if "data" not in st.session_state:
        st.session_state["data"] = stok.DATA_CONTOH.copy()
    if st.button("Kembalikan data ke contoh"):
        st.session_state["data"] = stok.DATA_CONTOH.copy()
        st.session_state.pop("editor", None)
        st.rerun()
    data = st.data_editor(
        st.session_state["data"], key="editor", num_rows="dynamic", width="stretch", hide_index=True,
        column_config={
            "Bahan": st.column_config.TextColumn(required=True),
            "Satuan": st.column_config.SelectboxColumn(options=stok.SATUAN, required=True),
            "Total pemakaian": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%.1f", required=True,
                                                             help="Total bahan terpakai selama periode"),
            "Jumlah hari periode": st.column_config.NumberColumn(min_value=1, step=1, format="%d", required=True,
                                                                 help="Lama periode pemakaian dalam hari"),
            "Lama pengiriman (hari)": st.column_config.NumberColumn(min_value=0, step=1, format="%d", required=True,
                                                                    help="Hari dari pesan sampai barang datang"),
            "Stok sekarang": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%.1f", required=True),
        })
    data = data.reset_index(drop=True)
    errors = stok.validasi(data, hari_cadangan)
    for e in errors:
        st.error(e)

ok = not errors
if ok:
    hasil = stok.hitung(data, hari_cadangan)

# ---------------------------------------------------------------- hasil
with tab_hasil:
    if not ok:
        st.info("Perbaiki data pada tab Data terlebih dahulu.")
    else:
        n = hasil["Status"].value_counts()
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Kritis", int(n.get("Kritis", 0)))
        c2.metric("🟠 Segera pesan", int(n.get("Segera pesan", 0)))
        c3.metric("🟢 Aman", int(n.get("Aman", 0)))
        for _, r in hasil[hasil["Status"] == "Kritis"].iterrows():
            st.error(f"**{r['Bahan']}** kritis: stok {r['Stok sekarang']:.1f} {r['Satuan']} sudah di bawah "
                     f"stok pengaman {r['Stok pengaman']:.1f}. Pesan sekarang.")
        for _, r in hasil[hasil["Status"] == "Segera pesan"].iterrows():
            st.warning(f"**{r['Bahan']}**: stok {r['Stok sekarang']:.1f} {r['Satuan']} sudah mencapai titik pesan "
                       f"ulang {r['Titik pesan ulang']:.1f}. Saatnya memesan.")
        if n.get("Kritis", 0) + n.get("Segera pesan", 0) == 0:
            st.success("Semua bahan baku masih aman.")
        tampil = hasil.copy()
        tampil["Status"] = tampil["Status"].map(EMOJI)
        st.dataframe(
            tampil, width="stretch", hide_index=True,
            column_config={c: st.column_config.NumberColumn(format="%.1f") for c in
                           ["Pemakaian per hari", "Stok pengaman", "Titik pesan ulang", "Stok sekarang", "Sisa hari stok"]})
        st.download_button("Unduh hasil (CSV)", tampil.to_csv(index=False).encode("utf-8"),
                           file_name="hasil_persediaan.csv", mime="text/csv")
        st.subheader("Lihat per bahan")
        pilih = st.selectbox("Pilih bahan", hasil["Bahan"].tolist())
        r = hasil[hasil["Bahan"] == pilih].iloc[0]
        grafik = pd.DataFrame({"Jumlah": [r["Stok sekarang"], r["Stok pengaman"], r["Titik pesan ulang"]]},
                              index=["Stok sekarang", "Stok pengaman", "Titik pesan ulang"])
        st.bar_chart(grafik)
        st.caption(f"Satuan: {r['Satuan']}. Stok sekarang cukup untuk sekitar "
                   f"{r['Sisa hari stok']:.1f} hari pemakaian." if pd.notna(r["Sisa hari stok"])
                   else f"Satuan: {r['Satuan']}.")
        st.caption("Aplikasi ini membantu keputusan pemesanan, bukan menggantikan penilaian pengelola.")

# ---------------------------------------------------------------- langkah
with tab_langkah:
    if not ok:
        st.info("Perbaiki data pada tab Data terlebih dahulu.")
    else:
        st.markdown(f"Hari cadangan yang dipakai: **{hari_cadangan:g} hari**.")
        for (_, r), (_, d) in zip(hasil.iterrows(), data.iterrows()):
            with st.expander(f"{r['Bahan']} ({r['Satuan']}) - {EMOJI[r['Status']]}", expanded=False):
                st.markdown(
                    f"1. Pemakaian per hari = {d['Total pemakaian']:g} / {d['Jumlah hari periode']:g} "
                    f"= **{r['Pemakaian per hari']:.2f}**\n"
                    f"2. Stok pengaman = {hari_cadangan:g} x {r['Pemakaian per hari']:.2f} "
                    f"= **{r['Stok pengaman']:.2f}**\n"
                    f"3. Titik pesan ulang = ({r['Pemakaian per hari']:.2f} x {d['Lama pengiriman (hari)']:g}) "
                    f"+ {r['Stok pengaman']:.2f} = **{r['Titik pesan ulang']:.2f}**\n"
                    f"4. Stok sekarang **{r['Stok sekarang']:.2f}** dibandingkan dengan titik pesan ulang "
                    f"dan stok pengaman, sehingga statusnya **{r['Status']}**.")
