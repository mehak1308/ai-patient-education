# AI Patient Education Assistant

A source-grounded healthcare education application that helps users explore general medical topics using information retrieved from **MedlinePlus**, a trusted health information resource provided by the U.S. National Library of Medicine and the National Institutes of Health.

The application combines medical-source retrieval, safety screening, structured content presentation, and a professional Streamlit interface to provide accessible patient education while maintaining clear boundaries around personalized medical advice.

---

## Overview

The **AI Patient Education Assistant** was designed to make general healthcare information easier to understand and navigate.

Rather than generating unsupported medical information, the application retrieves healthcare content from **MedlinePlus** and presents it in a structured, patient-friendly format.

The application also performs safety screening before providing educational information. Requests involving personal diagnosis, personalized treatment, medication recommendations, or potentially serious emergency symptoms are handled separately.

---
## Key Features

### 1. Source-Grounded Medical Information

Healthcare information is retrieved from **MedlinePlus** using the National Library of Medicine's search service.

Users can search for recognized healthcare topics such as:

- Asthma
- Diabetes
- Hypertension
- Allergies
- Other available health topics

The application identifies the medical source so users can understand where the information originated.

### 2. Safety Screening

The application distinguishes between general educational questions and requests that require personalized medical judgment.

Examples include:

```text
Do I have diabetes?

What medication should I take for high blood pressure?
## Technology Stack

The application was built using the following technologies:

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Streamlit** | Interactive web application interface |
| **Requests** | HTTP requests to the MedlinePlus search service |
| **XML Parsing** | Processing MedlinePlus search results |
| **Regular Expressions** | Content cleaning, parsing, and safety-pattern matching |
| **HTML/CSS** | Interface structure and visual styling |
| **MedlinePlus / U.S. National Library of Medicine** | External medical information source |
| **Git & GitHub** | Version control and project management |

---

## Application Architecture

The application follows a source-grounded workflow:

```text
User enters healthcare topic
            ↓
      Safety screening
            ↓
    ┌───────┴────────┐
    │                │
Safety concern    General topic
    │                │
    ↓                ↓
Safety response   MedlinePlus search
                       ↓
                 Source retrieval
                       ↓
                  Content parsing
                       ↓
                Section organization
                       ↓
                Patient education UI
                       ↓
              Source + safety notice
## Safety Design

This project is intentionally designed as an educational information tool, not a diagnostic system.

The application does not:

- Diagnose medical conditions
- Interpret individual laboratory results
- Recommend personalized medications
- Recommend individualized dosages
- Replace a healthcare professional
- Provide emergency medical assessment

When a user asks a personalized medical question, the application explains its limitations and recommends consultation with a qualified healthcare professional.

Potential emergency-related inputs are handled separately and do not proceed through the normal educational-information workflow.

The safety system uses predefined keyword and pattern matching. This is intentionally simple and transparent rather than being presented as a clinical triage system.

---

## Medical Information Source

Medical information is retrieved from:

**MedlinePlus — U.S. National Library of Medicine**

MedlinePlus is produced by the National Library of Medicine, part of the National Institutes of Health.

**Official source:**  
https://medlineplus.gov/

The application uses MedlinePlus as its external medical information source rather than relying exclusively on manually written medical content.

---
## Example Usage

### 1. General Healthcare Topic

**Input:**

    asthma

The application retrieves information from MedlinePlus and presents available sections covering topics such as:

- What asthma is
- Causes and triggers
- Risk factors
- Symptoms
- Diagnosis
- Treatment

The medical source is displayed alongside the resulting educational information.

---

### 2. Personalized Medical Question

**Input:**

    Do I have diabetes?

The application identifies the request as a personal medical question and does not attempt to determine whether the user has diabetes.

Instead, it explains that the application provides general education and recommends professional medical guidance.

---

### 3. Medication Request

**Input:**

    What medication should I take for high blood pressure?

The application does not recommend a medication or dosage.

Instead, it directs the user toward personalized guidance from a qualified healthcare professional.

---

### 4. Potential Medical Emergency

**Input:**

    I have chest pain

The application does not attempt to determine the cause of the symptom.

Instead, it displays an emergency-oriented safety message recommending immediate professional medical attention for severe or concerning symptoms.

---

### 5. Invalid Topic

**Input:**

    xyzabc123

The application displays a message explaining that no reliable information was found through MedlinePlus and suggests trying a recognized healthcare topic.

---

### 6. Empty Input

If the user submits an empty search, the application asks them to enter a healthcare topic.

---
## Installation

