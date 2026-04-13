from config import STOPWORDS

def _remove_stopwords(text):
    return [w for w in text.split() if w.lower() not in STOPWORDS]

def _safe_ratio(correct: int, total: int) -> float:
    return round((correct / total), 2) if total else 0.0
