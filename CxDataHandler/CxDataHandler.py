# Time-stamp: <Last changed 07-11-2014 08:31:52 by Daniel H0yer Iversen, dahoiv>
from os import listdir
from os.path import isfile
from xml.dom import minidom
import matplotlib.animation as animation
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import sys
import warnings
import zlib

# CxFileHandler
#   - CxAcqFileHandler
#        -  tpFile
#        -  tsFile
#             -  ttsFile
#             -  ftsFile
#        -  Probedata
#        -  UsData
#             - Bandwidth
#             - Frequency
#             - Scanconverted
#             - Tissue
#             - Velocity
#   - CxImagesHandler      (not implemented)
#        - RecVolume       (not implemented)
#        - MeshModel       (not implemented)
#        - CenterLine      (not implemented)

# CxTransformsHandler
#   - prMt
#   - sMt  (not implemented)
#   - rMpr (not implemented)
#   - rMd  (not implemented)


class CxFileHandler(object):
    def __init__(self, file_path,newFile=False):
        self._file_path = file_path
        if not isfile(file_path) and not newFile:
            raise RuntimeError('No file found: %s' % file_path)
        if not newFile:
            self._data=self.read_data()
        else:
            self._data=None

    def read_data(self):
        raise RuntimeError('Should be implemented in child class')

    def get_file_path(self):
        return self._file_path

    def get_folder_name(self):
        return self._file_path.split(os.sep,-1)[-2]

    def copy_to(self,path,overwrite=False):
        if not overwrite and isfile(path) :
            warnings.warn("File already exists, and overwrite=False" )
        else:
            shutil.copy2(self._file_path, path)

class CxAcqFileHandler(CxFileHandler):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder,data_type):
        raise RuntimeError('Should be implemented in child class')

    @classmethod
    def get_filepath_from_data_type(CxFileHandler,acq_folder,data_type,fileending):
        return get_filepath_from_data_type(acq_folder,data_type,fileending)

class tpFile(CxAcqFileHandler):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder,data_type):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,data_type,'.tp')
        return CxFileHandler(filepath,False)


    def get_tp_nr(self,nr):
        if nr <0 or nr >self.get_no_of_tp():
            raise RuntimeError('No tp matrix found for nr= %s' % str(nr))
        temp=self._data[nr,:].reshape(3,4)
        res=np.append(temp,[0, 0, 0, 1]).reshape(4,4)
        return res


    def get_no_of_tp(self):
	return len(self._data)

    def add_tp(self,mat):
        mat=mat.reshape(16,1)
        mat=mat[0:12]
        mat=mat.transpose()
        if self._data==None or len(self._data)==0:
            self._data=mat
        else:
            self._data= np.vstack((self._data,mat))

    def add_tps(self,mat):
        if self._data==None or len(self._data)==0:
            self._data=mat
        else:
            self._data= np.vstack((self._data,mat))

    def read_data(self):
        file_path=self.get_file_path()
        file = open(file_path)
        mat = np.fromstring(file.read(),sep=' ')
        mat = mat.reshape([len(mat)/12,12])
        return mat


    def save_to_file(self,overwrite=False):
        if not overwrite and isfile(self._file_path) :
            warnings.warn("File already exists, and overwrite=False" )
        else:
            mat=self._data.reshape([12/4*len(self._data),4])
            np.savetxt(self.get_file_path(),mat,fmt='%.7f')



class tsFile(CxAcqFileHandler):
    def get_ts(self):
        return self._data

    def get_ts_nr(self,nr):
        if nr <0 or nr >len(self._data):
            raise RuntimeError('No tts matrix found for nr= %s' % str(nr))
        return self._data[nr]

    def read_data(self):
        file_path=self.get_file_path()
        file = open(file_path)
        mat = np.fromstring(file.read(),sep=' ')
        return mat

    def add_ts(self,mat):
        if self._data==None :#or len(self._data)==0:
            self._data=np.array(mat)
        else:
            self._data= np.hstack((self._data,mat))

    def save_to_file(self,overwrite=False):
        if not overwrite and isfile(self._file_path) :
            warnings.warn("File already exists, and overwrite=False" )
        else:
            np.savetxt(self.get_file_path(),self._data,fmt='%.7f')


