import streamlit as st
import numpy as np
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

# ============================================================================
# HEADER & INFORMASI PENGEMBANG
# ============================================================================
st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0;'>🔬 Simulasi Dispersi Cahaya pada Prisma</h1>
        <p style='color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;'>
            Dikembangkan oleh <strong>Felix Marcellino Henrikus</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# FUNGSI FISIKA - HUKUM SNELL & DISPERSI
# ============================================================================

def cauchy_equation(wavelength_nm, A=1.5046, B=4.47e-15, C=1.70e-20):
    """
    Persamaan Cauchy untuk indeks bias
    n(λ) = A + B/λ² + C/λ⁴
    λ dalam meter
    """
    wavelength_m = wavelength_nm * 1e-9
    n = A + B / (wavelength_m ** 2) + C / (wavelength_m ** 4)
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
    i1 = np.radians(incident_angle_deg)
    A = np.radians(prism_angle_deg)
    
    if model == 'cauchy':
        n = cauchy_equation(wavelength_nm)
    else:
        n = sellmeier_equation(wavelength_nm)
    
    n_air = 1.0
    
    try:
        sin_r1 = n_air * np.sin(i1) / n
        if abs(sin_r1) > 1:
            return None, None, None, None
        
        r1 = np.arcsin(sin_r1)
        r2 = A - r1
        
        sin_i2 = n * np.sin(r2) / n_air
        if abs(sin_i2) > 1:
            return None, None, None, None
        
        i2 = np.arcsin(sin_i2)
        delta = i1 + i2 - A
        
        return np.degrees(delta), np.degrees(r1), np.degrees(r2), np.degrees(i2)
    except:
        return None, None, None, None

def get_spectrum_colors():
    """Mengembalikan array panjang gelombang dan warna spektrum"""
    wavelengths = [700, 620, 580, 530, 470, 420, 380]  # nm
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
    step=1.0,
    help="Sudut apex prisma (default 60° untuk prisma sama kaki)"
)

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
    - Geser slider untuk melihat perubahan sudut deviasi
    - Sudut deviasi minimum terjadi saat i₁ ≈ i₂
    - Warna berbeda memiliki indeks bias berbeda
