import os
import numpy as np
import pydicom



npimg = np.fromfile(os.path.join(path, name), dtype=np.float32)
imageSize = (4352, 3480)
npimg = npimg.reshape(imageSize)

dicom_data = pydicom.dcmread(os.path.join(path, name))
dicom_data.add_new([0x0028, 0x0008], 'IS', new_shape[0]) # Number of Frames
dicom_data[0x0028, 0x0010].value = new_shape[1]  # Number of Raws\n",
dicom_data[0x0028, 0x0011].value = new_shape[2]  # Number of Columns\n",
try:
	dicom_data[0x0028, 0x0030].value = [new_PixelSpacing[0], new_PixelSpacing[1]] # Pixel Spacing
except:
	dicom_data[0x0018, 0x1164].value = [new_PixelSpacing[0], new_PixelSpacing[1]]  # Pixel Spacing
dicom_data.PixelData = imarray_new.astype('int16').tobytes()
dicom_data.save_as(os.path.join(res_path, res_name))