class ttsFile(tsFile):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder,data_type):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,data_type,'.tts')
        return CxFileHandler(filepath,False)

class ftsFile(tsFile):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder,data_type):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,data_type,'.fts')
        return CxFileHandler(filepath,False)



class Probedata(CxAcqFileHandler):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder,data_type):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,data_type,'.probedata.xml')
        return CxFileHandler(filepath,False)

    def read_data(self):
        file_path=self.get_file_path()
        return minidom.parse(file_path)

    def get_clipRect_p(self):
        item=self._data.getElementsByTagName('image')
        temp=item[0].attributes['clipRect_p'].value
        temp=temp.split()
        temp =[float(temp[0]),float(temp[1]),float(temp[2]),float(temp[3])]
        return temp


    def get_temporalCalibration(self):
        item=self._data.getElementsByTagName('configuration')
        temp=item[0].attributes['temporalCalibration'].value
        return float(temp)

    def get_width(self):
        item=self._data.getElementsByTagName('configuration')
        temp=item[0].attributes['width'].value
        return float(temp)

    def get_depthStart(self):
        item=self._data.getElementsByTagName('configuration')
        temp=item[0].attributes['depthStart'].value
        return float(temp)

    def get_depthEnd(self):
        item=self._data.getElementsByTagName('configuration')
        temp=item[0].attributes['depthEnd'].value
        return float(temp)

    def get_spacing(self):
        item=self._data.getElementsByTagName('image')
        temp=item[0].attributes['spacing'].value
        temp=temp.split()
        temp =[float(temp[0]),float(temp[1]),float(temp[2])]
        return temp


class UsData(CxAcqFileHandler):
    def __init__(self, mhd_file_path,newFile=False):
        self._no_of_frames=0
        self._ftsFile=None
        self._ttsFile=None
        self._tpFile=None
        self._prMt=None
        CxAcqFileHandler.__init__(self,mhd_file_path,newFile)

    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
        raise RuntimeError('Should be implemented in child class')


    def load_frame(self,frame_no):
        file_path=self.get_file_path()

        pd=self.get_probedata()
        clipRect=pd.get_clipRect_p()

        vtk = self.load_mhd(frame_no)

        if vtk is not None:
            data=vtk.get_samples()
            data=data[clipRect[0]:clipRect[1]+1,clipRect[2]:clipRect[3]+1]
            return data
        else:
            print "Could not find ",  file_path

        return None


    def load_mhd(self,frame_no):
        file_path=self.get_file_path()
        file_path_temp=file_path[0:-5]

        file_path=file_path_temp+str(frame_no)+'.mhd'
        if isfile(file_path):
            vtk=mhdFile(file_path)
            return vtk
        else:
            print "Could not find ",  file_path

        return None


    def get_mask(self):
        mask_file=self.get_file_path().replace('_0.mhd','.mask.mhd')
        vtk_mask=mhdFile(mask_file)
        mask=vtk_mask.get_samples()
        return mask

    def get_ftsFile(self):
        if self._ftsFile is None:
            fts_file=self.get_file_path().replace('_0.mhd','.fts')
            self._ftsFile=ftsFile(fts_file)
        return self._ftsFile

    def get_ttsFile(self):
        if self._ttsFile is None:
            tts_file=self.get_file_path().replace('_0.mhd','.tts')
            self._ttsFile=ftsFile(tts_file)
        return self._ttsFile

    def get_tpFile(self):
        if self._tpFile is None:
            tp_file=self.get_file_path().replace('_0.mhd','.tp')
            self._tpFile=tpFile(tp_file)
        return self._tpFile


    def get_prMt(self):
        if self._prMt is None:
            self._prMt=prMt(self.get_tpFile(),self.get_ttsFile())
        return self._prMt


    def get_probedata(self):
        probedata_file=self.get_file_path().replace('_0.mhd','.probedata.xml')
        return Probedata(probedata_file)

    def GetDimSize(self,frameNo):
        return self._data[:,:,frameNo].shape

    def read_data(self):
        file_path=self.get_file_path()
        file_path_temp=file_path[0:-5]

        k=1
        file_path=file_path_temp+str(k)+'.mhd'
        while isfile(file_path):
            k=k+1
            file_path=file_path_temp+str(k)+'.mhd'

        self._no_of_frames=k

        return None

    def get_no_of_frames(self):
        return self._no_of_frames

    def show_data(self,frame_no):
        data=self.load_frame(frame_no)
        plt.imshow(data.transpose(), cmap = cm.Greys_r)
        plt.show()

    def show_datas(self):
        def updatefig(frame_no):
            # set the data in the axesimage object
            im.set_array(self.load_frame(frame_no).transpose())
            # return the artists set
            return im,

        fig = plt.figure() # make figure

        im = plt.imshow(self.load_frame(0).transpose(), cmap= cm.Greys_r)

        ani = animation.FuncAnimation(fig, updatefig, frames=range(self.get_no_of_frames()),
                              interval=1, blit=True)
        plt.show()


