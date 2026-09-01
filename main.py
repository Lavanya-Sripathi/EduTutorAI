# -*- coding: utf-8 -*-
"""EduTutor AI - Colab-compatible version

Features:
1. Login / Register
2. Concept explanation using IBM Granite 3.3-2B-Instruct
3. English / Hindi language learning
4. MCQ generation from uploaded PDF
5. 5-question topic quiz

Important:
- This version fixes the Gradio error caused by show_copy_button.
- It also avoids passing max_new_tokens into the pipeline constructor.
- The model will use GPU automatically if Colab provides CUDA.
"""

# ============================================================
# 1. INSTALL REQUIRED PACKAGES
# ============================================================

!pip -q install -U PyPDF2 gradio transformers accelerate

# Install bitsandbytes only if you intend to use 4-bit GPU loading.
# It is NOT required for the CPU fallback used below.
!pip -q install -U bitsandbytes


# ============================================================
# 2. IMPORTS
# ============================================================

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import gradio as gr
import torch
import PyPDF2
import re


# ============================================================
# 3. USER DATABASE
# ============================================================

# Keep existing users if the Colab cell is re-run.
if "users_db" not in globals():
    users_db = {
        "student1": "pass123",
        "student2": "abc456"
    }

# Store basic session information.
user_sessions = {}


# ============================================================
# 4. CHECK DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print("=" * 60)
print("Device:", device)

if device == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))
else:
    print("WARNING: CUDA is not available.")
    print("The Granite model will run on CPU and may be slow.")

print("=" * 60)


# ============================================================
# 5. LOAD IBM GRANITE MODEL
# ============================================================

model_name = "ibm-granite/granite-3.3-2b-instruct"

generator = None

try:
    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print("Loading model...")

    # dtype is selected according to available hardware.
    # On CPU, float32 is used.
    # On GPU, float16 is used to reduce memory usage.
    if device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16
        )
        model = model.to("cuda")
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32
        )

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )

    print("✅ Model and tokenizer loaded successfully.")

except Exception as e:
    print("❌ Error loading model/tokenizer:")
    print(e)
    generator = None


# ============================================================
# 6. TEXT GENERATION FUNCTION
# ============================================================

def generate_response(prompt, max_new_tokens=500):
    """
    Generate a response using IBM Granite.
    """

    if generator is None:
        return "❌ Error: Model was not loaded."

    try:
        print("\nGenerating response...")
        print("Prompt:", prompt[:150], "...")

        response = generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            return_full_text=False
        )

        if (
            response
            and isinstance(response, list)
            and len(response) > 0
            and "generated_text" in response[0]
        ):
            answer = response[0]["generated_text"].strip()

            print("✅ Response generated successfully.")

            return answer

        return "❌ Error: Unexpected model response format."

    except Exception as e:
        print("❌ Error during text generation:", e)
        return f"❌ Error during text generation: {e}"


# ============================================================
# 7. CONCEPT UNDERSTANDING
# ============================================================

def concept_understanding(concept):

    if not concept or not concept.strip():
        return "❌ Please enter a concept."

    prompt = f"""
You are EduTutor AI, a helpful teacher.

Explain the following concept to a 15-year-old student:

Concept: {concept}

Use:
1. Simple definition
2. Easy explanation
3. One simple example
4. Real-world application
5. Short summary

Avoid unnecessary technical jargon.
"""

    return generate_response(prompt, max_new_tokens=500)


# ============================================================
# 8. LANGUAGE LEARNING
# ============================================================

def language_learning(language):

    if not language:
        return "❌ Please choose a language."

    prompt = f"""
You are EduTutor AI, a language teacher.

Teach a beginner the basics of {language}.

Include:
1. Parts of speech
2. Basic grammar rules
3. 10 common vocabulary words
4. 5 simple example sentences
5. A short practice exercise

Keep the explanation beginner-friendly.
"""

    return generate_response(prompt, max_new_tokens=600)


# ============================================================
# 9. PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_file):

    if pdf_file is None:
        return ""

    try:
        # Compatible with Gradio versions that return a filepath.
        pdf_path = pdf_file

        # Some Gradio versions may return an object with a .name attribute.
        if hasattr(pdf_file, "name"):
            pdf_path = pdf_file.name

        reader = PyPDF2.PdfReader(pdf_path)

        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        return "\n".join(pages)

    except Exception as e:
        print("PDF extraction error:", e)
        return ""


# ============================================================
# 10. GENERATE TEST FROM PDF
# ============================================================

def generate_test_from_pdf(pdf_file):

    if pdf_file is None:
        return "❌ Please upload a PDF file."

    text = extract_pdf_text(pdf_file)

    if not text.strip():
        return "❌ Could not extract text from the PDF."

    # Prevent an extremely large PDF from creating an enormous prompt.
    text = text[:12000]

    prompt = f"""
You are EduTutor AI.

Create 5 multiple-choice questions from the study material below.

IMPORTANT:
Use exactly this format:

1. Question text
A. Option A
B. Option B
C. Option C
D. Option D
Correct Answer: A

2. Question text
A. Option A
B. Option B
C. Option C
D. Option D
Correct Answer: B

Continue until there are 5 questions.

Study material:
{text}
"""

    return generate_response(prompt, max_new_tokens=800)


# ============================================================
# 11. QUIZ GENERATOR
# ============================================================

