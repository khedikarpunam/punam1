import os
import streamlit as st
from groq import Groq

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="AI Health Triage Assistant", page_icon="🏥", layout="centered")

# Retrieve API Key from Streamlit Secrets or Environment Variables
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

# Offer sidebar input for manual override/fallback if key is not configured
sidebar_key = st.sidebar.text_input(
    "🔑 Enter Groq API Key (Optional fallback):",
    value="",
    type="password",
    help="Use this to run the app if you haven't configured the Streamlit Secrets yet."
)

if sidebar_key:
    api_key = sidebar_key

# Check if the API key exists. If not, show instructions and stop execution cleanly.
if not api_key:
    st.title("🏥 AI Health Triage Assistant")
    st.error("### 🔑 Groq API Key is Missing")
    st.markdown(
        """
        To run this application, a **Groq API Key** is required.
        
        ### How to fix this:
        
        #### Option 1: Streamlit Cloud Settings (Recommended for deployment)
        1. Open your app dashboard on [Streamlit Cloud](https://share.streamlit.io).
        2. Click on **Manage App** (bottom right) -> click the three dots icon -> select **Settings**.
        3. Go to **Secrets** and add your key:
           ```toml
           GROQ_API_KEY = "your-actual-groq-api-key"
           ```
        4. Save, and Streamlit will automatically restart the app with your secret active.
        
        #### Option 2: Local Development
        Create a file named `.streamlit/secrets.toml` in your project folder, and add:
        ```toml
        GROQ_API_KEY = "your-actual-groq-api-key"
        ```
        
        #### Option 3: Quick Test (Direct Input)
        Enter your Groq API key in the **sidebar input field** on the left to start using the app immediately.
        """
    )
    st.stop()

# Initialize Groq client
client = Groq(api_key=api_key)

TEXT_MODEL = "llama-3.3-70b-versatile"

RED_FLAG_KEYWORDS = [
    "chest pain", "difficulty breathing", "can't breathe", "cannot breathe",
    "unconscious", "fainted", "severe bleeding", "heavy bleeding",
    "blue lips", "seizure", "convulsion", "paralysis", "slurred speech",
    "severe head injury", "suicidal", "poisoning", "high fever for more than 5 days",
    "coughing blood", "vomiting blood"
]

LANGUAGE_OPTIONS = {
    "English": "Respond in simple English.",
    "मराठी": "Respond fully in Marathi language, using simple everyday words, not heavy medical jargon.",
    "हिंदी": "Respond fully in Hindi language, using simple everyday words, not heavy medical jargon.",
}

# ─────────────────────────────────────────────
# SESSION STATE (controls which "screen" is shown)
# ─────────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "result" not in st.session_state:
    st.session_state.result = None

def go_back():
    st.session_state.submitted = False
    st.session_state.result = None

# ─────────────────────────────────────────────
# LLM CALLS
# ─────────────────────────────────────────────
def call_llm(prompt):
    chat = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return chat.choices[0].message.content


def check_valid_symptom_input(symptoms):
    """Reject obviously non-medical input (e.g. 'pizza', 'car')."""
    prompt = f"""You are an input validator for a health triage tool.
Decide if the following text describes real human physical/medical symptoms.

Input: "{symptoms}"

Reply with ONLY one word: VALID or INVALID.
VALID = describes any bodily symptom, discomfort, pain, illness sign, even if vague.
INVALID = unrelated text, random words, objects, food items, nonsense, or anything not describing a health symptom."""
    result = call_llm(prompt).strip().upper()
    return "VALID" in result


def detect_red_flag(symptoms, history):
    text = f"{symptoms} {history}".lower()
    for kw in RED_FLAG_KEYWORDS:
        if kw in text:
            return True
    prompt = f"""Patient symptoms: {symptoms}
Medical history: {history}

Does this describe a medical EMERGENCY needing immediate hospital care
(e.g. severe chest pain, breathing difficulty, unconsciousness, heavy bleeding,
stroke signs, severe allergic reaction, suicidal intent)?
Reply with ONLY one word: YES or NO."""
    result = call_llm(prompt).strip().upper()
    return "YES" in result


