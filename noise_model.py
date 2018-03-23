#!/bin/python

import sys
import argparse
import cmath
import numpy as np
import matplotlib.pyplot as plt
import impedance as Q
import plot_util

# setup Latex and font
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=True)

def get_args():
    parser = argparse.ArgumentParser('Noise Model')
    parser.add_argument('--makeplots',action='store_true',help='debug toggle')
    parser.add_argument('--savename', default=None, type=str, help="File path for saving plots if given")
    parser.add_argument('--debug',action='store_true',help='debug toggle')
    parser.add_argument('--show',action='store_true',help='Make and show plots.')
    parser.add_argument('--logy',action='store_true',help='Log y axis.')
    parser.add_argument('--drainI', default=0.001, help='Drain current.')
    parser.add_argument('--T_4K', default=4.0, help='Temperature at the 4K stage.')
    parser.add_argument('--T_300K', default=300.0, help='Temperature for nominal room temperature circuits.')
    parser.add_argument('--num', default=20, help='Number of points to calculate wihtin the bandwidth.')
    a = parser.parse_args()
    print(a)
    return a





def main():

    plot_util.setup_plt()
    #plt.rcParams['axes.grid'] = True

    # prepare output
    outfile_dict = {}
    
    # freqency vector
    f_arr = np.logspace(0,6, num=args.num)
    outfile_dict['f_arr'] = f_arr

    # setup components of the circuits
    Z1_MC = Q.Z1_MC('Z1_MC', Cdet=200e-12, Rbias=100e6, Rbleed=100e6, Cc=10e-9)
    Z1_g = Q.Z1_g('Z1_g', Ccg=10e-9)
    Z2 = Q.Z2('Z2', Cfb=0.25e-12, Rfb=400e6)
    Z3 = Q.Z3('Z3')
    Z4 = Q.Z4('Z4')
    Z5 = Q.Z5('Z5')
    Z6 = Q.Z6('Z6')
    opamp = Q.LT1677('opamp', flat=135.0, poles=(0.5, 80e3))
    bjt = Q.BJT('bjt')
    hemt = Q.HEMT('HEMT', Rg=1e12, Cgs=100e-12, gm=35)
    



    
    print('--Impedance and gain calculation --')

   
    ## Calculate opamp gain
    Aopen = Q.to_np_array(opamp.Aopen, f_arr)
    Aopen_gary = np.array([opamp.Aopen_gary(a,flat=2e7,pole1=0.5, pole2=80e3) for a in f_arr])
    Aopen = Aopen_gary

    print("Aopen")
    print(Aopen)
    print(Aopen_gary)
    
    # feedback fraction for opamp
    # no damping as it's non-inverting
    Z_Z5 = Q.to_np_array(Z5.Z_tot,f_arr)
    Z_Z6 = Q.to_np_array(Z6.Z_tot,f_arr)
    B = Z_Z5/(Z_Z5 +Z_Z6)

    # closed loop gain
    Aclosed = Aopen/(1 + Aopen*B)

    fig = plt.figure(figsize=(18,12))

    ## voltage gain of HEMT
    # gain given by gm times load impedance

    # load impedance
    Z_Z3 = Q.to_np_array(Z3.Z_tot, f_arr)

    # take into account any load impedance from current mirror in series 
    Z_BJT = Q.to_np_array(bjt.Z_tot, f_arr)
    Z_load = Z_Z3 + Z_BJT
    
    # any impedance from mirror would split voltage gain at opamp input
    Aopen_HEMT = hemt.gm*Z_load*(Z_Z3/Z_load)

    ## total voltage gain

    # total open loop gain is product of closed opamp gain and open HEMT gain
    Atotal_open = Aclosed*Aopen_HEMT

    ## feedback for inverting amplifier

    # HEMT input impedance: input capacitance and input resistor are parallel to ground
    Z_HEMT = Q.to_np_array(hemt.Z_tot, f_arr) 


    # impedance of gate coupling capacitor to the HEMT gate input
    Z_Z1_g = Q.to_np_array(Z1_g.Z_tot, f_arr) 

    # The gate coupling capacitor is in series with an open connection
    Ropen = Q.Resistor(1e19,'Ropen')
    Z_Z1_open = Q.series(Z_Z1_g, Ropen.Z(f_arr))

    # The feedback signal are split between the HEMT input and gate coupling capactor
    Z_input_4K = Q.parallel(Z_HEMT, Z_Z1_open)

    # feedback impedance
    Z_Z2 = Q.to_np_array(Z2.Z_tot, f_arr) 

    # feedback fraction: H_fb
    H_fb = Z_input_4K/(Z_input_4K + Z_Z2)

    print("H_fb")
    print(H_fb)
    
    # input damping: H_in
    H_in = -1*Z_Z2/(Z_input_4K + Z_Z2)

    # total closed loop voltage gain
    #Atotal_closed = np.abs(H_in*Atotal_open/(1+Atotal_open*H_fb))
    Atotal_closed = H_in*Atotal_open/(1+Atotal_open*H_fb)

    # cross-check: total closed loop voltage gain w/o input damping term
    Atotal_closed_no_H_in = Atotal_open/(1+Atotal_open*H_fb)
    Atotal_closed_no_H_fb = H_in*Atotal_open/(1+Atotal_open)

    
    ### Include circuitry at MC stage

    #calculate impedance contribution from  circuitry at the MC stage
    Z_Z1_MC = Q.to_np_array(Z1_MC.Z_tot,f_arr)

    
    # the MC stage contribution is connected in series with 4K stage through coupling capacitor
    Z_Z1_MC_g = Q.series(Z_Z1_g, Z_Z1_MC)

    # The feedback signal are split between the HEMT input and gate coupling capactor
    Z_input = Q.parallel(Z_HEMT, Z_Z1_MC_g)

    # feedback fraction
    H_fb_det = Z_input/(Z_input + Z_Z2)

    # input damping
    H_in_det = -1*Z_Z2/(Z_input + Z_Z2)

    # total closed loop voltage gain
    Atotal_closed_det = H_in_det*Atotal_open/(1+Atotal_open*H_fb_det)

    
    
    
    
    print('--Noise calculation --')


    # decide what closed loop gain to use

    # w/o detector:
    closed_loop_gain = Atotal_closed
    # with detector:
    #closed_loop_gain = Atotal_closed_det


    # dict to keep track of all noise sources
    noise_sources = {}

    
    # noise from feedback Circuit
    en_Z2 = np.sqrt(4*args.T_4K*Q.kB*Z_Z2.real)
    
    
    en_Z2_input = en_Z2/closed_loop_gain
    

    noise_sources['en_Z2'] = en_Z2_input
    
    # noise from HEMT
    en_HEMT_input = hemt.voltageNoise(f_arr, fc=1.2e3, vflat=0.24e-9)


    noise_sources['en_HEMT'] = en_HEMT_input

    # noise from Z3
    en_Z3 = np.sqrt(4*args.T_300K*Q.kB*Z_Z3.real)

    # refer voltage noise from Z3 to the input of the HEMT gate
    # BJT is 
    en_Z3_input = en_Z3/Aopen_HEMT
    
    noise_sources['en_Z3'] = en_Z3_input

    # noise from BJT
    #in_BJT = np.ones(len(f_arr))*bjt.currentNoise(args.drainI)
    in_BJT = 1e-19*np.ones(len(f_arr))

    # voltage noise from BJT as referred to the input of HEMT (scale by gm)
    en_BJT_input = in_BJT/hemt.gm


    noise_sources['en_BJT'] = en_BJT_input

    # noise from opamp
    en_opamp = opamp.voltage_noise(f_arr)
    en_opamp_gary = opamp.voltage_noise_gary(f_arr)
        
    # noise from opamp referred to HEMT gate input
    # divide by HEMT open loop gain 
    en_opamp_input = en_opamp/Aopen_HEMT
    en_opamp_gary_input = en_opamp_input/Aopen_HEMT

    noise_sources['en_opamp'] = en_opamp_input





    
    # Calculate sum of noise contributions

    # try different Z2 contributions
    en_total_input = None

    # use diffent Z2 contributions for the total noise
    for src, val in noise_sources.items():
        # take abs value
        val = np.abs(val)
        print("src " + src + " val " + str(val))
        if en_total_input is None:
            en_total_input = np.power(val,2)
        else:
            en_total_input += np.power(val,2)

        # plot noise sources
        if args.makeplots:
            plot_util.noise_plot(fig, f_arr, val, legend=src)

        # add to output file
        outfile_dict[src] = val
    

    # take the square root of the total noise
    en_total_input = np.sqrt(np.abs(en_total_input))
    print("en_total_input ")
    print(en_total_input)
    print ("closed_loop_gain")
    print(closed_loop_gain)
    en_total_output = np.abs(en_total_input*closed_loop_gain)

    print(en_total_output)

    # add to output file
    outfile_dict['en_total_input'] = en_total_input
    outfile_dict['en_total_output'] = en_total_output

    
    # plot total input noise
    if args.makeplots:
        plot_util.noise_plot(fig, f_arr, en_total_input, legend='en_total', name='en_total_input', ylabel=r'$V/\sqrt{Hz}$', note=r'Total voltage noise (input)')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_total_output, legend='en_total_output', name='en_total_output', ylabel=r'$V/\sqrt{Hz}$', note=r'Total voltage noise (output)')
        fig.clf()
    
    print("f_arr")
    print(f_arr)
    print("en_total_output")
    print(en_total_output)





    # make plots

    if args.makeplots:
        print("Make impedance plots")

        plot_util.impedance_plot(fig, f_arr, Z_Z5, 'Z_Z5.png', note='Z5')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_Z6, 'Z_Z6.png', note=r'Z6')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, B, 'B.png',ylabel='Feedback fraction B',note='Feedback fraction B')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Aopen, 'Aopen_opamp.png', ylabel='Aopen opamp', note='Aopen opamp')
        plot_util.impedance_plot(fig, f_arr, Aopen, 'Aopen_opamp.png', ylabel='Aopen opamp', note='Aopen opamp')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Aopen_gary, None, ylabel='Aopen opamp', legend='Gary')
        plot_util.impedance_plot(fig, f_arr, Aopen, 'Aopen_opamp_gary.png', ylabel='Aopen opamp', note='Aopen opamp', legend='Pelle')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Aclosed, 'Aclosed_opamp.png', ylabel='Aclosed opamp', note='Aclosed opamp')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_Z3, 'Z3.png', note='Z3')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_load, 'Z_load.png', note='Z_load')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Aopen_HEMT, 'Aopen_HEMT.png', ylabel='Aopen HEMT', note='Aopen HEMT gm={0:.1f}mS'.format(hemt.gm*1e3))
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Atotal_open, 'Atotal_open.png', ylabel='Atotal openT', note='Atotal open')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_HEMT, 'Z_HEMT.png', note='Z_HEMT')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_Z1_g, 'Z1_g.png', note='Z1_g')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_Z1_open, 'Z1_open.png', note='Z1_open')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_input_4K, 'Z_input_4K.png', note='Z_input_4K')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Z_Z2, 'Z2.png', note='Z2')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, H_fb, legend='H_fb')
        plot_util.impedance_plot(fig, f_arr, H_in, 'H_in.png', legend='H_in', ylabel='Feedback fraction & damping')
        fig.clf()
        plot_util.impedance_plot(fig, f_arr, Atotal_closed, 'Atotal_closed.png', ylabel='Atotal closed', note='Atotal closed')
        fig.clf()


        plot_util.impedance_plot(fig, f_arr, Atotal_closed,legend='Atotal_closed')
        plot_util.impedance_plot(fig, f_arr, Atotal_closed_no_H_in, legend='no H_in')
        plot_util.impedance_plot(fig, f_arr, Atotal_closed_no_H_fb, ylabel='Atotal_closed', legend='no H_fb',note='Compare FB/damping effect.', name='Atotal_closed_cmp.png')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC, note='Z_Z1_MC', name='Z1_MC.png')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC, legend='Z_Z1_MC')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC_g, note='Z_Z1_MC_g', name='Z1_MC_g.png')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC, legend='Z_Z1_MC')
        plot_util.impedance_plot(fig, f_arr, Z_Z1_g, legend='Z_Z1_g')
        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC_g, legend='Z_Z1_MC_g', name='Z1_MC_cmp.png')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Z_input, note='Z_input', name='Z_input.png')
        fig.clf()

        # compare w/ and w/o MC stage
        plot_util.impedance_plot(fig, f_arr, Z_input, legend='Z_input')
        plot_util.impedance_plot(fig, f_arr, Z_input_4K, legend='Z_input_4K')
        plot_util.impedance_plot(fig, f_arr, Z_Z1_MC_g, legend='Z1_MC',name='Z_input_cmp.png')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, H_fb_det, 'H_fb_det.png', note='H_fb_det')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, H_in_det, 'H_in_det.png', note='H_in_det')
        fig.clf()

        plot_util.impedance_plot(fig, f_arr, Atotal_closed_det, 'Atotal_closed_det.png', ylabel='Atotal closed det', note='Atotal_closed_det')
        fig.clf()

        # compare w/ and w/o MC stage
        plot_util.impedance_plot(fig, f_arr, Atotal_closed_det, legend='Atotal_closed_det')
        plot_util.impedance_plot(fig, f_arr, Atotal_closed, legend='Atotal_closed',name='Atotal_closed_det_cmp.png',ylabel='total closed loop gain')
        fig.clf()


        

        print("Make noise plots")

        
        plot_util.noise_plot(fig, f_arr, en_Z2, name='en_Z2', legend='T=4K', ylabel='V/sqHz', note='FB cap and R network.')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_Z2_input, name='en_Z2_input', ylabel='V/sqHz', note='FB cap and R network refered to input (/A_closed_total)')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_HEMT_input,  name='en_HEMT_input', ylabel='V/sqHz')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_Z3, name='en_Z3', ylabel='V/sqHz', legend=r'en Z_3')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_Z3_input,  name='en_Z3_input', ylabel=r'V/\sqrt{Hz}', legend=r'en Z_3 (input)')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, in_BJT, name='in_BJT', ylabel=r'A/\sqrt{Hz}', note='BJT shot noise')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_BJT_input, name='en_BJT', ylabel=r'V/\sqrt{Hz}', note=r'BJT shot noise (input, gm={0:.1f}mS)'.format(hemt.gm*1e3))
        #plot_util.impedance_plot(fig, f_arr, Aopen_HEMT, 'Aopen_HEMT.png', ylabel='Aopen HEMT', note='Aopen HEMT gm={0:.1f}mS'.format(hemt.gm*1e3))
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_opamp, name='en_opamp', ylabel=r'V/\sqrt{Hz}', note=r'Opamp voltage noise')
        fig.clf()
        plot_util.noise_plot(fig, f_arr, en_opamp_gary_input, ylabel=r'$V/\sqrt{Hz}$', note=r'Opamp voltage noise (input)')
        plot_util.noise_plot(fig, f_arr, en_opamp_input, name='en_opamp_input', ylabel=r'$V/\sqrt{Hz}$', legend='Gary')

        fig.clf()
    



    # close output file
    if outfile_dict and args.savename:
        np.savez_compressed(args.savename, outfile_dict)
    
    
    if args.show:
        plt.show()
    
                 



    

                 


if __name__ == '__main__':

    print('Just GO')

    args = get_args()
    
    main()
