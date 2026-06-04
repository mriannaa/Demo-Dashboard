import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Executive Performance Dashboard - Always Healthy Hospital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan profesional & clean (Tema Gradasi Ungu-Pink)
st.markdown("""
    <style>
    /* Background utama */
    .main { background-color: #f8f9fa; }
    
    /* Angka KPI Utama (Warna Ungu Indigo agar serasi) */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #6366f1; }
    div[data-testid="stMetricDelta"] { font-size: 14px; }
    
    /* Kotak informasi/alert */
    .stAlert { border-radius: 8px; }
    
    /* =========================================================================
       KUSTOMISASI KOTAK FILTER MULTISELECT (GRADASI UNGU-PINK)
       ========================================================================= */
    
    /* 1. Mengubah background kotak pilihan (tag) menjadi gradasi ungu ke pink */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-image: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
    }
    
    /* 2. Memaksa warna teks di dalam kotak pilihan agar tetap putih */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* 3. Memaksa icon silang (x) penghapus filter menjadi warna putih */
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] [role="button"] svg {
        fill: #ffffff !important;
    }
    
    /* 4. Mengubah warna border luar kotak input filter saat aktif (warna ungu muda) */
    div[data-baseweb="select"] > div {
        border-color: #a78bfa !important;
    }
    </style>
""", unsafe_allow_html=True)


# 2. LOAD DATA & PREPROCESSING
@st.cache_data
def load_and_clean_data():
    # Membaca data dengan pemisah semicolon sesuai struktur awal
    df = pd.read_csv('dataset deka.csv', sep=';')
    
    # Konversi Datetime
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d/%m/%Y %H.%M', errors='coerce')
    df['Month'] = df['Datetime'].dt.to_period('M').astype(str)
    
    # Merapikan Penamaan Cabang Rumah Sakit (Misal: "Always Healthy Hospital Bandung" -> "RS Bandung")
    df['Branch'] = df['Branch'].str.replace('Always Healthy Hospital ', 'RS ')
    
    return df

try:
    df_clean = load_and_clean_data()
except Exception as e:
    st.error(f"Gagal memuat file 'dataset deka.csv'. Pastikan file berada di folder yang sama. Error: {e}")
    st.stop()

# 3. SIDEBAR (FILTERS)
st.sidebar.header("🏥 Hospital Executive Filter")
st.sidebar.markdown("---")

# Filter Waktu (Bulan)
available_months = sorted(df_clean['Month'].unique())
selected_months = st.sidebar.multiselect("Pilih Periode Bulan:", available_months, default=available_months)

# Filter Cabang Rumah Sakit
available_branches = sorted(df_clean['Branch'].unique())
selected_branches = st.sidebar.multiselect("Pilih Cabang Rumah Sakit (RS):", available_branches, default=available_branches)

# Aplikasi Filter ke Dataset
df_filtered = df_clean[
    (df_clean['Month'].isin(selected_months)) & 
    (df_clean['Branch'].isin(selected_branches))
]

# Proteksi jika filter kosong
if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter Anda. Silakan tentukan filter kembali.")
    st.stop()

# 4. KALKULASI METRIK STATISTIK (KPI RUMAH SAKIT)
def calculate_nps(nps_series):
    if len(nps_series) == 0: return 0
    promoters = (nps_series >= 9).sum()
    detractors = (nps_series <= 6).sum()
    total = len(nps_series)
    return ((promoters - detractors) / total) * 100

# Hitung Skor Aktual Saat Ini (Filtered) vs Benchmark (All Data)
current_nps = calculate_nps(df_filtered['NPS'])
bench_nps = calculate_nps(df_clean['NPS'])

current_csi = df_filtered['CSI'].mean()
bench_csi = df_clean['CSI'].mean()

current_cli = df_filtered['Loyalty'].mean()  # Menggunakan kolom asli 'Loyalty'
bench_cli = df_clean['Loyalty'].mean()

current_ces = df_filtered['CES'].mean()
bench_ces = df_clean['CES'].mean()


# 5. MAIN DASHBOARD LAYOUT
st.title("🏥 Patient Experience & Executive Dashboard")
st.markdown("##### *Always Healthy Hospital — Strategic Insights & Quality Assurance Report*")
st.markdown("---")

# --- SECTION 1: METRIC CARD HEADER ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Net Promoter Score (NPS)", 
        value=f"{current_nps:.1f}", 
        delta=f"{current_nps - bench_nps:.1f} vs Bench"
    )
with col2:
    st.metric(
        label="Customer Satisfaction Index (CSI)", 
        value=f"{current_csi:.2f} / 5.0", 
        delta=f"{current_csi - bench_csi:.2f} vs Bench"
    )
with col3:
    st.metric(
        label="Patient Loyalty Index", 
        value=f"{current_cli:.2f} / 5.0", 
        delta=f"{current_cli - bench_cli:.2f} vs Bench"
    )
with col4:
    st.metric(
        label="Customer Effort Score (CES)", 
        value=f"{current_ces:.2f} / 5.0", 
        delta=f"{current_ces - bench_ces:.2f} vs Bench"
    )

st.markdown("---")

# --- SECTION 2: VISUALISASI UTAMA (TABS) ---
tab1, tab2 = st.tabs(["📈 Tren & Analisis Wilayah", "📊 Analisis Atribut Layanan Rumah Sakit"])

