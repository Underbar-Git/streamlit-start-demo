import streamlit as st
import pandas as pd
import requests

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
    
st.write('''
# Streamlit Start Demo
Hello World!
''')

res = requests.get('https://api.open-meteo.com/v1/forecast?latitude=37.566&longitude=126.9784&hourly=temperature_2m&past_days=2&forecast_days=3')
data = res.json()

df = pd.DataFrame(data["hourly"])
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)

st.dataframe(df)

redirect_button("https://toss.me/underbars","후원 감사합니다 🩵")
