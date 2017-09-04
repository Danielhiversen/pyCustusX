# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 17:16:41 2015

@author: Daniel Hoyer Iversen
"""


FOLDER_IN = '/home/dahoiv/disk/data/brainshift/' 
FOLDER_IN ='/home/dahoiv/disk/data/brainshift/'
FOLDER_OUT = '/home/dahoiv/disk/data/brainshift_anoymized' #Should be empty, otherwise it will be deleted
RM_FILES =('png','mp4') #Will be removed from output folder
RM_FACE_CUT_OFF = -1 #mm to remove of nose. EXperimental, Tries to remove face from MR images

import os
from dateutil import parser
import datetime, time
import shutil
import struct
from PIL import Image  
import sys
sys.path.append("../CxDataHandler")
import CxDataHandler
import numpy as np


DATE_FMT = "%Y%m%d"
DEFAULT_DATE = datetime.datetime.strptime('20000102',DATE_FMT)
TXT_FILES = ('xml','mhd','txt','fts','tts')

def tryConvertToDate(string):
    j=-1
    while j+14 < len(string):
        j=j+1
        strDate= string[j:(j+15)]
        date=None
        try:
            date= datetime.datetime.strptime(strDate,'%Y%m%dT%H%M%S')
        except ValueError:
            continue
        except TypeError:
            continue    
        if date:
            return date
    
    string = string.replace('.','')
    try:
        return parser.parse(string,fuzzy=True)    
    except ValueError:
        pass
    try:
        return parser.parse(string[:-1],fuzzy=True)    
    except ValueError:
        pass
    
    print "Failed to convert date:  ", string
    return datetime.date.fromordinal(1)        
    
def getAcqDate(patientFolder):
    date = None
    
    for root, dirs, files in os.walk(patientFolder):
        for f in files:
            if f.endswith(('fts','tts')):
                date = tryConvertToDate(f)
                if date:
                    print date
                    return date
                
    print "Could not find acq date"        
    return None
        
def isCxFolder(folder):
    if len(folder)<4 or not folder[-4:]=='.cx3':
        return False
    if not os.path.exists(os.path.join(folder, 'custusdoc.xml')):
        return False
    return True
         
def anonymizeString(string,date_fmt='%Y%m%dT%H%M%S',date_fmt2="%Y%m%d"):

    j=0
    while j+len(date_fmt) < len(string):
        strDate= string[j:(j+len(date_fmt))]
        j=j+1
        try:
            date= datetime.datetime.strptime(strDate,date_fmt)
        except ValueError:
            continue
        except TypeError:
            continue
        if date.year < 2000:
            continue
        string=string.replace(date.strftime(date_fmt2),DEFAULT_DATE.strftime(date_fmt2))       
    return string
         
         
def anonymizeFilePath(fullPath,patientFolder):
    relPath = os.path.relpath(fullPath,patientFolder)
    relPath=anonymizeString(relPath)
    newPath=os.path.join(patientFolder,relPath)
    os.renames(fullPath,newPath)
    return newPath
        
def readImage(filePathIn):
    if not filePathIn.endswith(('png')):
        return None

    try:
        picture = Image.open(filePathIn)
    except IOError:
        return None
        # filename not an image file
    return picture

def saveImage(filePathOut, picture):
    # save picture
    picture.save(filePathOut)

def anonymizeImage(picture, pixelsX=None, pixelsY=None, color=(0, 0, 0)):

    pixels = picture.load()
    
    width, height = picture.size

    if not pixelsX:
        pixelsX = range(width)

    if not pixelsY:
        pixelsY = range(height)

    # Process given pixels
    for x in pixelsX:
        if x >= width:
            continue
        for y in pixelsY:
            if y >= height:
                continue
            pixels[x, y] = color
    return picture
            
def anonymizeFace(filePathMhd):
    if RM_FACE_CUT_OFF <= 0:
        return

    cutOff = 0.15


    mhdFile=CxDataHandler.mhdFile(filePathMhd)
    if 'Modality'not in mhdFile.Params:
        if not 'MR'in filePathMhd:
            return
    elif not mhdFile.Params['Modality'] == 'MR':
        return
    elif not mhdFile.get_DimSize() == 3:
        pass        
        #return
    
    print filePathMhd
    data=mhdFile.get_samples()
    
   
    X=[]
    Y=[]
    Z=[]
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            for z in range(data.shape[2]):
                if data[x,y,z]>1:
                    X.append(x)
                    Y.append(y)
                    Z.append(z)
    
    x_com=np.mean(X)
    y_com=np.mean(Y)
    z_com=np.mean(Z)

    def avgElAboveLimit(plane,limit=10):
        res=0
        for i in range(plane.shape[0]):
            for j in range(plane.shape[1]):
                    if plane[i,j]>limit:
                        res=res+1
        return res/float(plane.shape[0]*plane.shape[1])
        
        
    def findN(vec):
        temp=None
        k=0
        for el in vec:
            if not temp and el > 0.015:
                temp=k
            if temp and el >cutOff:
                return k
                return k-temp
            k=k+1

        
    x=[]
    for i in range(data.shape[0]):
        temp=avgElAboveLimit(data[i,:,:])
        x.append(temp)
    x1=findN(x)            
    x2=findN(x[::-1])

    y=[]        
    for i in range(data.shape[1]):
        temp=avgElAboveLimit(data[:,i,:])
        y.append(temp)
    y1=findN(y)            
    y2=findN(y[::-1])   

    z=[]
    z1=None
    z2=None
    for i in range(data.shape[2]):
        temp=avgElAboveLimit(data[:,:,i])
        z.append(temp)
    z1=findN(z)            
    z2=findN(z[::-1])

    import matplotlib.pyplot as plt    
    
    plt.plot(x)
    plt.show()  
    print x1,x2
    plt.plot(y)
    plt.show()  
    print y1,y2
    plt.plot(z)
    plt.show()  
    print z1,z2

    print
    print x_com
    print y_com
    print z_com
    
    
    I00=0
    I11=0
    I22=0
    I01=0
    I12=0
    I02=0
    
    Ixx=0
    Iyy=0
    Izz=0
    
    for i in range(len(X)):
        I00=I00+(Y[i]-y_com)**2+(Z[i]-z_com)**2
        I11=I11+(X[i]-x_com)**2+(Z[i]-z_com)**2
        I22=I22+(X[i]-x_com)**2+(Y[i]-y_com)**2
        I01=I01+(X[i]-x_com)*(Y[i]-y_com)
        I12=I12+(Y[i]-y_com)*(Z[i]-z_com)
        I02=I02+(X[i]-x_com)*(Z[i]-z_com)
        
        Ixx=Ixx+(X[i]-x_com)*(X[i]-x_com)
        Iyy=Iyy+(Y[i]-y_com)*(Y[i]-y_com)
        Izz=Izz+(Z[i]-z_com)*(Z[i]-z_com)


    I00=I00/len(X)
    I11=I11/len(X)
    I22=I22/len(X)
    I01=I01/len(X)
    I12=I12/len(X)
    I02=I02/len(X)
    
    Ixx=Ixx/len(X)    
    Iyy=Iyy/len(X)    
    Izz=Izz/len(X)
    
    print
    
    print Ixx
    print Iyy
    print Izz
    
    print    
    
    print I00
    print I11
    print I22
    print
    print I01
    print I12
    print I02    
    

    return 

    if idx==0 and lvec(idx)>0: 
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[0])
        data[0:N,:,:]=0
    if idx==0 and lvec(idx)<0:
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[0])
        data[-N:,:,:]=0
    if idx==1 and lvec(idx)>0:
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[1])
        data[:,0:N,:]=0
    if idx==1 and lvec(idx)<0:
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[1])
        data[:,-N:,:]=0
    if idx==2 and lvec(idx)>0:
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[2])
        data[:,:,0:N]=0
    if idx==2 and lvec(idx)<0:
        N=int(RM_FACE_CUT_OFF/mhdFile.get_spacing()[2])
        data[:,:,-N:]=0
        
    CxDataHandler.rawFileWrither(mhdFile.getRawFilePath(),data,color=False,ElementType=mhdFile.get_ElementType())
        
        
        
     
def anonymizeFile(filePath,acqDate,firstTS):
    
#            picture = readImage(fullPath)
#            if picture:
#                anonymizeImage(picture, pixelsX=None, pixelsY=range(0,29), color=(80, 78, 71))
#                saveImage(fullPath, picture)
            #modify the file timestamp to current time    
    
    if not filePath.endswith(TXT_FILES):
        return

    filedata = None
    with open(filePath, 'r') as file :
            filedata = file.read()

    if filePath.endswith(('fts','tts')):
        with open(filePath, 'r') as file :
            for line in file.readlines():
                j=-1
                while j+12 < len(line):
                    j=j+1
                    strDate= line[j:(j+13)]
                    try:
                        floatDate = float(strDate)
                    except ValueError:
                        continue
                    except TypeError:
                        continue
                   
                    try:
                        date=datetime.datetime.fromtimestamp(floatDate/1000)
                    except ValueError:
                        continue
                    except TypeError:
                        continue
                    if abs((date-acqDate).days)<2:
                        filedata=filedata.replace(strDate,"{:.0f}".format(floatDate-firstTS))
                        
    elif filePath.endswith(('mhd')):
        #anonymizeFace(filePath)    
        pass
        
    elif filePath.endswith(('custusdoc.xml')):
        with open(filePath, 'r') as file :
            for line in file.readlines():
                if '<active_patient>' in line:
                    filedata=filedata.replace(line,'    <active_patient> </active_patient>\n')
                    break
        j=-1
        while j+12 < len(filedata):
            j=j+1
            strDate= filedata[j:(j+13)]
            try:
                floatDate = float(strDate)
            except ValueError:
                continue
            except TypeError:
                continue
            
            try:
                date=datetime.datetime.fromtimestamp(floatDate/1000)
            except ValueError:
                continue
            except TypeError:
                continue
            if abs((date-acqDate).days)<2:
                filedata=filedata.replace(strDate,"{:.0f}".format(floatDate-firstTS))
    
    filedata=anonymizeString(filedata,date_fmt='%Y%m%dT%H%M%S',date_fmt2="%Y%m%d")

    filedata=anonymizeString(filedata,date_fmt='%Y-%m-%d',date_fmt2='%Y-%m-%d')
    
   
    with open(filePath, 'w') as file:
        file.write(filedata)    

def anonymizeToolpos(toolPosFile,acqDate):
    mbr = bytearray(file(toolPosFile, 'rb').read() )
    fmt='<Q'
    struct_len = struct.calcsize(fmt)
    s = struct.Struct(fmt)
    
    #Find first time stamp
    firstTs=None
    j=0
    while j+struct_len < len(mbr):
        date_float = float(struct.unpack(fmt, mbr[j:j+struct_len])[0])
        date = None
        try:
            date=datetime.datetime.fromtimestamp(date_float/1000)   
        except ValueError:
            pass
        except TypeError:
            pass

        if date and abs((date-acqDate).days)<2:
            if not firstTs:
                firstTs=float( time.mktime(date.timetuple())) * 1000
            else:
                firstTs=min(firstTs,float( time.mktime(date.timetuple())) * 1000)
                
        j=j+1
    if firstTs is None:
        return 0
    firstTs=firstTs-float( time.mktime(DEFAULT_DATE.timetuple())) * 1000
    
    j=0
    while j+struct_len < len(mbr):
        date_float = float(struct.unpack(fmt, mbr[j:j+struct_len])[0])
        date = None
        try:
            date=datetime.datetime.fromtimestamp(date_float/1000)   
        except ValueError:
            pass
        except TypeError:
            pass
        if date and abs((date-acqDate).days)<2:
            byte_date = s.pack(date_float-firstTs)
            mbr[j:j+struct_len]=bytearray(byte_date)
            
        j=j+1

    with open(toolPosFile, 'wb') as fileout:
        fileout.write(mbr)  
    return firstTs

              
             
def anonymizeFolder(patientFolder):
    acqDate=getAcqDate(patientFolder)
    if not acqDate:
        return
    firstTS=anonymizeToolpos(os.path.join(patientFolder,'Logs/toolpositions.snwpos'),acqDate)
    
    for root, dirs, files in os.walk(patientFolder):
        for f in files:            
            fullPath=os.path.join(root,f)
            if f.endswith(RM_FILES):
                os.remove(fullPath)
                continue
            anonymizeFile(fullPath,acqDate,firstTS)
    
    for root, dirs, files in os.walk(patientFolder):
        for f in files:            
            fullPath=os.path.join(root,f)
            anonymizeFilePath(fullPath,patientFolder)    
    
    
    # change modified timestamp in files
    for root, dirs, files in os.walk(patientFolder):
        for f in files: 
            fullPath=os.path.join(root,f)
            os.utime(fullPath,(1,1))
        os.utime(root,(1,1))
    os.utime(patientFolder,(1,1))         




def run():
    if os.path.exists(FOLDER_OUT):
        shutil.rmtree(FOLDER_OUT)

    for root, dirs, files in os.walk(FOLDER_IN):
        if isCxFolder(root):
            print root
            dst= os.path.join(FOLDER_OUT,os.path.relpath(root,FOLDER_IN))
            shutil.copytree(root, dst)
            anonymizeFolder(dst)

if __name__ == '__main__':   
    os.nice(19)
    run()
    
