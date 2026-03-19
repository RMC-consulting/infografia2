import streamlit as st
import smtplib
import re
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Librería para convertir PDF a imagen
import fitz  # PyMuPDF

# ============================================
# CONFIGURACIÓN GENERAL
# ============================================
st.set_page_config(
    page_title="Descarga de documento",
    page_icon="📄",
    layout="centered"
)

# ============================================
# CONFIGURACIÓN DE RUTAS
# ============================================
BASE_DIR = Path(__file__).resolve().parent
PDF_FILENAME = "RMC-Flyer Sector Financiero (infografia).PDF"
PDF_PATH = BASE_DIR / PDF_FILENAME

# ============================================
# CONFIGURACIÓN DE CORREO
# ============================================
REMITENTE = "mkt.rochamendoza@gmail.com"
DESTINATARIO = "mkt.rochamendoza@gmail.com"
CONTRASENA_APP = "flub pyvf mjhn jfgb"
ASUNTO_CORREO = "Nuevo registro de descarga de PDF"

# ============================================
# SESSION STATE
# ============================================
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "descarga_habilitada" not in st.session_state:
    st.session_state.descarga_habilitada = False

# ============================================
# ESTILOS
# ============================================
st.markdown("""
<style>
.stApp {
    background-color: #f4f6f8 !important;
    color: #111111 !important;
}

.main-box {
    background-color: #ffffff !important;
    padding: 2.2rem !important;
    border-radius: 14px !important;
    margin-top: 1.5rem !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
}

h1, h2, h3 {
    color: #0f172a !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
    font-weight: 700 !important;
}

p, div, span, label {
    font-family: "Segoe UI", Arial, sans-serif !important;
}

[data-testid="stMarkdownContainer"] p {
    color: #1f2937 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #E5E7EB !important;
    color: #111111 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #6B7280 !important;
}

.stTextInput label,
.stTextArea label {
    color: #111111 !important;
    font-weight: 600 !important;
}

.stButton > button,
.stDownloadButton > button,
.stForm button {
    background-color: #14532d !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.70rem 1.25rem !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 10px rgba(20,83,45,0.20) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stForm button:hover {
    background-color: #166534 !important;
    color: #ffffff !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div,
.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button div,
.stForm button p,
.stForm button span,
.stForm button div {
    color: #ffffff !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}

.preview-note {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 14px;
    color: #334155;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES
# ============================================
def correo_valido(correo: str) -> bool:
    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(patron, correo) is not None


def cargar_pdf_desde_proyecto():
    ruta = PDF_PATH

    if not ruta.exists():
        return False, f"No se encontró el archivo PDF en la ruta: {ruta}"

    try:
        with open(ruta, "rb") as f:
            st.session_state.pdf_bytes = f.read()
            st.session_state.pdf_name = ruta.name
        return True, None
    except Exception as e:
        return False, f"Error al leer el PDF: {e}"


def mostrar_pdf_como_imagenes(pdf_bytes):
    """
    Convierte el PDF a imágenes y las muestra en Streamlit.
    Esta es la forma más estable para vista previa.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        if len(doc) == 0:
            st.warning("El PDF no contiene páginas.")
            return

        # Puedes cambiar esto si quieres ver todas las páginas
        # max_paginas = len(doc)
        max_paginas = len(doc)

        for i in range(max_paginas):
            page = doc.load_page(i)

            # Más calidad
            matrix = fitz.Matrix(1.8, 1.8)
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            img_bytes = pix.tobytes("png")
            st.image(img_bytes, use_container_width=True)

        doc.close()

    except Exception as e:
        st.error(f"No se pudo mostrar la vista previa del PDF: {e}")


def enviar_correo_registro(nombre, correo, empresa, telefono, comentarios, pdf_name):
    cuerpo = f"""
Se ha registrado una nueva descarga de documento.

Datos del registro:
- Nombre: {nombre}
- Correo: {correo}
- Empresa: {empresa}
- Teléfono: {telefono}
- Comentarios: {comentarios}
- Documento solicitado: {pdf_name}
"""

    msg = MIMEMultipart()
    msg["From"] = REMITENTE
    msg["To"] = DESTINATARIO
    msg["Subject"] = ASUNTO_CORREO
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(REMITENTE, CONTRASENA_APP)
        server.sendmail(REMITENTE, DESTINATARIO, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# ============================================
# CARGA INICIAL DEL PDF
# ============================================
if st.session_state.pdf_bytes is None:
    ok_pdf, error_pdf = cargar_pdf_desde_proyecto()
else:
    ok_pdf, error_pdf = True, None

# ============================================
# INTERFAZ
# ============================================
st.markdown("<div class='main-box'>", unsafe_allow_html=True)

st.title("Descarga de documento")

st.write("Consulta el documento y completa tus datos para habilitar la descarga.")

# ============================================
# VISTA PREVIA DEL PDF
# ============================================
st.subheader("Vista previa del documento")

if ok_pdf and st.session_state.pdf_bytes:
     mostrar_pdf_como_imagenes(st.session_state.pdf_bytes)
else:
    st.error(error_pdf if error_pdf else "No fue posible cargar el PDF.")

# ============================================
# FORMULARIO
# ============================================
st.subheader("Registro de datos")

with st.form("form_registro"):
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo electrónico")
    empresa = st.text_input("Empresa")
    telefono = st.text_input("Teléfono")
    comentarios = st.text_area("Comentarios", placeholder="Opcional")

    enviar = st.form_submit_button("Registrar y habilitar descarga")

    if enviar:
        if not ok_pdf or st.session_state.pdf_bytes is None:
            st.error("El documento no está disponible para descarga.")
        elif not nombre.strip():
            st.error("Debes capturar el nombre.")
        elif not correo_valido(correo.strip()):
            st.error("Debes capturar un correo válido.")
        elif not empresa.strip():
            st.error("Debes capturar la empresa.")
        else:
            ok_mail, error_mail = enviar_correo_registro(
                nombre=nombre.strip(),
                correo=correo.strip(),
                empresa=empresa.strip(),
                telefono=telefono.strip(),
                comentarios=comentarios.strip(),
                pdf_name=st.session_state.pdf_name
            )

            if ok_mail:
                st.session_state.descarga_habilitada = True
                st.success("Registro enviado correctamente. Ya puedes descargar el documento.")
            else:
                st.session_state.descarga_habilitada = False
                st.error(f"No se pudo enviar el correo: {error_mail}")

# ============================================
# DESCARGA
# ============================================

if st.session_state.descarga_habilitada and st.session_state.pdf_bytes is not None:
    st.download_button(
        label="📥 Descargar PDF",
        data=st.session_state.pdf_bytes,
        file_name=st.session_state.pdf_name,
        mime="application/pdf"
    )
else:
    st.info("La descarga se habilitará una vez que completes el registro.")

st.markdown("</div>", unsafe_allow_html=True)