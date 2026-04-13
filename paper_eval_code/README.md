# Lemmatizer Evaluation: Experimental Code and Results

This folder contains the experimental code and results report in the paper **RUMLEM: A Dictionary-Based Lemmatizer for Romansh** (Dominic P. Fischer, Zachary Hopton, Jannis Vamvas). 

For Variety and Language Identification, each of the experimental three setups (as-is, sets of words and stopwords removed) results in two separate files; a *results* file and an *analysis* file that summarizes the results.

The file "pipeline_all_evals.py" reruns the plot creation based on the existing results. In case you would like to rerun all results, uncomment the lines that are currently commented out. Note that doing so will:

A) overwrite the existing results
B) lead to different results, as the *Babulins* dataset is not openly available and will thus be skipped when reproducing results