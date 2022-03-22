#Initial import statements
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pandas import *
from matplotlib.pyplot import figure
import math

# Reads in the CSV files for the radar and CAN messages
radar = read_csv('output.csv') #Change to match the file name and location of the radar trajectories
can = read_csv('CAN_lead_dist_output.csv') #Change to match the file name and location of the lead distances recorded from CAN

# Stores relevant values in the radar and CAN data as lists
trajectory_number=radar['Trajectory_ID'].tolist()
trajectory_count = (len(np.unique(trajectory_number)))
trajectory_IDs = list(range(1, trajectory_count+1))
radar_timeraw = radar['t'].tolist()
radar_time = []
can_timeraw = can['Time'].tolist()
can_time = []
radar_dist_x = radar['x'].tolist()
can_dist = can['Message'].tolist()
radar_dist_y = radar['y'].tolist()

# Converts the times recorded such that the first time is set to zero
for t in radar_timeraw:
    time = t - 1628251713
    radar_time.append(time)
for t in can_timeraw:
    time = t - 1628251713
    can_time.append(time)

# Creates a list storing the magnitude of the radar distance, from the x and y components recorded
i = 0
radar_dist = []
while i < 18412:
    dist = math.sqrt(((radar_dist_x[i])**2) + ((radar_dist_y[i])**2))
    radar_dist.append(dist)
    i+=1
    
'''
From here on, the radar_dist will be primarily used, as this is the magnitude of the x and y components
of the radar distance.
'''

# Plots the radar distances (in lump) and the CAN lead distances as a function of time
fig = plt.figure(figsize=(17, 8))
plt.title("Comparision of ALL Radar Trajectory Distances and CAN Lead Distances")
plt.scatter(radar_time, radar_dist, marker='.',linewidths=0.1,label='Radar')
plt.scatter(can_time, can_dist, marker='.',linewidths=0.1,label='CAN')
plt.xlabel("Time (s)")
plt.ylabel("Lead Distance")
plt.legend()

'''
The following is an example of plotting a smaller subset of the data, based on desired times
'''
radar_time_s=radar_time[7100:18412]
can_time_s=can_time[248:814]
radar_dist_s=radar_dist[7100:18412]
can_dist_s=can_dist[248:814]

fig = plt.figure(figsize=(17, 8))
plt.title("Comparision of ALL Radar Trajectory Distances and CAN Lead Distances for Time Subset")
plt.scatter(radar_time_s, radar_dist_s, marker='.',linewidths=0.1,label='Radar')
plt.scatter(can_time_s, can_dist_s, marker='.',linewidths=0.1,label='CAN')
plt.xlabel("Time (s)")
plt.ylabel("Lead Distance")
plt.legend()

'''
The following subset of code creates nested lists that separate the lump radar data by each vehicle recorded,
such that each vehicle can be analyzed and plotted separately
'''
times = []
dists = []
indicies = []
for i in trajectory_IDs:
    individual_indicies = []
    for a in range(len(trajectory_number)):    
        if trajectory_number[a] == i:
            pos = a
            individual_indicies.append(a)
    indicies.append(individual_indicies)
for veh in indicies:
    individual_times = []
    individual_dists = []
    for index in veh:
        individual_times.append(radar_time[index])
        individual_dists.append(radar_dist[index])
    times.append(individual_times)
    dists.append(individual_dists)
    
'''
Now we have the following lists to work with each vehicle trajectory
times: a nested list of the times recorded for each vehicle, such that time[0] references trajectory 1,
       times[n-1] references trajectory n.
dists: a nested list of the MAGNITUDE of the distance recorded for each vehicle (sqrt(x^2 + y^2)), such
       that dist[0] references trajectory 1, dists[n-1] references trajectory n.
indicies: a nested list of the indicies recorded for each vehicle, such that indicies[0] references 
          trajectory 1, and is a list of all the indicies of data stores for veh 1 from the full set of data.

Although the indicies list may not be used for plotting, having these three nested lists are useful when looking
to analyze a vehicle that the radar tracked separately.

An example of using this notation to plot data is shown below
'''

# veh_list needs to be modified for what you want to plot. Input the index of each trajectory you want to plot
# For instance, to plot Trajectory 1 only, veh_list=[0]. To plot Trajectories 2 and 7, veh_list=[1,6].
veh_list = [5,6,7,8,9,10]

# Plots the radar distances for each vehicle's index listed in veh_list and the CAN lead distances as a function of time
fig = plt.figure(figsize=(17, 8))
plt.xlabel("Time (s)")
plt.ylabel("Lead Distance")
plt.title("Comparision of INDIVIDUAL Radar Trajectory Distances and CAN Lead Distances")
plt.scatter(can_time, can_dist, marker='.',linewidths=0.1,label='CAN')
for veh in veh_list:
    plt.scatter(times[veh], dists[veh], marker='.',linewidths=0.1,label='Radar #{}'.format(veh+1))
plt.legend()
