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
    st.session_state.master_insight = "המערכת לומדת את הרקע שלך..."
    st.session_state.initialized = False

# --- סיידבר (צד שמאל למעלה) ---
with st.sidebar:
    st.header("👁️ מבט יזם (Investor View)")
    st.write(f"**מהימנות אבחון:** {st.session_state.confidence}%")
    st.progress(st.session_state.confidence / 100)
    
    st.divider()
    
    # הצגת האחוזים בלבד כפי שביקשת
    st.metric("Vision", f"{st.session_state.stats['Vision']}%")
    st.metric("Independence", f"{st.session_state.stats['Independence']}%")
    st.metric("Execution", f"{st.session_state.stats['Execution']}%")
    
    st.divider()
    
    st.subheader("תובנת מערכת סמויה")
    st.info(st.session_state.master_insight)
    
    if st.button("איפוס נתונים"):
        st.session_state.clear()
        st.rerun()

# --- מרכז המסך (צד משתמש) ---
st.title("🧠 Collective Mind DNA")

if not st.session_state.initialized:
    st.subheader("ברוך הבא")
    initial_input = st.text_area("הדבק לינק ללינקדין או כתוב כמה מילים על הניסיון שלך כדי להתחיל:", height=150)
    if st.button("התחל אבחון DNA"):
        if initial_input:
            with st.spinner("מנתח רקע..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analyze user background in Hebrew. Provide a sharp summary and ask the first DNA question."}] + [{"role": "user", "content": initial_input}]
                )
                st.session_state.messages.append({"role": "user", "content": f"רקע ראשוני: {initial_input}"})
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.session_state.initialized = True
                st.rerun()
else:
    # הצגת הצ'אט
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע ראשוני:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("שתף מחשבה או עדכן משימה..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("מעדכן DNA..."):
            sys_prompt = f"""
            You are a Continuous Profiler. Update DNA stats.
            Current Stats: {st.session_state.stats}
            Return ONLY JSON:
            {{
                "response": "Hebrew text",
                "stats": {{"Vision": int, "Independence": int, "Execution": int}},
                "confidence_level": int,
                "master_insight": "Deep analysis in Hebrew"
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
# כפתור איפוס בסיידבר
if st.sidebar.button("איפוס נתונים והתחלה מחדש"):
    st.session_state.clear()
    st.rerun()
