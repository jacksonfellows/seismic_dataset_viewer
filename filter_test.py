import numpy as np
import scipy
from matplotlib import pyplot as plt

sos_coefs = scipy.signal.iirfilter(
    10, 1, btype="lowpass", ftype="butter", output="sos", fs=100
)

signal = np.load("events/pnsn1074268/UW.RCM..EHZ.npy")


def mysosfilt(sos, x):
    x = np.copy(x)
    zi = np.zeros((sos.shape[0], 2))
    for n in range(x.shape[0]):
        for s in range(sos.shape[0]):
            x_n = x[n]
            x[n] = sos[s, 0] * x_n + zi[s, 0]
            zi[s, 0] = sos[s, 1] * x_n - sos[s, 4] * x[n] + zi[s, 1]
            zi[s, 1] = sos[s, 2] * x_n - sos[s, 5] * x[n]
    print(zi)
    return x


def js_bandpass(pairs):
    print("let bandpassSos = {")
    for low, high in pairs:
        sos = scipy.signal.iirfilter(
            4, [low, high], btype="bandpass", ftype="butter", output="sos", fs=100
        )
        print(f'\t"{low}-{high}": [')
        for s in range(sos.shape[0]):
            print("\t\t", ", ".join([str(f) for f in sos[s]]), ",", sep="")
        print("\t],")
    print("};")


def js_lowpass(lows):
    print("let lowpassSos = {")
    for low in lows:
        sos = scipy.signal.iirfilter(
            4, low, btype="lowpass", ftype="butter", output="sos", fs=100
        )
        print(f'\t"<{low}": [')
        for s in range(sos.shape[0]):
            print("\t\t", ", ".join([str(f) for f in sos[s]]), ",", sep="")
        print("\t],")
    print("};")