def get_doctor_opinion(stance, patient_info, lang_instruction):
    if stance == "risk":
        persona = ("You are Doctor 1, a CAREFUL physician who pays close attention to detail. "
                   "You recommend an in-person doctor visit ONLY if the symptoms are unusually "
                   "severe, last longer than is typical for a common illness, are worsening, "
                   "or combine in an unusual way that could suggest something more serious. "
                   "For ordinary, mild, short-duration symptoms (like a few days of mild fever, "
                   "common cold, mild cough, mild headache), you agree that home care is reasonable. "
                   "You do not name a specific disease.")
    else:
        persona = ("You are Doctor 2, a REASSURING, evidence-based physician. "
                   "You look for signs that this is a common, mild, self-limiting condition that "
                   "can be safely managed at home. You do not name a specific disease.")

    prompt = f"""{persona}

IMPORTANT: Most everyday symptoms (mild fever, common cold, mild headache, mild body ache,
mild cough, lasting only a few days, with no severe or unusual signs) are NORMAL and do NOT
need an in-person doctor visit. Reserve "Visit a doctor" only for symptoms that are genuinely
severe, persistent beyond a typical illness duration, rapidly worsening, or unusual in
combination.

Patient details: {patient_info}

Based on these symptoms, give:
1. Your stance: either "Visit a doctor" or "Home care is likely fine"
2. 2-3 short sentences explaining your reasoning (no specific disease names, talk about symptom patterns only)

{lang_instruction}
Keep it short and in plain, non-technical language a common person can understand."""
    return call_llm(prompt)


def get_judge_verdict(patient_info, doc1_opinion, doc2_opinion, lang_instruction):
    prompt = f"""You are a Senior Triage Judge reviewing two doctors' opinions for the same patient.
You are balanced and evidence-based — you do not default to "visit a doctor" just because
one doctor is cautious. You weigh both opinions on their merit, considering how common,
mild, and short-lived the symptoms are.

Patient details: {patient_info}

Doctor 1 (careful) said: {doc1_opinion}
Doctor 2 (reassuring) said: {doc2_opinion}

Give your output in EXACTLY this structure, plain text, no markdown symbols:

VERDICT: [either "Visit a doctor" or "Home care is likely sufficient"]
CONFIDENCE: [a number 0-100 representing how much the two doctors agree]
REASONING: [2-3 sentences summarizing why, referring to both doctors' points]
PRECAUTIONS: [2-3 short bullet-style tips for what to do right now, separated by " | "]
PREVENTION: [2-3 short bullet-style tips to avoid this in future, separated by " | "]

Do NOT name any specific disease. Do not give medicine names or dosages.
{lang_instruction}
Keep language simple for a common person, not medical jargon."""
    return call_llm(prompt)


def parse_verdict(raw_text):
    """Very simple parser for the structured judge output."""
    data = {"VERDICT": "", "CONFIDENCE": "70", "REASONING": "", "PRECAUTIONS": "", "PREVENTION": ""}
    for line in raw_text.splitlines():
        for key in data:
            if line.upper().startswith(key + ":"):
                data[key] = line.split(":", 1)[1].strip()
    return data


