import os
import numpy as np
import glob
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import ExplicitVRLittleEndian

# ============================================================
# СЛОВАРЬ ТЕГОВ DICOM
# ============================================================
dicom_tags = {
    # ------ Группа 0008: Информация об изображении ------
    'SpecificCharacterSet': (0x0008, 0x0005),
    'ImageType': (0x0008, 0x0008),
    'SOPClassUID': (0x0008, 0x0016),
    'SOPInstanceUID': (0x0008, 0x0018),
    'StudyDate': (0x0008, 0x0020),
    'SeriesDate': (0x0008, 0x0021),
    'AcquisitionDate': (0x0008, 0x0022),
    'ContentDate': (0x0008, 0x0023),
    'AcquisitionDateTime': (0x0008, 0x002A),
    'StudyTime': (0x0008, 0x0030),
    'SeriesTime': (0x0008, 0x0031),
    'AcquisitionTime': (0x0008, 0x0032),
    'ContentTime': (0x0008, 0x0033),
    'AccessionNumber': (0x0008, 0x0050),
    'Modality': (0x0008, 0x0060),
    'PresentationIntentType': (0x0008, 0x0068),
    'Manufacturer': (0x0008, 0x0070),
    'InstitutionName': (0x0008, 0x0080),
    'InstitutionAddress': (0x0008, 0x0081),
    'ReferringPhysicianName': (0x0008, 0x0090),
    'StationName': (0x0008, 0x1010),
    'StudyDescription': (0x0008, 0x1030),
    'PhysiciansOfRecord': (0x0008, 0x1048),
    'PerformingPhysicianName': (0x0008, 0x1050),
    'NameOfPhysiciansReadingStudy': (0x0008, 0x1060),
    'ManufacturerModelName': (0x0008, 0x1090),

    # ------ Группа 0010: Информация о пациенте ------
    'PatientName': (0x0010, 0x0010),
    'PatientID': (0x0010, 0x0020),
    'PatientBirthDate': (0x0010, 0x0030),
    'PatientBirthTime': (0x0010, 0x0032),
    'PatientSex': (0x0010, 0x0040),
    'PatientWeight': (0x0010, 0x1030),

    # ------ Группа 0018: Технические параметры ------
    'BodyPartExamined': (0x0018, 0x0015),
    'KVP': (0x0018, 0x0060),
    'DeviceSerialNumber': (0x0018, 0x1000),
    'SoftwareVersions': (0x0018, 0x1020),
    'DistanceSourceToDetector': (0x0018, 0x1110),
    'EstimatedRadiographicMagnificationFactor': (0x0018, 0x1114),
    'ExposureInuAs': (0x0018, 0x1153),
    'ImagerPixelSpacing': (0x0018, 0x1164),  # ← ВАЖНО!
    'FocalSpots': (0x0018, 0x1190),
    'AnodeTargetMaterial': (0x0018, 0x1191),
    'BodyPartThickness': (0x0018, 0x11A0),
    'CompressionForce': (0x0018, 0x11A2),
    'PaddleDescription': (0x0018, 0x11A4),
    'AcquisitionDeviceProcessingCode': (0x0018, 0x1401),
    'RelativeXRayExposure': (0x0018, 0x1405),
    'ColumnAngulation': (0x0018, 0x1450),
    'PositionerPrimaryAngle': (0x0018, 0x1510),
    'ViewPosition': (0x0018, 0x5101),
    'DetectorConfiguration': (0x0018, 0x7005),
    'DetectorDescription': (0x0018, 0x7006),
    'DetectorMode': (0x0018, 0x7008),
    'DetectorID': (0x0018, 0x700A),
    'DetectorActiveShape': (0x0018, 0x7024),
    'DetectorActiveDimensions': (0x0018, 0x7026),
    'DetectorManufacturerModelName': (0x0018, 0x702B),
    'FilterMaterial': (0x0018, 0x7050),
    'ExposureControlMode': (0x0018, 0x7060),
    'ExposureControlModeDescription': (0x0018, 0x7062),
    'ExposureTimeInuS': (0x0018, 0x8150),
    'XRayTubeCurrentin_uA': (0x0018, 0x8151),  # ИСПРАВЛЕНО: правильное имя атрибута
    'ExposureInmAs': (0x0018, 0x9332),

    # ------ Группа 0020: Информация об исследовании ------
    'StudyInstanceUID': (0x0020, 0x000D),
    'SeriesInstanceUID': (0x0020, 0x000E),
    'StudyID': (0x0020, 0x0010),
    'SeriesNumber': (0x0020, 0x0011),
    'InstanceNumber': (0x0020, 0x0013),
    'PatientOrientation': (0x0020, 0x0020),
    'Laterality': (0x0020, 0x0060),
    'ImageLaterality': (0x0020, 0x0062),
    'ImagesInAcquisition': (0x0020, 0x1002),
    'ImageComments': (0x0020, 0x4000),

    # ------ Группа 0028: Информация об изображении (ВАЖНО!) ------
    'SamplesPerPixel': (0x0028, 0x0002),
    'PhotometricInterpretation': (0x0028, 0x0004),
    'Rows': (0x0028, 0x0010),
    'Columns': (0x0028, 0x0011),
    'PixelSpacing': (0x0028, 0x0030),  # ← ВАЖНО!
    'PixelAspectRatio': (0x0028, 0x0034),
    'BitsAllocated': (0x0028, 0x0100),
    'BitsStored': (0x0028, 0x0101),
    'HighBit': (0x0028, 0x0102),
    'PixelRepresentation': (0x0028, 0x0103),
    'PixelPaddingValue': (0x0028, 0x0120),
    'BurnedInAnnotation': (0x0028, 0x0301),
    'PixelSpacingCalibrationType': (0x0028, 0x0A02),
    'PixelSpacingCalibrationDescription': (0x0028, 0x0A04),
    'PixelIntensityRelationship': (0x0028, 0x1040),
    'PixelIntensityRelationshipSign': (0x0028, 0x1041),
    'WindowCenter': (0x0028, 0x1050),
    'WindowWidth': (0x0028, 0x1051),
    'RescaleIntercept': (0x0028, 0x1052),
    'RescaleSlope': (0x0028, 0x1053),
    'RescaleType': (0x0028, 0x1054),
    'LossyImageCompression': (0x0028, 0x2110),

    # ------ Группа 0032: Информация о запросе ------
    'RequestingPhysician': (0x0032, 0x1032),

    # ------ Группа 0040: Дозы ------
    'EntranceDose': (0x0040, 0x0302),
    'CommentsOnRadiationDose': (0x0040, 0x0310),
    'HalfValueLayer': (0x0040, 0x0314),
    'OrganDose': (0x0040, 0x0316),
    'EntranceDosein_mGy': (0x0040, 0x8302),  # ИСПРАВЛЕНО: правильное имя атрибута

    # ------ Группа 0054: Коды проекций ------
    'ViewCodeSequence': (0x0054, 0x0220),

    # ------ Группа 2050: LUT ------
    'PresentationLUTShape': (0x2050, 0x0020),

    # ------ Группа 3004: Дозы ------
    'DoseUnits': (0x3004, 0x0002),
    'DoseType': (0x3004, 0x0004),
    'DoseValue': (0x3004, 0x0012),
}

