import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import warnings
import pandas as pd
import base64
from PIL import Image
import io
import requests

warnings.filterwarnings('ignore')

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="Simulasi Dispersi Cahaya pada Prisma",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    /* ========================================
     * CSS VARIABLES
     * ======================================== */
    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-info: #e8f4f8;
        --bg-warning: #fff3cd;
        --text-primary: #0e1117;
        --text-secondary: #262730;
        --border-color: #667eea;
    }

    [data-theme="dark"] {
        --bg-primary: #0e1117;
        --bg-secondary: #262730;
        --bg-info: #2d3748;
        --bg-warning: #4a3c00;
        --text-primary: #ffffff;
        --text-secondary: #e0e0e0;
        --border-color: #8b9dc3;
    }

    /* ========================================
     * HEADER - FORCE WHITE TEXT
     * ======================================== */
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }

    .main-header h1 {
        color: #ffffff !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p,
    .main-header strong,
    .main-header em {
        color: #f0f0f0 !important;
        margin: 10px 0 0 0;
        font-size: 1rem;
    }

    /* Override Streamlit default heading colors */
    .main-header h1,
    .main-header h2,
    .main-header h3,
    .main-header h4,
    .main-header h5,
    .main-header h6 {
        color: #ffffff !important;
    }

    /* ========================================
     * ALL HEADINGS OUTSIDE HEADER
     * ======================================== */
    h3, h2, h1, h4, h5, h6,
    .stMarkdown h3,
    .stMarkdown h2,
    .stMarkdown h1,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h1 {
        color: var(--text-primary) !important;
        font-weight: bold;
    }

    /* ========================================
     * PARAGRAPH & TEXT
     * ======================================== */
    p, .stMarkdown p,
    div[data-testid="stMarkdownContainer"] p,
    strong, b, em, i {
        color: var(--text-primary) !important;
    }

    /* ========================================
     * INFO BOX - FIX FORMATTING
     * ======================================== */
    .info-box {
        background: var(--bg-info) !important;
        padding: 15px !important;
        border-radius: 8px;
        border-left: 5px solid var(--border-color);
        margin: 10px 0;
        color: var(--text-primary) !important;
    }

    .info-box p,
    .info-box strong,
    .info-box em,
    .info-box li,
    .info-box h4,
    .info-box h3,
    .info-box table,
    .info-box td,
    .info-box th {
        color: var(--text-primary) !important;
    }

    .info-box ul,
    .info-box ol {
        margin: 10px 0;
        padding-left: 20px;
    }

    .info-box li {
        margin: 5px 0;
        line-height: 1.6;
    }

    /* ========================================
     * METRIC CARDS
     * ======================================== */
    div[data-testid="stMetric"] {
        background: var(--bg-secondary) !important;
        padding: 15px !important;
        border-radius: 8px;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
    }

    /* ========================================
     * SUCCESS/ALERT BOX
     * ======================================== */
    div[data-testid="stAlert"][role="alert"] {
        background: var(--bg-info) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        padding: 10px;
    }

    div[data-testid="stAlert"][role="alert"] p,
    div[data-testid="stAlert"][role="alert"] strong {
        color: var(--text-primary) !important;
    }

    /* ========================================
     * TABLE - HEADER TOP CENTER
     * ======================================== */
    .stDataFrame thead th,
    table thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: bold;
        text-align: center !important;
        vertical-align: top !important;
        padding: 12px;
        border: 1px solid #ffffff30;
    }

    .stDataFrame tbody td {
        color: var(--text-primary) !important;
        text-align: center !important;
        padding: 10px;
    }

    /* ========================================
     * BUTTONS
     * ======================================== */
    .stButton>button,
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
    }

    /* ========================================
     * SIDEBAR
     * ======================================== */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: var(--text-primary) !important;
    }

    /* ========================================
     * GENERAL
     * ======================================== */
    .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔬 Simulasi Dispersi Cahaya pada Prisma</h1>
    <p>Dikembangkan oleh <strong>Felix Marcellino Henrikus, S.Si.</strong></p>
    <p>Program Studi Magister Sains Data, UKSW Salatiga</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FUNGSI FISIKA
# ============================================================================

def cauchy_equation(wavelength_nm, A=1.5046, B=4.47e3, C=1.70e8):
    """
    Persamaan Cauchy untuk indeks bias
    n(λ) = A + B/λ² + C/λ⁴
    λ dalam nanometer (nm)
    """
    n = A + B / (wavelength_nm ** 2) + C / (wavelength_nm ** 4)
    return n

def sellmeier_equation(wavelength_nm, B1=1.03961212, B2=0.231792344, B3=1.01046945,
                       C1=6.00069867e-3, C2=2.00179144e-2, C3=1.03560653e2):
    """
    Persamaan Sellmeier untuk indeks bias (kaca BK7)
    n²(λ) = 1 + Σ(Bᵢλ²/(λ²-Cᵢ))
    λ dalam mikrometer
    """
    wavelength_um = wavelength_nm * 1e-3
    n_squared = 1 + (B1 * wavelength_um**2 / (wavelength_um**2 - C1)) + \
                    (B2 * wavelength_um**2 / (wavelength_um**2 - C2)) + \
                    (B3 * wavelength_um**2 / (wavelength_um**2 - C3))
    return np.sqrt(n_squared)

