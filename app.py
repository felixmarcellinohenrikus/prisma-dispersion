import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import warnings
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
        color: white;
    }
    .info-box {
        background: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1 style='margin: 0;'>🔬 Simulasi Dispersi Cahaya pada Prisma</h1>
    <p style='margin: 10px 0 0 0; font-size: 16px;'>
        Dikembangkan oleh <strong>Felix Marcellino Henrikus, S.Si</strong>
    </p>
    <p style='margin: 10px 0 0 0; font-size: 16px;'>
        Program Studi Magister Sains Data, UKSW Salatiga
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FUNGSI FISIKA - DIPERBAIKI
# ============================================================================

def cauchy_equation(wavelength_nm, A=1.5046, B=4.47e3, C=1.70e8):
    """
    Persamaan Cauchy untuk indeks bias
    n(λ) = A + B/λ² + C/λ⁴
    λ dalam nanometer (nm)
    Koefisien yang diperbaiki untuk satuan nm
    """
    # Menggunakan satuan nm secara langsung
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
        
        # Hitung indeks bias
        if model == 'cauchy':
            n = cauchy_equation(wavelength_nm)
        else:
            n = sellmeier_equation(wavelength_nm)
        
        # Validasi indeks bias
        if n <= 1.0:
            return None, None, None, None
        
        n_air = 1.0
        
        # Pembiasan pertama: udara -> prisma
        sin_r1 = n_air * np.sin(i1) / n
        
        # Cek total internal reflection di permukaan pertama
        if abs(sin_r1) > 1:
            return None, None, None, None
        
        r1 = np.arcsin(sin_r1)
        
        # Sudut di dalam prisma
        r2 = A - r1
        
        # Cek apakah sinar bisa keluar dari prisma
        if r2 <= 0:
            return None, None, None, None
        
        # Pembiasan kedua: prisma -> udara
        sin_i2 = n * np.sin(r2) / n_air
        
        # Cek total internal reflection di permukaan kedua
        if abs(sin_i2) > 1:
            return None, None, None, None
        
        i2 = np.arcsin(sin_i2)
        
        # Hitung sudut deviasi
        delta = i1 + i2 - A
        
        return np.degrees(delta), np.degrees(r1), np.degrees(r2), np.degrees(i2)
    
    except Exception as e:
        return None, None, None, None

def get_spectrum_colors():
    """Mengembalikan array panjang gelombang dan warna spektrum"""
    wavelengths = [700, 620, 580, 530, 470, 420, 380]  # nm
    colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
    names = ['Merah', 'Jingga', 'Kuning', 'Hijau', 'Biru', 'Nila', 'Ungu']
    return wavelengths, colors, names

# ============================================================================
# SIDEBAR
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

# Slider untuk indeks bias (range umum kaca: 1.4 - 1.9)
refractive_index = st.sidebar.slider(
    "Indeks Bias (n)",
    min_value=1.40,
    max_value=1.90,
    value=1.52,
    step=0.01,
    help="Nilai indeks bias material prisma (kaca: ~1.5, flint: ~1.6-1.9)"
)

# Pilihan material preset
material_preset = st.sidebar.selectbox(
    "Preset Material",
    ["Custom", "Kaca Crown (n=1.52)", "Kaca Flint (n=1.65)", "Safir (n=1.77)", "Berlian (n=2.42)"],
    index=1
)

# Update indeks bias berdasarkan preset
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
# PERHITUNGAN
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
            "🔴 Sudut Deviasi (Merah)",
            f"{results[0]['delta']:.2f}°"
        )
    
    with col2:
        mid_idx = len(results) // 2
        st.metric(
            "🟢 Sudut Deviasi (Hijau)",
            f"{results[mid_idx]['delta']:.2f}°"
        )
    
    with col3:
        st.metric(
            "🟣 Sudut Deviasi (Ungu)",
            f"{results[-1]['delta']:.2f}°"
        )
    
    delta_range = results[-1]['delta'] - results[0]['delta']
    st.success(f"**🌈 Sudut Dispersi (Δδ):** {delta_range:.2f}°")