def quiz_generator(topic):

    if not topic or not topic.strip():
        return "❌ Please enter a quiz topic."

    prompt = f"""
You are EduTutor AI.

Create exactly 5 multiple-choice questions about:

Topic: {topic}

Use exactly this format:

1. Question text
A. Option A
B. Option B
C. Option C
D. Option D
Correct Answer: A

2. Question text
A. Option A
B. Option B
C. Option C
D. Option D
Correct Answer: B

Continue until there are exactly 5 questions.

Do not add explanations.
"""

    return generate_response(prompt, max_new_tokens=800)


# ============================================================
# 12. AUTHENTICATION
# ============================================================

def authenticate(username, password):

    return (
        username in users_db
        and users_db[username] == password
    )


def register_user(new_username, new_password):

    if not new_username or not new_username.strip():
        return "❌ Please enter a username."

    if not new_password:
        return "❌ Please enter a password."

    new_username = new_username.strip()

    if new_username in users_db:
        return "❌ Username already exists!"

    users_db[new_username] = new_password

    return "✅ User registered successfully. You can now login."


# ============================================================
# 13. LOGIN FUNCTION
# ============================================================

def login_fn(user, pwd):

    if authenticate(user, pwd):

        user_sessions[user] = []

        return (
            gr.update(visible=True),
            gr.update(value="✅ Login successful. Welcome!"),
            user
        )

    return (
        gr.update(visible=False),
        gr.update(value="❌ Invalid username or password!"),
        ""
    )


# ============================================================
# 14. RUN CLASSROOM FUNCTIONS
# ============================================================

def run_concept_language_pdf(
    username,
    concept,
    language,
    pdf_file
):

    if not username:
        return (
            "❌ Please login first.",
            "❌ Please login first.",
            "❌ Please login first."
        )

    if username not in user_sessions:
        user_sessions[username] = []

    concept_output = concept_understanding(concept)

    language_output = language_learning(language)

    test_pdf_output = generate_test_from_pdf(pdf_file)

    return (
        concept_output,
        language_output,
        test_pdf_output
    )


# ============================================================
# 15. TOPIC QUIZ FUNCTION
# ============================================================

def run_quiz_generation(quiz_topic):

    return quiz_generator(quiz_topic)


# ============================================================
# 16. GRADIO USER INTERFACE
# ============================================================

with gr.Blocks(title="EduTutor AI") as interface:

    gr.Markdown(
        """
        # 👩‍🏫 EduTutor AI
        ### Personalized Learning Platform
        """
    )

    username_state = gr.State("")


    # ========================================================
    # LOGIN TAB
    # ========================================================

    with gr.Tab("Login"):

        login_user = gr.Textbox(
            label="Username",
            placeholder="Enter username"
        )

        login_pwd = gr.Textbox(
            label="Password",
            type="password",
            placeholder="Enter password"
        )

        login_status = gr.Textbox(
            label="Status"
        )

        login_button = gr.Button("🔐 Login")


    # ========================================================
    # REGISTER TAB
    # ========================================================

    with gr.Tab("Register"):

        new_user = gr.Textbox(
            label="New Username"
        )

        new_pwd = gr.Textbox(
            label="New Password",
            type="password"
        )

        register_button = gr.Button("📝 Register")

        registration_status = gr.Textbox(
            label="Registration Status"
        )

        register_button.click(
            fn=register_user,
            inputs=[
                new_user,
                new_pwd
            ],
            outputs=registration_status
        )


    # ========================================================
    # CLASSROOM TAB
    # ========================================================

    with gr.Tab("Classroom"):

        with gr.Column(visible=False) as app_ui:

            gr.Markdown(
                """
                ## 📚 Learning Classroom

                Enter a concept, choose a language, or upload
                study material as a PDF.
                """
            )

            concept = gr.Textbox(
                label="Enter Concept",
                placeholder="Example: Generative AI"
            )

            language = gr.Radio(
                choices=["English", "Hindi"],
                label="Choose Language"
            )

            pdf = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath"
            )

            run_btn = gr.Button(
                "🚀 Run Concept, Language, and PDF Test"
            )

            # IMPORTANT:
            # show_copy_button=True was removed because your
            # installed Gradio version does not support it.

            concept_out = gr.Textbox(
                label="Concept Explanation",
                lines=12
            )

            language_out = gr.Textbox(
                label="Language Learning",
                lines=12
            )

            test_out = gr.Textbox(
                label="Generated Test from PDF",
                lines=20
            )

            run_btn.click(
                fn=run_concept_language_pdf,
                inputs=[
                    username_state,
                    concept,
                    language,
                    pdf
                ],
                outputs=[
                    concept_out,
                    language_out,
                    test_out
                ]
            )


            # =================================================
            # QUIZ GENERATION
            # =================================================

            gr.Markdown("## 📝 Quiz Generation")

            quiz_topic_input = gr.Textbox(
                label="Enter Topic for Quiz",
                placeholder="Example: Python Loops"
            )

            generate_quiz_btn = gr.Button(
                "🎯 Generate Quiz"
            )

            quiz_output = gr.Textbox(
                label="Generated Quiz",
                lines=20
            )

            generate_quiz_btn.click(
                fn=run_quiz_generation,
                inputs=[quiz_topic_input],
                outputs=[quiz_output]
            )


    # ========================================================
    # LOGIN EVENT
    # ========================================================

    login_button.click(
        fn=login_fn,
        inputs=[
            login_user,
            login_pwd
        ],
        outputs=[
            app_ui,
            login_status,
            username_state
        ]
    )


# ============================================================
# 17. LAUNCH
# ============================================================

print("\n🚀 Starting EduTutor AI...")

interface.launch(
    debug=True,
    share=True
)
