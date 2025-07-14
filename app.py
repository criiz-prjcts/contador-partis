import streamlit as st
import re
import unicodedata
from collections import defaultdict

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

def normalizar(texto):
    texto = unicodedata.normalize("NFKC", texto)
    return texto if match_exacto else texto.lower().replace("️", "")

if st.button("🔍 Analizar participación"):
    mensajes = re.split(r"\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}(?:/\d{4})?\]", texto_dinamica)[1:]

    desglose = {alumno: [False]*num_rondas for alumno in ALUMNOS}
    mensajes_match = {alumno: [[] for _ in range(num_rondas)] for alumno in ALUMNOS}
    mensajes_totales = {alumno: [[] for _ in range(num_rondas)] for alumno in ALUMNOS}
    usados_wampus = set()
    usados_rivales = set()

    for idx_ronda in range(num_rondas):
        respuestas = respuestas_correctas[idx_ronda]
        respuestas_comp = respuestas if match_exacto else [normalizar(r) for r in respuestas]

        for mensaje in mensajes:
            mensaje = mensaje.replace("\n", " ").strip()
            if not mensaje:
                continue

            mensaje_comp = normalizar(mensaje)

            # Extraer remitente
            if ":" in mensaje:
                remitente = mensaje.split(":", 1)[0].strip()
            else:
                continue  # saltar si no hay remitente claro

            for alumno, emoji in ALUMNOS.items():
                if remitente.startswith(alumno):
                    contiene_respuesta = any(r in mensaje_comp for r in respuestas_comp)
                    contiene_emocasa = any(normalizar(e) in mensaje_comp for e in emojis_casa)

                    mensajes_totales[alumno][idx_ronda].append(mensaje)

                    if contiene_respuesta and contiene_emocasa and not desglose[alumno][idx_ronda]:
                        desglose[alumno][idx_ronda] = True
                        mensajes_match[alumno][idx_ronda].append(mensaje)

                        if any(e in mensaje for e in CASAS["Wampus"]):
                            usados_wampus.add(emoji)
                        elif any(e in mensaje for casa in ["Thunder", "Pukukis", "Serpientes"] for e in CASAS[casa]):
                            usados_rivales.add(emoji)
                    break

    mostrar_resumen = st.checkbox("Mostrar resumen compacto (solo emoji y resultado)")

    st.subheader("📋 Resultados por alumno")
    for alumno, emoji in ALUMNOS.items():
        aciertos = sum(desglose[alumno])
        tiene_parti = aciertos >= 5
        resumen = f"{emoji} {'✅' if tiene_parti else '❌'} ({aciertos})"

        if mostrar_resumen:
            st.write(resumen)
        else:
            st.markdown(f"### {emoji} {alumno}")
            for i, estado in enumerate(desglose[alumno]):
                st.write(f"Ronda {i+1}: {'✅' if estado else '❌'}")
                if estado:
                    st.text_area(
                        f"✅ Mensajes que hicieron match (R{i+1})",
                        "\n\n".join(mensajes_match[alumno][i]),
                        height=120,
                        key=f"ok_{emoji}_r{i+1}"
                    )
                sin_match = set(mensajes_totales[alumno][i]) - set(mensajes_match[alumno][i])
                if sin_match:
                    st.text_area(
                        f"📝 Mensajes encontrados SIN match (R{i+1})",
                        "\n\n".join(sin_match),
                        height=120,
                        key=f"no_{emoji}_r{i+1}"
                    )

    st.subheader("🏠 Estadísticas por casa")
    st.write(f"Wampus (❤️, ♥️): {len(usados_wampus)} participantes")
    st.write(f"Rivales (💙, 💛, 💚): {len(usados_rivales)} participantes")

    st.subheader("📌 Uso individual de emojis Wampus")
    for emoji in ["❤️", "♥️"]:
        count = sum(m.count(emoji) for m in mensajes)
        st.write(f"{emoji}: {count} veces")

    st.subheader("📄 Resumen de la dinámica para copiar")
    resumen = [nombre_ronda]
    for alumno, emoji in ALUMNOS.items():
        check = "✅" if sum(desglose[alumno]) >= 5 else "❌"
        total = sum(desglose[alumno])
        resumen.append(f"{emoji} {check} ({total})")
    st.code("\n".join(resumen), language="")

    st.subheader("✅ Respuestas correctas por casa (por mensaje)")
    correctos_por_casa = {casa: 0 for casa in CASAS}
    for i in range(num_rondas):
        respuestas = respuestas_correctas[i]
        respuestas_comp = respuestas if match_exacto else [normalizar(r) for r in respuestas]
        for mensaje in mensajes:
            mensaje_comp = normalizar(mensaje)
            if any(r in mensaje_comp for r in respuestas_comp):
                for casa, casa_emojis in CASAS.items():
                    if any(normalizar(e) in mensaje_comp for e in casa_emojis):
                        correctos_por_casa[casa] += 1
                        break
    for casa, count in correctos_por_casa.items():
        st.write(f"{casa}: {count} respuestas correctas")
