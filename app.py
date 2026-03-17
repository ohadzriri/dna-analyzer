import streamlit as st
from openai import OpenAI
import json

# חיבור ל-API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# 1. אתחול משתנים
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "insight": "מנתח נתוני פתיחה...",
        "init": False
    })

# 2. סיידבר - המדדים שלך
with st.sidebar:
    st.title("📊 DNA Dashboard")
    mode = st.radio("מצב תצוגה:", ["צד משתמש", "צד יזם"])
    
    if mode == "צד יזם":
        st.divider()
        st.metric("Vision", f"{st.session_state.stats['Vision']}%")
        st.metric("Independence", f"{st.session_state.stats['Independence']}%")
        st.metric("Execution", f"{st.session_state.stats['Execution']}%")
        st.write(f"**מהימנות:** {st.session_state.conf}%")
        st.info(f"**תובנה:** {st.session_state.insight}")
    
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")

# 3. לוגיקת האפליקציה
if not st.session_state.init:
    st.subheader("ברוך הבא. בוא נתחיל לבנות את ה-DNA המקצועי שלך.")
    txt = st.text_area("הדבק כאן פרופיל לינקדין או רקע מקצועי:", height=200)
    
    if st.button("התחל אבחון"):
        if txt:
            with st.spinner("מנתח..."):
                # הנחיית מערכת מאוזנת וחכמה
                sys_init = "You are a professional Talent Auditor. Analyze the user's background and ask ONE deep, insightful question in Hebrew (1st person) to start uncovering their professional DNA."
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": sys_init}, {"role": "user", "content": txt}]
                )
                ai_msg = res.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                st.session_state.init = True
                st.rerun()

else:
    # הצגת הצ'אט
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("תשובה שלך..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מעדכן פרופיל..."):
            sys_prompt = """
            You are a Talent Auditor. Talk to the user in Hebrew (1st person). 
            Be analytical and professional.
            Return ONLY JSON with:
            {
                "res": "Your response + next question",
                "stats": {"Vision": int, "Independence": int, "Execution": int},
                "conf": int,
                "ins": "Deep analytical insight for the investor"
            }
            """
            
            raw_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(raw_res.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": data['res']})
            st.session_state.stats = data['stats']
            st.session_state.conf = data.get('conf', st.session_state.conf)
            st.session_state.insight = data.get('ins', st.session_state.insight)
            st.rerun()