class Bandwidth(UsData):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,'Bandwidth','_0.mhd')
        return CxFileHandler(filepath,False)


class ScanConverted(UsData):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,'ScanConverted','_0.mhd')
        return CxFileHandler(filepath,False)

class Tissue(UsData):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,'Tissue','_0.mhd')
        return CxFileHandler(filepath,False)

class cxOpenCV(UsData):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
        filepath=CxFileHandler.get_filepath_from_data_type(acq_folder,'cxOpenCV','_0.mhd')
        return CxFileHandler(filepath,False)


    def load_frame_angio_data(self,frame_no):
        rawData=self.load_frame(frame_no)
        index=nearly_equal(rawData)
        rawData=rawData=np.mean(rawData,axis=2)
        rawData[index]=0
        return rawData



class cxSearchMhd(UsData):
    @classmethod
    def from_acq_folder(CxFileHandler,acq_folder):
	if not acq_folder[-1]==os.sep:
            acq_folder=acq_folder+os.sep
        for filename in os.listdir(acq_folder):
            if filename.endswith('_0.mhd'):
                filepath=acq_folder+filename
                print filepath
                return CxFileHandler(filepath,False)

    

#end Files

###########

class CxAcqFolderHandler():
    def __init__(self, folder_path):
        self.folder_path=folder_path

        filepath=get_filepath_from_data_type(folder_path,'Bandwidth','_0.mhd')
        if isfile(filepath):
            self.Bandwidth= UsData(filepath)
        else:
            self.Bandwidth=None

        filepath=get_filepath_from_data_type(folder_path,'ScanConverted','_0.mhd')
        if isfile(filepath):
            self.ScanConverted= UsData(filepath)
        else:
            self.ScanConverted=None

        filepath=get_filepath_from_data_type(folder_path,'Tissue','_0.mhd')
        print filepath
        if isfile(filepath):
            self.Tissue= UsData(filepath)
        else:
            self.Tissue=None

        filepath=get_filepath_from_data_type(folder_path,'cxOpenCV','_0.mhd')
        if isfile(filepath):
            self.cxOpenCV= UsData(filepath)
        else:
            self.cxOpenCV=None





##########

class CxTransformsHandler(object):
    pass

class prMt(CxTransformsHandler):
    def __init__(self,tp,tts):
        self.tp=tp
        self.tts=tts

    @classmethod
    def from_tp_tts_files(self,tp_file_path,tts_file_path):
        tp=tpFile(tp_file_path)
        tts=ttsFile(tts_file_path)
        return prMt(tp,tts)

    @classmethod
    def from_acq_folder(self,acq_folder,data_type):
        tp=tpFile.from_acq_folder(acq_folder,data_type)
        tts=ttsFile.from_acq_folder(acq_folder,data_type)
        return prMt(tp,tts)

    def get_transform(self,time):

        tts_ts=self.tts.get_ts()

        temp=abs(tts_ts-time)
        iT1=temp.argmin() #finding the time closest to requested time
        t1=tts_ts[iT1]

        temp[iT1]=np.Inf
        iT2 = temp.argmin() #finding the time next closest to requested time
        t2=tts_ts[iT2]

        prMt= (-self.tp.get_tp_nr(iT1)*(time-t2)+self.tp.get_tp_nr(iT2)*(time-t1))/(t2-t1)
        return prMt


    def get_tp_file_path(self):
        return self.tp.get_file_path()


    def get_tts_file_path(self):
        return self.tts.get_file_path()






