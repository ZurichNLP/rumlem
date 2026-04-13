
import json
from pathlib import Path

path = Path(r"c:\Users\Dominic-Asus\Rumantsch_Projekt\lemmatizer-eval\Coverage\eval_results.json")

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

tokens_without_lemma = set()

def collect_tokens(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "tokens_without_lemma" and isinstance(v, (list, set, tuple)):
                tokens_without_lemma.update(v)
            else:
                collect_tokens(v)
    elif isinstance(obj, list):
        for item in obj:
            collect_tokens(item)

collect_tokens(data)

import re

print(f"Found {len(tokens_without_lemma)} unique tokens_without_lemma")

uppercase_tokens = {t for t in tokens_without_lemma if t and t[0].isupper()}
apostrophe_tokens = {t for t in tokens_without_lemma if t.startswith("'") or t.endswith("'")}
number_tokens = {t for t in tokens_without_lemma if any(c.isdigit() for c in t)}
hyphen_tokens = {t for t in tokens_without_lemma if t.startswith("-") or t.endswith("-")}

# anything not a letter, apostrophe, or hyphen
weird_char_tokens = {
    t for t in tokens_without_lemma
    if re.search(r"[^A-Za-zÀ-ÖØ-öø-ÿ'-]", t)
}

special_tokens = (
    uppercase_tokens
    | apostrophe_tokens
    | number_tokens
    | hyphen_tokens
    | weird_char_tokens
)

remaining_tokens = tokens_without_lemma - special_tokens

print(f"Tokens starting with uppercase: {len(uppercase_tokens)}")
print(f"Tokens starting or ending with \"'\": {len(apostrophe_tokens)}")
print(f"Tokens containing numbers: {len(number_tokens)}")
print(f"Tokens starting or ending with '-': {len(hyphen_tokens)}")
print(f"Tokens with weird special chars: {len(weird_char_tokens)}")
print(f"Remaining tokens: {len(remaining_tokens)}")

import json

categories = {
    "uppercase_tokens": uppercase_tokens,
    "apostrophe_tokens": apostrophe_tokens,
    "number_tokens": number_tokens,
    "hyphen_tokens": hyphen_tokens,
    "weird_char_tokens": weird_char_tokens,
    "remaining_tokens": remaining_tokens
}

output = {
    name: {
        "count": len(tokens),
        "tokens": sorted(tokens)
    }
    for name, tokens in categories.items()
}

with open("Coverage/missed_token_analysis.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)