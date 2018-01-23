import struct

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
    for i in range(m):
        gain_dB = p_gain[i]
        path_gain = np.power(10, gain_dB/10)
        omegay = k * d * np.sin(departure_angle[i, 1]) * np.sin(departure_angle[i, 0])
        omegax = k * d * np.sin(departure_angle[i, 1]) * np.cos(departure_angle[i, 0])
        vecy = np.exp(1j * omegay * np.arange(antenna_number))
        vecx = np.exp(1j * omegax * np.arange(antenna_number))
        departure_vec = np.matrix(np.kron(vecy, vecx))
        omegay = k * d * np.sin(arrival_angle[i, 1]) * np.sin(arrival_angle[i, 0])
        omegax = k * d * np.sin(arrival_angle[i, 1]) * np.cos(arrival_angle[i, 0])
        vecy = np.exp(1j * omegay * np.arange(antenna_number))
        vecx = np.exp(1j * omegax * np.arange(antenna_number))
        arrival_vec = np.matrix(np.kron(vecy, vecx))
        H = H + path_gain * departure_vec.conj().T * arrival_vec
    t1 = wt.conj().T * H * wr
    return t1

if __name__ == '__main__':
    with open('/Users/psb/Downloads/test_calc_rx_power.bin', 'rb') as infile:
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

        t1_py = calc_rx_power(departure_angle, arrival_angle, p_gain, antenna_number)

        np.sum(t1 - t1_py, (0,1))