import strym
from strym import strymread

csvfile = '' #Input file name
dbcfile = 'toyota_rav4_2021.dbc' #change to correct DBC file
r =strymread(csvfile, dbcfile)

'''
#OPTIONAL: Run the following two lines to check that the file is while the vehicle is moving, and not while parked
msg180 = r.get_ts(msg=180, signal=1)
strymread.plt_ts(msg180, title="Message msg180, Signal ID 1")
'''

'''
#OPTIONAL: Run the following two lines to check the lead distance recorded in this file is one you want to use
lead_distance = r.lead_distance()
strymread.plt_ts(lead_distance, title="Lead Vehicle's Distance [m]")
'''

#exports lead distance to csv file
lead_distance.to_csv('lead_distance_output.csv')
