import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find("corpora/stopwords")
except Exception:
    nltk.download("stopwords", quiet=True)

IMPORTANT_TERMS = {
    "intern", "internship", "training", "certificate", "law", "firm",
    "university", "college", "company", "organization", "duration",
    "legal", "project", "ugc", "period", "from", "to", "month", "months"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s\-/,:.\']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set()

    words = []
    for w in text.split():
        lw = w.lower()
        if lw in IMPORTANT_TERMS or lw not in stop_words:
            words.append(w)
    return " ".join(words)
