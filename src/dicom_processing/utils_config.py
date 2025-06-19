import os

from dotenv import load_dotenv

load_dotenv()

LOGS_PATH = os.getenv('LOGS_PATH')

# Переменные для unzip_manager
ZIPS_PATH = os.getenv('ZIPS_PATH')
UNZIPED_PATH = os.getenv('UNZIPED_PATH')

# Переменные для dicom_anonimizer
PATTERNS_FOR_DICOM_ANONIMIZER = {
    'acquisition',
    'bits',
    'date',
    'time',
    'manufacturer',
    'patient',
    'name',
    'study'
}

CRITICAL_PATTERNS = [
    ("bits", "allocated"),
    ("bits", "stored"),
    ("bits", "high"),
    ("pixel", "representation"),
    ("pixel", "spacing"),
    ("patient", "orientation"),
    ("patient", "position"),
    ("image", "orientation"),
    ("image", "position"),
    ("slice", "thickness"),
    ("slice", "between"),
    ("slice", "spacing"),
]
