import math
import numpy as np
import matplotlib.pyplot as plt
import impedance


x = np.logspace(2,7)

#plt.semilogx(x,20*np.log10(A))
opamp = impedance.LT1677('whatever')
#plt.semilogx(x,20*np.log10(opamp.Aopen(x)))
#plt.semilogx(x,opamp.Aopen(x))
#plt.grid()

xc=1e4
y = 90*(1 + (x/xc)*(- 30*np.log10(x)))
plt.semilogx(x,y)


plt.show()




