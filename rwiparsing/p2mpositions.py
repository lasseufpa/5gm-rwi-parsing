import collections
import numpy as np
# from .p2mdoa import P2mFileParser
import re
import os


class ParsingError(Exception):
    pass


class P2mFileParser:
    """Parser for p2m files"""

    # project.type.tx_y.rz.p2m
    _filename_match_re = (r'^(?P<project>.*)' +
                          r'\.' +
                          r'(?P<type>((doa)|(paths)|(positions)))' +
                          r'\.' +
                          r't(?P<transmitter>\d+)' +
                          r'_' +
                          r'(?P<transmitter_set>\d+)' +
                          r'\.' +
                          r'r(?P<receiver_set>\d+)' +
                          r'\.' +
                          r'p2m$')

    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self._parse()

    def get_data_dict(self):
        return self.data

    def _parse_meta(self):
        match = re.match(P2mFileParser._filename_match_re,
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
        """read the first line of the file, indicating the number of receivers"""
        line = self._get_next_line()
        self.n_receivers = int(line.strip())

    def _parse_receiver(self):
        raise NotImplementedError()

    def _get_next_line(self):
        """Get the next uncommedted line of the file

        Call this only if a new line is expected
        """
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


class P2mCir(P2mFileParser):
    """Parse a p2m cir file"""

    def _parse_receiver(self):
        """Get receiver and number of paths (pair Tx-Rx)"""
        line = self._get_next_line()
        time = int(line)
        line = self._get_next_line()
        n_veh = int(line)
        print('time = ', time)  # TODO take out
        print('print n_veh = ', n_veh)
        self.data["positions"] = collections.OrderedDict()
        self.data["positions"]["time"] = time
        if n_veh == 0:
            self.data["positions"] = None
            return
        """Read: phase, arrival_time and power of a ray"""
        for veh in range(n_veh):
            self.data["positions"][veh] = collections.OrderedDict()
            line = self._get_next_line()
            veh_name = str(line)
            self.data["positions"][veh]['name'] = veh_name
            line = self._get_next_line()
            x, y, z, vel, acel = [float(i) for i in line.split()]
            self.data["positions"][veh]['x'] = x
            self.data["positions"][veh]['y'] = y
            self.data["positions"][veh]['z'] = z
            self.data["positions"][veh]['vel'] = vel
            self.data["positions"][veh]['acel'] = acel

    def get_phase_ndarray(self, antenna_number):
        if self.data[antenna_number] is None:
            return None
        data_ndarray = np.zeros((self.data[antenna_number]['paths_number'],))
        for paths in range(self.data[antenna_number]['paths_number']):
            data_ndarray[paths] = self.data[antenna_number][paths + 1]['phase']
        return data_ndarray


if __name__ == '__main__':
    cir = P2mCir('../example/model.positions.t001_01.r002.p2m')
    print('Phase: ', cir.get_phase_ndarray(1))  # Pass the antenna_number as argument
