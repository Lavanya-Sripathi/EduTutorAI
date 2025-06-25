# 🧠 EduTutor AI: Personalized Learning with Generative AI and LMS Integration

**EduTutor AI** is a personalized learning assistant that uses the power of **IBM Granite 3.3-2B Instruct LLM (via Hugging Face)** to enhance the education experience. Developed as part of an internship project, this app provides interactive tutoring, language learning, and automated assessment generation from PDFs — all integrated into a simple **Gradio-based user interface**.

---

## 🚀 Features

🔐 **User Authentication**

* Simple login and registration system to manage student sessions.

📘 **Concept Understanding**

* Enter any topic (e.g., "Photosynthesis", "Generative AI") and receive age-appropriate, easy-to-understand explanations with examples.

🌍 **Language Learning Support**

* Choose a language (currently supports **English** and **Hindi**) and get a tailored introduction with grammar, vocabulary, and usage tips.

📄 **Test Generator from PDF**

* Upload educational PDFs and get auto-generated **multiple-choice questions (MCQs)** formatted for use in quizzes and exams.

🧪 **Custom Quiz Generator**

* Enter a topic (e.g., "World War II") and receive a full 5-question quiz with options and correct answers.

---

## 🛠️ Tech Stack

* **Python**
* **Hugging Face Transformers** (`ibm-granite/granite-3.3-2b-instruct`)
* **Gradio** (UI)
* **PyPDF2** (for PDF parsing)
* **Torch** (for LLM inference)

---

## 📂 File Overview

* `main.py`: Core application logic (Gradio interface, AI functionalities, quiz/test generator)
* `requirements.txt`: List of required Python packages
* `README.md`: Project overview and instructions

---

## 📦 Installation

```bash
git clone https://github.com/Lavanya-Sripathi/EduTutorAI

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
python main.py
```

Or open in **Google Colab** if you’re using a hosted environment.

---

## 🤖 Model Information

This project uses:

* **IBM Granite 3.3B Instruct** — an instruction-tuned LLM optimized for educational and question-answering tasks.
* Hosted via **Hugging Face**, used with authentication token.

---

## 📚 Example Prompts

* `"Explain Newton’s laws in a way a teenager would understand."`
* `"Generate 5 MCQs from this uploaded PDF on World History."`
* `"Teach me the basics of Hindi language including grammar and common words."`

---

## 🌐 LMS Integration (Future Scope)

In the future, EduTutor AI aims to:

* Connect with platforms like **Moodle or Google Classroom**
* Track student progress
* Adapt responses based on user learning history

---

## 👩‍💻 Developed By

    Lavanya Sripathi


