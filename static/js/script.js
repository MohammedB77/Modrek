const fileInput = document.getElementById("fileInput");
const chooseButton = document.getElementById("chooseButton");
const selectedFileElement = document.getElementById("selectedFile");
const generateButton = document.getElementById("generateButton");
const regenerateButton = document.getElementById("regenerateButton");
const fileInfo = document.getElementById("fileInfo");
const flashcardsSection = document.getElementById("flashcardsSection");
const flashcardsStatus = document.getElementById("flashcardsStatus");
const flashcards = document.getElementById("flashcards");

let selectedFile = null;
let selectedDifficulty = "easy";
let selectedCardCount = 8;
let selectedLanguage = "ar";
let allGeneratedCards = [];


// اختيار الملف

chooseButton.addEventListener("click", () => {
    fileInput.click();
});


// عند اختيار ملف

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) return;

    const allowedTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ];

    const allowedExtensions = [
        ".pdf",
        ".docx",
        ".txt"
    ];

    const extension =
        "." + file.name.split(".").pop().toLowerCase();

    if (
        !allowedTypes.includes(file.type) &&
        !allowedExtensions.includes(extension)
    ) {
        fileInput.value = "";
        selectedFile = null;

        selectedFileElement.textContent = "";

        generateButton.disabled = true;

        regenerateButton.style.display = "none";

        fileInfo.textContent =
            "الرجاء اختيار ملف PDF أو Word أو TXT فقط";

        return;
    }

    selectedFile = file;
    allGeneratedCards = [];

    const icons = {
        ".pdf": "📄",
        ".docx": "📝",
        ".txt": "📃"
    };

    selectedFileElement.textContent =
        `${icons[extension] || "📄"} ${file.name}`;

    fileInfo.textContent =
        "تم اختيار الملف";

    generateButton.disabled = false;

    regenerateButton.style.display = "none";
});


// مستوى الأسئلة

document.querySelectorAll(".difficulty").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelectorAll(".difficulty")
            .forEach(btn => {
                btn.classList.remove("active");
            });

        button.classList.add("active");

        selectedDifficulty =
            button.dataset.level;
    });

});


// لغة البطاقات

document.querySelectorAll(".language").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelectorAll(".language")
            .forEach(btn => {
                btn.classList.remove("active");
            });

        button.classList.add("active");

        selectedLanguage =
            button.dataset.language;
    });

});


// عدد البطاقات

document.querySelectorAll(".card-count").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelectorAll(".card-count")
            .forEach(btn => {
                btn.classList.remove("active");
            });

        button.classList.add("active");

        selectedCardCount =
            Number(button.dataset.count);
    });

});


// إنشاء البطاقات

generateButton.addEventListener("click", () => {
    generateCards(false);
});


// إعادة التوليد

regenerateButton.addEventListener("click", () => {
    generateCards(true);
});


// توليد البطاقات

