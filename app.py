import requests
import xml.etree.ElementTree as ET
from html import unescape
import re


# ============================================================
# SAFETY KEYWORDS
# ============================================================

emergency_keywords = [
    "chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
    "loss of consciousness",
    "stroke",
    "heart attack",
    "suicidal",
    "overdose"
]

personal_keywords = [
    "do i have",
    "could i have",
    "am i having",
    "what should i take",
    "what medication should i take",
    "what medicine should i take",
    "should i take",
    "what dose should i take",
    "how much medication should i take",
    "should i stop taking",
    "should i change my medication"
]


# ============================================================
# MEDLINEPLUS SEARCH FUNCTION
# ============================================================

def get_medical_information(topic):

    url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": topic,
        "rettype": "brief",
        "retmax": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        root = ET.fromstring(response.text)

        document = root.find(".//document")

        if document is None:
            return None

        title = document.find("content[@name='title']")
        summary = document.find("content[@name='FullSummary']")

        if title is None or summary is None:
            return None

        clean_title = re.sub(
            r"<.*?>",
            "",
            unescape(title.text or "")
        ).strip()

        clean_summary = re.sub(
            r"<.*?>",
            " ",
            unescape(summary.text or "")
        )

        clean_summary = re.sub(
            r"\s+",
            " ",
            clean_summary
        ).strip()

        source_url = document.get("url")

        return clean_title, clean_summary, source_url

    except Exception:
        return None


# ============================================================
# AI PATIENT EDUCATION ASSISTANT
# ============================================================

print("========================================")
print("       AI PATIENT EDUCATION")
print("========================================")
print("Enter 'quit' when you want to stop.\n")


while True:

    topic = input("Enter a healthcare topic: ").strip()

    # --------------------------------------------------------
    # EMPTY INPUT
    # --------------------------------------------------------

    if not topic:
        print("\n----------------------------------------")
        print("NO TOPIC ENTERED")
        print("----------------------------------------")
        print("Please enter a healthcare topic.\n")
        continue

    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    if topic.lower() == "quit":
        print("\nThank you for using the Patient Education Assistant.")
        break

    topic_lower = topic.lower()

    # --------------------------------------------------------
    # EMERGENCY SAFETY CHECK
    # --------------------------------------------------------

    if any(keyword in topic_lower for keyword in emergency_keywords):

        print("\n⚠️ POTENTIAL MEDICAL EMERGENCY")
        print("----------------------------------------")
        print("This tool cannot safely assess emergency symptoms.")
        print("If you are experiencing severe or concerning symptoms,")
        print("seek immediate medical attention or contact your local")
        print("emergency medical service.")
        print("----------------------------------------\n")

        continue

    # --------------------------------------------------------
    # PERSONAL MEDICAL QUESTION SAFETY CHECK
    # --------------------------------------------------------

    if any(keyword in topic_lower for keyword in personal_keywords):

        print("\n----------------------------------------")
        print("PERSONAL MEDICAL QUESTION")
        print("----------------------------------------")
        print("This tool can provide general health education,")
        print("but it cannot determine whether you have a condition")
        print("or recommend a treatment for you.")
        print("Please consult a qualified healthcare professional")
        print("for personalized medical guidance.")
        print("----------------------------------------\n")

        continue

    # --------------------------------------------------------
    # RETRIEVE MEDICAL INFORMATION FROM MEDLINEPLUS
    # --------------------------------------------------------

    result = get_medical_information(topic)

    if result is None:

        print("\n----------------------------------------")
        print("NO RELIABLE MEDICAL SOURCE FOUND")
        print("----------------------------------------")
        print("I could not find relevant information for this topic")
        print("in MedlinePlus.")
        print("Try entering a recognized healthcare topic, such as")
        print("asthma, diabetes, hypertension, or allergies.")
        print("----------------------------------------\n")

        continue

    title, medical_information, source_url = result

    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a healthcare patient-education assistant.

Your purpose is to explain reliable medical information
in simple language for a general adult audience.

You are NOT a doctor.

You must NOT:
- diagnose the user
- provide personalized medical advice
- recommend a medication or dosage
- tell someone to stop or change prescribed medication
- replace emergency medical care

The user asked about:

{topic}

A medical source was retrieved from MedlinePlus,
National Library of Medicine.

SOURCE TITLE:
{title}

SOURCE INFORMATION:
{medical_information}

Use the source information above as the primary factual basis
for your response.

Do not invent medical facts, statistics, guidelines, citations,
medications, or treatments that are not supported by the source.

Write for a general adult patient with no medical background.

Use plain English and short sentences.

Structure your answer exactly like this:

## What is it?
Give a short explanation.

## Common symptoms
List common symptoms when the source provides them.

## Common risk factors
List important risk factors when the source provides them.

## How is it usually managed?
Give a high-level explanation based on the source.

Do not provide personalized treatment recommendations.

## When should someone seek medical care?
Explain situations where professional medical care may be appropriate.
Clearly identify emergency situations when appropriate.

## Important note
Explain that symptoms can have many causes and that a healthcare
professional should be consulted for diagnosis.

Do not claim that the user has the condition.

End with exactly:

This information is for general educational purposes and is not a substitute for professional medical advice.
"""

    # --------------------------------------------------------
    # SEND SOURCE-GROUNDED PROMPT TO LOCAL LLAMA
    # --------------------------------------------------------

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        ai_response = response.json()["response"]

    except Exception as error:

        print("\n----------------------------------------")
        print("AI SERVICE ERROR")
        print("----------------------------------------")
        print("The medical source was found, but the AI service")
        print("could not generate a response.")
        print("Make sure Ollama is running.")
        print("----------------------------------------\n")

        continue

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    print("\n----------------------------------------")
    print("AI PATIENT EDUCATION")
    print("----------------------------------------")

    print(ai_response)

    print("\n----------------------------------------")
    print("SOURCE")
    print("----------------------------------------")
    print("MedlinePlus — National Library of Medicine")

    if source_url:
        print(f"Source URL: {source_url}")

    print("----------------------------------------\n")