#end Transforms

class vtkFileReader(object):
    def __init__(self, vtk_file):
        if not isfile(vtk_file):
            raise RuntimeError('Vtk file %s does not exists.' % vtk_file)

        self.vtk_file = vtk_file

        #.vtk mesh
        self.patches=[]
        self.nodes=[]
        self.num_nodes=-1
        self.num_patches=-1


        self.read_data(vtk_file)



    def read_data(self,vtk_file):
        file = open(vtk_file)

        file.readline() # vtk DataFile Version x.x
        file.readline() # comments
        assert file.readline()=="ASCII\n", "Unsupported vtk file, must be ASCII on line 3"
        assert file.readline()=="DATASET POLYDATA\n", "Unsupported vtk file, must be DATASET STRUCTURED_POINTS on line 4"

        line=file.readline()
        temp=line.split(" ")

        self.num_nodes=int(temp[1])

        nodes=[]
        j=0
        while j <self.num_nodes:
            line=file.readline()
            line=line[0:len(line)-2].split(' ')
            L=len(line)/3
            node=[]
            for temp in line:
                node.append(float(temp))
                if len(node)==3:
                    nodes.append(node)
                    node=[]

            j=j+L
        self.nodes=nodes

        line=file.readline()
        temp=line.split(" ")
        if not temp[0] =="POLYGONS":
            line=file.readline()
            temp=line.split(" ")
        assert temp[0] =="POLYGONS", "Unsupported vtk file, must be POLYGONS"

        self.num_patches=int(temp[1])
        patches=[]
        j=0
        while j < self.num_patches:
            line=file.readline()
            line=line[2:len(line)-2].split(' ')

            patch=[]
            for temp in line:
                patch.append(int(temp))

            patches.append(patch)
            patch=[]

            j=j+1
        self.patches=patches

    def get_nodes(self):
        if len(self.nodes)>0:
            return self.nodes
        else:
            warnings.warn('No nodes')
            return

    def get_patches(self):
        if len(self.patches)>0:
            return self.patches
        else:
            warnings.warn('No patches')
            return

    def get_num_nodes(self):
        if self.num_nodes>0:
            return self.num_nodes
        else:
            warnings.warn('No nodes')
            return

    def get_num_patches(self):
        if self.num_patches>0:
            return self.num_patches
        else:
            warnings.warn('No patches')
            return


