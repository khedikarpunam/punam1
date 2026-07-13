# Health-Triage-Assistant

## Abstract

Health-Triage-Assistant is an AI-powered healthcare web application developed using Python and Flask. The system helps users perform an initial health assessment by analyzing symptoms entered by the user and suggesting possible medical conditions along with general health recommendations. The application is designed to assist users in making informed decisions about seeking medical attention while reducing unnecessary hospital visits. It is intended only as a preliminary screening tool and not as a replacement for professional medical diagnosis.

---

## Keywords

- Artificial Intelligence
- Healthcare
- Disease Prediction
- Symptom Analysis
- Flask
- Python
- Machine Learning
- Medical Assistant

---

# 1. Introduction

Healthcare systems often experience delays due to overcrowding and unnecessary consultations. Many people are unable to identify the seriousness of their symptoms before visiting a doctor.

The Health-Triage-Assistant aims to provide an intelligent preliminary assessment based on user symptoms. The application helps users understand the possible health condition and whether immediate medical consultation may be required.

---

# 2. Problem Statement

Patients often struggle to determine the severity of their symptoms before consulting a healthcare professional. This leads to unnecessary hospital visits or delayed treatment. Existing online symptom checkers may lack simplicity or accessibility.

---

# 3. Objectives

- Develop an AI-powered symptom checker.
- Predict possible diseases based on symptoms.
- Provide preliminary healthcare guidance.
- Improve awareness about health conditions.
- Create a simple and user-friendly web application.

---

# 4. Methodology

The project follows the following workflow:

1. User enters symptoms.
2. Symptoms are processed and validated.
3. Machine Learning model analyzes the symptoms.
4. Possible disease is predicted.
5. General health recommendation is displayed.
6. User is advised to consult a healthcare professional if necessary.

---

# 5. Literature Review

| Existing System | Limitations | Proposed System |
|-----------------|------------|-----------------|
| Traditional symptom checker | Limited intelligence | AI-based prediction |
| Manual consultation | Time consuming | Instant assessment |
| Basic medical websites | No intelligent prediction | Machine Learning support |

---

# 6. System Architecture

```
User
   │
   ▼
Flask Web Interface
   │
   ▼
Input Processing
   │
   ▼
Machine Learning Model
   │
   ▼
Disease Prediction
   │
   ▼
Health Recommendation
```

---

# 7. Implementation

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Flask
- Python

## Machine Learning

- Scikit-learn
- NumPy
- Pandas

## Configuration

- TOML Configuration Files

---

# 8. Tech Stack

| Category | Technology |
|----------|------------|
| Programming Language | Python |
| Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Machine Learning | Scikit-learn |
| Configuration | TOML |
| Version Control | Git |
| Repository | GitHub |

---

# 9. Project Structure

```
Health-Triage-Assistant/
│
├── app.py
├── config.toml
├── secrets.toml
├── LICENSE
├── README.md
└── requirements.txt
```

---

# 10. Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/Health-Triage-Assistant.git
```

Move into project directory:

```bash
cd Health-Triage-Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

# 11. Results

The application successfully:

- Accepts user symptoms
- Performs AI-based prediction
- Displays possible disease
- Provides health recommendations
- Offers an easy-to-use web interface

---

# 12. Conclusion

Health-Triage-Assistant demonstrates the use of Artificial Intelligence in healthcare by providing a simple and efficient symptom analysis system. It improves accessibility to preliminary healthcare information while encouraging users to seek professional medical advice when required.

---

# 13. Future Scope

- Integration with hospital databases
- Doctor appointment booking
- Real-time patient monitoring
- Medical report analysis
- Mobile application
- Cloud deployment
- Deep Learning-based diagnosis

---

# 14. References

1. Python Documentation
2. Flask Documentation
3. Scikit-learn Documentation
4. WHO Health Guidelines
5. Research Papers on Disease Prediction
