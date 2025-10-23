from frozendict import frozendict

from romansh_lemmatizer.utils import get_features


def test_verbs():
    in_feat = {
        "V.PTCP;PST;MASC;SG": frozendict(
            {
                "PoS": "V",
                "VerbForm": "PTCP",
                "Tense": "PST",
                "Gender": "MASC",
                "Number": "SG",
            }
        ),
        "V;IND;FUT;3;SG": frozendict(
            {"PoS": "V", "Mood": "IND", "Tense": "FUT", "Person": "3", "Number": "SG"}
        ),
        "V;IND;PST;2;SG;IPFV": frozendict(
            {
                "PoS": "V",
                "Mood": "IND",
                "Tense": "PST",
                "Person": "2",
                "Number": "SG",
                "Aspect": "IPFV",
            }
        ),
        "V;NFIN": frozendict({"PoS": "V", "Finiteness": "NFIN"}),
    }

    for k, v in in_feat.items():
        assert get_features(k) == v


def test_n_adj():
    in_feat = {
        "N;MASC;SG": frozendict({"PoS": "N", "Gender": "MASC", "Number": "SG"}),
        "N;FEM;SG": frozendict({"PoS": "N", "Gender": "FEM", "Number": "SG"}),
        "ADJ;MASC;PL": frozendict({"PoS": "ADJ", "Gender": "MASC", "Number": "PL"}),
        "ADJ;FEM;PL": frozendict({"PoS": "ADJ", "Gender": "FEM", "Number": "PL"}),
    }
    for k, v in in_feat.items():
        assert get_features(k) == v
