import streamlit as st
from openai import OpenAI
import json

# אתחול הלקוח
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide", page_title="Collective Mind DNA - Pro Simulator")

# 1. תיקון תצוגה - צבעים בהירים לטקסט ושדה קלט ברור
st.markdown("""
    <style>
    /* רקע כללי */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* תיקון צבע המדדים (Metrics) - שיהיה לבן וקריא */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
    }
    
    /* עיצוב תיבות הסטטוס */
    .status-box { 
        background-color: #1f2937; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #3b82f6; 
        margin-bottom: 20px;
        color: #ffffff;
    }
    
    /* תיקון שדה הטקסט (Text Area) שיהיה קריא */
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
    }
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

# 3. סיידבר
with st.sidebar:
    st.title("📊 DNA Dashboard")
    st.write("---")
    st.metric("Vision", f"{st.session_state.stats['Vision']}%")
    st.metric("Execution", f"{st.session_state.stats['Execution']}%")
    st.metric("Independence", f"{st.session_state.stats['Independence']}%")
    
    st.write("---")
    st.write(f"**מהימנות:** {st.session_state.conf}%")
    st.progress(st.session_state.conf / 100)
    
    with st.expander("👁️ תובנת יזם"):
        st.info(st.session_state.insight)
    
    if st.button("🔄 איפוס סימולציה"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")

# 4. לוגיקת ה-Prompt
SYS_PROMPT = """
אתה פרופילר של מנהלים בכירים (Ops, CS, Data). 
תפקידך: להציב למשתמש דילמות קיצון ניהוליו כדי לחשוף את ה-DNA המקצועי שלו.
1. הצג תרחיש (Scenario) קונקרטי עם נתונים סותרים.
2. דרוש החלטה קשה (Trade-off). 
3. ענה בעברית חדה וישירה.
4. החזר JSON: {"res": "text", "stats": {"Vision": int, "Independence": int, "Execution": int}, "conf": int, "ins": "insight"}
"""

# 5. זרימת האפליקציה - שדה לינקדין/רקע
if not st.session_state.init:
    st.subheader("שלב 1: ניתוח רקע מקצועי")
    st.write("הדבק כאן את פרופיל הלינקדין שלך או תיאור קצר של הניסיון שלך:")
    
    # שדה הזנת טקסט ברור
    user_background = st.text_area("תיאור מקצועי / LinkedIn Profile", placeholder="לדוגמה: מנהל אופרציה עם רקע בדאטה...", height=250)
    
    if st.button("🚀 התחל ניתוח DNA"):
        if user_background:
            with st.spinner("מנתח רקע ובונה דילמה..."):
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": SYS_PROMPT}, {"role": "user", "content": f"זה הרקע שלי, הצג לי דילמה ראשונה: {user_background}"}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(res.choices[0].message.content)
                st.session_state.messages.append({"role": "assistant", "content": data['res']})
                st.session_state.stats = data['stats']
                st.session_state.init = True
                st.rerun()
        else:
            st.warning("בבקשה תדביק רקע מקצועי כדי שנוכל להתחיל.")

else:
    # הצגת הצ'אט
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(f"<div class='status-box'>{m['content']}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("מה ההחלטה שלך?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("מנתח החלטה..."):
            raw_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": SYS_PROMPT}] + st.session_state.messages[-6:],
                response_format={"type": "json_object"}
            )
            data = json.loads(raw_res.choices[0].message.content)
            
            # עדכון סטטיסטיקות
            for key in st.session_state.stats:
                st.session_state.stats[key] = int((st.session_state.stats[key] * 0.6) + (data['stats'].get(key, 50) * 0.4))
            
            st.session_state.messages.append({"role": "assistant", "content": data['res']})
            st.session_state.conf = min(100, st.session_state.conf + 10)
            st.session_state.insight = data['ins']
            st.rerun()
