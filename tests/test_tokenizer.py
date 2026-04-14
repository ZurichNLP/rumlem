"""Test Tokenizer class"""

from rumlem.tokenizer import Rm_Tokenizer

text = {
    "rm-rumgr": [
        "lavurer da guaud",
        """
        Mesemna, ils 23 da settember 2009, visita la regenza da l'Appenzell dadens il Grischun.
        """,
        "Tudestga",
        "qua sa sent'ins bain",
    ],
    "rm-sursilv": [
        "luvrer d'uaul",
        "1. Il pirat selegra: «Jeu hai anflau in scazi!»",
        "Tudestga",
    ],
    "rm-puter": [
        "bos-cher",
        "1. Il pirat s'allegra: «Eau d'he chatto ün s-chazi!»",
        "Tudas-cha",
        "A do eir pleds chi'ns pleschan meglder cu oters",
    ],
}

tokenized = {
    "rm-rumgr": [
        ["lavurer", "da", "guaud"],
        [
            "Mesemna",
            ",",
            "ils",
            "23",
            "da",
            "settember",
            "2009",
            ",",
            "visita",
            "la",
            "regenza",
            "da",
            "l'",
            "Appenzell",
            "dadens",
            "il",
            "Grischun",
            ".",
        ],
        ["Tudestga"],
        # Before t, apostrope belongs to the left word
        ["qua", "sa", "sent'", "ins", "bain"],
    ],
    "rm-sursilv": [
        ["luvrer", "d'", "uaul"],
        [
            "1",
            ".",
            "Il",
            "pirat",
            "selegra",
            ":",
            "«",
            "Jeu",
            "hai",
            "anflau",
            "in",
            "scazi",
            "!",
            "»",
        ],
        ["Tudestga"],
    ],
    "rm-puter": [
        ["bos-cher"],
        [
            "1",
            ".",
            "Il",
            "pirat",
            "s'",
            "allegra",
            ":",
            "«",
            "Eau",
            "d'",
            "he",
            "chatto",
            "ün",
            "s-chazi",
            "!",
            "»",
        ],
        ["Tudas-cha"],
        [
            "A",
            "do",
            "eir",
            "pleds",
            "chi",
            # Before a vowel, 'ns
            "'ns",
            "pleschan",
            "meglder",
            "cu",
            "oters",
        ],
    ],
}


def test_idiom_specific_tokenization():
    """Test idiom specific tokenization"""
    for idiom, samp in text.items():
        tokenizer = Rm_Tokenizer(lang=idiom)
        for i, t in enumerate(samp):
            doc = tokenizer.tokenize(t)
            # Check tokenization
            assert (
                doc == tokenized[idiom][i]
            ), f"Tokenization failed for {idiom} on sample {i}: {doc} != {tokenized[idiom][i]}"


def test_general_tokenization():
    """Test idiom specific tokenization"""
    tokenizer = Rm_Tokenizer(lang=None)
    for idiom, samp in text.items():
        for i, t in enumerate(samp):
            doc = tokenizer.tokenize(t)
            # Check tokenization
            assert doc == tokenized[idiom][i]


def test_protected_patterns():
    tokenizer = Rm_Tokenizer(lang=None)

    assert tokenizer.tokenize("sent'ins") == ["sent'", "ins"]

    assert tokenizer.tokenize("'m") == ["'m"]

    assert tokenizer.tokenize("agrada'igls") == ["agrada", "'igls"]


def test_apos():
    tokenizer = Rm_Tokenizer(lang=None)

    assert tokenizer.tokenize("’m") == ["'m"]

    assert tokenizer.tokenize("l’Appenzell") == ["l'", "Appenzell"]

    assert tokenizer.tokenize("minch’è") == ["minch'", "è"]
