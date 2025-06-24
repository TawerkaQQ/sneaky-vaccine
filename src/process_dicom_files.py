import os
import logging

from dicom_processing.dicom_anonimizer import AnonymizerInterface
from dicom_processing.utils_config import LOGS_PATH

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOGS_PATH, 'main.log'),
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    anonimizer = AnonymizerInterface()
    anonimizer.run()
