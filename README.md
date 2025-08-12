Resume Matcher

An AI-powered web app that compares a candidate’s resume against a given Job Description (JD) and provides:

- **Match Percentage**
- **Missing Keywords**
- **Concise HR-style review**

Built as part of a **3-member Mentorship Club project** to help students prepare for campus placements.

---

## 🚀 Features

- **Upload PDF Resume** (supports both editable and scanned PDFs)
- **Paste or Select JD** (includes multiple role presets)
- **ATS Mode:** Match %, missing keywords, final thoughts
- **HR Review Mode:** Strengths & weaknesses from a recruiter’s perspective
- **Fast Mode:** Analyze only the first 2 pages for quick results
- **Downloadable Feedback:** Export ATS results or HR review as `.txt`
- **Error Handling:** Friendly messages for API rate limits and timeouts
- **Hybrid PDF Parsing:** Text-first approach with image fallback for scanned resumes

---

## 🏗️ Tech Stack

| Layer              | Technology / Library                                              |
| ------------------ | ----------------------------------------------------------------- |
| **Frontend**       | Streamlit (UI, layout, widgets)                                   |
| **Backend Logic**  | Python                                                            |
| **AI Model**       | Google Gemini 1.5 Flash                                           |
| **PDF Processing** | PyMuPDF (text extraction), pdf2image + Poppler (image conversion) |
| **Image Handling** | Pillow (PIL)                                                      |
| **Env Management** | python-dotenv                                                     |

---

## 🧩 Architecture Overview

1. **User Input**

   - Upload resume (PDF)
   - Paste JD or choose preset

2. **PDF Ingestion**

   - Try text extraction (fast, cheap)
   - Fallback to image conversion (for scanned/locked PDFs)
   - Limit to first N pages in Fast Mode

3. **Prompt Building**

   - HR Mode → qualitative feedback
   - ATS Mode → strict format output

4. **Model Call**

   - Send resume + JD to Gemini 1.5 Flash
   - Multi-modal (text + images)

5. **Parsing & Display**
   - Extract Match %, Missing Keywords, Final Thoughts
   - Show results in Streamlit with KPI widgets & progress bar

---

## 👥 Team Roles

- **Member A (You)** — Backend & Integration
  - PDF ingestion pipeline
  - Gemini API integration
  - Prompt engineering
  - Output parsing (regex)
  - Error handling & performance optimization
- **Member B** — Frontend UI
  - Streamlit layout, components, tabs
  - User interaction flow
  - Styling & branding
- **Member C** — Deployment & Testing
  - Hosting setup
  - Cross-platform testing
  - UX refinements

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

bash
git clone https://github.com/<your-username>/resume-matcher.git
cd resume-matcher

### 2. Create Virtual Environment

bash
python -m venv .venv

# Activate

# Windows:

.venv\Scripts\activate

# macOS/Linux:

source .venv/bin/activate

### 3. Install Dependencies

bash
pip install -r requirements.txt

### 4. Install Poppler

Windows: Download from Poppler for Windows

Set POPPLER_BIN in .env to the bin folder path

macOS: brew install poppler

Linux: sudo apt install poppler-utils

### 5. Environment Variables

Create .env file:

env
GOOGLE_API_KEY=your_gemini_api_key
POPPLER_BIN=optional_path_for_windows

### 6.▶️ Run Locally

bash
streamlit run app.py
Then open http://localhost:8501 in your browser.
