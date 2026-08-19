from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pypdf import PdfReader
from docx import Document
from io import BytesIO

from google import genai
from google.genai import types

from dotenv import load_dotenv

import os
import json
import asyncio


load_dotenv()

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

app = FastAPI()


app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(
            BASE_DIR,
            "static"
        )
    ),
    name="static"
)

templates = Jinja2Templates(
    directory=os.path.join(
        BASE_DIR,
        "templates"
    )
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


api_key = os.getenv(
    "GEMINI_API_KEY"
)

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY غير موجود في Environment Variables"
    )

client = genai.Client(
    api_key=api_key
)


# الصفحة الرئيسية

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# استخراج النص

async def extract_text(file):
    filename = (
        file.filename or ""
    ).lower()

    data = await file.read()

    if filename.endswith(".pdf"):
        reader = PdfReader(
            BytesIO(data)
        )

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if filename.endswith(".docx"):
        document = Document(
            BytesIO(data)
        )

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    if filename.endswith(".txt"):
        return data.decode(
            "utf-8",
            errors="ignore"
        )

    raise HTTPException(
        status_code=400,
        detail="الملف يجب أن يكون PDF أو Word أو TXT"
    )


# اللغات

LANGUAGES = {
    "ar": """
اكتب السؤال والإجابة باللغة العربية.
استخدم عربية واضحة وطبيعية ومناسبة للطلاب.
""",

    "en": """
Write both the question and answer in English.
Use clear, natural English suitable for students.
"""
}


# مستويات الأسئلة

DIFFICULTIES = {
    "easy": """
اجعل جميع الأسئلة سهلة.
ركز على التعريفات والمصطلحات والمعلومات المباشرة
والحقائق الواضحة.
لا تجعل السؤال يحتاج إلى تحليل عميق.
""",

    "medium": """
اجعل جميع الأسئلة متوسطة.
اختبر فهم الطالب للمعلومة.
اجعل بعض الأسئلة تحتاج إلى الربط بين المعلومات
وفهم السبب والنتيجة والمقارنة بين المفاهيم.
""",

    "hard": """
اجعل جميع الأسئلة صعبة.
اختبر الفهم العميق والتحليل والاستنتاج
والربط بين عدة معلومات والفروقات الدقيقة.
تجنب الأسئلة المباشرة جدًا.
""",

    "mixed": """
أنشئ مزيجًا متوازنًا من مستويات الأسئلة:
30% سهلة، 40% متوسطة، 30% صعبة.
اجعل المستويات متنوعة بوضوح.
"""
}


# البطاقات السابقة

def get_previous_cards(data):
    if not data:
        return [], ""

    try:
        cards = json.loads(data)
    except json.JSONDecodeError:
        return [], ""

    if not isinstance(cards, list):
        return [], ""

    valid_cards = []
    previous_text = []

    for card in cards:
        if not isinstance(card, dict):
            continue

        question = str(
            card.get("question", "")
        ).strip()

        answer = str(
            card.get("answer", "")
        ).strip()

        if question and answer:
            valid_cards.append({
                "question": question,
                "answer": answer
            })

            previous_text.append(
                f"- السؤال: {question}\n"
                f"  الإجابة: {answer}"
            )

    return valid_cards, "\n".join(
        previous_text
    )


# تحليل استجابة Gemini

