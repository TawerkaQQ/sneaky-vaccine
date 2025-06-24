import os
import re
import threading
import shutil
import logging
import pydicom
import uuid

from typing import Tuple, Optional, Any
from tqdm import tqdm
from pydicom.uid import generate_uid
from .utils_config import ZIPS_PATH, UNZIPED_PATH, PATTERNS_FOR_DICOM_ANONYMIZER, LOGS_PATH, CRITICAL_PATTERNS
from .unzip_manager import UnzipManager
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOGS_PATH, 'dicom_anonimizer.log'),
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


class AnonymizerInterface:
    def __init__(self):
        self.anonymizer = Anonymizer()

    def has_archives(self) -> bool:
        return any(file.endswith('.zip') for file in os.listdir(ZIPS_PATH))
    
    def unzip_all(self):
        with UnzipManager(ZIPS_PATH, UNZIPED_PATH) as manager:
            dicom_dirs = manager.get_folder()
        return self

    def get_last_patient_index(self) -> int:
        folders = os.listdir(UNZIPED_PATH)
        indexes = []
        for folder in folders:
            if folder.startswith('patient__'):
                parts = folder.split('_')
                try:
                    indexes.append(int(parts[1]))
                except (IndexError, ValueError):
                    continue
        return max(indexes) if indexes else 0

    def anonimize_patients(self, start_index: int = 1):
        self.anonymizer.anonimize_folders()
        self.anonymizer.anonimize_all_patients(start_index=start_index)
        return self

    def run(self):
        if not self.has_archives():
            logger.info("No archives found. Process terminated.")
            print("No archives found. Process terminated.")
            return

        logger.info("Unzipping archives...")
        print("Unzipping archives...")
        self.unzip_all()

        logger.info("Starting anonymization...")
        print("Starting anonymization...")
        last_index = self.get_last_patient_index() + 1
        self.anonimize_patients(start_index=last_index)

        logger.info("Anonymization process completed.")
        print("Anonymization process completed.")
        

