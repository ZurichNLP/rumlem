from rumlem.analyzer import Analyzer
from rumlem.utils import Idiom
import os

in_voc = {}

# Path to the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for dial in Idiom:
    voc_path = os.path.join(
        BASE_DIR, "..", "src", "rumlem", "in_voc", f"{dial.value}.txt"
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
    assert a_surmiran.analyze("Switzerland")[0] == [None]
    assert a_surmiran.analyze("llama")[0] == [None]

    # Are lemmas that are in the dictionary correctly returned?
    assert a_sutsilv.analyze("inventariseias")[0] == ["inventarisar"]
    assert a_sutsilv.analyze("Avdànta")[0] == ["avdànta", "avdànta", "avdànta"]

    assert a_puter.analyze("mandel")[0] == ["mandel", "mandel"]
    assert a_puter.analyze("tramunta")[0] == ["tramunter", "tramunter"]

    # In cases where the lemmatizer falls back to the edit trees, is the output formatted correctly?
    # Carreras and abdominala are not in the pledari grond dict, but their edit trees were learned and should return the correct lemma
    assert a_sursilv.analyze("Carreras")[0] == ["carrera", "carrera"]
    assert a_sursilv.analyze("abdominala")[0] == ["abdominal"]

    # If a non word can be inflected by an edit tree but it isn't in the in_voc, it should return None
    assert a_sursilv.analyze("skies")[0] == [None]
    assert a_sursilv.analyze("Lámpara")[0] == [None]


def test_get_unimorph():
    """Are words that are in the dictionary returned with their UniMorph Features?"""

    assert a_vallader.analyze("suprastess")[2] == ["V;COND;3;SG"]
    assert a_vallader.analyze("vuolp")[2] == ["N;FEM;SG", "N;FEM;SG", "N;FEM;SG"]

    assert a_surmiran.analyze("suglialeiva")[2] == ["ADJ;FEM;SG"]
    assert a_surmiran.analyze("carogna")[2] == [
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
        "N;FEM;SG",
    ]

    assert a_puter.analyze("corazza")[2] == ["N;FEM;SG", "N;FEM;SG"]
    assert a_puter.analyze("scrollais")[2] == [
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
        "V;IND;PRS;2;PL",
    ]

    assert a_sursilv.analyze("puschlau")[2] == ["N;MASC;SG", "V.PTCP;PST;MASC;SG", "V.PTCP;PST;MASC;SG"]
    assert a_sursilv.analyze("dumbraziun")[2] == ["N;FEM;SG"]

    assert a_sutsilv.analyze("adigna")[2] == [None, None, None, None, None, None, None, None, None]
    assert a_sutsilv.analyze("spartgevla")[2] == ["ADJ;FEM;SG", "ADJ;FEM;SG"]

    assert a_rumgr.analyze("quadrel")[2] == [
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "N;MASC;SG",
        "V;IND;PRS;1;SG"
    ]
    assert a_rumgr.analyze("defunct")[2] == [
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
    assert a_sursilv.analyze("pareivel")[1] == [
        "offenbar",
        "sichtlich",
        "offenkundig",
        "sich gut präsentierend",
        "hübsch",
        "artig",
        "adrett",
    ]
    # then check different part of speech
    assert len(a_sursilv.analyze("arrundar")[1]) == 35

    assert a_sursilv.analyze("e")[1] == ["dritter Ton der Tonleiter in C-Dur", "und", "plus"] 

    # Sutsilvan
    assert a_sutsilv.analyze("Examinad")[1] == [
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
    assert a_sutsilv.analyze("TREMELI")[1] == ["dreitausend"]
    
    # Puter
    assert a_puter.analyze("pegioramaint")[1] == ["Verschlechterung"]
    assert a_puter.analyze("lessa")[1] == ["Siedfleisch"]
    # Vallader
    assert a_vallader.analyze("matutida")[1] == ["schläfrig (von der Hitze z.B.)"]
    assert a_vallader.analyze("insufficiaintamaing")[1] == [
        "mangelhaft (ungenügend)",
        "unbefriedigend",
    ]
    # RUMGR
    assert a_rumgr.analyze("conduita")[1] == [
        "Aufführung",
        "Verhalten",
        "Betragen",
        "Gebaren",
        "Führung",
        "Haltung",
        "Leumund",
        "Benehmen",
        "Lebenswandel"
    ]
    assert a_rumgr.analyze("dalunga")[1] == ["auf der Stelle", "sofort"]
    # Surmiran
    assert a_surmiran.analyze("coz")[1] == [
        "Bestand",
        "Dauer",
        "Fortbestand",
        "Laufzeit",
        "Zeitdauer",
        "dauern",
    ]
    assert a_surmiran.analyze("ai")[1] == ["ach"]