### 1. Clone the repository

    git clone https://github.com/mehak1308/ai-patient-education.git

### 2. Navigate into the project

    cd ai-patient-education

### 3. Create a virtual environment

    python3 -m venv .venv

### 4. Activate the virtual environment

**On macOS/Linux:**

    source .venv/bin/activate

### 5. Install dependencies

    pip install -r requirements.txt

### 6. Run the web application

    streamlit run web_app.py

The application will open in a local browser window.

---

## Testing

The application was tested using multiple categories of input to verify medical-source retrieval, safety screening, and input handling.

| Test Category | Example Input | Expected Behavior |
|---|---|---|
| Valid medical topic | `asthma` | Retrieve and display MedlinePlus information |
| Valid medical topic | `diabetes` | Retrieve source-grounded information |
| Personal diagnosis request | `Do I have diabetes?` | Display medical safety response |
| Medication request | `What medication should I take?` | Do not provide personalized medication advice |
| Emergency symptom | `I have chest pain` | Display emergency safety response |
| Invalid topic | `xyzabc123` | Display no reliable source message |
| Empty input | Blank | Ask the user to enter a healthcare topic |

Detailed testing information is documented in `TESTING.md`.

---
## Project Structure

    ai-patient-education/
    │
    ├── app.py
    ├── web_app.py
    ├── medical_source_test.py
    ├── TESTING.md
    ├── requirements.txt
    ├── README.md
    └── .gitignore

---

## File Descriptions

| File | Description |
|---|---|
| `web_app.py` | Main Streamlit web application containing the user interface, safety screening, medical-source retrieval, content parsing, and result presentation. |
| `app.py` | Command-line version of the patient education assistant. |
| `medical_source_test.py` | Testing script used to verify retrieval of medical information from MedlinePlus. |
| `TESTING.md` | Documents functional testing performed on the application's major retrieval, safety, and input-handling scenarios. |
| `requirements.txt` | Contains the Python dependencies required to run the project. |
| `README.md` | Project documentation, setup instructions, architecture, safety design, testing, and limitations. |
| `.gitignore` | Specifies files and directories that should not be tracked by Git. |

---
## Limitations

### Source Coverage

The application depends on information available through MedlinePlus. A topic that is not recognized by the source may not return a result.

### No Personalized Medical Reasoning

The application is not designed to determine whether a particular person has a medical condition or which treatment they should receive.

### Basic Safety Classification

The emergency and personalized-question filters use predefined keywords and pattern matching.

This provides a transparent first layer of safety but is not equivalent to clinical triage or medical decision-making.

### Educational Use Only

The application is intended for general health education and should not be used as a substitute for professional medical evaluation, diagnosis, or treatment.

---

## Future Improvements

Potential future development could include:

- Search history
- Improved topic matching
- More sophisticated medical-source retrieval
- Additional authoritative healthcare sources
- Better handling of medical terminology and synonyms
- Expanded automated testing
- Accessibility improvements
- Deployment as a public web application
- Improved source navigation
- More comprehensive safety classification

Future development should preserve the project's source-grounded and safety-first design.

---
## Design Philosophy

The central design principle of this project is:

    Trusted source
          ↓
    Safety screening
          ↓
    Structured information
          ↓
    Transparent sourcing
          ↓
    Patient education

The goal is not simply to produce a healthcare-related answer.

The application emphasizes where the information comes from, how the request is handled, and what the system should not attempt to do.

This is particularly important for healthcare applications, where usability must be balanced with accuracy, transparency, and appropriate safety boundaries.

---

## Why I Built This

I built this project to explore how technology can improve access to understandable healthcare information while maintaining appropriate boundaries around medical advice.

The project combines interests in healthcare, patient education, and technology.

Rather than creating a system that attempts to replace clinical judgment, I focused on building a tool that:

- Uses an established medical information source
- Makes healthcare information easier to navigate
- Clearly identifies the source of information
- Recognizes certain high-risk requests
- Avoids personalized diagnosis and treatment recommendations
- Communicates limitations to the user

---
## Disclaimer

This application provides general educational information only.

It does not provide:

- Medical diagnosis
- Individualized treatment recommendations
- Medication prescriptions
- Personalized medication or dosage advice
- Emergency medical assessment

Users with medical concerns should consult a qualified healthcare professional.

Anyone experiencing a potentially serious or life-threatening emergency should contact their local emergency medical service.

---

## Author

**Mehak Narang**

Biology | UMass Amherst

**GitHub:**  
https://github.com/mehak1308

---
