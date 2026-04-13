import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from eval_funcs import build_length_buckets, evaluate_buckets, enrich_analysis
from config import IDIOMS

def run_eval(suffix="", remove_stopwords=False, sets_only=False, langs=IDIOMS):
    if suffix != "":
        suffix = f"_{suffix}"
        suffix_folder = suffix
    else:
        suffix_folder = "as_is"

    #sources = ["rtr", "babulins"]
    sources = ["rtr"] # babulins is not openly available

    combined_results = {}
    combined_analysis = {}

    for source in sources:
        buckets = build_length_buckets(source, langs, print_summaries=False)
        results, analysis = evaluate_buckets(source, buckets, langs, remove_stopwords, sets_only)

        for idiom, idiom_results in results.items():
            combined_results.setdefault(idiom, {}).update(idiom_results)

        for idiom, idiom_analysis in analysis.items():
            combined_analysis.setdefault(idiom, {}).update(idiom_analysis)

    with open(f"IdiomID/{suffix_folder}/eval_results{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)

    with open(f"IdiomID/{suffix_folder}/eval_analysis{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_analysis, f, indent=2, ensure_ascii=False)

    enrich_analysis(f"IdiomID/{suffix_folder}/eval_analysis{suffix}.json")

if __name__ == "__main__":
    run_eval()
    run_eval("stopwords_removed", remove_stopwords=True, sets_only=False)
    run_eval("sets_only", remove_stopwords=False, sets_only=True)