import os

import streamlit as st
from google import genai

MODEL = 'gemini-2.5-flash'

st.set_page_config(page_title='Astrology Chatbot', page_icon='✨', layout='centered')

if 'history' not in st.session_state:
    st.session_state.history = [
        {
            'role': 'assistant',
            'content': 'Hello! I am your astrology guide. Ask me about natal charts, zodiac insights, horoscopes, or cosmic timing.'
        }
    ]

st.title('✨ Astrology Chatbot')
st.write(
    'Ask your astrology questions and receive friendly guidance on zodiac signs, birth charts, planetary influences, and daily horoscopes.'
)

api_key = None
if 'GENAI_API_KEY' in st.secrets:
    api_key = st.secrets['GENAI_API_KEY']
else:
    api_key = os.getenv('GENAI_API_KEY')

if not api_key:
    st.error(
        'No API key found. Set GENAI_API_KEY in Streamlit secrets or as an environment variable.'
    )
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as exc:
    st.error(f'Failed to initialize Google GenAI client: {exc}')
    st.stop()


def extract_response_text(response):
    if hasattr(response, 'text') and response.text:
        return response.text
    if hasattr(response, 'output'):
        output = response.output
        if isinstance(output, (list, tuple)) and output:
            first = output[0]
            if hasattr(first, 'content'):
                return first.content
            if isinstance(first, dict):
                return first.get('content', '')
    if isinstance(response, dict):
        return response.get('text') or response.get('output', [{}])[0].get('content', '')
    return str(response)


def build_prompt(user_question: str) -> str:
    return (
        'You are a warm astrology guide who explains zodiac traits, planetary influences, and horoscope advice in a friendly, modern tone. '
        'Answer the user question clearly and helpfully, using astrology concepts when relevant.'
        f'\n\nUser: {user_question}\nAstrology guide:'
    )

with st.form(key='astrology_form'):
    user_input = st.text_input(
        'Ask about your Sun sign, natal chart, daily horoscope, or relationship astrology',
        key='user_prompt',
    )
    submitted = st.form_submit_button('Send')

if submitted and user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})

    with st.spinner('Consulting the stars...'):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=build_prompt(user_input),
            )
            assistant_text = extract_response_text(response)
        except Exception as exc:
            assistant_text = f'Sorry, I could not get a response from the model: {exc}'

    st.session_state.history.append({'role': 'assistant', 'content': assistant_text})

for entry in st.session_state.history:
    if entry['role'] == 'user':
        st.chat_message('user').write(entry['content'])
    else:
        st.chat_message('assistant').write(entry['content'])

st.markdown(
    '---\n'
    '**Tip:** Store your GENAI_API_KEY in Streamlit secrets or as an environment variable instead of hardcoding it.'
)
