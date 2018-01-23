import re
import os
import collections

import numpy as np

class ParsingError(Exception):
    pass

class P2MDoA():
    """Parse a p2m direction of arrival file
    > P2MDoA('iter0.doa.t001_05.r006.p2m').get_data_ndarray()
    """
    # project.type.tx_y.rz.p2m
    _filename_match_re = (r'^(?P<project>.*)' +
                          '\.' + 
                          '(paths|doa)' + 
                          '\.' + 
                          't(?P<transmitter>\d+)'+
                          '_' +
                          '(?P<transmitter_set>\d+)' +
                          '\.' + 
                          'r(?P<receiver_set>\d+)' + 
                          '\.' +
                          'p2m$')
    
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self._parse()
        
    def get_data_ndarray(self):
        ''' return the DoA as a ndarray
        
        The array is shaped (reiceiver, path, direction) the order is the one they appear in the file
        
        If a receiver has less paths than another its path is populated with zeros
        '''
        data_ndarray = np.zeros((self.n_receivers, self.biggest_n_paths(), 3))
        for rec_idx, path_dict in enumerate(self.data.values()):
            for path_idx, direction in enumerate(path_dict.values()):
                data_ndarray[rec_idx][path_idx][:] = direction
        return data_ndarray
    
    def biggest_n_paths(self):
        ''' find the reciever with the biggest number of received paths'''
        biggest = -np.inf
        for receiver, receiver_v in self.data.items():
            n_paths = len(receiver_v)
            if n_paths > biggest:
                biggest = n_paths
        return biggest
    
    def get_data_dict(self):
        return self.data
        
    def _parse_meta(self):
        match = re.match(P2MDoA._filename_match_re,
                         os.path.basename(self.filename))
        self.project = match.group('project')
        self.transmitter_set = int(match.group('transmitter_set'))
        self.transmitter = int(match.group('transmitter'))
        self.receiver_set = int(match.group('receiver_set'))
        
    def _parse(self):
        with open(self.filename) as self.file:
            self._parse_meta()
            self._parse_header()
            self.data = collections.OrderedDict()
            for rec in range(self.n_receivers):
                self._parse_receiver()

    def _parse_header(self):
        '''read the first line of the file, indicating the number of receivers'''
        line = self._get_next_line()
        self.n_receivers = int(line.strip())
        
    def _parse_receiver(self):
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        self.data[receiver] = collections.OrderedDict()
        for i in range(n_paths):
            line = self._get_next_line()
            sp_line = line.split()
            path = int(sp_line[0])
            direction = np.array([float(j) for j in sp_line[1:]])
            self.data[receiver][path] = direction
        
    def _get_next_line(self):
        '''get the next uncommedted line of the file
        
        Call this only if a new line is expected
        '''
        if self.file is None:
            raise ParsingError('File is closed')
        while True:
            next_line = self.file.readline()
            if next_line == '':
                raise ParsingError('Unexpected end of file')
            if re.search(r'^\s*#', next_line, re.DOTALL):
                continue
            else:
                return next_line

class P2MPaths(P2MDoA):
    """Parse a p2m paths file
    > P2MPaths('iter0.paths.t001_05.r006.p2m').get_data_ndarray()
    """

    def _parse_receiver(self):
        '''Get receiver and number of paths(pair Tx-Rx)'''
        line = self._get_next_line()
        receiver, n_paths = [int(i) for i in line.split()]
        '''Read: received_power -self.data[receiver][0]-, arrival_time -self.data[receiver][1]-,
         spread_delay -self.data[receiver][2]-'''
        line = self._get_next_line()
        self.data[receiver] = collections.OrderedDict()
        received_power, arrival_time, spread_delay = [float(i) for i in line.split()]
        self.data[receiver]['received_power'] = received_power
        self.data[receiver]['arrival_time'] = arrival_time
        self.data[receiver]['spread_delay'] = spread_delay
        self.data[receiver]['paths_number'] = n_paths
        #print (self.data) #debug
        #print (self.data[receiver]) #debug
        #for rec in range(self.n_receivers):
        '''Read: srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2
            GETTING ERROR --- TO FIX'''
        for rays in xrange(0,25):
            line = self._get_next_line()
            ray_n, n_interactions, srcvdpower, arrival_time, arrival_angle1, arrival_angle2, departure_angle1, departure_angle2 = [float(i) for i in line.split()]
            interactions_list = self._get_next_line().strip()
            #print (interactions_list) #debug
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
            
            #print (self.data)
            #print(self.data[receiver])
            #print(interactions_list.split('-')[0])
            #print(self.data[receiver][ray][interactions_list])
            '''Get coordenates of interactions'''
            for i in range(n_interactions+2):
                line = self._get_next_line()
                sp_line = line.split()
                #print (sp_line)
                interaction = i 
                #print (interaction)
                coordenates = np.array([float(j) for j in sp_line[0:]])
                self.data[receiver][ray_n]['interactions'][interactions_list.split('-')[i]] = coordenates
                #print(self.data[receiver][ray_n]['interactions'])
            #print(self.data)

    def get_departure_angle_ndarray(self, antenna_number):

        ''' return the daparture angles as a ndarray
        
        The array is shaped (number_paths, departure_angle1, departure_angle2)
        '''
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in xrange(self.data[antenna_number]['paths_number']):
            #print(self.data[antenna_number][paths+1]['srcvdpower'])
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['departure_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['departure_angle2']
            pass
        return data_ndarray
    def get_arrival_angle_ndarray(self, antenna_number):

        ''' return the arrival angles as a ndarray
        
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        '''
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 2))
        for paths in xrange(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['arrival_angle1']
            data_ndarray[paths][1]= self.data[antenna_number][paths+1]['arrival_angle2']
            pass
        return data_ndarray

    def get_p_gain_ndarray(self, antenna_number):

        ''' return the gains as a ndarray
        
        The array is shaped (number_paths, arrival_angle1, arrival_angle2)
        '''
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'], 1))
        for paths in xrange(self.data[antenna_number]['paths_number']):
            data_ndarray[paths][0]= self.data[antenna_number][paths+1]['srcvdpower']
            pass
        return data_ndarray



if __name__=='__main__':
    path = P2MPaths('example/iter0.paths.t001_05.r006.p2m')
    doa = P2MDoA('example/iter0.doa.t001_05.r006.p2m')
    #print(path.receiver_set)
    #print('project: ', doa.project)
    #print('transmitter set: ', doa.transmitter_set)
    #print('transmitter: ', doa.transmitter)
    #print('receiver set: ', doa.receiver_set)
    #print(doa.get_data_ndarray())
    #print(path.data[1])
    print('Departure angeles: ',path.get_departure_angle_ndarray(1)) #Pass the antenna_number as argument
    print('Arrival angeles: ',path.get_arrival_angle_ndarray(1))
    print('Gains: ',path.get_p_gain_ndarray(1))