import subprocess
import sys
from pathlib import Path

# Root of the project (one level up from this script)
project_root = Path(__file__).parent.parent
print(project_root)

scripts = [
    #"paper_eval_code/Coverage/coverage_run_eval.py",
    #"paper_eval_code/Coverage/uncovered_tokens_analysis/analyse_uncovered_tokens.py"
    #"paper_eval_code/VarietyID/varietyID_run_eval.py",
    #"paper_eval_code/LangID/langID_run_eval.py",
    "paper_eval_code/create_plots.py"
]

for script in scripts:
    print(f"Running {script}...")
    subprocess.run([sys.executable, script], check=True)

print("All scripts finished.")