# ─────────────────────────────────────────────
# SCREEN 1 — INPUT FORM
# ─────────────────────────────────────────────
def render_input_screen():
    st.title("🏥 AI Health Triage Assistant")
    st.caption("Two AI doctors review your symptoms — a judge gives the final guidance")

    st.warning(
        "**For awareness only — this is NOT a medical diagnosis.** "
        "This tool does not replace a doctor. In an emergency, seek immediate medical care.",
        icon="⚠️"
    )

    st.markdown("### 👤 Patient Details")

    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name:")
            age = st.number_input("Age:", min_value=1, max_value=120, value=25)
        with col2:
            gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
            duration = st.text_input("Symptom Duration:", placeholder="e.g. 3 days")

        language = st.selectbox("Language for result:", list(LANGUAGE_OPTIONS.keys()))

        medical_history = st.text_area(
            "Medical History:", placeholder="e.g. Diabetic, Blood pressure patient... (or leave blank)"
        )
        symptoms = st.text_area(
            "Symptoms:", placeholder="e.g. fever, headache, vomiting..."
        )

        photo = st.file_uploader(
            "Photo (optional) — e.g. rash, swelling, insect bite",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button("Start Diagnosis Debate", type="primary", use_container_width=True)

    if photo:
        st.info("Photo support is a planned future addition for this version — "
                "your text symptoms above will be used for this analysis.")

    if submitted:
        if not name or not symptoms:
            st.error("Please enter Patient Name and Symptoms!")
            return

        patient_info = (f"Name: {name}, Age: {age}, Gender: {gender}, "
                         f"Duration: {duration}, Medical History: {medical_history}, "
                         f"Symptoms: {symptoms}")
        lang_instruction = LANGUAGE_OPTIONS[language]

        with st.spinner("Checking input..."):
            if not check_valid_symptom_input(symptoms):
                st.error("Please enter valid medical symptoms (e.g. fever, headache, cough). "
                          "The text entered doesn't look like a health symptom.")
                return

        with st.spinner("Screening for emergency signs..."):
            is_emergency = detect_red_flag(symptoms, medical_history)

        if is_emergency:
            st.session_state.result = {"emergency": True}
            st.session_state.submitted = True
            st.rerun()
            return

        with st.spinner("Doctor 1 (careful) is analyzing..."):
            doc1 = get_doctor_opinion("risk", patient_info, lang_instruction)
        with st.spinner("Doctor 2 (reassuring) is analyzing..."):
            doc2 = get_doctor_opinion("calm", patient_info, lang_instruction)
        with st.spinner("Judge is reviewing both opinions..."):
            verdict_raw = get_judge_verdict(patient_info, doc1, doc2, lang_instruction)

        st.session_state.result = {
            "emergency": False,
            "doc1": doc1,
            "doc2": doc2,
            "verdict": parse_verdict(verdict_raw),
        }
        st.session_state.submitted = True
        st.rerun()


# ─────────────────────────────────────────────
# SCREEN 2 — RESULT
# ─────────────────────────────────────────────
def render_result_screen():
    st.button("← New diagnosis", on_click=go_back)

    result = st.session_state.result

    if result.get("emergency"):
        st.error(
            "🚨 **This needs in-person care.**\n\n"
            "The symptoms described may be serious or outside this tool's scope. "
            "Please visit a doctor or hospital immediately. Do not rely on this tool for emergencies.",
            icon="🚨"
        )
        return

    v = result["verdict"]
    is_visit_doctor = "visit" in v["VERDICT"].lower()

    # ---- STEP 1: Two doctors' opinions ----
    st.markdown("### 🥊 Step 1 — Two Doctors Give Their Opinion")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔴 Doctor 1 — Careful view")
        st.write(result["doc1"])
    with col2:
        st.markdown("#### 🔵 Doctor 2 — Reassuring view")
        st.write(result["doc2"])

    st.divider()

    # ---- STEP 2: Judge's verdict ----
    st.markdown("### ⚖️ Step 2 — Judge Reviews Both Opinions")
    st.caption("The Judge agent reads both doctors' opinions above and decides the final guidance.")

    with st.container(border=True):
        if is_visit_doctor:
            st.error(f"🔴 **Judge's Verdict: {v['VERDICT']}**")
        else:
            st.success(f"🟢 **Judge's Verdict: {v['VERDICT']}**")

        try:
            conf = int("".join(c for c in v["CONFIDENCE"] if c.isdigit()) or "70")
        except ValueError:
            conf = 70
        conf = min(max(conf, 0), 100)

        if conf >= 70:
            agreement_note = "✅ Both doctors mostly agreed — the Judge is fairly confident."
        elif conf >= 45:
            agreement_note = "⚖️ Doctors partly disagreed — the Judge weighed both sides."
        else:
            agreement_note = "⚠️ Doctors disagreed significantly — the Judge leaned cautious."

        st.metric("Judge's confidence (based on doctor agreement)", f"{conf}%")
        st.progress(conf / 100)
        st.caption(agreement_note)

        st.markdown("**Judge's reasoning:** " + v["REASONING"])

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 💧 Precautions (right now)")
        for tip in v["PRECAUTIONS"].split("|"):
            if tip.strip():
                st.markdown(f"- {tip.strip()}")
    with col4:
        st.markdown("#### 🛡️ Prevention (going forward)")
        for tip in v["PREVENTION"].split("|"):
            if tip.strip():
                st.markdown(f"- {tip.strip()}")

    st.caption("This is a student project for educational purposes only. "
               "Always consult a licensed doctor for medical concerns.")


# ─────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────
if st.session_state.submitted and st.session_state.result is not None:
    render_result_screen()
else:
    render_input_screen()
