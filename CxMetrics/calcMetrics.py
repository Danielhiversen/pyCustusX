# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 11:39:42 2015

@author: dahoiv
"""

import numpy as np

def loadMetrics(filepath):
    mr_points=dict()
    us_points=dict()
    with open(filepath, 'r') as file :
        for line in file.readlines():
            line = line.translate(None, '"')
            
            data=  line.split()
            if not "pointMetric" in data[0]:
                continue
            key= data[1][-2:]
            point = data[6:9]
            if "_mr_" in data[1] and not "us" in data[2].lower():
                mr_points[key]=[float(point[0]),float(point[1]),float(point[2])]
            if "_us_" in data[1] and "us" in data[2].lower():
                us_points[key]=[float(point[0]),float(point[1]),float(point[2])]
    return (mr_points,us_points)
                
def calcDist(mr_points,us_points):
    k=0
    dist=[]
    for key in mr_points.keys():
        if not key in us_points.keys():
            print key, "  missing in us"
            continue
        diff = np.array(mr_points[key])-np.array(us_points[key])
        dist.append((diff[0]**2 +diff[1]**2 +diff[2]**2)**0.5)
        print key, dist[-1]
        k=k+1
    print "mean; ", np.mean(dist)
    print "var: ", np.var(dist)
            
if __name__ == '__main__':   
    filePath1="/home/dahoiv/disk/data/brainshift/079_Tumor.cx3/Logs/metrics_a.txt"
    (mr_points_1,us_points_1)=loadMetrics(filePath1)    
    calcDist(mr_points_1,us_points_1)
    
    
    filePath2="/home/dahoiv/disk/data/brainshift/079_Tumor.cx3/Logs/metrics_b.txt"
    (mr_points_2,us_points_2)=loadMetrics(filePath2)
    calcDist(mr_points_2,us_points_2)
    