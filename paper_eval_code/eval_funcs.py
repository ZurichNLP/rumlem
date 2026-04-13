from collections import Counter, defaultdict
from romansh_lemmatizer import Lemmatizer, tokenizer
import nltk
import ds_loaders
import config
from config import IDIOMS, STRIP_PUNCT
import json
from tqdm import tqdm
from utils import _remove_stopwords, _safe_ratio
import re

def build_length_buckets(source, langs=IDIOMS, print_summaries=True, streaming=False, limit=None):
    BUCKETS = getattr(config, f"{source.upper()}_BUCKETS")
    loading_func = getattr(ds_loaders, f"load_{source}")

    MIN_BUCKET = min(lo for lo, _ in BUCKETS)
    MAX_BUCKET = max(hi for _, hi in BUCKETS)

    def bucket_for_len(n: int):
        if n < MIN_BUCKET or n >= MAX_BUCKET:
            return None
        for lo, hi in BUCKETS:
            if lo <= n < hi:
                return f"{lo}-{hi}"
        return None

    sample_counts = {}
    token_totals = {}
    examples = {}
    bucket_datasets = {}  # <- what we return

    MAX_EXAMPLES = 3

    for idiom in langs:
        if print_summaries:
            print(f"\n=== {idiom} ===")

        # --- load dataset ---
        ds = loading_func(idiom) if source != "fineweb" else loading_func(idiom, streaming, limit)

        # annotate
        def annotate(example):
            tokens = nltk.word_tokenize(example.get("sentence"))
            n = len(tokens)
            return {"len": n, "bucket": bucket_for_len(n)}

        if "sentence" not in ds.column_names:
            ds = ds.rename_column("text", "sentence")
        ds = ds.map(annotate)

        # --- collect datasets per bucket ---
        idiom_bucket_sets = {}
        for lo, hi in BUCKETS:
            label = f"{lo}-{hi}"
            bucket_ds = ds.filter(lambda x: x["bucket"] == label)
            if streaming:
                bucket_ds = list(bucket_ds)  # convert this bucket to a list for fast iteration
            idiom_bucket_sets[label] = bucket_ds
        bucket_datasets[idiom] = idiom_bucket_sets

        # --- examples ---
        bucket_examples = defaultdict(list)
        for sample in ds:
            sent = sample["sentence"]
            b = sample["bucket"]
            if b is None:
                continue
            if len(bucket_examples[b]) < MAX_EXAMPLES:
                bucket_examples[b].append(sent)
        examples[idiom] = bucket_examples

        # --- stats ---
        count_counter = Counter()
        token_counter = Counter()

        for sample in ds:
            n = sample["len"]
            b = sample["bucket"]
            if b is None:
                continue
            count_counter[b] += 1
            token_counter[b] += n

        sample_counts[idiom] = count_counter
        token_totals[idiom] = token_counter

        if print_summaries:
            for lo, hi in BUCKETS:
                label = f"{lo}-{hi}"
                c = count_counter.get(label, 0)
                t = token_counter.get(label, 0)
                avg = (t / c) if c > 0 else 0
                print(f"{label}: {c} samples | {t} tokens | avg={avg:.1f}")

    # -------- summary printing --------
    if print_summaries:

        print("\n\n=== SAMPLE COUNTS ===")
        header = ["idiom"] + [f"{lo}-{hi}" for lo, hi in BUCKETS]
        print("\t".join(header))
        for idiom in langs:
            row = [idiom] + [
                str(sample_counts[idiom].get(f"{lo}-{hi}", 0)) for lo, hi in BUCKETS
            ]
            print("\t".join(row))

        print("\n\n=== TOKEN TOTALS ===")
        print("\t".join(header))
        for idiom in langs:
            row = [idiom] + [
                str(token_totals[idiom].get(f"{lo}-{hi}", 0)) for lo, hi in BUCKETS
            ]
            print("\t".join(row))

        print("\n\n=== EXAMPLES PER BUCKET ===")
        for idiom in langs:
            print(f"\n######## {idiom} ########")
            for lo, hi in BUCKETS:
                label = f"{lo}-{hi}"
                print(f"\n--- {label} ---")
                for s in examples[idiom].get(label, []):
                    print(s)
                    print("---")

    return bucket_datasets

