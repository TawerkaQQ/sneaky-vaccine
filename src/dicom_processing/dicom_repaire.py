import pydicom
import logging
import os

from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

def setup_logging():
    log_file_path = os.path.join("tests", "dicom_repaire.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(message)s')
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def load_env_path():
    load_dotenv()
    dicom_path = os.getenv("DICOM_ROOT_PATH")
    if dicom_path is None:
        raise ValueError("DICOM_ROOT_PATH не найден в .env файле.")
    return dicom_path

class DicomRepairProcessor:
    def __init__(self):
        self.logger = logging.getLogger("DicomProcessor")

    def fix_dicom_geometry(self, dicom_path: str) -> bool:
        """Correction of geometric attributes in one DICOM file"""
        ds = pydicom.dcmread(dicom_path)
        changed = False

        if not hasattr(ds, "ImageOrientationPatient") or not ds.ImageOrientationPatient:
            ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
            self.logger.info(f"Patched ImageOrientationPatient in: {dicom_path}")
            changed = True

        if not hasattr(ds, "PixelSpacing") or ds.PixelSpacing == [0, 0]:
            ds.PixelSpacing = [0.4, 0.4]
            self.logger.info(f"Patched PixelSpacing in: {dicom_path}")
            changed = True

        if not hasattr(ds, "SpacingBetweenSlices"):
            slice_thickness = getattr(ds, "SliceThickness", 0.32)
            ds.SpacingBetweenSlices = slice_thickness
            self.logger.info(f"Patched SpacingBetweenSlices in: {dicom_path}")
            changed = True

        if changed:
            ds.save_as(dicom_path)

        return changed
