"""Test the implementation of the Romansh dicitonary-based idiom identification module"""
from pathlib import Path

from rumlem.tokenizer import Rm_Tokenizer
from rumlem.idiom_id import get_scores
from rumlem.utils import Idiom
import os


in_voc = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for dial in Idiom:
    voc_path = os.path.join(
        BASE_DIR, "..", "src", "rumlem", "in_voc", f"{dial.value}.txt"
    )
    with open(voc_path, "r", encoding="utf-8") as f:
        fast_dict = set()
        for line in f:
            fast_dict.add(line.strip("\n"))
    in_voc[dial] = fast_dict



def test_typing():
    t = Rm_Tokenizer(lang="rm-vallader")

    sample = [
        "El ha noscha glüna, cur chi plouva, cur chi naiva e cur chi'd es sulai.",
        "",
        "plouva",
    ]

    for s in sample:
        scores = get_scores(t.tokenize(s),in_voc=in_voc)
        assert isinstance(scores, dict)

        for k, v in scores.items():
            assert isinstance(k, Idiom)
            assert isinstance(v, float)
            assert 0 <= v <= 1
        assert len(scores) == 6

def test_idiom_scores():
    """Regardless of whether the method correctly identifies the idiom, are the scores what we expect?"""
    sample = ["El ha NOSCHA glüna",
              "El â schleata LUNA",
              "EL ha schliata lUna"]
    
    t = Rm_Tokenizer(lang = None)

    for i,s in enumerate(sample):
        scores = get_scores(t.tokenize(s), in_voc=in_voc)

        if i == 0:
            assert scores[Idiom.PUTER] == 1.0
            assert scores[Idiom.SURMIRAN] == 0.5
        elif i == 1:
            assert scores[Idiom.SUTSILV] == 1.0
            assert scores[Idiom.VALLADER] == 0.5
        else:
            assert scores[Idiom.SURSILV] == 1.0
            assert scores[Idiom.RUMGR] == 0.75
