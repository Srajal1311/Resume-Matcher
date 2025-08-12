# app.py

from dotenv import load_dotenv
load_dotenv()

import os
import io
import re
import base64
import streamlit as st
from PIL import Image  # noqa: F401
import pdf2image
import google.generativeai as genai

# ----------------- Streamlit page config -----------------
st.set_page_config(page_title="Sahyog ATS — Resume Matcher", page_icon="🧭", layout="wide")

# Ensure session key exists before widgets
if "jd" not in st.session_state:
    st.session_state["jd"] = ""

# ----------------- Sidebar -----------------
with st.sidebar:
    st.markdown("### 🧭 Sahyog ATS")
    st.caption("AI-powered resume matching for placement prep.")
    st.divider()

    # Optional presets to speed up testing
    preset = st.selectbox(
        "Sample Job Description",
        ["— None —", "Data Engineer (Preset)", "Data Scientist (Preset)", "Cook (Preset)", "SDE (Preset)"],
        index=0,
    )

    st.divider()
    st.caption("Built for Sahyog Mentorship Club • NIT Raipur")

# ----------------- Gemini API setup -----------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ----------------- Helpers -----------------
def input_pdf_setup(uploaded_file, dpi=150):
    """
    Convert ALL PDF pages to Gemini-compatible image parts.
    Uses POPPLER_BIN env var if set; otherwise relies on system PATH.
    Returns (parts, page_count).
    """
    poppler_bin = os.getenv("POPPLER_BIN")  # e.g., r"C:\poppler-25.08.0\Library\bin"
    poppler_path = poppler_bin or None

    images = pdf2image.convert_from_bytes(
        uploaded_file.read(),
        poppler_path=poppler_path,
        dpi=dpi,  # moderate DPI for speed + readability
    )
    parts = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        parts.append({
            "mime_type": "image/jpeg",
            "data": base64.b64encode(buf.getvalue()).decode("utf-8")
        })
    return parts, len(images)


def get_gemini_response(system_prompt: str, pdf_parts: list, job_description: str) -> str:
    """
    Compose multi-part prompt (system + images + JD) and call Gemini.
    """
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"max_output_tokens": 512},
    )
    content = [system_prompt] + pdf_parts + [f"Job Description:\n{job_description.strip()}"]
    try:
        resp = model.generate_content(content, request_options={"timeout": 45})
        return (getattr(resp, "text", "") or "").strip()
    except Exception as e:
        msg = str(e)
        if "429" in msg or "quota" in msg.lower():
            return "ERROR: Rate limit hit (free tier). Please wait for daily reset or try later."
        if "timeout" in msg.lower() or "deadline" in msg.lower():
            return "ERROR: Request timed out. Try again or reduce pages."
        return f"ERROR: {e}"

# ----------------- Header -----------------
st.markdown(
    """
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
      <span style="font-size:28px;font-weight:700">Sahyog ATS — Resume Matcher</span>
      <span style="background:#eef6ff;color:#1266f1;border:1px solid #d6e8ff;padding:2px 8px;border-radius:999px;font-size:12px">
        Beta
      </span>
    </div>
    <div style="color:#666;margin-bottom:10px">Compare any PDF resume against a job description and get a match score, missing keywords, and feedback.</div>
    """,
    unsafe_allow_html=True,
)

# ----------------- JD presets -----------------
preset_map = {
    "Data Engineer (Preset)": (
        "We are seeking a Data Engineer to design and maintain scalable ETL/ELT pipelines, "
        "integrate data from multiple sources, and build data lakes/warehouses. Must have strong SQL, Python, "
        "and experience with Spark or similar big data tools. Cloud (AWS/GCP/Azure) experience preferred; "
        "data modeling and governance required."
    ),
    "Data Scientist (Preset)": (
        "Looking for a Data Scientist skilled in ML, statistics, and visualization. Build predictive models, "
        "perform EDA, and communicate insights. Proficient in Python (pandas, numpy, scikit-learn), SQL; "
        "cloud experience is a plus."
    ),
    "Cook (Preset)": (
        "Seeking a Cook to prepare and present meals per recipes, maintain kitchen hygiene, manage inventory, "
        "and ensure food safety. Prior experience as Cook/Line Cook preferred; ability to work in fast-paced environment required."
    ),
    "SDE (Preset)": (
        "We are hiring a Software Development Engineer to design, build, and maintain scalable services. Strong DSA, "
        "proficiency in Java/C++/Python, understanding of OOP, REST APIs, and version control. Exposure to cloud and CI/CD is a plus."
    ),
}

