import re
from typing import Optional, List, Dict
import dateparser

# Optional (better) NER fallback
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None

# Optional fuzzy
try:
    from fuzzywuzzy import process
except Exception:
    process = None


MONTH_WORDS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"


def _clean_text_for_extraction(text: str) -> str:
    # normalize whitespace, remove weird OCR artifacts but keep punctuation structure
    t = text.replace('\r', ' ').replace('\t', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    # sometimes OCR adds weird spacing in hyphenated words -> normalize common broken tokens
    t = re.sub(r'\s*-\s*', '-', t)
    return t


def _safe_spacy_person(text: str) -> Optional[str]:
    if not _nlp:
        return None
    doc = _nlp(text)
    # find first PERSON entity with at least two tokens (first+last)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            return ent.text.strip()
    return None


def _safe_spacy_org(text: str) -> Optional[str]:
    if not _nlp:
        return None
    doc = _nlp(text)
    # try longest ORG entity
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ in ("ORG", "FAC", "NORP")]
    if orgs:
        # return longest (heuristic)
        return max(orgs, key=len)
    return None


def _fuzzy_match_company(candidate: str, companies: List[str], threshold: int = 80) -> Optional[str]:
    if not process or not companies:
        return None
    match, score = process.extractOne(candidate, companies)
    if score >= threshold:
        return match
    return None


