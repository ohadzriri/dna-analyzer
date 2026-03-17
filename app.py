import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# חיבור ל-OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# 1. אתחול משתני מערכת
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "insight": "מנתח נתוני פתיחה...",
        "init": False
    })

# 2. סיידבר - ניהול תצוגה
with st.sidebar:
    st.title("⚙️ בקרה")
    mode = st.radio("מצב תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    
    if mode == "צד יזם (Investor View)":
        st.divider()
        st.subheader("📊 מדדי DNA")
        st.metric("Vision", f"{st.session_state.stats.get('Vision', 50)}%")
        st.metric("Independence", f"{st.session_state.stats.get('Independence', 50)}%")
        st.metric("Execution", f"{st.session_state.stats.get('Execution', 50)}%")
        st.write(f"**מהימנות:** {st.session_state.conf}%")
        st.progress(st.session_state.conf / 100)
        st.divider()
        st.subheader("תובנה סמויה")
        st.info(st.session_state.insight)
    
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

# 3. מסך ראשי
st.title("🧠 Collective Mind DNA")

# שלב א': הזנת רקע (לינקדין/טקסט)
if not st.session_state.init:
    st.subheader("ברוך הבא. בוא נתחיל לבנות את ה-DNA המקצועי שלך.")
    txt = st.text_area("הדבק כאן פרופיל לינקדין או רקע מקצועי קצר:", height=200)
    
    if st.button("התחל אבחון"):
        if txt:
            with st.spinner("מנתח רקע..."):
                sys_init = "You are a sharp, ruthless Profiler. Respond in Hebrew, 1st person. Be very brief: One short sentence of reflection on their background + one provocative DNA question."
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": sys_init}, {"role": "user", "content": txt}]
                )
                ai_msg = res.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                st.session_state.init = True
                st.rerun()

# שלב ב': צ'אט אבחון זורם
else:
    # הצגת היסטוריית הצ'אט (ללא הרקע הגולמי)
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("ענה לשאלה או שתף מחשבה..."):
        # הצגת הודעת המשתמש
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מעדכן פרופיל..."):
            sys_prompt = """
            You are a sharp Profiler. Talk DIRECTLY to the user in Hebrew (1st person). 
            Style: Sharp, provocative, minimal. 
            Return ONLY JSON with these exact keys:
            {
                "res": "Short insight + next tough question",
                "stats": {"Vision": int, "Independence": int, "Execution": int},
                "conf": int,
                "ins": "Internal analytical insight for the investor"
            }
            """
            
            raw_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
                response_format={"type": "json_object"}
            )
            
            try:
                data = json.loads(raw_res.choices[0].message.content)
                # עדכון הסטייט
                st.session_state.messages.append({"role": "assistant", "content": data.get('res', 'מעניין. תמשיך.')})
                st.session_state.stats = data.get('stats', st.session_state.stats)
                st.session_state.conf = min(100, data.get('conf', st.session_state.conf))
                st.session_state.insight = data.get('ins', st.session_state.insight)
            except:
                st.session_state.messages.append({"role": "assistant", "content": "הבנתי. בוא נצלול עמוק יותר."})
            
            st.rerun()
