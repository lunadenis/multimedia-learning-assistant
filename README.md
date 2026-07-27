# Multimedia Learning Assistant

Agente de inteligencia artificial desarrollado para responder consultas sobre lenguaje audiovisual, guion técnico, storyboard y producción multimedia a partir de una base de conocimiento en formato PDF.

La aplicación está dirigida a estudiantes, aprendices y personas que están comenzando a desarrollar productos audiovisuales y necesitan consultar conceptos de forma rápida y comprensible.

## Aplicación desplegada

Puedes probar el agente en:

[Multimedia Learning Assistant en Streamlit](https://multimedia-learning-assistant-wovcxkk7utzd8e6cggckys.streamlit.app)

## Problema que busca resolver

Los conceptos relacionados con lenguaje audiovisual y producción multimedia suelen encontrarse distribuidos en presentaciones, guías, apuntes y documentos diferentes.

Multimedia Learning Assistant centraliza esta información y permite realizar preguntas en lenguaje natural. La aplicación localiza los fragmentos más relacionados con la consulta y utiliza un modelo de lenguaje para generar una respuesta basada en el documento.

## Funcionalidades

- Lectura y procesamiento de un documento PDF.
- División del contenido en fragmentos.
- Búsqueda de información relacionada con cada pregunta.
- Generación de respuestas en lenguaje natural.
- Identificación del documento y las páginas consultadas.
- Historial de conversación durante la sesión.
- Visualización de los fragmentos recuperados.
- Control de respuestas cuando la información no está disponible.
- Despliegue público mediante Streamlit Community Cloud.

## Temas incluidos en la base de conocimiento

El agente puede responder preguntas relacionadas con:

- Secuencia, escena, plano y toma.
- Tipos de plano según el encuadre.
- Angulación de cámara.
- Movimientos de cámara.
- Guion literario y guion técnico.
- Storyboard.
- Preproducción, producción y posproducción.
- Continuidad y narrativa visual.
- Sonido, música y efectos.
- Resolución, formatos y exportación.

- ## Arquitectura de la solución

El flujo de la aplicación es el siguiente:

```text
Pregunta del usuario
        ↓
Lectura de la base de conocimiento
        ↓
División del PDF en fragmentos
        ↓
Conversión del texto mediante TF-IDF
        ↓
Comparación por similitud de coseno
        ↓
Recuperación de los fragmentos más relacionados
        ↓
Envío del contexto al modelo Gemini
        ↓
Respuesta fundamentada con referencia a la fuente
```
### Recuperación de información

El documento PDF se procesa con `pypdf` y se divide en fragmentos pequeños. Después, TF-IDF convierte esos fragmentos en una representación numérica y la similitud de coseno permite identificar cuáles tienen mayor relación con la pregunta realizada.

### Generación de la respuesta

Los fragmentos recuperados se envían al modelo Gemini junto con instrucciones que limitan la respuesta al contenido de la base de conocimiento. Si la información no aparece en el documento, el agente debe reconocerlo y evitar inventar datos.

### Interfaz de usuario

La aplicación utiliza Streamlit para presentar una interfaz sencilla con:

- Una explicación del propósito del agente.
- Preguntas sugeridas.
- Campo para escribir consultas.
- Historial de la conversación.
- Identificación de la fuente consultada.
- Visualización de los fragmentos recuperados.
- Opción para limpiar la conversación.

- ## Tecnologías utilizadas

| Tecnología | Uso dentro del proyecto |
|---|---|
| Python | Desarrollo de la aplicación |
| Streamlit | Creación de la interfaz web |
| Google Gemini | Generación de respuestas |
| pypdf | Lectura y extracción del contenido del PDF |
| scikit-learn | Búsqueda mediante TF-IDF y similitud de coseno |
| Git y GitHub | Control de versiones y publicación del código |
| Streamlit Community Cloud | Despliegue público de la aplicación |

## Estructura del repositorio

```text
multimedia-learning-assistant/
│
├── app.py
├── requirements.txt
├── base_conocimiento_multimedia_learning_assistant.pdf
├── README.md
├── .gitignore
│
└── evidencias/
    ├── README.md
    ├── 01-pantalla-inicial-multimedia.png
    ├── 02-secuencia-escena-plano.png
    ├── 03-guion-tecnico.png
    └── 04-control-informacion-no-disponible.png
```

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/bettelgeuxe/multimedia-learning-assistant.git
```

### 2. Entrar a la carpeta del proyecto

```bash
cd multimedia-learning-assistant
```

### 3. Crear un entorno virtual

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

En macOS o Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```
### 5. Configurar la clave de Gemini

Dentro del proyecto se debe crear esta ruta:

```text
.streamlit/secrets.toml
```

En el archivo `secrets.toml` se agrega:

```toml
GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"
```

La clave es privada y no debe publicarse en GitHub.

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en el navegador local.

## Ejemplos de preguntas

El agente puede responder consultas como:

- ¿Cuál es la diferencia entre secuencia, escena y plano?
- ¿Qué debe incluir un guion técnico?
- ¿Qué diferencia hay entre zoom y travelling?
- ¿Para qué sirve un storyboard?
- ¿Cuáles son las etapas de producción multimedia?
- ¿Qué resolución se recomienda para un video horizontal en alta definición?

## Ejemplo de respuesta

**Pregunta:**

> ¿Qué debe incluir un guion técnico?

**Respuesta generada:**

> Un guion técnico puede incluir el número de secuencia, escena y plano, la descripción visual, el tipo de plano, la angulación, el movimiento de cámara, el diálogo o sonido, la duración aproximada y las observaciones necesarias.

La aplicación también muestra el documento y la página utilizados para construir la respuesta.

## Control de información no disponible

Para comprobar que el agente no inventara respuestas, se realizó la siguiente consulta:

> ¿Cuál es el precio actual de Blender Studio?

Como ese dato no aparece en la base de conocimiento y puede cambiar con el tiempo, el agente indicó que no contaba con información suficiente y evitó generar una respuesta sin respaldo documental.

## Evidencias del funcionamiento

Las pruebas realizadas, las respuestas obtenidas y las capturas del despliegue se encuentran documentadas en:

[Ver evidencias del proyecto](evidencias/README.md)

## Despliegue

La aplicación se encuentra publicada en Streamlit Community Cloud:

[Probar Multimedia Learning Assistant](https://multimedia-learning-assistant-wovcxkk7utzd8e6cggckys.streamlit.app)

El despliegue está conectado con la rama `main` del repositorio. Cuando se actualiza el código en GitHub, Streamlit puede volver a desplegar automáticamente la aplicación.

## Seguridad

La clave de Gemini no está incluida dentro de `app.py` ni almacenada en el repositorio público.

Para el despliegue se utilizó el administrador de secretos de Streamlit, que permite mantener las credenciales separadas del código fuente.

## Posibles mejoras

Como continuación del proyecto se podrían implementar:

- Incorporación de nuevos documentos sobre animación 2D y 3D.
- Consulta de varias bases de conocimiento.
- Carga de archivos desde la interfaz.
- Clasificación de preguntas por temas.
- Inclusión de ejemplos visuales de planos y movimientos de cámara.
- Almacenamiento permanente del historial.
- Panel para administrar documentos.
- Uso de embeddings y una base de datos vectorial.
- Inclusión de guías de evidencias y criterios de evaluación.

## Contexto académico

Este proyecto fue desarrollado para el **Challenge Alura Agente**, correspondiente al programa Oracle Next Education y Alura Latam.

El objetivo del desafío es construir un agente funcional capaz de leer documentación, responder preguntas basadas en su contenido, publicar el código en GitHub y demostrar el funcionamiento de la solución mediante un despliegue accesible públicamente.