class mhdFile(CxFileHandler):
    def __init__(self, mhd_file,newFile=False):

        self.Params=Ordered_dict()
       

        self.color=False

        CxFileHandler.__init__(self,mhd_file,newFile)


    def read_data(self):
        file = open(self._file_path)
        j=0
        self.ElementNumberOfChannels=0
        for line in file.readlines():

            if line.count('ObjectType')==1:
                j=j+1;
                temp=line.split()
                self.Params['ObjectType'] = temp[-1]
                
            elif line.count('NDims')==1:
                j=j+1;
                temp=line.split()
                self.Params['NDims']=int(temp[-1])
                
            elif line.count('BinaryData ')==1:
                j=j+1;
                temp=line.split()
                self.Params['BinaryData']= temp[-1]=='True'
                
            elif line.count('BinaryDataByteOrderMSB ')==1:
                j=j+1;
                temp=line.split()
                self.Params['BinaryDataByteOrderMSB']= temp[-1]=='True'
                
            elif line.count('CompressedData ') ==1 :
                temp=line.split()
                self.Params['CompressedData']= temp[-1]=='True'
                
            elif line.count('CompressedDataSize')==1:
                temp=line.split()
                self.Params['CompressedDataSize']= int(temp[-1])
                
            elif line.count('CenterOfRotation')==1:
                j=j+1;
                temp=line.split()

                if len(temp)==4:
                    self.Params['CenterOfRotation']=[float(temp[2]),float(temp[3])]
                elif len(temp)==5:
                    self.Params['CenterOfRotation']=[float(temp[2]),float(temp[3]),float(temp[4])]
                
            elif line.count('ElementSpacing')==1:
                j=j+1;
                temp=line.split()
                if len(temp)==4:
                    self.Params['ElementSpacing']=[float(temp[2]),float(temp[3])]
                elif len(temp)==5:
                    self.Params['ElementSpacing']=[float(temp[2]),float(temp[3]),float(temp[4])]
                
            elif line.count('DimSize')==1:
                j=j+1;
                temp=line.split()
                if len(temp)==4:
                    self.Params['DimSize']=[int(temp[2]),int(temp[3])]
                elif len(temp)==5:
                    self.Params['DimSize']=[int(temp[2]),int(temp[3]),int(temp[4])]
                    
            elif line.count('AnatomicalOrientation')==1:
                j=j+1;
                temp=line.split()
                self.Params['AnatomicalOrientation']=temp[-1]
                
            elif line.count('ElementSize')==1:
                j=j+1;
                temp=line.split()
                self.Params['ElementSize']=[float(temp[2]),float(temp[3])]
                
            elif line.count('ElementType')==1:
                j=j+1;
                temp=line.split()
                self.Params['ElementType']=temp[-1]
                
            elif line.count('TransformMatrix')==1:
                j=j+1
                temp=line.split()
                temp=temp[2:(len(temp))]
                TransformMatrix =[]
                for x in temp:
                    TransformMatrix.append(float(x))
                self.Params['TransformMatrix']=TransformMatrix
                
            elif line.count('Offset')==1:
                j=j+1
                temp=line.split()
                if len(temp)==4:
                    self.Params['Offset']=np.array([float(temp[2]),float(temp[3])])
                elif len(temp)==5:
                    self.Params['Offset']=np.array([float(temp[2]),float(temp[3]),float(temp[4])])
                else:
                    warnings.warn('Unsupported mhd file')
                    
            elif line.count('Modality')==1:
                j=j+1;
                temp=line.split()
                self.Params['Modality']=temp[-1]
                
            elif line.count('ImageType3')==1:
                j=j+1;
                temp=line.split()
                self.Params['ImageType3']=temp[-1]
                
            elif line.count('ElementDataFile')==1:
                j=j+1
                temp=line.split()
                self.Params['ElementDataFile']=temp[len(temp)-1]

            elif line.count('ElementNumberOfChannels') ==1:
                temp=line.split()
                self.Params['ElementNumberOfChannels']= temp[-1]
                if  self.Params['ElementNumberOfChannels']>0:
                    self.color=True

        # if j < 6:
        #      warnings.warn('Some parameters not found')
    

    def get_spacing(self):
        if not self.Params.has_key('ElementSpacing'):
            warnings.warn('No spacing')
            return
        else:
            return self.Params['ElementSpacing']

    def get_orientation(self):
        if not self.Params.has_key('Offset'):
            warnings.warn('No orientation')
            return
        else:
            return self.Params['Offset']

    def get_samples(self):
        rawFile=self.loadRawFile()
        return rawFile.get_samples()

    def get_modality(self):
        if not self.Params.has_key('Modality'):
            warnings.warn('No Modality')
            return
        else:
            return self.Params['Modality']   
        
    def get_DimSize(self):
        if not self.Params.has_key('DimSize'):
            warnings.warn('No DimSize')
            return
        else:
            return self.Params['DimSize']

                        
    def get_ElementType(self):
        if not self.Params.has_key('ElementType'):
            warnings.warn('No elementtype')
            return
        else:
            return self.Params['ElementType']

    def get_rMd(self):
        if not self.Params.has_key('ElementType'):
            warnings.warn('no matrix')
            return
        if not self.Params.has_key('Offset'):
            warnings.warn('no matrix')
            return
            
        tm=np.array(self.Params['TransformMatrix']).reshape(3,3)
        om=np.array(self.Params['Offset']).reshape(3,1)
        rMd=np.hstack((tm,om))
        rMd=np.vstack((rMd, np.array([0, 0, 0, 1]).reshape(1,4)))
        return rMd
        
            
        

        
    def getFilePath(self):
        return self._file_path

    def isRawCompressed(self):
        return self.Params['ElementDataFile'][-5:]=='.zraw'

    def getRawFilePath(self):
        temp=self._file_path.split(os.sep)
        return self._file_path.replace(temp[-1],self.Params['ElementDataFile'])


        
    def loadRawFile(self):
        return rawFileReader(self.getRawFilePath(),self.get_DimSize(),self.color,self.get_ElementType())

    def loadRawData_removeRect(self,color=[255,255,131],tol=4):
        samples=self.get_samples()
        temp=   np.abs(samples -np.array(color).reshape(1,1,3))
        a=np.max(temp,axis=2)
        samples[a<=tol ]=np.array([0,0,0] ).reshape(1,3)
        return samples


    def save_to_new_file(self,file_path_new,overwrite=False):
        if not overwrite and isfile(file_path_new) :
            warnings.warn("File already exists, and overwrite=False" )
        else:
            #old_file = open(self._file_path,'r')
            buffer=''
            for key,val in self.Params.ordered_items():
                
                
                buffer += key + ' = ' + str(val).replace('[','').replace(']','').replace(',','')+ os.linesep

                
        
            #             for line in old_file.readlines():
            #     if line.count('ElementDataFile')==1:
            #         temp=line.split()
            #         newline=line.replace(temp[len(temp)-1],self.ElementDataFile)
            #     elif line.count('ElementNumberOfChannels')==1:
            #         temp=line.split()
            #         newline=line.replace(temp[len(temp)-1],str(self.ElementNumberOfChannels))
            #     elif line.count('CompressedData ')==1:
            #         temp=line.split()
            #         if self.CompressedData:
            #             newline=line.replace(temp[len(temp)-1],'True')
            #         else:
            #             newline=line.replace(temp[len(temp)-1],'False')
            #     elif line.count('CompressedDataSize')==1:
            #         temp=line.split()
            #         if self.CompressedData:
            #             filepath=file_path_new[:-3]+'zraw'
            #         else:
            #             filepath=file_path_new[:-3]+'raw'
            #         newline=line.replace(temp[len(temp)-1], str(os.path.getsize(filepath)))
            #     else:
            #         newline=line
            #     buffer+=newline

            # old_file.close()

            new_file = open(file_path_new,'w')
            new_file.write(buffer)
            new_file.close()


