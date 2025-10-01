import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64
from datetime import datetime

# --- Konfigurace Stránky Streamlit ---
# Nastavení titulku a širšího layoutu
st.set_page_config(
    page_title="Generátor Bodů na Kružnici",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Pomocné Funkce ---

def generate_circle_points(stred_x, stred_y, polomer, pocet_bodu):
    """Vypočítá souřadnice bodů na kružnici."""
    t = np.linspace(0, 2 * np.pi, pocet_bodu, endpoint=False)
    x = stred_x + polomer * np.cos(t)
    y = stred_y + polomer * np.sin(t)
    return x, y

def generate_pdf(params, fig, author_info):
    """Generuje PDF s parametry, grafem a kontaktními údaji pomocí ReportLab."""
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 

    # Uložení Matplotlib grafu do PNG bufferu
    plot_buffer = BytesIO()
    fig.savefig(plot_buffer, format='png', bbox_inches='tight') 
    plot_buffer.seek(0)
    
    # --- Obsah PDF ---
    
    # Hlavička
    p.setFont('Helvetica-Bold', 18)
    p.drawString(50, height - 50, "Technická Zpráva: Body na kružnici")
    
    # Parametry úlohy
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, height - 100, "Vstupní Parametry:")
    p.setFont('Helvetica', 12)
    p.drawString(70, height - 120, f"Střed (X, Y): ({params['stred_x']:.2f}, {params['stred_y']:.2f}) {params['jednotka']}")
    p.drawString(70, height - 140, f"Poloměr (R): {params['polomer']} {params['jednotka']}")
    p.drawString(70, height - 160, f"Počet bodů: {params['pocet_bodu']}")
    p.drawString(70, height - 180, f"Barva bodů: {params['barva_bodu']}")

    # Vložení grafu
    img_width = 450
    img_height = 450
    img_x = (width - img_width) / 2 # Centrování obrázku
    img_y = height - 200 - img_height
    p.drawImage(plot_buffer, img_x, img_y, img_width, img_height, preserveAspectRatio=True)

    # Informace o autorovi a kontaktu
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, 100, "Vygenerováno:")
    p.setFont('Helvetica', 12)
    p.drawString(70, 80, f"Jméno/Firma: {author_info['jmeno']}")
    p.drawString(70, 60, f"Kontakt: {author_info['kontakt']}")
    p.drawString(70, 40, f"Datum a čas: {author_info['datum']}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

# --- Vstupní Prvky (Sidebar) ---
st.sidebar.title("Nastavení Kružnice")

col_x, col_y = st.sidebar.columns(2)
with col_x:
    stred_x = st.number_input("Střed X", value=0.0, step=0.1, format="%.2f")
with col_y:
    stred_y = st.number_input("Střed Y", value=0.0, step=0.1, format="%.2f")

polomer = st.sidebar.slider("Poloměr (R)", min_value=1.0, max_value=20.0, value=10.0, step=0.1)
pocet_bodu = st.sidebar.slider("Počet bodů", min_value=3, max_value=200, value=50, step=1)
barva_bodu = st.sidebar.color_picker("Barva bodů", "#23C46C") # Zelená
jednotka = st.sidebar.text_input("Jednotka os (např. m, cm)", "m")

st.sidebar.divider()
st.sidebar.subheader("Info pro PDF Zprávu")
jmeno_autora = st.sidebar.text_input("Vaše jméno/firma", "AI Generátor Aplikací")
kontakt_autora = st.sidebar.text_input("Váš kontakt", "ai-generator@online.cz")


# --- Hlavní Aplikace (Generování a Vykreslení) ---

st.title("Generátor Bodů na Kružnici")

if polomer <= 0 or pocet_bodu < 3:
    st.error("Poloměr musí být kladný a počet bodů alespoň 3.")
else:
    # 1. Generování dat
    x, y = generate_circle_points(stred_x, stred_y, polomer, pocet_bodu)
    
    # 2. Vykreslení Grafu (Matplotlib)
    fig, ax = plt.subplots(figsize=(8, 8)) 
    
    ax.scatter(x, y, color=barva_bodu, s=30, label=f'{pocet_bodu} bodů')
    ax.plot(stred_x, stred_y, 'x', color='black', markersize=10, label='Střed')
    
    # Nastavení os a jednotek
    ax.set_title(f"Vizualizace bodů na kružnici (R={polomer} {jednotka})", fontsize=16)
    ax.set_xlabel(f"Osa X [{jednotka}]", fontsize=12)
    ax.set_ylabel(f"Osa Y [{jednotka}]", fontsize=12)
    
    ax.set_aspect('equal', adjustable='box')
    
    limit = polomer * 1.2
    ax.set_xlim(stred_x - limit, stred_x + limit)
    ax.set_ylim(stred_y - limit, stred_y + limit)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    st.subheader("Vykreslený Graf")
    st.pyplot(fig) # Zobrazení grafu ve Streamlit

    # 3. Tabulka s číselnými hodnotami
    st.subheader(f"Číselné Souřadnice Bodů (Jednotka: {jednotka})")
    data = {'X': np.round(x, 4), 'Y': np.round(y, 4)}
    df = pd.DataFrame(data)

    df_display = df.apply(lambda col: col.astype(str) + ' ' + jednotka)
    st.dataframe(df_display.head(15))

    # --- Tlačítko pro Tisk do PDF ---
    st.divider()
    
    pdf_params = {
        "stred_x": stred_x, "stred_y": stred_y, "polomer": polomer,
        "pocet_bodu": pocet_bodu, "barva_bodu": barva_bodu, "jednotka": jednotka
    }
    
    pdf_author_info = {
        "jmeno": jmeno_autora,
        "kontakt": kontakt_autora,
        "datum": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    pdf_buffer = generate_pdf(pdf_params, fig, pdf_author_info)
    
    st.download_button(
        label="Stáhnout Zprávu jako PDF",
        data=pdf_buffer,
        file_name=f"Zprava_Kruznice_R{polomer}{jednotka}.pdf",
        mime="application/pdf"
    )

    plt.close(fig)

# --- Informace o Aplikaci a Technologiích ---

st.divider()
st.header("Informace o Aplikaci a Technologiích")

tab1, tab2 = st.tabs(["O AI Generátoru", "Použité Technologie"])

with tab1:
    st.markdown("""
    Tento kód byl **vygenerován umělou inteligencí** (Google Gemini) a je připraven k nasazení na cloudových platformách, 
    jako je Streamlit Community Cloud. 
    """)

with tab2:
    st.markdown("""
    Aplikace využívá pouze **standardní a bezplatné** Python knihovny:
    
    * **Streamlit:** Pro interaktivní **webové rozhraní**.
    * **NumPy & Pandas:** Pro **matematické výpočty** a strukturování dat.
    * **Matplotlib:** Pro **vykreslení grafu** s přesnými číselnými hodnotami na osách.
    * **ReportLab:** Pro **generování PDF** (vytvoření zprávy s grafem a parametry).
    """)