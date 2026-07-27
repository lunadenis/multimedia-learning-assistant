import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
from google import genai
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================
# El programa busca este PDF dentro del mismo repositorio.
PDF_PATH = Path(__file__).parent / "base_conocimiento_multimedia_learning_assistant.pdf"

# Modelo de lenguaje usado para redactar la respuesta final.
MODEL_NAME = "gemini-2.5-flash"

# Si la similitud entre la pregunta y el documento es demasiado baja,
# el agente reconoce que no encontró suficiente información.
MIN_RELEVANCE = 0.045

# Cantidad de fragmentos del PDF que se entregan a Gemini.
TOP_K = 4


st.set_page_config(
    page_title="Multimedia Learning Assistant",
    page_icon="🎬",
    layout="centered",
)


# ============================================================
# 2. LIMPIEZA DEL TEXTO
# ============================================================
def normalize_text(text: str) -> str:
    """Elimina espacios repetidos sin cambiar el contenido."""
    return re.sub(r"\s+", " ", text or "").strip()


# ============================================================
# 3. LECTURA Y PROCESAMIENTO DEL PDF
# ============================================================
@st.cache_resource(show_spinner=False)
def load_knowledge_base(
    pdf_path: str,
) -> Tuple[List[Dict], TfidfVectorizer, object]:
    """
    Lee el PDF, divide cada página en fragmentos y crea un índice TF-IDF.

    TF-IDF convierte el texto en números y permite comparar qué fragmentos
    tienen más relación con la pregunta escrita por la persona.
    """
    reader = PdfReader(pdf_path)
    chunks: List[Dict] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = normalize_text(page.extract_text())

        if not page_text:
            continue

        # Cada página se divide en fragmentos para que la búsqueda sea precisa.
        chunk_size = 1100
        overlap = 180
        start = 0

        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))
            fragment = page_text[start:end].strip()

            if fragment:
                chunks.append(
                    {
                        "text": fragment,
                        "page": page_number,
                        "source": PDF_PATH.name,
                    }
                )

            if end == len(page_text):
                break

            # El solapamiento conserva parte del contexto entre fragmentos.
            start = end - overlap

    if not chunks:
        raise ValueError("No fue posible extraer texto del documento PDF.")

    # Se construye el índice de búsqueda.
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        stop_words=None,
    )

    matrix = vectorizer.fit_transform(
        [chunk["text"] for chunk in chunks]
    )

    return chunks, vectorizer, matrix


# ============================================================
# 4. RECUPERACIÓN DE INFORMACIÓN
# ============================================================
def retrieve_context(
    question: str,
    chunks: List[Dict],
    vectorizer: TfidfVectorizer,
    matrix: object,
    top_k: int = TOP_K,
) -> Tuple[List[Dict], float]:
    """
    Compara la pregunta con todos los fragmentos y devuelve los más relevantes.
    """
    question_vector = vectorizer.transform([question])
    scores = cosine_similarity(question_vector, matrix).flatten()
    ranked_indices = scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:
        item = dict(chunks[index])
        item["score"] = float(scores[index])
        results.append(item)

    best_score = results[0]["score"] if results else 0.0
    return results, best_score


# ============================================================
# 5. CREACIÓN DEL PROMPT
# ============================================================
def build_prompt(question: str, retrieved: List[Dict]) -> str:
    """
    Construye las instrucciones que recibe Gemini.
    Gemini solo recibe la pregunta y los fragmentos recuperados del PDF.
    """
    context_blocks = []

    for index, item in enumerate(retrieved, start=1):
        context_blocks.append(
            f"[Fragmento {index} | Fuente: {item['source']} | "
            f"Página: {item['page']}]\n{item['text']}"
        )

    context = "\n\n".join(context_blocks)

    return f"""
Eres Multimedia Learning Assistant, un asistente educativo especializado
en lenguaje audiovisual y producción multimedia.

REGLAS OBLIGATORIAS:
1. Responde únicamente con la información del CONTEXTO proporcionado.
2. No utilices conocimiento externo ni inventes datos.
3. Si el contexto no permite responder, di exactamente:
   "No encontré esa información en la base de conocimiento disponible.
   Te recomiendo consultar la guía del proyecto o ampliar la documentación
   del agente."
4. Responde en español claro, natural y educativo.
5. Explica los conceptos de forma breve y comprensible para una persona
   que está aprendiendo.
6. Al final incluye una línea con este formato:
   Fuente consultada: base_conocimiento_multimedia_learning_assistant.pdf,
   página X
7. Si se usaron varias páginas, menciónalas sin repetirlas.
8. No inventes requisitos de evidencias, precios, fechas ni versiones
   de software.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:
""".strip()


