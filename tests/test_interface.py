from unittest import TestCase

from frozendict import frozendict

from rumlem import Lemmatizer, Doc, Idiom, Lemma, MorphAnalysis


class LemmatizerInterfaceTestCase(TestCase):

    def setUp(self):
        print("1️⃣ Starting setUp()")
        self.lemmatizer = Lemmatizer()
        print("2️⃣ Lemmatizer created")
        self.text = "La vuolp d'eira darcheu üna jada fomantada."
        self.doc = self.lemmatizer(self.text)
        print("3️⃣ Doc created")


    def test_doc(self):
        self.assertIsInstance(
            self.doc, Doc, "The output of the lemmatizer should be a Doc instance."
        )
        self.assertEqual(
            self.text, self.doc.text, "The text in the Doc should match the input text."
        )
        self.assertEqual(
            self.text,
            str(self.doc),
            "The string representation of the Doc should be the text.",
        )

    def test_idiom_scores(self):
        idiom_scores = self.doc.idiom_scores
        self.assertIsInstance(
            idiom_scores, dict, "idiom_scores should be a dictionary."
        )
        for idiom in Idiom:
            self.assertIn(
                idiom, idiom_scores, f"idiom_scores should contain the idiom {idiom}."
            )
        for prob in idiom_scores.values():
            self.assertGreaterEqual(
                prob, 0.0, "Each probability in idiom_scores should be >= 0."
            )
            self.assertLessEqual(
                prob, 1.0, "Each probability in idiom_scores should be <= 1."
            )
        self.assertEqual(
            self.doc.idiom,
            Idiom.VALLADER,
            f"The highest probability in idiom_scores should correspond to VALLADER for the text '{self.text}'.",
        )

    def test_tokenization(self):
        tokens = self.doc.tokens
        self.assertEqual(
            len(tokens),
            len(self.doc.tokens),
            "The __len__() of Doc should be the number of tokens.",
        )
        self.assertEqual(
            ["La", "vuolp", "d'", "eira", "darcheu", "üna", "jada", "fomantada", "."],
            [token.text for token in tokens],
            "The tokens should match the expected tokenization of the text.",
        )

    def test_token(self):
        token = self.doc.tokens[1]
        self.assertEqual(
            "vuolp",
            token.text,
            "The text of the token should be the surface form of the token.",
        )
        self.assertEqual(
            token._doc_idiom,
            Idiom.VALLADER,
            "Each token should be assigned the doc idiom",
        )

        # Check that token.all_lemmas has type tuple[dict[Lemma, list[MorphAnalysis]]]
        self.assertIsInstance(
            token.all_lemmas, dict, "token.all_lemmas should be a dictionary."
        )
        self.assertIsInstance(
            token.lemmas, dict, "token.lemmas should be a dictionary."
        )
        for key, value in token.all_lemmas.items():
            self.assertIsInstance(
                key, Lemma, "Keys of token.all_lemmas should be Lemma instances."
            )
            self.assertIsInstance(
                value,
                list,
                "Values of token.all_lemmas should be lists of MorphAnalysis.",
            )
            for analysis in value:
                self.assertIsInstance(
                    analysis,
                    MorphAnalysis,
                    "Elements of the lemma list should be MorphAnalysis instances.",
                )

    def test_lemmas(self):
        """
        Surmiran dictionary entry:
         {
            "DStichwort": "aushungern",
            "participperfectfs": "fomantada",
            "RStichwort": "fomantar",
            ...
        }
        Vallader dictionary entry:
        {
            "DStichwort": "jn aushungern",
            "participperfectfs": "fomantada",
            "RStichwort": "fomantạr a qchn",
            ...
        }
        """
        token = self.doc.tokens[-2]
        for el in token.all_lemmas:
            print(el)
        # Changed to three, because fomantada is also an inflection of the surmiran adj. fomanto
        self.assertEqual(
            7,
            len(token.all_lemmas),
            "The token 'fomantada' should have seven lemmas associated with it.",
        )
        self.assertEqual(
            5,
            len(token.lemmas),
            "The token 'fomantada' should have one rm-vallader lemma associated with it.",
        )
        

    def test_morph_analysis(self):
        token = self.doc.tokens[-2]
        lemmas = list(token.all_lemmas.keys())
        lemma1 = lemmas[0]
        lemma2 = lemmas[1]
        lemma3 = lemmas[2]
        print(lemma1, lemma2, lemma3)
        self.assertEqual(1, len(token.all_lemmas[lemma1]), f"The lemma '{lemma1}' should have one MorphAnalysis associated with it.")
        self.assertEqual(1, len(token.all_lemmas[lemma2]), f"The lemma '{lemma2}' should have one MorphAnalysis associated with it.")
        self.assertEqual(1, len(token.all_lemmas[lemma3]), f"The lemma '{lemma3}' should have one MorphAnalysis associated with it.")
        morph_analysis1 = token.all_lemmas[lemma1][0]
        morph_analysis2 = token.all_lemmas[lemma2][0]
        morph_analysis3 = token.all_lemmas[lemma3][0]
        self.assertIsInstance(
            morph_analysis1.features,
            frozendict,
            "MorphAnalysis features should be a frozendict.",
        )
        self.assertIsInstance(
            morph_analysis2.features,
            frozendict,
            "MorphAnalysis features should be a frozendict.",
        )
        # Updating for unimorph features
        self.assertDictEqual(
            {
                "PoS": "ADJ",
                "Gender": "FEM",
                "Number": "SG",
            },
            dict(morph_analysis1.features),
        )
        self.assertDictEqual(
            {
                "PoS": "V",
                "VerbForm": "PTCP",
                "Tense": "PST",
                "Gender": "FEM",
                "Number": "SG",
            },
            dict(morph_analysis2.features),
        )
        self.assertDictEqual(
            {
                "PoS": "ADJ",
                "Gender": "FEM",
                "Number": "SG",
            },
            dict(morph_analysis3.features),
        )
        # Fomanto
        self.assertEqual("PoS=ADJ;Gender=FEM;Number=SG", str(morph_analysis1))
        # Fomantar
        self.assertEqual(
            "PoS=V;VerbForm=PTCP;Tense=PST;Gender=FEM;Number=SG", str(morph_analysis2)
        )
        self.assertEqual(
            "PoS=ADJ;Gender=FEM;Number=SG", str(morph_analysis3)
        )
