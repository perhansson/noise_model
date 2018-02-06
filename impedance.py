from math import pi as pi
from math import sqrt
import cmath
import numpy as np
import matplotlib.pyplot as plt


kB = 1.38064852e-23
qE = 1.602e-19



def radToDeg(v):
    return 180.0*v/pi

def parallel(Z1,Z2):
    return 1.0/(1.0/Z1 + 1.0/Z2)

def series(Z1,Z2):
    return Z1 + Z2



def to_np_array(func, arr):
    return np.array([func(a) for a in arr])


def impedancePlot(fig, f, Z, name=None, ylabel='Impedance', xlabel='Frequency', note=None, legend=None, logy=True):
    """Plot impedance and phase"""


    if fig == None:
        plt.figure()
    
    ax_MC211 = plt.subplot(211)
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
    
    ax_MC212 = plt.subplot(212)
    plt.plot(f, radToDeg(Z_phase))
    plt.ylabel('Phase')
    plt.xlabel('Frequency')
    #ax_MC1.set_yscale(u'log')
    ax_MC212.set_xscale(u'log')

    if name:
        plt.savefig(name,bbox_inches='tight')

    
    return [ax_MC211, ax_MC212]



def noisePlot(fig, f, Z, name=None, ylabel='Noise', xlabel='Frequency', note=None, legend=None, logy=True):
    """Plot noise."""

    if fig == None:
        plt.figure()

    
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
              




class Component(object):
    def __init__(self, value, name=''):
        self.value = value
        self.name = name
    def Z(self,f):
        """Override this function."""

class Capacitor(Component):
    def __init__(self, value, name=''):
        Component.__init__(self,value, name)
    def Z(self,f):
        return complex(0,-1.0/(2*pi*f*self.value))

class Resistor(Component):
    def __init__(self, value, name=''):
        Component.__init__(self,value, name)
    def Z(self,f):
        return complex(self.value,0)
    def voltage_noise(self,T):
        """Return voltage noise in V/sqHz"""
        return sqrt(4*kB*T*self.value)


class Circuit(object):

    """ Base class. """

    def __init__(self, name):
        """init class"""
        self.name = name

    def Z_tot(self):
        """Should override this function"""


class HEMT(Circuit):
    def __init__(self,name, Rg=1e12, Cgs=100e-12, gm=35):
        """ Arguments:
        Rg: input resistance on the gate
        Cgs: gate-source capacitance
        gm: transconductance in mS
        """
        Circuit.__init__(self,name)
        self.Rg = Resistor(Rg,'Rg')
        self.Cgs = Capacitor(Cgs,'Cgs)')
        self.gm = gm*1e-3 #S

    def Z_tot(self, freq):
        # gate to source resistance and gate to source capacitance in parallel
        Zt = parallel(self.Rg.Z(freq), self.Cgs.Z(freq))
        return Zt

    def voltageNoise(self,f, fc=1.2e3, vflat=0.254-9):
        """Voltage noise in V/sqHz.

        fc = knee frequencey in Hz
        vflat = white noise level.
        """
        return (fc/f + 1)*vflat
    


class OpAmp(Circuit):
    def __init__(self,name):
        Circuit.__init__(self,name)

    def Aopen(self,freq):
        """ override this function"""
        return 0
    
    def voltage_noise(self, freq):
        """ override this function"""
        return voltage_noise(freq)


    
class LT1677(OpAmp):
    """Specific Opamp"""
    def __init__(self, name):
        OpAmp.__init__(self,name)
        self._pole1 = 0.5 #Hz
        self._pole2 = 80e3 #Hz
        self._Aflat = 135.0 #Db
        self._phase_slope = -30 #deg/decade in Freq
        
    def Aopen_phase(self, freq):
        if freq <1e5:
            return math.pi/2
        elif freq >=1e5 and freq < 1e6:            
            return 240 - self._phase_slope*np.log10(freq)
        else:
            return 60.0*math.pi/180

    def Aopen(self,freq):
        #return np.power(10,self._Aflat/20.0)/((1+freq/self._pole1)*(1+freq/self._pole2))
        w = np.power(10,self._Aflat/20.0)
        w1 = complex(1,freq/self._pole1)
        w2 = complex(1,freq/self._pole2)
        return w/(w1*w2)
    
    def Aopen_gary(self,freq):
        w = 2*np.pi*freq
        w0 = complex(1,w/(2*np.pi*10))
        w1 = complex(1, w/(2*np.pi*1e6))
        return 2e7/( w0*w1 )

    def voltage_noise(self, freq, fc=13.0, vflat=3.2e-9):
        """Input voltage noise.
        fc = knee frequencey in Hz
        vflat = white noise level.
        """
        return (fc/freq + 1)*vflat

    def voltage_noise_gary(self, freq):
        """Input voltage noise based on Gary's notes. """
        w = 2*pi*freq
        return np.sqrt(np.power(1.8e-9,2) + np.power(30e-9,2)/freq)

    
        


