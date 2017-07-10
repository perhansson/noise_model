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


def impedancePlot(fig, f, Z, name=None, ylabel='Impedance', xlabel='Frequency', note=None, legend=None):
    """Plot impedance and phase"""

    
    ax_MC211 = plt.subplot(211)
    line1, = plt.plot(f, np.abs(Z), label=legend)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if args.logy:
        ax_MC211.set_yscale(u'log')
    ax_MC211.set_xscale(u'log')
    if note:
        plt.text(0.1, 0.9, note, transform = ax_MC211.transAxes)
    if legend:
        #hs = ax_MC211.get_legend_handles_labels()
        #hs = [hs,line1]
        #if hss:
        #    handles.append(line1)
        plt.legend()
        #else:
        #    plt.legend(handles=[line1])
    

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
    f_arr = np.logspace(0,6)
    #f_arr = np.append(np.logspace(0,4)[:-1],np.logspace(4,5))

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

    # feedback fraction for opamp
    # no damping as it's non-inverting
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

    # The gate coupling capacitor is in series with an open connection
    Ropen = Q.Resistor(1e19,'Ropen')
    Z_Z1_open = Q.series(Z_Z1_g, Ropen.Z(f_arr))

    impedancePlot(plt.figure(), f_arr, Z_Z1_open, 'Z1_open.png', note='Z1_open')

    # The feedback signal are split between the HEMT input impedance and gate coupling capactor
    Z_input_4K = Q.parallel(Z_HEMT, Z_Z1_open)

    impedancePlot(plt.figure(), f_arr, Z_input_4K, 'Z_input_4K.png', note='Z_input_4K')


    # feedback impedance
    Z_Z2 = to_np_array(Z2.Z_tot, f_arr) 

    impedancePlot(plt.figure(), f_arr, Z_Z2, 'Z2.png', note='Z2')

    # feedback fraction: H_fb
    H_fb = Z_input_4K/(Z_input_4K + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_fb, 'H_fb.png', note='H_fb')

    # input damping: H_in
    H_in = -1*Z_Z2/(Z_input_4K + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_in, 'H_in.png', note='H_in')

    # total closed loop voltage gain
    Atotal_closed = H_in*Atotal_open/(1+Atotal_open*H_fb)

    impedancePlot(plt.figure(), f_arr, Atotal_closed, 'Atotal_closed.png', ylabel='Atotal closed', note='Atotal closed')

    # total closed loop voltage gain w/o input damping term
    Atotal_closed_no_H_in = Atotal_open/(1+Atotal_open*H_fb)
    Atotal_closed_no_H_fb = H_in*Atotal_open/(1+Atotal_open)

    fig = plt.figure()
    impedancePlot(fig, f_arr, Atotal_closed,legend='Atotal_closed')
    impedancePlot(fig, f_arr, Atotal_closed_no_H_in, legend='no H_in')
    impedancePlot(fig, f_arr, Atotal_closed_no_H_fb, ylabel='Atotal_closed', legend='no H_fb',note='Compare FB/damping effect.', name='Atotal_closed_cmp.png')


    ### Include circuitry at MC stage

    #calculate impedance contribution from  circuitry at the MC stage
    Z_Z1_MC = to_np_array(Z1_MC.Z_tot,f_arr)

    impedancePlot(plt.figure(), f_arr, Z_Z1_MC, note='Z_Z1_MC', name='Z1_MC.png')

    # makes some cross check on the bahavior of the Z1_MC contributions
    Z1_MC_det100pf = Q.Z1_MC('Z1_MC_det100pf',Cdet=100.0e-12)
    Z1_MC_det10pf = Q.Z1_MC('Z1_MC_det10pf',Cdet=10.0e-12)
    Z1_MC_Rbias10Meg = Q.Z1_MC('Z1_MC_Rbias10Meg',Rbias=10.0e6)
    Z_Z1_MC_det100pf = to_np_array(Z1_MC_det100pf.Z_tot,f_arr)
    Z_Z1_MC_det10pf = to_np_array(Z1_MC_det10pf.Z_tot,f_arr)
    Z_Z1_MC_Rbias10Meg = to_np_array(Z1_MC_Rbias10Meg.Z_tot,f_arr)
    fig = plt.figure()
    impedancePlot(fig, f_arr, Z_Z1_MC, legend='Z_Z1_MC')
    impedancePlot(fig, f_arr, Z_Z1_MC_det100pf, legend='Z_Z1_MC_det100pf')
    impedancePlot(fig, f_arr, Z_Z1_MC_det10pf, legend='Z_Z1_MC_det10pf')
    impedancePlot(fig, f_arr, Z_Z1_MC_Rbias10Meg, legend='Z_Z1_MC_Rbias10Meg', name='Z1_MC_cmp.png')

    # the MC stage contribution is connected in series with 4K stage through Cc
    Z_Z1_MC_g = Q.series(Z_Z1_g, Z_Z1_MC)
    #Z_Z1_MC_g = Z_Z1_MC #Q.series(Z_Z1_g, Z_Z1_MC)

    impedancePlot(plt.figure(), f_arr, Z_Z1_MC_g, note='Z_Z1_MC_g', name='Z1_MC_g.png')

    fig = plt.figure()
    impedancePlot(fig, f_arr, Z_Z1_MC, legend='Z_Z1_MC')
    impedancePlot(fig, f_arr, Z_Z1_g, legend='Z_Z1_g')
    impedancePlot(fig, f_arr, Z_Z1_MC_g, legend='Z_Z1_MC_g', name='Z1_MC_cmp.png')

    # The feedback signal are split between the HEMT input impedance and gate coupling capactor
    Z_input = Q.parallel(Z_HEMT, Z_Z1_MC_g)

    impedancePlot(plt.figure(), f_arr, Z_input, note='Z_input', name='Z_input.png')

    # compare w/ and w/o MC stage
    fig = plt.figure()
    impedancePlot(fig, f_arr, Z_input, legend='Z_input')
    impedancePlot(fig, f_arr, Z_input_4K, legend='Z_input_4K')
    impedancePlot(fig, f_arr, Z_Z1_MC_g, legend='Z1_MC',name='Z_input_cmp.png')

    # feedback fraction
    H_fb_det = Z_input/(Z_input + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_fb_det, 'H_fb_det.png', note='H_fb_det')

    # input damping
    H_in_det = -1*Z_Z2/(Z_input + Z_Z2)

    impedancePlot(plt.figure(), f_arr, H_in_det, 'H_in_det.png', note='H_in_det')

    # total closed loop voltage gain
    Atotal_closed_det = H_in_det*Atotal_open/(1+Atotal_open*H_fb_det)

    impedancePlot(plt.figure(), f_arr, Atotal_closed_det, 'Atotal_closed_det.png', ylabel='Atotal closed det', note='Atotal_closed_det')

    # compare w/ and w/o MC stage
    fig = plt.figure()
    impedancePlot(fig, f_arr, Atotal_closed_det, legend='Atotal_closed_det')
    impedancePlot(fig, f_arr, Atotal_closed, legend='Atotal_closed',name='Atotal_closed_det_cmp.png',ylabel='total closed loop gain')


    if not args.noshow:
        plt.show()
        
    #print('Z_tot = ' + str(Z_tot(f_arr)))



if __name__ == '__main__':

    print('Just GO')

    args = get_args()
    
    main()
