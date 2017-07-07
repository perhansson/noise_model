#!/bin/python

import sys
import argparse
import cmath
import numpy as np
import matplotlib.pyplot as plt

import impedance as Q
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


def impedancePlot(fig, f, Z, name=None, ylabel='Impedance', xlabel='Frequency', note=None):
    """Plot impedance and phase"""

    
    ax_MC211 = plt.subplot(211)
    plt.plot(f, np.abs(Z))
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if args.logy:
        ax_MC211.set_yscale(u'log')
    ax_MC211.set_xscale(u'log')
    if note:
        plt.text(0.1, 0.9, note, transform = ax_MC211.transAxes)

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

    figNr=0
    
    # freqency vector
    f_arr = np.logspace(0,5)

    # circuits
    Z1_MC = Q.Z1_MC('Z1_MC')
    Z1_g = Q.Z1_g('Z1_g')
    Z2 = Q.Z2('Z2')
    Z3 = Q.Z3('Z3')
    Z4 = Q.Z4('Z4')
    Z5 = Q.Z5('Z5')
    Z6 = Q.Z6('Z6')
    opamp = Q.LT1677('LT1677')
    bjt = Q.BJT('bjt')
    hemt = Q.HEMT('HEMT')

    ## Calculate opamp gain
    Aopen = to_np_array(opamp.Aopen, f_arr)

    # feedback fraction
    Z_Z5 = to_np_array(Z5.Z_tot,f_arr)
    Z_Z6 = to_np_array(Z6.Z_tot,f_arr)
    B = Z_Z5/(Z_Z5 +Z_Z6)
    
    # closed loop gain
    Aclosed = Aopen/(1 + Aopen*B)

    impedancePlot(plt.figure(), f_arr, Z_Z5, 'Z_Z5.png', note='Z5')
    impedancePlot(plt.figure(), f_arr, Z_Z6, 'Z_Z6.png', note=r'Z6')
    impedancePlot(plt.figure(), f_arr, B, 'B.png',ylabel='Feedback fraction B',note='Feedback fraction B')
    impedancePlot(plt.figure(), f_arr, Aopen, 'Aopen_opamp.png', ylabel='Aopen opamp', note='Aopen opamp')
    impedancePlot(plt.figure(), f_arr, Aclosed, 'Aclosed_opamp.png', ylabel='Aclosed opamp', note='Aclosed opamp')

    ## voltage gain of HEMT
    # gain given by gm times load

    # load impedance
    Z_Z3 = to_np_array(Z3.Z_tot, f_arr)

    # take into account any load impedance from current mirror in series 
    Z_BJT = to_np_array(bjt.Z_tot, f_arr)
    Z_load = Z_Z3 + Z_BJT
    
    # any impedance from mirror would split voltage gain at opamp input
    Aopen_HEMT = hemt.gm*Z_load*(Z_Z3/Z_load)

    impedancePlot(plt.figure(), f_arr, Z_Z3, 'Z3.png', note='Z3')
    impedancePlot(plt.figure(), f_arr, Z_load, 'Z_load.png', note='Z_load')
    impedancePlot(plt.figure(), f_arr, Aopen_HEMT, 'Aopen_HEMT.png', ylabel='Aopen HEMT', note='Aopen HEMT gm={0:.1f}mS'.format(hemt.gm*1e3))
    

    ## total voltage gain

    # total open loop gain is product of closed opamp gain and open HEMT gain
    Atotal_open = Aclosed*Aopen_HEMT

    impedancePlot(plt.figure(), f_arr, Atotal_open, 'Atotal_open.png', ylabel='Atotal openT', note='Atotal open')
    
    ## feedback for inverting amplifier

    # HEMT input impedance: input capacitance and input resistor are parallel to ground
    Z_HEMT = to_np_array(hemt.Z_tot, f_arr) 

    impedancePlot(plt.figure(), f_arr, Z_HEMT, 'Z_HEMT.png', note='Z_HEMT')

    # impedance of gate coupling capacitor to the HEMT gate input
    Z_Z1_g = to_np_array(Z1_g.Z_tot, f_arr) 

    impedancePlot(plt.figure(), f_arr, Z_Z1_g, 'Z1_g.png', note='Z1_g')

    # The gate coupling capacitor and HEMT input impedance are in parallel to ground
    Z_Z1_4K = Q.parallel(Z_HEMT, Z_Z1_g)

    impedancePlot(plt.figure(), f_arr, Z_Z1_4K, 'Z1_4K.png', note='Z1_4K')

    # feedback impedance
    Z_Z2 = to_np_array(Z2.Z_tot, f_arr) 

    impedancePlot(plt.figure(), f_arr, Z_Z2, 'Z2.png', note='Z2')

    # feedback fraction at HEMT gate is split between Z2 and Z_input on the HEMT gate
    # the Z_input consists the input impedance of the HEMT and the gate coupling capacitance in parallel

    Z_input = Z_Z1_4K

    impedancePlot(plt.figure(), f_arr, Z_input, 'Z_input.png', note='Z_input')
    

    # feedback fraction: H_fb
    H_fb = Z_input/(Z_input + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_fb, 'H_fb.png', note='H_fb')

    # input damping: H_in
    H_in = -1*Z_Z2/(Z_input + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_in, 'H_in.png', note='H_in')

    # total closed loop voltage gain
    Atotal_closed = H_in*Atotal_open/(1+Atotal_open*H_fb)

    impedancePlot(plt.figure(), f_arr, Atotal_closed, 'Atotal_closed.png', ylabel='Atotal closed', note='Atotal closed')
    



    
    if not args.noshow:
        plt.show()
        
    #print('Z_tot = ' + str(Z_tot(f_arr)))



if __name__ == '__main__':

    print('Just GO')

    args = get_args()
    
    main()
