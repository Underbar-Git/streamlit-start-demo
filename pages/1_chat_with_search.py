import streamlit as st
from streamlit_chat import message 
from duckduckgo_search import DDGS
import requests


def web_search(q):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(q, max_results=5)]
    return results

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["I'm HugChat, How may I help you?"]

if 'past' not in st.session_state:
    st.session_state['past'] = ['Hi!']
    
# Layout of input/response containers

response_container = st.container()

# User input
## Function for taking user provided prompt as input
def get_text():
    input_text = st.chat_input("질문을 해주시면 됩니다.")
    return input_text
## Applying the user input box
user_input = get_text()

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    response = web_search(prompt)
    
    res = ""
    if response:
        for r in response:
            res += '<a href="' + r['href'] + '" target="_blank">' + r['title'] + '</a>\n\n' + r['body'] + '\n\n\n'
    
    if res == "":
        res = "모르겠는데?"
    return res

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:
        response = generate_response(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i), allow_html=True)