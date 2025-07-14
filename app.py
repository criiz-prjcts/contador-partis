import streamlit as st
import unicodedata
import re
from collections import defaultdict

st.set_page_config(page_title="Contador de Participación", page_icon="📊")
st.title("📊 Contador de Participación en Dinámicas")

# --- Funciones auxiliares ---
def normalizar(texto):
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("️", "").replace("\u200d", "")
    return texto.lower().strip() if not match_exacto else texto.strip()

# --- Diccionarios predefinidos ---
ALUMNOS = {
    "h ~criiz🗺️": "🗺️",
    "Gwen FG 🦖🐬🇲🇽 Wampus": "🦖"
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
    desglose = defaultdict(lambda: [False]*num_rondas)
    mensajes_match = defaultdict(lambda: defaultdict(list))
    mensajes_no_match = defaultdict(lambda: defaultdict(list))
    aciertos_por_casa = {casa: 0 for casa in CASAS}
    participantes_por_casa = defaultdict(set)
    usados_wampus = set()
    usados_rivales = set()

    for idx_ronda in range(num_rondas):
        respuestas = respuestas_correctas[idx_ronda]
        respuestas_comp = respuestas if match_exacto else [normalizar(r) for r in respuestas]

        for mensaje in mensajes:
            mensaje = mensaje.replace("\n", " ").strip()
            if not mensaje:
                continue

            if ":" in mensaje:
                remitente, cuerpo = mensaje.split(":", 1)
                remitente = remitente.strip()
                cuerpo = cuerpo.strip()
            else:
                continue

            cuerpo_normalizado = normalizar(cuerpo)
            contiene_respuesta = any(r in cuerpo_normalizado for r in respuestas_comp)

            if contiene_respuesta:
                for c, emojilist in CASAS.items():
                    if any(e in cuerpo for e in emojilist):
                        desglose[remitente][idx_ronda] = True
                        mensajes_match[remitente][idx_ronda].append(mensaje)
                        aciertos_por_casa[c] += 1
                        participantes_por_casa[c].add(remitente)
                        if c == "Wampus":
                            emoji = ALUMNOS.get(remitente, remitente)
                            usados_wampus.add(emoji)
                        else:
                            usados_rivales.add(remitente)
                        break
            else:
                mensajes_no_match[remitente][idx_ronda].append(mensaje)

    st.header("📋 Resultados")
    resumen = ""
    for remitente, resultados in desglose.items():
        total = sum(resultados)
        emoji = ALUMNOS.get(remitente, remitente)
        tiene_parti = total >= 5
        st.write(f"{emoji} {'✅' if tiene_parti else '❌'} - {total} rondas")
        resumen += f"{emoji} {'✅' if tiene_parti else '❌'} - {total} rondas\n"

        with st.expander(f"📂 Detalle de {emoji}"):
            for i in range(num_rondas):
                st.markdown(f"**Ronda {i+1}:** {'✅' if resultados[i] else '❌'}")
                if mensajes_match[remitente][i]:
                    st.text_area("Mensajes válidos", value="\n".join(mensajes_match[remitente][i]), height=80, key=f"match_{remitente}_{i}")
                if mensajes_no_match[remitente][i]:
                    st.text_area("Mensajes encontrados sin coincidencia", value="\n".join(mensajes_no_match[remitente][i]), height=80, key=f"no_match_{remitente}_{i}")

    st.subheader("📌 Estadísticas generales")
    st.markdown(f"**Casa seleccionada:** {casa} {' '.join(emojis_casa)}")
    cantidad_alumnos = sum(1 for alumno in ALUMNOS if ALUMNOS[alumno] in emojis_casa)
    st.markdown(f"**Alumnos en esta casa:** {cantidad_alumnos}")
    st.markdown(f"**Wampus:** {len(usados_wampus)} personas")
    st.markdown(f"**Rivales:** {len(usados_rivales)} personas")
    for casa_nombre, cuenta in aciertos_por_casa.items():
        casa_emojis = ' '.join(CASAS[casa_nombre])
        participantes = len(participantes_por_casa[casa_nombre])
        st.markdown(f"**{casa_nombre} {casa_emojis}:** {cuenta} respuestas correctas por {participantes} participantes")

    st.code(f"{nombre_dinamica}\n{resumen.strip()}", language="text")
