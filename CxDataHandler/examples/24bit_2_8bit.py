import CxDataHandler
import numpy as np
import os
import shutil
import sys

def convert(nav_acq):
  save_folder=nav_acq+"_8bit/"

  if not os.path.isdir(save_folder):
    os.makedirs(save_folder)
        
  for dirpath, dirnames, filenames in os.walk(nav_acq):
    for file_j in filenames:
      print file_j
      file_org = os.path.join(dirpath, file_j)
      file_new = os.path.join(save_folder, file_j)
      if (file_j[-3:]=='raw') and 'mask' not in file_j:

        if (file_j[-4:]=='zraw'):
          file_org_mhd=file_org.replace('zraw','mhd')
          file_new_mhd=file_new.replace('zraw','mhd')
        else:
          file_org_mhd=file_org.replace('raw','mhd')
          file_new_mhd=file_new.replace('raw','mhd')

        org_file_mhd = open(file_org_mhd)
        new_file_mhd = open(file_new_mhd,'w')
        convert=False

        for line in org_file_mhd:
          if 'ElementNumberOfChannels = 3' in line:
            newline=''
            convert=True
          elif 'ElementSize' in line:
            newline=''            
          elif 'DimSize' in line:
            newline=line
            temp=line.split()
            if len(temp) == 5:
                dimSize=[int(temp[2]),int(temp[3]),int(temp[4])]
            elif len(temp) == 4:
                dimSize=[int(temp[2]),int(temp[3])]
           
          else:
            newline =line
          new_file_mhd.write(newline)
        new_file_mhd.close()
        org_file_mhd.close()

        dimSize=np.hstack([3,dimSize])
        if convert:
          raw_file = CxDataHandler.rawFileReader(file_org,dimSize)
          data=raw_file.get_samples()
          data=np.mean(data,axis=0)
          rawWrither = CxDataHandler.rawFileWrither(file_new,data)
        else:
          shutil.copy2(file_org, file_new)

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
