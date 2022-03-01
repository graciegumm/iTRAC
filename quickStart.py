import iTRAC as it


#below is stuff I have added
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

import xlwt #for exporting as excel book
#end of stuff I have added


#replace with your filepath
data = pd.read_csv('/media/ggrumm/Extreme SSD/2021-08-04-14-53-43_2T3MWRFVXLW056972_CAN_Messages.csv')

#replace with your filepath
db2 = s.initializeDBC_Cantools('/home/ggrumm/strym/strym/dbc/toyota_rav4_hybrid.dbc')


radarData = it.allRadar(data)
G = it.myGraph(radarData,dt=0.5)
p = it.SSP(G.G)
dfs = it.getPathDfs(p, G) #added G as parameter
