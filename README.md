
# License
The romansh_lemmatizer software is licensed under the MIT License © 2025 University of Zurich (UZH). See the LICENSE file for details.

# Acknowledgements and Data Rights
The underlying dictionary data is the property of Uniun dals Grischs (UdG) and may only be used for the romansh_lemmatizer itself. Any other use of the dictionary data is strictly prohibited.

# Description
This package is a dictionary-based romansh lemmatizer. It is not context-aware. Functionalities include:
- Tokenization of sentences in any romansh idiom
- Lemmatization of tokens, within a specific idiom or across idioms
- Lemmas contain unimorph features for verbs, nouns and adjectives
- Lemmas contain and German translations

# Usage
## Installation
`pip install git+https://github.com/ZurichNLP/romansh_lemmatizer.git@v1.0.0`

## Examples
### Initialising the lemmatizer
```python
from lemmatizer import Lemmatizer

lemmatizer = Lemmatizer()
sent = "La vuolp d'eira darcheu üna jada fomantada."
doc = lemmatizer(sent)
```

### Automatic idiom detection
```python
print("Automatic Idiom Detection:")
# If no idiom is passed by the user, automatic idiom detection occurs
print(f"The sentence '{sent}' is in:", doc.idiom) # <Idiom.VALLADER: 'rm-vallader'>

print("\nProbabilities across idioms:")
for k, v in doc.idiom_scores.items():
    print("\t", k, v) # {<Idiom.RUMGR: 'rm-rumgr'>: 0.7777777777777778, <Idiom.SURSILV: 'rm-sursilv'>: 0.2222222222222222,...}
```

### Idiom detection given a lang-specifically initialised lemmatizer
```python
idiom = "rm-vallader"
vallader_lemmatizer = Lemmatizer(idiom=idiom)
doc = vallader_lemmatizer(sent)

print(f"\nPassing '{idiom}' as an argument:")
print(f"The sentence '{sent}' is in: ", doc.idiom) # <Idiom.VALLADER: 'rm-vallader'>
print("\nProbabilities across idioms:")
for k, v in doc.idiom_scores.items():
    print("\t", k, v) # {<Idiom.RUMGR: 'rm-rumgr'>: 0.0, <Idiom.SURSILV: 'rm-sursilv'>: 0.0,...}
```

### Accessing the tokens and their attributes
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

# Development

## Installation
`pip install -e ".[dev]"`

## Running the tests
`python -m unittest discover -s tests`
`pytest -v`

