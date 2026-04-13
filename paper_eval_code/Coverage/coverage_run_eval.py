import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from eval_funcs import build_length_buckets, evaluate_buckets_coverage, enrich_coverage_analysis
from config import IDIOMS

def run_eval(langs=IDIOMS, suffix=""):
    edittrees = False
    if suffix != "":
        suffix = f"_{suffix}"
        edittrees = True if suffix == "_edittrees" else False
    #sources = ["rtr", "babulins"]
    sources = ["rtr"] # babulins is not openly available

    combined_results = {}
    combined_analysis = {}

    for source in sources:
        buckets = build_length_buckets(source, langs, print_summaries=False)
        results, analysis = evaluate_buckets_coverage(source, buckets, langs, edittrees=edittrees)

        for idiom, idiom_results in results.items():
            combined_results.setdefault(idiom, {}).update(idiom_results)

        for idiom, idiom_analysis in analysis.items():
            combined_analysis.setdefault(idiom, {}).update(idiom_analysis)

    with open(f"Coverage/eval_results{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2, ensure_ascii=False)

    with open(f"Coverage/eval_analysis{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(combined_analysis, f, indent=2, ensure_ascii=False)

    enrich_coverage_analysis(f"Coverage/eval_analysis{suffix}.json")

if __name__ == "__main__":
    run_eval()
    
    # Coverage with activated ML-component to map unknown forms to a lemma (i.e., the Edit Trees) was not part of the eval in the paper
    #run_eval("edittrees")