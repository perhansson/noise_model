from math import pi as pi


def radToDeg(v):
    return 180.0*v/pi

def parallel(Z1,Z2):
    return 1.0/(1.0/Z1 + 1.0/Z2)

def series(Z1,Z2):
    return Z1 + Z2

class Component:
    def __init__(self, value, name=''):
        self.value = value
        self.name = name
    def Z(self,f):
        """Override this function."""

class Capacitor(Component):
    def Z(self,f):
        return 1.0/complex(0,2*pi*f*self.value)

class Resistor(Component):
    def Z(self,f):
        return complex(self.value,0)


class Circuit:

    """ Base class. """

    def __init__(self, name):
        """init class"""
        self.name = name

    def Z_tot(self):
        """Should override this function"""


class ChargeCircuit(Circuit):

    """Description of charge circuit for ionization readout for SCDMS."""

    def __init__(self, name, Cdet=200.0e-12, Rbias=100e6, Rbleed=100e6, Cc=10e-9):
        """init class"""
        self.name = name
        self.Cc = Capacitor(Cc, 'Cc')
        self.Cdet = Capacitor(Cdet, 'Cdet')
        self.Rbias = Resistor(Rbias, 'Rbias')
        self.Rbleed = Resistor(Rbleed, 'Rbleed')
        
    
    def Z_MC1(self, freq):
        """Impendance of circuitry at on lower coax PCB at MC stage."""

        # bias and detector are in parallel
        Z1 = parallel(self.Rbias.Z(freq), self.Cdet.Z(freq))

        # Z1 in series with coupling capacitor
        Z2 = series(Z1, self.Cc.Z(freq))

        #Z2 in parallel with bleed resistor
        Z3 = parallel(Z2,self.Rbleed.Z(freq))

        return Z3
        
        
    def Z_tot(self, freq):
        return self.Z_MC1(freq)




    
