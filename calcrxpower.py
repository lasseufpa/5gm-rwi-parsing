import struct
import os
import datetime

import numpy as np


def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)
    return w


def calc_rx_power(departure_angle, arrival_angle, p_gain, antenna_number, frequency=6e10):
    c = 3e8
    mlambda = c/frequency
    k = 2 * np.pi / mlambda
    d = mlambda / 2
    nt = np.power(antenna_number, 2)
    m = np.shape(departure_angle)[0]
    nr = nt
    wt = dft_codebook(nt)
    wr = dft_codebook(nr)
    H = np.matrix(np.zeros((nt, nr)))
    gain_dB = p_gain
    path_gain = np.power(10, gain_dB/10)
    antenna_range = np.arange(antenna_number)
    def calc_omega(angle):
        sin = np.sin(angle)
        k_d_sin = k * d * sin[:, 1]
        omegay = k_d_sin * sin[:, 0]
        omegax = k_d_sin * np.cos(angle[:, 0])
        return np.matrix((omegax, omegay))
    departure_omega = calc_omega(departure_angle)
    arrival_omega = calc_omega(arrival_angle)
    def calc_vec_i(i, omega, antenna_range):
        vec = np.exp(1j * omega[:,i] * antenna_range)
        return np.matrix(np.kron(vec[1], vec[0]))
    for i in range(m):
        departure_vec = calc_vec_i(i, departure_omega, antenna_range)
        arrival_vec = calc_vec_i(i, arrival_omega, antenna_range)
        H = H + path_gain[i] * departure_vec.conj().T * arrival_vec
    t1 = wt.conj().T * H * wr
    return t1

if __name__ == '__main__':

    EXAMPLE_DIR=os.path.dirname(os.path.realpath(__file__))
    MATLAB_DATA=os.path.join(EXAMPLE_DIR, 'test', 'data',
                             'test_calc_rx_power.bin')

    with open(MATLAB_DATA, 'rb') as infile:
        L = 15
        def get_float_complex(L):
            L2 = np.array(struct.unpack('d' * L * 2, infile.read(L * 2 * 8)), dtype=np.float64)
            #L2 = L2[0:L * 2] + L2[L * 2:] * 1j
            L2 = L2.reshape((L, 2), order='F')
            L2 = L2[:, 0] + L2[:, 1] * 1j
            return L2

        departure_angle = get_float_complex(L * 2).reshape((L, 2), order='F')
        arrival_angle = get_float_complex(L * 2).reshape((L, 2), order='F')
        p_gain = get_float_complex(L)
        antenna_number = int(np.real(get_float_complex(1)))
        t1 = get_float_complex(16 * 16).reshape((16, 16), order='F')

        antenna_number = 20
        n_paths = 500
        departure_angle = np.random.uniform(size=(n_paths, n_paths))
        arrival_angle = np.random.uniform(size=(n_paths, n_paths))
        p_gain = np.random.uniform(size=n_paths)


        start = datetime.datetime.today()
        t1_py = calc_rx_power(departure_angle, arrival_angle, p_gain, antenna_number)
        stop = datetime.datetime.today()

        #print(np.mean(np.power(t1 - t1_py, 2)))
        print(stop - start)