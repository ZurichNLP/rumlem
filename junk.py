import sys

sys.path.insert(0, r"C:\Users\Dominic-Asus\Rumantsch_Projekt\github-release\src")
from rumlem import Lemmatizer

lemmatizer = Lemmatizer(learned_et=True)
doc = lemmatizer("fomantada")
for t in doc.tokens:
    print(t.lemmas)
