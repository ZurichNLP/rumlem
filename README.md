# Usage

```python
from lemmatizer import Lemmatizer

lemmatizer = Lemmatizer()
sent = "La vuolp d'eira darcheu üna jada fomantada."
doc = lemmatizer(sent)
```

```python
print("Automatic Idiom Detection:")
# If no idiom is passed by the user, automatic idiom detection occurs
print(f"The sentence '{sent}' is in:", doc.idiom) # <Idiom.VALLADER: 'rm-vallader'>

print("\nProbabilities across idioms:")
for k, v in doc.idiom_scores.items():
    print("\t", k, v) # {<Idiom.RUMGR: 'rm-rumgr'>: 0.7777777777777778, <Idiom.SURSILV: 'rm-sursilv'>: 0.2222222222222222,...}
```

```python
idiom = "rm-vallader"
vallader_lemmatizer = Lemmatizer(idiom=idiom)
doc = vallader_lemmatizer(sent)

print(f"\nPassing '{idiom}' as an argument:")
print(f"The sentence '{sent}' is in: ", doc.idiom) # <Idiom.VALLADER: 'rm-vallader'>
print("\nProbabilities across idioms:")
for k, v in doc.idiom_scores.items():
    print("\t", k, v) # {<Idiom.RUMGR: 'rm-rumgr'>: 0.7777777777777778, <Idiom.SURSILV: 'rm-sursilv'>: 0.2222222222222222,...}
```

```python
print("\n", doc.tokens) # ['La', 'vuolp', "d'", 'eira', 'darcheu', 'üna', 'jada', 'fomantada', '.']
token = doc.tokens[-2]
```

```python
print(f"\nPrint {idiom}-lemmas of token '{token}'")
print(token.lemmas) # {rm-vallader::fomantar: [PoS=V;VerbForm=PTCP;Tense=PST;Gender=FEM;Number=SG]}

```

```python
print(f"\nPrint all lemmas of token '{token}'")
for t in token.all_lemmas:
    print(t)
# {
#   rm-surmiran::fomanto: [PoS=ADJ;Gender=FEM;Number=SG],
#   rm-surmiran::fomantar: [PoS=V;VerbForm=PTCP;Tense=PST;Gender=FEM;Number=SG],
#   rm-vallader::fomantar: [PoS=V;VerbForm=PTCP;Tense=PST;Gender=FEM;Number=SG]
# }
```

```python
token = doc.tokens[1]
lemma = list(token.lemmas.keys())

print(f"\nThe German translation of a lemma, here '{token}' is an attribute of the Lemma object")
for l in lemma:
    print(f"{l}: {l.translation_de}")

# rm-vallader::vuolp: Filou (Gauner, Spitzbube)
# rm-vallader::vuolp: Fuchs
# rm-vallader::vuolp: Schlauberger (Filou)
```