def parse_cards(result_text):
    result_text = (
        result_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    cards = []

    try:
        parsed = json.loads(
            result_text
        )

        if isinstance(parsed, list):
            cards = parsed

    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        position = 0

        while position < len(result_text):
            start = result_text.find(
                "{",
                position
            )

            if start == -1:
                break

            try:
                item, end = decoder.raw_decode(
                    result_text[start:]
                )

                if isinstance(item, dict):
                    cards.append(item)

                position = start + end

            except json.JSONDecodeError:
                position = start + 1

    clean_cards = []
    seen = set()

    for card in cards:
        if not isinstance(card, dict):
            continue

        question = str(
            card.get("question", "")
        ).strip()

        answer = str(
            card.get("answer", "")
        ).strip()

        if not question or not answer:
            continue

        key = question.lower()

        if key in seen:
            continue

        seen.add(key)

        clean_cards.append({
            "question": question,
            "answer": answer
        })

    return clean_cards


# منع تكرار البطاقات

def remove_previous_cards(
    cards,
    previous
):
    if not previous:
        return cards

    old_questions = {
        card["question"].strip().lower()
        for card in previous
    }

    old_answers = {
        card["answer"].strip().lower()
        for card in previous
    }

    return [
        card
        for card in cards
        if card["question"].strip().lower()
        not in old_questions
        and card["answer"].strip().lower()
        not in old_answers
    ]


# إنشاء البطاقات

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    difficulty: str = Form("easy"),
    card_count: int = Form(8),
    language: str = Form("ar"),
    previous_cards: str = Form("")
):

    allowed = (
        ".pdf",
        ".docx",
        ".txt"
    )

    filename = (
        file.filename or ""
    ).lower()

    if not filename.endswith(allowed):
        raise HTTPException(
            status_code=400,
            detail="الرجاء اختيار PDF أو Word أو TXT"
        )

    card_count = max(
        1,
        min(card_count, 12)
    )

    language = (
        language
        if language in LANGUAGES
        else "ar"
    )

    difficulty = (
        difficulty
        if difficulty in DIFFICULTIES
        else "easy"
    )

    text = await extract_text(file)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="لم يتم العثور على نص داخل الملف"
        )

    previous, previous_text = (
        get_previous_cards(
            previous_cards
        )
    )

    regeneration = ""

    if previous_text:
        regeneration = f"""
المستخدم يطلب مجموعة جديدة.

هذه البطاقات ظهرت سابقًا:

{previous_text}

ممنوع إعادة أي بطاقة سابقة.

لا تعيد:
- نفس السؤال بصياغة مختلفة.
- نفس الإجابة بصياغة مختلفة.
- نفس المعلومة الأساسية.
- نفس النقطة بطريقة شبه مطابقة.

ابحث عن معلومات ونقاط أخرى من الملف.
حاول زيادة تنوع البطاقات في كل إعادة توليد.
"""

    prompt = f"""
أنت مساعد تعليمي متخصص في إنشاء
بطاقات مراجعة للطلاب.

اقرأ محتوى الملف وأنشئ
{card_count} بطاقات Flashcards.

لغة البطاقات:

{LANGUAGES[language]}

مستوى الأسئلة:

{DIFFICULTIES[difficulty]}

{regeneration}

الشروط:

- كل بطاقة تحتوي على question و answer.
- السؤال واضح ومختصر.
- السؤال لا يتجاوز تقريبًا 12 كلمة.
- اجعل السؤال مناسبًا للعرض داخل بطاقة.
- الإجابة دقيقة ومفيدة.
- اجعل الإجابة من جملة إلى 3 جمل حسب الحاجة.
- لا تحذف معلومة مهمة.
- اعتمد فقط على محتوى الملف.
- لا تضف معلومات من خارج الملف.
- اجعل الأسئلة متنوعة.
- لا تنشئ أسئلة متشابهة.

الإيموجيات:

- أضف إيموجي واحد مناسب لكل سؤال.
- يكون مرتبطًا بموضوع السؤال.
- ضعه في نهاية السؤال.
- لا تستخدم نفس الإيموجي لجميع الأسئلة.

أمثلة لفهم الأسلوب فقط:

{{"question":"ما المقصود بالذكاء الاصطناعي؟ 🤖",
"answer":"مجال يهتم بتطوير أنظمة قادرة على تنفيذ مهام تتطلب عادةً قدرات ذهنية بشرية."}}

{{"question":"ما الفرق بين البيانات والمعلومات؟ 📊",
"answer":"البيانات حقائق خام، بينما المعلومات بيانات تمت معالجتها وأصبح لها معنى."}}

لا تستخدم معلومات الأمثلة.
اعتمد على محتوى الملف فقط.

أرسل JSON Array فقط بهذا الشكل:

[
  {{
    "question": "السؤال 🤖",
    "answer": "الإجابة"
  }}
]

لا تستخدم Markdown.
لا تستخدم ```json.
لا تكتب أي نص خارج JSON.
يجب إنشاء {card_count} بطاقات.

محتوى الملف:

{text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=min(
                    4000,
                    max(
                        1200,
                        card_count * 300
                    )
                )
            )
        )

    except Exception as error:
        print(
            "Gemini Error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="حدث خطأ أثناء الاتصال بـ Gemini"
        )

    cards = parse_cards(
        response.text or ""
    )

    cards = remove_previous_cards(
        cards,
        previous
    )[:card_count]

    if not cards:
        raise HTTPException(
            status_code=400,
            detail="لم يتم العثور على بطاقات جديدة. حاول إعادة التوليد مرة أخرى."
        )

    print(
        f"Cards requested: {card_count} | "
        f"Cards found: {len(cards)} | "
        f"Previous: {len(previous)}"
    )

    async def stream_cards():
        for card in cards:
            yield (
                json.dumps(
                    card,
                    ensure_ascii=False
                )
                + "\n"
            )

            await asyncio.sleep(
                0.15
            )

    return StreamingResponse(
        stream_cards(),
        media_type="application/x-ndjson"
    )


# التشغيل المحلي

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                8000
            )
        )
    )