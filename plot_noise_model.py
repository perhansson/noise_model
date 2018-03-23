import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import plot_util



def get_args():
    parser = argparse.ArgumentParser('Make plots from noise model and compare to data.')
    parser.add_argument('--data', '-d', nargs='+', help='Data files.')
    parser.add_argument('--model', '-m', default='outputfile.npz', help='Model data files.')
    parser.add_argument('--show',action='store_true',help='Show plots.')

    a = parser.parse_args()
    print(a)
    return a




def get_noise_data(files, unique=False):
    f = None
    n = None
    for file in files:
        a = np.genfromtxt(file)
        if f is None:
            f = a[:,0]
            n = a[:,1]
        else:
            if not unique:
                f = np.concatenate((f,a[:,0]), axis=0)
                n = np.concatenate((n,a[:,1]), axis=0)
            else:
                # increasing frequencies only!
                f_max = np.max(f)
                f = np.concatenate((f, a[:,0][ a[:,0] > f_max] ))
                n = np.concatenate((n, a[:,1][ a[:,0] > f_max] ))
    
    return (f,n)


    


def get_model_noise_data(filepath):

    print("Getting data from: " + filepath)

    # get container
    c = np.load(filepath)
    print(c)
    # recover dict of data 
    return c['arr_0'].item()



if __name__ == "__main__":


    args = get_args()
    
    plot_util.setup_plt()    

    logx = True
    logy = True
    
    # get the noise model data
    raw_data_model = get_model_noise_data(args.model)
    freq_model = raw_data_model['f_arr']

    # make unique
    

    plot_util.simple_plot(freq_model, raw_data_model["en_total_output"], 
                          xlabel="Frequency (Hz)", ylabel=r'$V/\sqrt{Hz}$', note="Total output noise", 
                          logx=logx, logy=logy,
                          name="noise_model_total_output_noise")
    
    # get the noise data
    if args.data:
        freq_data, data = get_noise_data(args.data, unique=True)
    
        # plot the raw data
        plot_util.simple_plot(freq_data, data, xlabel="Frequency (Hz)", ylabel=r'$V/\sqrt{Hz}$', note="Raw data", 
                              logx=logx, logy=logy)
        
        # plot raw data to model
        ind = freq_model <= np.max(freq_data)
        
        fig, ax1 = plt.subplots(figsize=(18,12))

        plot_util.setup_plt(fig)

        ax1.scatter(freq_data, data, label="data")
        ax1.plot(freq_model[ind], raw_data_model['en_total_output'][ind], "k", label="model")
        plt.ylabel(r'$V/\sqrt{Hz}$')
        plt.xlabel("Frequency (Hz)")
        if logy:
            ax1.set_yscale(u'log') 
        if logx:
            ax1.set_xscale(u'log')
            plt.text(0.1, 0.9, "Output noise", transform = ax1.transAxes)
        plt.legend()
        plt.savefig("noise_output_data_vs_model",bbox_inches='tight')

        #plot difference
        print("len of data {:d}, len of model {:d}".format(len(freq_data), len(freq_model[ind])))
        fig2, (ax21,ax22) = plt.subplots(2,1,figsize=(18,12))
        freq_model_idx = []
        for freq in freq_data:
            freq_model_idx.append(np.argmin(np.abs(freq_model-freq)))
        #ax22.plot(freq_data,freq_model[freq_model_idx])

        ax21.plot(freq_data, data-raw_data_model['en_total_output'][ind][freq_model_idx])
        plt.text(0.1, 0.9, "Difference b/w data and model", transform=ax21.transAxes)
        plt.ylabel(r'data-model [$V/\sqrt{Hz}$]')
        plt.xlabel("Frequency (Hz)")
        #ax21.set_yscale(u'log') 
        ax21.set_xscale(u'log') 
        ax22.plot(freq_data, (data-raw_data_model['en_total_output'][ind][freq_model_idx])/raw_data_model['en_total_output'][ind][freq_model_idx])
        plt.text(0.1, 0.9, "Relative difference", transform=ax22.transAxes)
        plt.ylabel("(data-model)/model [arb. units]")
        plt.xlabel("Frequency (Hz)")
        #ax22.set_yscale(u'log') 
        ax22.set_xscale(u'log') 
        
        plt.savefig("noise_output_data_vs_model_diff",bbox_inches='tight')
        
        
        #ax2.plot(x1, y2-y1)
        #plt.text(0.1, 0.9, "Data-model", transform = ax2.transAxes)
        

    
    
    
    if args.show:
        plt.show()

    sys.exit(0)