async function generateCards(isRegenerate = false) {

    if (!selectedFile) {
        fileInfo.textContent =
            "اختر الملف أولًا";

        return;
    }

    generateButton.disabled = true;
    regenerateButton.disabled = true;

    generateButton.textContent =
        isRegenerate
            ? "جاري إعادة التوليد..."
            : "جاري الإنشاء...";

    fileInfo.textContent =
        isRegenerate
            ? "جاري البحث عن أسئلة جديدة..."
            : "جاري تحليل الملف وإنشاء البطاقات...";

    flashcards.innerHTML = "";

    flashcardsSection.classList.add("visible");

    flashcardsStatus.textContent =
        isRegenerate
            ? "جاري إنشاء مجموعة جديدة..."
            : "جاري إنشاء بطاقات المراجعة...";

    setTimeout(() => {

        flashcardsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 100);


    const formData = new FormData();

    formData.append(
        "file",
        selectedFile
    );

    formData.append(
        "difficulty",
        selectedDifficulty
    );

    formData.append(
        "card_count",
        selectedCardCount
    );

    formData.append(
        "language",
        selectedLanguage
    );


    if (isRegenerate) {

        formData.append(
            "previous_cards",
            JSON.stringify(allGeneratedCards)
        );

    }


    try {

        const response = await fetch(
            "/upload",
            {
                method: "POST",
                body: formData
            }
        );


        if (!response.ok) {

            let message =
                "حدث خطأ أثناء إنشاء البطاقات";

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    message =
                        errorData.detail;
                }

            } catch {}

            throw new Error(message);
        }


        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder("utf-8");

        let buffer = "";
        let newCards = [];


        while (true) {

            const {
                value,
                done
            } = await reader.read();


            if (done) break;


            buffer += decoder.decode(
                value,
                {
                    stream: true
                }
            );


            const lines =
                buffer.split("\n");

            buffer = lines.pop();


            for (const line of lines) {

                const cleanLine =
                    line.trim();

                if (!cleanLine) continue;


                try {

                    const card =
                        JSON.parse(cleanLine);


                    if (
                        !card.question ||
                        !card.answer
                    ) {
                        continue;
                    }


                    newCards.push(card);

                    allGeneratedCards.push(card);


                    createFlashcard(
                        card,
                        newCards.length
                    );


                    flashcardsStatus.textContent =
                        `تم إنشاء ${newCards.length} من ${selectedCardCount} بطاقة`;


                } catch (error) {

                    console.error(
                        "JSON Error:",
                        error
                    );
                }

            }
        }


        // آخر بطاقة

        if (buffer.trim()) {

            try {

                const card =
                    JSON.parse(
                        buffer.trim()
                    );


                if (
                    card.question &&
                    card.answer
                ) {

                    newCards.push(card);

                    allGeneratedCards.push(card);


                    createFlashcard(
                        card,
                        newCards.length
                    );

                }

            } catch (error) {

                console.error(
                    "Final JSON Error:",
                    error
                );
            }
        }


        if (!newCards.length) {

            flashcardsStatus.textContent =
                "لم يتم إنشاء بطاقات جديدة";

            fileInfo.textContent =
                "لم يتم العثور على أسئلة جديدة. حاول إعادة التوليد مرة أخرى.";

        } else {

            flashcardsStatus.textContent =
                `تم إنشاء ${newCards.length} بطاقة جديدة`;

            fileInfo.textContent =
                isRegenerate
                    ? "تم إنشاء مجموعة جديدة من أسئلة مختلفة"
                    : `تم إنشاء ${newCards.length} بطاقة بنجاح`;

            regenerateButton.style.display =
                "inline-block";
        }


    } catch (error) {

        console.error(error);

        flashcardsStatus.textContent =
            "حدث خطأ أثناء إنشاء البطاقات";

        fileInfo.textContent =
            error.message ||
            "حدث خطأ أثناء إنشاء البطاقات";

        regenerateButton.style.display =
            "none";


    } finally {

        generateButton.disabled = false;

        regenerateButton.disabled = false;

        generateButton.textContent =
            "إنشاء البطاقات";

        regenerateButton.textContent =
            "🔄 إعادة توليد";
    }
}


// إنشاء الكرت

function createFlashcard(card, index) {

    const cardElement =
        document.createElement("div");

    cardElement.className =
        "flashcard";


    cardElement.innerHTML = `

        <div class="flashcard-inner">

            <div class="flashcard-front">

                <span class="card-number">
                    بطاقة ${index}
                </span>

                <div class="question-icon">
                    ؟
                </div>

                <h3>
                    ${escapeHTML(card.question)}
                </h3>

                <small>
                    اضغط لمعرفة الإجابة
                </small>

            </div>


            <div class="flashcard-back">

                <span class="card-number">
                    الإجابة
                </span>

                <div class="answer-icon">
                    ✓
                </div>

                <p>
                    ${escapeHTML(card.answer)}
                </p>

                <small>
                    اضغط للعودة للسؤال
                </small>

            </div>

        </div>
    `;


    cardElement.addEventListener(
        "click",
        () => {

            cardElement.classList.toggle(
                "flipped"
            );

        }
    );


    flashcards.appendChild(
        cardElement
    );


    setTimeout(() => {

        cardElement.classList.add(
            "show"
        );

    }, 60);
}


// حماية النص

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}