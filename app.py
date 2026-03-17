import streamlit as st
from openai import OpenAI
import json

# עיצוב CSS - מבטיח קריאות (מספרים לבנים)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    .stChatMessage { border-radius: 10px; border: 1px solid #3b82f6; margin-bottom: 10px; }
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
        "master_insight": "מנתח נתונים...",
        "linkedin": ""
    })

with st.sidebar:
    st.title("📊 DNA Dashboard")
    st.metric("Vision", f"{st.session_state.stats['Vision']}%")
    st.metric("Independence", f"{st.session_state.stats['Independence']}%")
    st.metric("Execution", f"{st.session_state.stats['Execution']}%")
    if st.button("🔄 איפוס"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA Profiler")

if not st.session_state.linkedin:
    li_input = st.text_area("הדבק את ה-About שלך מהלינקדין:", height=200)
    if st.button("צור דילמה 'תכלס'"):
        if li_input:
            st.session_state.linkedin = li_input
            
            # הפרומפט המדויק שתוקף את הסתירה בין Ops ל-Data
            first_question_prompt = f"""
            Context: {li_input}
            Task:
            1. Identify a core contradiction in this profile (e.g., Structured Ops vs. Fast Data Science).
            2. Ask ONE sharp Hebrew question that forces a BINARY choice. 
            3. Do NOT ask 'what do you prefer'. 
            4. Create a high-stakes scenario where the user must choose between operational stability and data-driven innovation.
            5. No intro or compliments. Just the dilemma.
            """
            
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": first_question_prompt}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

else:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("מה ההחלטה שלך?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # לוגיקה שמוודאת שה-AI לא מוותר לך אם ניסית לאזן
        sys_prompt = """
        You are a Brutally Honest VC Profiler. 
        If the user tries to balance or mitigate (saying 'I'll do both' or 'it depends'), EXPOSE the fallacy. 
        Force them into a corner. Demand to know which specific resource they sacrifice.
        Return ONLY JSON:
        {
            "user_reply": "Critique + New Sharp Dilemma (Hebrew)",
            "master_insight": "DNA Analysis (Hebrew)",
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
