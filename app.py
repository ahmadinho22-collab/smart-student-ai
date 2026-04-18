// -------------------------------
// 1. الإعدادات الأساسية
// -------------------------------
import express from "express";
import bodyParser from "body-parser";
import nodemailer from "nodemailer";
import { OpenAI } from "openai";

const app = express();
app.use(bodyParser.json());

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// -------------------------------
// 2. دالة إرسال البريد للإدارة
// -------------------------------
async function sendAlertEmail(studentName, studentId, message) {
  const transporter = nodemailer.createTransport({
    service: "gmail", 
    auth: {
      user: process.env.ALERT_EMAIL,
      pass: process.env.ALERT_EMAIL_PASS
    }
  });

  const mailOptions = {
    from: process.env.ALERT_EMAIL,
    to: "ahmadmoaidi@gmail.com",
    subject: "🚨 تنبيه عاجل: تم رصد حالة محتملة",
    text: `
تم اكتشاف حالة حساسة من قبل أحد الطلاب.

اسم الطالب: ${studentName}
رقم الطالب: ${studentId}

الرسالة التي كتبها:
"${message}"

يرجى التعامل مع الحالة بشكل عاجل.
`
  };

  await transporter.sendMail(mailOptions);
}

// كلمات حساسة
const dangerWords = [
  "تحرش", "اغتصاب", "لمس غير لائق",
  "تنمر", "يضربني", "عنف", "تعنيف",
  "عنف أسري", "يهددني", "تهديد",
  "ابتزاز", "صور", "فضيحة"
];

// -------------------------------
// -------------------------------
app.post("/start", async (req, res) => {
  const { name, studentId } = req.body;

  if (!name || !studentId) {
    return res.json({ error: "الرجاء إدخال الاسم والرقم المدرسي لبدء المحادثة." });
  }

  // نخزن بيانات الطالب داخل session بسيط (يمكن تغييره لقاعدة بيانات)
  req.session = { name, studentId };

  return res.json({
    message: `مرحبًا ${name}! أنا هنا لمساعدتك في الدراسة أو المشكلات المدرسية.`
  });
});

// -------------------------------
// 4. التفاعل مع المساعد
// -------------------------------
app.post("/chat", async (req, res) => {
  const { message } = req.body;
  const session = req.session;

  if (!session) {
    return res.json({
      error: "يجب تسجيل الاسم والرقم أولاً عبر /start"
    });
  }

  const studentName = session.name;
  const studentId = session.studentId;

  // -------------------------------
  // 5. اكتشاف الكلمات الحساسة
  // -------------------------------
  const foundDanger = dangerWords.some(word => message.includes(word));

  if (foundDanger) {
    // أرسل بريدًا للإدارة
    sendAlertEmail(studentName, studentId, message);

    // رسالة للطالب (لطيفة وغير مخيفة)
    return res.json({
      alert: true,
      message:
        "شكرًا لثقتك. لاحظتُ أن رسالتك تحتوي على مشكلة قد تحتاج إلى دعم من مختصين. سيتم تحويل الموضوع للجهة المناسبة في المدرسة لمساعدتك، وسيتم التعامل معه بسرية تامة."
    });
  }

  // -------------------------------
  // 6. استدعاء API للدعم الدراسي
  // -------------------------------
  const aiResponse = await client.responses.create({
    model: "gpt-4.1-mini",
    input: `الطالب: ${studentName} (${studentId}) يسأل: ${message}`
  });

  res.json({
    alert: false,
    answer: aiResponse.output[0].content[0].text
  });
});

// -------------------------------
// 7. تشغيل السيرفر
// -------------------------------
app.listen(3000, () => {
  console.log("Assistant running on port 3000");
});
