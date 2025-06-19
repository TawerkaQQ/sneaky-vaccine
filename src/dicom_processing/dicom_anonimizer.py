import os
import pydicom
import zipfile
import shutil
import logging
import uuid

from pydicom.uid import generate_uid
from .utils_config import ZIPS_PATH, UNZIPED_PATH, PATTERNS_FOR_DICOM_ANONIMIZER, LOGS_PATH, CRITICAL_PATTERNS
from .unzip_manager import UnzipManager

# logging.basicConfig(
#     level=logging.INFO,
#     filename=os.path.join(LOGS_PATH, 'dicom_anonimizer.log'),
#     filemode='w',
# )
# logger = logging.getLogger(__name__)

class IAnonimizer:
    def __init__(self):
        self.anonimizer = Anonimizer()

    def anonimize_patients(self):
        """
        Метод анонимизирует все dicom всех patient в директории UNZIPED_PATH
        """
        self.anonimizer.anonimize_all_patients()

    def unzip_all(self):
        """
        Метод распаковывает архивы из ZIPS_PATH в UNZIPED_PATH
        """
        with UnzipManager(ZIPS_PATH, UNZIPED_PATH) as manager:
            dicom_dirs = manager.get_folder()
        return self

    def anonimize_folders(self):
        """
        Метод анонимизирует названия директорий patient
        """
        self.anonimizer.anonimize_folders()
        return self


class Anonimizer:
    @staticmethod
    def is_critical_patterns(attr_name):
        return any(key in attr_name and val in attr_name for key, val in CRITICAL_PATTERNS)

    def anonimize_all_patients(self):
        patients_folders = os.listdir(UNZIPED_PATH)
        for patient_folder in patients_folders:
            self.anonimize_patient(patient_folder)
        return self

    def anonimize_patient(self, patient_folder):
        global_uid = generate_uid()
        anon_patient_id = f"annon_{uuid.uuid4().hex[:8]}"
        for root, dirs, files in os.walk(top=UNZIPED_PATH):
            for file in files:
                if file.endswith('.dcm'):
                    current_dicom_path = os.path.join(root, file)
                    current_dicom_data = pydicom.dcmread(current_dicom_path)
                    attrs_to_anon = [x for x in dir(current_dicom_data) if any(pattern in x.lower() for pattern in PATTERNS_FOR_DICOM_ANONIMIZER)]
                    for attr in attrs_to_anon:
                        if "study" in attr.lower() and "uid" in attr.lower():
                            setattr(current_dicom_data, attr, global_uid)
                            continue
                        elif "patient" in attr.lower() and "id" in attr.lower():
                            setattr(current_dicom_data, attr, anon_patient_id)
                            continue
                        elif self.is_critical_patterns(attr.lower()):
                            continue
                        else:
                            setattr(current_dicom_data, attr, '')

                    current_dicom_data.save_as(current_dicom_path)
        return self

    def anonimize_folders(self):
        folders = [x for x in os.listdir(UNZIPED_PATH)]
        patient_folders = [f'patient__{x}' for x in range(1, len(folders) + 1)]
        for x, y in zip(folders, patient_folders):
            for root, dirs, files in os.walk(top=UNZIPED_PATH):
                for file in files:
                    if file.endswith('.dcm'):
                        current_dicom_path = os.path.join(root, file)
                        current_dicom_data = pydicom.dcmread(current_dicom_path)
                        sex_attribute_found = False
                        age_attribute_found = False
                        for attr in dir(current_dicom_data):
                            if 'Sex' in attr:
                                if getattr(current_dicom_data, attr) != '':
                                    sex_attribute_found = True
                                    sex_attribute = getattr(current_dicom_data, attr)
                                    # logger.info(sex_attribute)
                                    # logger.info(type(sex_attribute))
                                    # logger.info(len(sex_attribute))
                            if attr.endswith('Age') or attr.startswith('Age'):
                                if getattr(current_dicom_data, attr) != '':
                                    age_attribute_found = True
                                    age_attribute = getattr(current_dicom_data, attr)
                                    # logger.info(attr)
                                    # logger.info(type(age_attribute))
                                    # logger.info(len(age_attribute))
                                    # logger.info(f'_{age_attribute}_')
                        if not sex_attribute_found:
                            sex_attribute = 'NO_SEX'
                        if not age_attribute_found:
                            age_attribute = 'NO_AGE'
            folder_name = f"{y}_{sex_attribute}_{age_attribute}"
            folder = os.path.join(UNZIPED_PATH, x)
            pat_folder = os.path.join(UNZIPED_PATH, folder_name)
            os.mkdir(pat_folder)
            for inner_folder in os.listdir(folder):
                source_path = os.path.join(folder, inner_folder)
                destination_path = os.path.join(pat_folder, inner_folder)
                shutil.move(source_path, destination_path)
            os.rmdir(folder)
