import streamlit as st
from openai import OpenAI
import json

# 1. הגדרות עיצוב לממשק נקי ומקצועי
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    .stChatMessage { border-radius: 10px; border: 1px solid #3b82f6; background-color: #1f2937; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("Missing OpenAI API Key in Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "master_insight": "ממתין לניתוח ראשוני...",
        "linkedin": ""
    })

with st.sidebar:
    st.title("📊 DNA Dashboard")
    st.metric("Vision", f"{st.session_state.stats['Vision']}%")
    st.metric("Independence", f"{st.session_state.stats['Independence']}%")
    st.metric("Execution", f"{st.session_state.stats['Execution']}%")
    if st.button("🔄 איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA Profiler")

# שלב 1: הזנת הלינקדין והוצאת הדילמה ה"צרופה"
if not st.session_state.linkedin:
    st.subheader("ניתוח פרופיל מקצועי")
    li_input = st.text_area("הדבק את ה-About מהלינקדין שלך:", height=200, placeholder="I'm an experienced Operations leader...")
    if st.button("נתח והפק דילמה"):
        if li_input:
            st.session_state.linkedin = li_input
            
            # פרומפט "תופר" - מחייב ניתוח סתירות פנימיות
            first_question_prompt = f"""
            User LinkedIn About: "{li_input}"
            
            TASK: 
            1. Identify the core professional tension: The user claims to be both a master of "Structured Processes/Quality" AND "Digital Transformation/Data Science". 
            2. Create a specific, non-emergency scenario where their own "Structured Processes" (SOPs) are the direct obstacle to the "Innovation/Data" goals they claim to have.
            3. Ask ONE sharp question in Hebrew that forces them to either 'Kill' their own processes or 'Sacrifice' innovation.
            
            STRICT LIMITATIONS:
            - NO generic "system crashes" or "emergencies". 
            - NO compliments or introductions. 
            - Focus on the 'Slow Death' of the company's innovation due to the user's rigid operational success.
            """
            
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": first_question_prompt}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

else:
    # הצגת היסטוריה
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("ההחלטה שלך (תהיה חד)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # לוגיקת המשך קשוחה - "אנטי-איזון"
        sys_prompt = """
        You are a Brutally Honest VC Profiler. 
        If the user tries to balance (e.g., 'I will optimize both'), call them out for being a 'typical corporate manager' who avoids hard choices.
        Force a binary trade-off. 
        Return ONLY JSON:
        {
            "user_reply": "Critique + Shiper Dilemma (Hebrew)",
            "master_insight": "Deep DNA analysis of their choice (Hebrew)",
            "stats": {"Vision": int, "Independence": int, "Execution": int}
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages,
            response_format={ "type": "json_object" }
        )
        
        res_data = json.loads(response.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": res_data["user_reply"]})
        st.session_state.stats = res_data["stats"]
        st.rerun()
