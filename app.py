import streamlit as st
from openai import OpenAI
import json

# משיכת המפתח מהכספת
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# --- מנגנון הזיכרון (כמו בצ'אט שלנו) ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # כאן נשמר כל השיח
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.master_insight = "ממתין לנתונים ראשוניים..."
    st.session_state.started = False

with st.sidebar:
    st.title("🚀 DNA Control")
    view_mode = st.radio("תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    if st.button("איפוס שיחה"):
        st.session_state.messages = []
        st.session_state.started = False
        st.rerun()

if view_mode == "צד משתמש":
    st.title("🧠 Collective Mind DNA")

    # שלב הכניסה - פעם אחת בלבד
    if not st.session_state.started:
        user_input = st.text_area("הדבק לינקדין או ספר קצת על עצמך כדי להתחיל:", height=150)
        if st.button("התחל אבחון"):
            if user_input:
                st.session_state.started = True
                # שליחת ההודעה הראשונה ל-AI
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional profiler. Ask one tough Hebrew question based on this: " + user_input}]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    
    # שלב השיחה הרציפה (כמו שאנחנו מדברים עכשיו)
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

        if prompt := st.chat_input("השב כאן..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            # השלב שבו ה-AI מעבד את כל ההיסטוריה ומעדכן את ה-DNA
            sys_prompt = f"""
            You are a Master VC Profiler. Analyze the conversation and:
            1. Update DNA stats (1-100).
            2. Write a 3-sentence insight in Hebrew.
            3. Ask the next challenging Hebrew question.
            
            Return ONLY JSON:
            {{
                "next_question": "string",
                "master_insight": "string",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}}
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                response_format={ "type": "json_object" }
            )
            
            res = json.loads(response.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": res["next_question"]})
            st.session_state.stats = res["stats"]
            st.session_state.master_insight = res["master_insight"]
            st.rerun()

    # מדדי DNA בתחתית המסך
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Vision", f"{st.session_state.stats['Vision']}%")
    c2.metric("Independence", f"{st.session_state.stats['Independence']}%")
    c3.metric("Execution", f"{st.session_state.stats['Execution']}%")

else: # Investor View
    st.title("🕵️ Investor Dashboard")
    st.info(f"**Master Insight:** {st.session_state.master_insight}")
    st.bar_chart(st.session_state.stats)
