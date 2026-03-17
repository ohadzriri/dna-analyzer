import streamlit as st
from openai import OpenAI
import json
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# חיבורים
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# פונקציית עזר לשמירה ב-Google Sheets (תעבוד רק אחרי הגדרת ה-Secrets)
def save_to_sheets(u_msg, ai_msg):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # מבנה השורה בטבלה
        new_row = [now, u_msg, ai_msg, str(st.session_state.stats), st.session_state.conf, st.session_state.insight]
        conn.create(data=[new_row])
    except:
        pass # מונע קריסה אם ה-Sheets עדיין לא מחובר

st.set_page_config(layout="wide", page_title="Collective Mind DNA")

# 1. אתחול ה-Session State
if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Independence": 50, "Execution": 50},
        "conf": 10,
        "insight": "מנתח נתוני פתיחה...",
        "init": False
    })

# 2. סיידבר - ניהול תצוגה ומדדים
with st.sidebar:
    st.title("⚙️ לוח בקרה")
    mode = st.radio("מצב תצוגה:", ["צד משתמש", "צד יזם (Investor View)"])
    
    if mode == "צד יזם (Investor View)":
        st.divider()
        st.subheader("📊 מדדי DNA")
        st.metric("חזון (Vision)", f"{st.session_state.stats.get('Vision', 50)}%")
        st.metric("עצמאות (Independence)", f"{st.session_state.stats.get('Independence', 50)}%")
        st.metric("ביצוע (Execution)", f"{st.session_state.stats.get('Execution', 50)}%")
        st.write(f"**מהימנות אבחון:** {st.session_state.conf}%")
        st.progress(st.session_state.conf / 100)
        st.divider()
        st.subheader("תובנה אנליטית סמויה")
        st.info(st.session_state.insight)
    
    if st.button("איפוס מערכת"):
        st.session_state.clear()
        st.rerun()

# 3. מסך ראשי
st.title("🧠 Collective Mind DNA")

# שלב א': הזנת רקע (לינקדין/טקסט)
if not st.session_state.init:
    st.subheader("בוא נבנה את פרופיל ה-DNA המקצועי שלך.")
    txt = st.text_area("הדבק כאן פרופיל לינקדין או רקע מקצועי קצר:", height=200)
    
    if st.button("התחל אבחון"):
        if txt:
            with st.spinner("מנתח רקע..."):
                sys_init = "אתה פרופילר מקצועי חסר רחמים. ענה אך ורק בעברית, בגוף ראשון. אל תהיה 'נחמד'. נתח את הניסיון המקצועי ושאל שאלה אחת בוטה ומאתגרת על היכולת שלהם לספק תוצאות תחת לחץ."
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": sys_init}, {"role": "user", "content": txt}]
                )
                ai_msg = res.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                st.session_state.init = True
                save_to_sheets("INIT_BACKGROUND", ai_msg)
                st.rerun()

# שלב ב': צ'אט אבחון
else:
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if prompt := st.chat_input("ענה לשאלת הפרופילר..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with
