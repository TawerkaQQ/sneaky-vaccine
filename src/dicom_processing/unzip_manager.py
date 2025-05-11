import zipfile
import os


class UnzipManager:

    def __init__(self, zip_dir, extract_path):
        """
        Инициализация класса, принимаем путь к директории с зипами и путь для извлечения файлов.
        """
        self.zip_dir = zip_dir
        self.extract_path = extract_path
        self.zip_files = []

    def __enter__(self):
        """
        Метод вызывается при входе в контекст. Открываем все зипы в директории и распаковываем их.
        """
        self.zip_files = [os.path.join(self.zip_dir, f) for f in os.listdir(self.zip_dir) if f.lower().endswith('.zip')]
        for zip_file_path in self.zip_files:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Метод вызывается при закрытии контекста.
        """
        pass

    def get_folder(self):
        """
        Возвращает список директорий, где хранятся DICOM файлы.
        Ищем DICOM файлы по расширению .dcm.
        """
        dicom_folders = set()
        for root, dirs, files in os.walk(self.extract_path):
            for file in files:
                if file.lower().endswith('.dcm'):
                    dicom_folders.add(root)
        return list(dicom_folders)