class mhdFileReader(mhdFile):
    pass 
    #backward compatibility


class rawFileReader(object):
    def __init__(self, raw_file,DimSize,color=False,ElementType='MET_UCHAR'):
        f = open(raw_file, 'rb')
        samples = f.read()

        if raw_file[-5:]=='.zraw':
            samples = zlib.decompress(samples)

        if ElementType=='MET_UCHAR':
            dtype='uint8'
        elif ElementType=='MET_SHORT':
            dtype='int16'
        elif ElementType=='MET_USHORT':
            dtype='uint16'
        elif ElementType=='MET_FLOAT':
            dtype='float32'
        else:
            print "unknown dtype", ElementType

        samples = np.fromstring(samples, dtype=dtype)
     
        if color:
            samples = samples.reshape(np.hstack((3, DimSize)), order='F')
            samples = np.transpose(samples,(1,2,0))
        else:
            if len(DimSize)>2:
                samples = samples.reshape([DimSize[2],DimSize[0],DimSize[1]], order='C')
                samples = np.transpose(samples,(1,2,0))

            else:
                samples = samples.reshape(DimSize, order='F')




        ### Maa bruke order='F' (column-major) for aa faa det til aa virke
        ### Basert paa http://stackoverflow.com/questions/8380780/vtk-data-format-error:
        ###    "the data should be written in column major order, not row major.
        ###     This is a point in which the VTK file formats document is lacking."
        self._samples=samples

    def get_samples(self):
        return self._samples