""")

# ============================================================================
# PERHITUNGAN SUDUT DEVIASI
# ============================================================================
st.markdown("### 📊 Hasil Perhitungan")

wavelengths, colors, color_names = get_spectrum_colors()

results = []
for wl, color, name in zip(wavelengths, colors, color_names):
    if dispersion_model == 'Cauchy':
        delta, r1, r2, i2 = calculate_deviation_angle(incident_angle, prism_angle, wl, 'cauchy')
        n = cauchy_equation(wl)
    else:
        delta, r1, r2, i2 = calculate_deviation_angle(incident_angle, prism_angle, wl, 'sellmeier')
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
            " Sudut Deviasi (Merah)",
            f"{results[0]['delta']:.2f}°",
            delta=f"{results[0]['delta'] - 40:.2f}°"
        )
    
    with col2:
        mid_idx = len(results) // 2
        st.metric(
            "🟢 Sudut Deviasi (Hijau)",
            f"{results[mid_idx]['delta']:.2f}°",
            delta=f"{results[mid_idx]['delta'] - 40:.2f}°"
        )
    
    with col3:
        st.metric(
            "🟣 Sudut Deviasi (Ungu)",
            f"{results[-1]['delta']:.2f}°",
            delta=f"{results[-1]['delta'] - 40:.2f}°"
        )
    
    delta_range = results[-1]['delta'] - results[0]['delta']
    st.success(f"**🌈 Sudut Dispersi (Δδ):** {delta_range:.2f}°")
else:
    st.error("⚠️ Sudut datang terlalu besar, terjadi pemantulan internal total!")

# ============================================================================
# VISUALISASI RAY TRACING
# ============================================================================
st.markdown("---")
st.markdown("### 🔍 Visualisasi Ray Tracing")

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#ffffff')

prism_size = 5
apex_x = 0
apex_y = prism_size * np.sqrt(3) / 2
base_left_x = -prism_size / 2
base_left_y = 0
base_right_x = prism_size / 2
base_right_y = 0

prism_vertices = np.array([
    [apex_x, apex_y],
    [base_left_x, base_left_y],
    [base_right_x, base_right_y]
])

prism_patch = Polygon(prism_vertices, closed=True, 
                      fill=True, alpha=0.3, 
                      edgecolor='#2c3e50', linewidth=2,
                      facecolor='#3498db')
ax.add_patch(prism_patch)

A_rad = np.radians(prism_angle)
left_surface_angle = np.pi/2 - A_rad/2
right_surface_angle = np.pi/2 + A_rad/2

entry_point_x = -prism_size/4
entry_point_y = apex_y * 0.6

i1_rad = np.radians(incident_angle)
normal_left_angle = left_surface_angle + np.pi/2
incident_ray_angle = normal_left_angle - i1_rad - np.pi

incident_length = 4
incident_start_x = entry_point_x + incident_length * np.cos(incident_ray_angle)
incident_start_y = entry_point_y + incident_length * np.sin(incident_ray_angle)

ax.plot([incident_start_x, entry_point_x], 
        [incident_start_y, entry_point_y], 
        'k-', linewidth=2, label='Sinar Datang', zorder=5)

ax.plot([entry_point_x, entry_point_x + 0.5*np.cos(normal_left_angle)],
        [entry_point_y, entry_point_y + 0.5*np.sin(normal_left_angle)],
        'k--', linewidth=1, alpha=0.5)

for i, result in enumerate(results):
    if not show_spectrum and i not in [0, len(results)//2, len(results)-1]:
        continue
    
    n = result['n']
    r1_rad = np.radians(result['r1'])
    r2_rad = np.radians(result['r2'])
    i2_rad = np.radians(result['i2'])
    
    internal_angle = normal_left_angle - r1_rad - np.pi
    internal_length = prism_size * 0.8
    internal_end_x = entry_point_x + internal_length * np.cos(internal_angle)
    internal_end_y = entry_point_y + internal_length * np.sin(internal_angle)
    
    if show_spectrum:
        ax.plot([entry_point_x, internal_end_x],
                [entry_point_y, internal_end_y],
                color=result['color'], linewidth=1.5, alpha=0.7)
    else:
        ax.plot([entry_point_x, internal_end_x],
                [entry_point_y, internal_end_y],
                'r-', linewidth=1.5, alpha=0.7)
    
    normal_right_angle = right_surface_angle - np.pi/2
    exit_ray_angle = normal_right_angle - i2_rad
    
    exit_length = 5
    exit_end_x = internal_end_x + exit_length * np.cos(exit_ray_angle)
    exit_end_y = internal_end_y + exit_length * np.sin(exit_ray_angle)
    
    if show_spectrum:
        ax.plot([internal_end_x, exit_end_x],
                [internal_end_y, exit_end_y],
                color=result['color'], linewidth=2, alpha=0.9,
                label=f"{result['warna']}" if i < 3 else "")
    else:
        ax.plot([internal_end_x, exit_end_x],
                [internal_end_y, exit_end_y],
                'r-', linewidth=2)
    
    ax.plot([internal_end_x, internal_end_x + 0.5*np.cos(normal_right_angle)],
            [internal_end_y, internal_end_y + 0.5*np.sin(normal_right_angle)],
            'k--', linewidth=1, alpha=0.5)

ax.plot([incident_start_x, incident_start_x + 2],
        [incident_start_y, incident_start_y],
        'k-', linewidth=1)

extended_exit_start_x = exit_end_x - 3 * np.cos(exit_ray_angle)
extended_exit_start_y = exit_end_y - 3 * np.sin(exit_ray_angle)
ax.plot([extended_exit_start_x, exit_end_x + 1],
        [extended_exit_start_y, exit_end_y + 1],
        'k:', linewidth=1, alpha=0.5)

if show_angles:
    arc_radius = 0.8
    arc_angles = np.linspace(incident_ray_angle, normal_left_angle, 50)
    arc_x = entry_point_x + arc_radius * np.cos(arc_angles)
    arc_y = entry_point_y + arc_radius * np.sin(arc_angles)
    ax.plot(arc_x, arc_y, 'b-', linewidth=1.5)
    ax.text(entry_point_x + 0.9, entry_point_y + 0.3, 'i₁', fontsize=12, 
            fontweight='bold', color='blue')
    
    arc_angles = np.linspace(normal_left_angle - np.pi, internal_angle, 50)
    arc_x = entry_point_x + arc_radius * 0.7 * np.cos(arc_angles)
    arc_y = entry_point_y + arc_radius * 0.7 * np.sin(arc_angles)
    ax.plot(arc_x, arc_y, 'g-', linewidth=1.5)
    ax.text(entry_point_x + 0.3, entry_point_y - 0.5, 'r₁', fontsize=12,
            fontweight='bold', color='green')
    
    arc_angles = np.linspace(normal_right_angle - np.pi, exit_ray_angle, 50)
    arc_x = internal_end_x + arc_radius * 0.7 * np.cos(arc_angles)
    arc_y = internal_end_y + arc_radius * 0.7 * np.sin(arc_angles)
    ax.plot(arc_x, arc_y, 'm-', linewidth=1.5)
    ax.text(internal_end_x + 0.3, internal_end_y - 0.5, 'i₂', fontsize=12,
            fontweight='bold', color='magenta')

ax.set_xlim(-8, 8)
ax.set_ylim(-2, 8)
ax.set_aspect('equal')
ax.axis('off')

if show_spectrum:
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

plt.tight_layout()
st.pyplot(fig)
plt.close()

# ============================================================================
# FORMULASI MATEMATIS
# ============================================================================
st.markdown("---")
st.markdown("### 📐 Formulasi Matematis")

st.markdown("""
<div style='background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea;'>

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
- $\\lambda$ = Panjang gelombang cahaya

