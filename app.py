import streamlit as st
from openai import OpenAI
import json

# חיבור ל-OpenAI דרך Secrets של Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA | Live Tracker")

# אתחול Session State - המידע הזה יהיה הבסיס לזיכרון ארוך הטווח
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stats = {"Vision": 50, "Independence": 50, "Execution": 50}
    st.session_state.confidence = 10  # מדד כמה המערכת "בטוחה" באבחון שלה
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
if prompt := st.chat_input("שתף מחשבה, דווח על ביצוע משימה או התייעץ על דילמה..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("מעבד את הנתונים לתוך ה-DNA שלך..."):
        # בניית ה-Prompt שגורם ל-AI להתנהג כמאבחן מתמשך
        sys_prompt = f"""
        You are a Continuous Professional Profiler. 
        Your goal is to build a dynamic DNA profile of the user based on daily interactions.
        
        Current Stats: {st.session_state.stats}
        Current Confidence: {st.session_state.confidence}%
        
        Your task:
        1. Analyze the new input (task, thought, or dilemma).
        2. Update the DNA stats (0-100) based on the evidence provided. 
           - If they report a successful execution, increase 'Execution'. 
           - If they share a strategic vision, increase 'Vision'.
        3. Respond in Hebrew: A brief, professional validation + one challenging follow-up question.
        4. Increment 'confidence_level' (max 100) by 3-8 points per meaningful interaction.
        
        Return ONLY JSON:
        {{
            "response": "Hebrew text",
            "stats": {{"Vision": int, "Independence": int, "Execution": int}},
            "confidence_level": int,
            "master_insight": "Deep critical analysis for the investor view (Hebrew)"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-15:], # שולחים היסטוריה רלוונטית
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

col1.metric("Vision (חזון ואסטרטגיה)", f"{st.session_state.stats['Vision']}%")
col2.metric("Independence (עצמאות ניהולית)", f"{st.session_state.stats['Independence']}%")
col3.metric("Execution (יכולת ביצוע)", f"{st.session_state.stats['Execution']}%")

# אזור הניתוח הסמוי (Investor View)
with st.expander("🔍 ניתוח עומק למנהלים (Investor View)"):
    st.warning(st.session_state.master_insight)
    st.write("---")
    st.write("מדדי DNA נוכחיים:")
    st.bar_chart(st.session_state.stats)

# כפתור איפוס (לצורכי בדיקה)
if st.sidebar.button("איפוס כל הנתונים"):
    st.session_state.clear()
    st.rerun()        st.balloons()
        with st.expander("ראה את סיכום הפרופיל שלך"):
            st.write(st.session_state.master_insight)

# מדדים בתחתית
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Vision", f"{st.session_state.stats['Vision']}%")
c2.metric("Independence", f"{st.session_state.stats['Independence']}%")
c3.metric("Execution", f"{st.session_state.stats['Execution']}%")
