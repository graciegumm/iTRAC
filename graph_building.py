#!/usr/bin/env python
# coding: utf-8

# Author : Matthew Nice
# Initial Date: Feb 21, 2021
# About: graph building is for the class(es) and related functions used to make radar detections into graphs, and pulling out their data.
# Read associated README for full description
# License: MIT License

#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:

#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
#   ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
#   TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
#   SHALL THE AUTHORS, COPYRIGHT HOLDERS OR ARIZONA BOARD OF REGENTS
#   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#   AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#   OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Mathew Nice'
__email__  = 'matthew.nice@vanderbilt.edu'

## general import for data manipulation, file gathering

import numpy as np
import matplotlib.pyplot as pt
import csv
import pandas as pd
import cantools
import matplotlib.animation as animation
from matplotlib import style
from haversine import haversine, Unit
import itertools
import math
import strym as s
import networkx as nx
import os


try:
    db2 = s.initializeDBC_Cantools('/strym/strym/dbc/toyota_rav4_hybrid.dbc')
    print('Loaded DBC from: /strym/strym/dbc/toyota_rav4_hybrid.dbc')
except:
    print('make sure to import and/or locate your dbc file')

def setDBC(filePath):
    '''Initialize the DBC from strym, give the filepath to your dbc file.'''
    db2 = s.initializeDBC_Cantools(filePath)

def search_files(directory='.', extension=''):
    '''Search for files below directory that contain the extension.'''
    extension = extension.lower()
    matches = []
    for dirpath, dirnames, files in os.walk(directory):
        for name in files:
            if extension and name.lower().endswith(extension):
                matches.append(os.path.join(dirpath, name))
            elif not extension:
                matches.append(os.path.join(dirpath, name))
    return matches


def trackRadar(i,data):
    '''Pull in all the relevant radar signals from a Toyota radar CAN data csv file.\
     This function gets everything from a single "track" on a Toyota'''
    lon = s.convertData(i,1,data,db2)
    lat = s.convertData(i,2,data,db2)
    lat = lat.reset_index(drop=True)

    relv = s.convertData(i,4,data,db2)
    relv=relv.reset_index(drop=True)

    score = convertData(i+16,'SCORE',data,db2)
    score = score.reset_index(drop=True)

    lon = lon.rename(columns={"Message": "Longitude"})
    lon = lon.reset_index(drop=True)

    rel_accel = s.convertData(i+16,'REL_ACCEL',data,db2)
    rel_accel = rel_accel.reset_index(drop=True)
    lon['rel_accel'] = rel_accel.Message

    lon['Latitude'] = lat.Message
    lon['Relv'] = relv.Message
    lon['Score'] = score.Message

    lon['Track'] = i

    lon1 = lon.loc[
        lon.Longitude <= 330
    ]
    return lon1


def allRadar(data):
    '''With a CSV file as input, this function outputs the complete set of \
    radar detections from a Toyota RAV4. Sorted by Time by default.'''
    bigFrame = pd.DataFrame()

    for i in range(384,400):
        temp = trackRadar(i,data)
        bigFrame = pd.concat([temp,bigFrame])

    bigFrame = bigFrame.sort_values(by='Time')
    return bigFrame

class Detection():
    """This class is to create an object for each radar detection in the data."""

    newid = itertools.count()
    beta_i = 0.02 #rate of false positives in sensor (arbitrary at the moment)


    def __init__(self,datapoint):
        self.x = datapoint.Longitude
        self.y = datapoint.Latitude
        self.rv = datapoint.Relv
        self.a = datapoint.rel_accel
        self.t = datapoint.Time
        self.cost = math.log(self.beta_i/(1-self.beta_i),10)
        self.id = Detection.newid.__next__()
        self.score = datapoint.Score
        self.track =  datapoint.Track
#         self.next  = []
#         self.prev = []

    def getAll(self):
        print('ID: ',self.id,'\nTime: ',self.t, '\nLong: ',self.x,'\nLat: ',self.y,'\nRel_Vel: ',
              self.rv,'\nRel_Accel: ',self.a,'\nScore: ',self.score)

    def costij(self,v):
        dist = 5*np.sqrt((self.x-v.x)**2+2*(self.y-v.y)**2)
        rvdist = 1000*abs(self.rv-v.rv)**2

        extra = 0
        if abs(self.x-v.x) > 10:
            extra = 1000*abs(self.x-v.x)

        return dist + rvdist + extra

    def add_arcij(self,v):
        G_arr[self.id,v.id] == 1

    def rm_arcij(self,v):
        G_arr[self.id,v.id] == 0


