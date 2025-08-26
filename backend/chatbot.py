import os
import pandas as pd
from openai import OpenAI

# OpenAI-Client
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# FAQ laden
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "faq.csv")
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame(columns=["frage","antwort"])

def search_faq(question: str):
    q = (question or "").lower()
    for _, row in df.iterrows():
        if str(row.get("frage","")).lower() in q:
            return row.get("antwort")
    # fallback: Teil-Keywords
    tokens = [t for t in q.split() if len(t) > 3]
    for _, row in df.iterrows():
        faq_q = str(row.get("frage","")).lower()
        for t in tokens:
            if t in faq_q:
                return row.get("antwort")
    return None

def get_ai_answer(question: str):
    if not client:
        return "(OpenAI API-Key fehlt. Bitte OPENAI_API_KEY setzen.)"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":question}],
        max_tokens=300,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

def chatbot_response(user_input: str) -> str:
    faq_ans = search_faq(user_input)
    if faq_ans:
        return faq_ans
    return get_ai_answer(user_input)
