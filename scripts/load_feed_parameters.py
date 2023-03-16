import os
import json
from pathlib import Path

RISK_PARAMETERS_DIR = Path(os.getcwd()) / 'scripts/all_feeds_all_parameters.txt'   

def get_parameters():
    with  open(RISK_PARAMETERS_DIR, 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    get_parameters()