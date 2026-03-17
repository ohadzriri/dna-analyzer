import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# 1. אתחול
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "ins": "מנתח נתוני פתיחה...",
        "init": False
    })

# 2. סיידבר
with st.sidebar:
    st.title("⚙️ בקרה")
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

# 3. לוגיקת אפליקציה
if not st.session_state.init:
    txt = st.text_area("הדבק פרופיל לינקדין או רקע מקצועי:", height=200)
    if st.button("התחל אבחון"):
        if txt:
            sys = "אתה פרופילר מקצועי חסר רחמים. ענה רק בעברית, גוף ראשון. שאל שאלה אחת בוטה ומאתגרת על היכולת לספק תוצאות תחת לחץ."
            res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys}, {"role": "user", "content": txt}])
            msg = res.choices[0].message.content
            st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.init = True
            st.rerun()
else:
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("ענה לפרופילר..."):
        st.session_state.messages.append({"role": "user", "content": p})
        # יצירת התגובה ללא בלוק "with" מסובך
        sys = "פרופילר מקצועי חד. עברית בלבד, גוף ראשון. בוטה וישיר. Return JSON: {'res': 'text', 'stats': {}, 'conf': int, 'ins': 'text'}"
        raw = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": sys}] + st.session_state.messages[-10:],
            response_format={"type": "json_object"}
        )
        try:
            d = json.loads(raw.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": d.get('res', 'המשך...')})
            st.session_state.stats = d.get('stats', st.session_state.stats)
            st.session_state.conf = min(100, d.get('conf', st.session_state.conf))
            st.session_state.ins = d.get('ins', st.session_state.ins)
        except:
            st.session_state.messages.append({"role": "assistant", "content": "הבנתי. תן דוגמה מהשטח."})
        st.rerun()
