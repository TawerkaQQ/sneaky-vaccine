import os
import logging

from dicom_processing.dicom_anonimizer import IAnonimizer
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
    try:
        anonimizer = IAnonimizer()
        if anonimizer.has_archives():
            logger.info("Archives found. Starting unzipping...")
            print("Archives found. Starting unzipping...")
            anonimizer.unzip_all()
        else:
            logger.info("No archives found. Starting anonymization...")
            print(("No archives found. Starting anonymization..."))

        last_patient_index = anonimizer.get_last_patient_index()
        anonimizer.anonimize_patients(start_index=last_patient_index + 1)

        logger.info("Anonymization completed successfully.")
        print("Anonymization completed successfully.")

    except Exception as e:
        logger.error(f"Error while executing: {e}")
        print(f"Error while executing: {e}")