import sys
import numpy as np
import matplotlib.pyplot as plt



def get_noise_data(files):
    f = None
    n = None
    for file in files:
        a = np.genfromtxt(file)
        if f == None:
            f = a[:,0]
            n = a[:,1]
        else:
            f = np.concatenate((f,a[:,0]), axis=0)
            n = np.concatenate((n,a[:,1]), axis=0)

    return (f,n)


data = get_noise_data(sys.argv[1:len(sys.argv)])

plt.semilogy(data[0],data[1])
#plt.axis.set_xscale("log")

plt.show()

#plt.plot(n)

#plt.show()


