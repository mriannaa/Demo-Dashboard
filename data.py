import sqlite3
from matplotlib.pyplot import show
import streamlit as st
import pandas as pd 
import plotly.express as px
import numpy as np

# =========================================================
# KONFIGURASI HALAMAN & CSS 
# =========================================================
st.set_page_config(page_title="Always Healthy Hospital", layout="wide")

st.markdown(
    """
    <style>
    /* Mengatur Background Utama Aplikasi (Putih tulang yang bersih) */
    .stApp {
        background-color: #F8FAFC; 
    }

    /* 💙 Mengubah warna teks menjadi Biru Medis agar senada dengan palet */
    h1, h2, h3, p, div {
        color: #0F4C75; 
    }

    /* Mengatur Kartu Metrik (Executive Summary) Atas */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* 🏥 KARTU GRAFIK: Soft Medical Blue Card */
    [data-testid="stPlotlyChart"] {
        background-color: #E2E8F0 !important; 
        padding: 12px;
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        overflow: hidden !important; 
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F4C75 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html = True
)

# =========================================================
# PREPROCESSING DATASET
# =========================================================
@st.cache_data
def load_data():
    file_path = r"c:\Users\Downloads\dataset deka.csv"
    df = pd.read_csv(file_path, sep=None, engine='python')

    # Standarisasi Nama Kolom 
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Preprocessing Datetime
    if 'datetime' in df.columns:
        df['datetime'] = df['datetime'].astype(str).str.replace('.', ':', regex=False)
        df['date_dt'] = pd.to_datetime(df['datetime'], dayfirst=True, errors='coerce')
        df['tanggal'] = df['date_dt'].dt.date
        df['bulan'] = df['date_dt'].dt.to_period('M').astype(str)
       
    # Preprocessing Teks
    if 'branch' in df.columns:
        df['branch'] = df['branch'].str.replace('Always Healthy Hospital ', '', case=False, regex=False)
        df['branch'] = df['branch'].str.strip().str.title()
    if 'gender' in df.columns:
        df['gender'] = df['gender'].str.strip().str.title()
        
    # Standarisasi Metrik jadi numerik
    kpi_cols = ['nps', 'csi', 'loyalty', 'ces']
    for col in kpi_cols:
        df[col] = pd.to_numeric(df[col], errors = 'coerce') 

    return df  

df = load_data() 

# =========================================================
# MENU NAVIGASI (SIDEBAR)
# =========================================================
st.sidebar.title("Menu")
st.sidebar.write("---")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Executive Summary", "Detail Cabang", "Pasien"]
)
st.sidebar.write("---")
st.sidebar.caption("Always Healthy Hospital Dashboard © 2026")

# =========================================================
# PAGE 1: EXECUTIVE SUMMARY
# =========================================================
if menu == "Executive Summary":
    st.markdown("<h1 style='color: #0F4C75;'>Always Healthy Hospital</h1>", unsafe_allow_html = True)
    st.markdown("<h3 style='color: #0F4C75;'>Executive Summary</h3>", unsafe_allow_html = True)
    
    # 1. METRIK UTAMA (Semua Cabang)
    df_filtered = df.copy() 
    teks_judul = "Semua Cabang"
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("NPS (Net Promoter Score)", f"{df_filtered['nps'].mean():.2f}")
    kpi2.metric("CSI (Customer Satisfaction)", f"{df_filtered['csi'].mean():.2f}")
    kpi3.metric("Customer Loyalty", f"{df_filtered['loyalty'].mean():.2f}")
    kpi4.metric("Customer Effort Score", f"{df_filtered['ces'].mean():.2f}")
    
    st.write("---")
    
    col_kiri, col_kanan = st.columns(2)
    
    # 2. TREN KPI (Semua Cabang)
    with col_kiri:
        metrik_asli = ['nps', 'csi', 'loyalty', 'ces']
        df_trend = df_filtered.groupby('bulan')[metrik_asli].mean().reset_index()
        df_trend = df_trend.rename(columns={'nps': 'NPS', 'csi': 'CSI', 'loyalty': 'Loyalty', 'ces': 'CES'})
        metrik_tampil = ['NPS', 'CSI', 'Loyalty', 'CES']

        fig_line = px.line(
            df_trend, x = 'bulan', y = metrik_tampil, markers = True, height = 350,
            labels = {"value": "Skor", 'variable': '', 'bulan': ''} 
        )
        
        fig_line.update_layout(
            title = dict(text = f"<b>Tren KPI</b>", font = dict(size = 18, color = '#1E293B'), x = 0.02, y = 0.98),
            margin = {"r": 20, "t": 60, "l": 0, "b": 70}, 
            legend = dict(orientation = "h", yanchor = "top", y = 1.15, xanchor = "right", x = 1, title_text = ""),
            paper_bgcolor = '#E2E8F0', plot_bgcolor = '#E2E8F0', font = dict(color = '#1E293B') 
        )
        fig_line.update_xaxes(tickfont = dict(color = '#000000'), showgrid = True, gridwidth = 1, gridcolor = 'rgba(0, 0, 0, 0.15)', fixedrange = True)
        fig_line.update_yaxes(tickfont = dict(color = '#000000'), showgrid = True, gridwidth = 1, gridcolor = 'rgba(0, 0, 0, 0.15)', fixedrange = True)
        
        st.plotly_chart(fig_line, use_container_width = True, config = {'displayModeBar': False})
        
    # INSIGHT & REKOMENDASI (Semua Cabang)
        st.write("---")
        st.subheader("Feedback")

        if 'improvement_feedback' in df.columns:
            df_fb= df_filtered.dropna(subset=['improvement_feedback']).copy()
            df_fb['feedback_clean'] = df_fb['improvement_feedback'].astype(str).str.strip().str.lower()
            df_fb = df_fb[df_fb['feedback_clean'] != 'nan']

            total_fb = df_fb.shape[0]
            df_good = df_fb[df_fb['feedback_clean'] == 'service good']
            df_improve = df_fb[df_fb['feedback_clean'] != 'service good']
        
            jumlah_good = df_good.shape[0]
            jumlah_improve = df_improve.shape[0]

            persen_good = (jumlah_good / total_fb) * 100 if total_fb > 0 else 0
            persen_improve = (jumlah_improve / total_fb) * 100 if total_fb > 0 else 0    

            # 💡 Pengganti st.metric menjadi HTML Card Sejajar Kiri-Kanan
            st.markdown(f"""
            <div style="background-color: #F8FAFC; padding: 15px 20px; border-radius: 12px; border: 1px solid #E2E8F0; display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <p style="margin: 0px; font-size: 14px; color: #475569; font-weight: 600;">💬 Total Feedback - {teks_judul}</p>
                    <h2 style="margin: 5px 0px 0px 0px; color: #0F172A; font-size: 28px;">{total_fb} <span style="font-size: 13px; font-weight: normal; color: #64748B;">Data</span></h2>
                </div>
                <div style="display: flex; gap: 10px; flex: 1.2;">
                    <!-- Kotak Hijau untuk Service Good -->
                    <div style="flex: 1; background-color: #F0FDF4; padding: 10px; border-radius: 8px; border: 1px solid #BBF7D0;">
                        <p style="margin: 0px; font-size: 12px; color: #166534; font-weight: bold;">✅ Service Good</p>
                        <h4 style="margin: 3px 0px 0px 0px; color: #15803D; font-size: 18px;">{persen_good:.1f}% <span style="font-size:12px; font-weight:normal; color:#166534;">({jumlah_good})</span></h4>
                    </div>
                    <!-- Kotak Merah untuk Need Improve -->
                    <div style="flex: 1; background-color: #FEF2F2; padding: 10px; border-radius: 8px; border: 1px solid #FECACA;">
                        <p style="margin: 0px; font-size: 12px; color: #991B1B; font-weight: bold;">⚠️ Need Improve</p>
                        <h4 style="margin: 3px 0px 0px 0px; color: #B91C1C; font-size: 18px;">{persen_improve:.1f}% <span style="font-size:12px; font-weight:normal; color:#991B1B;">({jumlah_improve})</span></h4>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TOUCHPOINT (Semua Cabang)
    with col_kanan:
        tp_cols = ['registration', 'doctor_consultation', 'nurse_service', 'pharmacy_service', 
                   'laboratory', 'emergency_response', 'billing_process', 'facility_cleanliness', 
                   'staff_friendliness', 'waiting_time']
        
        df_tp = df_filtered[tp_cols].mean().reset_index()
        df_tp.columns = ['Touchpoint', 'Rata_rata']
        df_tp['Touchpoint'] = df_tp['Touchpoint'].str.replace('_', ' ').str.title()
        df_tp = df_tp.sort_values('Rata_rata', ascending = True)

        fig_bar = px.bar(
            df_tp, x = 'Rata_rata', y = 'Touchpoint', orientation = 'h', text_auto = '.2f', 
            color = 'Rata_rata', color_continuous_scale = 'Blues', height = 350, 
        )

        fig_bar.update_traces(textfont_size = 13, textposition = "inside")
        fig_bar.update_layout(
            title = dict(text = f"<b>Touchpoint</b>", font = dict(size = 18, color = '#1E293B'), x = 0.02, y = 0.98),
            margin = {"r": 20, "t": 60, "l": 0, "b": 70}, coloraxis_showscale = False, 
            yaxis_title = "", xaxis_title = "Rataan Skor Touchpoint",
            paper_bgcolor = '#E2E8F0', plot_bgcolor = '#E2E8F0', font = dict(color = '#1E293B'),
        )
        fig_bar.update_xaxes(tickfont = dict(color = '#000000'))
        fig_bar.update_yaxes(tickfont = dict(color = '#000000'))
        st.plotly_chart(fig_bar, use_container_width = True, config = {'displayModeBar': False})

        # BARCHART AREA PERBAIKAN (Semua Cabang)
        st.write("")
        tab_rincian, tab_insight = st.tabs(["📋 Rincian Area Perbaikan", "🔍 Kesimpulan & Tindak Lanjut"])
        
        
        with tab_rincian:
            if jumlah_improve > 0:
                teks_token = df_improve['feedback_clean'].str.replace('improve ', '', regex = False).str.split(',')
                df_exploded = teks_token.explode().str.strip().str.title()
                
                detil_improve = df_exploded.value_counts().reset_index()
                detil_improve.columns = ['Area Perbaikan', 'Jumlah Feedback']
                detil_improve['Persentase'] = (detil_improve['Jumlah Feedback'] / jumlah_improve) * 100
                detil_improve = detil_improve.sort_values('Persentase', ascending = True).reset_index(drop = True)

                fig_improve = px.bar(
                    detil_improve, x = 'Persentase', y = 'Area Perbaikan', orientation = 'h',
                    text_auto = '.1f', color = 'Persentase', color_continuous_scale = 'Reds', height = 350
                )
                fig_improve.update_traces(textangle = 0)

                fig_improve.update_layout(
                    title = dict(text = "<b>Distribusi Area Perbaikan Utama</b>", font = dict(size = 18, color = '#1E293B'), x = 0.02, y = 0.98),
                    margin = {"r": 30, "t": 60, "l": 0, "b": 70}, coloraxis_showscale = False, 
                    xaxis_title = "Persentase Keluhan (%)", yaxis_title = "",
                    paper_bgcolor = '#E2E8F0', plot_bgcolor = '#E2E8F0', font = dict(color = '#1E293B'),
                )
                fig_improve.update_xaxes(tickfont = dict(color = '#1E293B'), fixedrange=True)
                fig_improve.update_yaxes(tickfont = dict(color = '#1E293B'), fixedrange=True)
                
                st.plotly_chart(fig_improve, use_container_width = True, config = {'displayModeBar': False})
            else:
                st.success("🎉 Luar biasa! Tidak ada catatan keluhan yang masuk.")
        
        with tab_insight:
            st.info(f"**Kesimpulan Evaluasi:**\n* Sebesar **{persen_good:.1f}%** pasien sudah merasa puas dengan standar pelayanan yang ada.\n* Namun, porsi **{persen_improve:.1f}%** *feedback* negatif tidak boleh diabaikan, terutama rincian masalah yang paling mendominasi di *tab* sebelah.")
            st.success("**Rekomendasi Tindak Lanjut:**\n1. **Fokus pada Prioritas:** Perbaiki segera masalah yang menduduki peringkat teratas pada grafik rincian keluhan.\n2. **Sidak dan Pelatihan:** Jika keluhan berkaitan dengan keramahan atau prosedur, lakukan penyegaran SOP staf di titik pelayanan tersebut.")

# =========================================================
# PAGE 2: DETAIL CABANG 
# =========================================================
elif menu == "Detail Cabang":
    st.markdown("<h1 style='color: #0F4C75;'>Kinerja Cabang</h1>", unsafe_allow_html = True)
    
    col_left, col_right = st.columns([1.1, 1])

    # KINERJA CABANG (Alat Filter Utama)
    with col_left: 
        kpi_cols = ['nps', 'csi', 'loyalty', 'ces']
        df_rank = df.groupby('branch')[kpi_cols].mean().reset_index()
        df_rank['total_score'] = df_rank[kpi_cols].mean(axis = 1)
        df_rank = df_rank.sort_values('total_score', ascending = False).reset_index(drop = True)

        # 💡 PERUBAHAN 1: Tabel hanya mengambil Cabang dan Total Score
        df_tabel = df_rank[['branch', 'total_score']]
        df_tabel.columns = ["Nama Cabang", "Rataan KPI"]

        def beri_warna_peringkat(x):
            import pandas as pd
            df_css = pd.DataFrame('', index=x.index, columns=x.columns)
            total_baris = len(x)
            for i in range(total_baris):
                if i < 10: bg = '#D1FAE5'
                elif i >= total_baris - 10: bg = '#FEE2E2'
                else: bg = '#F1F5F9'
                df_css.iloc[i] = f'background-color: {bg}; color: #1E293B; border: 1px solid #CBD5E1; padding: 8px;'
            return df_css

        df_styled = df_tabel.style.apply(beri_warna_peringkat, axis=None)

        tabel_event = st.dataframe(
            df_styled, 
            use_container_width = True, 
            hide_index = True, 
            height = 500, 
            on_select = "rerun",           
            selection_mode = "single-row"  
        )

        selected_rows = tabel_event.selection.rows
        if len(selected_rows) > 0:
            selected_branch = df_tabel.iloc[selected_rows[0]]["Nama Cabang"]
            teks_judul = f"Cabang {selected_branch}"
            df_filtered = df[df['branch'] == selected_branch]
        else:
            selected_branch = "Semua Cabang"
            teks_judul = "Semua Cabang"
            df_filtered = df.copy()

    # 💡 PERUBAHAN 2: Menampilkan Rincian KPI di sebelah kanan tabel

        st.markdown(f"<h3 style='color: #0F4C75; margin-bottom: 20px;'>Rincian Metrik - {teks_judul}</h3>", unsafe_allow_html=True)
        
        # Menggunakan kolom 2x2 di dalam kolom kanan agar tampil layaknya kartu Executive Summary
        k1, k2 = st.columns(2)
        k1.metric("NPS (Net Promoter Score)", f"{df_filtered['nps'].mean():.2f}")
        k2.metric("CSI (Customer Satisfaction)", f"{df_filtered['csi'].mean():.2f}")
        
        st.write("") # Sedikit jarak antar baris kartu
        
        k3, k4 = st.columns(2)
        k3.metric("Customer Loyalty", f"{df_filtered['loyalty'].mean():.2f}")
        k4.metric("Customer Effort Score", f"{df_filtered['ces'].mean():.2f}")

#========================================================
# PAGE 3: PASIEN
#========================================================
elif menu == "Pasien":
    st.markdown("<h1 style='color: #0F4C75;'>Pasien</h1>", unsafe_allow_html=True)
    st.write("---")

    # 💡 KUNCI KOREKSI: Definisikan df_filtered dan teks_judul di sini agar tidak eror
    df_filtered = df.copy()
    teks_judul = "Semua Cabang"

    # JUMLAH PASIEN & DEMOGRAFI 
    total_pasien = len(df_filtered)
    jumlah_laki = len(df_filtered[df_filtered['gender'] == 'Male'])
    jumlah_perempuan = len(df_filtered[df_filtered['gender'] == 'Female'])
        
    str_total = f"{total_pasien:,.0f}".replace(",", ".")
    str_laki = f"{jumlah_laki:,.0f}".replace(",", ".")
    str_perempuan = f"{jumlah_perempuan:,.0f}".replace(",", ".")

    st.markdown(f"""
    <div style="background-color: #F8FAFC; padding: 15px 20px; border-radius: 12px; border: 1px solid #E2E8F0; display: flex; align-items: center; justify-content: space-between; gap: 20px;">
    <div style="flex: 1;">
    <p style="margin: 0px; font-size: 14px; color: #475569; font-weight: 600;">👥 Total Pasien - {teks_judul}</p>
    <h2 style="margin: 5px 0px 0px 0px; color: #0F172A; font-size: 28px;">{str_total} <span style="font-size: 13px; font-weight: normal; color: #64748B;">Orang</span></h2>
    </div>
    <div style="display: flex; gap: 10px; flex: 1.2;">
    <div style="flex: 1; background-color: #EFF6FF; padding: 10px; border-radius: 8px; border: 1px solid #BFDBFE;">
    <p style="margin: 0px; font-size: 12px; color: #1E3A8A; font-weight: bold;">👨 Laki-laki</p>
    <h4 style="margin: 3px 0px 0px 0px; color: #2563EB; font-size: 18px;">{str_laki}</h4>
    </div>
    <div style="flex: 1; background-color: #FDF2F8; padding: 10px; border-radius: 8px; border: 1px solid #FBCFE8;">
    <p style="margin: 0px; font-size: 12px; color: #831843; font-weight: bold;">👩 Perempuan</p>
    <h4 style="margin: 3px 0px 0px 0px; color: #DB2777; font-size: 18px;">{str_perempuan}</h4>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 

    # Bagi Area 
    col_kiri, col_kanan = st.columns(2)
    
    #=========================================
    # Area Kiri  
    with col_kiri:
    # GRAFIK DISTRIBUSI UMUR
        df_umur = df_filtered[['age']].copy()
        batas_umur = [0, 18, 26, 36, 46, 56, 150]
        label_umur = ['< 18', '18-25', '26-35', '36-45', '46-55', '> 55']
        df_umur['Rentang Umur'] = pd.cut(df_umur['age'], bins=batas_umur, labels=label_umur, right=False)

        df_age_count = df_umur['Rentang Umur'].value_counts().reset_index()
        df_age_count.columns = ['Rentang Umur', 'Jumlah'] 
        df_age_count['Rentang Umur'] = pd.Categorical(df_age_count['Rentang Umur'], categories=label_umur, ordered=True)
        df_age_count = df_age_count.sort_values('Rentang Umur')

        fig_age = px.bar(
            df_age_count, x = 'Rentang Umur', y = 'Jumlah', text_auto = True, 
            height = 360, color_discrete_sequence = ['#3B82F6']
        )
            
        fig_age.update_layout(
            title = dict(text = "<b>Distribusi Umur Pasien</b>", font = dict(size = 18, color = '#1E293B'), x = 0.02, y = 0.98),
            margin = {"r": 20, "t": 60, "l": 0, "b": 70}, 
            xaxis_title = "Rentang Umur", yaxis_title = "Jumlah Pasien",
            paper_bgcolor = '#E2E8F0', plot_bgcolor = '#E2E8F0', font = dict(color = '#1E293B') 
        )
        fig_age.update_xaxes(tickfont = dict(color = '#000000'), fixedrange = True)
        fig_age.update_yaxes(tickfont = dict(color = '#000000'), fixedrange = True, showgrid = True, gridcolor = 'rgba(0, 0, 0, 0.1)', showticklabels = False)
        
        st.plotly_chart(fig_age, use_container_width = True, config = {'displayModeBar': False})
    
    #========================================
    # Area kanan
    with col_kanan:
        # GRAFIK JUMLAH PASIEN PER BULAN
        # Menghitung jumlah baris data berdasarkan kolom 'bulan'
        df_bulan = df_filtered.groupby('bulan').size().reset_index(name='Jumlah')

        fig_bulan = px.line(
            df_bulan, x = 'bulan', y = 'Jumlah', markers = True, 
            height = 360, color_discrete_sequence = ['#0F4C75'], # Warna biru gelap medis
            labels = {"Jumlah": "Total Pasien", 'bulan': ''}
        )
        
        fig_bulan.update_layout(
            title = dict(text = "<b>Tren Pasien per Bulan</b>", font = dict(size = 18, color = '#1E293B'), x = 0.02, y = 0.98),
            margin = {"r": 20, "t": 60, "l": 0, "b": 70}, 
            paper_bgcolor = '#E2E8F0', plot_bgcolor = '#E2E8F0', font = dict(color = '#1E293B')
        )
        fig_bulan.update_xaxes(tickfont = dict(color = '#000000'), fixedrange = True, showgrid = True, gridwidth = 1, gridcolor = 'rgba(0, 0, 0, 0.1)')
        fig_bulan.update_yaxes(tickfont = dict(color = '#000000'), fixedrange = True, showgrid = True, gridwidth = 1, gridcolor = 'rgba(0, 0, 0, 0.1)')
        
        st.plotly_chart(fig_bulan, use_container_width = True, config = {'displayModeBar': False})