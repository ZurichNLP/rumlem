import json
import numpy as np
import os
import matplotlib.pyplot as plt
from config import FILES_ROMANSH_FROM_FINEWEB, FILES_ROMANSH_FROM_RTR_BABULINS, COLORS, LINESTYLES, EXCLUSIONS

def load_all_scores(path, bucket, score_key):
    scores = []
    label=path
    excluded = EXCLUSIONS.get((label, bucket, score_key), set()) if label else set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for lang, buckets in data.items():
            if lang.startswith("_"):
                continue
            if bucket not in buckets:
                continue
            dist = buckets[bucket].get(score_key, {})
            for score_str, count in dist.items():
                score = float(score_str)
                if score in excluded:
                    print(f"\t[Exclusion] Skipping score {score} for label='{label}', bucket='{bucket}', key='{score_key}'")
                    continue
                scores.extend([score] * int(count))
    except FileNotFoundError:
        print(f"Skipping missing file: {path}")
    return scores

def find_best_threshold_with_margin(positives, negatives):
    positives = np.sort(np.array(positives))
    negatives = np.sort(np.array(negatives))

    all_scores = np.sort(np.unique(np.concatenate([positives, negatives])))

    best_thresh = all_scores[0]
    best_fn = best_fp = 0
    best_score = -1
    best_margin = -np.inf

    for i in range(len(all_scores) - 1):
        t = (all_scores[i] + all_scores[i + 1]) / 2

        fn = np.searchsorted(positives, t, side="left")
        fp = len(negatives) - np.searchsorted(negatives, t, side="left")
        correct = len(positives) - fn - fp

        # compute margin (distance from closest positive above to closest negative below)
        pos_above = positives[positives >= t]
        neg_below = negatives[negatives < t]
        if len(pos_above) > 0 and len(neg_below) > 0:
            margin = pos_above.min() - neg_below.max()
        else:
            margin = 0  # no margin if one side empty

        # pick threshold: maximize correct, break ties with margin
        if (correct > best_score) or (correct == best_score and margin > best_margin):
            best_score = correct
            best_thresh = t
            best_fn = fn
            best_fp = fp
            best_margin = margin

    return best_thresh, best_fn, best_fp, best_margin