class myGraph():
    """This class is to create graphs from CAN radar detections using NetworkX and the Detection class.
    These graphs can be analyzed to track the objects being tracked in the radar data. Tip: remove invalid
    radar values above 327m to improve speed. Larger datasets have increased time to finish."""


    def __init__(self,datapoints,dt = 0.5):
        self.datapoints = datapoints

        self.G = nx.DiGraph()
        self.G.add_node("s", demand=-1)
        self.G.add_node("t", demand=1)
        self.delta_t_max = dt
        self.create()

    def change_dt(self,newDT):
        self.delta_t_max = newDT
        self.create()

    def get_dt(self):
        return self.delta_t_max

    def create(self):
        self.G.clear()
        count = -1
        for i in self.datapoints.iterrows(): #for each datapoint
            count +=1
            v = Detection(i[1]) #make a detection object
            self.G.add_node(v.id,obj=v) #add the node from the datapoint
            self.G.add_edge('s',v.id,weight=0) #add the edge from s
            self.G.add_edge(v.id,'t',weight=0) #add the edge from t

            if count > 0: #if not first, add edges from older vertices
    #                 print(v.id)
                v = self.G.nodes[v.id]['obj']
    #             delta_t = 0
    #             print(v.id)
                n = 1
                u = self.G.nodes[v.id-n]['obj']
                delta_t = u.t-v.t
                while delta_t < self.delta_t_max:
    #                 print(delta_t)

                    self.G.add_edge(v.id-n,v.id,weight=v.costij(u)+v.cost )
    #                 (10*np.sqrt(abs(delta_t)))
                        #add the edge(s) from nearby detections
                        #cost is euclidean distance + log likelihood real detection + 10*sqrt(dt)
    #                     if n < v.id:
                    n+=1
                    try:
                        u = self.G.nodes[v.id-n]['obj']
                        delta_t = v.t-u.t
                    except:
                        delta_t = 100
    #                     elif n >= v.id-1:

#define a successive shortest path algorithm to extract the tracjectories
def SSP(H, s='s', t='t'):
    """Successive shortest path algorithm using Bellman-Ford. Robust to negative weights. Graph H, and the source and target
    nodes of the flow network are needed as inputs. """
    J = H.copy()

    ax1 = pt.subplot(121)
#     pt.ylim([0,180])
    ax2 = pt.subplot(122)
#     pt.ylim([0,180])

    paths = []
    path_cost = nx.shortest_path_length(J,s,t, weight='weight',method='bellman-ford')
#     print(path_cost)
    stop = False
    while (len(J.nodes) > 2 and path_cost < 0 and stop == False): #find a shortest path between s and t until they have all been removed
#         print('finding shortest path!')
#         print(path_cost)
        path_cost = nx.shortest_path_length(J,s,t, weight='weight',method='bellman-ford')
        if path_cost < 0:
            path = nx.shortest_path(J,s,t, weight='weight',method='bellman-ford')
            if len(path)< 40:
                stop = True
    #         print('found!')

    #         print(path_cost)
    #         print(path)

            paths.append(path)
#             mydf = getPath(path,J)

#             if len(path) > 40:
#                 print(len(path),path_cost)
#     #             pt.figure()

#                 ax1.plot(mydf.y,mydf.x ,ls='',marker='.',markersize=3)

#                 ax2.plot(mydf.t,mydf.x,ls='',marker='.',markersize=3)

#     #             pt.figure()


            for i in path:
    #             print(path)
    #             print()
                if i != 't' and i != 's':
    #                 print(H.nodes[i]['obj'].getAll())
    #                     if G.nodes[i]['obj'].x >=320:
    #                         print(G.nodes[i]['obj'].id,G.nodes[i]['obj'].t,G.nodes[i]['obj'].x,G.nodes[i]['obj'].y,G.nodes[i]['obj'].cost)
                    J.remove_node(i)
    return paths


def getPath(path, J):
    """This function takes a path and NetworkX graph, and outputs a df of the relevant data."""
    df = pd.DataFrame()
    for i in path:
        if i != 't' and i != 's':

            df = df.append(pd.DataFrame([[J.nodes[i]['obj'].t, J.nodes[i]['obj'].x, J.nodes[i]['obj'].y,\
                                          J.nodes[i]['obj'].rv, J.nodes[i]['obj'].a,J.nodes[i]['obj'].score,\
                                        J.nodes[i]['obj'].track]]\
                                        ,columns=['t','x','y','rv','a','s','track'],index = [J.nodes[i]['obj'].id]))


    return df

def getPathDfs(p):
    """This function gets a list of dataframes, each correstponding to a trajectory
    of a vehicle tracked from the drive with the ITCAN approach. p is the list of
     the lists of nodes in graph G which correspond to a vehicle's trajectory.
    It is the output from the SSP method."""

    dfs = []
    for i in p[0:len(p)-1]:
        print(len(dfs))
        mydf = getPath(i,F.G)
        dfs.append(mydf)

    return dfs