class BJT(Circuit):
    def __init__(self,name):
        Circuit.__init__(self,name)

    def Z_tot(self, freq):
        return 0

    def shotNoise(self,I):
        """Shot noise in A/sqHz."""
        return sqrt(2*qE*I)

    def currentNoise(self,I):
        """Total current noise in A/sqHz."""
        return self.shotNoise(I)
    

class Z6(Circuit):
    """Opamp feedback circuit."""
    def __init__(self,name, Rfb=1e20, Cfb=20e-12):
        Circuit.__init__(self,name)
        self.Rfb = Resistor(Rfb,'Rfb')
        self.Cfb = Capacitor(Cfb,'Cfb)')

    def Z_tot(self, freq):
        """Impedance of opamp feedback network."""
        Z = parallel(self.Rfb.Z(freq), self.Cfb.Z(freq))
        return Z

        

class Z3(Circuit):
    """Load resistor and stabilization circuit."""
    def __init__(self,name, R113=1.6e3, R1110=1e2, C1120=10e-9):
        Circuit.__init__(self,name)
        self.C1120 = Capacitor(C1120,'C1120')
        self.R113 = Resistor(R113,'R113')
        self.R1110 = Resistor(R1110,'R1110')
    
    def Z_tot(self, freq):
        Z1 = series(self.R1110.Z(freq), self.C1120.Z(freq))
        Z = parallel(Z1, self.R113.Z(freq))
        return Z


class Z1_g(Circuit):
    """Coupling capacitor to the HEMT gate at 4K"""
    def __init__(self, name, Ccg=10e-9):
        Circuit.__init__(self, name)
        self.Ccg = Capacitor(Ccg, 'Ccg')
    
    def Z_tot(self,freq):
        return self.Ccg.Z(freq)



class Z1_MC(Circuit):
    """Circuitry on lower coax PCB at MC stage."""
    def __init__(self,name,Cdet=200.0e-12, Rbias=80e6, Rbleed=80e6, Cc=10e-9):
        Circuit.__init__(self,name)
        self.Cdet = Capacitor(Cdet, 'Cdet')
        self.Rbias = Resistor(Rbias, 'Rbias')
        self.Rbleed = Resistor(Rbleed, 'Rbleed')
        self.Cc = Capacitor(Cc, 'Cc')
    
    def Z_tot(self,freq):

        # bias and detector are in parallel
        Z1 = parallel(self.Rbias.Z(freq), self.Cdet.Z(freq))

        # Z1 in series with coupling capacitor
        Z2 = series(Z1, self.Cc.Z(freq))

        #Z2 in parallel with bleed resistor
        Z3 = parallel(Z2,self.Rbleed.Z(freq))

        return Z3



class Z5(Circuit):
    """"""
    def __init__(self,name, C118=100e-9, R115=3.3e3, R114=3.3e3, R1140=1e3):
        """"""
        Circuit.__init__(self,name)
        """Impedance of opamp comparator bias network."""
        self.C118 = Capacitor(C118,'C118')
        self.R115 = Resistor(R115,'R115')
        self.R114 = Resistor(R114,'R114')
        self.R1140 = Resistor(R1140,'R1140')

    def Z_tot(self, freq):
        Z1 = parallel(self.R115.Z(freq),self.R114.Z(freq))
        Z2 = parallel(Z1,self.C118.Z(freq))
        Z = series(self.R1140.Z(freq), Z2)
        return Z


class Z4(Circuit):
    """"""
    def __init___(self,name, Rmirror=1e2):
        """"""
        Circuit.__init__(self,name)
        self.Rmirror = Resistor(Rmirror,'Rmirror')
    
    def Z_tot(self, freq):
        """Impedance of load resistance in current mirror."""
        return self.Rmirror.Z(freq)
    


class Z2(Circuit):
    """Feedback cap and resistor network."""
    def __init__(self,name, Cfb=0.25e-12, Rfb=400e6):
        Circuit.__init__(self, name)
        self.Cfb = Capacitor(Cfb, 'Cfb')
        self.Rfb = Resistor(Rfb, 'Rfb')
    
    def Z_tot(self, freq):
        Z = parallel(self.Cfb.Z(freq), self.Rfb.Z(freq))
        return Z

    def voltageNoise(self, T):
        return self.Rfb.voltageNoise(T)
    

class ChargeCircuit(Circuit):

    """Description of charge circuit for ionization readout for SCDMS."""

    def __init__(self, name):
        """init class"""
        Circuit.__init__(self,name)
        self._components = []

    def addCircuit(self,c):
        if self.get(c.name) != None:
            raise ValueError('this circuit is already present')
        else:
            self._components.append(circ)
    
    def getCircuit(self, name):
        for c in self._components:
            if c.name == name:
                return c
        return None
    
    def setGain(self,A,f):
        """Set total gain vs frequency"""
        self._gain = A
        self._f = f

        
    
    

    
