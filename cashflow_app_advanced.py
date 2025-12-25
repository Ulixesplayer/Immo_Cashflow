import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
import tempfile
import os

# =========================
# App Titel
# =========================
st.title("Immobilien Cashflow-Simulator Advanced")

# =========================
# Eingaben
# =========================
st.sidebar.header("Parameter einstellen")
kaufpreis = st.sidebar.number_input("Kaufpreis (€)", value=1350000)
tilgung = st.sidebar.slider("Tilgung (%)", 0.5, 5.0, 1.0) / 100
steuersatz = st.sidebar.slider("Steuersatz (%)", 0.0, 50.0, 42.0) / 100
ek_quote = st.sidebar.selectbox("Eigenkapitalquote", [0.0, 0.05, 0.10, 0.20])
zins_min = st.sidebar.slider("Zins min (%)", 2.0, 5.0, 2.0)
zins_max = st.sidebar.slider("Zins max (%)", 2.0, 5.0, 5.0)
miete_min = st.sidebar.slider("Miete min (€)", 3000, 6000, 3000)
miete_max = st.sidebar.slider("Miete max (€)", 3000, 6000, 5000)

zinse = np.arange(zins_min, zins_max + 0.001, 0.05) / 100
mieten = np.arange(miete_min, miete_max + 1, 100)

# =========================
# Berechnung
# =========================
def berechne_cashflow(kaufpreis, ek_quote, tilgung, steuersatz, zinse, mieten):
    kredit = kaufpreis * (1 - ek_quote)
    cashflow = np.zeros((len(mieten), len(zinse)))
    for i, miete in enumerate(mieten):
        for j, zins in enumerate(zinse):
            annuitaet_monat = kredit * (zins + tilgung) / 12
            steuer_vorteil = (kredit * zins / 12) * steuersatz
            cashflow[i, j] = miete - annuitaet_monat + steuer_vorteil
    return cashflow

cashflow = berechne_cashflow(kaufpreis, ek_quote, tilgung, steuersatz, zinse, mieten)

  # =========================
# Heatmap anzeigen
# =========================
fig = go.Figure(data=go.Heatmap(
    z=cashflow,
    x=zinse * 100,
    y=mieten,
    colorscale='RdYlGn',
    zmin=-2500, zmax=2500,
    colorbar=dict(title="Cashflow (€)")
))
fig.update_layout(title="Cashflow inkl. Steuerersparnis",
                  xaxis_title="Zinssatz (%)",
                  yaxis_title="Monatliche Nettomiete (€)")

st.plotly_chart(fig)

# =========================
# PDF Export
# =========================
if st.button("Export als PDF"):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name)
    c.drawString(100, 800, "Cashflow-Simulation")
    c.drawString(100, 780, f"Kaufpreis: {kaufpreis} €, EK-Quote: {ek_quote*100} %")
    c.drawString(100, 760, f"Tilgung: {tilgung*100} %, Steuersatz:{steuersatz*100} %")
    c.save()
    st.download_button("Download PDF", data=open(temp_file.name, "rb"), file_name="cashflow_report.pdf")

# =========================
# Animation der Break-even-Linien
# =========================
jahre = st.slider("Animation: Jahre", 1, 30, 1)
restschuld = kaufpreis * (1 - ek_quote) * ((1 - tilgung) ** jahre)
cashflow_jahr = berechne_cashflow(kaufpreis, ek_quote, tilgung, steuersatz, zinse, mieten)

fig_anim = go.Figure(data=go.Heatmap(
    z=cashflow_jahr,
    x=zinse * 100,
    y=mieten,
    colorscale='RdYlGn',
    zmin=-2500, zmax=2500
))
fig_anim.update_layout(title=f"Cashflow nach {jahre} Jahren",
                       xaxis_title="Zinssatz (%)",
                       yaxis_title="Monatliche Nettomiete (€)")
st.plotly_chart(fig_anim)
 
