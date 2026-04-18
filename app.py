import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText

# =========================
# 🔐 إعداد API
# =========================
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ لم يتم العثور على API KEY")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-flash-latest")

# =========================
# 👤 تسجيل الطالب
# =========================
if "student_name" not in st.session_state:
    st.session_state.student_name = None

if not st.session_state.student_name:
    st.title("🎓 تسجيل الطالب")

    name = st.text_input("اسم الطالب")
    student_id = st.text_input("رقم الطالب")

    if st.button("دخول"):
        if name and student_id:
            st.session_state.student_name = name
            st.session_state.student_id = student_id
            st.rerun()
        else:
            st.warning("الرجاء إدخال جميع البيانات")

    st.stop()

# =========================
# ⚠️ كلمات الخطر
# =========================
unsafe_keywords = [
    "تحرش", "اغتصاب", "لمس", "غير لائق",
    "تنمر", "يسخر", "يضحك علي",
    "ضرب", "يضربني", "يعنفني",
    "تهديد", "يهددني",
    "ابتزاز", "يبتزني",
    "عنف أسري", "أبي يضربني", "أمي تضربني",
    "أخاف", "في خطر", "أذوني"
]

def detect_unsafe_message(text):
    for word in unsafe_keywords:
        if word in text:
            return True
    return False

# =========================
# 📧 إرسال إيميل
# =========================
def send_alert_email(student_message):
    try:
        sender_email = st.secrets.get("EMAIL_USER")
        sender_password = st.secrets.get("EMAIL_PASS")
        receiver_email = st.secrets.get("ahmadmoaidi@gmail.com")

        body = f"""
🚨 تنبيه من المساعد الذكي

👤 اسم الطالب: {st.session_state.student_name}
🆔 رقم الطالب: {st.session_state.student_id}

📩 الرسالة:
{student_message}
"""

        msg = MIMEText(body)
        msg["Subject"] = "🚨 بلاغ طالب"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        st.error(f"خطأ في إرسال الإيميل: {e}")

# =========================
# 🤖 واجهة التطبيق
# =========================
st.title("🤖 مساعد الطالب الذكي")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("كيف أساعدك اليوم؟")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # =========================
    # 🛑 فحص الأمان
    # =========================
    if detect_unsafe_message(prompt):
        send_alert_email(prompt)

        warning_message = """
⚠️ أنا هنا لدعمك 💙

لاحظت أن رسالتك قد تشير إلى موقف صعب.  
حرصًا على سلامتك، سيتم إشعار الجهة المختصة في مدرستك لمساعدتك بسرّية تامة.
"""

        with st.chat_message("assistant"):
            st.markdown(warning_message)

        st.session_state.messages.append({
            "role": "assistant",
            "content": warning_message
        })

        st.stop()

    # =========================
    # 🤖 الرد الذكي
    # =========================
    try:
        response = model.generate_content(
            f"أنت مساعد ذكي للطلاب، اشرح بطريقة بسيطة:\n{prompt}"
        )

        reply = response.text

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    except Exception as e:
        st.error(f"خطأ: {e}")
