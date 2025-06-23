import os
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from dicom_processing.dicom_repaire import DicomRepairProcessor, setup_logging, load_env_path

def find_dicom_files(root_path):
    dicom_files = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files

def process_file(processor, file_path):
    try:
        return processor.fix_dicom_geometry(file_path)
    except Exception as e:
        logging.error(f"Error while processing {file_path}: {e}")
        return False

def main():
    setup_logging()
    dicom_path = load_env_path()

    processor = DicomRepairProcessor()
    dicom_files = find_dicom_files(dicom_path)

    logging.info(f"Found {len(dicom_files)} DICOM files to process.")

    fixed_count = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, processor, file_path): file_path for file_path in dicom_files}
        for future in tqdm(as_completed(futures), total=len(futures), desc="File repaire"):
            if future.result():
                fixed_count += 1

    logging.info(f"Done: fixed {fixed_count} of {len(dicom_files)} files.")

if __name__ == "__main__":
    main()