with tab1:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("Tren Bulanan Metrik Utama (Time Series)")
        # Agregasi bulanan
        df_trend = df_filtered.groupby('Month').agg({
            'CSI': 'mean',
            'Loyalty': 'mean',
            'CES': 'mean'
        }).reset_index()
        
        fig_trend = px.line(
            df_trend, x='Month', y=['CSI', 'Loyalty', 'CES'],
            labels={'value': 'Skor Rata-rata', 'variable': 'Metrik'},
            markers=True,
            color_discrete_sequence=['#0284c7', '#10B981', '#F59E0B']
        )
        fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_right:
        st.subheader("Peringkat Kinerja Cabang (Berdasarkan NPS)")
        # Agregasi Cabang untuk NPS
        branch_nps_data = df_filtered.groupby('Branch')['NPS'].apply(calculate_nps).reset_index()
        branch_nps_data = branch_nps_data.sort_values(by='NPS', ascending=True)
        
        fig_branch = px.bar(
            branch_nps_data, x='NPS', y='Branch',
            orientation='h',
            color='NPS',
            color_continuous_scale='Tealgrn',
            labels={'NPS': 'Skor NPS'}
        )
        fig_branch.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_branch, use_container_width=True)

with tab2:
    st.subheader("Analisis Driver Kepuasan Pasien (Korelasi vs Performa Aktual)")
    st.markdown(
        "*Grafik ini memetakan aspek pelayanan rumah sakat secara mikro. Aspek dengan korelasi tinggi terhadap CSI memiliki dampak strategis besar.*"
    )
    
    # List aspek layanan asli rumah sakit dari dataset deka.csv
    touchpoints = [
        'Registration', 'Doctor Consultation', 'Nurse Service', 
        'Pharmacy Service', 'Laboratory', 'Emergency Response', 
        'Billing Process', 'Facility Cleanliness', 'Staff Friendliness', 
        'Waiting Time'
    ]
    
    # Hitung Mean dan Korelasi Pearson terhadap CSI
    mean_scores = df_filtered[touchpoints].mean()
    correlations = df_filtered[touchpoints].corrwith(df_filtered['CSI'])
    
    df_driver = pd.DataFrame({
        'Aspek Layanan': touchpoints,
        'Skor Kepuasan Aktual': mean_scores,
        'Dampak terhadap Kepuasan (Korelasi)': correlations
    }).reset_index(drop=True)
    
    fig_driver = px.scatter(
        df_driver, 
        x='Skor Kepuasan Aktual', 
        y='Dampak terhadap Kepuasan (Korelasi)',
        text='Aspek Layanan',
        size=[12]*len(df_driver),
        color='Skor Kepuasan Aktual',
        color_continuous_scale='RdYlGn'
    )
    fig_driver.update_traces(textposition='top center')
    fig_driver.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_driver, use_container_width=True)

st.markdown("---")

# --- SECTION 3: INSIGHT & RECOMMENDATION (AUTOMATED STATISTICAL INSIGHTS) ---
st.subheader("💡 Executive Insights & Strategic Recommendations")

# Cari 2 aspek dengan skor terendah dari analisis driver untuk dijadikan rekomendasi otomatis
lowest_aspects = df_driver.sort_values(by='Skor Kepuasan Aktual').head(2)
worst_branch = branch_nps_data.sort_values(by='NPS').iloc[0] if not branch_nps_data.empty else None
best_branch = branch_nps_data.sort_values(by='NPS', ascending=False).iloc[0] if not branch_nps_data.empty else None

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.markdown("### 🎯 Fokus Perbaikan Layanan (*Immediate Action*)")
    if len(lowest_aspects) >= 2:
        st.info(
            f"1. **Optimasi Operasional:** Aspek **{lowest_aspects.iloc[0]['Aspek Layanan']}** saat ini memiliki "
            f"skor pelayanan terendah ({lowest_aspects.iloc[0]['Skor Kepuasan Aktual']:.2f}/5.0). Mengingat aspek ini memiliki tingkat "
            f"korelasi sebesar {lowest_aspects.iloc[0]['Dampak terhadap Kepuasan (Korelasi)']:.2f} terhadap kepuasan pasien (CSI), "
            f"perbaikan taktis di sektor ini diproyeksikan akan mendongkrak kepuasan makro secara signifikan."
        )
        st.info(
            f"2. **Bottleneck Pelayanan:** Prioritas peningkatan mutu kedua jatuh pada **{lowest_aspects.iloc[1]['Aspek Layanan']}** "
            f"(Skor: {lowest_aspects.iloc[1]['Skor Kepuasan Aktual']:.2f}/5.0). Diperlukan evaluasi Standar Prosedur Operasional (SPO) klinis atau peningkatan kapasitas petugas."
        )

with col_ins2:
    st.markdown("### 🏆 Analisis Komparatif Cabang RS (*Geospatial Performance*)")
    if worst_branch is not None and best_branch is not None:
        st.success(
            f"**Cabang RS Berkinerja Terbaik:** `{best_branch['Branch']}` memimpin dengan NPS tertinggi sebesar **{best_branch['NPS']:.1f}**. "
            f"Manajemen pelayanan klinis dan non-klinis di rumah sakit ini direkomendasikan menjadi *Role Model* bagi unit kerja lainnya."
        )
        st.error(
            f"**Cabang RS Perlu Intervensi:** `{worst_branch['Branch']}` mencatat kinerja NPS terendah yaitu **{worst_branch['NPS']:.1f}**. "
            f"Komite *Quality Assurance* disarankan untuk melakukan evaluasi performa pelayanan (*clinical audit*) yang mendalam di cabang ini."
        )