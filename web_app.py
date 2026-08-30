import streamlit as st
import requests
import xml.etree.ElementTree as ET
from html import unescape
import re


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Patient Education",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f9fc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background: #eef5f8;
        border-right: 1px solid #d8e4ea;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 2rem 1.3rem;
    }

    .sidebar-title {
        color: #173f5f;
        font-size: 1.3rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }

    .sidebar-subtitle {
        color: #718694;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 1.8rem;
    }

    .sidebar-section {
        color: #648197;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-top: 1.6rem;
        margin-bottom: 0.75rem;
    }

    .sidebar-step {
        color: #40596c;
        font-size: 0.84rem;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }

    /* BRAND */

    .brand-name {
        color: #173f5f;
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.35;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }

    .brand-subtitle {
        color: #78909f;
        font-size: 0.78rem;
        line-height: 1.4;
        margin-bottom: 2rem;
    }

    /* HERO */

    .hero-box {
        background: linear-gradient(
            135deg,
            #123f61 0%,
            #176582 55%,
            #168b98 100%
        );

        border-radius: 22px;
        padding: 3rem 3.2rem;
        margin-bottom: 2.5rem;

        box-shadow:
            0 18px 40px rgba(18, 63, 97, 0.15);
    }

    .hero-label {
        color: #bce6e9;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        margin-bottom: 0.85rem;
    }

    .hero-heading {
        color: white;
        font-size: 2.55rem;
        font-weight: 800;
        line-height: 1.18;
        letter-spacing: -0.035em;
        margin-bottom: 1rem;
        max-width: 720px;
    }

    .hero-description {
        color: #e2f0f3;
        font-size: 0.98rem;
        line-height: 1.7;
        max-width: 700px;
    }

    /* SECTION */

    .section-label {
        color: #17768b;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        margin-bottom: 0.4rem;
    }

    .section-heading {
        color: #173f5f;
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.35rem;
    }

    .section-description {
        color: #6c8190;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* INPUT */

    div[data-testid="stTextInput"] input {
        background: white;
        border: 1px solid #cbd9e1;
        border-radius: 11px;
        min-height: 48px;
        font-size: 0.95rem;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #197a91;
        box-shadow: 0 0 0 2px rgba(25, 122, 145, 0.12);
    }

    .examples {
        color: #7a8c99;
        font-size: 0.75rem;
        margin-top: 0.4rem;
        margin-bottom: 1.25rem;
    }

    /* BUTTON */

    div.stButton > button {
        background: #176b86;
        color: white;
        border: none;
        border-radius: 10px;
        min-height: 46px;
        font-weight: 700;
        padding: 0.5rem 1.3rem;
    }

    div.stButton > button:hover {
        background: #125970;
        color: white;
    }

    /* RESULTS */

    .result-label {
        color: #17768b;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        margin-top: 1rem;
        margin-bottom: 0.3rem;
    }

    .result-title {
        color: #173f5f;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }

    .result-meta {
        color: #7a8b98;
        font-size: 0.78rem;
        margin-bottom: 1.3rem;
    }

    /* MEDICAL CONTENT */

    .medical-card {
        background: white;
        border: 1px solid #dce6eb;
        border-radius: 14px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 12px rgba(31, 61, 78, 0.04);
    }

    .medical-heading {
        color: #173f5f;
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .medical-text {
        color: #4e6475;
        font-size: 0.91rem;
        line-height: 1.8;
    }

    .medical-bullet {
        color: #4e6475;
        font-size: 0.9rem;
        line-height: 1.7;
        margin-left: 0.3rem;
        margin-bottom: 0.25rem;
    }

    /* SOURCE */

    .source-box {
        background: #edf7f8;
        border: 1px solid #cfe5e8;
        border-radius: 14px;
        padding: 1.15rem 1.3rem;
        margin-top: 1.4rem;
    }

    .source-heading {
        color: #176278;
        font-size: 0.88rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .source-description {
        color: #58717f;
        font-size: 0.8rem;
        line-height: 1.55;
    }

    /* SAFETY */

    .safety-box {
        background: #fff9ed;
        border: 1px solid #eadcb9;
        border-left: 5px solid #c69b3b;
        border-radius: 12px;
        padding: 1.15rem 1.3rem;
        margin-top: 1.3rem;
    }

    .safety-heading {
        color: #80621f;
        font-size: 0.95rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .safety-description {
        color: #6f6247;
        font-size: 0.85rem;
        line-height: 1.65;
    }

    /* EMERGENCY */

    .emergency-box {
        background: #fff5f4;
        border: 1px solid #efc9c5;
        border-left: 5px solid #c64747;
        border-radius: 12px;
        padding: 1.2rem 1.3rem;
        margin-top: 1.4rem;
    }

    .emergency-heading {
        color: #9d2e2e;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .emergency-description {
        color: #744646;
        font-size: 0.86rem;
        line-height: 1.65;
    }

    /* EMPTY */

    .empty-box {
        background: white;
        border: 1px dashed #cbd9e1;
        border-radius: 14px;
        padding: 1.8rem;
        margin-top: 1.4rem;
        text-align: center;
    }

    .empty-heading {
        color: #173f5f;
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .empty-description {
        color: #7a8c98;
        font-size: 0.84rem;
        line-height: 1.6;
    }

    /* FOOTER */

    .app-footer {
        border-top: 1px solid #dce5ea;
        margin-top: 3rem;
        padding-top: 1.2rem;
        color: #8795a0;
        font-size: 0.7rem;
        text-align: center;
        line-height: 1.6;
    }

    @media (max-width: 800px) {

        .block-container {
            padding-top: 1.8rem;
        }

        .hero-box {
            padding: 2rem 1.5rem;
        }

        .hero-heading {
            font-size: 2rem;
        }

        .result-title {
            font-size: 1.65rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MEDLINEPLUS
# ============================================================

def get_medical_information(topic):

    url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": topic
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

    except requests.RequestException:

        return None

    if response.status_code != 200:

        return None

    try:

        root = ET.fromstring(response.text)

    except ET.ParseError:

        return None

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

    if title.text is None or summary.text is None:

        return None

    clean_title = re.sub(
        r"<.*?>",
        "",
        unescape(title.text)
    ).strip()

    raw_summary = unescape(summary.text)

    # Convert HTML line breaks to newlines
    raw_summary = re.sub(
        r"<br\s*/?>",
        "\n",
        raw_summary,
        flags=re.IGNORECASE
    )

    # Convert paragraph/list HTML to newlines
    raw_summary = re.sub(
        r"</(p|div|li|h[1-6])>",
        "\n",
        raw_summary,
        flags=re.IGNORECASE
    )

    # Remove remaining HTML tags
    clean_summary = re.sub(
        r"<.*?>",
        "",
        raw_summary
    )

    clean_summary = re.sub(
        r"[ \t]+",
        " ",
        clean_summary
    )

    clean_summary = re.sub(
        r"\n\s*\n+",
        "\n\n",
        clean_summary
    ).strip()

    return clean_title, clean_summary


# ============================================================
# SAFETY FILTERS
# ============================================================

EMERGENCY_KEYWORDS = [

    "chest pain",
    "severe chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "trouble breathing",
    "unconscious",
    "passed out",
    "severe bleeding",
    "stroke symptoms",
    "heart attack",
    "seizure",
    "overdose"

]


PERSONAL_QUESTION_PATTERNS = [

    "do i have",
    "what medication should i take",
    "what medicine should i take",
    "should i take",
    "what should i take",
    "am i sick",
    "is this serious",
    "what treatment should i use",
    "how much medicine",
    "what dose should i take",
    "my symptoms",
    "i have symptoms"

]


def is_emergency_question(text):

    text = text.lower().strip()

    return any(
        keyword in text
        for keyword in EMERGENCY_KEYWORDS
    )


def is_personal_medical_question(text):

    text = text.lower().strip()

    return any(
        pattern in text
        for pattern in PERSONAL_QUESTION_PATTERNS
    )


# ============================================================
# FORMAT MEDICAL CONTENT
# ============================================================

def format_medical_content(text):

    """
    Converts the MedlinePlus summary into readable sections.

    We specifically look for the common MedlinePlus question-style
    headings. If a topic does not contain these headings, the
    complete source text is still displayed rather than discarded.
    """

    text = text.strip()

    if not text:

        return []


    # Normalize whitespace while preserving paragraph breaks

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    ).strip()


    # Common MedlinePlus headings

    heading_patterns = [

        r"What is [^?]+\?",
        r"What causes [^?]+\?",
        r"Who is at risk for [^?]+\?",
        r"What are the symptoms of [^?]+\?",
        r"How is [^?]+ diagnosed\?",
        r"What are the treatments for [^?]+\?",
        r"How is [^?]+ treated\?",
        r"What are [^?]+ treatments\?",
        r"How can [^?]+ be prevented\?",
        r"How can [^?]+ be treated\?",
        r"What tests are used to diagnose [^?]+\?",
        r"What happens during [^?]+\?",
        r"What are the complications of [^?]+\?"

    ]


    combined_pattern = (
        "("
        + "|".join(heading_patterns)
        + ")"
    )


    matches = list(
        re.finditer(
            combined_pattern,
            text,
            flags=re.IGNORECASE
        )
    )


    sections = []


    # --------------------------------------------------------
    # If recognizable headings exist
    # --------------------------------------------------------

    if matches:

        # Text before first heading

        if matches[0].start() > 0:

            intro = text[
                :matches[0].start()
            ].strip()

            if intro:

                sections.append(
                    ("Overview", intro)
                )


        for i, match in enumerate(matches):

            heading = match.group().strip()

            start = match.end()

            if i + 1 < len(matches):

                end = matches[
                    i + 1
                ].start()

            else:

                end = len(text)

            content = text[
                start:end
            ].strip()

            if content:

                sections.append(
                    (heading, content)
                )


        return sections


    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return [
        ("Medical information", text)
    ]


def pretty_heading(heading):

    lower = heading.lower().strip()


    if lower.startswith("what is"):

        return "What is it?"


    if lower.startswith("what causes"):

        return "What causes it?"


    if lower.startswith("who is at risk"):

        return "Who is at risk?"


    if lower.startswith("what are the symptoms"):

        return "Common symptoms"


    if lower.startswith("how is") and "diagnos" in lower:

        return "How is it diagnosed?"


    if "treatment" in lower or "treated" in lower:

        return "How is it treated?"


    if "prevented" in lower:

        return "How can it be prevented?"


    return heading


def display_content(content):

    """
    Displays source content in readable paragraphs and bullets.
    """

    # Clean excessive spaces

    content = re.sub(
        r"\s+",
        " ",
        content
    ).strip()


    # Recognize common bullet-like patterns

    bullet_markers = [
        "Dust mites",
        "Mold",
        "Pets",
        "Pollen",
        "Chest tightness",
        "Coughing",
        "Shortness of breath",
        "Wheezing"
    ]


    # For normal medical prose, simply display it.

    st.markdown(
        f'<div class="medical-text">'
        f'{content}'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">'
        'AI Patient Education'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Source-grounded healthcare education'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">'
        'HOW IT WORKS'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-step">'
        '<b>01</b> &nbsp; Enter a healthcare topic'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-step">'
        '<b>02</b> &nbsp; Safety screening checks the request'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-step">'
        '<b>03</b> &nbsp; Information is retrieved from MedlinePlus'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-step">'
        '<b>04</b> &nbsp; Information is presented clearly'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">'
        'TRUSTED SOURCE'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "MedlinePlus\n\n"
        "National Library of Medicine\n\n"
        "National Institutes of Health"
    )

    st.markdown(
        '<div class="sidebar-section">'
        'SAFETY'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-step">'
        'This application provides general educational '
        'information. It does not diagnose conditions, '
        'prescribe medications, or replace professional '
        'medical care.'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# BRAND
# ============================================================

st.markdown(
    '<div class="brand-name">'
    'AI Patient Education'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand-subtitle">'
    'Healthcare information assistant'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero-box">'
    '<div class="hero-label">'
    'MEDICAL INFORMATION · SOURCE-GROUNDED'
    '</div>'
    '<div class="hero-heading">'
    'Understand your health,<br>'
    'one topic at a time.'
    '</div>'
    '<div class="hero-description">'
    'Explore clear explanations of general healthcare topics '
    'using information retrieved from MedlinePlus, a resource '
    'of the U.S. National Library of Medicine.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SEARCH AREA
# ============================================================

st.markdown(
    '<div class="section-label">'
    'PATIENT EDUCATION'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">'
    'What would you like to learn about?'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Ask about a general healthcare topic such as asthma, '
    'diabetes, hypertension, allergies, or another recognized '
    'health topic.'
    '</div>',
    unsafe_allow_html=True
)


topic = st.text_input(
    "Healthcare topic",
    placeholder="Enter a healthcare topic...",
    label_visibility="collapsed"
)


st.markdown(
    '<div class="examples">'
    'Examples: asthma · diabetes · hypertension · allergies'
    '</div>',
    unsafe_allow_html=True
)


search_clicked = st.button(
    "Search medical information"
)


# ============================================================
# RESULTS
# ============================================================

if search_clicked:

    topic = topic.strip()


    # EMPTY

    if not topic:

        st.markdown(
            '<div class="empty-box">'
            '<div class="empty-heading">'
            'No topic entered'
            '</div>'
            '<div class="empty-description">'
            'Enter a general healthcare topic to begin.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


    # EMERGENCY

    elif is_emergency_question(topic):

        st.markdown(
            '<div class="emergency-box">'
            '<div class="emergency-heading">'
            'Potential medical emergency'
            '</div>'
            '<div class="emergency-description">'
            'This application cannot safely assess emergency '
            'symptoms. If you are experiencing severe or '
            'concerning symptoms, seek immediate medical '
            'attention or contact your local emergency '
            'medical service.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


    # PERSONAL MEDICAL QUESTION

    elif is_personal_medical_question(topic):

        st.markdown(
            '<div class="safety-box">'
            '<div class="safety-heading">'
            'Personal medical question'
            '</div>'
            '<div class="safety-description">'
            'This tool provides general health education, '
            'but it cannot determine whether you have a '
            'condition, recommend a medication, or provide '
            'personalized treatment.'
            '<br><br>'
            'Please consult a qualified healthcare professional '
            'for personalized medical guidance.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


    # GENERAL HEALTHCARE TOPIC

    else:

        with st.spinner(
            "Retrieving information from MedlinePlus..."
        ):

            result = get_medical_information(topic)


        if result is None:

            st.markdown(
                '<div class="empty-box">'
                '<div class="empty-heading">'
                'No reliable medical source found'
                '</div>'
                '<div class="empty-description">'
                'I could not find relevant information on this '
                'topic in MedlinePlus.'
                '<br><br>'
                'Try a recognized healthcare topic such as '
                'asthma, diabetes, hypertension, or allergies.'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


        else:

            title, information = result


            st.divider()


            # RESULT HEADER

            st.markdown(
                '<div class="result-label">'
                'PATIENT EDUCATION'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="result-title">'
                f'{title}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="result-meta">'
                'Source-grounded information · MedlinePlus'
                '</div>',
                unsafe_allow_html=True
            )


            # MEDICAL SECTIONS

            sections = format_medical_content(
                information
            )


            for heading, content in sections:

                pretty = pretty_heading(
                    heading
                )

                st.markdown(
                    '<div class="medical-card">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="medical-heading">'
                    f'{pretty}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                display_content(content)

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


            # SOURCE CARD

            st.markdown(
                '<div class="source-box">'
                '<div class="source-heading">'
                'Verified medical source'
                '</div>'
                '<div class="source-description">'
                'MedlinePlus — National Library of Medicine<br>'
                'National Institutes of Health'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            st.link_button(
                "Open MedlinePlus",
                "https://medlineplus.gov/"
            )


            # DISCLAIMER

            st.markdown(
                '<div class="safety-box">'
                '<div class="safety-heading">'
                'Educational information only'
                '</div>'
                '<div class="safety-description">'
                'This information is intended for general '
                'educational purposes and is not a substitute '
                'for professional medical advice, diagnosis, '
                'or treatment.'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer">'
    'AI Patient Education · Source-grounded healthcare education '
    '· General educational information only'
    '</div>',
    unsafe_allow_html=True
)