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
    mode = st.radio("מצב תצוגה:", ["משתמש", "יזם"])
    if mode == "יזם":
        st.write(f"**מהימנות:** {st.session_state.conf}%")
        for k, v in st.session_state.stats.items():
            st.metric(k, f"{v}%")
        st.info(st.session_state.insight)
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")

if not st.session_state.init:
    txt = st.text_area("הדבק לינקדין או רקע מקצועי:", height=200)
    if st.button("התחל אבחון"):
        if txt:
            # שינוי הנחיית המערכת לחדה ותוקפנית יותר
            sys_init = "You are a world-class professional Profiler. Hebrew, 1st person. DO NOT be philosophical or 'nice'. Look for contradictions in their CV. Ask ONE blunt, professional question about their ability to scale or lead under pressure."
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_init}, {"role": "user", "content": txt}]
            )
            st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.session_state.init = True
            st.rerun()
else:
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]): st.write(m["content"])

    if p := st.chat_input("ענה למקודן..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.write(p)

        # הנחיה קשיחה ל-JSON עם דרישה לתוכן מקצועי בלבד
        sys_prompt = """
        You are a ruthless Profiler. Hebrew, 1st person. 
        Focus ONLY on professional capability, risk-taking, and leadership. 
        NO 'soft' or 'spiritual' questions. 
        Return JSON: {"res": "Short reflection + Tough professional question", "stats": {"Vision": int, "Independence": int, "Execution": int}, "conf": int, "ins": "Raw analytical insight"}
        """
        raw = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
            response_format={"type": "json_object"}
        )
        try:
            d = json.loads(raw.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": d.get('res', 'מעניין. תמשיך.')})
            st.session_state.stats = d.get('stats', st.session_state.stats)
            st.session_state.conf = min(100, d.get('conf', st.session_state.conf))
            st.session_state.insight = d.get('ins', st.session_state.insight)
        except:
            st.session_state.messages.append({"role": "assistant", "content": "הבנתי. תן לי דוגמה ספציפית מהשטח."})
        st.rerun()
