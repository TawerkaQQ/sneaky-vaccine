import os
import sys
import subprocess
subprocess.check_call([sys.executable, '-m', "pip", "install", "pandas", "pyarrow"])
import pandas as pd
import csv
from DICOMLib import DICOMUtils

base_path = "C:/Users/admin/Desktop/anonymize/test"
log_path = "C:/Users/admin/Desktop/anonymize/log.parquet"
log_path_csv = "C:/Users/admin/Desktop/anonymize/log.csv"

log_entries = []

for patient_folder in os.listdir(base_path):
    print(f'Обрабатывается пациент: {patient_folder}')
    patient_path = os.path.join(base_path, patient_folder)
    
    if not os.path.isdir(patient_path):
        continue
    
    try:
        with DICOMUtils.TemporaryDICOMDatabase() as db:
            DICOMUtils.importDicom(patient_path, db)
            patientUIDs = db.patients()
            num_patients = len(patientUIDs)
            print(f"Найдено пациентов: {len(patientUIDs)}")
            
            if num_patients == 0:
                log_entries.append({
                    "Name_patient": patient_folder,
                    "Patients_found": 0,
                    "SeriesUID": None,
                    "Success": False
                })
                print(f"[{patient_folder}] ❌ Пациенты не найдены")
                continue
            
            for patientUID in patientUIDs:
                studyUIDs = db.studiesForPatient(patientUID)
                for studyUID in studyUIDs:
                    seriesUIDs = db.seriesForStudy(studyUID)
                    for seriesUID in seriesUIDs:
                        print(f"[{patient_folder}] Загрузка серии: {seriesUID} ...")
                        success = DICOMUtils.loadSeriesByUID([seriesUID])
                        loaded = bool(success)
                        log_entries.append({
                            "Name_patient": patient_folder,
                            "Patients_found": num_patients,
                            "SeriesUID": seriesUID,
                            "Success": loaded
                        })
                        if loaded:
                            print(f"✅ Данные загрузились успешно!")
                        else:
                            print(f"❌ Данные загрузились c ошибкой!")

    except Exception as e:
        log_entries.append({
            "Name_patient": patient_folder,
            "Patients_found": 0,
            "SeriesUID": None,
            "Success": False
        })
        print(f"[{patient_folder}] ⚠ Ошибка при загрузке: {str(e)}")

df = pd.DataFrame(log_entries)
df.to_parquet(log_path, engine='pyarrow', index=False)

with open(log_path_csv, mode='w', newline='', encoding='utf8') as cvsfile:
    field_names= ["Name_patient", "Patients_found", "SeriesUID", "Success"]
    writer = csv.DictWriter(cvsfile, fieldnames=field_names, delimiter=',', extrasaction='ignore')
    writer.writeheader()
    for entry in log_entries:
        row = {key: entry.get(key, "") for key in writer.fieldnames}
        line = ','.join([str(row[key]) for key in writer.fieldnames])
        cvsfile.write(line + '\n')

print(f"\n Лог сохранен в {log_path} и {log_path_csv}")