else:
    st.error("⚠️ Tidak ada hasil perhitungan. Coba ubah sudut datang atau sudut prisma.")
    st.warning("💡 **Saran:** Gunakan sudut datang antara 30°-60° dan sudut prisma 60° untuk visualisasi yang ideal.")

# ============================================================================
# ILUSTRASI STATIS RAY TRACING
# ============================================================================
st.markdown("---")
st.markdown("### 🔍 Ilustrasi Ray Tracing pada Prisma")

st.markdown("""
<div style='background: white; padding: 20px; border-radius: 10px; border: 2px solid #667eea;'>

**Diagram Skematik Dispersi Cahaya pada Prisma:**

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Prism_rainbow.svg/800px-Prism_rainbow.svg.png" 
     alt="Prisma Dispersi" 
     style="width: 100%; max-width: 600px; display: block; margin: 20px auto;">

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
1. 🔦 Sinar putih datang dari kiri → memasuki prisma
2. 🔄 Dibiaskan pertama kali (i₁ → r₁) 
3. 🌈 Terjadi dispersi: setiap warna punya indeks bias berbeda
4. 🔄 Dibiaskan kedua kali (i₂ → r₂) saat keluar prisma
5. 🎨 Spektrum warna terpisah di luar prisma

</div>
""", unsafe_allow_html=True)

# Atau jika ingin membuat ilustrasi sederhana dengan matplotlib:
def create_static_illustration(prism_angle, incident_angle, n_value):
    """Membuat ilustrasi statis sederhana"""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    
    # Prism
    apex = np.array([0, 3])
    base_left = np.array([-2.5, 0])
    base_right = np.array([2.5, 0])
    prism = Polygon([apex, base_left, base_right], 
                    fill=True, alpha=0.2, edgecolor='black', facecolor='skyblue')
    ax.add_patch(prism)
    
    # Incident ray (simplified)
    entry = base_left + 0.4 * (apex - base_left)
    ax.plot([-4, entry[0]], [-1, entry[1]], 'k-', linewidth=2)
    
    # Internal ray
    exit_point = apex + 0.5 * (base_right - apex)
    ax.plot([entry[0], exit_point[0]], [entry[1], exit_point[1]], 
            'b-', linewidth=1.5, alpha=0.7)
    
    # Emergent spectrum (simplified)
    colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
    for i, color in enumerate(colors):
        angle_offset = -0.1 + i * 0.04
        ax.plot([exit_point[0], exit_point[0] + 3], 
                [exit_point[1], exit_point[1] - 1 + angle_offset],
                color=color, linewidth=2, alpha=0.8)
    
    # Labels
    ax.text(entry[0]-0.8, entry[1]+0.3, 'i₁', fontsize=10, fontweight='bold')
    ax.text(entry[0]+0.3, entry[1]-0.3, 'r₁', fontsize=10, fontweight='bold')
    ax.text(exit_point[0]-0.4, exit_point[1]-0.3, 'i₂', fontsize=10, fontweight='bold')
    ax.text(exit_point[0]+0.5, exit_point[1]+0.2, 'r₂', fontsize=10, fontweight='bold')
    ax.text(0, 3.3, f'A={prism_angle}°', fontsize=10, ha='center')
    
    ax.set_xlim(-5, 5)
    ax.set_ylim(-1, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    return fig

# Tampilkan ilustrasi sederhana
fig_static = create_static_illustration(prism_angle, incident_angle, 1.5)
st.pyplot(fig_static)
plt.close(fig_static)

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
    import pandas as pd
    
    df = pd.DataFrame(results)
    df_display = df[['warna', 'wl', 'n', 'delta']].copy()
    df_display.columns = ['Warna', 'λ (nm)', 'Indeks Bias (n)', 'Sudut Deviasi (°)']
    df_display['λ (nm)'] = df_display['λ (nm)'].astype(int)
    df_display['Indeks Bias (n)'] = df_display['Indeks Bias (n)'].round(4)
    df_display['Sudut Deviasi (°)'] = df_display['Sudut Deviasi (°)'].round(2)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# GRAFIK DISPERSI
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Fitting Model Dispersi: Cauchy vs Sellmeier")

wavelength_range = np.linspace(380, 750, 100)
n_cauchy = [cauchy_equation(wl) for wl in wavelength_range]
n_sellmeier = [sellmeier_equation(wl) for wl in wavelength_range]

fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=100)
fig2.patch.set_facecolor('#f8f9fa')
ax2.set_facecolor('#ffffff')

