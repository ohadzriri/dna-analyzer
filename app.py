import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# אתחול נקי
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "ins": "מנתח...",
        "init": False
    })

with st.sidebar:
    mode = st.radio("תצוגה:", ["משתמש", "יזם"])
    if mode == "יזם":
        st.write(f"**מהימנות:** {st.session_state.conf}%")
        for k, v in st.session_state.stats.items():
            st.metric(k, f"{v}%")
        st.info(st.session_state.ins)
    if st.button("איפוס"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")

# הנחיית מערכת מאוזנת (כמו שעבד אתמול)
SYS_PROMPT = """
You are an expert Talent Auditor and Profiler. 
Your goal is to identify the 'Professional DNA' of the user.
1. Be analytical, insightful, and slightly challenging (but professional).
2. Speak Hebrew, 1st person.
3. Use the user's background to ask deep questions about their decision-making and capabilities.
4. Always return a JSON object with:
   {"res": "Your response to the user", "stats": {"Vision": 1-100, "Independence": 1-100, "Execution": 1-100}, "conf": 1-100, "ins": "Internal insight"}
"""

if not st.session_state.init:
    txt = st.text_area("הדבק רקע מקצועי/לינקדין:", height=200)
    if st.button("התחל אבחון"):
        if txt:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": txt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
            st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
            st.session_state.messages.append({"role": "assistant", "content": data['res']})
            st.session_state.stats = data['stats']
            st.session_state.ins = data['ins']
            st.session_state.init = True
            st.rerun()
else:
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("תשובה שלך..."):
        st.session_state.messages.append({"role": "user", "content": p})
        raw = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYS_PROMPT}] + st.session_state.messages[-10:],
            response_format={"type": "json_object"}
        )
        data = json.loads(raw.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": data['res']})
        st.session_state.stats = data['stats']
        st.session_state.conf = data['conf']
        st.session_state.ins = data['ins']
        st.rerun()
