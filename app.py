import streamlit as st
import google.generativeai as genai

st.title("🤖 مساعد الطالب الذكي")

# جلب المفتاح
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ لم يتم العثور على API KEY")
    st.stop()

# إعداد Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# واجهة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        reply = response.text

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"خطأ: {e}")