ax2.plot(wavelength_range, n_cauchy, 'b-', linewidth=2.5, 
         label='Model Cauchy', alpha=0.8)
ax2.plot(wavelength_range, n_sellmeier, 'r--', linewidth=2.5, 
         label='Model Sellmeier', alpha=0.8)

for wl, color in zip(wavelengths, colors):
    n_c = cauchy_equation(wl)
    n_s = sellmeier_equation(wl)
    ax2.scatter([wl], [n_c], color=color, s=100, zorder=5, 
                edgecolors='black', linewidth=1)
    ax2.scatter([wl], [n_s], color=color, s=100, marker='s', zorder=5,
                edgecolors='black', linewidth=1)

ax2.set_xlabel('Panjang Gelombang (nm)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Indeks Bias (n)', fontsize=12, fontweight='bold')
ax2.set_title('Perbandingan Model Dispersi Cauchy vs Sellmeier', 
              fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=11, loc='upper right')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_xlim(350, 780)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

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
# GRAFIK DEVIASI VS SUDUT DATANG - DIPERBAIKI
# ============================================================================
st.markdown("---")
st.markdown("### 📊 Sudut Deviasi vs Sudut Datang")

incident_angles = np.linspace(30, 80, 100)
delta_red = []
delta_violet = []
valid_angles = []

model_key = 'cauchy' if dispersion_model == 'Cauchy' else 'sellmeier'

# Hitung semua sudut deviasi
for i1 in incident_angles:
    d_r, _, _, _ = calculate_deviation_angle(i1, prism_angle, 700, model_key)
    d_v, _, _, _ = calculate_deviation_angle(i1, prism_angle, 380, model_key)
    
    # Simpan semua nilai (gunakan None jika tidak valid)
    if d_r is not None:
        delta_red.append(d_r)
    else:
        delta_red.append(np.nan)
    
    if d_v is not None:
        delta_violet.append(d_v)
    else:
        delta_violet.append(np.nan)
    
    valid_angles.append(i1)

# Konversi ke numpy array dan filter NaN
delta_red = np.array(delta_red)
delta_violet = np.array(delta_violet)
valid_angles = np.array(valid_angles)

# Buat mask untuk data yang valid (kedua warna harus valid)
valid_mask = ~(np.isnan(delta_red) | np.isnan(delta_violet))

