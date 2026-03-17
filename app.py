import streamlit as st
from openai import OpenAI
import json

# חיבור ל-OpenAI דרך Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# 1. אתחול Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.confidence = 10 
    st.session_state.master_insight = "המערכת לומדת אותך..."
    st.session_state.initialized = False

# --- סיידבר: בחירת מצב תצוגה ---
with st.sidebar:
    mode = st.radio("בחר מצב תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    st.divider()
    if mode == "צד יזם (Investor View)":
        st.subheader("📊 מדדי DNA")
        # שימוש ב-.get() למניעת קריסות
        v = st.session_state.stats.get('Vision', 50)
        i = st.session_state.stats.get('Independence', 50)
        e = st.session_state.stats.get('Execution', 50)
        
        st.metric("Vision", f"{v}%")
        st.metric("Independence", f"{i}%")
        st.metric("Execution", f"{e}%")
        st.write(f"**מהימנות:** {st.session_state.confidence}%")
        st.divider()
        st.subheader("תובנה סמויה")
        st.info(st.session_state.master_insight)
    
    if st.button("איפוס נתונים"):
        st.session_state.clear()
        st.rerun()

# --- מרכז המסך ---
st.title("🧠 Collective Mind DNA")

if not st.session_state.initialized:
    initial_input = st.text_area("הדבק לינקדין או ספר על עצמך בקצרה:", height=150)
    if st.button("התחל אבחון"):
        if initial_input:
            with st.spinner("מתחבר..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a sharp Profiler. Respond in Hebrew. Talk DIRECTLY to the user (1st person). Be very brief: One short sentence of reflection + one killer DNA question."}] + [{"role": "user", "content": initial_input}]
                )
                st.session_state.messages.append({"role": "user", "content": f"רקע: {initial_input}"})
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.session_state.initialized = True
                st.rerun()
else:
    # הצגת הצ'אט
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("שתף מחשבה או עדכן משימה..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מנתח..."):
            sys_prompt = "You are a sharp Profiler. Talk DIRECTLY to the user in Hebrew (1st person). Style: Sharp, direct, minimal. Return ONLY JSON with keys: 'response', 'stats', 'confidence_level', 'master_insight'."
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
                response_format={ "type": "json_object" }
            )
            
            try:
                # פירוק ה-JSON בזהירות רבה
                raw_res = json.loads(response.choices[0].message.content)
                
                # עדכון הנתונים שלב אחר שלב
                ai_text = raw_res.get("response", "הבנתי. בוא נמשיך.")
                new_stats = raw_res.get("stats", st.session_state.stats)
                new_