class rawFileWrither(object):
    def __init__(self, raw_file,samples,color=False,ElementType='MET_UCHAR'):

        samples = np.asarray(samples)
        #high_values_indices = samples > 255  # Where values are to high
        #samples[high_values_indices] = 255  

        #if np.amax(samples) > 255:
        #    warnings.warn('Some values are greater than 255, will be flipped: '+ str(np.amax(samples)))

        if ElementType=='MET_UCHAR':
            dtype='uint8'
        elif ElementType=='MET_SHORT':
            dtype='int16'
        elif ElementType=='MET_USHORT':
            dtype='uint16'
        elif ElementType=='MET_FLOAT':
            dtype='float32'
        else:
            print "unknown dtype", ElementType

        if color:
            warnings.warn("NOT TESTED" )
            samples = np.transpose(samples,(0,1,2))
            samples =np.fliplr(samples)


	elif len(samples.shape)>2:
            samples = np.transpose(samples,(2,0,1))
        else:
            samples = np.transpose(samples,(1,0))
            
        samples=np.array(samples,dtype=dtype,order='C')


        if raw_file[-5:]=='.zraw':
            samples = zlib.compress(samples)

        f = open(raw_file, 'wrb')
        f.write(samples)
        f.close()



###end vtk


def get_filepath_from_data_type(acq_folder,data_type,fileending):
    if not acq_folder[-1] == os.sep:
        acq_folder = acq_folder+ os.sep
    temp=acq_folder.split(os.sep)
    fileSeg=temp[-2].split('_')

    files = [file for file in listdir(acq_folder) if file.lower().endswith('.fts')]
    fileSeg1=files[0].split('_')

    file=fileSeg1[0]+'_'+fileSeg[1]+'_'+fileSeg[2]

    filename=file+'_'+data_type+fileending

    return acq_folder+filename


class Ordered_dict(dict):
        def __init__(self, *args, **kwargs):
                dict.__init__(self, *args, **kwargs)
                self._order = self.keys()

        def __setitem__(self, key, value):
                dict.__setitem__(self, key, value)
                if key in self._order:
                        self._order.remove(key)
                self._order.append(key)

        def __delitem__(self, key):
                dict.__delitem__(self, key)
                self._order.remove(key)

        def order(self):
                return self._order[:]

        def ordered_items(self):
                return [(key,self[key]) for key in self._order] 



def nearly_equal(vals,tol=5):
    a=np.max(vals,axis=2)
    b=np.min(vals,axis=2)
    return a-b < tol