def evaluate_buckets(source, buckets, langs=IDIOMS, remove_stopwords=False, sets_only=False):
    BUCKETS = getattr(config, f"{source.upper()}_BUCKETS")

    results = {idiom: {f"{lo}-{hi}": {} for lo, hi in BUCKETS} for idiom in langs}
    analysis = {
        idiom: {f"{lo}-{hi}": {"total": 0, "correct": 0} for lo, hi in BUCKETS}
        for idiom in langs
    }

    lemmatizer = Lemmatizer()
    # iterate over buckets and print some examples
    for idiom, idiom_buckets in buckets.items():
        print(f"\n=== {idiom} ===")
        for bucket_key, ds in idiom_buckets.items():
            print(f"\n--- Bucket {bucket_key} ---")
            # use the lemmatizer to classify each sentence in the bucket
            for idx, sample in enumerate(tqdm(ds, desc=f"{idiom}-{bucket_key}")):
                actual_idiom = idiom
                sent = sample["sentence"]
                #sent = re.sub(STRIP_PUNCT, '', sent)
                if sets_only:
                    sent = " ".join(list(set(tokenizer.Rm_Tokenizer("unk").tokenize(sent))))
                if remove_stopwords:
                    sent = " ".join(_remove_stopwords(sent))

                doc = lemmatizer(sent)
                scores = doc.idiom_scores.items()
                # make sure these keys exist
                results[idiom][bucket_key][idx] = {
                    "actual_idiom": actual_idiom,
                    "scores": {idiom.value: score for idiom, score in scores},
                    "winning_score": max(score for idiom, score in scores),
                    "avg_score": sum(score for idiom, score in scores) / len(scores),
                    "sentence": sent,
                }

    # --- analysis ---
    for idiom in langs:
        for bucket_key in results[idiom]:
            # for each bucket, store A), the lowest winning score, and B), the lowest avg score
            lowest_winning_score = min(
                res["winning_score"] for res in results[idiom][bucket_key].values()
            )
            lowest_avg_score = min(
                res["avg_score"] for res in results[idiom][bucket_key].values()
            )
            analysis[idiom][bucket_key]["lowest_winning_score"] = round(lowest_winning_score, 2)
            analysis[idiom][bucket_key]["lowest_avg_score"] = round(lowest_avg_score, 2)
            # also compute the distribution of these two values as dictionaries mapping score to count; round them to two decimal places for readability
            winning_score_dist = Counter(
                round(res["winning_score"], 2)
                for res in results[idiom][bucket_key].values()
            )
            avg_score_dist = Counter(
                round(res["avg_score"], 2)
                for res in results[idiom][bucket_key].values()
            )
            analysis[idiom][bucket_key]["winning_score_dist"] = dict(winning_score_dist)
            analysis[idiom][bucket_key]["avg_score_dist"] = dict(avg_score_dist)

            for idx, res in results[idiom][bucket_key].items():
                actual_idiom = res["actual_idiom"]
                scores = res["scores"]
                winning_idioms = [
                    cand_idiom
                    for cand_idiom, score in scores.items()
                    if score == res["winning_score"]
                ]
                if actual_idiom in winning_idioms:
                    analysis[idiom][bucket_key]["correct"] += 1
                analysis[idiom][bucket_key]["total"] += 1

    return results, analysis

def evaluate_buckets_coverage(source, buckets, langs=IDIOMS, edittrees=False):
    def _has_info(morph, translation):
        morph_info = False
        for m in morph:
            if m is None:
                continue
            if getattr(m, "features", None):
                morph_info = True
                break
        trans_info = translation not in (None, "null", "n/v", "N/V", "n/a", "N/A")
        return morph_info or trans_info

    BUCKETS = getattr(config, f"{source.upper()}_BUCKETS")

    results = {idiom: {f"{lo}-{hi}": {} for lo, hi in BUCKETS} for idiom in langs}
    analysis = {
        idiom: {f"{lo}-{hi}": {"total_tokens": 0, "lemmatized_tokens": 0} for lo, hi in BUCKETS}
        for idiom in langs
    }

    if edittrees:
        lemmatizer = Lemmatizer(learned_et=True)
    else:
        lemmatizer = Lemmatizer()
    # iterate over buckets and print some examples
    for idiom, idiom_buckets in buckets.items():
        print(f"\n=== {idiom} ===")
        for bucket_key, ds in idiom_buckets.items():
            print(f"\n--- Bucket {bucket_key} ---")
            # use the lemmatizer to classify each sentence in the bucket
            for idx, sample in enumerate(tqdm(ds, desc=f"{idiom}-{bucket_key}")):
                sent = sample["sentence"]
                sent = re.sub(STRIP_PUNCT, '', sent)
                doc = lemmatizer(sent)
                total_lemmatized = 0
                tokens_no_lemma = []
                for tok in doc.tokens:
                    if not tok.lemmas:
                        tokens_no_lemma.append(tok.text)
                    if tok.lemmas:
                        # check whether has morph or has trans
                        if any(_has_info(morph, l.translation_de) for l, morph in tok.lemmas.items()):
                            total_lemmatized += 1
                        else:
                            tokens_no_lemma.append(tok.text)
 
                total_tokens = len(doc.tokens)
                assert total_lemmatized == total_tokens - len(tokens_no_lemma), "something went wrong counting lemmatizable and non-lemmatizable forms"

                results[idiom][bucket_key][idx] = {
                    "total_tokens": total_tokens,
                    "total_lemmatized": total_lemmatized,
                    "tokens_without_lemma": tokens_no_lemma,
                    "coverage": total_lemmatized/total_tokens,
                }

    # --- analysis ---
    for idiom in langs:
        for bucket_key in results[idiom]:
            # for each bucket, store A), the lowest coverage score
            lowest_coverage = min(
                res["coverage"] for res in results[idiom][bucket_key].values()
            )
            analysis[idiom][bucket_key]["lowest_coverage"] = lowest_coverage

            coverage_list = sorted(
                res["coverage"]
                for res in results[idiom][bucket_key].values()
            )
            total_tokens_overall = sum(
                res["total_tokens"]
                for res in results[idiom][bucket_key].values()
            )
            total_lemmatized_overall = sum(
                res["total_lemmatized"]
                for res in results[idiom][bucket_key].values()
            )
            analysis[idiom][bucket_key]["total_tokens"] = total_tokens_overall
            analysis[idiom][bucket_key]["lemmatized_tokens"] = total_lemmatized_overall
            analysis[idiom][bucket_key]["overall_coverage"] = round(total_lemmatized_overall/total_tokens_overall, 2)
            analysis[idiom][bucket_key]["avg_coverage"] = round(sum(coverage_list)/len(coverage_list), 2)
            analysis[idiom][bucket_key]["all_coverages"] = coverage_list

    return results, analysis

