import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(layout="wide", page_title="Collective Mind DNA")

if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "insight": "מנתח נתוני פתיחה...",
        "init": False
    })

with st.sidebar:
    mode = st.radio("תצוגה:", ["משתמש", "יזם"])
    if mode == "יזם":
        st.write(f"**מהימנות:** {st.session_state.conf}%")
        for k, v in st.session_state.stats.items():
            st.metric(k, f"{v}%")
        st.info(st.session_state.insight)
    if st.button("איפוס"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")

if not st.session_state.init:
    txt = st.text_area("הדבק לינקדין או רקע מקצועי:", height=150)
    if st.button("התחל"):
        if txt:
            # כאן התיקון המרכזי ב-Prompt
            sys = "You are a ruthless, sharp Profiler. Respond in Hebrew, 1st person. Do NOT be 'nice'. Analyze the input and ask ONE provocative question that tests their actual capability, not their CV."
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys}] + [{"role": "user", "content": txt}]
            )
            st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.session_state.init = True
            st.rerun()
else:
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("שתף מחשבה או משימה..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)

        # הנחיה חדה גם לשיחה השוטפת
        sys = "You are a professional Profiler. 1st person Hebrew. Be sharp and direct. No corporate fluff. Return JSON: {'res': 'Short insight + Provocative question', 'stats': {'Vision': int, 'Independence': int, 'Execution': int}, 'conf': int, 'ins': 'Raw analytical insight'}"
        
        raw = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys}] + st.session_state.messages[-10:],
            response_format={"type": "json_object"}
        )
        
        try:
            data = json.loads(raw.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": data.get('res', 'ממתין לתשובה שלך.')})
            st.session_state.stats = data.get('stats', st.session_state.stats)
            st.session_state.conf = min(100, data.get('conf', st.session_state.conf))
            st.session_state.insight = data.get('ins', st.session_state.insight)
        except:
            st.session_state.messages.append({"role": "assistant", "content": "מעניין. תרחיב על זה?"})
        st.rerun()
