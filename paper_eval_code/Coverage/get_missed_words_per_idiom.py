import json
import re

def is_special(t):
    return (
        not t
        or t[0].isupper()
        or t.startswith("'") or t.endswith("'")
        or any(c.isdigit() for c in t)
        or t.startswith("-") or t.endswith("-")
        or bool(re.search(r"[^A-Za-zÀ-ÖØ-öø-ÿ'-]", t))
    )

with open("eval_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

unknown_words_per_idiom = {idiom: set() for idiom in data.keys()}
tokens_without_lemma = set()

for idiom, results in data.items():
    for bucket, bucket_results in results.items():
        for sample, sample_results in bucket_results.items():
            for t in sample_results.get("tokens_without_lemma", []):
                if not is_special(t):
                    tokens_without_lemma.add(t)
                    unknown_words_per_idiom[idiom].add(t)

for idiom, unknown_words in unknown_words_per_idiom.items():
    print(f"{idiom}: {len(unknown_words)} remaining tokens without lemma")

print(f"total unique tokens without lemma: {len(tokens_without_lemma)}")
# save the per idiom unknown words to a json for later analysis
with open("unknown_words_per_idiom.json", "w", encoding="utf-8") as f:
    json.dump({idiom: list(words) for idiom, words in unknown_words_per_idiom.items()}, f, ensure_ascii=False, indent=2)
