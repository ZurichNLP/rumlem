import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from eval_funcs import build_length_buckets, evaluate_buckets, enrich_analysis
from config import ROM_LANGS

def run_eval(suffix="", remove_stopwords=False, sets_only=False, langs=ROM_LANGS):
    if suffix != "":
        suffix = f"_{suffix}"
    source = "fineweb"

    combined_results = {}
    combined_analysis = {}

    buckets = build_length_buckets(source, langs, streaming=True, limit=5000, print_summaries=False)
    results, analysis = evaluate_buckets(source, buckets, langs, remove_stopwords, sets_only)

    for idiom, idiom_results in results.items():
        combined_results.setdefault(idiom, {}).update(idiom_results)

    for idiom, idiom_analysis in analysis.items():
        combined_analysis.setdefault(idiom, {}).update(idiom_analysis)

    with open(f"LangID/eval_results{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)

    with open(f"LangID/eval_analysis{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_analysis, f, indent=2, ensure_ascii=False)

    enrich_analysis(f"LangID/eval_analysis{suffix}.json")


if __name__ == "__main__":
    # run with stopwords removed
    run_eval("stopwords_removed", remove_stopwords=True, sets_only=False)
    # run with the SETS of tokens of each sentence
    #run_eval("sets_only", False, True)
    
    # run rumantsch only
    run_eval("rumantsch", langs=["roh_Latn"])
    run_eval("rumantsch_sets_only", remove_stopwords=False, sets_only=True, langs=["roh_Latn"])
    run_eval("rumantsch_stopwords_removed", remove_stopwords=True, sets_only=False, langs=["roh_Latn"])
