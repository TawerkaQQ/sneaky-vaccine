import zipfile
import os


class UnzipManager:
    
    def __init__(self, zip_path, extract_path):
        """
        Инициализация класса, принимаем путь к зипарю и путь для извлечения файлов.
        """
        self.zip_path = zip_path
        self.extract_path = extract_path
        self.zip_file = None

    def __enter__(self):
        """
        Метод вызывается при входе в контекст. Открываем зипарь и распаковываем его.
        """
        self.zip_file = zipfile.ZipFile(self.zip_path, 'r')
        self.zip_file.extractall(self.extract_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Метод вызывается при закрытии зипаря
        """
        if self.zip_file:
            self.zip_file.close()

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


if __name__ == "__main__":
    
    zip_path = "datasets/pacient5.zip"
    extract_path = "datasets/patient5"

    with UnzipManager(zip_path, extract_path) as manager:
        dicom_dirs = manager.get_folder()
        print("Папки с DICOM файлами:", dicom_dirs)
