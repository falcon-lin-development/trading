# settings.py
from pathlib import Path

# Define the base directory relative to the current file
# This assumes the config file is in the top-level directory of your project
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
CONTANT_DIR = BASE_DIR / 'constants'
