import streamlit as st
from openai import OpenAI
import json

# אתחול הלקוח
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA - Pro Simulator")

# 1. עיצוב ממשק (Dark Mode מקצועי)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; }
    .status-box { background-color: #111827; padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. אתחול ה-Session State
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 20,
        "insight": "ממתין להחלטה ראשונה...",
        "init": False
    })

# 3. סיידבר - לוח בקרה ויזואלי
with st.sidebar:
    st.title("📊 DNA Dashboard")
    st.write("---")
    col1, col2 = st.columns(2)
    st.metric("Vision", f"{st.session_state.stats['Vision']}%")
    st.metric("Execution", f"{st.session_state.stats['Execution']}%")
    st.metric("Independence", f"{st.session_state.stats['Independence']}%")
    
    st.write("---")
    st.write(f"**מהימנות אבחון:** {st.session_state.conf}%")
    st.progress(st.session_state.conf / 100)
    
    with st.expander("👁️ תובנת יזם (סמוי)"):
        st.info(st.session_state.insight)
    
    if st.button("🔄 איפוס סימולציה"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")
st.caption("סימולטור קבלת החלטות לדרג ניהולי")

# 4. לוגיקת ה-Prompt (הלב של המערכת)
SYS_PROMPT = """
אתה פרופילר של מנהלים בכירים (Ops, CS, Data). 
תפקידך: להציב למשתמש דילמות קיצון ניהוליות כדי לחשוף את ה-DNA המקצועי שלו.
חוקים:
1. אל תשאל שאלות תיאורטיות ("איך היית מאזן?").
2. בכל שלב, הצג תרחיש (Scenario) קונקרטי עם נתונים סותרים. לדוגמה: לקוח גדול עוזב מול קריסה של תשתית.
3. דרוש החלטה קשה (Trade-off). אל תאפשר "גם וגם".
4. ענה בעברית חדה, ישירה ומקצועית.
5. החזר אך ורק JSON במבנה הבא:
{"res": "ניתוח קצר של ההחלטה הקודמת + הדילמה הבאה", "stats": {"Vision": int, "Independence": int, "Execution": int}, "conf": int, "ins": "תובנה אנליטית עמוקה"}
"""

# 5
