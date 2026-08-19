
# 🧠 مُدرك | Modrek

> AI-powered flashcard generator that transforms your study materials into smart, interactive flashcards.

مُدرك هو أداة دراسية ذكية تساعد الطلاب على تحويل ملازمهم وموادهم الدراسية إلى بطاقات مراجعة تفاعلية باستخدام الذكاء الاصطناعي.

بدلًا من قراءة المحتوى كاملًا وكتابة أسئلة المراجعة يدويًا، يتيح لك مُدرك رفع ملفك وتحويل محتواه إلى بطاقات مراجعة جاهزة.

---

## ✨ Features

- 🧠 توليد بطاقات Flashcards باستخدام Gemini AI
- 📄 دعم ملفات PDF
- 📝 دعم ملفات Word (.docx)
- 📃 دعم ملفات TXT
- 🎯 اختيار مستوى الأسئلة:
  - سهل
  - متوسط
  - صعب
  - مكس
- 🌐 اختيار لغة البطاقات:
  - العربية
  - English
- 🔢 اختيار عدد البطاقات
- 🔄 إعادة توليد مجموعة جديدة من الأسئلة
- 🚫 تقليل تكرار الأسئلة السابقة
- 💫 بطاقات تفاعلية قابلة للقلب
- 📱 تصميم متجاوب مع الجوال والتابلت والكمبيوتر

---

## 🎯 How It Works

```text
Study Material
      ↓
    Upload
      ↓
Text Extraction
      ↓
   Gemini AI
      ↓
Smart Flashcards
      ↓
     Review
````

1. يستخرج النظام النص من الملف.
2. يتم إرسال المحتوى وإعدادات المستخدم إلى Gemini AI.
3. يقوم Gemini بإنشاء الأسئلة والإجابات.
4. يعرض مُدرك البطاقات بشكل تفاعلي.
5. يمكن للطالب قلب البطاقة لرؤية الإجابة.
6. يمكن إعادة توليد مجموعة جديدة عند الحاجة.

---

## 🛠️ Technologies

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive Design

### Backend

* Python
* FastAPI

### AI

* Google Gemini API

### File Processing

* PyPDF
* python-docx

### Deployment

* Vercel

---

## 📁 Supported Files

| File Type    | Support |
| ------------ | ------- |
| PDF          | ✅       |
| Word (.docx) | ✅       |
| TXT          | ✅       |

---

## 🎚️ Question Difficulty

| Level  | Description                                                         |
| ------ | ------------------------------------------------------------------- |
| Easy   | يركز على التعريفات والمعلومات المباشرة والحقائق الواضحة.            |
| Medium | يركز على فهم المعلومات والربط بين المفاهيم والسبب والنتيجة.         |
| Hard   | يركز على التحليل والاستنتاج والربط بين المعلومات والفروقات الدقيقة. |
| Mixed  | ينشئ مزيجًا من مستويات الأسئلة المختلفة.                            |

---

## 🌐 Flashcard Languages

يدعم مُدرك إنشاء البطاقات بلغتين:

* 🇸🇦 العربية
* 🇺🇸 English

---

## 🔄 Regenerate

إذا لم تكن المجموعة الأولى مناسبة، يمكن للمستخدم اختيار **إعادة توليد** لإنشاء مجموعة جديدة من الأسئلة.

يتم إرسال البطاقات السابقة إلى النظام لتقليل تكرار الأسئلة والمعلومات السابقة، ومحاولة إنشاء أسئلة جديدة من محتوى الملف.

---

## 📄 File Processing

يدعم مُدرك استخراج المحتوى من:

* 📄 ملفات PDF
* 📝 ملفات Microsoft Word
* 📃 ملفات TXT

ثم يتم استخدام النص المستخرج لإنشاء البطاقات اعتمادًا على محتوى الملف فقط.

---

## 🔌 API

### `POST /upload`

يستقبل:

| Parameter        | Description                     |
| ---------------- | ------------------------------- |
| `file`           | الملف الدراسي                   |
| `difficulty`     | مستوى الأسئلة                   |
| `card_count`     | عدد البطاقات                    |
| `language`       | لغة البطاقات                    |
| `previous_cards` | البطاقات التي تم إنشاؤها سابقًا |

ويعيد البطاقات بشكل متدفق:

```json
{
  "question": "Example question?",
  "answer": "Example answer."
}
```

---

## 🔐 API Key

يستخدم المشروع **Gemini API** لإنشاء البطاقات.

يتم تخزين مفتاح API باستخدام **Environment Variables** بدلًا من وضعه داخل الكود.

أنشئ ملف:

```text
.env
```

ثم أضف:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

> ⚠️ لا تقم برفع ملف `.env` إلى GitHub.

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/MohammedB77/Modrek.git
```

### 2. Enter the project

```bash
cd Modrek
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

أنشئ ملف `.env`:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

افتح:

```text
http://127.0.0.1:8000
```

---

## 📂 Project Structure

```text
Modrek/
│
├── api/
│   └── index.py
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── Assets/
│   │
│   └── js/
│       └── script.js
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

---

## 🔒 Security

* 🔑 يتم تخزين Gemini API Key باستخدام Environment Variables.
* 🚫 ملف `.env` مستبعد من Git.
* 🔐 لا يتم وضع API Key داخل JavaScript.
* 📁 تتم معالجة الملفات على الخادم.

---

## 🚀 Deployment

المشروع مجهز للنشر باستخدام **Vercel**.

### Environment Variable

أضف المتغير التالي في إعدادات Vercel:

```text
GEMINI_API_KEY
```

ثم ضع مفتاح Gemini كقيمة للمتغير.

---

## 📸 Screenshots

### Landing Page

![Modrek Landing Page](screenshots/landing.png)

### Flashcards

![Modrek Flashcards](screenshots/flashcards.png)

---

## 🤝 Contributing

المساهمات والأفكار لتحسين المشروع مرحب بها.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Open a Pull Request.

---

## ⭐ Support

إذا أعجبك المشروع أو وجدته مفيدًا، لا تنسَ إعطاء المشروع ⭐ على GitHub.

---

## 👨‍💻 Developer

**Mohammed Bamhraz**

---

## 📄 License
```

```
