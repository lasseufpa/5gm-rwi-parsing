import collections

import numpy as np

from .p2mdoa import P2mFileParser


class P2mPaths(P2mFileParser):
    """Parse a p2m paths file"""

    def _parse_receiver(self):
        """Get receiver and number of paths (pair Tx-Rx)"""
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        self.data[receiver] = collections.OrderedDict()
        if n_paths == 0:
            self.data[receiver] = None
            return
        """Read: received_power -self.data[receiver][0]-, arrival_time -self.data[receiver][1]-,
         spread_delay -self.data[receiver][2]-"""
        line = self._get_next_line()
        received_power, arrival_time, spread_delay = [float(i) for i in line.split()]
        self.data[receiver]['received_power'] = received_power
        self.data[receiver]['arrival_time'] = arrival_time
        self.data[receiver]['spread_delay'] = spread_delay
        self.data[receiver]['paths_number'] = n_paths
        """Read: srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2"""
        for rays in range(0,n_paths):
            line = self._get_next_line()
            ray_n, n_interactions, srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2 = [float(i) for i in line.split()]
            interactions_list = self._get_next_line().strip()
            ray_n = int(ray_n)
            n_interactions = int(n_interactions)
            self.data[receiver][ray_n] = collections.OrderedDict()
            self.data[receiver][ray_n]['srcvdpower'] = srcvdpower
            self.data[receiver][ray_n]['arrival_time'] = arrival_time
            self.data[receiver][ray_n]['arrival_angle1'] = arrival_angle1
            self.data[receiver][ray_n]['arrival_angle2'] = arrival_angle2
            self.data[receiver][ray_n]['departure_angle1'] = departure_angle1
            self.data[receiver][ray_n]['departure_angle2'] = departure_angle2
            self.data[receiver][ray_n]['interactions_list'] = interactions_list
            self.data[receiver][ray_n]['interactions'] = collections.OrderedDict()
            """Get coordenates of interactions"""
            for i in range(n_interactions+2):
                line = self._get_next_line()
                sp_line = line.split()
                interaction = i 
                coordenates = np.array([float(j) for j in sp_line[0:]])
                self.data[receiver][ray_n]['interactions'][interactions_list.split('-')[i]] = coordenates

    def get_total_received_power(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        return self.data[antenna_number]['received_power']

    def get_mean_time_of_arrival(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        return self.data[antenna_number]['arrival_time']

    def get_arrival_time_ndarray(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'],))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['arrival_time']
        return data_ndarray

    def get_interactions_list(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        data = []
        for paths in range(self.data[antenna_number]['paths_number']):
            data.append(self.data[antenna_number][paths+1]['interactions_list'])
        return data

    def get_departure_angle_ndarray(self, antenna_number):
        """ return the daparture angles as a ndarray        
        The array is shaped (number_paths, departure_angle1, departure_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['departure_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['departure_angle2']
        return data_ndarray

    def get_arrival_angle_ndarray(self, antenna_number):
        """Return the arrival angles as a ndarray
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['arrival_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['arrival_angle2']
        return data_ndarray

    def get_p_gain_ndarray(self, antenna_number):
        """Return the gains as a ndarray
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        """
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number']))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths+1]['srcvdpower']
        return data_ndarray

if __name__=='__main__':
    path = P2mPaths('/mnt/d/github/5gm-rwi-simulation/example/results_new_simuls/run00001/study/model.paths.t001_01.r002.p2m')
    #path = P2mPaths('example/iter0.paths.t001_05.r006.p2m')
    print('Departure angeles: ',path.get_departure_angle_ndarray(1)) #Pass the antenna_number as argument
    print('Arrival angeles: ',path.get_arrival_angle_ndarray(1))
    print('Gains: ',path.get_p_gain_ndarray(1))
