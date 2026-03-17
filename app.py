import streamlit as st
from openai import OpenAI
import json

# חיבור ל-OpenAI דרך Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA | Live Tracker")

# 1. אתחול Session State (חייב להיות בתחילת הקוד)
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.confidence = 10 
    st.session_state.master_insight = "המערכת בתהליך למידה ראשוני..."
    st.session_state.initialized = False

st.title("🧠 Collective Mind DNA")
st.subheader("ניטור יכולות ופרופיל אישיותי בזמן אמת")

# 2. תצוגת רמת המהימנות בראש הדף (תמיד גלוי)
st.write(f"**רמת מהימנות האבחון (Confidence Level):** {st.session_state.confidence}%")
st.progress(st.session_state.confidence / 100)

st.divider()

# 3. אזור הקלט - משתנה לפי מצב האתחול
if not st.session_state.initialized:
    st.info("👋 ברוך הבא! כדי להתחיל, הדבק לינק ללינקדין או כתוב כמה מילים על הניסיון שלך:")
    initial_input = st.text_area("רקע מקצועי / לינקדין:", height=150, placeholder="למשל: יזם סדרתי בתחום הפינטק, ניהלתי צוותים של...")
    if st.button("התחל אבחון DNA"):
        if initial_input:
            with st.spinner("מנתח רקע ראשוני..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analyze the user's professional background in Hebrew. Be sharp. Ask the first deep DNA question."}] + [{"role": "user", "content": initial_input}]
                )
                st.session_state.messages.append({"role": "user", "content": f"רקע ראשוני: {initial_input}"})
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.session_state.initialized = True
                st.rerun()
else:
    # הצגת הצ'אט (רק הודעות שהן לא ה"רקע הראשוני" הגולמי)
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע ראשוני:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("שתף מחשבה, דווח על ביצוע משימה או התייעץ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מעדכן DNA..."):
            sys_prompt = f"""
            You are a Continuous Professional Profiler. 
            Update the user's DNA profile. Current Stats: {st.session_state.stats}
            
            Return ONLY JSON:
            {{
                "response": "Hebrew text",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}},
                "confidence_level": int,
                "master_insight": "Deep analysis for the investor (Hebrew)"
            }}
            """
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
                response_format={ "type": "json_object" }
            )
            res = json.loads(response.choices[0].message.content)
            st.session_state.messages.append({"role": "assistant", "content": res["response"]})
            st.session_state.stats = res["stats"]
            st.session_state.confidence = min(100, res["confidence_level"])
            st.session_state.master_insight = res["master_insight"]
            st.rerun()

# 4. לוח המדדים וה-Investor View (תמיד גלוי בתחתית)
st.divider()
st.subheader("📊 DNA Snapshot & Analytics")

col1, col2, col3 = st.columns(3)
col1.metric("Vision", f"{st.session_state.stats['Vision']}%")
col2.metric("Independence", f"{st.session_state.stats['Independence']}%")
col3.metric("Execution", f"{st.session_state.stats['Execution']}%")

# אזור היזם / משקיע (Investor View)
with st.expander("👁️ מבט יזם (Investor View) - ניתוח עומק סמוי", expanded=True):
    st.warning(f"**תובנת מערכת:** {st.session_state.master_insight}")
    st.write("התפלגות יכולות נוכחית:")
    st.bar_chart(st.session_state.stats)

# כפתור איפוס בסיידבר
if st.sidebar.button("איפוס נתונים והתחלה מחדש"):
    st.session_state.clear()
    st.rerun()
