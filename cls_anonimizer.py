import os
import pydicom
from pydicom.uid import generate_uid

class Anonimizer:
    
    def __init__(self, fields_for_anonymize=None):
        """
        Инициализация класса с набором полей для анонимизации.
        По умолчанию, можно задать список полей, либо загрузить из конфига.
        """
        
        self.fields_for_anonymize = fields_for_anonymize or {
            'StudyDate',
            'SeriesDate',
            'AcquisitionDate',
            'ContentDate',
            'StudyTime',
            'SeriesTime',
            'AcquisitionTime',
            'ContentTime',
            'AccessionNumber',
            'ReferringPhysician Name',
            'InstitutionName',
            'StudyDescription',
            'SeriesDescription',
            'SOPInstanceUID',
            'SOPClassUID',
            'StationName'
        }

    def anonymize_field(self, dicom_data, field):
        """
        Получение типа данных для анонимизации.
        """
        if hasattr(dicom_data, field):
            vr = dicom_data.data_element(field).VR

            if vr == 'DA':                                      # Для даты
                setattr(dicom_data, field, '00000000')
            elif vr == 'TM':                                    # Для времени
                setattr(dicom_data, field, '000000')
            elif vr == 'UI':  # Для UID
                setattr(dicom_data, field, generate_uid())
            else:
                setattr(dicom_data, field, "Anon")              # Для всех остальных типов
                
    def process(self, dicom_path):
        """
        Обрабатывает один DICOM файл и анонимизирует поля.
        """
        dicom_data = pydicom.dcmread(dicom_path)

        for field in self.fields_for_anonymize:
            self.anonymize_field(dicom_data, field)

        dicom_data.save_as(dicom_path)

        print(f"Файл {dicom_path} был успешно анонимизирован!")
        

    def process_all(self, folder_path):
        """
        Принимает путь до директории с DICOM файлами, проходит по ней и анонимизирует их.
        """
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.dcm'):
                    dicom_path = os.path.join(root, file)
                    self.process(dicom_path)
        
        print(f"Файлы в директории {dicom_path} были успешно анонимизированы!")


if __name__ == "__main__":
    
    # Для перепроверки:
    # fields_for_anonymize = {'StudyDate', 'SeriesDate'}
    # anon = Anonimizer(fields_for_anonymize)
    # anon.process('./I0013727.dcm')
    
    anon = Anonimizer()
    # anon.process('./I0013727.dcm')
    
    anon.process_all('./datasets/pacient1/IMGDATA')
