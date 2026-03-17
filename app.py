import streamlit as st
from openai import OpenAI
import json

# עיצוב CSS - מבטיח קריאות וצבעים נכונים
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

# סיידבר עם המדדים
with st.sidebar:
    st.title("📊 DNA Dashboard")
    st.metric("Vision (חזון)", f"{st.session_state.stats['Vision']}%")
    st.metric("Independence (עצמאות)", f"{st.session_state.stats['Independence']}%")
    st.metric("Execution (ביצוע)", f"{st.session_state.stats['Execution']}%")
    if st.button("🔄 איפוס אבחון"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA Profiler")

# שלב 1: ניתוח הלינקדין והוצאת השאלה ה"רעילה" הראשונה
if not st.session_state.linkedin:
    st.info("הדבק את ה-About שלך כדי להתחיל בסימולציית קבלת החלטות.")
    li_input = st.text_area("LinkedIn About Section:", height=200)
    if st.button("צור דילמה מותאמת אישית"):
        if li_input:
            st.session_state.linkedin = li_input
            
            # פרומפט שיוצר את השאלה המדויקת שדיברנו עליה
            first_question_prompt = f"""
            You are a Master VC Profiler. Read this LinkedIn About:
            {li_input}
            Identify the conflict between the user's skills (e.g. Data vs. Ops).
            Ask ONE sharp Hebrew question that forces a trade-off. 
            Do not allow a 'both' answer. Be direct and provocative.
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

    if prompt := st.chat_input("ההחלטה שלך..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # לוגיקת "אנטי-איזון" - לא נותן למשתמש לברוח לתשובות כלליות
        sys_prompt = """
        You are a Brutally Honest VC Profiler. 
        CRITICAL RULES:
        1. If the user tries to balance or 'mitigate risks' (Both/And approach), CALL THEM OUT.
        2. Force them back into a Binary Choice (This or That).
        3. Use the LinkedIn context to make the dilemma feel personal and high-stakes.
        4. No compliments. No fluff. Max 3 sentences.
        
        Return ONLY JSON:
        {
            "user_reply": "Short critique of their 'balance' + A NEW SHARPER DILEMMA (Hebrew)",
            "master_insight": "What does their hesitation or choice say about their DNA? (Hebrew)",
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