class Anonymizer:
    def __init__(self):
        self.successes = []
        self.failures = []
    
    def is_critical_patterns(self, attr_name: str) -> bool:
        return any(key in attr_name and val in attr_name for key, val in CRITICAL_PATTERNS)
    
    def guess_sex_and_age_from_name(self, name: str) -> Tuple[str, str]:
        name = name.lower()
        sex = "NO_SEX"
        age = "NO_AGE"

        age_match = re.search(r'(\d{2})', name)
        if age_match:
            age = f"{age_match.group(1)}"

        if re.search(r'\b(ж|f)\b', name) or re.search(r'(ж|f)(?=\d|[,;])', name):
            sex = "F"
        elif re.search(r'\b(м|m)\b', name) or re.search(r'(м|m)(?=\d|[,;])', name):
            sex = "M"
        return sex, age
    
    def get_sex_and_age_from_dicom(self, folder_path: str) -> Tuple[Optional[str], Optional[str]]:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.dcm'):
                    dcm_path = os.path.join(root, file)
                    try:
                        dcm = pydicom.dcmread(dcm_path, stop_before_pixels=True)
                        sex = getattr(dcm, "PatientSex", "").strip().upper() or "NO_SEX"
                        age = getattr(dcm, "PatientAge", "").strip().upper() or "NO_AGE"
                        return sex, age
                    except Exception as e:
                        logger.warning(f"Could not read {dcm_path}: {e}")
    
    def repair_dicom(self, dicom_data: Any, dcm_path: str, logger: Any):
        image_orientation = False
        pixel_spacing = False
        spacing_between_slices = False

        if not hasattr(dicom_data, "ImageOrientationPatient") or not dicom_data.ImageOrientationPatient:
            dicom_data.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
            image_orientation = True

        if not hasattr(dicom_data, "PixelSpacing") or dicom_data.PixelSpacing == [0, 0]:
            dicom_data.PixelSpacing = [0.4, 0.4]
            pixel_spacing = True

        if not hasattr(dicom_data, "SpacingBetweenSlices"):
            slice_thickness = getattr(dicom_data, "SliceThickness", 0.32)
            dicom_data.SpacingBetweenSlices = slice_thickness
            spacing_between_slices = True

        if image_orientation:
            logger.info(f"Patched ImageOrientationPatient in: {dcm_path}")
        if pixel_spacing:
            logger.info(f"Patched PixelSpacing in: {dcm_path}")
        if spacing_between_slices:
            logger.info(f"Patched SpacingBetweenSlices in: {dcm_path}")
    
    def anonymize_dicom(self, dicom_data: Any, global_uid: str, anon_patient_id: str):
        attrs = [x for x in dir(dicom_data) if any(p in x.lower() for p in PATTERNS_FOR_DICOM_ANONYMIZER)]

        for attr in attrs:
            if "study" in attr.lower() and "uid" in attr.lower():
                setattr(dicom_data, attr, global_uid)
            elif "patient" in attr.lower() and "id" in attr.lower():
                setattr(dicom_data, attr, anon_patient_id)
            elif self.is_critical_patterns(attr.lower()):
                continue
            else:
                setattr(dicom_data, attr, '')

    def anonimize_all_patients(self, start_index: int = 1):
        patient_folders = sorted([f for f in os.listdir(UNZIPED_PATH) if f.startswith("patient__")])
        to_process = patient_folders[start_index - 1:]
        total = len(to_process)
        lock = threading.Lock()

        logger.info("Starting to anonymize patients...")
        print("Starting to anonymize patients...")

        def task_wrapper(patient):
            try:
                result = self.anonimize_patient(patient)
                with lock:
                    if result:
                        self.successes.append(patient)
                    else:
                        self.failures.append(patient)
            except Exception as e:
                with lock:
                    self.failures.append(patient)
                    logger.error(f"Error in patient anonymization {patient}: {e}")

        with ThreadPoolExecutor() as executor:
            list(tqdm(executor.map(task_wrapper, to_process), total=total, desc='Anonymizing patients', unit='patient'))

        logger.info(f"Successfully: {len(self.successes)} | Errors: {len(self.failures)}")
        print(f"Successfully: {len(self.successes)} | Errors: {len(self.failures)}")
    
    def anonimize_patient(self, patient_folder: str) -> bool:
        global_uid = generate_uid()
        anon_patient_id = f"anon_{uuid.uuid4().hex[:8]}"
        patient_path = os.path.join(UNZIPED_PATH, patient_folder)

        for root, dirs, files in os.walk(patient_path):
            for file in files:
                if file.endswith('.dcm'):
                    dcm_path = os.path.join(root, file)
                    try:
                        dicom_data = pydicom.dcmread(dcm_path)
                        self.repair_dicom(dicom_data, dcm_path, logger)
                        self.anonymize_dicom(dicom_data, global_uid, anon_patient_id)
                        dicom_data.save_as(dcm_path)
                        
                    except Exception as e:
                        logger.warning(f"File with error {dcm_path}: {e}")
                        return False
        return True

    def anonimize_folders(self):
        folders = os.listdir(UNZIPED_PATH)
        non_anon_folders = [f for f in folders if not f.startswith("patient__")]
        existing_patients = [f for f in folders if f.startswith("patient__")]
        
        used_indexes = set()
        for f in existing_patients:
            logger.info(f"Skipping already anonymized patient: {f}")
            print((f"Skipping already anonymized patient: {f}"))
            try:
                idx = int(f.split('__')[1].split('_')[0])
                used_indexes.add(idx)
            except:
                continue

        next_index = max(used_indexes) + 1 if used_indexes else 1

        logger.info(f"Starting to rename folders: {len(non_anon_folders)}...")
        print(f"Starting to rename folders: {len(non_anon_folders)}...")

        for folder in non_anon_folders:
            full_path = os.path.join(UNZIPED_PATH, folder)
            sex, age = self.get_sex_and_age_from_dicom(full_path)

            if not sex or sex == "NO_SEX":
                guessed_sex, guessed_age = self.guess_sex_and_age_from_name(folder)
                if sex == "NO_SEX" and guessed_sex != "NO_SEX":
                    sex = guessed_sex
                if age == "NO_AGE" and guessed_age != "NO_AGE":
                    age = guessed_age

            if not sex:
                sex = "NO_SEX"
            if not age:
                age = "NO_AGE"

            while next_index in used_indexes:
                next_index += 1
            used_indexes.add(next_index)

            new_folder_name = f"patient__{next_index}_{sex}_{age}"
            new_folder_path = os.path.join(UNZIPED_PATH, new_folder_name)

            if not os.path.exists(new_folder_path):
                os.mkdir(new_folder_path)

            logger.info(f"Renaming folder: '{folder}' -> '{new_folder_name}'")
            print(f"Renaming folder: '{folder}' -> '{new_folder_name}'")

            for inner_item in os.listdir(full_path):
                src = os.path.join(full_path, inner_item)
                dst = os.path.join(new_folder_path, inner_item)
                try:
                    shutil.move(src, dst)
                except Exception as e:
                    logger.warning(f"Failed to move {src} to {dst}: {e}")
                    print(f"Failed to move {src} to {dst}: {e}")

            try:
                os.rmdir(full_path)
            except Exception as e:
                logger.warning(f"Could not remove folder {full_path}: {e}")
                print(f"Could not remove folder {full_path}: {e}")

            next_index += 1

        logger.info("Folders renamed successfully!")
        print("Folders renamed successfully!")

