import streamlit as st
from openai import OpenAI
import json

# עיצוב CSS מינימלי להבטחת קריאות (טקסט לבן במדדים)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    </style>
    """, unsafe_allow_html=True)

# בדיקת מפתח
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("שגיאה: המפתח הסודי לא הוגדר ב-Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# אתחול זיכרון
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
    
    if not st.session_state.linkedin:
        st.info("ברוכים הבאים לאבחון ה-DNA המקצועי. בואו נתחיל.")
        li_input = st.text_area("הדבק פרופיל לינקדין (או תיאור קצר עליך) להתחלה:", height=150)
        if st.button("התחל אבחון"):
            if li_input:
                st.session_state.linkedin = li_input
                # שאלה ראשונה מבוססת רקע
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional profiler. Based on this LinkedIn/Background, ask ONE tough Hebrew question about their professional challenge. Be direct and insightful: " + li_input}]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    else:
        # תצוגת הצ'אט
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("תשובתך..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # לוגיקת הניתוח המקורית
            sys_prompt = f"""
            You are a Master VC Profiler. Maintain a SINGLE evolving DNA analysis in Hebrew.
            Current Stats: {st.session_state.stats}
            Current Insight: {st.session_state.master_insight}
            
            Return ONLY JSON:
            {{
                "user_reply": "Hebrew follow-up question or dilemma",
                "master_insight": "Updated cohesive paragraph analysis in Hebrew (max 4-5 sentences)",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}}
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                response_format={ "type": "json_object" }
            )
            
            res_data = json.loads(response.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": res_data["user_reply"]})
            st.session_state.stats = res_data["stats"]
            st.session_state.master_insight = res_data["master_insight"]
            st.rerun()

    # מדדים בתחתית
    st.divider()
    cols = st.columns(3)
    cols[0].metric("Vision", f"{st.session_state.stats['Vision']}%")
    cols[1].metric("Independence", f"{st.session_state.stats['Independence']}%")
    cols[2].metric("Execution", f"{st.session_state.stats['Execution']}%")

else: # Investor View
    st.title("🕵️ Investor Dashboard")
    st.subheader(f"ניתוח DNA עבור המועמד")
    st.info(st.session_state.master_insight)
    st.write("---")
    st.subheader("מדדים כמותיים")
    st.json(st.session_state.stats)
