import streamlit as st
import re

# Casas y sus emojis
CASAS = {
    "Wampus": ["❤️", "♥️"],
    "Thunder": ["💙"],
    "Pukukis": ["💛"],
    "Serpientes": ["💚"]
}

# Lista completa de alumnos y sus emojis
ALUMNOS = {
    "h: ~criiz🗺️": "🗺️",
    "Cangu 🦘🇵🇦 Ilvermorny": "🦘",
    "Gris 🦄🇻🇪 Warriors": "🦄",
    "Gwen FG 🦖🐬🇲🇽 Wampus": "🦖",
    "Lauren 🦠🇵🇪 Htr": "🦠",
    "Mitai 🧟‍♀️🖤🇲🇽 2 HTR": "🧟‍♀️",
    "Darwin 🐾🇧🇴 Htr": "🐾",
    "Ed 🌠🇵🇪 Ilver": "🌠",
    "Ed 🦊🇵🇪 Warriors": "🦊",
    "Enzo 🐷🇦🇷 Circus": "🐷",
    "Michu 😾🇪🇨 Ilver": "😾",
    "Tabora 🐈‍⬛🇭🇳 Lsdm": "🐈‍⬛",
    "Tori 💎🇵🇾 Warriors": "💎",
    "+593 99 659 2587": "🌲",
    "+51 985 106 499": "🦈",
    "+52 1 56 1287 6598": "🛋️",
    "+52 1 55 3913 5014": "🐸",
    "+51 921 860 730": "🧣",
    "+505 7642 9575": "🪵",
    "+52 1 722 333 7959": "🫧",
    "+54 9 11 2862-5347": "🌺",
    "+51 931 201 174": "🦝"
}

st.title("📊 Contador de Participaciones en Dinámica")

# Elegir casa
casa = st.selectbox("Selecciona tu casa", list(CASAS.keys()))
emojis_casa = CASAS[casa]

# Nombre de la dinámica
nombre_ronda = st.text_input("Nombre de la dinámica")

# Número de rondas
num_rondas = st.number_input("Número de rondas", min_value=1, step=1)

# Respuestas correctas por ronda
st.subheader("✅ Respuestas correctas por ronda (una respuesta por línea)")
respuestas_correctas = []
for i in range(num_rondas):
    respuestas = st.text_area(f"Ronda {i+1}", height=100)
    respuestas_correctas.append([line.strip() for line in respuestas.strip().splitlines() if line.strip()])

# Texto de la dinámica
st.subheader("📄 Texto completo de la dinámica")
texto_dinamica = st.text_area("Pega aquí todo el texto (incluye los timestamps)", height=500)

# Checkbox para coincidencia exacta
match_exacto = st.checkbox("Coincidencia exacta (distingue mayúsculas y minúsculas)", value=False)

if st.button("🔍 Analizar participación"):
    mensajes = re.split(r"\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}(?:/\d{4})?\]", texto_dinamica)[1:]

    resultados = {}
    desglose = {alumno: [False]*num_rondas for alumno in ALUMNOS}
    usados_wampus = set()
    usados_rivales = set()

    for idx_ronda in range(num_rondas):
        respuestas = respuestas_correctas[idx_ronda]
        for mensaje in mensajes:
            mensaje = mensaje.strip()
            if not mensaje:
                continue

            mensaje_comp = mensaje if match_exacto else mensaje.lower()
            respuestas_comp = respuestas if match_exacto else [r.lower() for r in respuestas]
            emojis_casa_comp = emojis_casa if match_exacto else [e.lower() for e in emojis_casa]

            contiene_respuesta = any(r in mensaje_comp for r in respuestas_comp)
            contiene_emocasa = any(e in mensaje_comp for e in emojis_casa_comp)

            if contiene_respuesta and contiene_emocasa:
                for alumno, emoji in ALUMNOS.items():
                    emoji_comp = emoji if match_exacto else emoji.lower()
                    if emoji_comp in mensaje_comp:
                        desglose[alumno][idx_ronda] = True

                        if any(e in mensaje for e in CASAS["Wampus"]):
                            usados_wampus.add(emoji)
                        elif any(e in mensaje for casa in ["Thunder", "Pukukis", "Serpientes"] for e in CASAS[casa]):
                            usados_rivales.add(emoji)

    st.subheader("📋 Resultados por alumno")
    for alumno, emoji in ALUMNOS.items():
        aciertos = sum(desglose[alumno])
        tiene_parti = aciertos >= 5
        st.write(f"{emoji} {'✅' if tiene_parti else '❌'} — {aciertos} participaciones correctas")

        if st.checkbox(f"Ver detalle por ronda para {emoji}", key=alumno):
            for i, estado in enumerate(desglose[alumno]):
                st.write(f"Ronda {i+1}: {'✔️' if estado else '❌'}")

    st.subheader("🏠 Estadísticas por casa")
    st.write(f"Total de participantes con emojis de Wampus (❤️, ♥️): {len(usados_wampus)}")
    st.write(f"Total con emojis de casas rivales (💙, 💛, 💚): {len(usados_rivales)}")
