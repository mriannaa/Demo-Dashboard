import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr  # Diperlukan untuk menghitung p-value (Uji Signifikansi)

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Executive Performance Dashboard - Always Healthy Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - MENGGUNAKAN WARNA & SETTINGAN TERBARU DARI KAMU (INDIGO #6366f1 & SIMETRIS)
st.markdown("""
    <style>
    /* Background utama */
    .main { background-color: #f8f9fa; }
    
    /* =========================================================================
       KUSTOMISASI KOTAK METRIK (MEMBUAT ANGKA & JUDUL KE TENGAH SESUAI KODE KAMU)
       ========================================================================= */
    div[data-testid="stMetric"] {
        text-align: center !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 28px !important; 
        font-weight: bold !important; 
        color: #6366f1 !important; /* Warna Indigo Pilihanmu */
        width: 100% !important;
        text-align: center !important;
        margin-top: -5px !important;
    }
    
    div[data-testid="stMetricDelta"] { 
        font-size: 14px !important; 
        width: 100% !important;
        text-align: center !important;
    }
    
    .stAlert { border-radius: 8px; }
    
    /* Gaya Teks Berjalan */
    .marquee-text {
        font-size: 14px !important;
        font-weight: 700 !important;   /* Putih Tebal */
        color: #ffffff !important;     
        white-space: nowrap !important;
        display: block !important;
        width: 100% !important;
        margin-bottom: 2px !important;
    }
    
    /* KUSTOMISASI KOTAK FILTER MULTISELECT (GRADASI UNGU-PINK) */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-image: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border: none !important;
        border-radius: 6px !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] [role="button"] svg {
        fill: #ffffff !important;
    }
    div[data-baseweb="select"] > div {
        border-color: #a78bfa !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. LOAD DATA & PREPROCESSING
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('dataset deka.csv', sep=';')
    df.columns = df.columns.str.strip()
    
    # Konversi Datetime
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d/%m/%Y %H.%M', errors='coerce')
    df['Month'] = df['Datetime'].dt.to_period('M').astype(str)
    
    # Merapikan penamaan cabang
    df['Branch'] = df['Branch'].str.replace('Always Healthy Hospital ', 'RS ')
    
    # Menyamakan nama kolom loyalitas agar aman dari KeyError
    if 'Customer Loyalty Index (CLI)' in df.columns:
        df = df.rename(columns={'Customer Loyalty Index (CLI)': 'Loyalty'})
        
    # Pengelompokan umur untuk parameter Analisis Demografi
    bins = [0, 25, 45, 65, 100]
    labels = ['< 25 (Gen Z)', '25-44 (Milennial)', '45-64 (Gen X)', '65+ (Boomers)']
    df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels)
    
    return df

try:
    df_clean = load_and_clean_data()
except Exception as e:
    st.error(f"Gagal memuat file 'dataset deka.csv'. Error: {e}")
    st.stop()

# 3. SIDEBAR (FILTERS)
st.sidebar.header("🏥 Hospital Executive Filter")
st.sidebar.markdown("---")

# FITUR BARU: PILIHAN RENTANG WAKTU CEPAT (TIME SERIES FILTER)
st.sidebar.subheader("📅 Rentang Analisis Waktu")
time_range_option = st.sidebar.selectbox(
    "Pilih Periode Analisis:",
    ["Semua Periode", "3 Bulan Terakhir", "6 Bulan Terakhir", "10 Bulan Terakhir", "Kustom Bulan"]
)

# Mendapatkan daftar semua bulan unik yang terurut
all_months = sorted(df_clean['Month'].unique())

if time_range_option == "Semua Periode":
    selected_months = all_months
elif time_range_option == "3 Bulan Terakhir":
    selected_months = all_months[-3:]
elif time_range_option == "6 Bulan Terakhir":
    selected_months = all_months[-6:]
elif time_range_option == "10 Bulan Terakhir":
    selected_months = all_months[-10:]
else:
    # Jika memilih "Kustom Bulan", jalankan multiselect seperti biasa
    selected_months = st.sidebar.multiselect("Pilih Bulan Spesifik:", all_months, default=all_months)

# Filter Cabang Rumah Sakit
available_branches = sorted(df_clean['Branch'].unique())
selected_branches = st.sidebar.multiselect("Pilih Cabang Rumah Sakit (RS):", available_branches, default=available_branches)

# Aplikasi penyaringan data
df_filtered = df_clean[
    (df_clean['Month'].isin(selected_months)) & 
    (df_clean['Branch'].isin(selected_branches))
]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan tentukan filter kembali.")
    st.stop()

# 4. KALKULASI METRIK STATISTIK (MEAN)
current_nps = df_filtered['NPS'].mean()
bench_nps = df_clean['NPS'].mean()

current_csi = df_filtered['CSI'].mean()
bench_csi = df_clean['CSI'].mean()

current_pli = df_filtered['Loyalty'].mean() 
bench_pli = df_clean['Loyalty'].mean()

current_ces = df_filtered['CES'].mean()
bench_ces = df_clean['CES'].mean()

# 5. MAIN DASHBOARD LAYOUT
st.title("🏥 Patient Experience Executive Dashboard")
st.markdown("##### *Always Healthy Hospital — Strategic Insights & Quality Assurance Report*")
st.markdown("---")

# --- SECTION 1: METRIC CARD HEADER DENGAN ANIMASI TEKS BERJALAN ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<marquee class="marquee-text" scrollamount="4">Net Promoter Score (NPS)</marquee>', unsafe_allow_html=True)
    st.metric(label="", value=f"{current_nps:.2f}", delta=f"{current_nps - bench_nps:.2f} vs Bench")
with col2:
    st.markdown('<marquee class="marquee-text" scrollamount="4">Customer Satisfaction Index (CSI)</marquee>', unsafe_allow_html=True)
    st.metric(label="", value=f"{current_csi:.2f}", delta=f"{current_csi - bench_csi:.2f} vs Bench")
with col3:
    st.markdown('<marquee class="marquee-text" scrollamount="4">Patient Loyalty Index (PLI)</marquee>', unsafe_allow_html=True)
    st.metric(label="", value=f"{current_pli:.2f}", delta=f"{current_pli - bench_pli:.2f} vs Bench")
with col4:
    st.markdown('<marquee class="marquee-text" scrollamount="4">Customer Effort Score (CES)</marquee>', unsafe_allow_html=True)
    st.metric(label="", value=f"{current_ces:.2f}", delta=f"{current_ces - bench_ces:.2f} vs Bench")

st.markdown("---")

# --- SECTION 2: VISUALISASI UTAMA (TABS) ---
tab1, tab2 = st.tabs(["📈 Tren, Wilayah & Demografi", "📊 Analisis Atribut & Signifikansi (Deep-Dive)"])

with tab1:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("Tren Bulanan Metrik Utama (Time Series)")
        df_trend = df_filtered.groupby('Month').agg({'CSI': 'mean', 'Loyalty': 'mean', 'CES': 'mean'}).reset_index()
        
        fig_trend = px.line(
            df_trend, x='Month', y=['CSI', 'Loyalty', 'CES'],
            labels={'value': 'Skor Rata-rata', 'variable': 'Metrik'},
            markers=True,
            color_discrete_sequence=['#8b5cf6', '#ec4899', '#F59E0B']
        )
        fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_right:
        st.subheader("Peringkat Kinerja Cabang (Berdasarkan Rata-Rata NPS)")
        branch_nps_data = df_filtered.groupby('Branch')['NPS'].mean().reset_index()
        branch_nps_data = branch_nps_data.sort_values(by='NPS', ascending=True)
        
        fig_branch = px.bar(
            branch_nps_data, x='NPS', y='Branch',
            orientation='h',
            color='NPS',
            color_continuous_scale='Purples',
            labels={'NPS': 'Rata-rata NPS'}
        )
        fig_branch.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_branch, use_container_width=True)
        
    st.markdown("---")
    # TAMPILAN PARAMETER SEGMENTASI DEMOGRAFI
    st.subheader("👥 Segmentasi Kepuasan Pasien (Analisis Demografi)")
    col_demo1, col_demo2 = st.columns(2)
    
    with col_demo1:
        st.markdown("**Rata-rata CSI Berdasarkan Kelompok Umur**")
        df_age = df_filtered.groupby('Age_Group', observed=False)['CSI'].mean().reset_index()
        fig_age = px.bar(df_age, x='Age_Group', y='CSI', color='CSI', color_continuous_scale='Sunset')
        fig_age.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col_demo2:
        st.markdown("**Proporsi Pengisian Survei Berdasarkan Gender**")
        df_gender = df_filtered['Gender'].value_counts().reset_index()
        fig_gender = px.pie(df_gender, values='count', names='Gender', color_discrete_sequence=['#8b5cf6', '#ec4899'])
        st.plotly_chart(fig_gender, use_container_width=True)

with tab2:
    st.subheader("Analisis Driver Kepuasan Pasien (Korelasi vs Performa Aktual)")
    st.markdown("*Grafik memetakan aspek layanan mikro. Arahkan kursor pada poin untuk melihat nilai korelasi dan tingkat signifikansinya.*")
    
    touchpoints = [
        'Registration', 'Doctor Consultation', 'Nurse Service', 'Pharmacy Service', 
        'Laboratory', 'Emergency Response', 'Billing Process', 'Facility Cleanliness', 
        'Staff Friendliness', 'Waiting Time'
    ]
    
    # PERHITUNGAN KORELASI DAN P-VALUE (SIGNIFIKANSI STATISTIK)
    mean_scores = []
    correlations = []
    p_values = []
    significance = []
    
    for tp in touchpoints:
        mean_scores.append(df_filtered[tp].mean())
        valid_data = df_filtered[[tp, 'CSI']].dropna()
        if len(valid_data) > 1:
            corr, p_val = pearsonr(valid_data[tp], valid_data['CSI'])
        else:
            corr, p_val = 0, 1
            
        correlations.append(corr)
        p_values.append(p_val)
        significance.append("Signifikan (p < 0.05)" if p_val < 0.05 else "Tidak Signifikan (p >= 0.05)")
    
    df_driver = pd.DataFrame({
        'Aspek Layanan': touchpoints,
        'Skor Kepuasan Aktual': mean_scores,
        'Dampak terhadap Kepuasan (Korelasi)': correlations,
        'Nilai p-value': p_values,
        'Status Signifikansi': significance
    })
    
    fig_driver = px.scatter(
        df_driver, x='Skor Kepuasan Aktual', y='Dampak terhadap Kepuasan (Korelasi)',
        text='Aspek Layanan', size=[12]*len(df_driver), color='Status Signifikansi',
        color_discrete_map={'Signifikan (p < 0.05)': '#0d9488', 'Tidak Signifikan (p >= 0.05)': '#ef4444'},
        hover_data=['Nilai p-value']
    )
    fig_driver.update_traces(textposition='top center')
    st.plotly_chart(fig_driver, use_container_width=True)
    
    # Menampilkan Tabel Parameter Statistik Lengkap untuk Audit Mutu
    st.markdown("**Tabel Detail Ringkasan Parameter Statistik:**")
    st.dataframe(df_driver.style.format({
        'Skor Kepuasan Aktual': '{:.2f}', 
        'Dampak terhadap Kepuasan (Korelasi)': '{:.3f}', 
        'Nilai p-value': '{:.4e}'
    }), use_container_width=True)

st.markdown("---")

# --- SECTION 3: INSIGHT & RECOMMENDATION ---
st.subheader("💡 Executive Insights & Strategic Recommendations")

lowest_aspects = df_driver.sort_values(by='Skor Kepuasan Aktual').head(2)
worst_branch = branch_nps_data.sort_values(by='NPS').iloc[0] if not branch_nps_data.empty else None
best_branch = branch_nps_data.sort_values(by='NPS', ascending=False).iloc[0] if not branch_nps_data.empty else None

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.markdown("### 🩺 Fokus Perbaikan Layanan (*Immediate Action*)")
    if len(lowest_aspects) >= 2:
        st.info(
            f"1. **Optimasi Operasional:** Aspek **{lowest_aspects.iloc[0]['Aspek Layanan']}** saat ini memiliki "
            f"skor pelayanan terendah ({lowest_aspects.iloc[0]['Skor Kepuasan Aktual']:.2f}/5.0). Mengingat aspek ini memiliki tingkat "
            f"korelasi sebesar {lowest_aspects.iloc[0]['Dampak terhadap Kepuasan (Korelasi)']:.2f} dengan status **{lowest_aspects.iloc[0]['Status Signifikansi']}** terhadap kepuasan pasien (CSI), "
            f"perbaikan taktis di sektor ini diproyeksikan akan mendongkrak kepuasan makro secara nyata."
        )
        st.info(
            f"2. **Bottleneck Pelayanan:** Prioritas peningkatan mutu kedua jatuh pada **{lowest_aspects.iloc[1]['Aspek Layanan']}** "
            f"(Skor: {lowest_aspects.iloc[1]['Skor Kepuasan Aktual']:.2f}/5.0). Diperlukan evaluasi Standar Prosedur Operasional (SPO) klinis."
        )

with col_ins2:
    st.markdown("### 🏆 Analisis Komparatif Cabang RS (*Geospatial Performance*)")
    if worst_branch is not None and best_branch is not None:
        st.success(
            f"**Cabang RS Berkinerja Terbaik:** `{best_branch['Branch']}` memimpin dengan rata-rata NPS tertinggi sebesar **{best_branch['NPS']:.2f}**. "
            f"Manajemen pelayanan klinis di rumah sakit ini direkomendasikan menjadi *Best Practice* bagi unit kerja lainnya."
        )
        st.error(
            f"**Cabang RS Perlu Intervensi:** `{worst_branch['Branch']}` mencatat kinerja rata-rata NPS terendah yaitu **{worst_branch['NPS']:.2f}**. "
            f"Komite *Quality Assurance* disarankan untuk melakukan evaluasi performa pelayanan (*clinical audit*) yang mendalam di cabang ini."
        )