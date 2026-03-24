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
        # Ukuran figure lebih kecil
        fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#ffffff')
        
        prism_size = 4
        apex_x = 0
        apex_y = prism_size * np.sqrt(3) / 2
        base_left_x = -prism_size / 2
        base_left_y = 0
        base_right_x = prism_size / 2
        base_right_y = 0
        
        # Gambar prisma
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
        
        # Sudut permukaan prisma
        A_rad = np.radians(prism_angle)
        
        # Normal permukaan kiri (tegak lurus sisi kiri)
        # Sisi kiri memiliki sudut 60° dari horizontal untuk prisma sama sisi
        left_surface_angle_deg = 90 - prism_angle/2  # sudut sisi kiri terhadap horizontal
        left_surface_normal_angle = np.radians(left_surface_angle_deg + 90)  # normal tegak lurus sisi
        
        # Normal permukaan kanan
        right_surface_angle_deg = 90 + prism_angle/2  # sudut sisi kanan terhadap horizontal
        right_surface_normal_angle = np.radians(right_surface_angle_deg - 90)  # normal tegak lurus sisi
        
        # Titik masuk sinar (di permukaan kiri prisma, sekitar 1/3 dari alas)
        entry_point_x = base_left_x + 0.35 * (apex_x - base_left_x)
        entry_point_y = 0.35 * apex_y
        
        # Sinar datang - datang dari kiri bawah ke kanan atas
        i1_rad = np.radians(incident_angle)
        # Arah sinar datang (dari kiri bawah ke titik masuk)
        incident_direction = left_surface_normal_angle - i1_rad - np.pi
        
        incident_length = 3.5
        incident_start_x = entry_point_x + incident_length * np.cos(incident_direction)
        incident_start_y = entry_point_y + incident_length * np.sin(incident_direction)
        
        # Gambar sinar datang
        ax.plot([incident_start_x, entry_point_x], 
                [incident_start_y, entry_point_y], 
                'k-', linewidth=2, label='Sinar Datang', zorder=5)
        
        # Perpanjang sinar datang (garis putus-putus) untuk sudut deviasi
        extension_length = 4
        extension_end_x = entry_point_x - extension_length * np.cos(incident_direction)
        extension_end_y = entry_point_y - extension_length * np.sin(incident_direction)
        ax.plot([entry_point_x, extension_end_x],
                [entry_point_y, extension_end_y],
                'k:', linewidth=1, alpha=0.5)
        
        # Gambar garis normal di titik masuk (permukaan kiri)
        normal_length = 0.8
        ax.plot([entry_point_x - normal_length * np.cos(left_surface_normal_angle),
                 entry_point_x + normal_length * np.cos(left_surface_normal_angle)],
                [entry_point_y - normal_length * np.sin(left_surface_normal_angle),
                 entry_point_y + normal_length * np.sin(left_surface_normal_angle)],
                'k--', linewidth=1, alpha=0.5)
        
        # Simpan titik keluar untuk setiap warna
        exit_points_data = []
        
        for i, result in enumerate(results):
            if not show_spectrum and i not in [0, len(results)//2, len(results)-1]:
                continue
            
            r1_rad = np.radians(result['r1'])
            r2_rad = np.radians(result['r2'])
            i2_rad = np.radians(result['i2'])
            
            # Sinar di dalam prisma
            # Sudut sinar di dalam prisma terhadap horizontal
            internal_direction = left_surface_normal_angle - r1_rad
            
            # Hitung titik keluar di permukaan kanan
            # Parameterisasi permukaan kanan (dari apex ke base_right)
            surface_right_start = np.array([apex_x, apex_y])
            surface_right_end = np.array([base_right_x, base_right_y])
            
            # Cari perpotongan ray dengan permukaan kanan
            t_max = prism_size * 1.5
            t = np.linspace(0, t_max, 200)
            ray_x = entry_point_x + t * np.cos(internal_direction)
            ray_y = entry_point_y + t * np.sin(internal_direction)
            
            # Persamaan garis permukaan kanan
            exit_x, exit_y = None, None
            for j in range(len(t)-1):
                p1 = surface_right_start
                p2 = surface_right_end
                p3 = np.array([ray_x[j], ray_y[j]])
                p4 = np.array([ray_x[j+1], ray_y[j+1]])
                
                # Cek perpotongan
                d1 = (p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0])
                d2 = (p4[0]-p3[0])*(p2[1]-p3[1]) - (p4[1]-p3[1])*(p2[0]-p3[0])
                
                if d1 * d2 <= 0:
                    # Ada perpotongan
                    if abs(d1 - d2) > 1e-10:
                        alpha = abs(d1) / (abs(d1) + abs(d2))
                        exit_x = p1[0] + alpha * (p2[0] - p1[0])
                        exit_y = p1[1] + alpha * (p2[1] - p1[1])
                    else:
                        exit_x = ray_x[j]
                        exit_y = ray_y[j]
                    break
            
            if exit_x is None:
                exit_x = ray_x[-1]
                exit_y = ray_y[-1]
            
            exit_points_data.append({
                'exit_x': exit_x,
                'exit_y': exit_y,
                'i2_rad': i2_rad,
                'color': result['color'] if show_spectrum else 'r',
                'label': result['warna'] if show_spectrum and i < 3 else ""
            })
            
            # Gambar sinar di dalam prisma
            line_style = '-' if show_spectrum else '--'
            ax.plot([entry_point_x, exit_x],
                    [entry_point_y, exit_y],
                    color=result['color'] if show_spectrum else 'blue',
                    linewidth=1.5, alpha=0.7, linestyle=line_style)
        
        # Gambar sinar keluar untuk setiap warna
        for i, data in enumerate(exit_points_data):
            exit_x = data['exit_x']
            exit_y = data['exit_y']
            i2_rad = data['i2_rad']
            color = data['color']
            label = data['label']
            
            # Sinar keluar dari prisma
            # Arah sinar keluar
            exit_direction = right_surface_normal_angle - i2_rad
            
            exit_length = 3.5
            final_exit_x = exit_x + exit_length * np.cos(exit_direction)
            final_exit_y = exit_y + exit_length * np.sin(exit_direction)
            
            # Gambar sinar keluar
            ax.plot([exit_x, final_exit_x],
                    [exit_y, final_exit_y],
                    color=color, linewidth=2, alpha=0.9,
                    label=label if label else "")
            
            # Gambar garis normal di titik keluar (permukaan kanan)
            ax.plot([exit_x - normal_length * np.cos(right_surface_normal_angle),
                     exit_x + normal_length * np.cos(right_surface_normal_angle)],
                    [exit_y - normal_length * np.sin(right_surface_normal_angle),
                     exit_y + normal_length * np.sin(right_surface_normal_angle)],
                    'k--', linewidth=1, alpha=0.5)
            
            # Perpanjang sinar keluar (garis putus-putus) untuk sudut deviasi
            ax.plot([exit_x, exit_x - 2 * np.cos(exit_direction)],
                    [exit_y, exit_y - 2 * np.sin(exit_direction)],
                    color=color, linewidth=0.5, alpha=0.3, linestyle=':')
        
        # Gambar label sudut-sudut
        if show_angles and len(results) > 0:
            result = results[0]
            arc_radius = 0.5
            
            # Sudut i₁ (sudut datang) - antara sinar datang dan normal
            start_angle = incident_direction
            end_angle = left_surface_normal_angle
            # Pastikan busur tidak lebih dari 180 derajat
            if abs(end_angle - start_angle) > np.pi:
                if end_angle > start_angle:
                    start_angle += 2*np.pi
                else:
                    end_angle += 2*np.pi
            
            arc_angles = np.linspace(start_angle, end_angle, 50)
            arc_x = entry_point_x + arc_radius * np.cos(arc_angles)
            arc_y = entry_point_y + arc_radius * np.sin(arc_angles)
            ax.plot(arc_x, arc_y, 'b-', linewidth=2)
            # Posisi label i₁
            mid_angle = (start_angle + end_angle) / 2
            ax.text(entry_point_x + (arc_radius+0.15) * np.cos(mid_angle),
                    entry_point_y + (arc_radius+0.15) * np.sin(mid_angle),
                    'i₁', fontsize=11, fontweight='bold', color='blue',
                    ha='center', va='center')
            
            # Sudut r₁ (sudut bias pertama) - antara sinar dalam prisma dan normal
            r1_rad = np.radians(result['r1'])
            internal_direction = left_surface_normal_angle - r1_rad
            start_angle = internal_direction
            end_angle = left_surface_normal_angle
            
            arc_angles = np.linspace(start_angle, end_angle, 50)
            arc_x = entry_point_x + arc_radius * 0.65 * np.cos(arc_angles)
            arc_y = entry_point_y + arc_radius * 0.65 * np.sin(arc_angles)
            ax.plot(arc_x, arc_y, 'g-', linewidth=2)
            # Posisi label r₁
            mid_angle = (start_angle + end_angle) / 2
            ax.text(entry_point_x + (arc_radius*0.65+0.1) * np.cos(mid_angle),
                    entry_point_y + (arc_radius*0.65+0.1) * np.sin(mid_angle),
                    'r₁', fontsize=10, fontweight='bold', color='green',
                    ha='center', va='center')
            
            # Sudut i₂ (sudut datang kedua) - antara sinar dalam prisma dan normal permukaan kanan
            if len(exit_points_data) > 0:
                data = exit_points_data[0]
                exit_x = data['exit_x']
                exit_y = data['exit_y']
                i2_rad = data['i2_rad']
                
                # Arah sinar dalam prisma menuju permukaan kanan
                ray_to_surface = np.arctan2(exit_y - entry_point_y, exit_x - entry_point_x)
                
                # Normal permukaan kanan (arah keluar dari prisma)
                normal_right_out = right_surface_normal_angle
                
                # Sudut i₂
                start_angle = ray_to_surface
                end_angle = normal_right_out
                
                # Sesuaikan agar busur tidak terlalu besar
                while abs(end_angle - start_angle) > np.pi:
                    if end_angle > start_angle:
                        end_angle -= 2*np.pi
                    else:
                        start_angle -= 2*np.pi
                
                arc_angles = np.linspace(start_angle, end_angle, 50)
                arc_x = exit_x + arc_radius * 0.65 * np.cos(arc_angles)
                arc_y = exit_y + arc_radius * 0.65 * np.sin(arc_angles)
                ax.plot(arc_x, arc_y, 'm-', linewidth=2)
                # Posisi label i₂
                mid_angle = (start_angle + end_angle) / 2
                ax.text(exit_x + (arc_radius*0.65+0.12) * np.cos(mid_angle),
                        exit_y + (arc_radius*0.65+0.12) * np.sin(mid_angle),
                        'i₂', fontsize=10, fontweight='bold', color='magenta',
                        ha='center', va='center')
            
            # Sudut puncak prisma (A)
            apex_arc_radius = 0.7
            # Sudut sisi kiri dan kanan prisma di apex
            left_side_angle = np.arctan2(base_left_y - apex_y, base_left_x - apex_x)
            right_side_angle = np.arctan2(base_right_y - apex_y, base_right_x - apex_x)
            
            arc_angles = np.linspace(right_side_angle, left_side_angle, 50)
            arc_x = apex_x + apex_arc_radius * np.cos(arc_angles)
            arc_y = apex_y + apex_arc_radius * np.sin(arc_angles)
            ax.plot(arc_x, arc_y, 'c-', linewidth=2)
            ax.text(apex_x, apex_y - apex_arc_radius - 0.15,
                    f'A = {prism_angle}°', fontsize=10, fontweight='bold',
                    color='cyan', ha='center', va='top')
            
            # Sudut deviasi (δ) - untuk sinar merah saja
            # Sudut antara perpanjangan sinar datang dan sinar keluar
            if len(exit_points_data) > 0:
                data = exit_points_data[0]
                exit_direction = right_surface_normal_angle - data['i2_rad']
                
                # Cari titik perpotongan antara perpanjangan sinar datang dan sinar keluar
                # Sinar datang: dari incident_start ke entry_point, diperpanjang
                # Sinar keluar: dari exit_point ke final_exit, diperpanjang
                
                # Untuk visualisasi, gambar busur sudut deviasi di dekat sinar keluar
                dev_arc_radius = 2.5
                dev_center_x = exit_x
                dev_center_y = exit_y
                
                # Sudut perpanjangan sinar datang (ke depan)
                incident_extension_angle = incident_direction + np.pi
                # Sudut sinar keluar
                exit_angle = exit_direction
                
                # Gambar busur sudut deviasi
                start_angle = min(incident_extension_angle, exit_angle)
                end_angle = max(incident_extension_angle, exit_angle)
                
                arc_angles = np.linspace(start_angle, end_angle, 50)
                arc_x = dev_center_x + dev_arc_radius * np.cos(arc_angles)
                arc_y = dev_center_y + dev_arc_radius * np.sin(arc_angles)
                ax.plot(arc_x, arc_y, 'r-', linewidth=2, linestyle='--')
                
                # Label sudut deviasi
                mid_angle = (start_angle + end_angle) / 2
                ax.text(dev_center_x + (dev_arc_radius+0.3) * np.cos(mid_angle),
                        dev_center_y + (dev_arc_radius+0.3) * np.sin(mid_angle),
                        f'δ = {result["delta"]:.1f}°', fontsize=10,
                        fontweight='bold', color='red',
                        ha='center', va='center')
        
        # Set limits
        ax.set_xlim(-6, 6)
        ax.set_ylim(-1, 7)
        ax.set_aspect('equal')
        ax.axis('off')
        
        if show_spectrum:
            ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        
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
