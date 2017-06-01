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
    a =parser.parse_args()
    print(a)
    return a

def main():


    Q = ChargeCircuit('Circuit')


    f_arr = np.logspace(0,5)

    Z_MC1 = np.array([Q.Z_MC1(f) for f in f_arr])
    Z_MC1_phase = np.array([cmath.phase(z) for z in Z_MC1])
    print('Z_MC1 = ' + str(Z_MC1))
    print('Z_MC1_phase = ' + str(Z_MC1_phase))

    fig_MC211 =  plt.figure(1)
    ax_MC211 = plt.subplot(211)
    plt.plot(f_arr, np.abs(Z_MC1))
    plt.ylabel('Impedance')
    plt.xlabel('Frequency')
    #ax_MC1.set_yscale(u'log')
    ax_MC211.set_xscale(u'log')
    
    ax_MC212 = plt.subplot(212)
    plt.plot(f_arr, radToDeg(Z_MC1_phase))
    plt.ylabel('Phase')
    plt.xlabel('Frequency')
    #ax_MC1.set_yscale(u'log')
    ax_MC212.set_xscale(u'log')
    plt.savefig('Z_MC1.png',bbox_inches='tight')
    
    if not args.noshow:
        plt.show()
        
    #print('Z_tot = ' + str(Q.Z_tot(f_arr)))



if __name__ == '__main__':

    print('Just GO')

    args = get_args()
    
    main()