# ============================================================
# ЗНАЧЕНИЯ ТЕГОВ
# ============================================================
tag_values = {
    # Группа 0008
    'SpecificCharacterSet': 'ISO_IR 192',
    'ImageType': ['ORIGINAL', 'PRIMARY', ''],
    'SOPClassUID': '1.2.840.10008.5.1.4.1.1.1.2',
    'StudyDate': '20260702',
    'SeriesDate': '20260702',
    'AcquisitionDate': '20260702',
    'ContentDate': '20260702',
    'AcquisitionDateTime': '20260702141704.084000',
    'StudyTime': '141631.036154',
    'SeriesTime': '141704.084113',
    'AcquisitionTime': '141704.084113',
    'ContentTime': '141704.084113',
    'AccessionNumber': '1',
    'Modality': 'MG',
    'PresentationIntentType': 'FOR PRESENTATION',
    'Manufacturer': 'MEDICAL TECHNOLOGIES Ltd',
    'InstitutionName': 'Poliklinika 7',
    'InstitutionAddress': 'Clinic address.',
    'ReferringPhysicianName': '',
    'StationName': '[袧袝_袧袗小孝袪袨袝袧袨]',
    'StudyDescription': '',
    'PhysiciansOfRecord': '',
    'PerformingPhysicianName': '[袧袝_袧袗小孝袪袨袝袧袨]',
    'NameOfPhysiciansReadingStudy': '',
    'ManufacturerModelName': 'NCC-1701',

    # Группа 0010
    'PatientName': '@2026-07-02-14-16@',
    'PatientID': 'EM20260702-1416',
    'PatientBirthDate': '',
    'PatientBirthTime': '',
    'PatientSex': 'F',
    'PatientWeight': 0,  # ИСПРАВЛЕНО: DS → число

    # Группа 0018
    'BodyPartExamined': 'BREAST',
    'KVP': 26,  # ИСПРАВЛЕНО: DS → число
    'DeviceSerialNumber': '42',
    'SoftwareVersions': '26.0.1.13',
    'DistanceSourceToDetector': 660,  # ИСПРАВЛЕНО: DS → число
    'EstimatedRadiographicMagnificationFactor': 1.03999996185,  # ИСПРАВЛЕНО: DS → число
    'ExposureInuAs': 24400,  # ИСПРАВЛЕНО: IS → число
    'ImagerPixelSpacing': [0.069, 0.069],  # ИСПРАВЛЕНО: DS → числа
    'FocalSpots': 0.3,  # ИСПРАВЛЕНО: DS → число
    'AnodeTargetMaterial': 'TUNGSTEN',
    'BodyPartThickness': -1,  # ИСПРАВЛЕНО: DS → число
    'CompressionForce': 0,  # ИСПРАВЛЕНО: DS → число
    'PaddleDescription': '24x30',
    'AcquisitionDeviceProcessingCode': 'MAMMO SCREENING SINGLE FRAME CAPTURE',
    'RelativeXRayExposure': 17,  # ИСПРАВЛЕНО: IS → число
    'ColumnAngulation': 0,  # ИСПРАВЛЕНО: DS → число
    'PositionerPrimaryAngle': 0,  # ИСПРАВЛЕНО: DS → число
    'ViewPosition': 'CC',
    'DetectorConfiguration': 'AREA',
    'DetectorDescription': '',
    'DetectorMode': 'Empty',
    'DetectorID': '',
    'DetectorActiveShape': 'RECTANGLE',
    'DetectorActiveDimensions': [4352, 3480],  # ИСПРАВЛЕНО: DS → числа
    'DetectorManufacturerModelName': '',
    'FilterMaterial': 'SILVER',
    'ExposureControlMode': 'MANUAL',
    'ExposureControlModeDescription': 'MANUAL',
    'ExposureTimeInuS': 1000,  # ИСПРАВЛЕНО: DS → число
    'XRayTubeCurrentin_uA': 0,  # ИСПРАВЛЕНО: DS → число (и исправлено имя)
    'ExposureInmAs': 24.44288,  # ИСПРАВЛЕНО: FD → число

    # Группа 0020
    'StudyID': 'EM20260702-1416',
    'SeriesNumber': 1,  # ИСПРАВЛЕНО: IS → число
    'InstanceNumber': 0,  # ИСПРАВЛЕНО: IS → число
    'PatientOrientation': ['A', 'R'],
    'Laterality': 'L',
    'ImageLaterality': 'L',
    'ImagesInAcquisition': 0,  # ИСПРАВЛЕНО: IS → число
    'ImageComments': '',

    # Группа 0028
    'SamplesPerPixel': 1,
    'PhotometricInterpretation': 'MONOCHROME2',
    'PixelAspectRatio': [1, 1],  # ИСПРАВЛЕНО: IS → числа
    'BitsAllocated': 16,
    'BitsStored': 16,
    'HighBit': 15,
    'PixelRepresentation': 0,
    'PixelPaddingValue': 0,
    'BurnedInAnnotation': 'NO',
    'PixelSpacingCalibrationType': 'GEOMETRY',
    'PixelSpacingCalibrationDescription': 'Mammounit estimated magnification defined spacing calibration',
    'PixelIntensityRelationship': 'LIN',
    'PixelIntensityRelationshipSign': 1,
    'WindowCenter': 32767,  # ИСПРАВЛЕНО: DS → число
    'WindowWidth': 65535,  # ИСПРАВЛЕНО: DS → число
    'RescaleIntercept': 0,  # ИСПРАВЛЕНО: DS → число
    'RescaleSlope': 1,  # ИСПРАВЛЕНО: DS → число
    'RescaleType': 'US',
    'LossyImageCompression': '00',

    # Группа 0032
    'RequestingPhysician': '',

    # Группа 0040
    'EntranceDose': 0,  # ИСПРАВЛЕНО: US → число
    'CommentsOnRadiationDose': 'RelativeXRayExposure (0018,1405) contains effective dose in microSv calculated by Russia Federation guidelines (袦校袣 2.6.1.1797-03). It is product of AGD in microGy and 0.05 koeff.',
    'HalfValueLayer': 0.512000024319,  # ИСПРАВЛЕНО: DS → число
    'OrganDose': 0.338176391391,  # ИСПРАВЛЕНО: DS → число
    'EntranceDosein_mGy': 1.0940633088,  # ИСПРАВЛЕНО: DS → число (и исправлено имя)

    # Группа 2050
    'PresentationLUTShape': 'IDENTITY',

    # Группа 3004
    'DoseUnits': 'GY',
    'DoseType': 'EFFECTIVE',
    'DoseValue': 1.69088195695e-05,  # ИСПРАВЛЕНО: DS → число
}



