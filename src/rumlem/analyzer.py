import json
from pathlib import Path
import pickle
import sys

from jiwer import cer

import romansh_lemmatizer.edittree as edittree

BASE_DIR = Path(__file__).parent


class Analyzer:
    """A class to obtain lemmas, unimorph analysis, and de_translations for Romansh tokens"""

    def __init__(self, idiom: str, in_voc: set, learned_et: bool = True):

        self.idiom = idiom

        self.learned_et = learned_et

        assert self.idiom in [
            "rm-rumgr",
            "rm-surmiran",
            "rm-sursilv",
            "rm-sutsilv",
            "rm-puter",
            "rm-vallader",
        ]

        json_path = BASE_DIR / "lemma_tables" / f"{self.idiom}.json"

        with open(json_path, "r", encoding="utf-8") as f:
            self.dict = json.load(f)

        lem = []
        for v in self.dict.values():
            lem += v["lemma"]

        self.lemma = lem
        if self.learned_et:
            self.edit_trees = []

            for pos in "noun", "adj", "verb":
                et_path = (
                    BASE_DIR / "edit_trees" / f"{self.idiom}" / f"{pos}" / "et.txt"
                )
                sys.modules["edittree"] = edittree
                with open(et_path, "rb") as f:
                    self.edit_trees += pickle.load(f)

        self.in_voc = in_voc

        other_de_path = BASE_DIR / "other_de" / f"{self.idiom}.json"

        with open(other_de_path, "r", encoding="utf-8") as f:
            self.other_de = json.load(f)

    def get_lemma(self, tok: str):
        """Obtain lemma through table look up; backs off
        to unsupervised edit tree rules if no lemma found
        """
        tok = tok.lower().strip()
        entry = self.dict.get(tok)
        entry_ls = []
        if entry:
            entry_ls.extend(entry["lemma"])
        if tok in self.other_de: # Augment the results with other_de entries
              amount = len(self.other_de[tok]) # we need to add the lemma as many times as there are de translations for correct zipping later
              tok_ls = [tok] * amount
              entry_ls.extend(tok_ls)
        if entry_ls:
            return entry_ls
        
        # Check if there's a lemma from the edit trees
        if self.learned_et:
            et_out = self._et_lemma(tok)
            if et_out:
                return [et_out]

        # Assume the token is a lemma
        return [tok] if tok in self.in_voc else [None]

    def _et_lemma(self, tok: str):
        candidates = []

        for et_pack in self.edit_trees:
            et = et_pack["et"]
            out = et.apply(tok)

            if out != -1:
                candidates.append(out)

        strong = [c for c in candidates if c in self.lemma]

        if len(strong) > 1:
            # Choose the candidate with the lowest edit distance to the tok:
            dist = {}
            for c in strong:
                dist[c] = cer(tok, c)
            out = min(dist, key=dist.get)
            return out if out in self.in_voc else None

        return strong[0] if strong and strong[0] in self.in_voc else None

    def get_unimorph(self, tok: str):
        """Obtain Unimorph annotation for N, V, and ADJ
        in the Pledari Grond Dict"""
        tok = tok.lower().strip()
        entry = self.dict.get(tok)
        if entry:
            return entry["unimorph"]
        return [None]

    def get_de(self, tok: str):
        """Obtain the German word corresponding to Romansh terms in the Pledari Grond Dict"""
        tok = tok.lower().strip()
        entry = self.dict.get(tok)
        entry_ls = []
        if entry:
            entry_ls.extend(entry["DStichwort"])
        if tok in self.other_de: # Augment the results with other_de entries
           entry_ls.extend(self.other_de[tok])
        return entry_ls if entry_ls else [None]

