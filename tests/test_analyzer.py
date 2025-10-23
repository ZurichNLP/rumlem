from romansh_lemmatizer.analyzer import Analyzer
from romansh_lemmatizer.utils import Idiom
import os

in_voc = {}

# Path to the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for dial in Idiom:
    voc_path = os.path.join(
        BASE_DIR, "..", "src", "romansh_lemmatizer", "in_voc", f"{dial.value}.txt"
    )
    with open(voc_path, "r", encoding="utf-8") as f:
        fast_dict = {line.strip("\n") for line in f}
    in_voc[dial] = fast_dict


a_surmiran = Analyzer("rm-surmiran", in_voc[Idiom("rm-surmiran")])
a_sutsilv = Analyzer("rm-sutsilv", in_voc[Idiom("rm-sutsilv")])
a_puter = Analyzer("rm-puter", in_voc[Idiom("rm-puter")])
a_sursilv = Analyzer("rm-sursilv", in_voc[Idiom("rm-sursilv")])
a_vallader = Analyzer("rm-vallader", in_voc[Idiom("rm-vallader")])
a_rumgr = Analyzer("rm-rumgr", in_voc[Idiom("rm-rumgr")])


def test_get_lem():
    # Are complete non words (i.e., not in dictionary and not lemmatizable by edit trees) returned as None?
    assert a_surmiran.get_lemma("Switzerland") == [None]
    assert a_surmiran.get_lemma("llama") == [None]

    # Are lemmas that are in the dictionary correctly returned?
    assert a_sutsilv.get_lemma("inventariseias") == ["inventarisar"]
    assert a_sutsilv.get_lemma("Avdànta") == ["avdànt", "avdànt", "avdànt"]

    print(a_puter.get_lemma("mandel"))
    assert a_puter.get_lemma("mandel") == ["mandel", "mandel"]
    assert a_puter.get_lemma("tramunta") == ["tramunter", "tramunter"]

    # In cases where the lemmatizer falls back to the edit trees, is the output formatted correctly?
    # Carreras and abdominala are not in the pledari grond dict, but their edit trees were learned and should return the correct lemma
    assert a_sursilv.get_lemma("Carreras") == ["carrera"]
    assert a_sursilv.get_lemma("abdominala") == ["abdominal"]

    # If a non word can be inflected by an edit tree but it isn't in the in_voc, it should return None
    assert a_sursilv.get_lemma("skies") == [None]
    assert a_sursilv.get_lemma("Lámpara") == [None]


def test_get_unimorph():
    """Are words that are in the dictionary returned with their UniMorph Features?"""

    assert a_vallader.get_unimorph("suprastess") == ["V;COND;3;SG"]
    print(a_vallader.get_unimorph("vuolp"))
    assert a_vallader.get_unimorph("vuolp") == ["N;FEM;SG", "N;FEM;SG", "N;FEM;SG"]

    assert a_surmiran.get_unimorph("suglialeiva") == ["ADJ;FEM;SG"]
    assert a_surmiran.get_unimorph("carogna") == [
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
    ]

    assert a_puter.get_unimorph("corazza") == ["N;FEM;SG", "N;FEM;SG"]
    assert a_puter.get_unimorph("scrollais") == [
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
    ]

    assert a_sursilv.get_unimorph("puschlau") == ["N;MASC;SG"]
    assert a_sursilv.get_unimorph("dumbraziun") == ["N;FEM;SG"]

    assert a_sutsilv.get_unimorph("adigna") == [None]
    assert a_sutsilv.get_unimorph("spartgevla") == ["ADJ;FEM;SG", "ADJ;FEM;SG"]

    assert a_rumgr.get_unimorph("quadrel") == [
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "V;IND;PRS;1;SG",
    ]
    assert a_rumgr.get_unimorph("defunct") == [
        "ADJ;MASC;SG",
        "ADJ;MASC;SG",
        "ADJ;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
    ]


def test_get_de():
    """Can we obtain the de_translation for a word in Pledari Grond, regardless of whether the lemma/MorphAnalysis is available?"""
    # Sursilvan
    # first check word in lemma table
    assert a_sursilv.get_de("pareivel") == [
        "offenbar",
        "sichtlich",
        "offenkundig",
        "sich gut präsentierend",
        "hübsch",
        "artig",
        "adrett",
    ]
    # then check different part of speech
    assert a_sursilv.get_de("arrundar") == [
        "abrunden",
        "vergrössern",
        "Güter zusammenlegen",
        "arrondieren",
        "rund machen",
    ]

    # Sutsilvan
    assert a_sutsilv.get_de("Examinad") == [
        "beschauen",
        "besehen",
        "besichtigen",
        "betrachten",
        "durchleuchten",
        "durchsehen",
        "ergründen",
        "erproben",
        "erwägen",
        "examinieren",
        "prüfen",
        "testen",
        "überprüfen",
        "untersuchen",
    ]
    print(a_sutsilv.get_de("TREMELI"))
    assert a_sutsilv.get_de("TREMELI") == ["dreitausend"]

    # Puter
    assert a_puter.get_de("pegioramaint") == ["Verschlechterung"]
    assert a_puter.get_de("lessa") == ["Siedfleisch"]
    # Vallader
    assert a_vallader.get_de("matutida") == ["schläfrig (von der Hitze z.B.)"]
    assert a_vallader.get_de("insufficiaintamaing") == [
        "mangelhaft (ungenügend)",
        "unbefriedigend",
    ]
    # RUMGR
    assert a_rumgr.get_de("conduita") == [
        "Aufführung",
        "Verhalten",
        "Betragen",
        "Gebaren",
        "Führung",
        "Haltung",
        "Leumund",
        "Benehmen",
    ]
    assert a_rumgr.get_de("dalunga") == ["auf der Stelle", "sofort"]
    # Surmiran
    assert a_surmiran.get_de("coz") == [
        "Bestand",
        "Dauer",
        "Fortbestand",
        "Laufzeit",
        "Zeitdauer",
        "dauern",
    ]
    assert a_surmiran.get_de("ai") == ["ach"]
