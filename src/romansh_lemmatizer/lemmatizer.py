from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from frozendict import frozendict

from romansh_lemmatizer.analyzer import Analyzer
from romansh_lemmatizer.idiom_id import get_scores
from romansh_lemmatizer.tokenizer import Rm_Tokenizer
from romansh_lemmatizer.utils import Idiom, get_features


@dataclass(frozen=True)
class Lemma:
    idiom: Idiom
    text: str
    translation_de: str

    def __str__(self):
        return f"{self.idiom.value}::{self.text}"

    def __repr__(self):
        return f"{self.idiom.value}::{self.text}"

    def __eq__(self, other):
        return (
            isinstance(other, Lemma)
            and self.idiom == other.idiom
            and self.text == other.text
            and self.translation_de == other.translation_de
        )

    def __hash__(self):
        # Collapse dictionary entries when the idiom and text are the same
        return hash((self.idiom, self.text, self.translation_de))


@dataclass(frozen=True)
class MorphAnalysis:
    """
    Uses feature values from Unimorph for Nouns, Adj, and Verbs
    """

    features: frozendict[str, str]

    def __str__(self):
        """
        "Feat1;Feat2;..."
        """
        return ";".join(f"{k}={v}" for k, v in self.features.items())

    def __repr__(self):
        return (
            ";".join(f"{k}={v}" for k, v in self.features.items())
            if self.features
            else "null"
        )


@dataclass(frozen=True)
class Token:
    text: str
    all_lemmas: dict[Lemma, list[MorphAnalysis]]
    _doc_idiom: Idiom = None

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"{self.text!r}"

    @property
    def lemmas(self) -> dict[Lemma, list[MorphAnalysis]]:
        """
        Returns only lemmas for the document's idiom.
        If no document idiom is set, returns all lemmas.
        """
        if self._doc_idiom is None:
            return self.all_lemmas

        return {
            lemma: analyses
            for lemma, analyses in self.all_lemmas.items()
            if lemma.idiom == self._doc_idiom
        }


@dataclass(frozen=True)
class Doc:
    text: str
    tokens: list[Token]
    _in_voc: dict[Idiom, set]
    _user_idiom: Idiom = None  # Pass an optional idiom

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.tokens)

    def __post_init__(self):
        """
        Set the document idiom reference in all tokens after initialization.
        """
        new_tokens = []

        for token in self.tokens:
            new_tokens.append(Token(token.text, token.all_lemmas, self.idiom))

        object.__setattr__(self, "tokens", new_tokens)

    @property
    def idiom_scores(self) -> dict[Idiom, float]:
        """
        Get the idiom scores for a given document
        """
        if self._user_idiom:
            # Give all weight to the idiom the user passed
            return {
                idiom: (1.0 if idiom == self._user_idiom else 0.0) for idiom in Idiom
            }

        # Do Dictionary-based idiom ID
        return get_scores([tok.text for tok in self.tokens], self._in_voc)

    @property
    def idiom(self) -> Idiom:
        """
        Returns the idiom with the highest idiom score.
        """
        return Idiom(max(self.idiom_scores, key=self.idiom_scores.get))


class Lemmatizer:

    def __init__(self, idiom: Idiom = None, leanred_et: bool = True):
        if isinstance(idiom, str):
            idiom = Idiom(idiom)
        self.idiom = idiom
        # If no idiom passed, use the unknown idiom tokenizer
        self.tokenizer = Rm_Tokenizer(lang=self.idiom.value if self.idiom else None)

        self.in_voc = {}
        BASE_DIR = Path(__file__).parent
        for dial in Idiom:
            voc_path = BASE_DIR / "in_voc" / f"{dial.value}.txt"
            with open(voc_path, "r", encoding="utf-8") as f:
                fast_dict = set()
                for line in f:
                    fast_dict.add(line.strip("\n"))
            self.in_voc[dial] = fast_dict

        # Initialize all analyzers
        self._analyzers = {
            i: Analyzer(idiom=i.value, in_voc=self.in_voc[i], learned_et=leanred_et)
            for i in Idiom
        }

    def __call__(self, text: str) -> Doc:
        # Tokenize the text
        toks = self.tokenizer.tokenize(text)

        tok_obj = []

        for t in toks:
            full_lemma = defaultdict(list)
            t_lower = t.lower()
            from itertools import zip_longest

            for idiom in Idiom:
                a = self._analyzers[idiom]
                lemma = a.get_lemma(t_lower)
                de = a.get_de(t_lower)
                unimorph = a.get_unimorph(t_lower)

                # safer: align lists of possibly different length
                for l, d, u in zip_longest(lemma, de, unimorph, fillvalue=None):
                    if l:
                        lem = Lemma(idiom, l, d if d else "null")
                        analysis = MorphAnalysis(get_features(u))
                        full_lemma[lem].append(analysis)

            tok_obj.append(Token(t, full_lemma, self.idiom))

        return Doc(
            text,
            tok_obj,
            self.in_voc,
            self.idiom,
        )
