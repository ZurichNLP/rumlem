"""Implement dictionary-based LID for lemmatizer"""

from romansh_lemmatizer.utils import Idiom


def _get_counts(toks: list, fast_dict: set):
    t = 0

    for tok in toks:
        if tok.lower() in fast_dict:
            t += 1
    try:
        out = t / len(toks)
    except ZeroDivisionError:
        out = 0.0
    return out


def get_scores(toks, in_voc: dict[Idiom, set]) -> dict[Idiom, float]:
    """Calculate the proportion of tokens in a document that belong to the vocabulary of a given idiom"""
    output = {}

    for dial in in_voc.keys():
        fast_dict = in_voc[dial]

        output[dial] = _get_counts(toks, fast_dict)

    return output
