# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 17:16:41 2015

@author: Daniel Hoyer Iversen
"""

import os
from dateutil import parser
import datetime, time
import shutil
import struct
from PIL import Image  

FOLDER_IN = '/home/dahoiv/disk/data/brainshift/' #'/home/dahoiv/disk/data/brainshift'
FOLDER_OUT = '/home/dahoiv/disk/data/brainshift_anoymized'

DATE_FMT = "%Y%m%d"
DEFAULT_DATE = datetime.datetime.strptime('19700101',DATE_FMT)

TXT_FILES = ('xml','mhd','txt','fts','tts')
RM_FILES =('png','mp4') #Will be removed from output folder

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
    
#    import commands
#    picture.save('temp.bmp')
#    # Invoking tesseract from python to extract characters
#    commands.getoutput('tesseract temp.bmp data')
#    # Reading the output generated in data.txt
#    with open('data.txt', 'r') as data:
#        print data.readline().strip()
# 

    # Get the size of the image
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
        

            
     
def anonymizeFile(filePath,acqDate,firstTS):
    
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
                    
    elif filePath.endswith(('xml')):
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
        
    j=-1
    while j+14 < len(filedata):
        j=j+1
        strDate= filedata[j:(j+15)]
        try:
            date= datetime.datetime.strptime(strDate,'%Y%m%dT%H%M%S')
        except ValueError:
            continue
        except TypeError:
            continue
        filedata=filedata.replace(date.strftime("%Y%m%d"),DEFAULT_DATE.strftime("%Y%m%d"))        
        
    j=-1
    while j+9 < len(filedata):
        j=j+1
        strDate= filedata[j:(j+10)]
        try:
            date= datetime.datetime.strptime(strDate,'%Y-%m-%d')
        except ValueError:
            continue
        except TypeError:
            continue
        filedata=filedata.replace(date.strftime('%Y-%m-%d'),DEFAULT_DATE.strftime('%Y-%m-%d'))       


    with open(filePath, 'w') as file:
        file.write(filedata)    

def anonymizeToolpos(toolPosFile,acqDate):
    mbr = bytearray(file(toolPosFile, 'rb').read() )
    fmt='<Q'
    struct_len = struct.calcsize(fmt)
    s = struct.Struct(fmt)
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
         
def anonymizeFilePath(fullPath,patientFolder):
    relPath = os.path.relpath(fullPath,patientFolder)
    rename = False
    j=-1
    while j+14 < len(relPath):
        j=j+1
        strDate= relPath[j:(j+15)]
        try:
            date= datetime.datetime.strptime(strDate,'%Y%m%dT%H%M%S')
        except ValueError:
            continue
        except TypeError:
            continue
        relPath=relPath.replace(date.strftime("%Y%m%d"),DEFAULT_DATE.strftime("%Y%m%d"))
        rename = True

    if rename:
        os.renames(fullPath,os.path.join(patientFolder,relPath))
        return os.path.join(patientFolder,relPath)
        
    return fullPath
               
             
def anonymizeFolder(patientFolder):
    acqDate=getAcqDate(patientFolder)
    if not acqDate:
        return
    firstTS=anonymizeToolpos(os.path.join(patientFolder,'Logs/toolpositions.snwpos'),acqDate)
    
    os.utime(patientFolder,None)
    for root, dirs, files in os.walk(patientFolder):
        os.utime(root,None)
        
        for f in files:            
            if f.endswith(RM_FILES):
                os.remove(os.path.join(root,f))
                continue

            fullPath=anonymizeFilePath( os.path.join(root,f),patientFolder)
            
            if f.endswith(TXT_FILES):
                anonymizeFile(fullPath,acqDate,firstTS)

#            picture = readImage(fullPath)
#            if picture:
#                anonymizeImage(picture, pixelsX=None, pixelsY=range(0,29), color=(80, 78, 71))
#                saveImage(fullPath, picture)
            #modify the file timestamp to current time
            os.utime(fullPath,(0,0))
         


def isCxFolder(folder):
    if len(folder)<4 or not folder[-4:]=='.cx3':
        return False
    if not os.path.exists(os.path.join(folder, 'custusdoc.xml')):
        return False
    return True

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
    