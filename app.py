import streamlit as st
import unicodedata
import re
from collections import defaultdict
import emoji

st.set_page_config(page_title="Contador de Participación", page_icon="📊")
st.title("📊 Contador de Participación en Dinámicas")

# --- Funciones auxiliares ---
def normalizar(texto):
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("️", "").replace("\u200d", "")  # elimina selectores invisibles
    return texto.lower().strip() if not match_exacto else texto.strip()

def limpiar_texto(texto):
    texto = normalizar(texto)
    texto = ''.join(c for c in texto if c.isalnum())
    return texto

# --- Diccionarios predefinidos ---
ALUMNOS = {
    "h ~criiz🗺️": "🗺️",
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

CASAS = {
    "Wampus": ["❤️", "♥️"],
    "Thunder": ["💙"],
    "Pukukis": ["💛"],
    "Serpies": ["💚"]
}

# --- Interfaz ---
casa = st.selectbox("Selecciona la casa de esta dinámica:", list(CASAS.keys()))
emojis_casa = CASAS[casa]
nombre_dinamica = st.text_input("Nombre de la dinámica")
num_rondas = st.number_input("¿Cuántas rondas hubo?", min_value=1, max_value=50, step=1)
match_exacto = st.checkbox("¿Coincidencia exacta (mayúsculas y símbolos incluidos)?")

respuestas_correctas = []
for i in range(num_rondas):
    respuestas = st.text_area(f"Respuesta(s) correcta(s) para la ronda {i+1} (una por línea)")
    respuestas_correctas.append([r.strip() for r in respuestas.strip().splitlines() if r.strip()])

texto_dinamica = st.text_area("Pega aquí todo el texto de la dinámica")

if st.button("🔍 Analizar participación"):
    mensajes = re.split(r"\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}(?:/\d{4})?\]", texto_dinamica)[1:]
    desglose = {alumno: [False]*num_rondas for alumno in ALUMNOS}
    mensajes_match = defaultdict(lambda: defaultdict(list))
    mensajes_totales = defaultdict(lambda: defaultdict(list))
    mensajes_no_match = defaultdict(lambda: defaultdict(list))
    usados_wampus = set()
    usados_rivales = set()
    aciertos_por_casa = {casa: 0 for casa in CASAS}

    for idx_ronda in range(num_rondas):
        respuestas = respuestas_correctas[idx_ronda]
        respuestas_comp = respuestas if match_exacto else [normalizar(r) for r in respuestas]

        for mensaje in mensajes:
            mensaje = mensaje.replace("\n", " ").strip()
            if not mensaje:
                continue

            mensaje_comp = normalizar(mensaje)

            if ":" in mensaje:
                remitente = mensaje.split(":", 1)[0].strip()
            else:
                continue

            for alumno, emoji in ALUMNOS.items():
                if normalizar(remitente) == normalizar(alumno):
                    mensajes_totales[alumno][idx_ronda].append(mensaje)
                    contiene_respuesta = any(r in mensaje_comp for r in respuestas_comp)
                    contiene_emocasa = any(normalizar(e) in mensaje_comp for e in emojis_casa)

                    if contiene_respuesta and contiene_emocasa:
                        desglose[alumno][idx_ronda] = True
                        mensajes_match[alumno][idx_ronda].append(mensaje)

                        for c, emojilist in CASAS.items():
                            if any(normalizar(e) in mensaje_comp for e in emojilist):
                                aciertos_por_casa[c] += 1

                        if any(normalizar(e) in mensaje_comp for e in CASAS["Wampus"]):
                            usados_wampus.add(emoji)
                        elif any(normalizar(e) in mensaje_comp for casa_r in ["Thunder", "Pukukis", "Serpientes"] for e in CASAS[casa_r]):
                            usados_rivales.add(emoji)
                    else:
                        mensajes_no_match[alumno][idx_ronda].append(mensaje)
                    break

    st.header("📋 Resultados")
    resumen = ""
    for alumno, resultados in desglose.items():
        total = sum(resultados)
        emoji = ALUMNOS[alumno]
        tiene_parti = total >= 5
        st.write(f"{emoji} {'✅' if tiene_parti else '❌'} - {total} rondas")
        resumen += f"{emoji} {'✅' if tiene_parti else '❌'} - {total} rondas\n"

        with st.expander(f"📂 Detalle de {emoji}"):
            for i in range(num_rondas):
                st.markdown(f"**Ronda {i+1}:** {'✅' if resultados[i] else '❌'}")
                if mensajes_match[alumno][i]:
                    st.text_area("Mensajes válidos", value="\n".join(mensajes_match[alumno][i]), height=80, key=f"match_{alumno}_{i}")
                if mensajes_no_match[alumno][i]:
                    st.text_area("Mensajes encontrados sin coincidencia", value="\n".join(mensajes_no_match[alumno][i]), height=80, key=f"no_match_{alumno}_{i}")

    st.subheader("📌 Estadísticas generales")
    st.markdown(f"**Casa seleccionada:** {casa} {' '.join(emojis_casa)}")
    cantidad_alumnos = sum(1 for emoji in ALUMNOS.values() if emoji in emojis_casa)
    st.markdown(f"**Alumnos en esta casa:** {cantidad_alumnos}")
    st.markdown(f"**Wampus:** {len(usados_wampus)} personas")
    st.markdown(f"**Rivales:** {len(usados_rivales)} personas")
    for casa_nombre, cuenta in aciertos_por_casa.items():
        casa_emojis = ' '.join(CASAS[casa_nombre])
        st.markdown(f"**{casa_nombre} {casa_emojis}:** {cuenta} respuestas correctas")

    st.text_area("📋 Resumen final (para copiar)", value=f"{nombre_dinamica}\n{resumen.strip()}", height=200)
