import streamlit as st
from streamlit_chat import message 
from duckduckgo_search import DDGS
from langchain.schema.document import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import requests
GOOGLE_API_KEY = "AIzaSyA10EDo80sAY2XoQsY_KoU_IgbBdcKX5yg"
from langchain_google_genai import ChatGoogleGenerativeAI
from google import generativeai as genai
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

model_name = "jhgan/ko-sbert-nli"
model_kwargs = {'device': 'mps'}
encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
custom_prompt_template = """
{context}
Question: {question}
Helpful Answer:
"""

def web_search(q):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(q, region="ko-ko", max_results=1000)]
    return results

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["안녕? 나는 잼민이야. 뭘 도와줄까?"]

if 'past' not in st.session_state:
    st.session_state['past'] = ['똑똑!']
    
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
    
    documents = []
    for r in response:
        document = Document(
            page_content=r['title'] + '\n' + r['body'],
            metadata={'source': r['href']}
        )
        documents.append(document)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    # print(texts)
    
    store = FAISS.from_documents(texts, embeddings)
    retriever = store.as_retriever()
    
    safety_settings_NONE=[
        { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    LLM = ChatGoogleGenerativeAI(
        model="gemini-pro", 
        temperature=0,
        max_output_tokens=2048,
        google_api_key=GOOGLE_API_KEY)
    LLM.client = genai.GenerativeModel(
        model_name="gemini-pro", 
        safety_settings=safety_settings_NONE
    )
    print('LLM?', LLM)
    custom_prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    
    chain = RetrievalQA.from_chain_type(
        llm=LLM,
        chain_type="stuff",
        retriever=retriever,
        verbose=True,
        return_source_documents=True,
        chain_type_kwargs={"prompt": custom_prompt},
    )
    # print('chain', chain)
    q = {'query': prompt}
    results = chain(q)
    print('result :::', results)
    res = results['result']
    # res = ""
    # if response:
    #     for r in response:
    #         res += '<a href="' + r['href'] + '" target="_blank">' + r['title'] + '</a>\n\n' + r['body'] + '\n\n\n'
    
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