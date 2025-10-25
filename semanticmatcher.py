from gensim.models import KeyedVectors
import os
import numpy as np

MODEL_PATH = "models/GoogleNews-vectors-negative300.bin"

w2v = None
if os.path.exists(MODEL_PATH):
    try:
        w2v = KeyedVectors.load_word2vec_format(MODEL_PATH, binary=True)
    except Exception:
        w2v = None

def _w2v_similarity_between_words(word1: str, word2: str) -> float:
    try:
        return float(w2v.similarity(word1, word2))
    except Exception:
        return 0.0

def compare_texts_wmd(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0

    text1_tokens = [t.lower() for t in text1.split() if len(t) > 1]
    text2_tokens = [t.lower() for t in text2.split() if len(t) > 1]

    if w2v:
        sims = []
        sample1 = text1_tokens[:200]
        sample2 = set(text2_tokens[:200])
        for t in sample1:
            if t in w2v.key_to_index:
                best = 0.0
                for s in sample2:
                    if s in w2v.key_to_index:
                        sim = _w2v_similarity_between_words(t, s)
                        if sim > best:
                            best = sim
                sims.append(best)
        if sims:
            avg = float(np.mean(sims))
            return max(0.0, min(1.0, (avg + 1) / 2))
        else:
            return 0.0

    set1 = set(text1_tokens)
    set2 = set(text2_tokens)
    if not set1 or not set2:
        return 0.0
    inter = set1 & set2
    union = set1 | set2
    return float(len(inter)) / float(len(union))

RECOGNIZED_COMPANIES = [
    "Deloitte", "EY", "PwC", "KPMG", "TCS", "Infosys", "Wipro",
    "Accenture", "Google", "Microsoft", "Amazon", "IBM", "Carter & Mills",
    "Law Firm", "Ministry", "High Court", "Supreme Court"
]

def find_recognized_company(text: str):
    if not text:
        return None
    tl = text.lower()
    for c in RECOGNIZED_COMPANIES:
        if c.lower() in tl:
            return c
    return None