def calculate_deviation_angle(incident_angle_deg, prism_angle_deg, wavelength_nm, model='cauchy'):
    """
    Menghitung sudut deviasi berdasarkan hukum Snell
    δ = i₁ + i₂ - A
    """
    try:
        i1 = np.radians(incident_angle_deg)
        A = np.radians(prism_angle_deg)
        
        if model == 'cauchy':
            n = cauchy_equation(wavelength_nm)
        else:
            n = sellmeier_equation(wavelength_nm)
        
        if n <= 1.0:
            return None, None, None, None
        
        n_air = 1.0
        sin_r1 = n_air * np.sin(i1) / n
        
        if abs(sin_r1) > 1:
            return None, None, None, None
        
        r1 = np.arcsin(sin_r1)
        r2 = A - r1
        
        if r2 <= 0:
            return None, None, None, None
        
        sin_i2 = n * np.sin(r2) / n_air
        
        if abs(sin_i2) > 1:
            return None, None, None, None
        
        i2 = np.arcsin(sin_i2)
        delta = i1 + i2 - A
        
        return np.degrees(delta), np.degrees(r1), np.degrees(r2), np.degrees(i2)
    
    except Exception:
        return None, None, None, None

def get_spectrum_colors():
    """Mengembalikan array panjang gelombang dan warna spektrum"""
    wavelengths = [700, 620, 580, 530, 470, 420, 380]
    colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
    names = ['Merah', 'Jingga', 'Kuning', 'Hijau', 'Biru', 'Nila', 'Ungu']
    return wavelengths, colors, names

# ============================================================================
# SIDEBAR - INPUT PARAMETER
# ============================================================================
st.sidebar.header("⚙️ Parameter Simulasi")
st.sidebar.markdown("---")

incident_angle = st.sidebar.slider(
    "📐 Sudut Sinar Datang (i₁)",
    min_value=0.0,
    max_value=90.0,
    value=45.0,
    step=0.5,
    help="Sudut antara sinar datang dan garis normal permukaan prisma"
)

prism_angle = st.sidebar.slider(
    "🔺 Sudut Puncak Prisma (A)",
    min_value=30.0,
    max_value=90.0,
    value=60.0,
    step=0.5,
    help="Sudut apex prisma (default 60° untuk prisma sama kaki)"
)

refractive_index = st.sidebar.slider(
    "Indeks Bias (n)",
    min_value=1.40,
    max_value=1.90,
    value=1.52,
    step=0.01,
    help="Nilai indeks bias material prisma"
)

material_preset = st.sidebar.selectbox(
    "Preset Material",
    ["Custom", "Kaca Crown (n=1.52)", "Kaca Flint (n=1.65)", "Safir (n=1.77)", "Berlian (n=2.42)"],
    index=1
)

if material_preset != "Custom":
    preset_values = {
        "Kaca Crown (n=1.52)": 1.52,
        "Kaca Flint (n=1.65)": 1.65,
        "Safir (n=1.77)": 1.77,
        "Berlian (n=2.42)": 2.42
    }
    refractive_index = preset_values[material_preset]
    
dispersion_model = st.sidebar.selectbox(
    "📊 Model Dispersi",
    ['Cauchy', 'Sellmeier'],
    help="Pilih model dispersi untuk perhitungan indeks bias"
)

show_spectrum = st.sidebar.checkbox(
    "🌈 Tampilkan Spektrum Warna",
    value=True,
    help="Visualisasi dispersi warna pada sinar keluar"
)

show_angles = st.sidebar.checkbox(
    "📏 Tampilkan Label Sudut",
    value=True,
    help="Menampilkan label sudut pada diagram"
)

st.sidebar.markdown("---")
st.sidebar.info("""
    **Tips:**
    - Sudut deviasi minimum terjadi saat i₁ ≈ i₂
    - Untuk prisma 60°, sudut datang optimal sekitar 45-50°
    - Warna berbeda memiliki indeks bias berbeda
""")

# ============================================================================
# PERHITUNGAN HASIL
# ============================================================================
st.markdown("### 📊 Hasil Perhitungan")

wavelengths, colors, color_names = get_spectrum_colors()

results = []
for wl, color, name in zip(wavelengths, colors, color_names):
    model_key = 'cauchy' if dispersion_model == 'Cauchy' else 'sellmeier'
    delta, r1, r2, i2 = calculate_deviation_angle(incident_angle, prism_angle, wl, model_key)
    
    if model_key == 'cauchy':
        n = cauchy_equation(wl)
    else:
        n = sellmeier_equation(wl)
    
    if delta is not None:
        results.append({
            'warna': name,
            'wl': wl,
            'n': n,
            'delta': delta,
            'r1': r1,
            'r2': r2,
            'i2': i2,
            'color': color
        })