def main(files):
    plt.figure(figsize=(8, 5))
    FILES = files
    idiomid_scores = load_all_scores(FILES["ROMANSH"], BUCKET, SCORE_KEY)
    if not idiomid_scores:
        print("No ROMANSH scores found.")
        return

    # Plot histograms
    for label, path in FILES.items():
        scores = load_all_scores(path, BUCKET, SCORE_KEY)
        if not scores:
            continue

        if "stopwords removed" in label:
            style_key = "stopwords removed"
        elif "sets only" in label:
            style_key = "sets only"
        else:
            style_key = "default"

        linestyle = LINESTYLES[style_key]
        edge_color, fill_color = COLORS.get(label, ("black", "#dddddd"))

        plt.hist(
            scores,
            bins=40,
            density=True,
            histtype="stepfilled",
            edgecolor=edge_color,
            facecolor=fill_color,
            linestyle=linestyle,
            linewidth=1.8,
            alpha=0.6,
            label=label,
        )

    # Compute best threshold per LangID variant
    results = []

    for label, path in FILES.items():
        if not label.startswith("OTHER"):
            continue

        if "stopwords removed" in label:
            idiom_label = "ROMANSH (stopwords removed)"
        elif "sets only" in label:
            idiom_label = "ROMANSH (sets only)"
        else:
            idiom_label = "ROMANSH"

        positives = load_all_scores(FILES[idiom_label], BUCKET, SCORE_KEY)
        negatives = load_all_scores(FILES[label], BUCKET, SCORE_KEY)

        if not positives or not negatives:
            continue

        thresh, fn, fp, margin = find_best_threshold_with_margin(positives, negatives)
        results.append({
            "method": idiom_label,
            "threshold": thresh,
            "fn": fn,
            "fp": fp,
            "margin": margin,
            "total_correct": len(positives) - fn - fp,
            "negatives_len": len(negatives),
            "positives": positives,
            "negatives": negatives,
        })

        print(f"{idiom_label}: threshold={thresh:.3f}, margin={margin:.3f}, "
              f"fn={fn}, fp={fp}, correct={len(positives)-fn-fp}")

    # Pick overall best: widest margin among perfect separation, else max correct
    best_result = None
    for r in results:
        if r["fn"] == 0 and r["fp"] == 0:
            if best_result is None or r["margin"] > best_result["margin"]:
                best_result = r

    if best_result is None:
        # no perfect separation, fallback to max correct
        best_result = max(results, key=lambda r: r["total_correct"])

    # Overlay best threshold (existing)
    plt.axvline(
        best_result["threshold"],
        color="black",
        linestyle="--",
        linewidth=2,
        label=f"Best threshold: {best_result['method']} = {best_result['threshold']:.3f},\nmisclassified: {best_result['fn'] + best_result['fp']} out of {len(idiomid_scores) + best_result['negatives_len']}",
    )

    # Update legend to show "— Minimum" / "— Maximum" for best method
    handles, labels = plt.gca().get_legend_handles_labels()
    new_labels = []

    # Determine style_key and corresponding OTHER label
    if "stopwords removed" in best_result["method"]:
        style_key = "stopwords removed"
    elif "sets only" in best_result["method"]:
        style_key = "sets only"
    else:
        style_key = "default"
    other_label = "OTHER" if style_key == "default" else f"OTHER ({style_key})"

    # Update legend to show only variant (stopwords removed / sets only)
    handles, labels = plt.gca().get_legend_handles_labels()
    new_labels = []

    # Extract variant name from label (remove 'ROMANSH' or 'OTHER')
    def get_variant(lbl):
        for base in ["ROMANSH", "OTHER"]:
            if lbl.startswith(base) and lbl != base:
                variant = lbl.replace(base, "").strip()
                if variant.startswith("(") and variant.endswith(")"):
                    return variant[1:-1]  # remove parentheses
                else:
                    return variant
        return lbl  # default if no match

    new_labels = []

    for lbl in labels:
        # Special threshold lines
        if lbl == best_result["method"]:
            new_labels.append(f"{get_variant(lbl)} [lowest score indicated]")
        elif lbl == other_label:
            new_labels.append(f"{get_variant(lbl)} [highest score indicated]")
        else:
            # General case: just show variant name
            new_labels.append(get_variant(lbl))

    # Lowest ROMANSH (positive) sample – best method color
    plt.axvline(
        min(best_result["positives"]),
        color=COLORS[best_result["method"]][0],  # edge color of best method
        linestyle=linestyle,
        linewidth=1.5,
        alpha=0.8
    )

    # Highest OTHER (negative) sample – matching OTHER color for this variant
    other_label = "OTHER" if style_key == "default" else f"OTHER ({style_key})"
    plt.axvline(
        max(best_result["negatives"]),
        color=COLORS[other_label][0],  # edge color of OTHER variant
        linestyle=linestyle,
        linewidth=1.5,
        alpha=0.8
    )

    # Probability y-axis
    title_key = SCORE_KEY.split("_")
    title_key = [t.capitalize() for t in title_key]
    title_key = " ".join(title_key).replace("Dist", "Distributions")
    plt.title(f"{title_key} (Bucket {BUCKET})", fontsize=16)
    plt.xlabel("Score", fontsize=16)
    plt.ylabel("Density", fontsize=16)
    plt.tick_params(axis='both', labelsize=16)
    plt.legend(handles, new_labels, fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    save_path_subfolder = "fineweb" if FILES == FILES_ROMANSH_FROM_FINEWEB else "RTR_Babulins"
    save_dir = os.path.join("paper_eval_code", "plots", save_path_subfolder, SCORE_KEY)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{BUCKET}.png")
    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")
    #plt.show()

    # Print best threshold info
    print(f"\nOverall best separating threshold: {best_result['threshold']:.3f} "
          f"(method: {best_result['method']})")
    print(f"False negatives (ROMANSH < threshold): {best_result['fn']} / {len(idiomid_scores)}")
    print(f"False positives (OTHER >= threshold): {best_result['fp']} / {best_result['negatives_len']}")
    print(f"Margin: {best_result['margin']:.3f}\n---\n")

if __name__ == "__main__":
    
    files_list = [FILES_ROMANSH_FROM_RTR_BABULINS, FILES_ROMANSH_FROM_FINEWEB]
    for files in files_list:
        for sc_key in ["winning_score_dist", "avg_score_dist"]:
            for bucket in ["50-300", "300-800", "800-2000"]:
                BUCKET = bucket
                SCORE_KEY = sc_key
                main(files)