# ----------------- Clear JD callback -----------------
def clear_jd():
    st.session_state["jd"] = ""

# ----------------- Inputs -----------------
left, right = st.columns([2, 1])
with left:
    input_text = st.text_area(
        "Job Description",
        value=(preset_map.get(preset) if preset in preset_map else st.session_state.get("jd", "")),
        placeholder="Paste the JD here…",
        key="jd",
    )
with right:
    st.write("")  # spacing
    st.write("")
    st.button("Clear JD", on_click=clear_jd)

uploaded_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])
if uploaded_file is not None:
    st.success("PDF uploaded successfully.")
else:
    st.info("Upload a PDF resume to begin.")

# ----------------- Tabs -----------------
tab_review, tab_match = st.tabs(["💬 HR Review", "📊 ATS Match"])

input_prompt1 = (
    "You are an experienced Technical HR Manager. Review the provided resume "
    "against the job description. Explain whether the candidate aligns with the role, "
    "highlighting strengths and weaknesses relative to the requirements. Be concise and actionable."
)

input_prompt3 = (
    "You are an ATS scanner with a strong understanding of data roles and ATS behavior. "
    "Evaluate the resume against the job description and output ONLY in this format:\n\n"
    "Match: <percent>%\n"
    "Missing Keywords: <comma-separated list>\n"
    "Final Thoughts: <2-4 concise bullets>"
)

# ----------------- Tab 1: HR Review -----------------
with tab_review:
    run_review = st.button("Run HR Review", key="run_review")
    if run_review:
        if not uploaded_file:
            st.warning("Please upload the resume (PDF).")
        elif not input_text.strip():
            st.warning("Please paste the Job Description.")
        else:
            with st.spinner("Analyzing resume vs JD…"):
                try:
                    pdf_content, pages = input_pdf_setup(uploaded_file)
                    st.caption(f"Analyzing **{pages}** page(s)…")
                    response_text = get_gemini_response(input_prompt1, pdf_content, input_text)
                except Exception as e:
                    response_text = f"ERROR: {e}"

            st.subheader("Review")
            if response_text.startswith("ERROR:"):
                st.error(response_text)
            elif response_text:
                st.markdown(response_text)
            else:
                st.info("No response returned from Gemini.")

# ----------------- Tab 2: ATS Match -----------------
with tab_match:
    fast_mode = st.toggle("⚡ Fast mode (limit to first 2 pages)", value=True, key="fast_mode")
    run_match = st.button("Run ATS Match", key="run_match")

    if run_match:
        if not uploaded_file:
            st.warning("Please upload the resume (PDF).")
        elif not input_text.strip():
            st.warning("Please paste the Job Description.")
        else:
            with st.spinner("Computing ATS match…"):
                try:
                    max_pages = 2 if fast_mode else 6
                    full_parts, total_pages = input_pdf_setup(uploaded_file)
                    pdf_parts = full_parts[:max_pages]
                    st.caption(f"Analyzing **{min(total_pages, max_pages)}** of {total_pages} page(s)…")
                    response_text = get_gemini_response(input_prompt3, pdf_parts, input_text)
                except Exception as e:
                    response_text = f"ERROR: {e}"

            st.subheader("ATS Match Result")
            if response_text.startswith("ERROR:"):
                st.error(response_text)
            elif response_text:
                m = re.search(r"(\d{1,3})\s*%", response_text)
                percent = int(m.group(1)) if m else 0
                percent = max(0, min(percent, 100))

                kpi1, kpi2 = st.columns([1, 3])
                with kpi1:
                    st.metric("Match", f"{percent}%")
                with kpi2:
                    st.progress(percent / 100)

                mk = re.search(r"(Missing\s*Keywords[:\-]?\s*)(.*)", response_text, flags=re.I | re.S)
                ft = re.search(r"(Final\s*Thoughts[:\-]?\s*)(.*)", response_text, flags=re.I | re.S)

                if mk:
                    st.markdown("**Missing Keywords**")
                    mk_text = mk.group(2).strip()
                    if ft:
                        mk_text = mk_text.split(ft.group(1), 1)[0].strip()
                    st.markdown(mk_text or "_None detected_")

                if ft:
                    st.markdown("**Final Thoughts**")
                    st.markdown(ft.group(2).strip())
            else:
                st.info("No response returned from Gemini.")

# ----------------- Footer -----------------
st.divider()
st.caption("© Sahyog Mentorship Club • Built for placement readiness.")
