import zipfile
import os

from tqdm import tqdm

class UnzipManager:

    def __init__(self, zip_dir, extract_path):
        """
        Class initialization. Accepts the path to the directory containing zip files and the extraction path.
        """
        self.zip_dir = zip_dir
        self.extract_path = extract_path
        self.zip_files = []

    def __enter__(self):
        """
        Called when entering the context. Opens all zip files in the directory and extracts them.
        """
        self.zip_files = [os.path.join(self.zip_dir, f) for f in os.listdir(self.zip_dir) if f.lower().endswith('.zip')]
        for zip_file_path in tqdm(self.zip_files, desc='Unzipping files', unit='file'):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when exiting the context.
        """
        pass

    def get_folder(self):
        """
        Returns a list of directories where DICOM files are stored.
        Searches for DICOM files by the .dcm extension.
        """
        dicom_folders = set()
        for root, dirs, files in os.walk(self.extract_path):
            for file in files:
                if file.lower().endswith('.dcm'):
                    dicom_folders.add(root)
        return list(dicom_folders)
