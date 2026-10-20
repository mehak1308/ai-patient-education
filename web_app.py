import re
import time
import html
import io
import json
import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, quote

import requests
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareClarity",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIG
# ============================================================

MEDLINEPLUS_SEARCH_URL = "https://wsearch.nlm.nih.gov/ws/query"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_AI_MODEL = "gpt-5.6-luna"  # Legacy API path retained but not used by the free local-AI interface

MYMEMORY_TRANSLATE_URL = "https://api.mymemory.translated.net/get"
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr", "German": "de",
    "Portuguese": "pt", "Italian": "it", "Dutch": "nl", "Russian": "ru",
    "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Japanese": "ja", "Korean": "ko", "Arabic": "ar", "Hindi": "hi",
    "Bengali": "bn", "Urdu": "ur", "Punjabi": "pa", "Gujarati": "gu",
    "Marathi": "mr", "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
    "Malayalam": "ml", "Vietnamese": "vi", "Thai": "th", "Indonesian": "id",
    "Malay": "ms", "Filipino": "tl", "Turkish": "tr", "Polish": "pl",
    "Ukrainian": "uk", "Romanian": "ro", "Greek": "el", "Hebrew": "he",
    "Swedish": "sv", "Danish": "da", "Norwegian": "no", "Finnish": "fi",
    "Czech": "cs", "Hungarian": "hu", "Swahili": "sw", "Persian": "fa",
}

UI_TRANSLATIONS = {
    "en": {"language":"Language", "search":"Search medical information", "topic":"What would you like to learn about?", "empty":"Enter a general healthcare topic to begin.", "result_label":"PATIENT EDUCATION", "result_meta":"MedlinePlus retrieval · safety screening · source-grounded education", "source_grounded":"Source-grounded education", "source_grounded_desc":"The information below is presented directly from the retrieved MedlinePlus source. Optional local AI is not required; core education works without an AI API key."},
    "es": {"language":"Idioma", "search":"Buscar información médica", "topic":"¿Sobre qué te gustaría aprender?", "empty":"Ingresa un tema general de salud para comenzar."},
    "fr": {"language":"Langue", "search":"Rechercher des informations médicales", "topic":"Que souhaitez-vous apprendre ?", "empty":"Saisissez un sujet général de santé pour commencer."},
    "de": {"language":"Sprache", "search":"Medizinische Informationen suchen", "topic":"Worüber möchten Sie etwas erfahren?", "empty":"Geben Sie ein allgemeines Gesundheitsthema ein."},
    "pt": {"language":"Idioma", "search":"Pesquisar informações médicas", "topic":"Sobre o que você gostaria de aprender?", "empty":"Digite um tema geral de saúde para começar."},
    "it": {"language":"Lingua", "search":"Cerca informazioni mediche", "topic":"Che cosa vorresti sapere?", "empty":"Inserisci un argomento generale di salute per iniziare."},
    "nl": {"language":"Taal", "search":"Medische informatie zoeken", "topic":"Waarover wil je meer weten?", "empty":"Voer een algemeen gezondheidsonderwerp in om te beginnen."},
    "ru": {"language":"Язык", "search":"Поиск медицинской информации", "topic":"О чем вы хотите узнать?", "empty":"Введите общую медицинскую тему, чтобы начать."},
    "zh-CN": {"language":"语言", "search":"搜索医学信息", "topic":"您想了解什么？", "empty":"输入一个一般健康主题即可开始。"},
    "zh-TW": {"language":"語言", "search":"搜尋醫療資訊", "topic":"您想了解什麼？", "empty":"輸入一般健康主題即可開始。"},
    "ja": {"language":"言語", "search":"医療情報を検索", "topic":"何について知りたいですか？", "empty":"一般的な健康トピックを入力してください。"},
    "ko": {"language":"언어", "search":"의료 정보 검색", "topic":"무엇에 대해 알고 싶으신가요?", "empty":"일반적인 건강 주제를 입력하세요."},
    "ar": {"language":"اللغة", "search":"البحث عن معلومات طبية", "topic":"ما الذي تريد معرفة المزيد عنه؟", "empty":"أدخل موضوعًا صحيًا عامًا للبدء."},
    "hi": {"language":"भाषा", "search":"चिकित्सीय जानकारी खोजें", "topic":"आप किस बारे में जानना चाहते हैं?", "empty":"शुरू करने के लिए कोई सामान्य स्वास्थ्य विषय दर्ज करें।"},
    "tr": {"language":"Dil", "search":"Tıbbi bilgi ara", "topic":"Ne hakkında bilgi edinmek istiyorsunuz?", "empty":"Başlamak için genel bir sağlık konusu girin."},
    "pl": {"language":"Język", "search":"Szukaj informacji medycznych", "topic":"Czego chcesz się dowiedzieć?", "empty":"Wpisz ogólny temat zdrowotny, aby rozpocząć."},
    "uk": {"language":"Мова", "search":"Пошук медичної інформації", "topic":"Про що ви хочете дізнатися?", "empty":"Введіть загальну тему про здоров’я, щоб почати."},
    "ro": {"language":"Limbă", "search":"Caută informații medicale", "topic":"Despre ce ai vrea să afli?", "empty":"Introduceți un subiect general de sănătate pentru a începe."},
    "el": {"language":"Γλώσσα", "search":"Αναζήτηση ιατρικών πληροφοριών", "topic":"Τι θα θέλατε να μάθετε;", "empty":"Εισαγάγετε ένα γενικό θέμα υγείας για να ξεκινήσετε."},
    "he": {"language":"שפה", "search":"חיפוש מידע רפואי", "topic":"על מה תרצה ללמוד?", "empty":"הזן נושא בריאותי כללי כדי להתחיל."},
    "vi": {"language":"Ngôn ngữ", "search":"Tìm kiếm thông tin y tế", "topic":"Bạn muốn tìm hiểu về điều gì?", "empty":"Nhập một chủ đề sức khỏe chung để bắt đầu."},
    "th": {"language":"ภาษา", "search":"ค้นหาข้อมูลทางการแพทย์", "topic":"คุณต้องการเรียนรู้เกี่ยวกับอะไร?", "empty":"ป้อนหัวข้อสุขภาพทั่วไปเพื่อเริ่มต้น"},
    "id": {"language":"Bahasa", "search":"Cari informasi medis", "topic":"Apa yang ingin Anda pelajari?", "empty":"Masukkan topik kesehatan umum untuk memulai."},
    "ms": {"language":"Bahasa", "search":"Cari maklumat perubatan", "topic":"Apakah yang anda ingin pelajari?", "empty":"Masukkan topik kesihatan umum untuk bermula."},
    "tl": {"language":"Wika", "search":"Maghanap ng impormasyong medikal", "topic":"Ano ang gusto mong malaman?", "empty":"Maglagay ng pangkalahatang paksa sa kalusugan upang magsimula."},
    "bn": {"language":"ভাষা", "search":"চিকিৎসা তথ্য খুঁজুন", "topic":"আপনি কী সম্পর্কে জানতে চান?", "empty":"শুরু করতে একটি সাধারণ স্বাস্থ্য বিষয় লিখুন।"},
    "ur": {"language":"زبان", "search":"طبی معلومات تلاش کریں", "topic":"آپ کس بارے میں جاننا چاہتے ہیں؟", "empty":"شروع کرنے کے لیے صحت کا عمومی موضوع درج کریں۔"},
    "pa": {"language":"ਭਾਸ਼ਾ", "search":"ਡਾਕਟਰੀ ਜਾਣਕਾਰੀ ਖੋਜੋ", "topic":"ਤੁਸੀਂ ਕਿਸ ਬਾਰੇ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?", "empty":"ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਸਿਹਤ ਦਾ ਆਮ ਵਿਸ਼ਾ ਦਰਜ ਕਰੋ।"},
    "gu": {"language":"ભાષા", "search":"તબીબી માહિતી શોધો", "topic":"તમે શે વિશે જાણવા માંગો છો?", "empty":"શરૂ કરવા માટે સામાન્ય આરોગ્ય વિષય દાખલ કરો."},
    "mr": {"language":"भाषा", "search":"वैद्यकीय माहिती शोधा", "topic":"तुम्हाला कशाबद्दल जाणून घ्यायचे आहे?", "empty":"सुरुवात करण्यासाठी सामान्य आरोग्य विषय प्रविष्ट करा."},
    "ta": {"language":"மொழி", "search":"மருத்துவ தகவலைத் தேடுங்கள்", "topic":"எதைப் பற்றி தெரிந்துகொள்ள விரும்புகிறீர்கள்?", "empty":"தொடங்க பொதுவான சுகாதார தலைப்பை உள்ளிடவும்."},
    "te": {"language":"భాష", "search":"వైద్య సమాచారాన్ని శోధించండి", "topic":"మీరు దేని గురించి తెలుసుకోవాలనుకుంటున్నారు?", "empty":"ప్రారంభించడానికి సాధారణ ఆరోగ్య అంశాన్ని నమోదు చేయండి."},
    "kn": {"language":"ಭಾಷೆ", "search":"ವೈದ್ಯಕೀಯ ಮಾಹಿತಿಗಾಗಿ ಹುಡುಕಿ", "topic":"ನೀವು ಯಾವುದರ ಬಗ್ಗೆ ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಿ?", "empty":"ಪ್ರಾರಂಭಿಸಲು ಸಾಮಾನ್ಯ ಆರೋಗ್ಯ ವಿಷಯವನ್ನು ನಮೂದಿಸಿ."},
    "ml": {"language":"ഭാഷ", "search":"മെഡിക്കൽ വിവരങ്ങൾ തിരയുക", "topic":"നിങ്ങൾ എന്തിനെക്കുറിച്ചാണ് അറിയാൻ ആഗ്രഹിക്കുന്നത്?", "empty":"ആരംഭിക്കാൻ ഒരു പൊതുവായ ആരോഗ്യ വിഷയം നൽകുക."},
    "sw": {"language":"Lugha", "search":"Tafuta taarifa za matibabu", "topic":"Ungependa kujifunza kuhusu nini?", "empty":"Weka mada ya jumla ya afya ili kuanza."},
    "fa": {"language":"زبان", "search":"جستجوی اطلاعات پزشکی", "topic":"درباره چه چیزی می‌خواهید بدانید؟", "empty":"برای شروع یک موضوع کلی سلامت وارد کنید."},
}


SYNONYMS = {
    "high blood pressure": "hypertension", "blood pressure": "hypertension",
    "heart attack": "myocardial infarction", "mi": "myocardial infarction",
    "stroke": "cerebrovascular accident", "cva": "cerebrovascular accident",
    "sugar diabetes": "diabetes", "type 2 diabetes": "type 2 diabetes",
    "heartburn": "gastroesophageal reflux", "acid reflux": "gastroesophageal reflux",
    "pink eye": "conjunctivitis", "chickenpox": "varicella", "shingles": "herpes zoster",
    "flu": "influenza", "covid": "covid-19", "eczema": "atopic dermatitis",
    "kidney stones": "kidney stone", "uti": "urinary tract infection",
    "blood clot": "deep vein thrombosis", "dvt": "deep vein thrombosis",
    "copd": "chronic obstructive pulmonary disease", "ibs": "irritable bowel syndrome",
    "adhd": "attention deficit hyperactivity disorder", "anxiety": "anxiety disorders",
}

AUTHORITATIVE_SOURCES = [
    ("CDC", "https://www.cdc.gov/"),
    ("National Institutes of Health", "https://www.nih.gov/"),
    ("FDA", "https://www.fda.gov/"),
    ("National Institute of Mental Health", "https://www.nimh.nih.gov/"),
]

EMERGENCY_MESSAGE = (
    "This tool cannot assess an emergency. If you may be in immediate "
    "danger or need urgent medical attention, call 911 or your local "
    "emergency service now."
)

CRISIS_MESSAGE = (
    "If you or someone else may be at immediate risk of suicide or self-harm, "
    "call or text 988 for the 988 Suicide & Crisis Lifeline. If there is "
    "immediate danger, call 911."
)


# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --ink: #34264f;
        --muted: #6f6580;
        --line: #ddd5ea;
        --surface: #ffffff;
        --bg: #f7f3fb;
        --teal: #8067b8;
        --teal-dark: #5d4a8c;
        --blue: #7357ad;
        --soft-blue: #f0ebf8;
    }

    .stApp { background: linear-gradient(180deg, #f6f1fb 0%, #fbf9fd 46%, #f4eff9 100%); }
    .block-container { max-width: 1160px; padding-top: 2.8rem; padding-bottom: 3.2rem; }
    [data-testid="stAppViewContainer"] > .main { border-top: 1px solid #ddd5ea; }
    #MainMenu, footer { visibility: hidden; }

    /* Keyboard accessibility: keep a clear, high-contrast focus ring. */
    :focus-visible { outline: 3px solid #5d4387 !important; outline-offset: 3px !important; }
    a { text-underline-offset: 3px; }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
    }

    section[data-testid="stSidebar"] {
        background: #fcfaff;
        border-right: 1px solid #d8cfe7;
    }
    section[data-testid="stSidebar"] .block-container { padding: 1.6rem 1.15rem 2rem; }

    .sidebar-title {
        color: #34264f; font-size: 1.15rem; font-weight: 800; line-height: 1.25;
        margin-bottom: .2rem;
    }
    .sidebar-subtitle { color: var(--muted); font-size: .78rem; line-height: 1.5; margin-bottom: 1.25rem; }
    .sidebar-section {
        color: #76648f; font-size: .66rem; font-weight: 800; letter-spacing: .13em;
        text-transform: uppercase; margin-top: 1.25rem; margin-bottom: .6rem;
    }
    .sidebar-link {
        display: block; padding: .52rem .65rem; margin-bottom: .35rem; border: 1px solid var(--line);
        border-radius: 9px; background: #fbf9fe; color: #5c477f !important; text-decoration: none !important;
        font-size: .82rem; font-weight: 650;
    }
    .sidebar-link:hover { background: #f0eafa; border-color: #c9b9df; transform: translateY(-1px); }
    .sidebar-note { color: #657887; font-size: .78rem; line-height: 1.55; }

    .brand-row { display: flex; align-items: center; gap: .7rem; margin-bottom: .45rem; padding-top: .35rem; }
    .brand-mark {
        width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #6d56a6, #9a7bd1); color: white; font-size: 1.05rem; font-weight: 800;
        box-shadow: 0 7px 18px rgba(109,86,166,.22);
    }
    .brand-name { color: #34264f; font-size: 1.55rem; font-weight: 800; line-height: 1.25; letter-spacing: -.02em; }
    .brand-subtitle { color: #756a85; font-size: .82rem; line-height: 1.45; margin-bottom: .75rem; }

    .hero-box {
        position: relative; overflow: hidden; background: linear-gradient(115deg, #514078 0%, #7459a6 54%, #9a7bc6 100%);
        border: 1px solid #cbb9df; border-radius: 22px; padding: 2.15rem 2.35rem; min-height: 248px;
        margin-bottom: .05rem; box-shadow: 0 12px 28px rgba(73,53,107,.11);
    }
    .hero-box:after {
        content: ""; position: absolute; width: 280px; height: 280px; right: -75px; top: -100px;
        border-radius: 50%; background: rgba(255,255,255,.11);
    }
    .hero-photo {
        position: absolute; right: 1.65rem; top: 1.35rem; width: 300px; height: 218px;
        object-fit: cover; object-position: 50% 30%; background: transparent;
        border-radius: 15px; opacity: 1; border: 1px solid rgba(255,255,255,.38);
        box-shadow: 0 10px 24px rgba(45,31,69,.20); z-index: 1;
    }
    .hero-label { color: #eee6fb; font-size: .67rem; font-weight: 800; letter-spacing: .14em; margin-bottom: .65rem; }
    .hero-heading { color: white; font-size: 2.25rem; font-weight: 800; line-height: 1.18; letter-spacing: -.035em; margin-bottom: .7rem; max-width: 700px; }
    .hero-description { color: #f5f0fb; font-size: .93rem; line-height: 1.65; max-width: 720px; }

    .section-label { color: #7458a8; font-size: .66rem; font-weight: 800; letter-spacing: .14em; margin-top: 0; margin-bottom: .18rem; }
    .section-heading { color: var(--ink); font-size: 1.45rem; font-weight: 800; letter-spacing: -.02em; margin-bottom: .2rem; }
    .section-description { color: var(--muted); font-size: .86rem; line-height: 1.55; margin-bottom: .55rem; }

    div[data-testid="stTextInput"] input {
        background: white !important; color: #172033 !important; -webkit-text-fill-color: #172033 !important;
        border: 1px solid #d7cde5; border-radius: 11px; min-height: 48px; font-size: .92rem;
        caret-color: #172033 !important;
    }
    div[data-testid="stTextInput"] input:focus { border-color: #8067b8; box-shadow: 0 0 0 3px rgba(128,103,184,.12); }
    div[data-baseweb="input"] input::placeholder { color: #7a8496 !important; -webkit-text-fill-color: #7a8496 !important; opacity: 1 !important; }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: white !important; border: 1px solid #d7cde5 !important; border-radius: 10px !important;
        min-height: 44px !important; color: #172033 !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p { color: #172033 !important; font-size: .86rem !important; }
    div[data-testid="stSelectbox"] svg { color: #7056a5 !important; }

    div[data-testid="stButton"] > button {
        border-radius: 12px !important; border: 1px solid #d6c6e8 !important;
        font-weight: 700 !important; min-height: 44px !important; font-size: .86rem !important;
        background: #f3edf9 !important; color: #4a3865 !important;
        -webkit-text-fill-color: #4b3d61 !important; box-shadow: 0 3px 9px rgba(80,55,112,.05) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #e8def3 !important; border-color: #bda7d7 !important; color: #352744 !important;
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] button, div[data-testid="stButton"] button * {
        color: #4b3d61 !important; -webkit-text-fill-color: #4b3d61 !important;
    }
    /* Buttons: enforce readable labels and preserve contrast in every state. */
    div[data-testid="stButton"] > button {
        border-radius: 12px !important; border: 1px solid #d6c6e8 !important;
        font-weight: 700 !important; min-height: 44px !important; font-size: .86rem !important;
        background: #f3edf9 !important; color: #4b3d61 !important;
        -webkit-text-fill-color: #4b3d61 !important; box-shadow: 0 3px 9px rgba(80,55,112,.05) !important;
        opacity: 1 !important; visibility: visible !important;
    }
    div[data-testid="stButton"] > button *,
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span {
        color: #4b3d61 !important; -webkit-text-fill-color: #4b3d61 !important;
        opacity: 1 !important; visibility: visible !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #e8def3 !important; border-color: #bda7d7 !important; color: #352744 !important;
    }

    /* Native Streamlit link buttons: explicit foreground/background contrast. */
    div[data-testid="stLinkButton"] a,
    div[data-testid="stLinkButton"] a:link,
    div[data-testid="stLinkButton"] a:visited,
    div[data-testid="stLinkButton"] a:hover,
    div[data-testid="stLinkButton"] a:focus {
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        gap: .45rem !important; min-height: 44px !important; padding: .55rem 1rem !important;
        background: #5d4387 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #5d4387 !important; border-radius: 10px !important; font-weight: 700 !important;
        font-size: .86rem !important; line-height: 1.35 !important; opacity: 1 !important;
        visibility: visible !important; text-decoration: none !important;
        box-shadow: 0 3px 10px rgba(73,53,107,.12) !important;
    }
    div[data-testid="stLinkButton"] a *,
    div[data-testid="stLinkButton"] a p,
    div[data-testid="stLinkButton"] a span,
    div[data-testid="stLinkButton"] a div,
    div[data-testid="stLinkButton"] a svg {
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; fill: #ffffff !important;
        opacity: 1 !important; visibility: visible !important;
    }
    div[data-testid="stLinkButton"] a:hover { background: #493267 !important; border-color: #493267 !important; }

    /* The primary search action is the only solid-purple Streamlit button. */
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button,
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button *,
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button p,
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button span,
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button[kind="primary"],
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button[kind="primary"] * {
        background: #7051a1 !important; border-color: #7051a1 !important;
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; fill: #ffffff !important;
        opacity: 1 !important; visibility: visible !important;
    }
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button { padding-left: 1.15rem !important; padding-right: 1.15rem !important; }
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button:hover,
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button:hover * {
        background: #593d86 !important; border-color: #593d86 !important;
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    }
    div[data-testid="stButton"]:has(button[aria-label="Search"] ) > button:hover { background: #5f438d !important; border-color: #5f438d !important; }

    /* Quick-topic buttons: soft lavender cards, visually distinct from the primary action. */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #eee6f7 !important;
        border-color: #d3c1e7 !important;
        color: #493660 !important;
        -webkit-text-fill-color: #493660 !important;
        box-shadow: 0 4px 12px rgba(91,65,125,.07) !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: #e5d9f1 !important;
        border-color: #bca5d4 !important;
    }

    /* Explicit main-content typography: prevent Streamlit/theme defaults from making
       educational tools and tab content white or low-contrast. */
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] li,
    .main [data-testid="stMarkdownContainer"] strong,
    .main [data-testid="stMarkdownContainer"] em,
    .main [data-testid="stCaptionContainer"] p {
        color: #46506a !important;
        -webkit-text-fill-color: #46506a !important;
    }
    .main [data-testid="stMarkdownContainer"] h1,
    .main [data-testid="stMarkdownContainer"] h2,
    .main [data-testid="stMarkdownContainer"] h3,
    .main [data-testid="stMarkdownContainer"] h4 {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }
    .main [data-testid="stTabs"] button[role="tab"] {
        color: #5f5270 !important;
        -webkit-text-fill-color: #5f5270 !important;
        font-weight: 700 !important;
    }
    .main [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #6d56a6 !important;
        -webkit-text-fill-color: #6d56a6 !important;
        border-bottom-color: #8067b8 !important;
    }
    .main [data-testid="stRadio"] label,
    .main [data-testid="stRadio"] label p,
    .main [data-testid="stRadio"] [role="radio"] {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }
    .main [data-testid="stRadio"] [role="radio"][aria-checked="true"] {
        background: #eee7f8 !important;
        border-color: #8067b8 !important;
    }
    /* Fallback selectors for current Streamlit DOM structure. */
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
        color: #46506a !important;
        -webkit-text-fill-color: #46506a !important;
    }
    [data-testid="stMain"] [data-testid="stTabs"] button[role="tab"] span {
        color: #5f5270 !important;
        -webkit-text-fill-color: #5f5270 !important;
    }
    [data-testid="stMain"] [data-testid="stTabs"] button[role="tab"][aria-selected="true"] span {
        color: #6d56a6 !important;
        -webkit-text-fill-color: #6d56a6 !important;
    }
    [data-testid="stMain"] [data-testid="stRadio"] label * {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }
    .main .tool-card, .main .tool-card * {
        color: #465c6d !important;
        -webkit-text-fill-color: #465c6d !important;
    }
    .main .tool-card strong { color: #34264f !important; -webkit-text-fill-color: #34264f !important; }
    .main [data-testid="stAlert"] p, .main [data-testid="stAlert"] div, .main [data-testid="stAlert"] span { color: #46506a !important; -webkit-text-fill-color: #46506a !important; }
    .main .section-heading, .main .result-title, .main .medical-heading,
    .main .source-heading, .main .ai-heading, .main .safety-heading,
    .main .crisis-heading, .main .emergency-heading {
        color: #34264f !important; -webkit-text-fill-color: #34264f !important;
    }

    /* Streamlit native controls: keep labels/text visible on the lilac theme. */
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] span {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }
    div[data-testid="stRadio"] label, div[data-testid="stRadio"] label p {
        color: #34264f !important;
        -webkit-text-fill-color: #34264f !important;
    }

    .examples {
        color: #756987 !important;
        -webkit-text-fill-color: #756987 !important;
        font-size: .78rem !important;
        margin-top: .15rem !important;
        margin-bottom: .55rem !important;
    }

    .examples { color: #5f5270 !important; -webkit-text-fill-color: #5f5270 !important; font-size: .82rem; line-height: 1.45; margin: .35rem 0 .5rem; }
    .learning-intro { margin-top: .15rem; margin-bottom: .7rem; }
    .learning-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .85rem; margin: .55rem 0 .8rem; }
    .learning-card {
        background: #fffdfd; border: 1px solid #ddd2e9; border-radius: 14px; padding: 1rem 1.05rem;
        box-shadow: 0 4px 14px rgba(72,51,105,.045); min-height: 116px;
    }
    .learning-card-kicker { color: #7657a8; font-size: .62rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .25rem; }
    .learning-card-title { color: #34264f; font-size: .96rem; font-weight: 800; margin-bottom: .3rem; }
    .learning-card-body { color: #625b70 !important; -webkit-text-fill-color: #625b70 !important; font-size: .79rem; line-height: 1.52; }
    .mode-focus { background: #f5effb; border: 1px solid #ded1ec; border-radius: 11px; padding: .72rem .9rem; margin: .4rem 0 .8rem; }
    .mode-focus-title { color: #4b3868; font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .18rem; }
    .mode-focus-body { color: #625b70 !important; -webkit-text-fill-color: #625b70 !important; font-size: .8rem; line-height: 1.48; }
    .tool-divider { border-top: 1px solid #e2d9ed; margin: .75rem 0 .75rem; }
    .tool-card { background: #fff; border: 1px solid #d9d0e5; border-radius: 12px; padding: 1.1rem 1.2rem; color: #465c6d; box-shadow: 0 5px 18px rgba(72,51,105,.06); }
    .tool-card-title { color: #34264f !important; font-size: 1rem; font-weight: 800; margin: 0 0 .65rem 0; }
    .tool-card-body { color: #465c6d !important; line-height: 1.65; white-space: normal; }
    .tool-card-list { color: #465c6d !important; margin: .2rem 0 0 1.1rem; padding: 0; }
    .tool-card-list li { color: #465c6d !important; margin: .35rem 0; line-height: 1.55; }
    .tool-card strong, .tool-card p, .tool-card li { color: #465c6d !important; -webkit-text-fill-color: #465c6d !important; }
    .tool-card h3, .tool-card h4 { color: #34264f !important; -webkit-text-fill-color: #34264f !important; }

    div[data-testid="stRadio"] [role="radiogroup"] { gap: .45rem; }
    div[data-testid="stRadio"] label { background: #faf7fd; border: 1px solid #ddd2eb; border-radius: 9px; padding: .35rem .65rem; }
    div[data-testid="stRadio"] label, div[data-testid="stRadio"] label p, div[data-testid="stRadio"] label span { color: #34264f !important; -webkit-text-fill-color: #34264f !important; }

    .medical-card, .source-box, .safety-box, .empty-box, .ai-box, .crisis-box, .emergency-box {
        background: var(--surface); border: 1px solid #d9d0e5; border-radius: 12px;
        box-shadow: 0 5px 18px rgba(72,51,105,.06);
    }
    .medical-card { padding: 1.25rem 1.35rem; margin: 0 0 .9rem; min-height: 120px; }
    .medical-heading { color: var(--ink); font-size: 1rem; font-weight: 800; line-height: 1.35; margin-bottom: .55rem; }
    .medical-body { color: #465c6d; font-size: .88rem; line-height: 1.72; }
    .medical-paragraph { margin: 0 0 .75rem; }
    .medical-list { margin: .1rem 0 .7rem 1.15rem; padding: 0; }
    .medical-list li { margin-bottom: .35rem; }

    .result-label { color: var(--teal); font-size: .64rem; font-weight: 800; letter-spacing: .14em; margin-top: .2rem; }
    .result-title { color: var(--ink); font-size: 1.65rem; font-weight: 800; line-height: 1.25; margin: .3rem 0 .3rem; }
    .result-meta { color: #78909f; font-size: .76rem; line-height: 1.5; margin-bottom: 1rem; }

    .source-box { padding: 1.1rem 1.25rem; margin-top: 1.5rem; margin-bottom: .65rem; }
    .source-heading { color: var(--ink); font-size: .98rem; font-weight: 800; margin-bottom: .35rem; }
    .source-description { color: var(--muted); font-size: .82rem; line-height: 1.55; }
    .source-actions { margin-top: .55rem; }
    .source-citation { margin: .15rem 0 1rem; padding: .8rem 1rem; background: #faf8fd; border: 1px solid #e5dcef; border-radius: 10px; color: #4b4560; font-size: .82rem; line-height: 1.6; overflow-wrap: anywhere; }
    .source-citation strong { display: block; margin-bottom: .2rem; color: #34264f !important; -webkit-text-fill-color: #34264f !important; }
    .source-citation a { color: #514077 !important; -webkit-text-fill-color: #514077 !important; text-decoration: underline; }

    .ai-box { padding: 1rem 1.15rem; margin: 1rem 0; background: #faf8fd; }
    .ai-heading, .safety-heading, .crisis-heading, .emergency-heading { color: var(--ink); font-size: .94rem; font-weight: 800; margin-bottom: .3rem; }
    .ai-description, .safety-description, .crisis-description, .emergency-description { color: #526979; font-size: .82rem; line-height: 1.55; }

    .empty-box { padding: 1.4rem; margin-top: 1rem; }
    .empty-heading { color: var(--ink); font-size: .98rem; font-weight: 800; margin-bottom: .35rem; }
    .empty-description { color: var(--muted); font-size: .84rem; line-height: 1.6; }

    .trusted-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .65rem; margin: .7rem 0 1.5rem; }
    .trusted-card {
        display: block; background: white; border: 1px solid var(--line); border-radius: 11px; padding: .8rem .9rem;
        text-decoration: none !important; box-shadow: 0 3px 12px rgba(24,50,74,.035); transition: transform .15s ease, border-color .15s ease;
    }
    .trusted-card:hover { transform: translateY(-2px); border-color: #bca9d6; }
    .trusted-name { color: #5f4788; font-size: .82rem; font-weight: 800; }
    .trusted-desc { color: #788b98; font-size: .7rem; margin-top: .2rem; line-height: 1.35; }

    .app-footer { color: #81778f; font-size: .72rem; text-align: center; border-top: 1px solid #ddd5ea; padding-top: 1.2rem; margin-top: 2rem; }

    /* Even page framing and Streamlit toolbar clearance */
    [data-testid="stAppViewContainer"] .main .block-container {
        border-left: 1px solid #e5deed;
        border-right: 1px solid #e5deed;
        background: rgba(255,255,255,.34);
        box-sizing: border-box;
    }
    [data-testid="stHeader"] { background: rgba(251,249,253,.96) !important; border-bottom: 1px solid #e5deed; }

    @media (max-width: 760px) {
        .block-container { padding-top: 4rem; }
        .hero-box { padding: 2rem 1.45rem; border-radius: 18px; min-height: 0; }
        .hero-heading { font-size: 1.8rem; max-width: 100%; }
        .trusted-grid { grid-template-columns: repeat(2, 1fr); }
        .medical-card { padding: 1rem; }
        .hero-photo { position: relative; right: auto; top: auto; width: 100%; height: 210px; margin: 1rem 0 0; object-fit: cover; object-position: center 24%; }
        .learning-grid { grid-template-columns: 1fr; }
        .hero-box > div[style*="padding-right"] { padding-right: 0 !important; }
    }

    /* Accessibility refinements: visible keyboard focus, reduced motion and print. */
    :focus-visible { outline: 3px solid #5d4a8c !important; outline-offset: 3px !important; }
    a { text-underline-offset: 3px; }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
    }
    @media print {
        [data-testid="stSidebar"], [data-testid="stHeader"], button, input, textarea, select { display: none !important; }
        .block-container { max-width: 100% !important; padding: 0 !important; }
        .medical-card, .source-box, .tool-card { break-inside: avoid; box-shadow: none !important; }
        body { background: #ffffff !important; color: #111111 !important; }
    }

    /* High-specificity contrast rules for Streamlit source-link buttons. */
    [data-testid="stMain"] [data-testid="stLinkButton"] a,
    [data-testid="stMain"] [data-testid="stLinkButton"] a:link,
    [data-testid="stMain"] [data-testid="stLinkButton"] a:visited,
    [data-testid="stMain"] [data-testid="stLinkButton"] a:hover,
    [data-testid="stMain"] [data-testid="stLinkButton"] a:focus {
        background-color: #5d4387 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #5d4387 !important;
        opacity: 1 !important;
        visibility: visible !important;
        text-decoration: none !important;
        font-weight: 700 !important;
    }
    [data-testid="stMain"] [data-testid="stLinkButton"] a *,
    [data-testid="stMain"] [data-testid="stLinkButton"] a p,
    [data-testid="stMain"] [data-testid="stLinkButton"] a span,
    [data-testid="stMain"] [data-testid="stLinkButton"] a div,
    [data-testid="stMain"] [data-testid="stLinkButton"] a svg {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        fill: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stMain"] [data-testid="stLinkButton"] a:hover {
        background-color: #493267 !important;
        border-color: #493267 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def normalize_text(text):
    text = html.unescape(text or "").lower()
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_sentence_boundaries(text):
    """Repair missing whitespace between adjacent source sentences without changing punctuation."""
    text = text or ""
    # Source summaries occasionally join sentence endings directly to the next
    # sentence (for example, "What is asthma?Asthma is ...").
    text = re.sub(r"([.!?])([A-Z][a-z])", r"\1 \2", text)
    # Also repair the common HTML-decoding case where punctuation is followed
    # immediately by a quote/closing parenthesis and then a new capitalized sentence.
    return text


def clean_html(text):
    """Decode MedlinePlus HTML and preserve readable sentence/paragraph boundaries."""
    text = text or ""
    for _ in range(3):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded

    # HTML paragraphs/headings are often concatenated in the XML summary.
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<(?:p|div|li|h[1-6]|ul|ol|section|article|tr)\b[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"</(?:p|div|li|h[1-6]|ul|ol|section|article|tr)\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<li\b[^>]*>", "• ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = normalize_sentence_boundaries(text)
    return text.strip()



# ============================================================
# LANGUAGE / SEARCH HELPERS
# ============================================================


def ui_text(key, language_code="en"):
    return UI_TRANSLATIONS.get(language_code, UI_TRANSLATIONS["en"]).get(key, UI_TRANSLATIONS["en"].get(key, key))


def expand_topic(topic):
    """Return the user's wording plus carefully matched medical aliases.

    Whole-phrase matching avoids accidental substring matches (for example,
    the abbreviation "MI" must not match the word "migraine").
    """
    original = (topic or "").strip()
    normalized = normalize_text(original)
    if not normalized:
        return []

    expansions = []
    seen = set()

    def add(value):
        value = (value or "").strip()
        key = normalize_text(value)
        if key and key not in seen:
            seen.add(key)
            expansions.append(value)

    add(original)
    add(normalized)

    # Longer phrases are checked first so specific aliases win over broad ones.
    for phrase, canonical in sorted(SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        phrase_norm = normalize_text(phrase)
        if not phrase_norm:
            continue
        if re.search(r"(?<!\w)" + re.escape(phrase_norm) + r"(?!\w)", normalized):
            add(canonical)

    # If the query is a canonical term, also try common patient-language aliases.
    for phrase, canonical in sorted(SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        if normalized == normalize_text(canonical):
            add(phrase)

    return expansions[:6]


@st.cache_data(ttl=3600, show_spinner=False)
def translate_text(text, target_language, source_language="en"):
    """Fast, best-effort translation with a short timeout.

    Translation is never allowed to block or erase the medical result.
    Text is translated in small chunks and requests are attempted in parallel.
    """
    if not text or target_language == source_language:
        return text

    chunks = [c for c in re.split(r"(\n\n|\n)", text) if c]

    def translate_chunk(chunk):
        if not chunk.strip() or len(chunk.strip()) < 2:
            return chunk
        source_chunk = chunk[:2500]
        try:
            response = requests.get(
                GOOGLE_TRANSLATE_URL,
                params={
                    "client": "gtx",
                    "sl": source_language,
                    "tl": target_language,
                    "dt": "t",
                    "q": source_chunk,
                },
                timeout=4,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data and isinstance(data[0], list):
                parts = [str(x[0]) for x in data[0] if isinstance(x, list) and x and x[0]]
                result = "".join(parts).strip()
                if result:
                    return result
        except (requests.RequestException, ValueError, TypeError, IndexError):
            pass
        return None

    # Keep the app responsive on phones and slow networks.
    from concurrent.futures import ThreadPoolExecutor
    results = [None] * len(chunks)
    work = [(i, c) for i, c in enumerate(chunks) if c.strip()]
    with ThreadPoolExecutor(max_workers=min(6, max(1, len(work)))) as executor:
        futures = {executor.submit(translate_chunk, c): i for i, c in work}
        for future, i in [(f, futures[f]) for f in futures]:
            try:
                results[i] = future.result()
            except Exception:
                results[i] = None

    if not any(r for r in results):
        return text
    return "".join(r if r is not None else chunks[i] for i, r in enumerate(results))


@st.cache_data(ttl=3600, show_spinner=False)
def translate_query_to_english(query, source_language):
    """Translate a user's non-English search query into English for MedlinePlus."""
    if not query or source_language == "en":
        return query
    try:
        response = requests.get(
            GOOGLE_TRANSLATE_URL,
            params={
                "client": "gtx",
                "sl": source_language,
                "tl": "en",
                "dt": "t",
                "q": query[:500],
            },
            timeout=4,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and data and isinstance(data[0], list):
            result = "".join(
                str(x[0]) for x in data[0] if isinstance(x, list) and x and x[0]
            ).strip()
            return result or query
    except (requests.RequestException, ValueError, TypeError, IndexError):
        pass
    return query


def safe_source_url(url):
    """Allow HTTPS links only to the real MedlinePlus domain or its subdomains."""
    if not url:
        return None
    try:
        cleaned = html.unescape(url).strip()
        parsed = urlparse(cleaned)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme == "https" and (hostname == "medlineplus.gov" or hostname.endswith(".medlineplus.gov")):
            return cleaned
    except (ValueError, TypeError):
        pass
    return None


def render_source_link_button(label, url):
    """Render a visible source link as HTML rather than Streamlit's link-button widget."""
    safe_url = safe_source_url(url)
    if not safe_url:
        return False
    # Escape both values before embedding them in HTML. The URL validator above
    # restricts destinations to HTTPS MedlinePlus pages.
    href = html.escape(safe_url, quote=True)
    visible_label = html.escape(str(label), quote=True)
    st.markdown(
        f'<a href="{href}" target="_blank" rel="noopener noreferrer" '
        'style="display:inline-flex !important; align-items:center !important; '
        'justify-content:center !important; box-sizing:border-box !important; '
        'min-height:46px !important; padding:0.7rem 1.1rem !important; '
        'margin:0.25rem 0 0.75rem 0 !important; border-radius:10px !important; '
        'border:1px solid #5d4387 !important; background:#5d4387 !important; '
        'color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; '
        'font-size:16px !important; font-weight:700 !important; line-height:1.4 !important; '
        'text-decoration:none !important; opacity:1 !important; visibility:visible !important; '
        'position:relative !important; z-index:2 !important;">'
        f'<span style="color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; '
        f'opacity:1 !important; visibility:visible !important;">{visible_label}</span></a>',
        unsafe_allow_html=True,
    )
    return True


def source_navigation_links(topic):
    """Build query-specific links to trusted organizations; these are not cited sources."""
    query = quote((topic or "").strip())
    return [
        ("CDC", f"https://www.cdc.gov/search/?query={query}"),
        ("NIH", f"https://search.nih.gov/search?affiliate=nih&query={query}"),
        ("FDA", f"https://www.fda.gov/search?s={query}"),
        ("NIMH", f"https://www.nimh.nih.gov/search?query={query}"),
    ]

# ============================================================
# SAFETY CLASSIFICATION
# ============================================================

CRISIS_PATTERNS = [
    r"\bi want to kill myself\b",
    r"\bi want to die\b",
    r"\bi am suicidal\b",
    r"\bi'm suicidal\b",
    r"\bsuicidal thoughts?\b",
    r"\bthinking about suicide\b",
    r"\bthinking of suicide\b",
    r"\bthinking about killing myself\b",
    r"\bthinking of killing myself\b",
    r"\bwant to hurt myself\b",
    r"\b(?:want|wants) to hurt (?:myself|himself|herself|themselves)\b",
    r"\b(?:might|may|going to|plan to|planning to) hurt myself\b",
    r"\b(?:i )?hurt myself\b",
    r"\bi want to hurt myself\b",
    r"\bi don't want to live(?: anymore)?\b",
    r"\bi don't want to be alive\b",
    r"\bi wish i were dead\b",
    r"\bi would be better off dead\b",
    r"\bi want to end my life\b",
    r"\bi plan to end my life\b",
    r"\bi am going to end my life\b",
    r"\b(?:suicide plan|plan to commit suicide)\b",
    r"\bself[- ]harm\b",
    r"\bself[- ]harming\b",
    r"\bcut myself\b",
]

ACUTE_PATTERNS = [
    r"\bi (?:think|think i'm|think i am|feel like) .*?\b(?:having|getting)\b .*?\b(?:heart attack|stroke)\b",
    r"\bmy face is drooping\b",
    r"\bmy (?:face|arm|leg) (?:is|feels|feeling) numb\b",
    r"\bmy arm is numb\b",
    r"\bmy chest hurts\b",
    r"\bmy chest is hurting\b",
    r"\b(?:really bad|severe|crushing) chest pain\b",
    r"\bi can't breathe\b",
    r"\bi cannot breathe\b",
    r"\bi am having trouble breathing\b",
    r"\btrouble breathing\b",
    r"\bdifficulty breathing\b",
    r"\bshortness of breath\b",
    r"\banaphylaxis\b",
    r"\bsevere allergic reaction\b",
    r"\bswallowed (?:bleach|poison|cleaner|cleaning product)\b",
    r"\bdrank (?:bleach|poison|cleaner|cleaning product)\b",
    r"\bingested (?:bleach|poison|cleaner|cleaning product)\b",
    r"\bpassed out\b",
    r"\bunconscious\b",
    r"\bsevere bleeding\b",
    r"\bbleeding won't stop\b",
    r"\bmy lips? (?:are|is) (?:turning )?blue\b",
    r"\bmy throat is closing\b",
    r"\bseizure (?:right now|currently)\b",
    r"\bi took too many pills\b",
    r"\bi overdosed\b",
    r"\b(?:overdose|poisoning) and (?:can't|cannot) breathe\b",
]

# These phrases are intentionally NOT emergency triggers by themselves:
# "heart attack", "seizure", "opioid overdose prevention", etc.
# Educational queries should remain searchable.

PERSONAL_PATTERNS = [
    r"\bdo i have\b",
    r"\bcould i have\b",
    r"\bam i having\b",
    r"\bis this serious for me\b",
    r"\bis this safe for me\b",
    r"\bwhat should i take\b",
    r"\bwhat medication should i take\b",
    r"\bwhat medicine should i take\b",
    r"\bwhat dose should i take\b",
    r"\bcan i take [a-zA-Z]+\b",
    r"\bis [a-zA-Z]+ safe for me\b",
    r"\bcan i use this medication\b",
    r"\bis it safe for me to take this\b",
    r"\bhow much .*medication\b",
    r"\bshould i stop taking\b",
    r"\bshould i change my medication\b",
    r"\bcan i stop taking\b",
    r"\bcan i eat .* if i have\b",
    r"\bi have .* can i\b",
    r"\bmy symptoms\b",
    r"\bwhat do my (?:lab|test) results mean for me\b",
    r"\bshould i increase my dose\b",
    r"\bshould i lower my dose\b",
    r"\bcan i mix .*medications?\b",
    r"\bwhat treatment is best for me\b",
]

def matches_any(text, patterns):
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized, re.I) for pattern in patterns)


def classify_safety(text):
    """
    Return one of:
      crisis
      emergency
      personal
      none

    The classifier is intentionally context-aware:
    educational mentions such as "heart attack" alone do not
    trigger an emergency banner.
    """
    if matches_any(text, CRISIS_PATTERNS):
        return "crisis"

    if matches_any(text, ACUTE_PATTERNS):
        return "emergency"

    if matches_any(text, PERSONAL_PATTERNS):
        return "personal"

    return "none"


# ============================================================
# MEDLINEPLUS SEARCH
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def search_medlineplus(topic):
    """Search MedlinePlus health topics and rank candidates by query relevance.

    Returns a result dictionary, None for a genuine no-match, or a dictionary
    with ``_search_error`` when every attempted request failed. This lets the UI
    distinguish a network outage from a topic that was not found.
    """
    query_variants = expand_topic(topic)
    if not query_variants:
        return None

    candidates = {}
    request_succeeded = False
    request_errors = 0

    for query in query_variants[:5]:
        params = {"db": "healthTopics", "term": query, "retmax": 10}
        try:
            response = requests.get(MEDLINEPLUS_SEARCH_URL, params=params, timeout=8)
            response.raise_for_status()
            root = ET.fromstring(response.text)
            request_succeeded = True
        except (requests.RequestException, ET.ParseError, ValueError):
            request_errors += 1
            continue

        query_norm = normalize_text(query)
        query_tokens = {token for token in query_norm.split() if len(token) >= 2}
        if not query_tokens:
            continue

        for document in root.findall(".//document"):
            title_element = document.find("content[@name='title']")
            summary_element = document.find("content[@name='FullSummary']")
            if title_element is None or summary_element is None:
                continue

            title = clean_html(title_element.text or "")
            summary = clean_html(summary_element.text or "")
            source_url = safe_source_url(document.get("url"))
            if not title or not summary or not source_url:
                continue

            title_norm = normalize_text(title)
            summary_norm = normalize_text(summary)
            title_tokens = set(title_norm.split())
            summary_tokens = set(summary_norm.split())
            title_overlap = len(query_tokens & title_tokens)
            summary_overlap = len(query_tokens & summary_tokens)
            coverage = title_overlap / max(1, len(query_tokens))
            exact_phrase = bool(query_norm and (query_norm in title_norm or title_norm in query_norm))
            score = (title_overlap * 5) + min(summary_overlap, 8) + (coverage * 8)
            if exact_phrase:
                score += 12
            if title_norm == query_norm:
                score += 10
            if query_norm != normalize_text(topic):
                score += 1  # Slightly reward a successful synonym query, not enough to dominate relevance.

            existing = candidates.get(source_url)
            candidate = {"title": title, "summary": summary, "url": source_url, "score": score}
            if existing is None or score > existing["score"]:
                candidates[source_url] = candidate

    if not candidates:
        if not request_succeeded and request_errors:
            return {"_search_error": True}
        return None

    ranked = sorted(candidates.values(), key=lambda item: item["score"], reverse=True)
    best = ranked[0]
    query_tokens = {token for token in normalize_text(topic).split() if len(token) >= 2}
    best_title_tokens = set(normalize_text(best["title"]).split())
    overlap = len(query_tokens & best_title_tokens)

    # For multi-word queries, reject results that share no meaningful title terms.
    # This is a conservative relevance gate; it is not a medical accuracy score.
    if len(query_tokens) >= 2 and overlap == 0 and best["score"] < 8:
        return None

    best["alternatives"] = [item for item in ranked[1:4] if item["score"] >= max(6, best["score"] * 0.55)]
    return best


# ============================================================
# CONTENT FORMATTING
# ============================================================

HEADING_PATTERNS = [
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
    r"What are the complications of [^?]+\?",
]

def format_medical_content(text):
    text = text.strip()

    if not text:
        return []

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    combined = "(" + "|".join(HEADING_PATTERNS) + ")"
    matches = list(re.finditer(combined, text, flags=re.I))

    if not matches:
        return [("Medical information", text)]

    sections = []

    if matches[0].start() > 0:
        intro = text[:matches[0].start()].strip()
        if intro:
            sections.append(("Overview", intro))

    for index, match in enumerate(matches):
        heading = match.group().strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        if content:
            sections.append((heading, content))

    return sections


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
    if "complications" in lower:
        return "Possible complications"

    return heading


def display_content(content):
    """
    Preserve paragraphs and simple lists instead of flattening
    all line breaks into one paragraph.
    """
    content = normalize_sentence_boundaries(clean_html(content)).strip()

    if not content:
        return ""

    blocks = re.split(r"\n\s*\n", content)
    html_parts = []

    for block in blocks:
        block = block.strip()

        if not block:
            continue

        lines = [
            re.sub(r"\s+", " ", line.strip())
            for line in block.splitlines()
            if line.strip()
        ]

        bullet_lines = [
            re.sub(r"^(?:[-•*]|\d+[.)])\s*", "", line)
            for line in lines
            if re.match(r"^(?:[-•*]|\d+[.)])\s+", line)
        ]

        if bullet_lines and len(bullet_lines) == len(lines):
            items = "".join(f"<li>{html.escape(item)}</li>" for item in bullet_lines)
            html_parts.append(f'<ul class="medical-list">{items}</ul>')
        else:
            paragraph = html.escape(" ".join(lines))
            html_parts.append(
                f'<p class="medical-paragraph">{paragraph}</p>'
            )

    return "".join(html_parts)


# ============================================================
# PATIENT SUMMARY EXPORT + OPTIONAL LOCAL AI (NO API BILL)
# ============================================================

def make_patient_summary_pdf(topic, title, information, source_url, language_name="English"):
    """Create a simple printable PDF. Requires the free reportlab package."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    except ImportError:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=0.62*inch, leftMargin=0.62*inch,
        topMargin=0.55*inch, bottomMargin=0.55*inch,
        title=f"CareClarity - {title}", author="CareClarity"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CCBrand", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#49347A"), alignment=TA_LEFT, spaceAfter=5))
    styles.add(ParagraphStyle(name="CCSub", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#55516A"), spaceAfter=8))
    styles.add(ParagraphStyle(name="CCHeading", parent=styles["Heading2"], fontSize=12, leading=15, textColor=colors.HexColor("#49347A"), spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="CCBody", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=5))
    story = [Paragraph("CareClarity", styles["CCBrand"]),
             Paragraph("Patient education summary · General information, not a diagnosis", styles["CCSub"]),
             HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D8CDEB")), Spacer(1, 7),
             Paragraph(html.escape(title), styles["Heading1"]),
             Paragraph(f"Search topic: {html.escape(topic)} · Display language: {html.escape(language_name)}", styles["CCSub"]),
             Paragraph("In plain language", styles["CCHeading"])]
    sentences = extract_sentences(information)
    overview = " ".join(sentences[:3]) if sentences else information[:900]
    story.append(Paragraph(html.escape(overview), styles["CCBody"]))
    story.append(Paragraph("Key points", styles["CCHeading"]))
    for item in key_takeaways(information, limit=4):
        story.append(Paragraph("- " + html.escape(item), styles["CCBody"]))
    story.append(Paragraph("Questions to discuss with a healthcare professional", styles["CCHeading"]))
    for q in appointment_questions(title)[:4]:
        story.append(Paragraph("[ ] " + html.escape(q), styles["CCBody"]))
    story.append(Paragraph("Source and limitations", styles["CCHeading"]))
    story.append(Paragraph("Primary source: MedlinePlus, U.S. National Library of Medicine. Retrieved " + datetime.date.today().isoformat() + ". This is the retrieval date, not a medical review date.", styles["CCBody"]))
    story.append(Paragraph(html.escape(source_url if safe_source_url(source_url) else "https://medlineplus.gov/"), styles["CCBody"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("This summary is for general education only. It does not diagnose a condition or replace advice from a qualified healthcare professional. Do not use it to start, stop, or change treatment.", styles["CCSub"]))
    doc.build(story)
    return buffer.getvalue()


def get_local_ai_explanation(topic, source_text, source_url):
    """Use a locally installed Ollama model; no paid API or cloud transfer."""
    base_url = str(get_secret("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
    model = str(get_secret("OLLAMA_MODEL", "llama3.2:3b"))
    prompt = f"""Rewrite this source material into a concise patient-friendly educational explanation. Use only information explicitly supported by the source. Do not diagnose, personalize treatment, recommend medication or dosage, or invent facts. If information is missing, say the source does not specify. Do not claim to have verified facts outside the supplied text. Include: Plain-language overview, 3 key points, 3 questions to ask a healthcare professional. End by saying this is general education, not medical advice.\n\nTopic: {topic}\nSource URL: {source_url}\nSource text:\n{source_text[:10000]}"""
    try:
        response = requests.post(
            base_url + "/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}},
            timeout=90,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        return (answer, "enabled") if answer else (None, "empty")
    except requests.ConnectionError:
        return None, "not_running"
    except requests.Timeout:
        return None, "timeout"
    except requests.HTTPError as exc:
        # Ollama returns a useful JSON message when the configured model is
        # missing; preserve that diagnosis instead of hiding it behind a generic
        # failure message.
        detail = ""
        try:
            detail = str(exc.response.json().get("error", ""))[:240]
        except (AttributeError, ValueError, TypeError):
            detail = ""
        if "model" in detail.lower() and ("not found" in detail.lower() or "pull" in detail.lower()):
            return None, "model_missing"
        return None, "http_error: " + detail if detail else "http_error"
    except (requests.RequestException, ValueError, TypeError) as exc:
        return None, "error: " + str(exc)[:180]


# ============================================================
# AI EXPLANATION
# ============================================================

def get_secret(name, default=None):
    try:
        value = st.secrets.get(name, default)
        return value
    except Exception:
        return default


def extract_response_text(data):
    """
    Extract text from a raw Responses API response without
    requiring the OpenAI Python package.
    """
    if isinstance(data.get("output_text"), str):
        return data["output_text"].strip()

    parts = []

    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                parts.append(text)

    return "\n".join(parts).strip()


def get_ai_explanation(topic, source_text, source_url):
    api_key = get_secret("OPENAI_API_KEY")

    if not api_key:
        return None, "disabled"

    model = get_secret("OPENAI_MODEL", DEFAULT_AI_MODEL)

    prompt = f"""
You are a source-grounded patient education assistant.

Topic:
{topic}

Primary source:
MedlinePlus / U.S. National Library of Medicine
{source_url or "MedlinePlus health information"}

Source content:
{source_text}

Create a concise patient-friendly explanation.

STRICT RULES:
- Use only facts supported by the source content.
- Do not diagnose the user.
- Do not say or imply the user has the condition.
- Do not recommend a medication or dosage.
- Do not tell someone to start, stop, or change medication.
- Do not provide individualized treatment advice.
- Do not invent facts, statistics, or risk estimates.
- Preserve important uncertainty.
- Do not cite sources other than the supplied MedlinePlus source.
- If the source does not contain enough information for a section, say so.

Return these sections:

### In plain language
2-4 sentences.

### Key points
3-5 concise bullet points.

### When to talk with a healthcare professional
General guidance supported by the source. Do not give individualized advice.

End with:
"This is general health education, not a diagnosis or personalized medical advice."
"""

    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 700,
    }

    try:
        response = requests.post(
            OPENAI_RESPONSES_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text = extract_response_text(data)

        if not text:
            return None, "empty"

        return text, "enabled"

    except requests.RequestException:
        return None, "error"
    except (ValueError, TypeError, KeyError):
        return None, "error"



# ============================================================
# AUTOMATED SAFETY EVALUATION
# ============================================================

SAFETY_TEST_CASES = [
    # 25 crisis cases
    ("crisis", "I want to kill myself"), ("crisis", "I want to die"),
    ("crisis", "I am suicidal"), ("crisis", "I'm suicidal"),
    ("crisis", "I have suicidal thoughts"), ("crisis", "suicidal thought"),
    ("crisis", "thinking about suicide"), ("crisis", "thinking of suicide"),
    ("crisis", "thinking about killing myself"), ("crisis", "thinking of killing myself"),
    ("crisis", "I want to hurt myself"), ("crisis", "I want to self-harm"),
    ("crisis", "self-harm"), ("crisis", "self harm"), ("crisis", "self-harming"),
    ("crisis", "I might hurt myself"), ("crisis", "I am going to hurt myself"),
    ("crisis", "I want to cut myself"), ("crisis", "I cut myself"),
    ("crisis", "she wants to hurt herself"), ("crisis", "he wants to hurt himself"),
    ("crisis", "they want to hurt themselves"), ("crisis", "I am thinking about killing myself"),
    ("crisis", "I keep thinking about suicide"), ("crisis", "I don't want to live anymore"),
    # 25 emergency cases
    ("emergency", "my face is drooping"), ("emergency", "my arm is numb"),
    ("emergency", "my face feels numb"), ("emergency", "my leg is numb"),
    ("emergency", "my chest hurts"), ("emergency", "my chest is hurting"),
    ("emergency", "severe chest pain"), ("emergency", "crushing chest pain"),
    ("emergency", "really bad chest pain"), ("emergency", "I can't breathe"),
    ("emergency", "I cannot breathe"), ("emergency", "I am having trouble breathing"),
    ("emergency", "trouble breathing"), ("emergency", "difficulty breathing"),
    ("emergency", "shortness of breath"), ("emergency", "anaphylaxis"),
    ("emergency", "severe allergic reaction"), ("emergency", "I swallowed bleach"),
    ("emergency", "I drank poison"), ("emergency", "I ingested cleaner"),
    ("emergency", "I passed out"), ("emergency", "I am unconscious"),
    ("emergency", "severe bleeding"), ("emergency", "my bleeding won't stop"),
    # 20 personal medical cases
    ("personal", "Do I have diabetes?"), ("personal", "Could I have asthma?"),
    ("personal", "Am I having a heart attack?"), ("personal", "Is this serious for me?"),
    ("personal", "Is this safe for me?"), ("personal", "What should I take?"),
    ("personal", "What medication should I take?"), ("personal", "What medicine should I take?"),
    ("personal", "What dose should I take?"), ("personal", "How much medication should I take?"),
    ("personal", "Should I stop taking my medication?"), ("personal", "Should I change my medication?"),
    ("personal", "Can I stop taking this medication?"), ("personal", "Can I eat rice if I have diabetes?"),
    ("personal", "I have diabetes, can I eat rice?"), ("personal", "My symptoms are getting worse"),
    ("personal", "Is ibuprofen safe for me?"), ("personal", "Can I take ibuprofen?"),
    ("personal", "Can I use this medication?"), ("personal", "Is it safe for me to take this?"),
    # 30 safe/educational cases, including emergency terms that must remain searchable
    ("none", "What is a heart attack?"), ("none", "What is a stroke?"),
    ("none", "What is asthma?"), ("none", "What is diabetes?"),
    ("none", "What are seizure symptoms?"), ("none", "What is opioid overdose prevention?"),
    ("none", "What causes hypertension?"), ("none", "How is asthma treated?"),
    ("none", "What are migraine symptoms?"), ("none", "How is eczema diagnosed?"),
    ("none", "What is influenza?"), ("none", "What is a blood clot?"),
    ("none", "What is a urinary tract infection?"), ("none", "What is COPD?"),
    ("none", "How can diabetes be prevented?"), ("none", "What causes heartburn?"),
    ("none", "What are the treatments for allergies?"), ("none", "How is pneumonia diagnosed?"),
    ("none", "What is conjunctivitis?"), ("none", "What are shingles symptoms?"),
    ("none", "How does blood pressure work?"), ("none", "What is cholesterol?"),
    ("none", "What are the symptoms of anemia?"), ("none", "What is osteoporosis?"),
    ("none", "How is depression treated?"), ("none", "What is ADHD?"),
    ("none", "What are common cold symptoms?"), ("none", "What is food poisoning?"),
    ("none", "What causes kidney stones?"), ("none", "How can flu be prevented?"),
    ("none", "What is a migraine?"),
    ("crisis", "I don't want to be alive"),
    ("crisis", "I wish I were dead"),
    ("crisis", "I want to end my life"),
    ("crisis", "I plan to end my life"),
    ("crisis", "I would be better off dead"),
    ("emergency", "My throat is closing"),
    ("emergency", "My lips are turning blue"),
    ("emergency", "I took too many pills"),
    ("emergency", "I overdosed"),
    ("personal", "Should I increase my dose?"),
    ("personal", "Should I lower my dose?"),
    ("personal", "What treatment is best for me?"),
]



# ============================================================
# HEALTH-LITERACY TOOLS
# ============================================================
COMPARISON_GUIDES = {
    "type 1 diabetes vs type 2 diabetes": ("Type 1 diabetes", "Type 2 diabetes", "Type 1 diabetes is an autoimmune condition; type 2 diabetes involves insulin resistance and/or inadequate insulin production. They have different causes, risk factors, and management considerations."),
    "heart attack vs cardiac arrest": ("Heart attack", "Cardiac arrest", "A heart attack involves blocked blood flow to heart muscle. Cardiac arrest occurs when the heart suddenly stops pumping effectively. They are not the same event."),
    "cold vs flu": ("Common cold", "Influenza (flu)", "Both are viral respiratory illnesses, but influenza can be more severe and often has more abrupt systemic symptoms. Symptoms alone do not establish a diagnosis."),
    "viral vs bacterial infection": ("Viral infection", "Bacterial infection", "Viruses and bacteria are different infectious agents. Treatment depends on the infection; antibiotics do not treat viral infections."),
    "ct vs mri": ("CT scan", "MRI", "CT uses X-rays and is often fast. MRI uses magnetic fields and radio waves and can provide detailed soft-tissue images. The appropriate test depends on the clinical question."),
}


def extract_sentences(text):
    clean = normalize_sentence_boundaries(clean_html(text))
    clean = re.sub(r"\s+", " ", clean).strip()
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", clean) if len(x.strip()) > 30]


def key_takeaways(text, limit=4):
    sentences = extract_sentences(text)
    if not sentences:
        return ["Review the linked source for the complete medical information."]
    return sentences[:limit]


def readability_score(text):
    clean = re.sub(r"<[^>]+>", " ", text or "")
    words = re.findall(r"\b[\w'-]+\b", clean)
    sentences = max(1, len(re.findall(r"[.!?]+", clean)))
    if not words:
        return 0, "Not enough text to estimate"
    syllables = 0
    for word in words:
        w = re.sub(r"[^a-zA-Z]", "", word).lower()
        if not w:
            continue
        count = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and count > 1:
            count -= 1
        syllables += max(1, count)
    score = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))
    if score >= 90: level = "Very easy to read"
    elif score >= 70: level = "Easy to read"
    elif score >= 60: level = "Standard"
    elif score >= 50: level = "Somewhat complex"
    elif score >= 30: level = "Complex"
    else: level = "Very complex"
    return max(0, min(100, score)), level


def medical_term_bridge(query, title):
    q = (query or "").lower().strip()
    matches = []
    title_norm = normalize_text(title or "")
    for patient_term, medical_term in sorted(SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        term_norm = normalize_text(patient_term)
        if not term_norm:
            continue
        pattern = r"(?<!\w)" + re.escape(term_norm) + r"(?!\w)"
        if (re.search(pattern, q) or re.search(pattern, title_norm)) and patient_term != medical_term:
            matches.append((patient_term, medical_term))
    return matches[:4]


def appointment_questions(topic):
    clean = topic.strip()
    return [
        f"What should I know about {clean} in general?",
        f"What symptoms or changes related to {clean} should I discuss with a healthcare professional?",
        f"What tests or evaluations are commonly used when {clean} is being considered?",
        f"What treatment or management options are commonly discussed for {clean}?",
        f"What questions should I ask based on my own medical history and circumstances?",
    ]


def general_when_to_get_help():
    """Conservative general safety guidance, not a symptom checker."""
    return [
        ("Call emergency services now", "For signs of a life-threatening emergency such as severe trouble breathing, chest pain with concerning symptoms, sudden weakness or trouble speaking, loss of consciousness, or severe uncontrolled bleeding."),
        ("Seek urgent medical advice", "For symptoms that are new, worsening, severe, or concerning, or when you are unsure how quickly care is needed. Use local urgent-care or nurse-advice services when appropriate."),
        ("Contact your healthcare professional", "For non-emergency questions about symptoms, test results, medicines, or treatment plans. Do not delay emergency care to search this website."),
    ]


def caregiver_points(topic):
    return [
        f"Ask the person what they already understand about {topic}.",
        "Use the plain-language explanation first, then introduce medical terms they may hear from clinicians.",
        "Write down questions, changes in symptoms, medications, and instructions to discuss with the healthcare team.",
        "Do not use general educational information to make a diagnosis or change treatment without professional guidance.",
    ]


def understanding_questions(topic):
    t = topic.strip()
    return [
        (f"Which statement best describes the purpose of learning about {t}?", "To understand reliable health information and prepare for informed conversations with healthcare professionals."),
        ("What should you do if the information conflicts with advice specific to you?", "Discuss the difference with a qualified healthcare professional who knows your medical history."),
        ("Does educational information by itself diagnose a person?", "No. General health information does not establish a personal diagnosis."),
    ]


def simplified_explanation(title, information, level):
    information = normalize_sentence_boundaries(clean_html(information))
    sentences = extract_sentences(information)
    if level == "Basic":
        return " ".join(sentences[:2]) if sentences else information[:700]
    if level == "Medical terminology":
        return information[:1800]
    return " ".join(sentences[:4]) if sentences else information[:1200]


def find_comparison(topic):
    q = re.sub(r"\s+", " ", topic.lower().strip())
    for key, value in COMPARISON_GUIDES.items():
        if key in q or all(part in q for part in key.split(" vs ")):
            return value
    return None


def render_communication_phrases(topic, language_code):
    phrases = [
        f"I would like to understand what {topic} means.",
        f"What should I watch for related to {topic}?",
        f"Are there questions I should ask about {topic}?",
        "Could you explain that in simpler terms?",
        "Can you show me how I should follow these instructions?",
    ]
    for phrase in phrases:
        if language_code == "en":
            st.markdown(f"- {html.escape(phrase)}")
        else:
            translated = translate_text(phrase, language_code, "en")
            st.markdown(f"- **{html.escape(translated)}**")
            st.caption(f"English: {phrase}")


def render_browser_audio(text, language_code="en", key="careclarity-audio"):
    """Use the browser's built-in speech synthesis; no audio is uploaded or stored."""
    safe_text = json.dumps((text or "")[:5000], ensure_ascii=False)
    safe_lang = json.dumps(language_code or "en")
    component_html = f"""<!doctype html><html><body style="font-family:Arial,sans-serif;margin:0;padding:4px 0;background:transparent;color:#352d46">
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <button id="play" type="button" style="border:1px solid #cfc3e6;border-radius:10px;padding:9px 13px;background:#f4effb;color:#352d46;cursor:pointer;font-size:14px">▶ Read aloud</button>
      <button id="stop" type="button" style="border:1px solid #d8d2e2;border-radius:10px;padding:9px 13px;background:#fff;color:#352d46;cursor:pointer;font-size:14px">Stop</button>
      <span id="status" role="status" aria-live="polite" style="font-size:12px">Uses your browser's speech feature; availability and voice quality vary by device.</span>
    </div><script>
      const text = {safe_text}; const lang = {safe_lang};
      const status = document.getElementById('status');
      document.getElementById('play').addEventListener('click', () => {{
        if (!('speechSynthesis' in window)) {{ status.textContent = 'Speech playback is not supported in this browser.'; return; }}
        window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(text); u.lang = lang;
        u.onstart = () => status.textContent = 'Reading aloud…';
        u.onend = () => status.textContent = 'Finished.';
        u.onerror = () => status.textContent = 'Playback could not start. Try your browser or device accessibility settings.';
        window.speechSynthesis.speak(u);
      }});
      document.getElementById('stop').addEventListener('click', () => {{ if ('speechSynthesis' in window) window.speechSynthesis.cancel(); status.textContent = 'Playback stopped.'; }});
    </script></body></html>"""
    components.html(component_html, height=64, scrolling=False)


def render_source_evidence(information, source_url):
    """Show excerpts from retrieved source text without claiming AI claim verification."""
    sentences = extract_sentences(information)
    if not sentences:
        sentences = [normalize_sentence_boundaries(clean_html(information))[:450]]
    with st.expander("Source passages behind this explanation", expanded=False):
        st.caption("These excerpts come from the retrieved MedlinePlus text. They help you compare the explanation with its source; they are not an automated guarantee that every AI statement is correct.")
        for index, sentence in enumerate(sentences[:5], start=1):
            st.markdown(f"**Source excerpt {index}**")
            st.write(sentence[:650] + ("…" if len(sentence) > 650 else ""))
        if safe_source_url(source_url):
            st.link_button("Review the complete original source", source_url)


def render_health_literacy_tools(topic, title, information, source_url, language_code):
    score, level = readability_score(information)
    takeaways = key_takeaways(information)
    bridges = medical_term_bridge(topic, title)

    st.markdown('<div class="tool-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Explore this topic</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-description learning-intro">Use these focused tools to clarify the explanation, review key points, and understand medical terminology.</div>', unsafe_allow_html=True)
    mode = st.session_state.get("audience_mode", "Learner")
    mode_content = {
        "Learner": ("Start with the basics", "Learn the core idea first, then use the tools below to build vocabulary and check your understanding."),
        "Preparing for a visit": ("Get ready for a healthcare conversation", "Review the topic, identify useful terms, and build a short list of questions to bring to a healthcare professional."),
        "Caregiver": ("Make the information easier to explain", "Use the plain-language explanation, key takeaways, and communication tools to help explain the topic to someone you support."),
    }
    mode_title, mode_body = mode_content[mode]
    st.markdown(f'<div class="mode-focus"><div class="mode-focus-title">{html.escape(mode_title)}</div><div class="mode-focus-body">{html.escape(mode_body)}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["Overview", "Key points", "Medical terms", "Compare", "Visit prep"])

    with tabs[0]:
        st.markdown("**Choose an explanation level**")
        
        explanation_options = ["Basic", "Standard", "Medical terminology"]
        if "explanation_level" not in st.session_state:
            st.session_state.explanation_level = "Basic"
        level_choice = st.radio(
            "Explanation level",
            explanation_options,
            horizontal=True,
            index=explanation_options.index(st.session_state.explanation_level),
            key="explanation_level_radio",
            label_visibility="collapsed",
        )
        st.session_state.explanation_level = level_choice
        explanation_text = simplified_explanation(title, information, level_choice)
        explanation_html = html.escape(explanation_text).replace("\n", "<br>")
        st.markdown(
            '<div class="tool-card">'
            f'<div class="tool-card-title">{html.escape(level_choice)} explanation</div>'
            f'<div class="tool-card-body">{explanation_html}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.caption("This is a presentation of retrieved source material; it is not a personalized medical explanation.")
        st.markdown("**Listen to this explanation**")
        render_browser_audio(explanation_text, language_code, key=f"audio_{normalize_text(title)}")

    with tabs[1]:
        takeaways_html = "".join(f"<li>{html.escape(item)}</li>" for item in takeaways)
        st.markdown(
            '<div class="tool-card">'
            '<div class="tool-card-title">Key takeaways</div>'
            f'<ul class="tool-card-list">{takeaways_html}</ul>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Readability estimate: **{level}** · score {score:.0f}/100. This is a readability estimate, not a measure of medical accuracy.")

        st.markdown("**Check your understanding**")
        st.caption("This short teach-back check focuses on using health information safely; it does not test your medical knowledge.")
        quiz_items = understanding_questions(title)
        quiz_key = f"teachback_{normalize_text(title).replace(' ', '_')}"
        selected_answer = st.radio(
            "Which statement is safest?",
            ["This page can diagnose me if the topic matches my symptoms.",
             "This page provides general education; personal questions should be discussed with a qualified healthcare professional.",
             "I should change treatment based on this page alone."],
            index=None, key=quiz_key,
        )
        if st.button("Check my answer", key=f"check_{quiz_key}"):
            if selected_answer is None:
                st.info("Choose an answer first.")
            elif selected_answer.startswith("This page provides general education"):
                st.success("Correct. General information can help you prepare questions, but it does not establish a diagnosis or personal treatment plan.")
            else:
                st.warning("Not quite. CareClarity provides general education only. Use the linked source and discuss personal decisions with a qualified healthcare professional.")

    with tabs[2]:
        if bridges:
            st.markdown("**Patient language → medical terminology**")
            for patient_term, medical_term in bridges:
                st.markdown(f"**{html.escape(patient_term.title())}** → `{html.escape(medical_term)}`")
                st.caption("Related terms are not necessarily exact clinical equivalents.")
        else:
            st.info("No patient-language synonym was detected. Try everyday wording such as “pink eye,” “high blood pressure,” or “heartburn.”")
        st.markdown("**What this does NOT mean**")
        st.write("Finding a topic does not mean you have that condition. The source provides general education, not an interpretation of your personal symptoms, test results, or treatment plan.")
        st.markdown("**I don't understand this medical term or test**")
        term_input = st.text_input("Term or test name", placeholder="e.g., HbA1c, MRI, tachycardia", key="term_explainer_input")
        if term_input:
            term_result = search_medlineplus(translate_query_to_english(term_input, language_code))
            if term_result and not term_result.get("_search_error"):
                st.write(f"**{term_result['title']}**")
                st.write(" ".join(key_takeaways(term_result["summary"], 2)))
                if safe_source_url(term_result["url"]):
                    st.link_button("Read the original source", term_result["url"])
            elif term_result and term_result.get("_search_error"):
                st.warning("The medical source service is temporarily unavailable. Please retry in a moment.")
            else:
                st.info("No closely matching MedlinePlus topic was found. Try the full term or ask a healthcare professional for clarification.")

    with tabs[3]:
        st.markdown("**Compare related medical concepts**")
        comparison = find_comparison(topic)
        if comparison:
            left, right, explanation = comparison
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{html.escape(left)}**")
            with c2:
                st.markdown(f"**{html.escape(right)}**")
            st.info(explanation)
        else:
            st.info("Try a search such as “heart attack vs cardiac arrest,” “cold vs flu,” “CT vs MRI,” “viral vs bacterial infection,” or “type 1 diabetes vs type 2 diabetes.”")

    with tabs[4]:
        st.markdown("**Questions you can bring to a healthcare professional**")
        for q in appointment_questions(title):
            st.markdown(f"- {html.escape(q)}")
        st.markdown("**Before your visit**")
        for checklist_item in ["Write down your questions and concerns.", "Bring an up-to-date medication and allergy list if relevant.", "Ask the clinician to explain anything that is unclear.", "Confirm the next steps and whom to contact with follow-up questions."]:
            st.markdown(f"- {html.escape(checklist_item)}")
        st.markdown("**My notes for the appointment**")
        st.caption("Keep notes general. Avoid entering names, dates of birth, contact details, or other identifying information.")
        visit_notes = st.text_area("Questions or notes to bring", key=f"visit_notes_{abs(hash(source_url))}", placeholder="Questions I want to ask…", height=120)
        if visit_notes.strip():
            st.download_button(
                "Download my appointment notes (.txt)",
                data=(f"CareClarity appointment notes\nTopic: {title}\nSource: {source_url}\n\n{visit_notes.strip()}\n\nFor personal medical decisions, consult a qualified healthcare professional.\n"),
                file_name=f"careclarity_visit_notes_{abs(hash(source_url)) % 100000}.txt",
                mime="text/plain", key=f"visit_notes_download_{abs(hash(source_url))}",
            )
        if safe_source_url(source_url):
            st.link_button("Open the source used for this topic", source_url)
        pdf_bytes = make_patient_summary_pdf(topic, title, information, source_url, st.session_state.get("language", "English"))
        if pdf_bytes:
            st.download_button(
                "Download printable patient summary (PDF)", pdf_bytes,
                file_name=f"careclarity_{re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()[:48] or 'summary'}.pdf",
                mime="application/pdf", key=f"download_pdf_{abs(hash(source_url))}",
                help="Includes a plain-language overview, key points, visit questions and the source URL."
            )
        else:
            st.info("PDF export requires the free reportlab package. Install project requirements to enable it.")

    # Secondary tools are kept outside the main six-step learning flow so the
    # interface does not mix core learning tasks with optional extras.
    if mode == "Caregiver":
        st.markdown('<div class="tool-divider"></div>', unsafe_allow_html=True)
        st.markdown("**Caregiver communication**")
        st.caption("Use these phrases to ask for clarification or explain what you learned in the selected language.")
        render_communication_phrases(title, language_code)
    elif mode == "Preparing for a visit":
        st.markdown('<div class="tool-divider"></div>', unsafe_allow_html=True)
        st.markdown("**Conversation prompts**")
        st.caption("A few concise prompts you can take into a healthcare conversation.")
        for q in appointment_questions(title)[:3]:
            st.markdown(f"- {html.escape(q)}")

    st.markdown('<div class="tool-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Explore additional trusted sources**")
    st.caption("These links open searches on other organizations' websites; they are not sources used to generate the explanation above.")
    source_links = source_navigation_links(topic)
    source_cols = st.columns(len(source_links))
    for col, (name, link) in zip(source_cols, source_links):
        with col:
            st.link_button(f"Search {name}", link, use_container_width=True)



def run_safety_evaluation():
    results = []
    for expected, text in SAFETY_TEST_CASES:
        actual = classify_safety(text)
        results.append({"expected": expected, "actual": actual, "text": text, "passed": expected == actual})
    total = len(results)
    passed = sum(r["passed"] for r in results)
    crisis = [r for r in results if r["expected"] == "crisis"]
    crisis_correct = sum(r["actual"] == "crisis" for r in crisis)
    return {
        "total": total,
        "passed": passed,
        "accuracy": passed / total if total else 0,
        "crisis_total": len(crisis),
        "crisis_correct": crisis_correct,
        "crisis_recall": crisis_correct / len(crisis) if crisis else 0,
        "results": results,
    }

# ============================================================
# RATE LIMITING
# ============================================================

def request_allowed():
    now = time.time()
    previous = st.session_state.get("last_request_time", 0.0)

    if now - previous < 2.0:
        return False

    st.session_state.last_request_time = now
    return True


# ============================================================
# SESSION STATE
# ============================================================

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "saved_topics" not in st.session_state:
    st.session_state.saved_topics = []

if "audience_mode" not in st.session_state:
    st.session_state.audience_mode = "Learner"

if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""

if "language" not in st.session_state:
    st.session_state.language = "English"

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "current_safety_level" not in st.session_state:
    st.session_state.current_safety_level = "none"

if "search_requested" not in st.session_state:
    st.session_state.search_requested = False



# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">CareClarity</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Source-grounded healthcare education'
        '</div>',
        unsafe_allow_html=True,
    )

    selected_language = st.selectbox(
        "Language",
        list(LANGUAGES.keys()),
        index=(list(LANGUAGES.keys()).index(st.session_state.language) if st.session_state.language in LANGUAGES else 0),
        key="language_selector",
        help="Choose the language for the interface and, when available, translated source-grounded content.",
    )
    st.session_state.language = selected_language
    language_code = LANGUAGES[selected_language]

    st.markdown('<div class="sidebar-section">YOUR LEARNING MODE</div>', unsafe_allow_html=True)
    st.session_state["audience_mode"] = st.selectbox(
        "Choose how to use CareClarity",
        ["Learner", "Caregiver", "Preparing for a visit"],
        index=["Learner", "Caregiver", "Preparing for a visit"].index(
            st.session_state.get("audience_mode", "Learner")
            if st.session_state.get("audience_mode", "Learner") in ["Learner", "Caregiver", "Preparing for a visit"]
            else "Learner"
        ),
        help="Changes the extra learning and communication tools shown with each topic.",
        key="audience_mode_selector",
    )

    # Accessibility options are kept lightweight and do not change source content.
    st.session_state.setdefault("high_readability", False)
    st.markdown('<div class="sidebar-section">ACCESSIBILITY</div>', unsafe_allow_html=True)
    font_scale = st.select_slider(
        "Text size", options=["Standard", "Large", "Extra large"],
        value=st.session_state.get("font_scale", "Standard"), key="font_scale_selector",
        help="Adjust the reading size across the page.",
    )
    st.session_state.font_scale = font_scale
    font_px = {"Standard": "16px", "Large": "18px", "Extra large": "20px"}[font_scale]
    st.markdown(f'<style>[data-testid="stAppViewContainer"] .stMarkdown p, [data-testid="stAppViewContainer"] li, [data-testid="stAppViewContainer"] label, .medical-body, .tool-card-body, .mode-focus-body, .source-description {{ font-size: {font_px} !important; line-height: 1.7 !important; }}</style>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-section">TRUSTED SOURCES</div>',
        unsafe_allow_html=True,
    )

    trusted_sources = [
        ("MedlinePlus", "NIH / NLM", "https://medlineplus.gov/"),
        ("CDC", "Public health", "https://www.cdc.gov/"),
        ("NIH", "Health information", "https://www.nih.gov/health-information"),
        ("FDA", "Medicines & safety", "https://www.fda.gov/"),
        ("NIMH", "Mental health", "https://www.nimh.nih.gov/"),
    ]
    for name, desc, url in trusted_sources:
        st.markdown(
            f'<a class="sidebar-link" href="{url}" target="_blank">{name} <span style="color:#8aa0ad;font-weight:500;">· {desc}</span></a>',
            unsafe_allow_html=True,
        )

    if st.session_state.search_history:
        st.markdown('<div class="sidebar-section">RECENT TOPICS</div>', unsafe_allow_html=True)
        for index, previous in enumerate(reversed(st.session_state.search_history[-5:])):
            if st.button(previous, key=f"history_{index}", use_container_width=True):
                st.session_state.topic_input = previous
                st.session_state.search_requested = True
                st.rerun()
        if st.button("Clear recent history", key="clear_search_history", use_container_width=True):
            st.session_state.search_history = []
            st.rerun()
        st.caption("Recent topics stay in this browser session and are not saved to a CareClarity account.")

    if st.session_state.saved_topics:
        st.markdown('<div class="sidebar-section">SAVED TOPICS</div>', unsafe_allow_html=True)
        for index, saved in enumerate(list(st.session_state.saved_topics)):
            saved_cols = st.columns([4, 1])
            with saved_cols[0]:
                if st.button(saved, key=f"saved_topic_{index}", use_container_width=True):
                    st.session_state.topic_input = saved
                    st.session_state.search_requested = True
                    st.rerun()
            with saved_cols[1]:
                if st.button("×", key=f"remove_saved_{index}", help=f"Remove {saved} from saved topics"):
                    st.session_state.saved_topics.remove(saved)
                    st.rerun()
        if st.button("Clear saved topics", key="clear_saved_topics", use_container_width=True):
            st.session_state.saved_topics = []
            st.rerun()
        st.caption("Saved topics last for this browser session only; they are not stored in an account.")

    with st.expander("Quality & usability evaluation", expanded=False):
        st.caption("A lightweight self-check for reviewers. These observations are session-only and are not clinical validation.")
        evaluation_checks = [
            "I can locate the original medical source.",
            "I can tell general education apart from personal medical advice.",
            "I can find the emergency-help guidance.",
            "The explanation is readable at my selected text size.",
            "The language and terminology are understandable to me.",
            "The appointment-preparation tools are easy to find."
        ]
        for check_index, check_label in enumerate(evaluation_checks):
            st.checkbox(check_label, key=f"usability_check_{check_index}")
        if st.button("Export usability checklist", key="export_usability_checklist", use_container_width=True):
            rows = ["check,completed"]
            for check_index, check_label in enumerate(evaluation_checks):
                checked = bool(st.session_state.get(f"usability_check_{check_index}", False))
                rows.append('"' + check_label.replace('"', '""') + '",' + ("yes" if checked else "no"))
            st.download_button(
                "Download checklist (.csv)",
                data="\n".join(rows), file_name="careclarity_usability_checklist.csv",
                mime="text/csv", key="download_usability_checklist",
            )
        if st.button("Clear session learning data", key="clear_session_learning_data", use_container_width=True):
            for state_key in list(st.session_state.keys()):
                if state_key == "search_history" or state_key == "saved_topics" or state_key == "careclarity_feedback" or state_key.startswith("visit_notes_") or state_key.startswith("teachback_") or state_key.startswith("usability_check_") or state_key.startswith("local_ai_summary::"):
                    del st.session_state[state_key]
            st.success("Session learning data cleared. The page may refresh to initialize default settings again.")
            st.rerun()

    with st.expander("Safety test suite", expanded=False):
        st.caption("Run the built-in phrase-classification regression cases. These checks do not prove clinical safety.")
        if st.button("Run safety checks", key="run_safety_checks", use_container_width=True):
            st.session_state.run_safety_checks = True
        if st.session_state.get("run_safety_checks", False):
            evaluation = run_safety_evaluation()
            st.metric("Cases passed", f"{evaluation['passed']} / {evaluation['total']}")
            st.metric("Crisis phrase recall", f"{evaluation['crisis_recall']:.0%}")
            failures = [row for row in evaluation["results"] if not row["passed"]]
            if failures:
                st.error(f"{len(failures)} case(s) did not match the expected category.")
                for failure in failures[:10]:
                    st.write(f"Expected **{failure['expected']}**, got **{failure['actual']}**: {failure['text']}")
            else:
                st.success("All built-in cases passed. This is not a substitute for clinical validation or broader testing.")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="brand-row"><div class="brand-mark">+</div><div class="brand-name">CareClarity</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand-subtitle">Clear, source-grounded health information for learning, understanding, and better healthcare conversations.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-box">'
    '<img class="hero-photo" src="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=900&q=90" alt="Healthcare professional providing patient care">'
    '<div style="position:relative;z-index:2;max-width:735px;padding-right:315px;">'
    '<div class="hero-label">MEDICAL INFORMATION · SOURCE-GROUNDED</div>'
    '<div class="hero-heading">Understand your health.<br>Prepare for better conversations.</div>'
    '<div class="hero-description">'
    'Explore general healthcare topics using trusted, source-grounded medical information. '
    'The app keeps the original medical source visible so you can review the information directly.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# SEARCH
# ============================================================

st.markdown(
    '<div class="section-label">PATIENT EDUCATION</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="section-heading">{html.escape(ui_text("topic", language_code))}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Explore trusted health information, understand key terms, and prepare questions for a healthcare professional. '
    'CareClarity presents general education from MedlinePlus and does not diagnose or replace clinical care.'
    '</div>',
    unsafe_allow_html=True,
)

topic = st.text_input(
    "Healthcare topic",
    value=st.session_state.topic_input,
    placeholder="Enter a healthcare topic...",
    label_visibility="collapsed",
)

st.markdown(
    '<div class="examples">'
    'Examples: asthma · diabetes · hypertension · allergies · migraine'
    '</div>',
    unsafe_allow_html=True,
)

button_cols = st.columns(4)

example_topics = ["Asthma", "Diabetes", "Hypertension", "Allergies"]

for column, example in zip(button_cols, example_topics):
    with column:
        if st.button(example, use_container_width=True, key=f"example_{example.lower()}"):
            st.session_state.topic_input = example
            st.session_state.search_requested = True
            st.rerun()

search_clicked = st.button(
    ui_text("search", language_code),
    use_container_width=False,
    key="search_medical_information",
    type="primary",
)

if search_clicked:
    st.session_state.search_requested = True


# ============================================================
# SEARCH EXECUTION
# ============================================================

if st.session_state.get("search_requested", False):
    topic = st.session_state.topic_input.strip() or topic.strip()
    st.session_state.topic_input = topic

    if not topic:
        st.session_state.search_requested = False
        st.markdown(
            '<div class="empty-box">'
            '<div class="empty-heading">No topic entered</div>'
            '<div class="empty-description">'
            'Enter a general healthcare topic to begin.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        st.stop()

    if not request_allowed():
        st.warning("Please wait a moment before making another search.")
        st.stop()

    safety_level = classify_safety(topic)

    # --------------------------------------------------------
    # CRISIS BANNER
    # --------------------------------------------------------

    if safety_level == "crisis":
        st.markdown(
            '<div class="crisis-box">'
            '<div class="crisis-heading">Immediate support is available</div>'
            '<div class="crisis-description">'
            f'{CRISIS_MESSAGE}'
            '<br><br>'
            'This application is not a crisis counseling service.'
            '</div></div>',
            unsafe_allow_html=True,
        )

        crisis_cols = st.columns(2)

        with crisis_cols[0]:
            st.link_button(
                "Call or text 988",
                "https://988lifeline.org/",
            )

        with crisis_cols[1]:
            st.link_button(
                "988 Get Help",
                "https://988lifeline.org/get-help/",
            )

        # Do not send a crisis statement to an AI model or
        # automatically turn it into a normal health-topic search.
        st.session_state.current_result = {"topic": topic, "safety_level": safety_level, "crisis": True}
        st.session_state.current_safety_level = safety_level
        st.session_state.search_requested = False
        st.stop()

    # --------------------------------------------------------
    # EMERGENCY BANNER
    # --------------------------------------------------------

    if safety_level == "emergency":
        st.markdown(
            '<div class="emergency-box">'
            '<div class="emergency-heading">Potential medical emergency</div>'
            '<div class="emergency-description">'
            f'{EMERGENCY_MESSAGE}'
            '<br><br>'
            'The app will still show general educational information when '
            'a relevant MedlinePlus topic can be identified.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # PERSONALIZED ADVICE
    # --------------------------------------------------------

    if safety_level == "personal":
        st.markdown(
            '<div class="safety-box">'
            '<div class="safety-heading">Personal medical question</div>'
            '<div class="safety-description">'
            'This application can provide general education, but it cannot '
            'determine whether you have a condition, tell you whether a '
            'medication is safe for you, or provide individualized treatment advice. '
            'The general topic may still be useful for learning.'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # RETRIEVE SOURCE
    # --------------------------------------------------------

    # MedlinePlus primarily indexes English health-topic titles. When a user
    # types Chinese, Italian, German, etc., translate the query to English
    # first so the search still works on a phone in that language.
    search_topic = translate_query_to_english(topic, language_code)

    with st.spinner("Finding a relevant MedlinePlus health topic..."):
        result = search_medlineplus(search_topic)
        # If translation/search did not help, also try the original wording.
        if (result is None or result.get("_search_error")) and search_topic != topic:
            original_result = search_medlineplus(topic)
            if original_result is not None:
                result = original_result

    if result and result.get("_search_error"):
        st.session_state.search_requested = False
        st.session_state.current_result = None
        st.markdown(
            '<div class="empty-box">'
            '<div class="empty-heading">Medical source search is temporarily unavailable</div>'
            '<div class="empty-description">'
            'The source service did not respond successfully. Please try again in a moment, '
            'or use the trusted-source links to search an authoritative website directly. '
            'CareClarity has not generated an answer without a source.'
            '</div></div>', unsafe_allow_html=True,
        )
        for name, link in source_navigation_links(topic):
            st.link_button(f"Search {name} for this topic", link)
        st.stop()

    if result is None:
        st.session_state.search_requested = False
        st.session_state.current_result = None
        st.markdown(
            '<div class="empty-box">'
            '<div class="empty-heading">No closely matching medical source found</div>'
            '<div class="empty-description">'
            'I could not identify a sufficiently relevant MedlinePlus health topic for this request. '
            'Try a common condition name, a recognized medical term, or a shorter search phrase. '
            'You can also explore the same topic through another trusted healthcare organization below.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        suggestion_cols = st.columns(4)
        for col, suggestion in zip(suggestion_cols, ["Asthma", "Diabetes", "Hypertension", "Migraine"]):
            with col:
                if st.button(suggestion, key=f"no_result_{suggestion.lower()}", use_container_width=True):
                    st.session_state.topic_input = suggestion
                    st.session_state.search_requested = True
                    st.rerun()
        for name, link in source_navigation_links(topic):
            st.link_button(f"Search {name} for this topic", link)
        st.stop()

    title = result["title"]
    information = result["summary"]
    source_url = result["url"]

    st.session_state.current_result = {
        "topic": topic,
        "title": title,
        "information": information,
        "source_url": source_url,
        "safety_level": safety_level,
        "alternatives": result.get("alternatives", []),
    }
    st.session_state.current_safety_level = safety_level
    st.session_state.search_requested = False

    # Split the original English source BEFORE translating it. Otherwise the
    # English section headings disappear and non-English results collapse into
    # one large card.
    original_sections = format_medical_content(information)

    translation_used = False
    if language_code != "en":
        translated_title = translate_text(title, language_code, "en")
        translated_sections = []

        if translated_title.strip() != title.strip():
            translation_used = True

        for original_heading, original_content in original_sections:
            translated_heading = translate_text(original_heading, language_code, "en")
            translated_content = translate_text(original_content, language_code, "en")

            if translated_heading.strip() != original_heading.strip():
                translation_used = True
            if translated_content.strip() != original_content.strip():
                translation_used = True

            translated_sections.append((translated_heading, translated_content))
    else:
        translated_title = title
        translated_sections = original_sections

    if topic.lower() not in [
        item.lower() for item in st.session_state.search_history
    ]:
        st.session_state.search_history.append(topic)



def render_current_result():
    current = st.session_state.get("current_result")
    if not current:
        return
    if current.get("crisis"):
        return

    topic = current["topic"]
    title = current["title"]
    information = current["information"]
    source_url = current["source_url"]
    safety_level = current.get("safety_level", "none")

    save_cols = st.columns([1, 3])
    with save_cols[0]:
        is_saved = topic in st.session_state.saved_topics
        if st.button("Remove saved topic" if is_saved else "Save topic", key=f"toggle_saved_{normalize_text(topic).replace(' ', '_')}", use_container_width=True):
            if is_saved:
                st.session_state.saved_topics = [item for item in st.session_state.saved_topics if item != topic]
            else:
                st.session_state.saved_topics = (st.session_state.saved_topics + [topic])[-20:]
            st.rerun()
    with save_cols[1]:
        st.caption("Saved topics are temporary and disappear when this browser session ends.")

    original_sections = format_medical_content(information)
    translation_used = False
    if language_code != "en":
        translated_title = translate_text(title, language_code, "en")
        translated_sections = []
        if translated_title.strip() != title.strip():
            translation_used = True
        for original_heading, original_content in original_sections:
            translated_heading = translate_text(original_heading, language_code, "en")
            translated_content = translate_text(original_content, language_code, "en")
            if translated_heading.strip() != original_heading.strip() or translated_content.strip() != original_content.strip():
                translation_used = True
            translated_sections.append((translated_heading, translated_content))
    else:
        translated_title = title
        translated_sections = original_sections

    st.divider()

    if safety_level == "emergency":
        st.markdown(
            '<div class="emergency-box"><div class="emergency-heading">Potential medical emergency</div>'
            f'<div class="emergency-description">{EMERGENCY_MESSAGE}<br><br>'
            'The educational source is still shown when a relevant topic can be identified.</div></div>',
            unsafe_allow_html=True,
        )
    elif safety_level == "personal":
        st.markdown(
            '<div class="safety-box"><div class="safety-heading">Personal medical question</div>'
            '<div class="safety-description">This result is general education only. It cannot determine a personal diagnosis, medication safety, dosage, or treatment plan.</div></div>',
            unsafe_allow_html=True,
        )

    with st.expander("When to get medical help", expanded=False):
        st.caption("General safety information only—not a symptom checker or personalized triage tool.")
        for help_title, help_text in general_when_to_get_help():
            st.markdown(f"**{html.escape(help_title)}**")
            st.write(help_text)
        st.warning("If you think someone is in immediate danger, contact local emergency services. In the U.S., call 911.")

    st.markdown(
        f'<div class="result-label">{html.escape(ui_text("result_label", language_code))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="result-title">{html.escape(translated_title)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="result-meta">{html.escape(ui_text("result_meta", language_code))}</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SOURCE-GROUNDED PRESENTATION
    # --------------------------------------------------------

    # --------------------------------------------------------
    # SOURCE CONTENT
    # --------------------------------------------------------

    for heading, content in translated_sections:
        st.markdown(
            f"""
            <div class="medical-card">
                <div class="medical-heading">{html.escape(heading)}</div>
                <div class="medical-body">{display_content(content)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if language_code != "en":
        with st.expander("View original English source text"):
            st.caption("This is the retrieved English source text. Compare it with the translated presentation when wording matters.")
            for original_heading, original_content in original_sections:
                st.markdown(f"**{html.escape(original_heading)}**")
                st.write(original_content)

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    st.markdown(
        '<div class="source-box">'
        '<div class="source-heading">Primary medical source</div>'
        '<div class="source-description">'
        'MedlinePlus · U.S. National Library of Medicine · National Institutes of Health'
        '<br><br>'
        'The source link below points to the specific MedlinePlus result used by the app.'
        f'<br><br>Retrieved by CareClarity on {datetime.date.today().isoformat()}. This is the retrieval date, not a medical review date.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    if safe_source_url(source_url):
        render_source_link_button("Open the specific MedlinePlus source ↗", source_url)
        # Keep the citation readable and integrated with the page instead of
        # showing it as a code block, which makes ordinary source metadata look
        # like something users are expected to copy or execute.
        st.markdown(
            '<div class="source-citation">'
            f'<strong>{html.escape(title)} — MedlinePlus, U.S. National Library of Medicine</strong>'
            f'<div><a href="{html.escape(source_url, quote=True)}" target="_blank" '
            'rel="noopener noreferrer">'
            f'{html.escape(source_url)}</a></div></div>',
            unsafe_allow_html=True,
        )
    else:
        render_source_link_button("Open MedlinePlus ↗", "https://medlineplus.gov/")

    render_source_evidence(information, source_url)

    # Optional source-grounded explanation feature.
    with st.expander("Simplify this explanation", expanded=False):
        st.caption("This explanation is generated from the medical source shown above. Do not enter personal medical details.")
        ai_key = f"local_ai_summary::{source_url}"
        if st.button("Generate simpler explanation", key=f"generate_local_ai_{abs(hash(source_url))}"):
            with st.spinner("Checking the local AI service and generating the explanation..."):
                generated_summary, summary_status = get_local_ai_explanation(title, information, source_url)
            if generated_summary and summary_status == "enabled":
                st.session_state[ai_key] = generated_summary
            elif summary_status == "not_running":
                st.warning("Ollama is not reachable. To use free local AI, install Ollama, start it, download a model (for example `ollama pull llama3.2:3b`), then run CareClarity locally.")
            elif summary_status == "timeout":
                st.warning("The local model took too long to respond. Try a smaller model or use the original source below.")
            elif summary_status == "model_missing":
                st.error("Ollama is running, but the configured model is not installed. In Terminal, run `ollama pull llama3.2:3b`, wait for it to finish, then click the AI button again.")
            elif summary_status.startswith("http_error"):
                st.error(f"Ollama returned an API error ({summary_status}). Check that the model name in OLLAMA_MODEL matches a model listed by `ollama list`.")
            elif summary_status.startswith("error:"):
                st.error(f"The local AI request failed: {summary_status[6:]}. Check Ollama and the configured model, then retry.")
            else:
                st.warning("The local AI service returned an empty answer. Check that the model is installed and try again; the original source remains available.")
        if st.session_state.get(ai_key):
            st.markdown(st.session_state[ai_key])
            st.caption("AI-generated wording based on the retrieved source. It may contain errors; compare it with the original source before making decisions.")
            with st.form(f"ai_feedback_form_{abs(hash(source_url))}"):
                feedback_kind = st.selectbox(
                    "How was this explanation?",
                    ["Looks helpful", "Hard to understand", "May contain an unsupported or incorrect claim", "Missing important source information", "Other issue"],
                    key=f"ai_feedback_kind_{abs(hash(source_url))}",
                )
                feedback_detail = st.text_area(
                    "Optional details (do not include personal health information)",
                    key=f"ai_feedback_detail_{abs(hash(source_url))}", height=80,
                )
                feedback_submitted = st.form_submit_button("Record feedback in this session")
            if feedback_submitted:
                st.session_state.setdefault("careclarity_feedback", [])
                st.session_state.careclarity_feedback.append({
                    "topic": title, "source_url": source_url, "kind": feedback_kind,
                    "detail": feedback_detail.strip(), "date": datetime.date.today().isoformat(),
                })
                st.success("Feedback recorded in this session only. It is not sent to a server or saved to an account.")
                st.download_button(
                    "Download feedback for review (.csv)",
                    data="date,topic,source_url,feedback,details\n" + "\n".join(
                        ",".join('"' + str(row.get(col, "")).replace('"', '""') + '"' for col in ["date", "topic", "source_url", "kind", "detail"])
                        for row in st.session_state.careclarity_feedback
                    ),
                    file_name="careclarity_feedback.csv", mime="text/csv",
                    key=f"feedback_export_{abs(hash(source_url))}",
                )

    alternatives = current.get("alternatives", [])
    if alternatives:
        with st.expander("Other potentially relevant MedlinePlus topics"):
            st.caption("These are additional search matches. Review each source to decide whether it fits your question.")
            for alternative in alternatives:
                st.markdown(f"**{html.escape(alternative['title'])}**")
                st.caption(alternative.get("summary", "")[:260].rstrip() + ("…" if len(alternative.get("summary", "")) > 260 else ""))
                if safe_source_url(alternative.get("url")):
                    st.link_button("Review this topic", alternative["url"])

    if language_code != "en":
        if translation_used:
            st.caption(
                "Translated presentation is provided as a convenience. The linked MedlinePlus page is the original source and may be available in additional languages."
            )
        else:
            st.warning(
                "The translation service was temporarily unavailable, so the original English source is shown instead. Your medical information has not been removed."
            )

    render_health_literacy_tools(topic, title, information, source_url, language_code)

    st.markdown(
        '<div class="safety-box">'
        '<div class="safety-heading">Educational information only</div>'
        '<div class="safety-description">'
        'This application is for general health education. It does not '
        'diagnose conditions, prescribe medications, determine whether a '
        'treatment is appropriate for you, or replace professional medical care.'
        '</div></div>',
        unsafe_allow_html=True,
    )


render_current_result()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer">'
    'CareClarity · Source-grounded healthcare education · '
    'MedlinePlus / National Library of Medicine · General educational information only'
    '</div>',
    unsafe_allow_html=True,
)
