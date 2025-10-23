from enum import Enum
from frozendict import frozendict

# Map UniMorph features to categories
FEATURE_MAP = {
    # Mood
    "IND": ("Mood", "IND"),
    "SBJV": ("Mood", "SBJV"),
    "COND": ("Mood", "COND"),
    "IMP": ("Mood", "IMP"),
    # Tense
    "PRS": ("Tense", "PRS"),
    "PST": ("Tense", "PST"),
    "FUT": ("Tense", "FUT"),
    # Aspect
    "IPFV": ("Aspect", "IPFV"),
    # Finiteness
    "NFIN": ("Finiteness", "NFIN"),
    # Verb forms
    "V.PTCP": ("VerbForm", "PTCP"),
    # Person
    "1": ("Person", "1"),
    "2": ("Person", "2"),
    "3": ("Person", "3"),
    # Number
    "SG": ("Number", "SG"),
    "PL": ("Number", "PL"),
    # Gender
    "MASC": ("Gender", "MASC"),
    "FEM": ("Gender", "FEM"),
    "NEUT": ("Gender", "NEUT"),
}


class Idiom(Enum):
    RUMGR = "rm-rumgr"
    SURSILV = "rm-sursilv"
    SUTSILV = "rm-sutsilv"
    SURMIRAN = "rm-surmiran"
    PUTER = "rm-puter"
    VALLADER = "rm-vallader"


def get_features(feat):
    """Format and categorize UniMorph features for MorphAnalysis"""
    if feat:
        feat = feat.split(";")
        if "ADJ" in feat:
            return frozendict({"PoS": "ADJ", "Gender": feat[1], "Number": feat[-1]})
        if "N" in feat:
            return frozendict({"PoS": "N", "Gender": feat[1], "Number": feat[-1]})

        f = {"PoS": "V"}
        for part in feat:
            if part in FEATURE_MAP:
                category, value = FEATURE_MAP[part]
                f[category] = value
        return frozendict(f)

    return None
