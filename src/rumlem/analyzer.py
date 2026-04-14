import json
from pathlib import Path
import pickle
import sys
from rapidfuzz.distance import Levenshtein
from collections import defaultdict
import rumlem.edittree as edittree

BASE_DIR = Path(__file__).parent


class Analyzer:
    """A class to obtain lemmas, unimorph analysis, and de_translations for Romansh tokens"""

    def __init__(self, idiom: str, in_voc: set,learned_et: bool = True):

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

        self.lemma = {lemma for v in self.dict.values() for lemma in v["lemma"]}

        self.edit_trees = []
        self.et_suffix_index = defaultdict(list)

        if self.learned_et:
            sys.modules["edittree"] = edittree
            for pos in "noun", "adj", "verb":
                et_path = BASE_DIR / "edit_trees" / f"{self.idiom}" / f"{pos}" / "et.txt"
                with open(et_path, "rb") as f:
                    self.edit_trees += pickle.load(f)

            for et_pack in self.edit_trees:
                suffix = self._get_expected_suffix(et_pack)
                if suffix is not None:
                    self.et_suffix_index[suffix].append(et_pack)

        self.in_voc = in_voc

        other_de_path = BASE_DIR / "other_de" / f"{self.idiom}.json"

        with open(other_de_path, "r", encoding="utf-8") as f:
            self.other_de = json.load(f)

        self.lemma_by_pos = defaultdict(set)
        for v in self.dict.values():
            for lemma, unimorph in zip(v["lemma"], v["unimorph"]):
                if unimorph:
                    pos = unimorph.split(";")[0]  # "N", "V", "ADJ", "V.PTCP"
                    self.lemma_by_pos[pos].add(lemma)

    def _get_expected_suffix(self, et_pack) -> str | None:
        """Recurse down the right spine to find the expected suffix."""
        node = et_pack["et"]
        while node is not None:
            if isinstance(node.val[0], str):  # leaf node
                return node.val[0]
            node = node.right
        return None

    def analyze(self, tok: str):
        tok = tok.lower().strip()
        entry = self.dict.get(tok)

        lemmas, de_list, unimorph_list = [], [], []

        if entry:
            lemmas.extend(entry["lemma"])
            de_list.extend(entry["DStichwort"])
            unimorph_list.extend(entry["unimorph"])

        if tok in self.other_de:
            amount = len(self.other_de[tok])
            lemmas.extend([tok] * amount)
            de_list.extend(self.other_de[tok])
            unimorph_list.extend([None] * amount)

        if lemmas:
            return lemmas, de_list, unimorph_list

        if tok in self.in_voc:
            return [tok], [None], [None]
        return [None], [None], [None]
        
    def _et_analyze(self, tok: str):
        candidates = []

        for suffix, packs in self.et_suffix_index.items():
            if tok.endswith(suffix):
                for et_pack in packs:
                    out = et_pack["et"].apply(tok)
                    if out != -1:
                        candidates.append((out, et_pack.get("majority_tag")))

        strong_tagged = []
        strong_untagged = []

        for c, tag in candidates:
            if c not in self.lemma:
                continue
            if tag:
                pos = tag.split(";")[0]
                pos_lemmas = self.lemma_by_pos.get(pos, self.lemma)
                if c in pos_lemmas:
                    strong_tagged.append((c, tag))
            else:
                if len(c) <= len(tok):  # lemma can't be longer than inflected form
                    strong_untagged.append((c, tag))

        # Prefer tagged candidates; only use untagged if nothing else found
        strong = strong_tagged if strong_tagged else strong_untagged

        if not strong:
            return None, None

        if len(strong) > 1:
            dist = {c: Levenshtein.normalized_distance(tok, c) for c, _ in strong}
            best = min(dist, key=dist.get)
            match = next((c, tag) for c, tag in strong if c == best)
            return match if match[0] in self.in_voc else (None, None)

        c, tag = strong[0]
        return (c, tag) if c in self.in_voc else (None, None)