import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.optimize import curve_fit

# =========================
# HEADER
# =========================
st.title("Simulasi Dispersi Cahaya pada Prisma")
st.markdown("Dikembangkan oleh **Felix Marcellino Henrikus**")

# =========================
# SIDEBAR PARAMETER
# =========================
theta1_deg = st.sidebar.slider("Sudut datang (°)", 0.0, 80.0, 30.0)
A_deg = st.sidebar.slider("Sudut puncak prisma (°)", 30.0, 80.0, 60.0)
model = st.sidebar.selectbox("Model Dispersi", ["Cauchy", "Sellmeier"])

theta1 = np.radians(theta1_deg)
A = np.radians(A_deg)

# =========================
# MODEL FISIKA
# =========================
def snell(theta, n1, n2):
    return np.arcsin(n1/n2 * np.sin(theta))

def prism_trace(theta1, A, n):
    theta2 = snell(theta1, 1, n)
    theta3 = A - theta2
    theta4 = snell(theta3, n, 1)
    delta = theta1 + theta4 - A
    return theta2, theta3, theta4, delta

def cauchy(lam):
    A = 1.5
    B = 4000
    return A + B/(lam**2)

def sellmeier(lam):
    lam = lam/1000
    B1, B2, B3 = 1.03961212, 0.231792344, 1.01046945
    C1, C2, C3 = 0.00600069867, 0.0200179144, 103.560653
    n2 = 1 + (B1*lam**2)/(lam**2 - C1) + \
            (B2*lam**2)/(lam**2 - C2) + \
            (B3*lam**2)/(lam**2 - C3)
    return np.sqrt(n2)

def wavelength_to_rgb(wl):
    if wl < 450:
        return "blue"
    elif wl < 495:
        return "cyan"
    elif wl < 570:
        return "green"
    elif wl < 590:
        return "yellow"
    elif wl < 620:
        return "orange"
    else:
        return "red"

# =========================
# GEOMETRI PRISMA
# =========================
def prism_geometry(A):
    h = 1
    base = 2 * h * np.tan(A/2)
    p1 = (-base/2, 0)
    p2 = (base/2, 0)
    p3 = (0, h)
    return p1, p2, p3

# =========================
# VISUALISASI
# =========================
fig = go.Figure()

p1, p2, p3 = prism_geometry(A)

# prisma
fig.add_trace(go.Scatter(
    x=[p1[0], p2[0], p3[0], p1[0]],
    y=[p1[1], p2[1], p3[1], p1[1]],
    mode='lines',
    name='Prisma'
))

# spektrum
wavelengths = np.linspace(400, 700, 25)

delta_sample = None

for wl in wavelengths:
    n = cauchy(wl) if model == "Cauchy" else sellmeier(wl)
    theta2, theta3, theta4, delta = prism_trace(theta1, A, n)

    if wl == 550:
        delta_sample = delta

    color = wavelength_to_rgb(wl)

    # sinar datang
    fig.add_trace(go.Scatter(
        x=[-2, 0],
        y=[np.tan(theta1)*-2, 0],
        mode='lines',
        line=dict(color=color),
        showlegend=False
    ))

    # sinar keluar
    fig.add_trace(go.Scatter(
        x=[0, 2],
        y=[0, np.tan(theta4)*2],
        mode='lines',
        line=dict(color=color),
        showlegend=False
    ))

fig.update_layout(
    title="Ray Tracing dan Dispersi",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

st.plotly_chart(fig)

# =========================
# OUTPUT NUMERIK
# =========================
st.subheader("Sudut Deviasi")

if delta_sample is not None:
    st.metric("Deviasi (°)", f"{np.degrees(delta_sample):.2f}")

# =========================
# FORMULASI MATEMATIS
# =========================
st.subheader("Formulasi Matematis")

st.latex(r"n_1 \sin \theta_1 = n_2 \sin \theta_2")
st.latex(r"\delta = \theta_1 + \theta_4 - A")
st.latex(r"n(\lambda) = A + \frac{B}{\lambda^2}")

st.markdown("""
Keterangan:
- θ₁ : sudut datang
- θ₂ : sudut dalam prisma
- θ₄ : sudut keluar
- A : sudut puncak prisma
""")

# =========================
# FITTING DISPERSI
# =========================
st.subheader("Fitting Model Dispersi")

data = []
for wl in wavelengths:
    n = cauchy(wl)
    data.append([wl, n])

data = np.array(data)

def cauchy_fit(lam, A, B):
    return A + B/(lam**2)

params, _ = curve_fit(cauchy_fit, data[:,0], data[:,1])

fig2 = go.Figure()
fig2.add_scatter(x=data[:,0], y=data[:,1],
                 mode='markers', name='Data')
fig2.add_scatter(x=data[:,0],
                 y=cauchy_fit(data[:,0], *params),
                 mode='lines', name='Fit Cauchy')

st.plotly_chart(fig2)