# Указываем путь к директории
directory_path = r"D:\Маммо_DBT\DBT_processing"
imageSize = (4352, 3480)

# Ищем все .raw файлы во всех подкаталогах
raw_files = glob.glob(os.path.join(directory_path, "**", "*.raw"), recursive=True)

print(f"Найдено .raw файлов: {len(raw_files)}")


for file_path in raw_files:
    try:
        # 1. Читаем .raw файл
        npimg = np.fromfile(file_path, dtype=np.float32)
        npimg = npimg.reshape(imageSize)
        npimg_normalized = ((npimg - npimg.min()) / (npimg.max() - npimg.min()) * 65535).astype(np.uint16)
        # ИНВЕРТИРУЕМ ЦВЕТА: черный ↔ белый
        npimg_inverted = 65535 - npimg_normalized

        ds = Dataset()

        for tag_name, tag_value in tag_values.items():
            try:
                if tag_name in dicom_tags:
                    setattr(ds, tag_name, tag_value)
            except Exception as e:
                print(f"  Предупреждение: не удалось установить тег {tag_name}: {e}")

        # 7. Генерируем новые UID
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()

        # 8. Обновляем размеры из данных
        rows, cols = npimg_inverted.shape
        ds.Rows = rows
        ds.Columns = cols

        # 9. Устанавливаем пиксельные данные
        ds.PixelData = npimg_inverted.tobytes()

        # 10. Устанавливаем file_meta
        ds.file_meta = Dataset()
        ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

        # 11. Сохраняем DICOM файл
        dcm_path = os.path.splitext(file_path)[0] + '.dcm'
        pydicom.dcmwrite(dcm_path, ds, write_like_original=False)

        print(f"  ✓ Сохранен DICOM: {os.path.basename(dcm_path)}")
    except Exception as e:
        print(f"  ✗ ОШИБКА: {e}")