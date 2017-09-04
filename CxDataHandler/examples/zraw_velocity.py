import sys
import os
sys.path.append( '../' )

import CxDataHandler
import numpy as np
import shutil
import matplotlib
matplotlib.use('Agg')
# pylint: disable= wrong-import-position
import matplotlib.pyplot as plt  # noqa
import matplotlib.cm as cm  # noqa

def convert(nav_acq):
  if nav_acq[-1] == '/':
        save_folder=nav_acq[0:-1]+"_png/"
  else:
        save_folder=nav_acq+"_png/"

  print save_folder


  if not os.path.isdir(save_folder):
    os.makedirs(save_folder)
  just_positive = True        
  for dirpath, dirnames, filenames in os.walk(nav_acq):
    for file_j in filenames:
      if "Velocity" not in file_j:
          continue
      print file_j
      file_org = os.path.join(dirpath, file_j)
      file_new = os.path.join(save_folder, file_j.replace('.zraw','.raw'))
      if (file_j[-4:]=='zraw') and 'mask' not in file_j:

        file_org_mhd=file_org[0:-4] + 'mhd'

        org_file_mhd = open(file_org_mhd)

        convert=False

        channels=1

        for line in org_file_mhd:
          if 'ElementNumberOfChannels = 3' in line:
            channels = 3
          elif 'ElementType' in line:
            temp=line.split()
            ElementType=temp[-1]
          elif 'DimSize' in line:
            temp=line.split()
            if len(temp) == 5:
                dimSize=[int(temp[2]),int(temp[3]),int(temp[4])]
            elif len(temp) == 4:
                dimSize=[int(temp[2]),int(temp[3])]
        org_file_mhd.close()

        if channels == 3:
            dimSize=np.hstack([3,dimSize])
        raw_file = CxDataHandler.rawFileReader(file_org,dimSize,ElementType=ElementType)
        data=raw_file.get_samples()
        idx_n = data < 0
        if sum(sum(data < 0)) ==0:
            just_positive = False
        idx_p = data > 0
        data = data*0 + 125
        data[idx_n] = 0
        data[idx_p] = 255
#        rawWrither = CxDataHandler.rawFileWrither(file_org,data,ElementType=ElementType)
        # rawWrither = CxDataHandler.rawFileWrither(file_new,data,ElementType=ElementType)
        print data.shape
  if just_positive:
      print("just positive values")

if __name__ == '__main__':
  if len(sys.argv) < 2:
    nav_acq='/home/dahoiv/disk/data/pasDataAngleCorr/tumor/071_Tumor.cx3/US_Acq/US-Acq_02_19700101T103141'
    #nav_acq='/home/dahoiv/disk/data/pasDataAngleCorr/tumor/145_2016-10-06_Tumor.cx3/US_Acq/US-Acq_2_20161006T110939'
  else:
    nav_acq=sys.argv[1]

  convert(nav_acq)
