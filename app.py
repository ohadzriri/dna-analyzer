import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# אתחול סטייט
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 20, "Independence": 20, "Execution": 20}
    st.session_state.progress = 5  # מד התקדמות כללי באחוזים
    st.session_state.phase = "DNA_Discovery" # השלב הנוכחי
    st.session_state.started = False

st.title("🧠 Collective Mind DNA")

# סרגל התקדמות בראש הדף
st.write(f"**שלב נוכחי:** {st.session_state.phase.replace('_', ' ')}")
st.progress(st.session_state.progress / 100)

if not st.session_state.started:
    user_input = st.text_area("הדבק לינקדין או ספר קצת על עצמך כדי להתחיל:", height=150)
    if st.button("התחל אבחון"):
        if user_input:
            st.session_state.started = True
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a world-class profiler. Start a deep DNA diagnosis in Hebrew based on the input."}] + [{"role": "user", "content": user_input}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

else:
    # הצגת הצ'אט
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    # אם הגענו ל-100%, לא מציגים יותר תיבת טקסט
    if st.session_state.progress < 100:
        if prompt := st.chat_input("השב כאן..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)

            with st.spinner("מנתח את ה-DNA..."):
                sys_prompt = f"""
                You are a Master Profiler. Current Phase: {st.session_state.phase}.
                Your goal is to reach 100% confidence in the user's profile.
                
                Rules:
                1. If Phase is 'DNA_Discovery', ask deep, abstract, or psychological questions.
                2. If stats for Vision/Independence are > 60, switch Phase to 'Professional_Execution' (Practical/Business questions).
                3. Each response must be: Brief validation + ONE sharp question.
                4. Increase 'progress_increment' (5-15) based on how detailed the user's answer was.
                
                Return ONLY JSON:
                {{
                    "next_question": "Hebrew text",
                    "new_phase": "DNA_Discovery" or "Professional_Execution" or "Complete",
                    "progress_increment": int,
                    "stats": {{"Vision": int, "Independence": int, "Execution": int}},
                    "master_insight": "Critical analysis for investor only"
                }}
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
                    response_format={ "type": "json_object" }
                )
                
                res = json.loads(response.choices[0].message.content)
                
                # עדכון סטייט
                st.session_state.messages.append({"role": "assistant", "content": res["next_question"]})
                st.session_state.stats = res["stats"]
                st.session_state.phase = res["new_phase"]
                st.session_state.progress = min(100, st.session_state.progress + res["progress_increment"])
                st.session_state.master_insight = res["master_insight"]
                
                if st.session_state.progress >= 100:
                    st.session_state.phase = "Complete"
                
                st.rerun()
    else:
        st.success("✅ האבחון הושלם! הנתונים נשמרו במערכת.")
        st.balloons()
        with st.expander("ראה את סיכום הפרופיל שלך"):
            st.write(st.session_state.master_insight)

# מדדים בתחתית
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Vision", f"{st.session_state.stats['Vision']}%")
c2.metric("Independence", f"{st.session_state.stats['Independence']}%")
c3.metric("Execution", f"{st.session_state.stats['Execution']}%")
