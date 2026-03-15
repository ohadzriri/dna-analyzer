import streamlit as st
from openai import OpenAI
import json

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.master_insight = "טרם גובש ניתוח מעמיק. המערכת ממתינה לתשובות נוספות."
    st.session_state.linkedin = ""

with st.sidebar:
    st.title("🚀 Control Panel")
    api_key = st.text_input("OpenAI API Key", type="password")
    view_mode = st.radio("תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

if view_mode == "צד משתמש":
    st.title("🧠 Collective Mind DNA")

    if not st.session_state.linkedin:
        li_input = st.text_area("הדבק פרופיל לינקדין להתחלה:", height=150)
        if st.button("התחל אבחון"):
            if li_input and api_key:
                st.session_state.linkedin = li_input
                client = OpenAI(api_key=api_key)
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a professional profiler. Based on this LinkedIn, ask ONE tough Hebrew question about their biggest professional challenge: " + li_input}]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("תשובתך..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            client = OpenAI(api_key=api_key)

            sys_prompt = f"""
            You are a Master VC Profiler.
            Your goal is to maintain a SINGLE, evolving DNA analysis of the user.

            Current Insight: {st.session_state.master_insight}
            Current Stats: {st.session_state.stats}

            SCORING RULES:
            - Scale: 0-100. (e.g., 85, 40, 92). NO single digits.
            - Update stats based on total consistency.
            - If the user contradicts themselves, reflect it in the insight and lower the scores.

            Return ONLY JSON:
            {{
                "user_reply": "Next deep question in Hebrew",
                "master_insight": "Update the full DNA analysis here in Hebrew (one cohesive paragraph).",
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
    st.title("🕵️ Investor Insights Dashboard")
    st.subheader("ניתוח DNA חי ומעודכן")
    st.info(st.session_state.master_insight)

    st.subheader("מדדים כמותיים")
    st.write(st.session_state.stats)