import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

# --- ПОДЕШАВАЊА СТРАНИЦЕ ---
st.set_page_config(page_title="НБС IPS QR Генератор", page_icon="💳", layout="centered")

st.title("💳 НБС IPS QR Генератор плаћања")
st.write("Попуните променљива поља за генерисање QR кода.")

# --- СТАЛНИ ПОДАЦИ ПРИМАОЦА (Конфигурација у бочној траци) ---
st.sidebar.header("⚙️ Подешавања примаоца")
RACUN_PRIMAOCA = st.sidebar.text_input("Рачун примаоца:", value="265-1100310095965-50")
NAZIV_PRIMAOCA = st.sidebar.text_input("Назив примаоца:", value="FIZIOFIT TIM BEOGRAD")
SIFRA_PLACANJA = st.sidebar.text_input("Шифра плаћања:", value="289")

# --- ФОРМА ЗА УНОС ПОДАТАКА ---
col1, col2 = st.columns(2)

with col1:
    iznos_input = st.text_input("Износ (РСД):", value="1500")
    svrha_input = st.text_input("Сврха плаћања:", value="Уплата по рачуну 01-2026")

with col2:
    poziv_input = st.text_input("Позив на број (опционо):", value="")

# --- ФУНКЦИЈА ЗА АУТОМАТСКО ФОРМАТИРАЊЕ И ГЕНЕРИСАЊЕ IPS СТРИНГА ---
def napravi_ips_string(racun, naziv, iznos, sf, svrha, poziv):
    # 1. Санирање рачуна (остави само цифре)
    racun_clean = "".join(filter(str.isdigit, str(racun)))
    
    # 2. Аутоматско форматирање износа на 2 децимале са запетом (нпр. 1500 -> 1500,00)
    raw_iznos = str(iznos).strip().replace(' ', '').replace(',', '.')
    try:
        val = float(raw_iznos)
        iznos_formatted = f"{val:.2f}".replace('.', ',')
    except ValueError:
        iznos_formatted = "0,00"

    # 3. Текст по стандарду НБС IPS
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

# Генерисање IPS стринга
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
    
    # Спремање слике у меморију за приказ и преузимање
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.image(byte_im, caption="Генерисани НБС IPS QR код", width=250)
    
    # Опција за преузимање
    st.download_button(
        label="💾 Преузми QR код (PNG)",
        data=byte_im,
        file_name="NBS_IPS_QR.png",
        mime="image/png"
    )
