from math import pi as pi
from math import sqrt
import cmath
import numpy as np
import matplotlib.pyplot as plt
from impedance import to_np_array, radToDeg



def setup_plt(*argv):
    """Setup plot style.
    
    Arguments:
    *argv: optional first is the fig reference

    """
    
    #plt.rcParams['figure.figsize'] = (10,12)
    plt.rcParams['axes.grid'] = True
    if len(argv) > 0:
        argv[0].set_facecolor("white")






def simple_plot(x, y, fig=None, ax=None, name=None, ylabel=None, xlabel=None, note=None, 
                legend=None, logy=False, logx=False, save_path=None, line='-'):
    """Simple plot. """


    if ax == None:
        fig, ax = plt.subplots(figsize=(18,12))
    setup_plt(fig)

    if legend != None:
        ax.plot(x, y, line, label=legend)
    else:
        ax.plot(x, y, line)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if logy:
        ax.set_yscale(u'log') 
    if logx:
        ax.set_xscale(u'log')

    if note:
        plt.text(0.1, 0.9, note, transform = ax.transAxes)
    
    
    # if a name is given, save to file
    if name:
        print("save " + name)
        plt.savefig(name,bbox_inches='tight')

    # if pathis given, save to file
    if save_path != None:
        if ".txt" in save_path:
            np.savetxt(save_path, x=x, y=y)
        else:
            np.savez(save_path, x=x, y=y)
    
    return (fig,ax)


        
def simple_overlay_plot(x1, y1, x2, y2, 
                        name=None, line1="b", line2="b", 
                        ylabel=None, xlabel=None, note=None, legend=(None,None), 
                        logy=False, logx=False, save_path=None):
    """Simple data overlay plot. """
    
    fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(18,12))

    setup_plt(fig)

    print(legend[0])
    ax1.plot(x1, y1, line1, label=legend[0])
    ax1.scatter(x2, y2, line2, label=legend[1])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if logy:
        ax1.set_yscale(u'log') 
    if logx:
        ax1.set_xscale(u'log')

    if note:
        plt.text(0.1, 0.9, note, transform = ax1.transAxes)
    

    if legend[0] is not None or legend[1] is not None:
        plt.legend()


    #plot difference
    #ax2.plot(x1, y2-y1)
    #plt.text(0.1, 0.9, "Difference", transform = ax2.transAxes)


    # if a name is given, save to file
    if name:
        print("save " + name)
        plt.savefig(name,bbox_inches='tight')

    # if pathis given, save to file
    if save_path != None:
        if ".txt" in save_path:
            np.savetxt(save_path, x=x, y=y)
        else:
            np.savez(save_path, x=x, y=y)
    
    return (fig, (ax1,ax2))



def impedance_plot(fig, f, Z, name=None, ylabel='Impedance', xlabel='Frequency', note=None, 
                   legend=None, logy=True):
    """Plot impedance and phase"""


    if fig == None:
        fig, (ax_MC211, ax_MC212) = plt.figure(2, 1, figsize=(18,12))

    
    line1, = plt.plot(f, np.abs(Z), label=legend)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if logy:
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

    if name != None:
        print("plot " + name)
    print("phase")
    print(Z_phase)
    
    plt.plot(f, radToDeg(Z_phase))
    plt.ylabel('Phase')
    plt.xlabel('Frequency')
    ax_MC212.set_xscale(u'log')

    # if a name is given, save to file
    if name:
        plt.savefig(name,bbox_inches='tight')
    return [ax_MC211, ax_MC212]



def noise_plot(fig, f, Z, name=None, ylabel='Noise', xlabel='Frequency', note=None, 
               legend=None, logy=True):
    """Plot noise."""

    if fig == None:
        plt.figure(figsize=(18,12))
    
    ax_MC211 = plt.subplot(111)
    line1, = plt.plot(f, np.abs(Z), label=legend)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    if logy:
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

    if name:
        plt.savefig(name,bbox_inches='tight')


    return [ax_MC211]
