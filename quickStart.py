import iTRAC as it


#replace with your filepath
data = pd.read_csv('/Volumes/SSD_MNICE/vanderdata/2T3MWRFVXLW056972/libpanda/2021_08_06/2021-08-06-11-40-19_2T3MWRFVXLW056972_CAN_Messages.csv')

#replace with your filepath
db2 = s.initializeDBC_Cantools('../strym/strym/dbc/toyota_rav4_hybrid.dbc')


radarData = it.allRadar(data)
G = it.myGraph(radarData,dt=0.5)
p = it.SSP(G.G)
dfs = it.getPathDfs(p)
