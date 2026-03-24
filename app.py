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
# VISUALISASI RAY TRACING
# ============================================================================
st.markdown("---")
st.markdown("### 🔍 Visualisasi Ray Tracing")

if results:
    def create_ray_tracing_plot(incident_angle, prism_angle, results, show_spectrum, show_angles):
        fig, ax = plt.subplots(figsize=(11, 7), dpi=100)
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#ffffff')
        
        # PRISM GEOMETRY
        prism_height = 4.5
        apex_x, apex_y = 0, prism_height
        base_width = prism_height * 2 * np.tan(np.radians(prism_angle/2))
        base_left_x, base_y = -base_width/2, 0
        base_right_x, _ = base_width/2, 0
        
        prism = Polygon([[apex_x, apex_y], [base_left_x, base_y], [base_right_x, base_y]],
                        fill=True, alpha=0.2, edgecolor='black', linewidth=1.5, facecolor='skyblue')
        ax.add_patch(prism)
        
        # LEFT FACE NORMAL (pointing OUT of prism)
        left_face_dx = apex_x - base_left_x
        left_face_dy = apex_y - base_y
        left_face_len = np.sqrt(left_face_dx**2 + left_face_dy**2)
        
        normal_left_x = -left_face_dy / left_face_len
        normal_left_y = left_face_dx / left_face_len
        normal_left_angle = np.arctan2(normal_left_y, normal_left_x)
        
        # RIGHT FACE NORMAL (pointing OUT of prism)
        right_face_dx = base_right_x - apex_x
        right_face_dy = base_y - apex_y
        right_face_len = np.sqrt(right_face_dx**2 + right_face_dy**2)
        
        normal_right_x = right_face_dy / right_face_len
        normal_right_y = -right_face_dx / right_face_len
        normal_right_angle = np.arctan2(normal_right_y, normal_right_x)
        
        # ENTRY POINT (35% from base up left face)
        t_entry = 0.35
        entry_x = base_left_x + t_entry * left_face_dx
        entry_y = base_y + t_entry * left_face_dy
        
        # INCIDENT RAY - DIPERBAIKI: dari KIRI menuju prisma
        i1_rad = np.radians(incident_angle)
        
        # Sinar datang dari KIRI, menuju entry point
        # Arah sinar: normal - i1 (karena datang dari kiri)
        incident_ray_angle = normal_left_angle + np.pi - i1_rad
        
        incident_len = 4.0
        # Sinar datang: dari incident_start MENUJU entry point
        incident_start_x = entry_x - incident_len * np.cos(incident_ray_angle)
        incident_start_y = entry_y - incident_len * np.sin(incident_ray_angle)
        
        # Draw incident ray (BLACK, SOLID) - datang dari kiri
        ax.plot([incident_start_x, entry_x], [incident_start_y, entry_y],
                'k-', linewidth=2.5, label='Sinar Datang', zorder=5)
        
        # Extension FORWARD (dotted) - perpanjangan sinar datang jika tidak dibiaskan
        ext_len = 5.0
        ext_end_x = entry_x + ext_len * np.cos(incident_ray_angle)
        ext_end_y = entry_y + ext_len * np.sin(incident_ray_angle)
        ax.plot([entry_x, ext_end_x], [entry_y, ext_end_y],
                'k:', linewidth=0.8, alpha=0.4, zorder=1)
        
        # REFRACTED RAY INSIDE (r1)
        n_red = results[0]['n']
        r1_rad = np.arcsin(np.sin(i1_rad) / n_red)
        
        # Internal ray direction (bends TOWARD normal)
        internal_ray_angle = normal_left_angle - r1_rad
        
        internal_dir_x = np.cos(internal_ray_angle)
        internal_dir_y = np.sin(internal_ray_angle)
        
        # Find exit point on right face
        t_max = 10
        exit_x, exit_y = None, None
        for t in np.linspace(0.1, t_max, 500):
            test_x = entry_x + t * internal_dir_x
            test_y = entry_y + t * internal_dir_y
            
            val1 = (test_x - apex_x) * (base_y - apex_y) - (test_y - apex_y) * (base_right_x - apex_x)
            val2 = (entry_x + (t+0.1) * internal_dir_x - apex_x) * (base_y - apex_y) - \
                   (entry_y + (t+0.1) * internal_dir_y - apex_y) * (base_right_x - apex_x)
            
            if val1 * val2 <= 0:
                exit_x, exit_y = test_x, test_y
                break
        
        if exit_x is None:
            exit_x = apex_x + 0.5 * (base_right_x - apex_x)
            exit_y = apex_y + 0.5 * (base_y - apex_y)
        
        # Draw internal ray (dark blue)
        ax.plot([entry_x, exit_x], [entry_y, exit_y],
                color='#1E3A8A', linewidth=2, alpha=0.8, zorder=4)
        
        # EMERGENT RAYS (spectrum) - DITAMBAHKAN
        exit_data = []
        
        for i, res in enumerate(results):
            if not show_spectrum and i not in [0, len(results)//2, len(results)-1]:
                continue
            
            n_wl = res['n']
            i2_val = res['i2']
            i2_rad = np.radians(i2_val)
            
            # Snell at exit: n*sin(i2) = 1*sin(r2)
            sin_r2 = n_wl * np.sin(i2_rad)
            if sin_r2 > 1:
                continue
            r2_rad = np.arcsin(sin_r2)
            
            # Emergent ray direction (bends AWAY from normal)
            emergent_angle = normal_right_angle - r2_rad
            
            emergent_len = 4.0
            final_x = exit_x + emergent_len * np.cos(emergent_angle)
            final_y = exit_y + emergent_len * np.sin(emergent_angle)
            
            exit_data.append({
                'exit_x': exit_x, 'exit_y': exit_y,
                'final_x': final_x, 'final_y': final_y,
                'emergent_angle': emergent_angle,
                'r2_rad': r2_rad,
                'color': res['color'] if show_spectrum else 'k',
                'label': res['warna'] if show_spectrum and i < 3 else "",
                'delta': res['delta']
            })
            
            # Draw emergent ray (COLOR spectrum)
            ax.plot([exit_x, final_x], [exit_y, final_y],
                    color=res['color'] if show_spectrum else 'k',
                    linewidth=2.5, alpha=0.9,
                    label=res['warna'] if show_spectrum and i < 3 else "", zorder=5)
            
            # Backward extension (dotted)
            back_x = exit_x - 2.0 * np.cos(emergent_angle)
            back_y = exit_y - 2.0 * np.sin(emergent_angle)
            ax.plot([exit_x, back_x], [exit_y, back_y],
                    color=res['color'] if show_spectrum else 'k',
                    linewidth=0.5, alpha=0.25, linestyle=':', zorder=1)
        
        # NORMAL LINES
        normal_len = 1.0
        
        ax.plot([entry_x - normal_len * normal_left_x,
                 entry_x + normal_len * normal_left_x],
                [entry_y - normal_len * normal_left_y,
                 entry_y + normal_len * normal_left_y],
                'k--', linewidth=1, alpha=0.5, zorder=2)
        
        ax.plot([exit_x - normal_len * normal_right_x,
                 exit_x + normal_len * normal_right_x],
                [exit_y - normal_len * normal_right_y,
                 exit_y + normal_len * normal_right_y],
                'k--', linewidth=1, alpha=0.5, zorder=2)
        
        # ANGLE LABELS
        if show_angles:
            arc_r = 0.35
            
            # i₁ - OUTSIDE (antara sinar datang dan normal)
            start_i1 = normal_left_angle
            end_i1 = incident_ray_angle
            
            while abs(end_i1 - start_i1) > np.pi:
                if end_i1 > start_i1:
                    end_i1 -= 2*np.pi
                else:
                    start_i1 -= 2*np.pi
            
            arc_i1 = np.linspace(start_i1, end_i1, 50)
            ax.plot(entry_x + arc_r * np.cos(arc_i1),
                    entry_y + arc_r * np.sin(arc_i1),
                    'k-', linewidth=1.8, zorder=6)
            
            mid_i1 = (start_i1 + end_i1) / 2
            ax.text(entry_x + (arc_r + 0.12) * np.cos(mid_i1),
                    entry_y + (arc_r + 0.12) * np.sin(mid_i1),
                    'i₁', fontsize=12, fontweight='bold', color='black',
                    ha='center', va='center', zorder=7)
            
            # r₁ - INSIDE (antara sinar dalam dan normal)
            start_r1 = normal_left_angle
            end_r1 = internal_ray_angle
            
            while abs(end_r1 - start_r1) > np.pi:
                if end_r1 > start_r1:
                    end_r1 -= 2*np.pi
                else:
                    start_r1 -= 2*np.pi
            
            arc_r1 = np.linspace(start_r1, end_r1, 50)
            ax.plot(entry_x + arc_r * 0.55 * np.cos(arc_r1),
                    entry_y + arc_r * 0.55 * np.sin(arc_r1),
                    'k-', linewidth=1.8, zorder=6)
            
            mid_r1 = (start_r1 + end_r1) / 2
            ax.text(entry_x + (arc_r * 0.55 + 0.1) * np.cos(mid_r1),
                    entry_y + (arc_r * 0.55 + 0.1) * np.sin(mid_r1),
                    'r₁', fontsize=11, fontweight='bold', color='black',
                    ha='center', va='center', zorder=7)
            
            # i₂ - INSIDE (antara sinar dalam dan normal kanan) - DITAMBAHKAN
            if exit_data:
                internal_exit_angle = np.arctan2(exit_y - entry_y, exit_x - entry_x)
                normal_right_in = normal_right_angle + np.pi
                
                start_i2 = normal_right_in
                end_i2 = internal_exit_angle
                
                while abs(end_i2 - start_i2) > np.pi:
                    if end_i2 > start_i2:
                        end_i2 -= 2*np.pi
                    else:
                        start_i2 -= 2*np.pi
                
                arc_i2 = np.linspace(start_i2, end_i2, 50)
                ax.plot(exit_x + arc_r * 0.55 * np.cos(arc_i2),
                        exit_y + arc_r * 0.55 * np.sin(arc_i2),
                        'k-', linewidth=1.8, zorder=6)
                
                mid_i2 = (start_i2 + end_i2) / 2
                ax.text(exit_x + (arc_r * 0.55 + 0.1) * np.cos(mid_i2),
                        exit_y + (arc_r * 0.55 + 0.1) * np.sin(mid_i2),
                        'i₂', fontsize=11, fontweight='bold', color='black',
                        ha='center', va='center', zorder=7)
                
                # r₂ - OUTSIDE (antara sinar keluar dan normal kanan) - DITAMBAHKAN
                r2_rad = exit_data[0]['r2_rad']
                emergent_angle = exit_data[0]['emergent_angle']
                
                start_r2 = normal_right_angle
                end_r2 = emergent_angle
                
                while abs(end_r2 - start_r2) > np.pi:
                    if end_r2 > start_r2:
                        end_r2 -= 2*np.pi
                    else:
                        start_r2 -= 2*np.pi
                
                arc_r2 = np.linspace(start_r2, end_r2, 50)
                ax.plot(exit_x + arc_r * 0.55 * np.cos(arc_r2),
                        exit_y + arc_r * 0.55 * np.sin(arc_r2),
                        'k-', linewidth=1.8, zorder=6)
                
                mid_r2 = (start_r2 + end_r2) / 2
                ax.text(exit_x + (arc_r * 0.55 + 0.1) * np.cos(mid_r2),
                        exit_y + (arc_r * 0.55 + 0.1) * np.sin(mid_r2),
                        'r₂', fontsize=11, fontweight='bold', color='black',
                        ha='center', va='center', zorder=7)
            
            # Prism angle A
            left_side_angle = np.arctan2(base_y - apex_y, base_left_x - apex_x)
            right_side_angle = np.arctan2(base_y - apex_y, base_right_x - apex_x)
            
            arc_A = np.linspace(right_side_angle, left_side_angle, 50)
            ax.plot(apex_x + 0.6 * np.cos(arc_A),
                    apex_y + 0.6 * np.sin(arc_A),
                    'k-', linewidth=1.8, zorder=6)
            ax.text(apex_x, apex_y - 0.8,
                    f'A = {prism_angle:.1f}°', fontsize=11,
                    fontweight='bold', color='black', ha='center', va='top', zorder=7)
            
            # Deviation δ - DITAMBAHKAN
            if exit_data:
                # δ = sudut antara perpanjangan sinar datang dan sinar keluar
                incident_ext_angle = incident_ray_angle  # Arah perpanjangan
                emergent_angle = exit_data[0]['emergent_angle']
                
                a1, a2 = incident_ext_angle, emergent_angle
                while a1 > np.pi: a1 -= 2*np.pi
                while a2 > np.pi: a2 -= 2*np.pi
                while a1 < -np.pi: a1 += 2*np.pi
                while a2 < -np.pi: a2 += 2*np.pi
                
                start_d, end_d = min(a1, a2), max(a1, a2)
                
                dev_cx = exit_x + 0.5
                dev_cy = exit_y + 1.2
                dev_r = 2.8
                
                arc_d = np.linspace(start_d, end_d, 50)
                ax.plot(dev_cx + dev_r * np.cos(arc_d),
                        dev_cy + dev_r * np.sin(arc_d),
                        'k--', linewidth=1.8, zorder=6)
                
                mid_d = (start_d + end_d) / 2
                ax.text(dev_cx + (dev_r + 0.3) * np.cos(mid_d),
                        dev_cy + (dev_r + 0.3) * np.sin(mid_d),
                        f'δ = {exit_data[0]["delta"]:.1f}°', fontsize=11,
                        fontweight='bold', color='black',
                        ha='center', va='center', zorder=7)
        
        ax.set_xlim(-6.5, 6.5)
        ax.set_ylim(-0.5, 6)
        ax.set_aspect('equal')
        ax.axis('off')
        
        if show_spectrum:
            ax.legend(loc='upper left', fontsize=9, framealpha=0.9, facecolor='white')
        
        plt.tight_layout()
        return fig
        
    fig = create_ray_tracing_plot(incident_angle, prism_angle, results, show_spectrum, show_angles)
    st.pyplot(fig)
    plt.close(fig)
else:
    st.warning("⚠️ Visualisasi tidak dapat ditampilkan. Periksa parameter input.")

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
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div class="footer">
    <h4>🔬 Simulasi Dispersi Cahaya pada Prisma</h4>
    <p><em>Dikembangkan oleh Felix Marcellino Henrikus. S.Si.</em></p>
    <p>Untuk pembelajaran Optika Geometri di Fisika UKSW Salatiga</p>
</div>
""", unsafe_allow_html=True)
