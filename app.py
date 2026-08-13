import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

# --- ПОДЕШАВАЊА СТРАНИЦЕ ---
st.set_page_config(page_title="НБС IPS QR Генератор", page_icon="💳", layout="centered")

st.title("💳 НБС IPS QR Генератор плаћања")
st.write("Попуните променљива поља за генерисање QR кода.")

# --- ЛИСТА ТЕКУЋИХ РАЧУНА (Овде упиши своје праве бројеве рачуна) ---
OPCIJE_RACUNA = {
    "Рачун 1 - Банка Интеса": "160-5100103505804-45",
    "Рачун 2 - Raiffeisen Bank": "265-7315567-41"
}

# --- СТАЛНИ ПОДАЦИ ПРИМАОЦА (Конфигурација у бочној траци) ---
st.sidebar.header("⚙️ Подешавања примаоца")

# Падајућа листа (combobox) за избор рачуна
izabrani_racun_naziv = st.sidebar.selectbox(
    "Изаберите текући рачун:",
    options=list(OPCIJE_RACUNA.keys())
)

# Преузимање тачног броја рачуна
RACUN_PRIMAOCA = OPCIJE_RACUNA[izabrani_racun_naziv]

# Приказ изабраног броја рачуна - наслов изнад, број испод у једном реду
st.sidebar.caption("Број изабраног рачуна:")
st.sidebar.markdown(f"**`{RACUN_PRIMAOCA}`**")

NAZIV_PRIMAOCA = st.sidebar.text_input("Назив примаоца:", value="МИЛОШ ПЕТРОВИЋ, БЕОГРАД")
SIFRA_PLACANJA = st.sidebar.text_input("Шифра плаћања:", value="289")

# --- ПОТПИС АУТОРА У БОЧНОЈ ТРАЦИ ---
st.sidebar.markdown("---")
st.sidebar.caption("👨‍💻 Дизајн и развој:")
st.sidebar.markdown("**Саша Петровић**")

# --- ФОРМА ЗА УНОС ПОДАТАКА ---
col1, col2 = st.columns(2)

with col1:
    iznos_input = st.text_input("Износ (РСД):", value="1500")
    svrha_input = st.text_input("Сврха плаћања:", value="Уплата по рачуну 01-2026")

with col2:
    poziv_input = st.text_input("Позив на број (опционо):", value="")

# --- ФУНКЦИЈА ЗА АУТОМАТСКО ФОРМАТИРАЊЕ И ГЕНЕРИСАЊЕ IPS СТРИНГА ---
def napravi_ips_string(racun, naziv, iznos, sf, svrha, poziv):
    racun_clean = "".join(filter(str.isdigit, str(racun)))
    
    raw_iznos = str(iznos).strip().replace(' ', '').replace(',', '.')
    try:
        val = float(raw_iznos)
        iznos_formatted = f"{val:.2f}".replace('.', ',')
    except ValueError:
        iznos_formatted = "0,00"

    ips = (
        f"K:PR"
        f"|V:01"
        f"|C:1"
        f"|R:{racun_clean}"
        f"|N:{naziv.strip()}"
        f"|I:RSD{iznos_formatted}"
        f"|SF:{sf.strip()}"
        f"|S:{svrha.strip()}"
    )

    if poziv and poziv.strip():
        ips += f"|RO:{poziv.strip()}"

    return ips

# Генерисање IPS стринга са изабраним рачуном
ips_tekst = napravi_ips_string(RACUN_PRIMAOCA, NAZIV_PRIMAOCA, iznos_input, SIFRA_PLACANJA, svrha_input, poziv_input)

st.markdown("---")

# Приказ генерисаног текста (за контролу)
with st.expander("🔍 Погледај генерисани IPS текст (за контролу)"):
    st.code(ips_tekst, language="text")

# --- ГЕНЕРИСАЊЕ И ПРИКАЗ QR КОДА ---
if st.button("🖼️ ГЕНЕРИШИ QR КОД", type="primary"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=3,
    )
    qr.add_data(ips_tekst)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.image(byte_im, caption=f"НБС IPS QR код за: {izabrani_racun_naziv}", width=250)
    
    st.download_button(
        label="💾 Преузми QR код (PNG)",
        data=byte_im,
        file_name="NBS_IPS_QR.png",
        mime="image/png"
    )

# --- ФУТЕР НА ДНУ ГЛАВНЕ СТРАНИЦЕ ---
st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: right; color: gray; font-size: 0.85em;'>"
    "Апликацију израдио: <b>Саша Петровић</b>"
    "</div>", 
    unsafe_allow_html=True
)
