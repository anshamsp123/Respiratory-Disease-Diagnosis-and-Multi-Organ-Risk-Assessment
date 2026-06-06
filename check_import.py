import sys
import os
# Ensure we are in the right directory
os.chdir(r'c:\updated_DL_CP')
sys.path.append(r'c:\updated_DL_CP')

print(f"Current Path: {sys.path}")
print(f"Files in utils: {os.listdir('utils')}")

try:
    from utils.simulation import generate_risk_timeline_chart, generate_contribution_pie_chart
    print("SUCCESS: Both functions imported correctly.")
except ImportError as e:
    print(f"FAILURE: {e}")
    # Check if the file content matches
    with open('utils/simulation.py', 'r') as f:
        content = f.read()
        print("--- CONTENT OF simulation.py ---")
        print(content)
        print("--- END CONTENT ---")
