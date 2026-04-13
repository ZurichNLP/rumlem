from spacy.lang.it.stop_words import STOP_WORDS as IT_STOP
from spacy.lang.ro.stop_words import STOP_WORDS as RO_STOP
from spacy.lang.ca.stop_words import STOP_WORDS as CA_STOP
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP

STOPWORDS = IT_STOP | RO_STOP | CA_STOP | FR_STOP

STRIP_PUNCT = r'[.,!?;:]'

IDIOMS = [
    "rm-rumgr",
    "rm-sursilv",
    "rm-sutsilv",
    "rm-surmiran",
    "rm-puter",
    "rm-vallader"
]

ROM_LANGS = [
    #"roh_Latn",
    "fra_Latn",
    "ita_Latn",
    "ron_Latn",
    "cat_Latn"
]

RTR_BUCKETS = [
    (2, 10),        # title, fragment, query
    (10, 50),       # utterance consisting of one or a few sentences
    (50, 300),      # paragraph
]

BABULINS_BUCKETS = [
    (300, 800),    # short story
    (800, 2000),   # longer story
]

FINEWEB_BUCKETS = [
    (50, 300),     # paragraph
    (300, 800),    # short story
    (800, 2000),   # longer story
]

FILES_ROMANSH_FROM_FINEWEB = {
    "ROMANSH": "paper_eval_code/LangID/Romansh/as_is/eval_analysis_rumantsch.json",
    "ROMANSH (stopwords removed)": "paper_eval_code/LangID/Romansh/stopwords_removed/eval_analysis_rumantsch_stopwords_removed.json",
    "ROMANSH (sets only)": "paper_eval_code/LangID/Romansh/sets_only/eval_analysis_rumantsch_sets_only.json",
    "OTHER": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/as_is/eval_analysis.json",
    "OTHER (stopwords removed)": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/stopwords_removed/eval_analysis_stopwords_removed.json",
    "OTHER (sets only)": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/sets_only/eval_analysis_sets_only.json",
}

FILES_ROMANSH_FROM_RTR_BABULINS = {
    "ROMANSH": "paper_eval_code/VarietyID/as_is/eval_analysis.json",
    "ROMANSH (stopwords removed)": "paper_eval_code/VarietyID/stopwords_removed/eval_analysis_stopwords_removed.json",
    "ROMANSH (sets only)": "paper_eval_code/VarietyID/sets_only/eval_analysis_sets_only.json",
    "OTHER": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/as_is/eval_analysis.json",
    "OTHER (stopwords removed)": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/stopwords_removed/eval_analysis_stopwords_removed.json",
    "OTHER (sets only)": "paper_eval_code/LangID/French_Italian_Catalan_Romanian/sets_only/eval_analysis_sets_only.json",
}

COLORS = {
    "ROMANSH": ("#0f766e", "#5eead4"),
    "ROMANSH (stopwords removed)": ("#115e59", "#99f6e4"),
    "ROMANSH (sets only)": ("#134e4a", "#ccfbf1"),
    "OTHER": ("#9a3412", "#fb923c"),
    "OTHER (stopwords removed)": ("#b45309", "#fdba74"),
    "OTHER (sets only)": ("#c2410c", "#ffedd5"),
}

LINESTYLES = {
    "default": "-",
    "stopwords removed": ":",
    "sets only": "--",
}

# Exclusions for specific files/buckets/score_keys where we want to ignore outlier scores with known issues (annotation errors, etc.) that would distort the plots. 
# Format: {(file, bucket, score_key): {set of scores to exclude}}
EXCLUSIONS = {
    ("paper_eval_code/LangID/Romansh/sets_only/eval_analysis_rumantsch_sets_only.json", "300-800", "winning_score_dist"): {0.56},
    ("paper_eval_code/LangID/Romansh/sets_only/eval_analysis_rumantsch_sets_only.json", "800-2000", "winning_score_dist"): {0.62},
}
