import requests
import xml.etree.ElementTree as ET
from html import unescape
import re


# ========================================
# MEDLINEPLUS MEDICAL SOURCE
# ========================================

def get_medical_information(topic):

    url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": topic
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
            unescape(title.text)
        )

        clean_summary = re.sub(
            r"<.*?>",
            " ",
            unescape(summary.text)
        )

        clean_summary = re.sub(
            r"\s+",
            " ",
            clean_summary
        ).strip()

        return clean_title, clean_summary

    except Exception:
        return None


# ========================================
# SAFETY KEYWORDS
# ========================================

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
    "do i have diabetes",
    "do i have asthma",
    "am i sick",
    "what should i take",
    "what medication should i take",
    "what medicine should i take",
    "should i take",
    "what should i do",
    "my symptoms",
    "my pain",
    "my condition"
]


# ========================================
# APPLICATION
# ========================================

print("========================================")
print("       AI PATIENT EDUCATION")
print("========================================")
print("Enter 'quit' when you want to stop.\n")


while True:

    topic = input("Enter a healthcare topic: ")

    topic_lower = topic.lower().strip()


    # ====================================
    # QUIT
    # ====================================

    if topic_lower == "quit":

        print("\nThank you for using the Patient Education Assistant.")

        break


    # ====================================
    # EMPTY INPUT
    # ====================================

    if not topic_lower:

        print("\n----------------------------------------")
        print("NO TOPIC ENTERED")
        print("----------------------------------------")
        print("Please enter a healthcare topic.")
        print("----------------------------------------\n")

        continue


    # ====================================
    # EMERGENCY SAFETY CHECK
    # ====================================

    if any(keyword in topic_lower for keyword in emergency_keywords):

        print("\n----------------------------------------")
        print("⚠️ POTENTIAL MEDICAL EMERGENCY")
        print("----------------------------------------")
        print("This tool cannot safely assess emergency symptoms.")
        print("If you are experiencing severe or concerning symptoms,")
        print("seek immediate medical attention or contact your local")
        print("emergency medical service.")
        print("----------------------------------------\n")

        continue


    # ====================================
    # PERSONAL MEDICAL QUESTION CHECK
    # ====================================

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


    # ====================================
    # GET MEDLINEPLUS INFORMATION
    # ====================================

    result = get_medical_information(topic)


    # ====================================
    # NO RELIABLE SOURCE
    # ====================================

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


    # ====================================
    # SOURCE INFORMATION
    # ====================================

    title, medical_information = result


    # ====================================
    # AI PROMPT
    # ====================================

    prompt = f"""
You are a healthcare patient-education assistant.

Your job is to transform reliable medical information into
clear, easy-to-understand educational information for a
general adult patient.

IMPORTANT SOURCE RULE:

The medical information provided below comes from MedlinePlus,
a service of the U.S. National Library of Medicine.

Use this MedlinePlus information as your PRIMARY factual source.

Do not invent medical facts.
Do not add statistics.
Do not add citations that are not provided.
Do not contradict the source.

If the source does not contain enough information to answer
something, say that the information is not available rather
than guessing.

MEDLINEPLUS TOPIC:

{title}

MEDLINEPLUS INFORMATION:

{medical_information}


AUDIENCE:

General adult patient with no medical background.


LANGUAGE:

- Use plain, easy-to-understand English.
- Avoid unnecessary medical terminology.
- Explain medical terms when they are necessary.
- Use short sentences.
- Use bullet points where appropriate.


FORMAT:

## What is it?

Give a short explanation based on the MedlinePlus information.


## Common symptoms

List important symptoms mentioned in the source.

Do not imply that everyone experiences the same symptoms.


## Common risk factors

List important risk factors mentioned in the source.


## How is it usually managed?

Summarize management information from the source.

Keep this high level.

Do not provide personalized treatment recommendations.


## When should someone seek medical care?

Explain warning signs or situations that may require
professional medical attention based on the source.

Clearly identify emergency situations when appropriate.


## Important note

Explain that symptoms can have many causes and that a
healthcare professional should be consulted for diagnosis
and personalized treatment.


SAFETY RULES:

- Never diagnose the user.
- Never tell the user they definitely have a condition.
- Never provide personalized medication recommendations.
- Never provide medication dosages.
- Never tell someone to stop or change prescribed medication.
- Never replace emergency medical care.
- Do not invent medical information.
- Do not invent statistics.
- Do not invent medical guidelines.
- Do not claim certainty when the source does not provide certainty.

End with exactly:

This information is for general educational purposes and is not a substitute for professional medical advice.
"""


    # ====================================
    # SEND TO LOCAL AI
    # ====================================

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        ai_response = response.json()["response"]


    except Exception as error:

        print("\n----------------------------------------")
        print("AI SERVICE ERROR")
        print("----------------------------------------")
        print("The local AI service could not generate a response.")
        print("Please make sure Ollama is running.")
        print("----------------------------------------\n")

        continue


    # ====================================
    # DISPLAY RESULT
    # ====================================

    print("\n========================================")
    print("AI PATIENT EDUCATION")
    print("========================================")

    print("\n")
    print(ai_response)

    print("\n----------------------------------------")
    print("Source:")
    print("MedlinePlus — National Library of Medicine")
    print("https://medlineplus.gov/")
    print("----------------------------------------\n")