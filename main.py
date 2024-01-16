import streamlit as st
from rembg import remove 
from duckduckgo_search import DDGS
import requests
from PIL import Image


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div.embeddedAppMetaInfoBar_container__DxxL1 {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

def redirect_button(url: str, text: str= None, color="#FD504D"):
    st.markdown(
    f"""
    <a href="{url}" target="_blank">
        <div style="
            display: inline-block;
            padding: 0.5em 1em;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 3px;
            text-decoration: none;">
            {text}
        </div>
    </a>
    """,
    unsafe_allow_html=True
    )
    
def get_images(keyword, count=3):
    res = []
    with DDGS() as ddgs:
        keywords = keyword
        ddgs_images_gen = ddgs.images(
            keywords,
            region="wt-wt",
            safesearch="off",
            size=None,
            color=None,
            type_image=None,
            layout=None,
            license_image=None,
            max_results=count,
        )
        for r in ddgs_images_gen:
            res.append(r)
    return res

st.write('''
# Streamlit Demo
검색어를 통해 이미지를 찾고, 이미지에 배경을 지워보자. 
''')

search_word = st.text_input('검색어를 입력하세요.', 'IU')
count = st.selectbox(
    '몇개의 결과를 보실래요?',
    (1, 3, 5))
if search_word:
    col1, col2 = st.columns(2)
    find_images = get_images(search_word, count)
    for find in find_images:
        with col1:
            st.image(find['image'], caption=f'출처 : {find["title"]}')
        
        with col2:
            # 이미지를 다운로드합니다.
            response = requests.get(find['image'], stream=True)

            # 이미지를 Pillow Image로 로드합니다.
            try:
                image = Image.open(response.raw)
                rembg_image = remove(image)
                st.image(rembg_image, caption='Remove Background')
            except:
                st.write('Oooops. ')

redirect_button("https://toss.me/underbars","클릭하여 후원 감사합니다 🩵")
