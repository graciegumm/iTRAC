import iTRAC as it
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
import glob


#replace with your filepath
data = pd.read_csv('/home/ggrumm/Documents/iTRAC-Gracie/2021-08-06-10-31-30_2T3H1RFV8LC057037_CAN_Messages.csv')

#replace with your filepath
db2 = s.initializeDBC_Cantools('/home/ggrumm/strym/strym/dbc/toyota_rav4_hybrid.dbc')


radarData = it.allRadar(data)
G = it.myGraph(radarData,dt=0.5)
p = it.SSP(G.G)
dfs = it.getPathDfs(p, G)




