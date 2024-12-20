import os
import zipfile
import pydicom
import logging

from utils.dicom_anonimizer import IAnonimizer
from utils.unzip_manager import UnzipManager
from utils.dicom_anonimizer import Anonimizer
from utils.utils_config import LOGS_PATH

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOGS_PATH, 'main.log'),
    filemode='a',
)
logger = logging.getLogger(__name__)

def unzip_patients(anonimizer_i):
    """
    Распаковать архивы
    """
    anonimizer_i.unzip_all()
    anonimizer_i.anonimize_folders()

def anonimize_patients(anonimizer_i):
    """
    Анонимизировать все dicom
    """
    anonimizer_i.anonimize_patients()

if __name__ == "__main__":
    anonimizer = IAnonimizer()
    unzip_patients(anonimizer)
    anonimize_patients(anonimizer)
