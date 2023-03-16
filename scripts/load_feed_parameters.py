import os
import json
from pathlib import Path

RISK_PARAMETERS_DIR = Path(os.getcwd()) / 'all_feeds_all_parameters.txt'   

def main():
    with  open(RISK_PARAMETERS_DIR, 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    main()