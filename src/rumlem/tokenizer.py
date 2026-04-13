"""Wrapper for Italian Moses tokenizer to respect rules of
apostrophe contractions in romansh varieties"""

import re

from sacremoses import MosesTokenizer


class Rm_Tokenizer:
    def __init__(self, lang: str):

        self.lang = lang if lang else "unk"

        assert self.lang in [
            "rm-rumgr",
            "rm-surmiran",
            "rm-sursilv",
            "rm-sutsilv",
            "rm-puter",
            "rm-vallader",
            "unk",
        ]

        # Add the protected patterns
        if self.lang == "rm-rumgr":
            self.protected = [r"(?<!\w)'ins\b"]
        elif self.lang == "rm-surmiran":
            self.protected = [
                r"(?<!\w)'m\b",
                r"(?<!\w)'l\b",
                r"(?<!\w)'la\b",
                r"(?<!\w)'ns\b",
                r"(?<!\w)'ls\b",
                r"(?<!\w)'las\b",
            ]
        elif self.lang == "rm-sursilv":
            self.protected = [r"(?<!\w)'l\b", r"(?<!\w)'la\b", r"(?<!\w)'las\b"]
        elif self.lang == "rm-sutsilv":
            self.protected = [
                r"(?<!\w)'ign\b",
                r"(?<!\w)'gl\b",
                r"(?<!\w)'igl\b",
                r"(?<!\w)'igls\b",
            ]
        elif self.lang == "rm-puter":
            self.protected = [
                r"(?<!\w)'m\b",
                r"(?<!\w)'l\b",
                r"(?<!\w)'la\b",
                r"(?<!\w)'ns\b",
                r"(?<!\w)'ls\b",
                r"(?<!\w)'las\b",
                r"(?<!\w)'t\b",
                r"(?<!\w)'s\b",
            ]
        elif self.lang == "rm-vallader":
            self.protected = [
                r"(?<!\w)'m\b",
                r"(?<!\w)'l\b",
                r"(?<!\w)'ns\b",
                r"(?<!\w)'ls\b",
                r"(?<!\w)'t\b",
                r"(?<!\w)'s\b",
            ]
        else:
            # unk
            self.protected = [
                r"(?<!\w)'ins\b",
                r"(?<!\w)'m\b",
                r"(?<!\w)'l\b",
                r"(?<!\w)'la\b",
                r"(?<!\w)'ns\b",
                r"(?<!\w)'ls\b",
                r"(?<!\w)'las\b",
                r"(?<!\w)'ign\b",
                r"(?<!\w)'gl\b",
                r"(?<!\w)'igl\b",
                r"(?<!\w)'igls\b",
                r"(?<!\w)'t\b",
                r"(?<!\w)'s\b",
            ]

        self.base_tokenizer = MosesTokenizer(lang="it")

    def preprocess_rumgr(self, text):
        """Break up suffixes"""
        text = re.sub(r"([aeiouAEIOU])'ins\b", r"\1 'ins", text)
        return text

    def preprocess_surmiran(self, text):
        """Break up suffixes"""
        text = re.sub(r"([aeiAEI])'m\b", r"\1 'm", text)
        text = re.sub(r"([aeiAEI])'l\b", r"\1 'l", text)
        text = re.sub(r"([aeiAEI])'la\b", r"\1 'la", text)
        text = re.sub(r"([aeiAEI])'ns\b", r"\1 'ns", text)
        text = re.sub(r"([aeiAEI])'ls\b", r"\1 'ls", text)
        text = re.sub(r"([aeiAEI])'las\b", r"\1 'las", text)

        return text

    def preprocess_sursilv(self, text):
        """Break up suffixes"""
        text = re.sub(r"([aeiAEI])'l\b", r"\1 'l", text)
        text = re.sub(r"([aeiAEI])'la\b", r"\1 'la", text)
        text = re.sub(r"([aeiAEI])'las\b", r"\1 'las", text)

        return text

    def preprocess_sutsilv(self, text):
        """Break up suffixes"""
        text = re.sub(r"([aâeiouAÂEIOU])'ign\b", r"\1 'ign", text)
        text = re.sub(r"'gl\b", r" 'gl", text)
        text = re.sub(r"([aâeiouAÂEIOU])'igl\b", r"\1 'igl", text)
        text = re.sub(r"([aâeiouAÂEIOU])'igls\b", r"\1 'igls", text)

        return text

    def preprocess_puter(self, text):
        """Break up suffixes"""
        text = re.sub(r"'m\b", r" 'm", text)
        text = re.sub(r"'l\b", r" 'l", text)
        text = re.sub(r"'la\b", r" 'la", text)
        text = re.sub(r"'ns\b", r" 'ns", text)
        text = re.sub(r"'ls\b", r" 'ls", text)
        text = re.sub(r"'las\b", r" 'las", text)
        text = re.sub(r"'t\b", r" 't", text)
        text = re.sub(r"'s\b", r" 's", text)

        return text

    def preprocess_vallader(self, text):
        """Break up suffixes"""
        text = re.sub(r"'m\b", r" 'm", text)
        text = re.sub(r"'l\b", r" 'l", text)
        text = re.sub(r"'ns\b", r" 'ns", text)
        text = re.sub(r"'ls\b", r" 'ls", text)
        text = re.sub(r"'t\b", r" 't", text)
        text = re.sub(r"'s\b", r" 's", text)

        return text

    def tokenize(self, text):
        """Main function for running tokenization"""
        # normalize apos
        text = re.sub("’", "'", text)
        if self.lang == "rm-rumgr":
            text = self.preprocess_rumgr(text)
        elif self.lang == "rm-surmiran":
            text = self.preprocess_surmiran(text)
        elif self.lang == "rm-sursilv":
            text = self.preprocess_sursilv(text)
        elif self.lang == "rm-sutsilv":
            text = self.preprocess_sutsilv(text)
        elif self.lang == "rm-puter":
            text = self.preprocess_puter(text)
        elif self.lang == "rm-vallader":
            text = self.preprocess_vallader(text)
        else:
            # Idiom unknown; aggressively break apart suffixes and tokenize the result
            text = self.preprocess_rumgr(text)
            text = self.preprocess_surmiran(text)
            text = self.preprocess_sursilv(text)
            text = self.preprocess_sutsilv(text)
            text = self.preprocess_puter(text)
            text = self.preprocess_vallader(text)

        return self.base_tokenizer.tokenize(
            text,
            protected_patterns=self.protected,
            escape=False,
            aggressive_dash_splits=False,
        )