---

#### 5. Persamaan Sellmeier (Model Dispersi)

$$n^2(\\lambda) = 1 + \\sum_{i=1}^{3} \\frac{B_i \\lambda^2}{\\lambda^2 - C_i}$$

**Keterangan:**
- $B_i, C_i$ = Koefisien Sellmeier (material-specific)
- Lebih akurat untuk rentang spektrum luas

</div>
""", unsafe_allow_html=True)

# ============================================================================
# TABEL DATA HASIL
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
        df_display.style.background_gradient(
            subset=['Sudut Deviasi (°)'], 
            cmap='RdYlBu_r'
        ),
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# GRAFIK DISPERSI - CAUCHY VS SELLMEIER
# ============================================================================
st.markdown("---")
st.markdown("### 📈 Fitting Model Dispersi: Cauchy vs Sellmeier")

wavelength_range = np.linspace(380, 750, 100)
n_cauchy = [cauchy_equation(wl) for wl in wavelength_range]
n_sellmeier = [sellmeier_equation(wl) for wl in wavelength_range]

fig2, ax2 = plt.subplots(figsize=(12, 6))
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
plt.close()

st.markdown("""
<div style='background: #e8f4f8; padding: 15px; border-radius: 8px; margin-top: 15px;'>

**📝 Penjelasan:**

| Model | Kelebihan | Kekurangan |
|-------|-----------|------------|
| **Cauchy** | Sederhana, cepat dihitung | Akurat hanya untuk rentang λ terbatas |
| **Sellmeier** | Lebih akurat, rentang spektrum luas | Lebih kompleks, butuh lebih banyak parameter |

**💡 Catatan:** Untuk kaca optik standar (BK7), model Sellmeier memberikan akurasi hingga 10⁻⁶ pada indeks bias.

</div>
""", unsafe_allow_html=True)

# ============================================================================
# GRAFIK SUDUT DEVIASI VS SUDUT DATANG
# ============================================================================
st.markdown("---")
st.markdown("### 📊 Sudut Deviasi vs Sudut Datang")

incident_angles = np.linspace(30, 80, 100)
delta_red = []
delta_violet = []

for i1 in incident_angles:
    d_r, _, _, _ = calculate_deviation_angle(i1, prism_angle, 700, 'cauchy')
    d_v, _, _, _ = calculate_deviation_angle(i1, prism_angle, 380, 'cauchy')
    delta_red.append(d_r if d_r else np.nan)
    delta_violet.append(d_v if d_v else np.nan)

fig3, ax3 = plt.subplots(figsize=(12, 6))
fig3.patch.set_facecolor('#f8f9fa')
ax3.set_facecolor('#ffffff')

ax3.plot(incident_angles, delta_red, 'r-', linewidth=2.5, 
         label='Merah (700 nm)', alpha=0.8)
ax3.plot(incident_angles, delta_violet, 'v-', linewidth=2.5, 
         label='Ungu (380 nm)', alpha=0.8)
ax3.axvline(x=incident_angle, color='blue', linestyle='--', 
            linewidth=2, label=f'Sudut Saat Ini: {incident_angle}°')

min_delta_idx = np.nanargmin(delta_red)
ax3.scatter([incident_angles[min_delta_idx]], [delta_red[min_delta_idx]], 
            color='red', s=150, zorder=5, marker='*', 
            label=f'Deviasi Min: {delta_red[min_delta_idx]:.2f}°')

ax3.set_xlabel('Sudut Datang i₁ (°)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Sudut Deviasi δ (°)', fontsize=12, fontweight='bold')
ax3.set_title('Hubungan Sudut Datang dan Sudut Deviasi', 
              fontsize=14, fontweight='bold', pad=15)
ax3.legend(fontsize=11, loc='upper right')
ax3.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
st.pyplot(fig3)
plt.close()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 10px; color: white;'>

**🔬 Simulasi Dispersi Cahaya pada Prisma**

*Dikembangkan oleh Felix Marcellino Henrikus*

Fisika Optik | Pendidikan Sains | Streamlit Dashboard

</div>
""", unsafe_allow_html=True)

# ============================================================================
# REQUIREMENTS.TXT CONTENT (untuk referensi)
# ============================================================================
st.markdown("""
<details>
<summary>📦 <strong>requirements.txt</strong> (Klik untuk melihat dependensi)</summary>
