# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 18:26:09 2015

@author: Daniel Hoyer Iversen

"""
import sys
sys.path.append( '../' )
import CxDataHandler
import numpy as np
import matplotlib.pyplot as plt

acq_folder = '/home/dahoiv/disk/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_01_20151102T093342/'

OUT = '/home/dahoiv/disk/temp/babyHeart/'

def calFolder(acq_folder):
    frame_pos = CxDataHandler.fpFile.from_acq_folder(acq_folder,'Angio')
    time_stamps = CxDataHandler.ftsFile.from_acq_folder(acq_folder,'Angio')
    res=np.zeros((4,4))
    x = []
    y = []
    z = []
    ts = []

    for k in range(frame_pos.get_no_of_tp()):
        temp = frame_pos.get_tp_nr(k)
        res = res + temp

        ts.append(time_stamps.get_ts_nr(k))
        x.append(temp[0, 3])
        y.append(temp[1, 3])        
        z.append(temp[2, 3])
        
    res = res / frame_pos.get_no_of_tp()
    ts = ts -ts[0]    
    ts = ts / 1000.0
    print res
    
    plt.cla()
    plt.plot(ts, x-np.mean(x), linewidth=2.0)    
    plt.plot(ts, y-np.mean(y), linewidth=2.0)    
    plt.plot(ts, z-np.mean(z), linewidth=2.0)    
    plt.ylabel('mm')
    plt.xlabel('s')
    plt.legend(['x','y','z'])
    #plt.show()    

    plt.savefig(OUT + time_stamps.get_folder_name() + '.jpg')

    np.savetxt(OUT + time_stamps.get_folder_name() + '.txt',res,fmt='%.7f')


if __name__ == '__main__':
    folders = [    
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_01_20151102T093342',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_02_20151102T093406',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_03_20151102T093427',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_04_20151102T093450',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_05_20151102T093520',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_06_20151102T093558',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_07_20151102T093623',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_08_20151102T093646',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_09_20151102T093709',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_10_20151102T093736',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_11_20151102T093807',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_12_20151102T094036',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_13_20151102T094101',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_14_20151102T094122',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_15_20151102T094146',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_16_20151102T094209',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_17_20151102T094454',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_18_20151102T094515',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_19_20151102T094536',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_20_20151102T094601',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_21_20151102T094628',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_22_20151102T094657',
'/mnt/luks-b976c9ed-5af1-4f04-be66-17548ca41d2d/data/BabyHeart/2015-11-02_baby_heart2.cx3/US_Acq/US-Acq_23_20151102T094717']
    for acq_folder in folders:
        calFolder(acq_folder)