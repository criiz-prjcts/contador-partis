import streamlit as st
import re

CASAS = {
    "Wampus": ["❤️", "♥️"],
    "Thunder": ["💙"],
    "Pukukis": ["💛"],
    "Serpientes": ["💚"]
}

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

casa = st.selectbox("Selecciona tu casa", list(CASAS.keys()))
emojis_casa = CASAS[casa]
nombre_ronda = st.text_input("Nombre de la dinámica")
num_rondas = st.number_input("Número de rondas", min_value=1, step=1)

st.subheader("✅ Respuestas correctas por ronda (una por línea)")
respuestas_correctas = []
for i in range(num_rondas):
    respuestas = st.text_area(f"Ronda {i+1}", height=100)
    respuestas_correctas.append([line.strip() for line in respuestas.strip().splitlines() if line.strip()])

st.subheader("📄 Texto completo de la dinámica")
texto_dinamica = st.text_area("Pega aquí todo el texto (incluye los timestamps)", height=500)

match_exacto = st.checkbox("Coincidencia exacta (distingue mayúsculas y minúsculas)", value=False)

if st.button("🔍 Analizar participación"):
    mensajes = re.split(r"\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}(?:/\d{4})?\]", texto_dinamica)[1:]

    desglose = {alumno: [False]*num_rondas for alumno in ALUMNOS}
    mensajes_match = {alumno: [[] for _ in range(num_rondas)] for alumno in ALUMNOS}
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
                        if not desglose[alumno][idx_ronda]:
                            desglose[alumno][idx_ronda] = True
                            mensajes_match[alumno][idx_ronda].append(mensaje)

                            if any(e in mensaje for e in CASAS["Wampus"]):
                                usados_wampus.add(emoji)
                            elif any(e in mensaje for casa in ["Thunder", "Pukukis", "Serpientes"] for e in CASAS[casa]):
                                usados_rivales.add(emoji)

    mostrar_resumen = st.checkbox("Mostrar resumen compacto (solo emoji y resultado)")

    st.subheader("📋 Resultados por alumno")
    for alumno, emoji in ALUMNOS.items():
        aciertos = sum(desglose[alumno])
        tiene_parti = aciertos >= 5
        resumen = f"{emoji} {'✅' if tiene_parti else '❌'} ({aciertos})"

        if mostrar_resumen:
            st.write(resumen)
        else:
            st.write(f"{resumen} — {alumno}")

            mostrar_detalle = st.checkbox(f"Ver detalle por ronda para {emoji}", key=f"ver_detalle_{emoji}")
            if mostrar_detalle:
                for i, estado in enumerate(desglose[alumno]):
                    st.write(f"Ronda {i+1}: {'✔️' if estado else '❌'}")
                    if estado:
                        st.text_area(
                            f"Mensajes que hicieron match en Ronda {i+1}",
                            "\n\n".join(mensajes_match[alumno][i]),
                            height=150,
                            key=f"mensajes_{emoji}_r{i+1}"
                        )

    st.subheader("🏠 Estadísticas por casa")
    st.write(f"Total de participantes con emojis de Wampus (❤️, ♥️): {len(usados_wampus)}")
    st.write(f"Total con emojis de casas rivales (💙, 💛, 💚): {len(usados_rivales)}")

    # Conteo individual de emojis de Wampus
    emoji_wampus_conteo = {"❤️": 0, "♥️": 0}
    for mensaje in mensajes:
        for emoji in emoji_wampus_conteo:
            emoji_wampus_conteo[emoji] += mensaje.count(emoji)

    st.subheader("📌 Uso individual de emojis Wampus")
    for emoji, count in emoji_wampus_conteo.items():
        st.write(f"{emoji} fue usado {count} veces en total")