def enrich_analysis(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lang_totals = {}
    bucket_totals_acc = defaultdict(lambda: {"total": 0, "correct": 0})

    for lang, buckets in data.items():
        # skip summary sections if re-running
        if lang.startswith("_"):
            continue

        lang_total = 0
        lang_correct = 0

        for bucket_name, stats in buckets.items():
            total = int(stats.get("total", 0))
            correct = int(stats.get("correct", 0))

            # A) add ratio to each bucket
            stats["ratio"] = _safe_ratio(correct, total)

            # NEW: compute highest winning & average scores
            winning_dist = stats.get("winning_score_dist", {})
            avg_dist = stats.get("avg_score_dist", {})

            if winning_dist:
                stats["highest_winning_score"] = max(
                    float(score) for score in winning_dist.keys()
                )
            else:
                stats["highest_winning_score"] = 0.0

            if avg_dist:
                stats["highest_avg_score"] = max(
                    float(score) for score in avg_dist.keys()
                )
            else:
                stats["highest_avg_score"] = 0.0

            lang_total += total
            lang_correct += correct

            bucket_totals_acc[bucket_name]["total"] += total
            bucket_totals_acc[bucket_name]["correct"] += correct

        # B) totals per language
        lang_totals[lang] = {
            "total": lang_total,
            "correct": lang_correct,
            "ratio": _safe_ratio(lang_correct, lang_total),
        }

    # C) totals per bucket
    bucket_totals = {}
    for bucket, agg in bucket_totals_acc.items():
        bucket_totals[bucket] = {
            "total": agg["total"],
            "correct": agg["correct"],
            "ratio": _safe_ratio(agg["correct"], agg["total"]),
        }

    # attach summaries
    data["_language_totals"] = lang_totals
    data["_bucket_totals"] = bucket_totals

    # overwrite file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def enrich_coverage_analysis(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lang_totals = {}
    bucket_totals_acc = defaultdict(lambda: {"total": 0, "lemmatized": 0})

    for lang, buckets in data.items():
        # skip summary sections if re-running
        if lang.startswith("_"):
            continue

        lang_total = 0
        lang_lemmatized = 0

        for bucket_name, stats in buckets.items():
            total = int(stats.get("total_tokens", 0))
            lemmatized = int(stats.get("lemmatized_tokens", 0))

            lang_total += total
            lang_lemmatized += lemmatized

            bucket_totals_acc[bucket_name]["total"] += total
            bucket_totals_acc[bucket_name]["lemmatized"] += lemmatized

        # B) totals per language
        lang_totals[lang] = {
            "total": lang_total,
            "lemmatized": lang_lemmatized,
            "ratio": _safe_ratio(lang_lemmatized, lang_total),
        }

    # C) totals per bucket
    bucket_totals = {}
    for bucket, agg in bucket_totals_acc.items():
        bucket_totals[bucket] = {
            "total": agg["total"],
            "lemmatized": agg["lemmatized"],
            "ratio": _safe_ratio(agg["lemmatized"], agg["total"]),
        }

    # attach summaries
    data["_language_totals"] = lang_totals
    data["_bucket_totals"] = bucket_totals

    # overwrite file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
