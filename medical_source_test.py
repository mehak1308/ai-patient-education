import requests
import xml.etree.ElementTree as ET
from html import unescape
import re


def clean_html(text):
    """Remove HTML tags and clean up the text."""

    text = unescape(text)

    text = re.sub(
        r"<.*?>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def get_medical_information(topic):

    url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": topic,
        "retmax": 5
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return None

        root = ET.fromstring(response.text)

        document = root.find(".//document")

        if document is None:
            return None

        title = document.find(
            "content[@name='title']"
        )

        summary = document.find(
            "content[@name='FullSummary']"
        )

        if title is None or summary is None:
            return None

        clean_title = clean_html(
            title.text or ""
        )

        clean_summary = clean_html(
            summary.text or ""
        )

        source_url = document.get("url")

        return {
            "title": clean_title,
            "summary": clean_summary,
            "source_url": source_url
        }

    except requests.RequestException:

        return None

    except ET.ParseError:

        return None


topic = input(
    "Enter a healthcare topic: "
)

result = get_medical_information(topic)

if result:

    print("\n========================================")
    print("MEDLINEPLUS RESULT")
    print("========================================")

    print("\nTitle:")
    print(result["title"])

    print("\nMedical information:")
    print(result["summary"])

    print("\nSource:")
    print("MedlinePlus — National Library of Medicine")

    print("\nSource URL:")
    print(result["source_url"])

    print("\n========================================")

else:

    print("\nNo medical information was found.")

    print(
        "Try a different healthcare topic."
    )