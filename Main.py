import streamlit as st
import requests
import google.generativeai as genai
from IPython.display import Markdown
import textwrap
import re

#Je t'aime plus que les mots,
#Plus que les sentiments,
#Plus que la vie elle-même

st.set_page_config(
    page_title="Google AI Chat",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png"
)
# Path: Main.py
#Author: Sergio Demis Lopez Martinez
st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
, Streamlit and Python''', unsafe_allow_html=True)
st.caption("By Sergio Demis Lopez Martinez")
st.divider()

def extraer_contenido(texto):
    # Expresión regular para extraer las llaves "parts" y "role" con su contenido
    expresion_regular = r'"parts":\s*{([^}]*)}.*"role":\s*"([^"]*)"'

    # Buscar coincidencias en el texto
    coincidencias = re.search(expresion_regular, texto)

    # Extraer el contenido de las llaves "parts" y "role"
    if coincidencias:
        contenido_parts = coincidencias.group(1).strip()
        role = coincidencias.group(2).strip()
        return contenido_parts, role
    else:
        return None, None

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def append_message(message):
    st.session_state.chat_session.append({'user': message})
    return

@st.cache_resource
def load_model():
    model = genai.GenerativeModel('gemini-pro')
    return model

@st.cache_resource
def load_modelvision():
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = load_model()

vision = load_modelvision()

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

#st.session_state.chat_session

#------------------------------------------------------------
#CHAT

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'welcome' not in st.session_state:
    welcome  = model.generate_content('Da un saludo de bienvenida al usuario y sugiere que puede hacer')
    welcome.resolve()
    st.session_state.welcome = welcome

    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)
else:
    with st.chat_message('ai'):
        st.write(st.session_state.welcome.text)

if len(st.session_state.chat_session) > 0:
    count = 0
    for message in st.session_state.chat_session:

        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])
                if len(message['user']['parts']) > 1:
                    st.image(message['user']['parts'][1], width=200)
        count += 1



#st.session_state.chat.history


image_atachment = st.checkbox("Adjuntar imagen")
if image_atachment:
    image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
else:
    image = None
prompt = st.chat_input("Escribe tu mensaje")


if prompt:
    if image:
        prmt  = {'role': 'user', 'parts':[prompt, image.read()]}
    else:
        prmt  = {'role': 'user', 'parts':[prompt]}

    append_message(prmt)

    with st.spinner('Espera un momento, estoy pensando...'):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'],stream=True)
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])
        append_message({'role': 'model', 'parts':response.text})
        st.experimental_rerun()



#st.session_state.chat_session
