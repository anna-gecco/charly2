import os
import pandas as pd
import difflib
from openai import OpenAI

# OpenAI Client
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# Pfad zu FAQ-Datei
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "faq.csv")
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame(columns=["frage", "antwort"])

def search_faq(question: str):
    """Durchsucht die FAQ-Liste nach der passendsten Antwort."""
    q = (question or "").lower().strip()
    if not q:
        return None

    # --- 1) Exakte oder Teilstring-Suche ---
    for _, row in df.iterrows():
        faq_q = str(row.get("frage", "")).lower().strip()
        if faq_q and faq_q in q:
            return row.get("antwort")

    # --- 2) Fuzzy-Suche mit difflib ---
    faq_questions = [str(row.get("frage", "")).lower().strip() for _, row in df.iterrows()]
    matches = difflib.get_close_matches(q, faq_questions, n=1, cutoff=0.65)
    if matches:
        match = matches[0]
        ans_row = df[df["frage"].str.lower().str.strip() == match]
        if not ans_row.empty:
            return ans_row.iloc[0]["antwort"]

    # --- 3) Token-Suche (Backup) ---
    tokens = [t for t in q.split() if len(t) > 3]
    for _, row in df.iterrows():
        faq_q = str(row.get("frage", "")).lower()
        for t in tokens:
            if t in faq_q:
                return row.get("antwort")

    return None

def get_ai_answer(question: str):
    """Fragt die OpenAI-API, falls keine FAQ-Antwort gefunden wurde."""
    if not client:
        return ("(OpenAI API-Key fehlt — setze OPENAI_API_KEY in deiner Shell, "
                "dann kann der Chatbot KI-Antworten generieren.)")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        max_tokens=300,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

def chatbot_response(user_input: str) -> str:
    """Gibt zuerst FAQ-Antwort zurück, sonst KI-Antwort."""
    faq_ans = search_faq(user_input)
    if faq_ans:
        return faq_ans
    return get_ai_answer(user_input)