if results:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🔴 Sudut Deviasi (Merah)",
            value=f"{results[0]['delta']:.2f}°",
            help="Sudut deviasi untuk cahaya merah (700 nm)"
        )
    
    with col2:
        mid_idx = len(results) // 2
        st.metric(
            label="🟢 Sudut Deviasi (Hijau)",
            value=f"{results[mid_idx]['delta']:.2f}°",
            help="Sudut deviasi untuk cahaya hijau (550 nm)"
        )
    
    with col3:
        st.metric(
            label="🟣 Sudut Deviasi (Ungu)",
            value=f"{results[-1]['delta']:.2f}°",
            help="Sudut deviasi untuk cahaya ungu (380 nm)"
        )
    
    delta_range = results[-1]['delta'] - results[0]['delta']
    st.success(f"**🌈 Sudut Dispersi (Δδ):** {delta_range:.2f}°")
else:
    st.error("⚠️ Tidak ada hasil perhitungan. Coba ubah sudut datang atau sudut prisma.")
    st.warning("💡 **Saran:** Gunakan sudut datang antara 30°-60° dan sudut prisma 60°.")

# ============================================================================
# ILUSTRASI RAY TRACING - MENGGUNAKAN GAMBAR DARI REPO
# ============================================================================
st.markdown("---")
st.markdown("### 🔍 Ilustrasi Ray Tracing pada Prisma")

from pathlib import Path

image_path = Path("prisma_diagram.jpg")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if image_path.exists():
        st.image(
            str(image_path),
            caption="Diagram Skematik Dispersi Cahaya pada Prisma. Sumber: https://ivandwisandra.wordpress.com/jenis-jenis-polarisasi/",
            width=400,
            clamp=True
        )
        st.success("✅ Gambar berhasil dimuat")
    else:
        st.error("⚠️ File prisma_diagram.jpg tidak ditemukan!")
        st.info("💡 Pastikan file sudah diupload ke GitHub (sama folder dengan app.py)")

st.markdown("""
<div class="info-box">

**Keterangan Simbol:**

| Simbol | Deskripsi | Lokasi |
|--------|-----------|--------|
| **i₁** | Sudut datang | Luar prisma (sisi kiri) |
| **r₁** | Sudut bias pertama | Dalam prisma (sisi kiri) |
| **i₂** | Sudut datang kedua | Dalam prisma (sisi kanan) |
| **r₂** | Sudut bias kedua | Luar prisma (sisi kanan) |
| **A** | Sudut puncak prisma | Di apex prisma |
| **δ** | Sudut deviasi | Antara perpanjangan sinar datang & sinar keluar |

**Alur Cahaya:**

1. 🔦 **Sinar datang** (hitam): Dari kiri → masuk prisma di sisi kiri
2. 🔄 **Dibiaskan pertama** (i₁ → r₁): Sinar membelok ke arah normal
3. 🌈 **Dispersi dalam prisma**: Setiap warna memiliki indeks bias berbeda
4. 🔄 **Dibiaskan kedua** (i₂ → r₂): Sinar keluar di sisi kanan, membelok menjauhi normal
5. 🎨 **Spektrum terpisah**: Merah, jingga, kuning, hijau, biru, nila, ungu

</div>
""", unsafe_allow_html=True)

# ============================================================================
# FORMULASI MATEMATIS
# ============================================================================
st.markdown("---")
st.markdown("### 📐 Formulasi Matematis")

st.markdown("""
<div class="info-box">

#### 1. Hukum Snellius (Pembiasan)

$$n_1 \\sin(\\theta_1) = n_2 \\sin(\\theta_2)$$

**Keterangan:**
- $n_1$ = Indeks bias medium 1 (udara ≈ 1.0)
- $n_2$ = Indeks bias medium 2 (prisma)
- $\\theta_1$ = Sudut datang
- $\\theta_2$ = Sudut bias

---

#### 2. Sudut Deviasi pada Prisma

$$\\delta = i_1 + i_2 - A$$

**Keterangan:**
- $\\delta$ = Sudut deviasi
- $i_1$ = Sudut datang pada permukaan pertama
- $i_2$ = Sudut keluar pada permukaan kedua
- $A$ = Sudut puncak prisma

---

#### 3. Hubungan Sudut dalam Prisma

$$r_1 + r_2 = A$$

**Keterangan:**
- $r_1$ = Sudut bias pada permukaan pertama
- $r_2$ = Sudut datang pada permukaan kedua

---

#### 4. Persamaan Cauchy (Model Dispersi)

$$n(\\lambda) = A + \\frac{B}{\\lambda^2} + \\frac{C}{\\lambda^4}$$

**Keterangan:**
- $A, B, C$ = Konstanta material (empiris)
- $\\lambda$ = Panjang gelombang cahaya (nm)

---

#### 5. Persamaan Sellmeier (Model Dispersi)

$$n^2(\\lambda) = 1 + \\sum_{i=1}^{3} \\frac{B_i \\lambda^2}{\\lambda^2 - C_i}$$

**Keterangan:**
- $B_i, C_i$ = Koefisien Sellmeier (material-specific)
- Lebih akurat untuk rentang spektrum luas

</div>
""", unsafe_allow_html=True)