# ============================================================
# 6. CLAVE PRIVADA Y CONEXIÓN CON GEMINI
# ============================================================
def get_api_key() -> str:
    """
    Busca la clave en Streamlit Secrets.
    También permite usar una variable de entorno al ejecutar localmente.
    """
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")


def generate_answer(
    question: str,
    retrieved: List[Dict],
    api_key: str,
) -> str:
    """Envía a Gemini la pregunta y el contexto recuperado."""
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(question, retrieved)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return (response.text or "").strip()


# ============================================================
# 7. INTERFAZ DE STREAMLIT
# ============================================================
st.title("🎬 Multimedia Learning Assistant")
st.caption(
    "Agente RAG para aprender lenguaje audiovisual y producción multimedia"
)

st.markdown(
    """
Este asistente consulta una base de conocimiento en PDF y responde preguntas
sobre secuencia, escena, plano, movimientos de cámara, guion técnico,
storyboard y etapas de producción multimedia.
"""
)

with st.expander("¿Cómo funciona este agente?"):
    st.markdown(
        """
1. Lee la base de conocimiento en PDF.  
2. Divide el documento en fragmentos pequeños.  
3. Compara la pregunta con esos fragmentos mediante TF-IDF.  
4. Recupera únicamente los textos más relacionados.  
5. Gemini redacta la respuesta usando ese contexto.  
6. La aplicación muestra la fuente y evita inventar información.
"""
    )


# ============================================================
# 8. CARGA DE LA BASE DE CONOCIMIENTO
# ============================================================
try:
    chunks, vectorizer, matrix = load_knowledge_base(str(PDF_PATH))
except Exception as error:
    st.error(f"No fue posible cargar la base de conocimiento: {error}")
    st.stop()


api_key = get_api_key()

if not api_key:
    st.warning(
        "La aplicación necesita la variable secreta GEMINI_API_KEY "
        "para generar respuestas."
    )


# ============================================================
# 9. PREGUNTAS SUGERIDAS
# ============================================================
example_questions = [
    "¿Cuál es la diferencia entre secuencia, escena y plano?",
    "¿Qué debe incluir un guion técnico?",
    "¿Qué diferencia hay entre zoom y travelling?",
    "¿Para qué sirve un storyboard?",
]

st.subheader("Preguntas de ejemplo")

columns = st.columns(2)
selected_question = None

for index, example in enumerate(example_questions):
    if columns[index % 2].button(example, use_container_width=True):
        selected_question = example


# ============================================================
# 10. HISTORIAL DE LA CONVERSACIÓN
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Limpiar conversación"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("Fragmentos recuperados"):
                for source in message["sources"]:
                    st.caption(
                        f"{source['source']} · página {source['page']} "
                        f"· relevancia {source['score']:.2f}"
                    )
                    st.write(source["text"])


# ============================================================
# 11. ENTRADA DEL USUARIO Y RESPUESTA DEL AGENTE
# ============================================================
typed_question = st.chat_input(
    "Escribe una pregunta sobre lenguaje audiovisual o producción multimedia"
)

question = selected_question or typed_question

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento..."):
            retrieved, best_score = retrieve_context(
                question,
                chunks,
                vectorizer,
                matrix,
            )

            if best_score < MIN_RELEVANCE:
                answer = (
                    "No encontré esa información en la base de conocimiento "
                    "disponible. Te recomiendo consultar la guía del proyecto "
                    "o ampliar la documentación del agente."
                )

            elif not api_key:
                answer = (
                    "La recuperación documental funcionó, pero falta configurar "
                    "GEMINI_API_KEY para generar la respuesta."
                )

            else:
                try:
                    answer = generate_answer(
                        question,
                        retrieved,
                        api_key,
                    )
                except Exception as error:
                    answer = (
                        "No fue posible generar la respuesta en este momento. "
                        f"Detalle técnico: {error}"
                    )

        st.markdown(answer)

        with st.expander("Fragmentos recuperados"):
            for source in retrieved:
                st.caption(
                    f"{source['source']} · página {source['page']} "
                    f"· relevancia {source['score']:.2f}"
                )
                st.write(source["text"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": retrieved,
        }
    )


st.divider()
st.caption(
    "Proyecto educativo desarrollado para practicar agentes RAG · "
    "Las respuestas se limitan al documento incorporado."
)
