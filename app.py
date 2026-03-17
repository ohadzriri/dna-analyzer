import streamlit as st
from openai import OpenAI
import json

# חיבור ל-OpenAI דרך Secrets של Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA | Live Tracker")

# אתחול Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.confidence = 10 
    st.session_state.master_insight = "המערכת בתהליך למידה של ה-DNA שלך..."
    st.session_state.initialized = False

st.title("🧠 Collective Mind DNA")
st.subheader("ניטור יכולות ופרופיל אישיותי בזמן אמת")

# תצוגת רמת המהימנות של האבחון בראש הדף
st.write(f"**רמת מהימנות האבחון (Confidence Level):** {st.session_state.confidence}%")
st.progress(st.session_state.confidence / 100)

# שלב 1: הזנת רקע ראשוני (לינקדין / אודות)
if not st.session_state.initialized:
    st.info("ברוך הבא! כדי להתחיל לבנות את ה-DNA שלך, הדבק כאן לינק לפרופיל לינקדין או כתוב כמה מילים על הניסיון המקצועי שלך:")
    initial_input = st.text_area("רקע מקצועי / לינקדין:", height=150)
    if st.button("התחל אבחון DNA"):
        if initial_input:
            with st.spinner("מנתח רקע ראשוני..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analyze the user's professional background in Hebrew. Provide a 2-sentence summary and ask the first deep question to start the tracking process."}] + [{"role": "user", "content": initial_input}]
                )
                st.session_state.messages.append({"role": "user", "content": f"רקע ראשוני: {initial_input}"})
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.session_state.initialized = True
                st.rerun()

# שלב 2: הצ'אט והניטור היומיומי (מוצג רק אחרי האתחול)
else:
    for m in st.session_state.messages:
        # לא מציגים למשתמש את ה"רקע הראשוני" הגולמי בבועות הצ'אט כדי לשמור על נקיון
        if not m["content"].startswith("רקע ראשוני:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("שתף מחשבה, דווח על ביצוע משימה או התייעץ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מעדכן את ה-DNA..."):
            sys_prompt = f"""
            You are a Continuous Professional Profiler. 
            Update the user's DNA profile based on the interaction.
            Current Stats: {st.session_state.stats}
            
            Return ONLY JSON:
            {{
                "response": "Hebrew text (insight + next question)",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}},
                "confidence_level": int,
                "master_insight": "Deep analysis for the investor"
            }}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-15:],
                response_format={ "type": "json_object" }
            )
            
            res = json.loads(response.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": res["response"]})
            st.session_state.stats = res["stats"]
            st.session_state.confidence = min(100, res["confidence_level"])
            st.session_state.master_insight = res["master_insight"]
            st.rerun()

# לוח מדדים תחתון (
