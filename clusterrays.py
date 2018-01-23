import p2mdoa

class ClusterRays():
    # Cluster rays into beams
    #something here
    
    def __init__(self):
        #self.doa = p2mdoa.P2MDoA(filename)
        #print(self.doa.get_data_ndarray())
        self.numBeams = 16 #number of beams
        self.beamAzimuthWidth=360/self.numBeams

    def processRays(self,azimuth,ellevation):
        #currently we will assume the beam is given by the azimuth only, and ignore ellevation
        beamNumber = int(azimuth / self.beamAzimuthWidth)
        return beamNumber

if __name__=='__main__':
    #doa = p2mdoa.P2MDoA('example/iter0.dod.t001_05.r006.p2m') #angle of departure
    doa = p2mdoa.P2MDoA('example/iter0.doa.t001_05.r006.p2m') #angle of arrival
    clusterrays = ClusterRays()
    
    data_ndarray = doa.get_data_ndarray()
    for rx in range(15):
        for path in range(25):
            print(clusterrays.processRays(data_ndarray[rx][path][0],data_ndarray[rx][path][1]))