# ============================================================================
# TABEL DATA
# ============================================================================
st.markdown("---")
st.markdown("### 📋 Tabel Data Hasil Simulasi")

if results:
    df = pd.DataFrame(results)
    df_display = df[['warna', 'wl', 'n', 'delta']].copy()
    df_display.columns = ['Warna', 'λ (nm)', 'Indeks Bias (n)', 'Sudut Deviasi (°)']
    df_display['λ (nm)'] = df_display['λ (nm)'].astype(int)
    df_display['Indeks Bias (n)'] = df_display['Indeks Bias (n)'].round(4)
    df_display['Sudut Deviasi (°)'] = df_display['Sudut Deviasi (°)'].round(2)
    
    # Custom styling untuk tabel
    st.markdown("""
    <style>
    .custom-table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-table thead tr {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: left;
        font-weight: bold;
    }
    
    .custom-table th,
    .custom-table td {
        padding: 12px 15px;
        border: 1px solid #ddd;
    }
    
    .custom-table tbody tr {
        border-bottom: 1px solid #ddd;
    }
    
    .custom-table tbody tr:nth-of-type(even) {
        background-color: #f8f9fa;
    }
    
    .custom-table tbody tr:hover {
        background-color: #e8f4f8;
        cursor: pointer;
    }
    
    /* Dark mode untuk custom table */
    [data-theme="dark"] .custom-table tbody tr:nth-of-type(even) {
        background-color: #262730;
    }
    
    [data-theme="dark"] .custom-table tbody tr:hover {
        background-color: #2d3748;
    }
    
    [data-theme="dark"] .custom-table th,
    [data-theme="dark"] .custom-table td {
        border-color: #4a5568;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render tabel dengan HTML custom
    html_table = df_display.to_html(index=False, classes='custom-table', border=0)
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Atau tetap gunakan st.dataframe dengan styling
    # st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# GRAFIK: CAUCHY VS SELLMEIER (DINAMIS - TERGANTUNG MATERIAL)
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Model Dispersi: Cauchy vs Sellmeier (Dinamis)")

material_coefficients = {
    "Kaca Crown (n=1.52)": {
        'cauchy': {'A': 1.5046, 'B': 4.47e3, 'C': 1.70e8},
        'sellmeier': {'B1': 1.03961212, 'B2': 0.231792344, 'B3': 1.01046945,
                      'C1': 6.00069867e-3, 'C2': 2.00179144e-2, 'C3': 1.03560653e2}
    },
    "Kaca Flint (n=1.65)": {
        'cauchy': {'A': 1.6200, 'B': 5.50e3, 'C': 2.10e8},
        'sellmeier': {'B1': 1.3400, 'B2': 0.3100, 'B3': 1.2500,
                      'C1': 7.5e-3, 'C2': 2.5e-2, 'C3': 1.1e2}
    },
    "Safir (n=1.77)": {
        'cauchy': {'A': 1.7500, 'B': 6.20e3, 'C': 2.50e8},
        'sellmeier': {'B1': 1.4500, 'B2': 0.3500, 'B3': 1.3500,
                      'C1': 8.0e-3, 'C2': 2.8e-2, 'C3': 1.2e2}
    },
    "Berlian (n=2.42)": {
        'cauchy': {'A': 2.4000, 'B': 8.50e3, 'C': 3.50e8},
        'sellmeier': {'B1': 2.1000, 'B2': 0.5000, 'B3': 1.8000,
                      'C1': 1.0e-2, 'C2': 3.5e-2, 'C3': 1.5e2}
    }
}

if material_preset == "Custom":
    cauchy_params = {'A': 1.5046, 'B': 4.47e3, 'C': 1.70e8}
    sellmeier_params = {'B1': 1.03961212, 'B2': 0.231792344, 'B3': 1.01046945,
                        'C1': 6.00069867e-3, 'C2': 2.00179144e-2, 'C3': 1.03560653e2}
else:
    coeffs = material_coefficients[material_preset]
    cauchy_params = coeffs['cauchy']
    sellmeier_params = coeffs['sellmeier']

def cauchy_dynamic(wl, params):
    return params['A'] + params['B'] / (wl ** 2) + params['C'] / (wl ** 4)

def sellmeier_dynamic(wl, params):
    wl_um = wl * 1e-3
    n_sq = 1 + (params['B1'] * wl_um**2 / (wl_um**2 - params['C1'])) + \
               (params['B2'] * wl_um**2 / (wl_um**2 - params['C2'])) + \
               (params['B3'] * wl_um**2 / (wl_um**2 - params['C3']))
    return np.sqrt(n_sq)

wavelength_range = np.linspace(380, 750, 100)
n_cauchy_dyn = [cauchy_dynamic(wl, cauchy_params) for wl in wavelength_range]
n_sellmeier_dyn = [sellmeier_dynamic(wl, sellmeier_params) for wl in wavelength_range]

fig_dyn, ax_dyn = plt.subplots(figsize=(12, 6), dpi=100)
ax_dyn.plot(wavelength_range, n_cauchy_dyn, 'b-', linewidth=2.5, label='Cauchy', alpha=0.8)
ax_dyn.plot(wavelength_range, n_sellmeier_dyn, 'r--', linewidth=2.5, label='Sellmeier', alpha=0.8)

n_cauchy_550 = cauchy_dynamic(550, cauchy_params)
n_sellmeier_550 = sellmeier_dynamic(550, sellmeier_params)

ax_dyn.axvline(x=550, color='green', linestyle=':', alpha=0.5)
ax_dyn.scatter([550], [n_cauchy_550], color='blue', s=100, zorder=5)
ax_dyn.scatter([550], [n_sellmeier_550], color='red', s=100, zorder=5)

ax_dyn.set_xlabel('Panjang Gelombang (nm)', fontsize=12, fontweight='bold')
ax_dyn.set_ylabel('Indeks Bias (n)', fontsize=12, fontweight='bold')
ax_dyn.set_title(f'Model Dispersi untuk {material_preset}', fontsize=14, fontweight='bold', pad=15)
ax_dyn.legend(fontsize=11, loc='upper right')
ax_dyn.grid(True, alpha=0.3, linestyle='--')
ax_dyn.set_xlim(350, 780)

plt.tight_layout()
st.pyplot(fig_dyn)
plt.close(fig_dyn)

st.info(f"""
**Indeks bias pada λ = 550 nm:** 
- Cauchy = {n_cauchy_550:.4f}
- Sellmeier = {n_sellmeier_550:.4f}
""")

st.markdown("""
<div class="info-box">

**📝 Penjelasan:**

| Model | Kelebihan | Kekurangan |
|-------|-----------|------------|
| **Cauchy** | Sederhana, cepat dihitung | Akurat hanya untuk rentang λ terbatas |
| **Sellmeier** | Lebih akurat, rentang spektrum luas | Lebih kompleks, butuh lebih banyak parameter |

**💡 Catatan:** Untuk kaca optik standar (BK7), model Sellmeier memberikan akurasi hingga 10⁻⁶ pada indeks bias.

</div>
""", unsafe_allow_html=True)

# ============================================================================
# GRAFIK: DEVIASI VS SUDUT DATANG
# ============================================================================
st.markdown("---")
st.markdown("### 📊 Sudut Deviasi vs Sudut Datang")

incident_angles = np.linspace(30, 80, 100)
delta_red = []
delta_violet = []
valid_angles = []

model_key = 'cauchy' if dispersion_model == 'Cauchy' else 'sellmeier'

for i1 in incident_angles:
    d_r, _, _, _ = calculate_deviation_angle(i1, prism_angle, 700, model_key)
    d_v, _, _, _ = calculate_deviation_angle(i1, prism_angle, 380, model_key)
    
    delta_red.append(d_r if d_r is not None else np.nan)
    delta_violet.append(d_v if d_v is not None else np.nan)
    valid_angles.append(i1)

delta_red = np.array(delta_red)
delta_violet = np.array(delta_violet)
valid_angles = np.array(valid_angles)
valid_mask = ~(np.isnan(delta_red) | np.isnan(delta_violet))

if np.sum(valid_mask) > 0:
    fig3, ax3 = plt.subplots(figsize=(10, 6), dpi=100)
    fig3.patch.set_facecolor('#f8f9fa')
    ax3.set_facecolor('#ffffff')
    
    ax3.plot(valid_angles[valid_mask], delta_red[valid_mask], 'r-', linewidth=2.5, label='Merah (700 nm)', alpha=0.8)
    ax3.plot(valid_angles[valid_mask], delta_violet[valid_mask], 'v-', linewidth=2.5, label='Ungu (380 nm)', alpha=0.8)
    
    if incident_angle >= valid_angles[valid_mask].min() and incident_angle <= valid_angles[valid_mask].max():
        idx = np.argmin(np.abs(valid_angles[valid_mask] - incident_angle))
        ax3.axvline(x=incident_angle, color='blue', linestyle='--', linewidth=2, label=f'Sudut Saat Ini: {incident_angle}°')
        ax3.scatter([incident_angle], [delta_red[valid_mask][idx]], color='red', s=100, zorder=5)
        ax3.scatter([incident_angle], [delta_violet[valid_mask][idx]], color='purple', s=100, zorder=5)
    
    if len(delta_red[valid_mask]) > 0:
        min_delta_idx = np.argmin(delta_red[valid_mask])
        min_angle = valid_angles[valid_mask][min_delta_idx]
        min_delta = delta_red[valid_mask][min_delta_idx]
        ax3.scatter([min_angle], [min_delta], color='red', s=150, zorder=5, marker='*', label=f'Deviasi Min Merah: {min_delta:.2f}°')
    
    ax3.set_xlabel('Sudut Datang i₁ (°)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Sudut Deviasi δ (°)', fontsize=12, fontweight='bold')
    ax3.set_title('Hubungan Sudut Datang dan Sudut Deviasi', fontsize=14, fontweight='bold', pad=15)
    ax3.legend(fontsize=10, loc='upper right')
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)
else:
    st.warning("⚠️ Tidak ada data yang valid untuk grafik. Coba ubah sudut prisma menjadi lebih kecil (misalnya 60°).")

# ============================================================================
# GRAFIK: PENGARUH INDEKS BIAS
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Pengaruh Indeks Bias terhadap Sudut Deviasi")

n_values = np.linspace(1.4, 2.0, 100)
wavelengths_plot = [700, 550, 400]
colors_plot = ['#FF0000', '#00FF00', '#0000FF']
labels_plot = ['Merah (700 nm)', 'Hijau (550 nm)', 'Biru (400 nm)']

fig_n, ax_n = plt.subplots(figsize=(10, 6), dpi=100)

for wl, color, label in zip(wavelengths_plot, colors_plot, labels_plot):
    delta_values = []
    for n in n_values:
        A_rad = np.radians(prism_angle)
        try:
            sin_term = n * np.sin(A_rad / 2)
            if sin_term <= 1:
                delta_min = 2 * np.arcsin(sin_term) - A_rad
                delta_values.append(np.degrees(delta_min))
            else:
                delta_values.append(np.nan)
        except Exception:
            delta_values.append(np.nan)
    
    ax_n.plot(n_values, delta_values, color=color, linewidth=2.5, label=label, alpha=0.8)
    
    try:
        sin_term = refractive_index * np.sin(A_rad / 2)
        if sin_term <= 1:
            delta_current = 2 * np.arcsin(sin_term) - A_rad
            ax_n.scatter([refractive_index], [np.degrees(delta_current)], color=color, s=100, zorder=5, edgecolors='black')
    except Exception:
        pass

ax_n.axvline(x=refractive_index, color='gray', linestyle='--', linewidth=1, alpha=0.5, label=f'n saat ini: {refractive_index:.2f}')
ax_n.set_xlabel('Indeks Bias (n)', fontsize=12, fontweight='bold')
ax_n.set_ylabel('Sudut Deviasi Minimum δ (°)', fontsize=12, fontweight='bold')
ax_n.set_title('Hubungan Indeks Bias dan Sudut Deviasi', fontsize=14, fontweight='bold', pad=15)
ax_n.legend(fontsize=10, loc='upper left')
ax_n.grid(True, alpha=0.3, linestyle='--')
ax_n.set_xlim(1.4, 2.0)

plt.tight_layout()
st.pyplot(fig_n)
plt.close(fig_n)

st.markdown("""
<div class="info-box">
    <h4>💡 Interpretasi Grafik:</h4>
    <ul>
        <li>Semakin <strong>besar indeks bias (n)</strong>, semakin <strong>besar sudut deviasi (δ)</strong></li>
        <li>Cahaya dengan <strong>panjang gelombang lebih pendek</strong> (biru) memiliki indeks bias lebih besar → deviasi lebih besar</li>
        <li><strong>Dispersi</strong> = perbedaan deviasi antar warna → spektrum terpisah</li>
    </ul>
    
    <h4>📐 Rumus Sudut Deviasi Minimum:</h4>
    <p style="text-align: center; font-size: 1.2em; padding: 10px; background: var(--bg-secondary); border-radius: 5px;">
        $$\\delta_{\\text{min}} = 2 \\cdot \\arcsin\\!\\big(n \\cdot \\sin(A/2)\\big) - A$$
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box" style="background: var(--bg-warning);">
    <h4>📝 Catatan:</h4>
    <ul>
        <li>Kurva menunjukkan <strong>dispersi normal</strong>: n menurun saat λ meningkat</li>
        <li><strong>Dispersi tinggi</strong> = kurva lebih curam = pemisahan warna lebih jelas</li>
        <li>Material dengan dispersi tinggi (seperti flint glass) menghasilkan spektrum lebih lebar</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# KALKULATOR SUDUT DEVIASI MINIMUM
# ============================================================================
st.markdown("---")
st.markdown("### 🎯 Kalkulator Sudut Deviasi Minimum")

st.markdown("""
<div class="info-box">

**Rumus Sudut Deviasi Minimum:**

$$\\delta_{min} = 2 \\cdot \\arcsin\\left(n \\cdot \\sin\\left(\\frac{A}{2}\\right)\\right) - A$$

**Kondisi:** Terjadi saat $i_1 = r_2$ dan $r_1 = i_2$ (sinar simetris)

</div>
""", unsafe_allow_html=True)

if results:
    A_rad = np.radians(prism_angle)
    
    col_min1, col_min2, col_min3 = st.columns(3)
    
    for i, (result, col) in enumerate(zip([results[0], results[len(results)//2], results[-1]], 
                                           [col_min1, col_min2, col_min3])):
        n = result['n']
        try:
            sin_term = n * np.sin(A_rad / 2)
            if sin_term <= 1:
                delta_min = 2 * np.arcsin(sin_term) - A_rad
                delta_min_deg = np.degrees(delta_min)
                
                with col:
                    st.metric(
                        f"{result['warna']} (λ={result['wl']} nm)",
                        f"{delta_min_deg:.2f}°",
                        delta=f"{delta_min_deg - result['delta']:.2f}° vs saat ini"
                    )
            else:
                with col:
                    st.error(f"{result['warna']}: TIR")
        except Exception as e:
            with col:
                st.error(f"Error: {e}")
                
# ============================================================================
# GRAFIK: DISPERSI n vs λ
# ============================================================================
st.markdown("---")
st.markdown("### 🌈 Kurva Dispersi: n vs λ")

# ----------------------------------------
# 1. KOEFISIEN DINAMIS BERDASARKAN MATERIAL
# ----------------------------------------
material_coefficients = {
    "Kaca Crown (n=1.52)": {
        'cauchy': {'A': 1.5046, 'B': 4.47e3, 'C': 1.70e8},
        'sellmeier': {'B1': 1.03961212, 'B2': 0.231792344, 'B3': 1.01046945,
                      'C1': 6.00069867e-3, 'C2': 2.00179144e-2, 'C3': 1.03560653e2}
    },
    "Kaca Flint (n=1.65)": {
        'cauchy': {'A': 1.6200, 'B': 5.50e3, 'C': 2.10e8},
        'sellmeier': {'B1': 1.3400, 'B2': 0.3100, 'B3': 1.2500,
                      'C1': 7.5e-3, 'C2': 2.5e-2, 'C3': 1.1e2}
    },
    "Safir (n=1.77)": {
        'cauchy': {'A': 1.7500, 'B': 6.20e3, 'C': 2.50e8},
        'sellmeier': {'B1': 1.4500, 'B2': 0.3500, 'B3': 1.3500,
                      'C1': 8.0e-3, 'C2': 2.8e-2, 'C3': 1.2e2}
    },
    "Berlian (n=2.42)": {
        'cauchy': {'A': 2.4000, 'B': 8.50e3, 'C': 3.50e8},
        'sellmeier': {'B1': 2.1000, 'B2': 0.5000, 'B3': 1.8000,
                      'C1': 1.0e-2, 'C2': 3.5e-2, 'C3': 1.5e2}
    }
}

if material_preset == "Custom":
    base_A = refractive_index
    cauchy_params = {'A': base_A, 'B': 4.47e3, 'C': 1.70e8}
    sellmeier_params = {'B1': 1.03961212, 'B2': 0.231792344, 'B3': 1.01046945,
                        'C1': 6.00069867e-3, 'C2': 2.00179144e-2, 'C3': 1.03560653e2}
else:
    coeffs = material_coefficients[material_preset]
    cauchy_params = coeffs['cauchy']
    sellmeier_params = coeffs['sellmeier']

def cauchy_dynamic(wl, params):
    """Persamaan Cauchy dengan parameter dinamis"""
    return params['A'] + params['B'] / (wl ** 2) + params['C'] / (wl ** 4)

def sellmeier_dynamic(wl, params):
    """Persamaan Sellmeier dengan parameter dinamis"""
    wl_um = wl * 1e-3
    n_sq = 1 + (params['B1'] * wl_um**2 / (wl_um**2 - params['C1'])) + \
               (params['B2'] * wl_um**2 / (wl_um**2 - params['C2'])) + \
               (params['B3'] * wl_um**2 / (wl_um**2 - params['C3']))
    return np.sqrt(n_sq)

# ----------------------------------------
# 2. GENERATE DATA GRAFIK
# ----------------------------------------
wavelength_range = np.linspace(380, 750, 200)

model_key = 'cauchy' if dispersion_model == 'Cauchy' else 'sellmeier'
params_active = cauchy_params if model_key == 'cauchy' else sellmeier_params
func_active = cauchy_dynamic if model_key == 'cauchy' else sellmeier_dynamic

n_values_active = [func_active(wl, params_active) for wl in wavelength_range]

params_alt = sellmeier_params if model_key == 'cauchy' else cauchy_params
func_alt = sellmeier_dynamic if model_key == 'cauchy' else cauchy_dynamic
n_values_alt = [func_alt(wl, params_alt) for wl in wavelength_range]

# ----------------------------------------
# 3. PLOT GRAFIK
# ----------------------------------------
fig_disp, ax_disp = plt.subplots(figsize=(11, 7), dpi=100)
fig_disp.patch.set_facecolor('#f8f9fa')
ax_disp.set_facecolor('#ffffff')

line_style = '-' if model_key == 'cauchy' else '--'
ax_disp.plot(wavelength_range, n_values_active, 
             color='#667eea' if model_key == 'cauchy' else '#e74c3c', 
             linewidth=3, label=f'{dispersion_model} (Aktif)', alpha=0.9, zorder=5)

alt_style = '--' if model_key == 'cauchy' else '-'
ax_disp.plot(wavelength_range, n_values_alt, 
             color='gray', linewidth=1.5, 
             label=f'{"Sellmeier" if model_key == "cauchy" else "Cauchy"} (Pembanding)', 
             alpha=0.5, zorder=3)

spectrum_wl = [700, 620, 580, 530, 470, 420, 380]
spectrum_colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
spectrum_names = ['Merah', 'Jingga', 'Kuning', 'Hijau', 'Biru', 'Nila', 'Ungu']

for wl, color, name in zip(spectrum_wl, spectrum_colors, spectrum_names):
    n_val = func_active(wl, params_active)
    ax_disp.scatter([wl], [n_val], color=color, s=120, edgecolors='black', 
                    linewidth=1.5, zorder=6, label=name)

# ----------------------------------------
# 4. INFORMASI NILAI PADA PANJANG GELOMBANG TERTENTU
# ----------------------------------------
# Tampilkan nilai n pada 3 panjang gelombang referensi
ref_wavelengths = [400, 550, 700]
ref_labels = ['Violet (400 nm)', 'Hijau (550 nm)', 'Merah (700 nm)']

for wl_ref, label_ref in zip(ref_wavelengths, ref_labels):
    n_ref = func_active(wl_ref, params_active)
    ax_disp.axvline(x=wl_ref, color='gray', linestyle=':', alpha=0.3)
    ax_disp.text(wl_ref + 5, n_ref + 0.005, f'{label_ref}\nn = {n_ref:.4f}', 
                 fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# ============================================================================
# 5. FORMATTING GRAFIK
# ============================================================================
ax_disp.set_xlabel('Panjang Gelombang λ (nm)', fontsize=12, fontweight='bold')
ax_disp.set_ylabel('Indeks Bias (n)', fontsize=12, fontweight='bold')

# Title dinamis
title_text = f'Kurva Dispersi: {material_preset} ({dispersion_model})'
ax_disp.set_title(title_text, fontsize=14, fontweight='bold', pad=15)

# ========================================
# LEGEND DI LUAR GRAFIK (BAWAH SUMBU X)
# ========================================
legend_curves = ax_disp.legend(
    fontsize=9, 
    loc='upper center',
    bbox_to_anchor=(0.5, -0.18),
    ncol=2,
    framealpha=0.9,
    frameon=True,
    fancybox=True,
    shadow=False
)

# Atau jika ingin legend lebih rapi dengan 3 kolom:
# legend_curves = ax_disp.legend(
#     fontsize=9, 
#     loc='lower center',
#     bbox_to_anchor=(0.5, -0.25),
#     ncol=3,
#     framealpha=0.9,
#     frameon=True
# )

ax_disp.grid(True, alpha=0.3, linestyle='--')
ax_disp.set_xlim(370, 760)
ax_disp.invert_xaxis()
plt.tight_layout(rect=[0, 0.1, 1, 1]) 
plt.tight_layout()
st.pyplot(fig_disp)
plt.close(fig_disp)

# ----------------------------------------
# 6. INFO BOX DINAMIS
# ----------------------------------------
n_550 = func_active(550, params_active)
n_400 = func_active(400, params_active)
n_700 = func_active(700, params_active)
dispersion_power = n_400 - n_700 

st.markdown(f"""
<div class="info-box" style="background: var(--bg-warning);">

**📊 Informasi Material: {material_preset}**

| Panjang Gelombang | Indeks Bias (n) |
|------------------|-----------------|
| 🔴 Merah (700 nm) | {n_700:.4f} |
| 🟢 Hijau (550 nm) | {n_550:.4f} |
| 🔵 Violet (400 nm) | {n_400:.4f} |

**🌈 Kekuatan Dispersi:** Δn = n(400nm) - n(700nm) = **{dispersion_power:.4f}**

**📝 Catatan:**
- Kurva menunjukkan **dispersi normal**: n menurun saat λ meningkat
- Semakin **curam kurva**, semakin **kuat dispersi** → spektrum lebih terpisah
- Model **{dispersion_model}** digunakan untuk perhitungan ini

</div>
""", unsafe_allow_html=True)

# ============================================================================
# EXPORT DATA (CSV & PNG)
# ============================================================================
st.markdown("---")
st.markdown("### 💾 Export Data")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if results:
        df_export = pd.DataFrame(results)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f"prisma_data_i{incident_angle}_A{prism_angle}.csv",
            mime="text/csv",
            use_container_width=True  # Agar button full width
        )

with col_exp2:
    if 'fig_disp' in locals():
        buf = io.BytesIO()
        fig_disp.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download Grafik (PNG)",
            data=buf,
            file_name=f"prisma_dispersi_{material_preset.replace(' ', '_')}.png",
            mime="image/png",
            use_container_width=True
        )
    
# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")

footer_html = (
    "<div style='text-align: center; padding: 20px; "
    "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
    "border-radius: 10px; color: white; margin-top: 30px;'>"
    "<h4 style='margin: 0;'>🔬 Simulasi Dispersi Cahaya pada Prisma</h4>"
    "<p style='margin: 10px 0 0 0;'><em>Dikembangkan oleh Felix Marcellino Henrikus, S.Si.</em></p>"
    "<p style='margin: 5px 0 0 0; font-size: 14px;'>Program Studi Magister Sains Data, UKSW Salatiga</p>"
    "</div>"
)

st.markdown(footer_html, unsafe_allow_html=True)
