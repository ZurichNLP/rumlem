import subprocess
import sys

scripts = [
    "Coverage/coverage_run_eval.py",
    "VarietyID/varietyID_run_eval.py",
    "LangID/langID_run_eval.py",
    "create_plots.py"
]

for script in scripts:
    print(f"Running {script}...")
    subprocess.run([sys.executable, script], check=True)

print("All scripts finished.")