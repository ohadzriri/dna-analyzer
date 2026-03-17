import streamlit as st
from openai import OpenAI
import json

# פקודה קריטית: מושך את המפתח מהכספת שהגדרת עכשיו
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("שגיאה: המפתח הסודי לא הוגדר ב-Secrets של Streamlit")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# אתחול זיכרון המערכת
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.master_insight = "מנתח נתונים ראשוניים..."
    st.session_state.linkedin = ""

with st.sidebar:
    st.title("🚀 DNA Control")
    view_mode = st.radio("תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

if view_mode == "צד משתמש":
    st.title("🧠 Collective Mind DNA")
    st.info("ברוכים הבאים לאבחון ה-DNA המקצועי. בואו נתחיל.")

    if not st.session_state.linkedin:
        li_input = st.text_area("הדבק פרופיל לינקדין (או תיאור קצר עליך) להתחלה:", height=150)
        if st.button("התחל אבחון"):
            if li_input:
                st.session_state.linkedin = li_input
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional profiler. Based on this LinkedIn, ask ONE tough Hebrew question about their professional challenge: " + li_input}]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("תשובתך..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            sys_prompt = f"""
            You are a Master VC Profiler. Maintain a SINGLE evolving DNA analysis in Hebrew.
            Current Stats: {st.session_state.stats}
            Current Insight: {st.session_state.master_insight}
            
            Return ONLY JSON:
            {{
                "user_reply": "Hebrew follow-up question",
                "master_insight": "Updated cohesive paragraph analysis in Hebrew (max 4-5 sentences)",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}}
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                response_format={ "type": "json_object" }
            )
            
            res = json.loads(response.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": res["user_reply"]})
            st.session_state.stats = res["stats"]
            st.session_state.master_insight = res["master_insight"]
            st.rerun()

    st.divider()
    cols = st.columns(3)
    cols[0].metric("Vision", f"{st.session_state.stats['Vision']}%")
    cols[1].metric("Independence", f"{st.session_state.stats['Independence']}%")
    cols[2].metric("Execution", f"{st.session_state.stats['Execution']}%")

else: # Investor View
    st.title("🕵️ Investor Dashboard")
    st.subheader(f"ניתוח DNA עבור: {st.session_state.linkedin[:50]}...")
    st.info(st.session_state.master_insight)
    st.write("---")
    st.subheader("מדדים כמותיים")
    st.json(st.session_state.stats)
