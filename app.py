import streamlit as st
from openai import OpenAI
import json

# משיכת המפתח מהכספת
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

if "messages" not in st.session_state:
    st.session_state.messages = []
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

    if not st.session_state.started:
        user_input = st.text_area("הדבק לינקדין או ספר קצת על עצמך כדי להתחיל:", height=150)
        if st.button("התחל אבחון"):
            if user_input:
                st.session_state.started = True
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a world-class professional profiler. Based on the input, ask one sharp, intriguing Hebrew question to start a DNA diagnosis."}] + [{"role": "user", "content": user_input}]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    
    else:
        # הצגת השיחה
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

        if prompt := st.chat_input("השב כאן..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.spinner("מנתח..."):
                sys_prompt = f"""
                You are a Master VC Profiler. 
                Your task is to respond to the user in a professional, sophisticated manner.
                
                1. Start with a brief, high-level acknowledgment of their point (Professional validation). 
                2. Transition smoothly to the next deep, challenging question.
                3. Keep the public response (next_question) smart but don't reveal the raw scores.
                
                The 'master_insight' is for the INVESTOR ONLY. Be critical and blunt there.
                Update the stats based on the entire conversation history.
                
                Return ONLY JSON:
                {{
                    "next_question": "A 2-3 sentence Hebrew response: Brief professional reflection + the next sharp question",
                    "master_insight": "3-4 sentences of RAW, CRITICAL professional analysis for the investor only (Hebrew)",
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

    # מדדי DNA בתחתית (למשתמש)
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Vision", f"{st.session_state.stats['Vision']}%")
    c2.metric("Independence", f"{st.session_state.stats['Independence']}%")
    c3.metric("Execution", f"{st.session_state.stats['Execution']}%")

else: # Investor View
    st.title("🕵️ Investor Dashboard")
    st.subheader("ניתוח פסיכולוגי-מקצועי (חשוף רק לך):")
    st.warning(st.session_state.master_insight)
    st.write("---")
    st.subheader("דירוג DNA נוכחי:")
    st.bar_chart(st.session_state.stats)