if np.sum(valid_mask) > 0:
    fig3, ax3 = plt.subplots(figsize=(10, 6), dpi=100)
    fig3.patch.set_facecolor('#f8f9fa')
    ax3.set_facecolor('#ffffff')
    
    # Plot hanya data yang valid
    ax3.plot(valid_angles[valid_mask], delta_red[valid_mask], 'r-', linewidth=2.5, 
             label='Merah (700 nm)', alpha=0.8)
    ax3.plot(valid_angles[valid_mask], delta_violet[valid_mask], 'v-', linewidth=2.5, 
             label='Ungu (380 nm)', alpha=0.8)
    
    # Tambahkan garis vertikal untuk sudut saat ini (jika dalam range valid)
    if incident_angle >= valid_angles[valid_mask].min() and incident_angle <= valid_angles[valid_mask].max():
        # Cari index terdekat
        idx = np.argmin(np.abs(valid_angles[valid_mask] - incident_angle))
        current_delta_red = delta_red[valid_mask][idx]
        current_delta_violet = delta_violet[valid_mask][idx]
        
        ax3.axvline(x=incident_angle, color='blue', linestyle='--', 
                    linewidth=2, label=f'Sudut Saat Ini: {incident_angle}°')
        ax3.scatter([incident_angle], [current_delta_red], color='red', s=100, zorder=5)
        ax3.scatter([incident_angle], [current_delta_violet], color='purple', s=100, zorder=5)
    
    # Cari deviasi minimum untuk merah
    if len(delta_red[valid_mask]) > 0:
        min_delta_idx = np.argmin(delta_red[valid_mask])
        min_angle = valid_angles[valid_mask][min_delta_idx]
        min_delta = delta_red[valid_mask][min_delta_idx]
        
        ax3.scatter([min_angle], [min_delta], 
                    color='red', s=150, zorder=5, marker='*', 
                    label=f'Deviasi Min Merah: {min_delta:.2f}°')
    
    ax3.set_xlabel('Sudut Datang i₁ (°)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Sudut Deviasi δ (°)', fontsize=12, fontweight='bold')
    ax3.set_title('Hubungan Sudut Datang dan Sudut Deviasi', 
                  fontsize=14, fontweight='bold', pad=15)
    ax3.legend(fontsize=10, loc='upper right')
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)
else:
    st.warning("⚠️ Tidak ada data yang valid untuk grafik. Coba ubah sudut prisma menjadi lebih kecil (misalnya 60°).")

# ============================================================================
# GRAFIK: PENGARUH INDEKS BIAS TERHADAP SUDUT DEVIASI
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Pengaruh Indeks Bias terhadap Sudut Deviasi")

# Generate data untuk plot
n_values = np.linspace(1.4, 2.0, 100)
wavelengths_plot = [700, 550, 400]  # Merah, Hijau, Biru
colors_plot = ['#FF0000', '#00FF00', '#0000FF']
labels_plot = ['Merah (700 nm)', 'Hijau (550 nm)', 'Biru (400 nm)']

fig_n, ax_n = plt.subplots(figsize=(10, 6), dpi=100)

for wl, color, label in zip(wavelengths_plot, colors_plot, labels_plot):
    delta_values = []
    for n in n_values:
        # Hitung deviasi sederhana (pendekatan sudut minimum)
        # δ_min = 2*arcsin(n*sin(A/2)) - A
        A_rad = np.radians(prism_angle)
        try:
            sin_term = n * np.sin(A_rad / 2)
            if sin_term <= 1:
                delta_min = 2 * np.arcsin(sin_term) - A_rad
                delta_values.append(np.degrees(delta_min))
            else:
                delta_values.append(np.nan)
        except:
            delta_values.append(np.nan)
    
    ax_n.plot(n_values, delta_values, color=color, linewidth=2.5, 
              label=label, alpha=0.8)
    
    # Tambahkan marker untuk nilai saat ini
    try:
        sin_term = refractive_index * np.sin(A_rad / 2)
        if sin_term <= 1:
            delta_current = 2 * np.arcsin(sin_term) - A_rad
            ax_n.scatter([refractive_index], [np.degrees(delta_current)], 
                        color=color, s=100, zorder=5, edgecolors='black')
    except:
        pass

# Garis vertikal untuk n saat ini
ax_n.axvline(x=refractive_index, color='gray', linestyle='--', 
             linewidth=1, alpha=0.5, label=f'n saat ini: {refractive_index:.2f}')

ax_n.set_xlabel('Indeks Bias (n)', fontsize=12, fontweight='bold')
ax_n.set_ylabel('Sudut Deviasi Minimum δ (°)', fontsize=12, fontweight='bold')
ax_n.set_title('Hubungan Indeks Bias dan Sudut Deviasi', 
               fontsize=14, fontweight='bold', pad=15)
