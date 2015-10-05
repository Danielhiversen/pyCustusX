import sys
import os
sys.path.append( '../' )

import CxDataHandler
import numpy as np
import shutil


def convert(nav_acq):
  if nav_acq[-1] == '/':
        save_folder=nav_acq[0:-1]+"_raw/"
  else:
        save_folder=nav_acq+"_raw/"

  print save_folder


  if not os.path.isdir(save_folder):
    os.makedirs(save_folder)
        
  for dirpath, dirnames, filenames in os.walk(nav_acq):
    for file_j in filenames:
      print file_j
      file_org = os.path.join(dirpath, file_j)
      file_new = os.path.join(save_folder, file_j.replace('.zraw','.raw'))
      if (file_j[-4:]=='zraw') and 'mask' not in file_j:

        file_org_mhd=file_org[0:-4] + 'mhd'
        file_new_mhd=file_new[0:-3] + 'mhd'

        org_file_mhd = open(file_org_mhd)
        new_file_mhd = open(file_new_mhd,'w')
        convert=False

        channels=1

        for line in org_file_mhd:
          if 'ElementNumberOfChannels = 3' in line:
            newline=line
            channels=3
          elif 'CompressedData ' in line:
            newline='CompressedData = False\n'            
          elif 'CompressedDataSize' in line:
            newline=''
          elif '.raw' in line:
            newline=line.replace('zraw','raw')
          elif 'ElementType' in line:
            temp=line.split()
            ElementType=temp[-1]
            newline=line
          elif 'DimSize' in line:
            newline=line
            temp=line.split()
            if len(temp) == 5:
                dimSize=[int(temp[2]),int(temp[3]),int(temp[4])]
            elif len(temp) == 4:
                dimSize=[int(temp[2]),int(temp[3])]
          elif 'ElementDataFile' in line:
            newline = 'ElementDataFile = ' + file_j.replace('.zraw','.raw')
          else:
            newline =line
          new_file_mhd.write(newline)
        new_file_mhd.close()
        org_file_mhd.close()

        if channels == 3:
            dimSize=np.hstack([3,dimSize])        
    
        raw_file = CxDataHandler.rawFileReader(file_org,dimSize,ElementType=ElementType)
        data=raw_file.get_samples()
        rawWrither = CxDataHandler.rawFileWrither(file_new,data,ElementType=ElementType)
     
      elif (file_j[-3:]=='mhd') and not ('mask' in file_j):
        continue
      else:
        shutil.copy2(file_org, file_new)

      

 

if __name__ == '__main__':
  if len(sys.argv) < 2:
    nav_acq='/home/dahoiv/Dokumenter/nav_doppler/kode_py/pyIQdataHandler/2013-12-10_14-27_Laboratory_16.cx3/US_Acq/US_02_20131210T163637'
  else:
    nav_acq=sys.argv[1]

  convert(nav_acq)
