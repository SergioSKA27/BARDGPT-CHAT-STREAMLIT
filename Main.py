import streamlit as st
import pandas as pd
import google.generativeai as genai


from PIL import Image
#Je t'aime plus que les mots,
#Plus que les sentiments,
#Plus que la vie elle-même

st.set_page_config(
    page_title="Google AI Chat",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)
# Path: Main.py
#Author: Sergio Demis Lopez Martinez
st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20">
, Streamlit and Python''', unsafe_allow_html=True)
st.caption("By Sergio Demis Lopez Martinez")
st.divider()


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

cols=st.columns(4)

with cols[0]:
    image_atachment = st.checkbox("Adjuntar imagen")
with cols[1]:
    txt_atachment = st.checkbox("Adjuntar texto")
with cols[2]:
    csv_excel_atachment = st.checkbox("Adjuntar CSV o Excel")


if image_atachment:
    image = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
else:
    image = None



if txt_atachment:
    txtattachment = st.file_uploader("Sube tu archivo de texto", type=['txt'])
else:
    txtattachment = None

if csv_excel_atachment:
    csvexcelattachment = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])
else:
    csvexcelattachment = None
prompt = st.chat_input("Escribe tu mensaje")

if prompt:
    txt = ''
    if txtattachment:
        txt = txtattachment.getvalue().decode("utf-8")
        txt = '   Archivo de texto: \n' + txt

    if csvexcelattachment:
        try:
            df = pd.read_csv(csvexcelattachment)
        except:
            df = pd.read_excel(csvexcelattachment)
        txt = '   Dataframe: \n' + str(df)

    if len(txt) > 5000:
        txt = txt[:5000] + '...'
    if image:
        prmt  = {'role': 'user', 'parts':[prompt+txt, Image.open(image)]}
    else:
        prmt  = {'role': 'user', 'parts':[prompt+txt]}

    append_message(prmt)

    with st.spinner('Espera un momento, estoy pensando...'):
        if len(prmt['parts']) > 1:
            response = vision.generate_content(prmt['parts'],stream=True,safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
    ]
)
            response.resolve()
        else:
            response = st.session_state.chat.send_message(prmt['parts'][0])

        append_message({'role': 'model', 'parts':response.text})
        st.rerun()



#st.session_state.chat_session