ax_n.legend(fontsize=10, loc='upper left')
ax_n.grid(True, alpha=0.3, linestyle='--')
ax_n.set_xlim(1.4, 2.0)

plt.tight_layout()
st.pyplot(fig_n)
plt.close(fig_n)

# Penjelasan
st.markdown("""
<div style='background: #e8f4f8; padding: 15px; border-radius: 8px; margin-top: 10px;'>

**💡 Interpretasi Grafik:**
- Semakin **besar indeks bias (n)**, semakin **besar sudut deviasi (δ)**
- Cahaya dengan **panjang gelombang lebih pendek** (biru) memiliki indeks bias lebih besar → deviasi lebih besar
- **Dispersi** = perbedaan deviasi antar warna → spektrum terpisah

**📐 Rumus Sudut Deviasi Minimum:**
$$\delta_{\text{min}} = 2 \cdot \arcsin\!\big(n \cdot \sin(A/2)\big) - A$$

# ============================================================================
# GRAFIK: DISPERSI - INDEKS BIAS vs PANJANG GELOMBANG
# ============================================================================
st.markdown("---")
st.markdown("### 🌈 Kurva Dispersi: n vs λ")

wavelength_range = np.linspace(380, 750, 100)

# Hitung n(λ) untuk nilai dispersi yang berbeda
B_values = [4.0e3, 5.0e3, 6.0e3]  # Koefisien dispersi berbeda
labels_B = ['Dispersi Rendah', 'Dispersi Sedang', 'Dispersi Tinggi']
colors_B = ['#2ECC71', '#F39C12', '#E74C3C']

fig_disp, ax_disp = plt.subplots(figsize=(10, 6), dpi=100)

for B, label, color in zip(B_values, labels_B, colors_B):
    n_disp = [1.5 + B / (wl**2) for wl in wavelength_range]
    ax_disp.plot(wavelength_range, n_disp, color=color, linewidth=2.5, 
                 label=label, alpha=0.8)

# Tambahkan titik spektrum
for wl, color in zip([700, 620, 580, 530, 470, 420, 380], 
                     ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']):
    n_val = 1.5 + 5000 / (wl**2)
    ax_disp.scatter([wl], [n_val], color=color, s=80, edgecolors='black', zorder=5)

ax_disp.set_xlabel('Panjang Gelombang λ (nm)', fontsize=12, fontweight='bold')
ax_disp.set_ylabel('Indeks Bias (n)', fontsize=12, fontweight='bold')
ax_disp.set_title('Ketergantungan Indeks Bias terhadap Panjang Gelombang', 
                  fontsize=14, fontweight='bold', pad=15)
ax_disp.legend(fontsize=10, loc='upper right')
ax_disp.grid(True, alpha=0.3, linestyle='--')
ax_disp.invert_xaxis()  # λ besar di kiri (konvensi optik)

plt.tight_layout()
st.pyplot(fig_disp)
plt.close(fig_disp)

st.markdown("""
<div style='background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 10px;'>

<strong>Catatan:</strong>
- Kurva menunjukkan **dispersi normal**: n menurun saat λ meningkat
- **Dispersi tinggi** = kurva lebih curam = pemisahan warna lebih jelas
- Material dengan dispersi tinggi (seperti flint glass) menghasilkan spektrum lebih lebar

</div>
""", unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")

footer_content = """
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 10px; color: white; margin-top: 30px;'>
    <h4 style='margin: 0;'>🔬 Simulasi Dispersi Cahaya pada Prisma</h4>
    <p style='margin: 10px 0 0 0;'><em>Dikembangkan oleh Felix Marcellino Henrikus, S.Si.</em></p>
    <p style='margin: 5px 0 0 0; font-size: 14px;'>Untuk pembelajaran Optika Geometri di Fisika UKSW Salatiga</p>
</div>
"""

st.markdown(footer_content, unsafe_allow_html=True)
