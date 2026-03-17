import streamlit as st
from openai import OpenAI
import json

# 1. עיצוב CSS - טקסט לבן במדדים ועיצוב נקי
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #9ca3af !important; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; border: 1px solid #3b82f6; }
    .stTextArea textarea { background-color: #111827 !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. חיבור ל-API
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("שגיאה: המפתח הסודי לא הוגדר ב-Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(layout="wide", page_title="Collective Mind DNA - Pro")

# 3. אתחול משתנים
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "master_insight": "ממתין להחלטה ראשונה...",
        "linkedin": ""
    })

# 4. סיידבר ניהולי
with st.sidebar:
    st.title("🚀 DNA Control")
    view_mode = st.radio("תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    if st.button("🔄 איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

# 5. לוגיקת ה-Prompt ה"תוקפני" (זה מה שמייצר את ה"תכלס")
SYS_PROMPT = """
You are a Brutally Honest VC Profiler. Your goal is to find the user's BREAKING POINT.
STRICT RULES:
1. NO COMPLIMENTS. Don't say "Good point" or "I agree".
2. NO THEORY. If the user gives a textbook answer (Pareto, Agile, KPI), CRITICIZE it as "Fluff" and present a MESSY scenario where that theory fails.
3. FORCE A TRADE-OFF. Every response MUST end with a "This or That" dilemma where both options have a heavy price (Money vs. People, Speed vs. Quality).
4. TONE: Sharp, senior, direct Hebrew.
5. NO LONG SENTENCES. Max 3 sentences for feedback, then the dilemma.

Return ONLY JSON:
{
    "user_reply": "Short critique + THE MESSY DILEMMA (Hebrew)",
    "master_insight": "What does their last choice reveal about their actual bias? (Hebrew, 3 sentences)",
    "stats": {"Vision": int, "Independence": int, "Execution": int}
}
"""

if view_mode == "צד משתמש":
    st.title("🧠 Collective Mind DNA")
    
    if not st.session_state.linkedin:
        st.subheader("שלב 1: הזנת רקע מקצועי")
        li_input = st.text_area("הדבק פרופיל לינקדין או רקע קצר:", height=150, placeholder="מנהל אופרציה, רקע בדאטה...")
        if st.button("התחל אבחון קשוח"):
            if li_input:
                st.session_state.linkedin = li_input
                # יצירת דילמה ראשונה מבוססת רקע
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "You are a senior profiler. Read this background and start with ONE very short, very tough dilemma in Hebrew. No intro. No hello. Just the dilemma: " + li_input}],
                    max_tokens=200
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
                st.rerun()
    else:
        # תצוגת צ'אט
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.write(m["content"])

        if prompt := st.chat_input("ההחלטה שלך (תכלס)..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("מנתח..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": SYS_PROMPT}] + st.session_state.messages[-6:],
                    response_format={ "type": "json_object" }
                )
                
                res_data = json.loads(response.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": res_data["user_reply"]})
                st.session_state.stats = res_data["stats"]
                st.session_state.master_insight = res_data["master_insight"]
                st.rerun()

    # מדדים בתחתית
    st.divider()
    cols = st.columns(3)
    cols[0].metric("Vision", f"{st.session_state.stats['Vision']}%")
    cols[1].metric("Independence", f"{st.session_state.stats['Independence']}%")
    cols[2].metric("Execution", f"{st.session_state.stats['Execution']}%")

else: # Investor View
    st.title("🕵️ Investor Dashboard")
    st.info(f"**ניתוח אופי:** {st.session_state.master_insight}")
    st.write("---")
    st.subheader("דירוג DNA")
    st.json(st.session_state.stats)