if __name__ == '__main__':
    if len(sys.argv) < 2:
		acq_folder2 = '/home/dahoiv/Dokumenter/nav_doppler/data/Carotis/Carotis_Navigasjon_150514/2013-05-15_10-53_Carotis_2_37.cx3/US_Acq/US_08_20130515T114444'
		acq_folder = '/media/dahoiv/BackupDHI2/data_backup/2013-03-18_13-54_ProbeCalibartion_GEML6-15.cx3/US_Acq/Cal-1_25_20130318T135638'
    else:
        acq_folder = sys.argv[1]
        acq_folder2 = sys.argv[2]


    # raw=ScanConverted.from_acq_folder(acq_folder)
    # #raw.show_data(23)
    # mhd=raw.load_mhd(10)
    # print mhd.getFilePath()
    # mhd.save_to_new_file('/home/dahoiv/test.mhd',overwrite=True)

    # file='test.raw'
    NoOfSamples=[10,5,3]

    # xx, yy = np.mgrid[:20, :20]
    # # circles contains the squared distance to the (100, 100) point
    # # we are just using the circle equation learnt at school
    # circle = (xx - 5) ** 2 + (yy - 5) ** 2
    # # donuts contains 1's and 0's organized in a donut shape
    # # you apply 2 thresholds on circle to define the shape
    # donut = np.logical_and(circle < (10), circle < (10))


    
    # samples=np.random.randint(255, size=NoOfSamples)*0

    # samples[circle<10]=10

    # rawWrither = rawFileWrither(file,samples)


    # rawReader =  rawFileReader(file,NoOfSamples)
    # samples2 = rawReader.get_samples()


    
    # print np.linalg.norm(samples2-samples) 
    filePath='test.raw'
    samples=np.random.randint(255, size=NoOfSamples)
    rawWrither = rawFileWrither(filePath,samples)


    rawReader =  rawFileReader(filePath,NoOfSamples)
    samples2 = rawReader.get_samples()


    
    print samples[:,:,2]-samples2[:,:,2]
    print np.linalg.norm(samples-samples2) 

    
    #exit()
    
    result=True

    try :
        probedata=Probedata.from_acq_folder(acq_folder,'ScanConverted')
        print probedata.get_temporalCalibration()
        print probedata.get_spacing()
        print probedata.get_width()
        print probedata.get_depthStart()
        print probedata.get_depthEnd()
    except Exception as inst:
        print inst.args
        print 'Failed to read probeData'
        result=False

    try :
        prMt=prMt.from_acq_folder(acq_folder,'ScanConverted')
    except Exception as inst:
        print inst.args
        print 'Failed to read prMt'
        result=False

    try :
        fts= ftsFile.from_acq_folder(acq_folder,'ScanConverted')
    except Exception as inst:
        print inst.args
        print 'Failed to read fts'
        result=False

    try :
        tp= tpFile.from_acq_folder(acq_folder,'ScanConverted')
    except Exception as inst:
        print inst.args
        print 'Failed to read tp'
        result=False

    try :
        tts=ttsFile.from_acq_folder(acq_folder,'ScanConverted')
    except Exception as inst:
        print inst.args
        print 'Failed to read tts'
        result=False

    try :
        times = tts.get_ts()
        for i in range(0,len(times)):
            assert np.linalg.norm((prMt.get_transform(times[i]))-tp.get_tp_nr(i)) < 10**-13
    except Exception as inst:
        print inst.args
        result=False

    try :
        raw=Bandwidth.from_acq_folder(acq_folder)
        raw.show_data(40)
    except Exception as inst:
        print inst.args
        print 'Failed to read bandwidth data'
        result=False


    try :
        raw=ScanConverted.from_acq_folder(acq_folder)
        pd=raw.get_probedata()
        print pd.get_spacing()
        raw.show_data(40)
    except Exception as inst:
        print inst.args
        print 'Failed to read ScanConverted data'
        result=False


    try :
        raw=cxOpenCV.from_acq_folder(acq_folder2)
        raw.show_data(40)
    except Exception as inst:
        print inst.args
        print 'Failed to read cxOpenCV data'
        result=False


    try :
        filePath = 'temp.raw'
        NoOfSamples=[100,10]
        for k in range(0,5):

            samples=np.random.randint(255, size=NoOfSamples)
            rawWrither = rawFileWrither(filePath,samples)


            rawReader =  rawFileReader(filePath,NoOfSamples)
            samples2 = rawReader.get_samples()

            assert np.linalg.norm(samples2-samples) == 0

    except Exception as inst:
        print inst.args
        print 'Failed writing/reading uncompressed data'
        result=False

    try :
        filePath = 'temp.zraw'
        NoOfSamples=[100,10]
        for k in range(0,5):

            samples=np.random.randint(255, size=NoOfSamples)
            rawWrither = rawFileWrither(filePath,samples)


            rawReader =  rawFileReader(filePath,NoOfSamples)
            samples2 = rawReader.get_samples()

            assert np.linalg.norm(samples2-samples) == 0

    except Exception as inst:
        print inst.args
        print 'Failed writing/reading ncompressed data'
        result=False

            
    try :
        filePath = 'temp.raw'
        NoOfSamples=[100,10,5]
        for k in range(0,5):

            samples=np.random.randint(255, size=NoOfSamples)
            rawWrither = rawFileWrither(file,samples)


            rawReader =  rawFileReader(filePath,NoOfSamples)
            samples2 = rawReader.get_samples()

            assert np.linalg.norm(samples2-samples) == 0

    except Exception as inst:
        print inst.args
        print 'Failed writing/reading uncompressed 3-D data'
        result=False

    try :
        filePath = 'temp.zraw'
        NoOfSamples=[100,10,5]
        for k in range(0,5):

            samples=np.random.randint(255, size=NoOfSamples)
            rawWrither = rawFileWrither(filePath,samples)


            rawReader =  rawFileReader(filePath,NoOfSamples)
            samples2 = rawReader.get_samples()

            assert np.linalg.norm(samples2-samples) == 0

    except Exception as inst:
        print inst.args
        print 'Failed writing/reading compressed 3-D data'
        result=False

    if result:
        print('Passed all tests')
