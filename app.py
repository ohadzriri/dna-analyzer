import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# עיצוב מותאם אישית - Dark Tech Style
st.set_page_config(layout="wide", page_title="DNA Profiler")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; }
    .dna-card { background: linear-gradient(135.2deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.update({
        "messages": [],
        "stats": {"Vision": 50, "Execution": 50, "Independence": 50},
        "ins": "ממתין לניתוח ראשוני...",
        "init": False
    })

# סיידבר מעוצב
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dna-helix.png")
    st.title("DNA Dashboard")
    st.divider()
    for label, value in st.session_state.stats.items():
        st.metric(label, f"{value}%")
    st.divider()
    if st.button("🚀 איפוס אבחון"):
        st.session_state.clear()
        st.rerun()

st.title("🧠 Collective Mind DNA")
st.write("---")

if not st.session_state.init:
    with st.container():
        st.markdown("<div class='dna-card'><h3>שלב 1: סריקת פרופיל</h3><p>הדבק את הלינקדין או הרקע המקצועי שלך כדי שנוכל לבנות את המודל הראשוני.</p></div>", unsafe_allow_html=True)
        txt = st.text_area("", placeholder="הדבק כאן...", height=150)
        if st.button("נתח DNA"):
            if txt:
                # הנחייה למודל להיות "פרופילר סימולציה"
                sys = """You are a DNA Profiler. Hebrew, 1st person. 
                Instead of dry questions, present a high-stakes professional DILEMMA based on the user's background. 
                Test their 'Proof of Capability'. 
                Format: JSON {"res": "Dilemma text", "stats": {"Vision": 60, "Execution": 40, "Independence": 50}, "ins": "Initial analysis"}"""
                
                res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": sys}, {"role": "user", "content": txt}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(res.choices[0].message.content)
                st.session_state.messages.append({"role": "user", "content": f"רקע: {txt}"})
                st.session_state.messages.append({"role": "assistant", "content": data['res']})
                st.session_state.stats = data['stats']
                st.session_state.init = True
                st.rerun()

else:
    # הצגת הצ'אט בסטייל של בועות דיבור
    for m in st.session_state.messages:
        if not m["content"].startswith("רקע:"):
            with st.chat_message(m["role"]):
                st.markdown(f"<div class='dna-card'>{m['content']}</div>", unsafe_allow_html=True)

    if p := st.chat_input("מה ההחלטה שלך?"):
        st.session_state.messages.append({"role": "user", "content": p})
        
        sys = """You are a Profiler. Hebrew. 
        1. Analyze the user's decision. 2. Update their DNA stats. 
        3. Present the NEXT logical challenge or pivot. 
        Be sharp, professional, and focus on capability proof.
        JSON format: {"res": "Feedback + Next Dilemma", "stats": {}, "ins": "Deep insight"}"""
        
        raw = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys}] + st.session_state.messages[-6:],
            response_format={"type": "json_object"}
        )
        data = json.loads(raw.choices[0].message.content)
        st.session_state.messages.append({"role": "assistant", "content": data['res']})
        st.session_state.stats = data['stats']
        st.session_state.ins = data['ins']
        st.rerun()
