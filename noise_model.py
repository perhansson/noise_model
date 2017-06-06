#!/bin/python

import sys
import argparse
import cmath
import numpy as np
import matplotlib.pyplot as plt

from impedance import ChargeCircuit
from impedance import radToDeg



def get_args():
    parser = argparse.ArgumentParser('Noise Model')
    parser.add_argument('--debug',action='store_true',help='debug toggle')
    parser.add_argument('--noshow',action='store_true',help='Do not show plots.')
    parser.add_argument('--logy',action='store_true',help='Log y axis.')
    a =parser.parse_args()
    print(a)
    return a



def to_np_array(func, arr):
    return np.array([func(a) for a in arr])


def impedancePlot(fig_MC211, f, Z, name=None):
    """Plot impedance and phase"""

    
    ax_MC211 = plt.subplot(211)
    plt.plot(f, np.abs(Z))
    plt.ylabel('Impedance')
    plt.xlabel('Frequency')
    if args.logy:
        ax_MC211.set_yscale(u'log')
    ax_MC211.set_xscale(u'log')

    Z_phase = to_np_array(cmath.phase, Z)

    ax_MC212 = plt.subplot(212)
    plt.plot(f, radToDeg(Z_phase))
    plt.ylabel('Phase')
    plt.xlabel('Frequency')
    #ax_MC1.set_yscale(u'log')
    ax_MC212.set_xscale(u'log')

    if name:
        plt.savefig(name,bbox_inches='tight')

    return [ax_MC211, ax_MC212]

def main():


    Q = ChargeCircuit('Circuit')

    f_arr = np.logspace(0,5)

    Z_MC1 = to_np_array(Q.Z_MC1, f_arr)
    impedancePlot(plt.figure(1), f_arr, Z_MC1, 'Z_MC1.png')


    Z_HEMT = to_np_array(Q.Z_HEMT, f_arr)    
    impedancePlot(plt.figure(2), f_arr, Z_HEMT,'Z_HEMT.png')


    Z1_tot = to_np_array(Q.Z1_tot, f_arr)    
    impedancePlot(plt.figure(3), f_arr, Z1_tot,'Z1_tot.png')

    Z_fb = to_np_array(Q.Z_fb, f_arr)    
    impedancePlot(plt.figure(4), f_arr, Z_fb,'Z_fb.png')

    Z6 = to_np_array(Q.Z6, f_arr)    
    impedancePlot(plt.figure(5), f_arr, Z6,'Z6.png')

    Z5 = to_np_array(Q.Z5, f_arr)    
    impedancePlot(plt.figure(6), f_arr, Z5,'Z5.png')

    Z3 = to_np_array(Q.Z3, f_arr)    
    impedancePlot(plt.figure(7), f_arr, Z3,'Z3.png')

    
    if not args.noshow:
        plt.show()
        
    #print('Z_tot = ' + str(Q.Z_tot(f_arr)))



if __name__ == '__main__':

    print('Just GO')

    args = get_args()
    
    main()
