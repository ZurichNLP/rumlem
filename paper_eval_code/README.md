# Lemmatizer Evaluation: Experimental Code and Results

This folder contains the experimental code and results reported in the paper **RUMLEM: A Dictionary-Based Lemmatizer for Romansh** (Dominic P. Fischer, Zachary Hopton, Jannis Vamvas).

Each experimental approach under Coverage, Variety and Language Identification results in two separate files: a _results_ file and an _analysis_ file, summarizing the results. Note that for Coverage, there is just one approach, while for the identification experiments, there are three in each: as-is, sets of words and stopwords removed.

The file "pipeline_all_evals.py" reruns the plot creation based on the existing results. In case you would like to rerun all experiments, uncomment the lines that are currently commented out. Note that doing so will:

A) overwrite the existing results

B) lead to different results, as the _Babulins_ dataset is not openly available and will thus be skipped when rerunning experiments