def extract_details(text: str, known_companies: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Robust extraction: name, course/role, company, duration, domain, date_of_certification.
    known_companies: optional list for fuzzy matching/recognition.
    """
    details = {
        "name": "Not Found",
        "course": "Not Found",
        "company": "Not Found",
        "duration": "Not Found",
        "domain": "Not Found",
        "date_of_certification": "Not Found"
    }

    if not text or not text.strip():
        return details

    t = _clean_text_for_extraction(text)

    # ------------------- NAME -------------------
    # 1) common certificate phrase "presented to", "awarded to", "This is to certify that"
    name_patterns = [
        r'(?:presented to|presented\s+to:|awarded to|awarded to:)\s*([A-Z][A-Za-z\-\.\' ]{3,80}?)\s*(?:for|on|having|who|,|\.|\n)',
        r'(?:this is to certify that|this certifies that)\s*(?:Mr\.|Ms\.|Mrs\.|Dr\.)?\s*([A-Z][A-Za-z\-\.\' ]{3,80}?)\s*(?:has|who|,|\.)'
    ]
    found_name = None
    for p in name_patterns:
        m = re.search(p, t, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            # basic filter: must contain a space (first + last) or be multiword
            if len(candidate.split()) >= 2:
                found_name = candidate
                break

    # 2) fallback: spaCy NER
    if not found_name:
        sp = _safe_spacy_person(t)
        if sp:
            found_name = sp

    # 3) final regex backup: two capitalized words
    if not found_name:
        m2 = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', t)
        if m2:
            found_name = m2.group(1).strip()

    if found_name:
        details["name"] = re.sub(r'\s{2,}', ' ', found_name).strip()

    # ------------------- COURSE / ROLE -------------------
    # Look for "internship as", "as a", "as an", "role", "position", "training as"
    course_patterns = [
        r'(?:for successfully completing\s+|for successfully completing a\s+|for successfully completing the\s+)([A-Za-z &\-]{3,70})',
        r'(?:internship\s*(?:as|for|in|:)?\s*|training\s*(?:as|in|for)?\s*|as\s+an?\s+|role\s*(?:of|:)?\s*)([A-Za-z &\-\(\)\/]{2,80}?)\s*(?=(?:at|with|in|during|for|,|\.|$))',
        r'(?:certificate of|certificate for|course:|program:)\s*([A-Za-z &\-\(\)\/]{2,80}?)\s*(?=(?:by|at|issued|,|\.|$))'
    ]
    found_course = None
    for p in course_patterns:
        m = re.search(p, t, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            # remove trailing words that are company-like accidentally captured
            cand = re.sub(r'\b(at|with|from|during|for|under)\b.*$', '', cand, flags=re.IGNORECASE).strip()
            # remove filler like "Certificate", "Internship"
            cand = re.sub(r'\b(internship|training|certificate|program|course|completion)\b', '', cand, flags=re.IGNORECASE).strip()
            if cand:
                found_course = re.sub(r'\s{2,}', ' ', cand).title()
                break
    if found_course:
        details["course"] = found_course

    # ------------------- COMPANY -------------------
    # Strategy: search phrases like "at <company>" or "with <company>" or bottom contact block
    company_patterns = [
        r'(?:at|with|from|under|in|by)\s+([A-Z][A-Za-z0-9&\-\.,\'\s]{2,120}?(?:Pvt|Pvt\.|Ltd|LLP|Inc|Corporation|Company|Firm|Institute|University|Bazaar|Bank|Group|Solutions|Technologies|Law Firm|Foundation|Enterprises)?)\b',
        # fallback: look for lines with all-caps company names near end / address lines
        r'\b([A-Z][A-Z0-9 &\-\.\']{2,80})(?:\s+Pvt| Ltd| LLP| INC| COMPANY| GROUP| BAZAAR| BANK| FOUNDATION)?\b'
    ]
    found_company = None
    for p in company_patterns:
        m = re.search(p, t, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            # cut if it's too long (stop at 'for successfully' etc)
            cand = re.split(r'\b(for successfully|for completing|during|who|that|has|has successfully)\b', cand, flags=re.IGNORECASE)[0].strip()
            # remove trailing punctuation
            cand = cand.rstrip(' ,.;:-')
            if len(cand) >= 2:
                found_company = cand
                break

    # spaCy fallback
    if not found_company:
        sp_org = _safe_spacy_org(t)
        if sp_org:
            found_company = sp_org

    # try bottom block address (lines with uppercase words)
    if not found_company:
        # often company name appears near address/phone block -> try last 200 chars for multiword caps
        tail = t[-400:]
        m_tail = re.search(r'([A-Z][A-Za-z &\.\']{2,80}(?:\s+(?:Pvt|Ltd|LLP|Inc|Company|Group|Bazaar|Firm))?)', tail)
        if m_tail:
            cand = m_tail.group(1).strip().rstrip(' ,.;:')
            found_company = cand

    # fuzzy match against known list if provided
    if found_company and known_companies:
        fuzzy = _fuzzy_match_company(found_company, known_companies) if process else None
        if fuzzy:
            found_company = fuzzy

    if found_company:
        details["company"] = re.sub(r'\s{2,}', ' ', found_company).title()

    # ------------------- DURATION -------------------
    # patterns like "3-month", "3 month", "54 Days", "1 year", "from 1 Jan 2020 to 31 Mar 2020", or "3-month internship"
    m = re.search(r'(\d{1,3}\s*(?:-|\sto\s)?\s*\d{0,3}\s*(?:day|days|month|months|week|weeks|year|years))', t, re.IGNORECASE)
    if m:
        details["duration"] = m.group(1).strip()
    else:
        m2 = re.search(r'(\d+\s*(?:day|days|month|months|year|years))', t, re.IGNORECASE)
        if m2:
            details["duration"] = m2.group(1).strip()

    # also capture "x-month internship" etc
    m3 = re.search(r'(\d+\s*-\s*month|\d+\s*month(?:s)?)', t, re.IGNORECASE)
    if m3 and details["duration"] == "Not Found":
        details["duration"] = m3.group(1).strip()

    # ------------------- DOMAIN -------------------
    m_dom = re.search(r'(?:domain|field\s*of|area\s*of|specialization)\s*[:\-]?\s*([A-Za-z &\-\/]{3,60})', t, re.IGNORECASE)
    if m_dom:
        details["domain"] = m_dom.group(1).strip().title()

    # ------------------- DATE -------------------
    # find any plausible date using dateparser search
    # dateparser.search.search_dates sometimes provides tuples; use fallback regex too
    try:
        from dateparser.search import search_dates
        res = search_dates(t, settings={'PREFER_DAY_OF_MONTH': 'first'})
        if res:
            # pick a candidate likely to be "date of certification" — prefer patterns near "date", "issued", "certification"
            chosen = None
            for text_snip, dt in res:
                # if text snippet is near keywords, pick it
                if re.search(r'(date of certification|date of cert|issued dated|issued date|date:|date )', t.lower().split(text_snip.lower())[0][-120:].lower()):
                    chosen = text_snip
                    break
            if not chosen:
                # otherwise pick last parsed date (common for certificate date)
                chosen = res[-1][0]
            if chosen:
                details["date_of_certification"] = re.sub(r'(st|nd|rd|th)', '', chosen).strip()
    except Exception:
        # fallback simple regex
        m_date = re.search(r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', t)
        if m_date:
            details["date_of_certification"] = m_date.group(1)

    return details

def validate_certificate(file_path: str) -> dict:
    extracted = extract_text_from_file(file_path)
    clean_cert = clean_text(extracted)
    clean_ref = clean_text(REFERENCE_TEXT)
    similarity = compare_texts_wmd(clean_cert, clean_ref)
    try:
        similarity = round(float(similarity), 2)
    except Exception:
        similarity = 0.0

    details = extract_details(extracted)
    status = "Success"
    if similarity < 0.2:
        status = "Suspect"
    if details.get("company", "Not Found") in ["Not Found", ""]:
        if similarity < 0.5:
            status = "Suspect"

    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    except Exception:
        file_hash = None

    return {
        "status": status,
        "similarity": similarity,
        "name": details.get("name", "Not Found"),
        "course": details.get("course", "Not Found"),
        "company": details.get("company", "Not Found"),
        "domain": details.get("domain", "Not Found"),
        "duration": details.get("duration", "Not Found"),
        "date_of_joining": details.get("date_of_joining", "Not Found"),
        "file_hash": file_hash
    }
