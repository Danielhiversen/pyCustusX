import shutil
import CxDataHandler
import numpy as np
from pyusound.dicom.recloader import DicomRecordingBMode2dCompounding
import os
import sys
from collections import defaultdict


def RemoveRect(nav_acq):
    if nav_acq[-1]=='/':
        nav_acq=nav_acq[:-1]
    if os.path.isdir(nav_acq+"_removed_rect"):
        print "Folder already exists"
        return
    shutil.copytree(nav_acq,nav_acq+"_removed_rect")

    CxData=CxDataHandler.cxOpenCV.from_acq_folder(nav_acq+"_removed_rect")

    for frame_no in range(0,CxData.get_no_of_frames()):
        print frame_no
        vtk=CxData.load_mhd(frame_no)
        data=vtk.loadRawData_removeRect()
        CxDataHandler.rawFileWrither(vtk.getRawFilePath(),data,True)
        vtk.save_to_new_file(vtk.getFilePath(),overwrite=True)
#CxDataHandler.rawFileWrither('/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/test/'+str(frame_no)+'.raw',data,True)   #
	

if __name__ == '__main__':
   	  
	# folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/US_Acq/Acq_03_20140126T115603'
	# RemoveRect(folder)


	# folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/US_Acq/Acq_04_20140126T115704'
	# RemoveRect(folder)

	# folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/US_Acq/Acq_06_20140126T115838'
	# RemoveRect(folder)




    # folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-02-06_AVM.cx3/US_Acq/US_26_20140206T114213'
    # RemoveRect(folder)


    # folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-02-06_AVM.cx3/US_Acq/US_27_20140206T114335'
    # RemoveRect(folder)

    # folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-02-06_AVM.cx3/US_Acq/US_28_20140206T114435'
    # RemoveRect(folder)


    folder ='/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/US_Acq/Acq_05_20140126T115746'
    RemoveRect(folder)

    folder='/home/dahoiv/Dokumenter/nav_doppler/data/2014-01-26_11-21_Laboratory_17.cx3/US_Acq/Acq_07_20140126T115931'
    RemoveRect(folder)
