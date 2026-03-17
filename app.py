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

st.title("🧠 Collective Mind DNA")
st.subheader("ניטור יכולות ופרופיל אישיותי בזמן אמת")

# תצוגת רמת המהימנות של האבחון בראש הדף
st.write(f"**רמת מהימנות האבחון (Confidence Level):** {st.session_state.confidence}%")
st.progress(st.session_state.confidence / 100)

# הצגת היסטוריית הצ'אט
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# תיבת קלט קבועה - המשתמש יכול להיכנס כל יום ולעדכן
if prompt := st.chat_input("שתף מחשבה, דווח על ביצוע משימה או התייעץ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("מעבד את הנתונים לתוך ה-DNA שלך..."):
        sys_prompt = f"""
        You are a Continuous Professional Profiler. 
        Your goal is to build a dynamic DNA profile of the user based on interactions.
        
        Current Stats: {st.session_state.stats}
        Current Confidence: {st.session_state.confidence}%
        
        Your task:
        1. Analyze the input.
        2. Update DNA stats (0-100).
        3. Respond in Hebrew: A brief, professional validation + one challenging follow-up.
        4. Increment 'confidence_level' (max 100) by 3-8 points.
        
        Return ONLY JSON:
        {{
            "response": "Hebrew text",
            "stats": {{"Vision": int, "Independence": int, "Execution": int}},
            "confidence_level": int,
            "master_insight": "Deep critical analysis in Hebrew"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-15:],
            response_format={ "type": "json_object" }
        )
        
        res = json.loads(response.choices[0].message.content)
        
        # עדכון ה-State
        st.session_state.messages.append({"role": "assistant", "content": res["response"]})
        st.session_state.stats = res["stats"]
        st.session_state.confidence = min(100, res["confidence_level"])
        st.session_state.master_insight = res["master_insight"]
        
        st.rerun()

# לוח מדדים (Dashboard) בתחתית הדף
st.divider()
st.subheader("DNA Snapshot")
col1, col2, col3 = st.columns(3)

col1.metric("Vision", f"{st.session_state.stats['Vision']}%")
col2.metric("Independence", f"{st.session_state.stats['Independence']}%")
col3.metric("Execution", f"{st.session_state.stats['Execution']}%")

# אזור הניתוח הסמוי (Investor View)
with st.expander("🔍 ניתוח עומק למנהלים (Investor View)"):
    st.warning(st.session_state.master_insight)
    st.bar_chart(st.session_state.stats)

# כפתור איפוס בסיידבר
if st.sidebar.button("איפוס נתונים"):
    st.session_state.clear()
    st.rerun()
